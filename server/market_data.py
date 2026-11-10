"""Bulk US data and bounded UK quote/fact collection for the discovery screen."""
import hashlib
import json
import math
from datetime import datetime,timezone,timedelta
from pathlib import Path
import duckdb
from . import market_sources as source
from . import store

BULK_FILES=['company_tickers.json','stock_profile.parquet','stock_statement.parquet','stock_shares_outstanding.parquet','stock_prices.parquet']
FIN_KEYS={'total_revenue':'TotalRevenue','gross_profit':'GrossProfit','operating_income':'OperatingIncome','net_income':'NetIncome','operating_cash_flow':'OperatingCashFlow','capital_expenditure':'CapitalExpenditure','total_assets':'TotalAssets','total_debt':'TotalDebt','cash_cash_equivalents_and_short_term_investments':'CashCashEquivalentsAndShortTermInvestments','cash_and_cash_equivalents':'CashAndCashEquivalents','stockholders_equity':'StockholdersEquity','ordinary_shares_number':'OrdinarySharesNumber'}


def bulk_files(stage):
    record,spec=source.json_source(source.BULK_BASE+'spec.json','Bulk manifest',max_bytes=2_000_000)
    files={};records=[record]
    for name in BULK_FILES:
        stage('Loading public US '+name)
        key='US/'+name;url=source.BULK_BASE+'data/'+key;expected=spec.get('hashes',{}).get(key)
        # Reuse the exact checksummed files downloaded during this build's feasibility check.
        prepared=store.DATA/'source-cache'/name
        if prepared.exists() and expected:
            digest=hashlib.sha256()
            with prepared.open('rb') as f:
                for chunk in iter(lambda:f.read(4*1024*1024),b''):digest.update(chunk)
            if digest.hexdigest()==expected:
                folder=store.DATA/'market-snapshots';folder.mkdir(exist_ok=True);target=folder/expected
                if not target.exists():
                    import shutil
                    shutil.copyfile(prepared,target)
                with store.db() as c:
                    exists=c.execute('SELECT id FROM market_sources WHERE url=? AND sha256=?',(url,expected)).fetchone()
                    if not exists:
                        import uuid
                        c.execute('INSERT INTO market_sources VALUES(?,?,?,?,?,?,?,?)',(uuid.uuid4().hex,url,'Public US bulk via Defeat Beta',expected,str(target),store.now(),spec.get('files',{}).get(key),target.stat().st_size))
        metadata,path=source.acquire(url,'Public US bulk via Defeat Beta',expected_hash=expected,provided_at=spec.get('files',{}).get(key))
        files[name]=str(path);records.append(metadata)
    return files,records


def read_bulk(files,stage):
    c=duckdb.connect(config={'memory_limit':'512MB','threads':2})
    try:
        catalog=json.loads(Path(files['company_tickers.json']).read_text());catalog={r['ticker']:r for r in catalog.values()}
        profiles={r[0]:{'sector':source.sector_name(r[1]),'industry':r[2] or '','domicile':r[3],'profile_date':r[4]} for r in c.execute('SELECT symbol,sector,industry,country,report_date FROM read_parquet(?) QUALIFY row_number() OVER (PARTITION BY symbol ORDER BY report_date DESC)=1',[files['stock_profile.parquet']]).fetchall()}
        stage('Normalising US annual financial observations')
        keys=list(FIN_KEYS);params=','.join('?' for _ in keys)
        rows=c.execute('SELECT symbol,report_date,item_name,MAX(item_value) FROM read_parquet(?) WHERE period_type=\'annual\' AND report_date>=? AND item_name IN ('+params+') GROUP BY symbol,report_date,item_name',[files['stock_statement.parquet'],(datetime.now(timezone.utc).date()-timedelta(days=1400)).isoformat(),*keys]).fetchall()
        statements={}
        for symbol,day,key,value in rows:
            if value is not None:statements.setdefault(symbol,{}).setdefault(day,{})[key]=float(value)
        stage('Calculating completed-session US liquidity')
        today=datetime.now(timezone.utc).date().isoformat();earliest=(datetime.now(timezone.utc).date()-timedelta(days=430)).isoformat()
        prices=c.execute('''WITH bars AS (SELECT symbol,report_date,close,volume,row_number() OVER(PARTITION BY symbol ORDER BY report_date DESC) AS n FROM read_parquet(?) WHERE report_date<? AND report_date>=? AND close>0 AND volume>=0)
            SELECT symbol,max(report_date),arg_max(close,report_date),median(close*volume) FILTER (WHERE n<=60),count(*) FILTER (WHERE n<=60),max(CASE WHEN n=21 THEN close END),max(CASE WHEN n=252 THEN close END) FROM bars GROUP BY symbol''',[files['stock_prices.parquet'],today,earliest]).fetchall()
        shares={r[0]:(r[1],int(r[2])) for r in c.execute('SELECT symbol,report_date,shares_outstanding FROM read_parquet(?) WHERE shares_outstanding>0 AND report_date<=? QUALIFY row_number() OVER(PARTITION BY symbol ORDER BY report_date DESC)=1',[files['stock_shares_outstanding.parquet'],today]).fetchall()}
        price_by={r[0]:r for r in prices};data={}
        for symbol,periods in statements.items():
            dates=sorted([day for day,v in periods.items() if v.get('total_revenue') is not None],reverse=True)
            if not dates:continue
            day=dates[0];previous=next((d for d in dates[1:] if 300<=(datetime.fromisoformat(day)-datetime.fromisoformat(d)).days<=430),None)
            p=price_by.get(symbol);s=shares.get(symbol);item=catalog.get(symbol,{})
            data[symbol]={'period':day,'annual':periods[day],'previous_period':previous,'previous_assets':periods[previous].get('total_assets') if previous else None,'financial_currency':item.get('financial_currency'),'quote_currency':'USD','price_date':p[1] if p else None,'price':float(p[2]) if p and p[2] else None,'median_daily_value':float(p[3]) if p and p[3] is not None else None,'liquidity_sessions':p[4] if p else 0,'shares_date':s[0] if s else None,'shares':s[1] if s else None,'momentum_252_21':float(p[5]/p[6]-1) if p and p[5] and p[6] and p[6]>0 else None,'warning':'Bulk OHLC adjustment semantics not independently verified; liquidity and momentum are exploratory.'}
        return catalog,profiles,data
    finally:c.close()


