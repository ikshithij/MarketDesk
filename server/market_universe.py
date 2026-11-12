"""Persistent full-market collection, exploratory ranking and top-100 AI queue."""
import csv
import hashlib
import io
import json
import threading
import time
import uuid
from datetime import datetime,timezone
from . import store,market_sources as sources,market_data as data,market_screen as screen
from . import company_analysis as ai,company_ratings as ratings

STOP=threading.Event()
CREATE_LOCK=threading.Lock()
THREADS=[]


def initialize():
    STOP.clear();sources.STOP.clear()
    with store.db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS market_sources(id TEXT PRIMARY KEY,url TEXT,kind TEXT,sha256 TEXT,path TEXT,retrieved_at TEXT,provided_at TEXT,bytes INTEGER);
        CREATE INDEX IF NOT EXISTS market_source_url ON market_sources(url,retrieved_at);
        CREATE TABLE IF NOT EXISTS market_runs(id TEXT PRIMARY KEY,status TEXT,phase TEXT,created_at TEXT,updated_at TEXT,config_json TEXT,progress_json TEXT,errors_json TEXT,auto_ai INTEGER,cohort_hash TEXT);
        CREATE TABLE IF NOT EXISTS market_observations(run_id TEXT,listing_id TEXT,country TEXT,symbol TEXT,name TEXT,sector TEXT,status TEXT,listing_json TEXT,features_json TEXT,reasons_json TEXT,warnings_json TEXT,sources_json TEXT,score REAL,peer_count INTEGER,rank INTEGER,shortlisted INTEGER,checked_at TEXT,PRIMARY KEY(run_id,listing_id));
        CREATE INDEX IF NOT EXISTS market_observation_scan ON market_observations(run_id,country,status);
        CREATE INDEX IF NOT EXISTS market_observation_rank ON market_observations(run_id,score);
        CREATE TABLE IF NOT EXISTS paper_baskets(run_id TEXT PRIMARY KEY,started_at TEXT NOT NULL,cohort_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS market_ai_queue(run_id TEXT,listing_id TEXT,position INTEGER,status TEXT,report_id TEXT,rating_job_id TEXT,attempts INTEGER,reason TEXT,updated_at TEXT,PRIMARY KEY(run_id,listing_id));
        ''')
        c.execute("UPDATE market_runs SET status='queued',phase='Resuming saved collection',updated_at=? WHERE status='running'",(store.now(),))


def start_workers():
    global THREADS
    THREADS=[threading.Thread(target=collection_loop,name='market-collection',daemon=True),threading.Thread(target=research_loop,name='market-research-queue',daemon=True)]
    for thread in THREADS:thread.start()


def stop_workers():
    STOP.set();sources.STOP.set()
    for thread in THREADS:thread.join(timeout=2)


def state(rid):
    with store.db() as c:r=c.execute('SELECT * FROM market_runs WHERE id=?',(rid,)).fetchone()
    if not r:raise ai.AnalysisError('Market scan not found.')
    row=dict(r)
    for key in ['config','progress','errors']:row[key]=json.loads(row.pop(key+'_json'))
    row['auto_ai']=bool(row['auto_ai'])
    return row


def progress(rid,phase,**changes):
    item=state(rid);item['progress'].update(changes)
    with store.db() as c:c.execute('UPDATE market_runs SET phase=?,progress_json=?,updated_at=? WHERE id=?',(phase,json.dumps(item['progress']),store.now(),rid))


def stopped(rid):return STOP.is_set() or state(rid)['status']!='running'


def create(auto_ai=True):
    with CREATE_LOCK:
        with store.db() as c:
            active=c.execute("SELECT id FROM market_runs WHERE status IN ('running','queued') ORDER BY created_at DESC LIMIT 1").fetchone()
            if active:return state(active['id'])
            rid=uuid.uuid4().hex
            config={'screen':screen.POLICY,'standard_version':'1.0.0','ai_rubric_version':ratings.VERSION,'created_with_app':'0.2.0','price_cutoff':'completed_prior_calendar_sessions','coverage':'Public current exchange snapshots; OTC/private companies outside scope; no broker verification.'}
            c.execute('INSERT INTO market_runs VALUES(?,?,?,?,?,?,?,?,?,?)',(rid,'queued','Waiting to discover US and UK listings',store.now(),store.now(),json.dumps(config),'{}','[]',int(auto_ai),None))
        return state(rid)


def control(rid,action):
    current=state(rid)
    with store.db() as c:
        if action=='pause' and current['status'] in ('running','queued'):
            c.execute("UPDATE market_runs SET status='paused',phase='Paused; checkpoints saved',updated_at=? WHERE id=?",(store.now(),rid))
        elif action=='resume' and current['status'] in ('paused','failed'):
            other=c.execute("SELECT id FROM market_runs WHERE status IN ('running','queued') AND id<>?",(rid,)).fetchone()
            if other:raise ai.AnalysisError('Another market scan is already active.')
            c.execute("UPDATE market_runs SET status='queued',phase='Resuming saved checkpoints',updated_at=? WHERE id=?",(store.now(),rid))
        elif action in ('pause-research','resume-research'):
            c.execute('UPDATE market_runs SET auto_ai=?,updated_at=? WHERE id=?',(int(action=='resume-research'),store.now(),rid))
            if action=='resume-research' and current['status']=='complete':
                shortlisted=c.execute('SELECT listing_id FROM market_observations WHERE run_id=? AND shortlisted=1 ORDER BY rank,listing_id LIMIT 100',(rid,)).fetchall()
                for position,row in enumerate(shortlisted,1):c.execute('INSERT OR IGNORE INTO market_ai_queue VALUES(?,?,?,?,?,?,?,?,?)',(rid,row['listing_id'],position,'pending',None,None,0,None,store.now()))
        elif action=='retry-research':
            c.execute("UPDATE market_ai_queue SET status='pending',report_id=NULL,rating_job_id=NULL,reason=NULL,attempts=0,updated_at=? WHERE run_id=? AND status='failed'",(store.now(),rid))
        else:
            if action not in ('pause','resume','retry-research','pause-research','resume-research'):raise ai.AnalysisError('Unknown market job action.')
    return state(rid)


def save_initial(rid,listings,metadata):
    with store.db() as c:
        for listing in listings:
            status='pending' if listing['classification']=='candidate' else listing['classification']
            c.execute('INSERT OR IGNORE INTO market_observations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(rid,listing['id'],listing['country'],listing['symbol'],listing['name'],listing['sector'],status,json.dumps(listing),'{}',json.dumps([listing['exclusion']] if listing.get('exclusion') else []),'[]',json.dumps([metadata]),None,0,None,0,None))


def discover(rid):
    records=[];errors=[]
    for other,url in [(False,'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'),(True,'https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt')]:
        if stopped(rid):return False
        progress(rid,'Discovering official US exchange listings')
        try:
            meta,path=sources.acquire(url,'Official US symbol directory',max_bytes=8_000_000);rows=sources.nasdaq_rows(path.read_text(),other);save_initial(rid,rows,meta);records.append({**meta,'rows':len(rows)})
        except sources.SourceError as exc:errors.append({'source':url,'error':str(exc)})
    if not stopped(rid):
        progress(rid,'Discovering London Main Market and AIM listings')
        try:
            meta,payload=sources.json_source('https://docs.londonstockexchange.com/reports/instruments/latest.json','Official LSE download metadata',max_bytes=1_000_000)
            item=next(r for r in payload['Data'] if r['fileType']=='xlsx')
            if not item['downloadLink'].startswith('https://docs.londonstockexchange.com/reports/'):raise sources.SourceError('Unexpected LSE download host.')
            meta,path=sources.acquire(item['downloadLink'],'Official LSE equity directory',max_bytes=20_000_000,provided_at=item.get('publishedDate'));rows=sources.lse_rows(path);save_initial(rid,rows,meta);records.append({**meta,'rows':len(rows)})
        except (sources.SourceError,KeyError,StopIteration,ValueError) as exc:errors.append({'source':'LSE','error':str(exc)})
    if not stopped(rid):
        progress(rid,'Discovering Aquis listings')
        try:
            meta,path=sources.acquire('https://aquis-public-files.s3.eu-west-2.amazonaws.com/aqse/security_web.csv','Official Aquis security directory',max_bytes=3_000_000)
            rows=sources.aquis_rows(path.read_text());save_initial(rid,rows,meta);records.append({**meta,'rows':len(rows)})
        except sources.SourceError as exc:errors.append({'source':'Aquis','error':str(exc)})
    if stopped(rid):return False
    with store.db() as c:c.execute('UPDATE market_runs SET errors_json=? WHERE id=?',(json.dumps(errors),rid))
    if errors:raise sources.SourceError('A listing source failed. Resume to retry; no incomplete-universe top 100 was frozen.')
    progress(rid,'Exchange universe discovered',discovered=True,directory_sources=records)
    return True


def pending(rid,country):
    with store.db() as c:rows=c.execute("SELECT * FROM market_observations WHERE run_id=? AND country=? AND status='pending' ORDER BY symbol,listing_id",(rid,country)).fetchall()
    return [dict(r) for r in rows]


def save_result(rid,listing,features,reasons,warnings,records,status=None):
    status=status or ('ineligible' if reasons else 'ready')
    with store.db() as c:c.execute('UPDATE market_observations SET status=?,listing_json=?,name=?,sector=?,features_json=?,reasons_json=?,warnings_json=?,sources_json=?,checked_at=? WHERE run_id=? AND listing_id=?',(status,json.dumps(listing),listing['name'],listing['sector'],json.dumps(features,allow_nan=False),json.dumps(reasons),json.dumps(warnings),json.dumps(records),store.now(),rid,listing['id']))


def refresh_ranks(rid,final=False):
    with store.db() as c:raw=c.execute('SELECT * FROM market_observations WHERE run_id=?',(rid,)).fetchall()
    rows=[{'listing':json.loads(r['listing_json']),'status':r['status'],'features':json.loads(r['features_json']),'reasons':[reason for reason in json.loads(r['reasons_json']) if reason not in ('Fewer than 20 complete country/sector peers','Duplicate inferred issuer identity')]} for r in raw]
    rows,shortlist=screen.rank_rows(rows)
    with store.db() as c:
        for row in rows:
            reasons=row['reasons'][:]
            if row.get('rank_reason'):reasons.append(row['rank_reason'])
            c.execute('UPDATE market_observations SET score=?,peer_count=?,rank=?,shortlisted=?,reasons_json=?,features_json=? WHERE run_id=? AND listing_id=?',(row['score'],row['peer_count'],row['rank'],int(row['shortlisted']),json.dumps(list(dict.fromkeys(reasons))),json.dumps(row['features'],allow_nan=False),rid,row['listing']['id']))
        if final:
            digest=hashlib.sha256(json.dumps({'config':state(rid)['config'],'rows':[{k:r[k] for k in ['listing','features','score','rank','shortlisted']} for r in sorted(rows,key=lambda r:r['listing']['id'])]},sort_keys=True,allow_nan=False).encode()).hexdigest()
            c.execute('UPDATE market_runs SET cohort_hash=? WHERE id=?',(digest,rid))
            if state(rid)['auto_ai']:
                for position,row in enumerate(shortlist,1):c.execute('INSERT OR IGNORE INTO market_ai_queue VALUES(?,?,?,?,?,?,?,?,?)',(rid,row['listing']['id'],position,'pending',None,None,0,None,store.now()))
    return len(shortlist)


def scan(rid):
    with store.db() as c:c.execute("UPDATE market_runs SET status='running',updated_at=? WHERE id=?",(store.now(),rid))
    try:
        if not state(rid)['progress'].get('discovered') and not discover(rid):return
        if stopped(rid):return
        fx=state(rid)['progress'].get('fx')
        if not fx:
            progress(rid,'Loading reference FX');fx=sources.fx_rates();progress(rid,'Reference FX saved',fx=fx)
        if pending(rid,'US'):
            files,records=data.bulk_files(lambda message:progress(rid,message))
            if stopped(rid):return
            catalog,profiles,bulk=data.read_bulk(files,lambda message:progress(rid,message))
            progress(rid,'Screening the US exchange universe',bulk_sources=records)
            for index,raw in enumerate(pending(rid,'US')):
                if stopped(rid):return
                listing=json.loads(raw['listing_json']);symbol=listing['symbol'];company=catalog.get(symbol,{});profile=profiles.get(symbol,{})
                listing.update(sector=profile.get('sector','Unclassified'),industry=profile.get('industry',''),cik=str(company['cik_str']).zfill(10) if company.get('cik_str') else '',domicile=profile.get('domicile'))
                if company.get('title'):listing['name']=company['title']
                if listing['cik']:listing['issuer_key']='cik:'+listing['cik']
                classification,reason=sources.classify(listing['name'],'common stock',industry=listing['industry'])
                if classification!='candidate':listing.update(classification=classification,exclusion=reason)
                facts=bulk.get(symbol,{})
                out,reasons,warnings=screen.features(listing,facts,fx)
                save_result(rid,listing,out,reasons,warnings,records,status='excluded' if classification=='excluded' else None)
                if index%250==0:progress(rid,'Screening US financials and liquidity',last_symbol=symbol)
            refresh_ranks(rid)
        refresh_ranks(rid)
        progress(rid,'Screening UK completed-session liquidity')
        for index,raw in enumerate(pending(rid,'UK')):
            if stopped(rid):return
            listing=json.loads(raw['listing_json']);symbol=listing['symbol'];records=json.loads(raw['sources_json'])
            # Preserve Aquis coverage while refusing to guess Yahoo mappings.
            if listing['venue']=='Aquis':
                save_result(rid,listing,{},['Aquis price mapping requires verification'],[],records,'unmapped');continue
            try:
                progress(rid,'Checking UK '+symbol,last_symbol=symbol)
                price,price_sources=data.uk_price(listing);records+=price_sources
                factor=screen.fx_factor(price['quote_currency'],'GBP',fx)
                if factor is not None and price['quote_currency'] in ('GBp','GBX'):factor/=100
                liquidity=price['median_daily_value']*factor if factor is not None else None
                if liquidity is not None and liquidity<screen.POLICY['median_daily_value_min_gbp']:
                    save_result(rid,listing,{'price':price['price'],'price_currency':price['quote_currency'],'price_date':price['price_date'],'median_daily_value_gbp':liquidity,'liquidity_sessions':price['liquidity_sessions']},['Median daily traded value below £5m'],[],records);continue
                facts,facts_sources=data.uk_fundamentals(listing,price);records+=facts_sources
                out,reasons,warnings=screen.features(listing,facts,fx);save_result(rid,listing,out,reasons,warnings,records)
            except sources.SourceError as exc:
                if stopped(rid):return
                save_result(rid,listing,{},[str(exc)],[],records,'unavailable')
            if index%30==0:refresh_ranks(rid)
        if stopped(rid):return
        count=refresh_ranks(rid,True)
        with store.db() as c:c.execute("UPDATE market_runs SET status='complete',phase=?,updated_at=? WHERE id=?",(f'Scan complete; {count} companies shortlisted for AI due diligence',store.now(),rid))
    except Exception as exc:
        if STOP.is_set() or state(rid)['status']=='paused':return
        message=str(exc) if isinstance(exc,sources.SourceError) else 'Collection stopped unexpectedly. Checkpoints retained; resume to retry.'
        with store.db() as c:c.execute("UPDATE market_runs SET status='failed',phase=?,updated_at=? WHERE id=?",(message,store.now(),rid))


def collection_loop():
    while not STOP.is_set():
        with store.db() as c:row=c.execute("SELECT id FROM market_runs WHERE status='queued' ORDER BY created_at LIMIT 1").fetchone()
        if row:scan(row['id'])
        else:STOP.wait(2)


def ensure_company(listing):
    with store.db() as c:c.execute('INSERT OR IGNORE INTO companies VALUES(?,?,?,?)',(listing['symbol'],listing['name'],listing.get('cik',''),listing['sector']))


def queue_update(rid,lid,**changes):
    allowed={'status','report_id','rating_job_id','attempts','reason'}
    if not set(changes)<=allowed:raise ValueError('Invalid queue update')
    changes['updated_at']=store.now()
    with store.db() as c:c.execute('UPDATE market_ai_queue SET '+','.join(k+'=?' for k in changes)+' WHERE run_id=? AND listing_id=?',(*changes.values(),rid,lid))


def research_step(item):
    rid=item['run_id'];lid=item['listing_id']
    with store.db() as c:raw=c.execute('SELECT * FROM market_observations WHERE run_id=? AND listing_id=?',(rid,lid)).fetchone()
    listing=json.loads(raw['listing_json']);ensure_company(listing)
    try:
        if item['status']=='pending':
            if item['attempts']>=3:queue_update(rid,lid,status='failed',reason='Three interrupted or failed attempts; retry explicitly.');return
            context={'run_id':rid,'listing':listing,'features':json.loads(raw['features_json']),'score':raw['score'],'rank':raw['rank'],'model':screen.POLICY,'cohort_hash':state(rid)['cohort_hash'],'sources':json.loads(raw['sources_json'])}
            report=ai.start_report(listing['symbol'],focus='Screen '+rid[:8]+': reconcile the frozen candidate against primary disclosures, then provide detailed company due diligence.',force=True,screen_context=context)
            queue_update(rid,lid,status='dossier',report_id=report['id'],attempts=item['attempts']+1,reason=None)
        elif item['status']=='dossier':
            report=ai.get_report(item['report_id'])
            if report['status']=='failed':queue_update(rid,lid,status='pending' if item['attempts']<3 else 'failed',reason=report.get('error'));STOP.wait(20);return
            if report['status']!='complete':return
            review=(report['report'] or {}).get('screening_review',{})
            if review.get('status')!='supported':
                queue_update(rid,lid,status='needs_review',reason=review.get('summary') or 'AI could not reconcile the screen inputs. Original numbers retained.');return
            job=ratings.start([listing['symbol']])
            if job.get('symbols') and listing['symbol'] not in job['symbols']:return
            queue_update(rid,lid,status='rating',rating_job_id=job.get('id'))
        elif item['status']=='rating':
            if item['rating_job_id']:
                job=ratings.get_job(item['rating_job_id'])
                if job['status'] in ('queued','running'):return
                if job['status'] in ('failed','partial'):queue_update(rid,lid,status='failed',reason='Dossier saved but rating failed; retry this review.');return
            queue_update(rid,lid,status='complete',reason='AI reports supported inputs; source access is AI-reported, not independently audited.')
    except ai.AnalysisError as exc:
        message=str(exc)
        # Stop spending calls when sign-in/allowance is unavailable; retain the queue.
        queue_update(rid,lid,reason=message)
        STOP.wait(30)
    except Exception:queue_update(rid,lid,status='failed',reason='Review worker stopped for this company; earlier reports retained.')


def research_loop():
    while not STOP.is_set():
        with store.db() as c:
            item=c.execute("SELECT q.* FROM market_ai_queue q JOIN market_runs r ON r.id=q.run_id WHERE r.status='complete' AND r.auto_ai=1 AND q.status IN ('pending','dossier','rating') ORDER BY r.created_at,q.position LIMIT 1").fetchone()
        if item:research_step(dict(item))
        STOP.wait(3)


def overview():
    with store.db() as c:latest=c.execute('SELECT id FROM market_runs ORDER BY created_at DESC LIMIT 1').fetchone()
    if not latest:return {'run':None,'counts':{},'countries':{},'queue':{},'policy':screen.POLICY,'sectors':[]}
    rid=latest['id'];run=state(rid)
    with store.db() as c:
        counts={r[0]:r[1] for r in c.execute('SELECT status,count(*) FROM market_observations WHERE run_id=? GROUP BY status',(rid,))}
        counts.update(discovered=sum(counts.values()),scored=c.execute('SELECT count(*) FROM market_observations WHERE run_id=? AND score IS NOT NULL',(rid,)).fetchone()[0],shortlisted=c.execute('SELECT count(*) FROM market_observations WHERE run_id=? AND shortlisted=1',(rid,)).fetchone()[0])
        countries={r[0]:r[1] for r in c.execute('SELECT country,count(*) FROM market_observations WHERE run_id=? GROUP BY country',(rid,))}
        queue={r[0]:r[1] for r in c.execute('SELECT status,count(*) FROM market_ai_queue WHERE run_id=? GROUP BY status',(rid,))}
        sectors=[r[0] for r in c.execute('SELECT DISTINCT sector FROM market_observations WHERE run_id=? ORDER BY sector',(rid,))]
    return {'run':run,'counts':counts,'countries':countries,'queue':queue,'policy':screen.POLICY,'sectors':sectors,'coverage_note':'Current exchange snapshots: US listed/other-listed, LSE Main Market/AIM and Aquis. Securities are not the same as unique companies. OTC/private companies excluded; unresolved mappings stay visible.'}


def rows(rid,q='',country='',sector='',view='all',offset=0,limit=50):
    state(rid);where=['o.run_id=?'];params=[rid]
    if q:
        where.append('(o.symbol LIKE ? ESCAPE \'\\\' OR o.name LIKE ? ESCAPE \'\\\')');query=q.replace('\\','\\\\').replace('%','\\%').replace('_','\\_');params+=['%'+query+'%']*2
    if country:where.append('o.country=?');params.append(country)
    if sector:where.append('o.sector=?');params.append(sector)
    if view=='top100':where.append('o.shortlisted=1')
    elif view=='scored':where.append('o.score IS NOT NULL')
    elif view=='pending':where.append("o.status='pending'")
    elif view=='excluded':where.append("o.status IN ('excluded','ineligible','unmapped','unavailable')")
    elif view=='reviewed':where.append("a.status IN ('complete','needs_review')")
    elif view!='all':raise ai.AnalysisError('Unknown market table view.')
    clause=' AND '.join(where)
    with store.db() as c:
        count=c.execute('SELECT count(*) FROM market_observations o LEFT JOIN market_ai_queue a ON a.run_id=o.run_id AND a.listing_id=o.listing_id WHERE '+clause,params).fetchone()[0]
        result=c.execute('SELECT o.*,a.status AS ai_status,a.reason AS ai_reason,a.report_id FROM market_observations o LEFT JOIN market_ai_queue a ON a.run_id=o.run_id AND a.listing_id=o.listing_id WHERE '+clause+' ORDER BY o.score IS NULL,o.score DESC,o.listing_id LIMIT ? OFFSET ?',(*params,limit,offset)).fetchall()
    output=[]
    for row in result:
        item=dict(row)
        for key,target in [('listing_json','listing'),('features_json','features'),('reasons_json','reasons'),('warnings_json','warnings'),('sources_json','sources')]:item[target]=json.loads(item.pop(key))
        for meta in item['sources']:meta.pop('path',None)
        output.append(item)
    return {'rows':output,'total':count,'offset':offset,'limit':limit,'run_id':rid}


def export_csv(rid):
    # Bounded universe export, with blank missing values and explicit source flags.
    out=io.StringIO();writer=csv.writer(out);writer.writerow(['Symbol','Company','Country','Sector','State','Discovery score /100','Rank','Top 100','Market cap GBP','Median daily value GBP','FCF yield','Operating yield proxy','Financial period','Price date','AI status','Reasons','Source URLs','Model'])
    offset=0
    while True:
        batch=rows(rid,offset=offset,limit=500)['rows']
        if not batch:break
        for r in batch:
            f=r['features'];cells=[r['symbol'],r['name'],r['country'],r['sector'],r['status'],r['score'],r['rank'],bool(r['shortlisted']),f.get('market_cap_gbp'),f.get('median_daily_value_gbp'),f.get('fcf_yield'),f.get('operating_yield_proxy'),f.get('financial_period'),f.get('price_date'),r.get('ai_status'),'; '.join(r['reasons']),' | '.join(s['url'] for s in r['sources']),screen.POLICY['id']+' '+screen.POLICY['version']]
            writer.writerow(["'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v for v in cells])
        offset+=len(batch)
    return out.getvalue()
