"""Bounded public-data acquisition and deterministic exchange-directory adapters."""
import csv
import hashlib
import io
import json
import re
import threading
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from zipfile import ZipFile
import httpx
from . import store

UA='MarketDesk/0.2 personal research https://github.com/ikshithij/MarketDesk'
PACE=threading.Lock()
LAST=0.0
STOP=threading.Event()
BULK_BASE='https://huggingface.co/datasets/defeatbeta/yahoo-finance-data/resolve/main/'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

class SourceError(Exception):pass


def acquire(url,kind,max_bytes=700_000_000,expected_hash=None,provided_at=None,max_age_hours=24):
    """Immutable content-addressed files; cache by URL, never log signed redirects."""
    global LAST
    folder=store.DATA/'market-snapshots';folder.mkdir(parents=True,exist_ok=True)
    with store.db() as c:
        prior=c.execute('SELECT * FROM market_sources WHERE url=? ORDER BY retrieved_at DESC LIMIT 1',(url,)).fetchone()
    if prior:
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(prior['retrieved_at'])).total_seconds()
        path=Path(prior['path'])
        if age<max_age_hours*3600 and path.is_file() and (not expected_hash or prior['sha256']==expected_hash):return dict(prior),path
    temporary=folder/(uuid.uuid4().hex+'.part')
    try:
        for attempt in range(3):
            if STOP.is_set():raise SourceError('Collection paused; progress is saved.')
            with PACE:
                if STOP.wait(max(0,1-(time.monotonic()-LAST))):raise SourceError('Collection paused; progress is saved.')
                LAST=time.monotonic()
            try:
                with httpx.Client(timeout=httpx.Timeout(90,connect=20),follow_redirects=True,headers={'User-Agent':UA}) as client:
                    with client.stream('GET',url) as response:
                        if response.status_code in (429,502,503,504):
                            if attempt==2:raise SourceError('Public provider unavailable or rate-limited; retry later.')
                            try:delay=min(120,max(3,float(response.headers.get('Retry-After',3*2**attempt))))
                            except ValueError:delay=3*2**attempt
                            if STOP.wait(delay):raise SourceError('Collection paused; progress is saved.')
                            continue
                        response.raise_for_status();size=0;digest=hashlib.sha256()
                        with temporary.open('wb') as target:
                            for chunk in response.iter_bytes(1024*1024):
                                if STOP.is_set():raise SourceError('Collection paused; progress is saved.')
                                size+=len(chunk)
                                if size>max_bytes:raise SourceError('Source exceeded the bounded download size.')
                                digest.update(chunk);target.write(chunk)
                sha=digest.hexdigest()
                if expected_hash and sha!=expected_hash:raise SourceError('Bulk source checksum differs from its manifest. Refresh the run rather than accepting unverified bytes.')
                path=folder/sha
                if not path.exists():temporary.replace(path)
                else:temporary.unlink(missing_ok=True)
                record={'id':uuid.uuid4().hex,'url':url,'kind':kind,'sha256':sha,'path':str(path),'retrieved_at':store.now(),'provided_at':provided_at,'bytes':size}
                with store.db() as c:c.execute('INSERT INTO market_sources VALUES(?,?,?,?,?,?,?,?)',tuple(record[k] for k in ['id','url','kind','sha256','path','retrieved_at','provided_at','bytes']))
                return record,path
            except httpx.HTTPStatusError as exc:raise SourceError(f'Public source returned HTTP {exc.response.status_code}; previous snapshots retained.') from exc
            except (httpx.HTTPError,OSError) as exc:
                if attempt==2:raise SourceError('Public-source connection failed; progress and previous snapshots retained.') from exc
                if STOP.wait(2**attempt):raise SourceError('Collection paused; progress is saved.')
        raise SourceError('Source request did not complete.')
    finally:temporary.unlink(missing_ok=True)


def json_source(url,kind,**kwargs):
    record,path=acquire(url,kind,**kwargs)
    try:return record,json.loads(path.read_text())
    except (ValueError,UnicodeError) as exc:raise SourceError('Public source returned invalid JSON.') from exc


def canonical_name(name):return re.sub(r'[^A-Z0-9]','',name.upper())


def classify(name,instrument='',industry='',test=False,etf=False):
    text=(name+' '+instrument).lower()
    if test:return 'excluded','Test security'
    if etf or re.search(r'\b(etf|etn|exchange.traded|ucits|closed.end fund|investment trust|investment fund|investment company|income fund|mutual fund)\b',text):return 'excluded','Fund or exchange-traded product'
    if re.search(r'\b(warrant[s]?|preferred|preference|rights|debenture[s]?|notes|bond[s]?|units|unit[s]? each|depositary|depository|adr|gdr)\b',text):return 'excluded','Non-ordinary security or unresolved depositary ratio'
    if any(word in industry.lower() for word in ['banks','insurance','reit','real estate','property investment']):return 'excluded','Accounting type outside the initial operating-company screen'
    if re.search(r'\b(bank|bancorp|bancshares|insurance|reinsurance|reit)\b',name.lower()):return 'excluded','Accounting type outside the initial operating-company screen'
    if 'acquisition corp' in text or 'acquisition company' in text:return 'excluded','Acquisition vehicle / operating history unresolved'
    if instrument and not re.search(r'\b(ord|ordinary|common|shrs|stock|shares)\b',text):return 'unmapped','Ordinary share classification unresolved'
    return 'candidate',None