def uk_price(listing):
    metadata,raw=source.json_source('https://query1.finance.yahoo.com/v8/finance/chart/'+listing['symbol']+'?range=2y&interval=1d&events=div%2Csplits','UK public daily prices',max_bytes=3_000_000)
    try:
        result=raw['chart']['result'][0];meta=result['meta'];quotes=result['indicators']['quote'][0];today=datetime.now(timezone.utc).date().isoformat()
        if meta.get('symbol','').upper()!=listing['symbol'].upper():raise ValueError('Symbol mismatch')
        bars=[]
        for i,ts in enumerate(result.get('timestamp',[])):
            day=datetime.fromtimestamp(ts,timezone.utc).date().isoformat()
            close=quotes.get('close',[])[i];volume=quotes.get('volume',[])[i]
            if day>=today:continue  # Freeze only completed prior calendar sessions, on both exchanges.
            if type(close) not in (int,float) or type(volume) not in (int,float) or not math.isfinite(close) or not math.isfinite(volume) or close<=0 or volume<0:continue
            bars.append((day,close,volume))
        bars.sort()
        if not bars:raise ValueError('No completed bars')
        import statistics
        data={'quote_currency':meta['currency'],'price_date':bars[-1][0],'price':bars[-1][1],'liquidity_sessions':min(60,len(bars)),'median_daily_value':statistics.median(b[1]*b[2] for b in bars[-60:]),'momentum_252_21':bars[-21][1]/bars[-252][1]-1 if len(bars)>=252 else None}
        return data,[metadata]
    except (KeyError,IndexError,TypeError,ValueError) as exc:raise source.SourceError('UK price/volume mapping unavailable or invalid.') from exc


def uk_fundamentals(listing,data):
    symbol=listing['symbol'];end=int(datetime.now(timezone.utc).timestamp());base='https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/'+symbol
    types=','.join('annual'+v for v in FIN_KEYS.values())
    metadata,raw=source.json_source(base+f'?symbol={symbol}&type={types}&period1=1577836800&period2={end//86400*86400}','UK public financials',max_bytes=3_000_000)
    periods={};currencies={};rows=raw.get('timeseries',{}).get('result') or []
    for row in rows:
        for key,vendor in FIN_KEYS.items():
            for point in row.get('annual'+vendor,[]):
                value=point.get('reportedValue',{}).get('raw');day=point.get('asOfDate')
                if type(value) in (int,float) and math.isfinite(value) and day and point.get('periodType')=='12M':
                    periods.setdefault(day,{})[key]=value
                    if key not in ('ordinary_shares_number',):currencies.setdefault(day,set()).add(point.get('currencyCode'))
    days=sorted([day for day,v in periods.items() if 'total_revenue' in v],reverse=True)
    if not days:raise source.SourceError('Annual financial observations unavailable for this UK symbol.')
    day=days[0];previous=next((d for d in days[1:] if 300<=(datetime.fromisoformat(day)-datetime.fromisoformat(d)).days<=430),None)
    if len(currencies.get(day,set()))!=1:raise source.SourceError('Conflicting or missing financial reporting currencies.')
    share_meta,share_raw=source.json_source(base+f'?symbol={symbol}&period1={(end//86400-180)*86400}&period2={end//86400*86400}','UK public shares outstanding',max_bytes=1_000_000)
    points=[(ts,value) for row in share_raw.get('timeseries',{}).get('result') or [] for ts,value in zip(row.get('timestamp',[]),row.get('shares_out',[])) if type(value) in (int,float) and value>0 and ts<=end]
    shares=max(points) if points else None
    return {**data,'period':day,'annual':periods[day],'previous_period':previous,'previous_assets':periods[previous].get('total_assets') if previous else None,'financial_currency':next(iter(currencies[day])),'shares':shares[1] if shares else None,'shares_date':datetime.fromtimestamp(shares[0],timezone.utc).date().isoformat() if shares else None},[metadata,share_meta]
