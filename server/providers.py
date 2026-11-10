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

_market_lock = threading.Lock()

def normalize_yahoo(payload, symbol, intraday_payload=None):
    """Validate Yahoo's public chart response without inventing missing observations."""
    import math
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo
    def number(value, positive=False):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value): return None
        return value if (not positive or value>0) else None
    try:
        result=payload['chart']['result'][0]
        meta=result['meta']
        price=number(meta.get('regularMarketPrice'),True)
        timestamp=number(meta.get('regularMarketTime'),True)
        if price is None or timestamp is None: raise ValueError('Missing quote')
        if meta.get('symbol','').upper()!=symbol.upper(): raise ValueError('Symbol mismatch')
        currency=meta.get('currency')
        if not isinstance(currency,str) or len(currency)!=3: raise ValueError('Missing currency')
        zone=ZoneInfo(meta.get('exchangeTimezoneName','UTC'))
        def parse_bars(result, daily=True):
            timestamps=result.get('timestamp',[])
            quote=result.get('indicators',{}).get('quote',[{}])[0]
            adjusted=result.get('indicators',{}).get('adjclose',[{}])[0].get('adjclose',[])
            parsed={}
            for i,ts in enumerate(timestamps):
                values={key:number(quote.get(key,[])[i],True) if i<len(quote.get(key,[])) else None for key in ('open','high','low','close')}
                if number(ts,True) is None or any(v is None for v in values.values()):continue
                if not values['low']<=min(values['open'],values['close'])<=max(values['open'],values['close'])<=values['high']:continue
                key=datetime.fromtimestamp(ts,zone).date().isoformat() if daily else int(ts)
                volume=number(quote.get('volume',[])[i]) if i<len(quote.get('volume',[])) else None
                parsed[key]={'time':key,**values,'volume':volume if volume is not None and volume>=0 else None,'adjusted_close':number(adjusted[i],True) if i<len(adjusted) else None}
            return [parsed[k] for k in sorted(parsed)]
        bars=parse_bars(result)
        intraday=[]
        if intraday_payload:
            intraday_result=intraday_payload.get('chart',{}).get('result')
            if intraday_result: intraday=parse_bars(intraday_result[0],False)
        # chartPreviousClose in a 1y chart is the start-of-range close, NOT yesterday.
        # Prefer the provider's day change, otherwise use completed daily closes.
        change=number(meta.get('regularMarketChangePercent'))
        previous=number(meta.get('previousClose'),True)
        quote_day=datetime.fromtimestamp(timestamp,zone).date().isoformat()
        if previous is None:
            prior=[b for b in bars if b['time']<quote_day]
            previous=prior[-1]['close'] if prior else None
        if change is None and previous:change=(price/previous-1)*100
        regular=meta.get('currentTradingPeriod',{}).get('regular',{})
        current=time.time()
        status='Regular session' if regular.get('start',0)<=current<regular.get('end',0) else 'Outside regular session'
        delay=number(meta.get('exchangeDataDelayedBy'))
        quote={'price':price,'change_pct':change,'previous_close':previous,'as_of':datetime.fromtimestamp(timestamp,timezone.utc).isoformat(),'currency':currency.upper(),'delay':f'{delay:g} min delayed' if delay is not None and delay>0 else 'Delay not specified by provider','market_status':status,'exchange':meta.get('fullExchangeName') or meta.get('exchangeName'),'provider':'Yahoo Finance','source':f'https://finance.yahoo.com/quote/{symbol}/','fetched_at':now(),'day_high':number(meta.get('regularMarketDayHigh'),True),'day_low':number(meta.get('regularMarketDayLow'),True),'volume':number(meta.get('regularMarketVolume')),'year_high':number(meta.get('fiftyTwoWeekHigh'),True),'year_low':number(meta.get('fiftyTwoWeekLow'),True)}
        return {'quote':quote,'bars':bars,'intraday':intraday,'intraday_interval':'5 minutes','notice':'Public Yahoo Finance feed for personal research. Refreshes every 60 seconds while viewed; not a guaranteed real-time exchange feed.'}
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        raise ProviderError('Yahoo Finance returned an invalid or unavailable quote. Previous data is retained.') from exc

def market_data(symbol, force=False):
    from datetime import datetime, timezone
    from urllib.parse import quote as urlquote
    with _market_lock:
        previous=cached(f'price:{symbol}')
        if previous and not force and (datetime.now(timezone.utc)-datetime.fromisoformat(previous['fetched_at'])).total_seconds()<45:
            return previous['data']
        try:
            endpoint=f'https://query1.finance.yahoo.com/v8/finance/chart/{urlquote(symbol,safe="")}'
            daily=fetch(endpoint,{'range':'1y','interval':'1d','events':'div,splits'})
            intraday=None
            try: intraday=fetch(endpoint,{'range':'1d','interval':'5m','includePrePost':'false'})
            except ProviderError: pass  # Quote/daily history still useful if intraday is unavailable.
            data=normalize_yahoo(daily,symbol,intraday)
            cache(f'price:{symbol}',data)
            return data
        except ProviderError as exc:
            if previous:return {**previous['data'],'stale':True,'warning':str(exc)}
            raise