def nasdaq_rows(text,other=False):
    output=[]
    for row in csv.DictReader(io.StringIO(text),delimiter='|'):
        symbol=row.get('ACT Symbol' if other else 'Symbol','')
        if not symbol or symbol.startswith('File Creation Time'):continue
        name=row.get('Security Name','').strip();exchange={'A':'NYSE American','N':'NYSE','P':'NYSE Arca','Z':'Cboe','V':'IEX'}.get(row.get('Exchange'),'Other US') if other else 'Nasdaq'
        status,reason=classify(name,'stock',test=row.get('Test Issue')=='Y',etf=row.get('ETF')=='Y')
        provider=symbol.replace('.','-')
        if not re.fullmatch(r'[A-Z0-9][A-Z0-9.-]{0,24}',provider):status,reason='unmapped','Provider symbol requires verified mapping'
        output.append({'id':'US:'+exchange+':'+symbol,'symbol':provider,'name':name,'country':'US','sector':'Unclassified','industry':'','venue':exchange,'isin':'','issuer_key':'name:'+canonical_name(name.split(' - ')[0]),'classification':status,'exclusion':reason,'currency':'USD','domicile':None,'cik':''})
    if not output:raise SourceError('US directory schema changed or was empty.')
    return output


def xlsx_rows(path,sheet='xl/worksheets/sheet1.xml'):
    """Read a bounded published input workbook; no workbook authoring or extraction."""
    with ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist())>400_000_000:raise SourceError('UK directory decompression exceeds the size limit.')
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rows=ET.fromstring(z.read(sheet)).find('m:sheetData',NS)
        for row in rows:
            result={}
            for cell in row:
                ref=re.sub(r'\d','',cell.attrib.get('r',''));value=cell.find('m:v',NS)
                if value is not None:result[ref]=strings[int(value.text)] if cell.attrib.get('t')=='s' else value.text
                elif cell.attrib.get('t')=='inlineStr':result[ref]=''.join(cell.itertext())
            yield result


def sector_name(value):
    value=(value or '').strip()
    return {'Financials':'Financial Services','Health Care':'Healthcare','Telecommunications':'Communication Services','Basic Materials':'Basic Materials'}.get(value,value or 'Unclassified')


def lse_rows(path):
    output=[];headers=None
    for cells in xlsx_rows(path):
        if cells.get('A')=='TIDM' and cells.get('D')=='ISIN':headers=cells;continue
        if headers is None or not cells.get('A') or not cells.get('D'):continue
        row={headers.get(k,k):str(v).strip() for k,v in cells.items()}
        symbol=row['TIDM'];isin=row['ISIN'];name=row.get('Issuer Name',symbol);kind=row.get('MiFIR Identifier Code','')
        industry=row.get('ICB Super-Sector Name','');status,reason=classify(name,row.get('Instrument Name','')+' '+kind,industry=industry,etf=kind=='ETFS')
        if kind!='SHRS':status,reason='excluded','Non-ordinary equity instrument'
        if row.get('FCA Listing Category','').lower().find('investment')>=0:status,reason='excluded','Listed investment vehicle'
        provider=symbol.rstrip('.').replace('.','-')+'.L'
        output.append({'id':'UK:XLON:'+isin+':'+symbol,'symbol':provider,'name':name,'country':'UK','sector':sector_name(row.get('ICB Industry')),'industry':industry,'venue':row.get('LSE Market','LSE'),'isin':isin,'issuer_key':'name:'+canonical_name(name),'classification':status,'exclusion':reason,'currency':row.get('Trading Currency'),'domicile':row.get('Country of Incorporation'),'cik':''})
    if not output:raise SourceError('LSE instrument columns changed or returned no rows.')
    return output


def aquis_rows(text):
    output=[]
    for row in csv.DictReader(io.StringIO(text)):
        if not row.get('isin') or not row.get('ticker'):continue
        symbol=row['ticker'];name=row.get('description') or row.get('issuer') or symbol;isin=row['isin']
        status,reason=classify(name,'ordinary' if row.get('instrument_type')=='ORD' else row.get('instrument_type',''),test=row.get('test_stock')!='0')
        if row.get('instrument_type')!='ORD':status,reason='excluded','Non-ordinary security'
        if row.get('is_tradeable')!='1':status,reason='excluded','Not marked tradable by source'
        output.append({'id':'UK:'+row.get('mic','AQSE')+':'+isin+':'+symbol,'symbol':symbol,'name':name,'country':'UK','sector':'Unclassified','industry':'','venue':'Aquis','isin':isin,'issuer_key':'name:'+canonical_name(row.get('issuer') or name),'classification':status,'exclusion':reason,'currency':row.get('currency'),'domicile':row.get('origin_country'),'cik':''})
    return output


def fx_rates():
    record,path=acquire('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml','ECB reference FX',max_bytes=1_000_000)
    root=ET.fromstring(path.read_bytes());rates={'EUR':1.0};day=None
    for node in root.iter():
        if 'time' in node.attrib:day=node.attrib['time']
        if 'currency' in node.attrib:rates[node.attrib['currency']]=float(node.attrib['rate'])
    if not day or 'GBP' not in rates or 'USD' not in rates:raise SourceError('ECB exchange-rate fields unavailable.')
    return {'date':day,'per_eur':rates,'source':record}
