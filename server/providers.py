"""Server-side providers with explicit provenance, bounded requests and no fallback fabrication."""
import os, time, threading
import httpx
from .store import cached, cache, settings, now
from .finance import statements, metrics

_lock=threading.Lock()
_last=0.

class ProviderError(Exception): pass

def fetch(url, params=None, sec=False):
    global _last
    headers={'User-Agent':'MarketDesk/0.1'}
    if sec:
        contact=settings().get('sec_contact') or os.getenv('SEC_CONTACT','')
        if '@' not in contact: raise ProviderError('Add your SEC contact email in Settings to enable filings and financials.')
        headers['User-Agent']=f'MarketDesk/0.1 {contact}'
    with _lock:  # conservative global limiter, including retries
        time.sleep(max(0,0.6-(time.monotonic()-_last)))
        _last=time.monotonic()
        try:
            with httpx.Client(timeout=30,follow_redirects=False) as client:
                response=client.get(url,params=params,headers=headers)
                response.raise_for_status()
                data=response.json()
        except (httpx.HTTPError,ValueError) as exc:
            # Never leak credential-bearing URLs or upstream exception details.
            raise ProviderError('Provider request failed. Check connectivity, access and rate limits; previous data is retained.') from exc
    return data

def sec_company(company):
    cik=company['cik']; url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
    raw=fetch(url,sec=True)
    annual=statements(raw); quarterly=statements(raw,'quarterly')
    submissions=fetch(f'https://data.sec.gov/submissions/CIK{cik}.json',sec=True)
    recent=submissions.get('filings',{}).get('recent',{})
    filings=[]
    for i,form in enumerate(recent.get('form',[])[:100]):
        if form not in ('10-K','10-Q','8-K','20-F','4','13F-HR'): continue
        acc=recent['accessionNumber'][i]; document=recent['primaryDocument'][i]
        filings.append({'form':form,'date':recent['filingDate'][i],'accession':acc,'url':f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace("-","")}/{document}'})
    data={'annual':annual,'quarterly':quarterly,'metrics':metrics(annual),'filings':filings[:25], 'description':submissions.get('sicDescription'),'source':url,'provider':'SEC EDGAR','kind':'reported','fetched_at':now()}
    cache(f'sec:{company["symbol"]}',data)
    return data

def alpha(symbol):
    key=os.getenv('ALPHA_VANTAGE_API_KEY')
    if not key: raise ProviderError('Set ALPHA_VANTAGE_API_KEY in your local .env to enable market prices.')
    raw=fetch('https://www.alphavantage.co/query',{'function':'TIME_SERIES_DAILY_ADJUSTED','symbol':symbol,'apikey':key,'outputsize':'compact'})
    series=raw.get('Time Series (Daily)')
    if not series: raise ProviderError('Adjusted daily history is unavailable. Your provider may require a paid entitlement or the request quota has been reached.')
    bars=[]
    try:
        for day,row in sorted(series.items()):
            bar={'time':day,'open':float(row['1. open']),'high':float(row['2. high']),'low':float(row['3. low']),'close':float(row['4. close']),'adjusted_close':float(row['5. adjusted close']),'volume':float(row['6. volume'])}
            if min(bar[k] for k in ('open','high','low','close','adjusted_close'))<=0: raise ValueError()
            bars.append(bar)
    except (ValueError,KeyError,TypeError) as exc: raise ProviderError('Provider returned invalid daily history.') from exc
    if not bars: raise ProviderError('Provider returned no price history.')
    quote={'price':bars[-1]['close'],'change_pct':(bars[-1]['close']/bars[-2]['close']-1)*100 if len(bars)>1 else None,'as_of':bars[-1]['time'],'currency':'USD','delay':'end-of-day','provider':'Alpha Vantage','source':'https://www.alphavantage.co/documentation/#dailyadj','fetched_at':now()}
    cache(f'price:{symbol}',{'quote':quote,'bars':bars})
    return quote

def fred():
    key=os.getenv('FRED_API_KEY')
    if not key: raise ProviderError('Set FRED_API_KEY in .env to enable macroeconomic indicators.')
    result=[]
    for series,name,unit in [('DGS10','US 10-year Treasury','%'),('FEDFUNDS','Federal funds rate','%'),('CPIAUCSL','US consumer price index','index'),('UNRATE','US unemployment','%')]:
        raw=fetch('https://api.stlouisfed.org/fred/series/observations',{'series_id':series,'api_key':key,'file_type':'json','sort_order':'desc','limit':10})
        points=[p for p in raw.get('observations',[]) if p.get('value')!='.']
        if points:
            p=points[0];result.append({'name':name,'series':series,'value':float(p['value']),'as_of':p['date'],'unit':unit,'source':f'https://fred.stlouisfed.org/series/{series}'})
    cache('macro',{'items':result,'fetched_at':now(),'provider':'FRED'})
    return result
