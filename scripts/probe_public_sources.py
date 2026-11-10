"""Bounded public-data feasibility probe; no login, credentials or app database writes.
Run with the project's Python environment. Results are observations, not coverage claims.
"""
import csv
import hashlib
import io
import json
import re
import time
from datetime import datetime,timezone
from pathlib import Path
import httpx

OUT=Path('.marketdesk/research-probes');OUT.mkdir(parents=True,exist_ok=True)
UA='MarketDesk public-data feasibility research https://github.com/ikshithij/MarketDesk'
results=[]

def request(label,url,params=None):
    started=time.monotonic()
    try:
        with httpx.Client(timeout=35,follow_redirects=True,headers={'User-Agent':UA}) as client:
            response=client.get(url,params=params)
        record={'label':label,'requested_url':url,'final_url':str(response.url),'status':response.status_code,'content_type':response.headers.get('content-type'),'bytes':len(response.content),'sha256':hashlib.sha256(response.content).hexdigest(),'retrieved_at':datetime.now(timezone.utc).isoformat(),'seconds':round(time.monotonic()-started,2)}
        response.raise_for_status()
        (OUT/(label+'.raw')).write_bytes(response.content)
        record['saved_as']=str(OUT/(label+'.raw'))
        return record,response
    except httpx.HTTPError as exc:
        record=locals().get('record',{'label':label,'requested_url':url,'error':type(exc).__name__})
        record['result']='failed';return record,None
    finally:time.sleep(.7)


def run():
    for label,url,kind in [
        ('nasdaq_listed','https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt','directory'),
        ('other_listed','https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt','directory'),
        ('sec_directory','https://www.sec.gov/files/company_tickers_exchange.json','sec_directory'),
        ('lse_reports','https://www.londonstockexchange.com/en/reports/issuers-and-instruments','html'),
        ('aquis_directory','https://www.aquis.eu/companies','html'),
        ('fca_nsm','https://data.fca.org.uk/','html')]:
        record,response=request(label,url)
        if response:
            if kind=='directory':
                rows=list(csv.DictReader(io.StringIO(response.text),delimiter='|'));rows=[r for r in rows if not str(next(iter(r.values()),'')).startswith('File Creation Time')]
                record.update(rows=len(rows),fields=list(rows[0]) if rows else [],non_etf_non_test_rows=sum(r.get('ETF')=='N' and r.get('Test Issue')=='N' for r in rows),note='Security rows, not distinct operating companies; further classification required.')
            elif kind=='sec_directory':
                payload=response.json();record.update(rows=len(payload.get('data',[])),fields=payload.get('fields'))
            else:
                links=re.findall(r'(?:https?[^\s"<>]+\.(?:xlsx|csv|zip)[^\s"<>]*|href=["\']([^"\']+\.(?:xlsx|csv|zip)[^"\']*)["\'])',response.text)
                record.update(download_links=links[:20],html_title=(re.findall(r'<title[^>]*>(.*?)</title>',response.text,re.S) or [''])[0])
        results.append(record);print(json.dumps(record),flush=True)
    for symbol,cik in [('QCOM','0000804328'),('NVDA','0001045810'),('MSFT','0000789019'),('SHEL','0001306965')]:
        record,response=request('sec_facts_'+symbol,f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json')
        if response:
            payload=response.json();namespaces=payload.get('facts',{});record.update(entity=payload.get('entityName'),taxonomies={k:len(v) for k,v in namespaces.items()})
            wanted=['Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','GrossProfit','OperatingIncomeLoss','NetIncomeLoss','NetCashProvidedByUsedInOperatingActivities','PaymentsToAcquirePropertyPlantAndEquipment','Assets','StockholdersEquity','CashAndCashEquivalentsAtCarryingValue','CommonStockSharesOutstanding','EntityCommonStockSharesOutstanding','Revenue','CashFlowsFromUsedInOperatingActivities','PurchaseOfPropertyPlantAndEquipment','ProfitLoss']
            record['candidate_fields']={ns:[key for key in wanted if key in facts] for ns,facts in namespaces.items()}
        results.append(record);print(json.dumps(record),flush=True)
    types=['annualTotalRevenue','annualGrossProfit','annualOperatingIncome','annualNetIncome','annualOperatingCashFlow','annualCapitalExpenditure','annualTotalAssets','annualTotalDebt','annualCashCashEquivalentsAndShortTermInvestments','annualOrdinarySharesNumber','annualStockholdersEquity']
    end=int(datetime.now(timezone.utc).timestamp())
    for symbol in ['QCOM','SHEL.L','SGE.L','JET2.L']:
        record,response=request('yahoo_fundamentals_'+symbol,f'https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}',{'symbol':symbol,'type':','.join(types),'period1':1577836800,'period2':end})
        if response:
            payload=response.json();rows=payload.get('timeseries',{}).get('result') or []
            fields={}
            for row in rows:
                for key in types:
                    points=row.get(key,[])
                    if points:
                        p=sorted(points,key=lambda p:p.get('asOfDate',''))[-1];fields[key]={'as_of':p.get('asOfDate'),'period_type':p.get('periodType'),'currency':p.get('currencyCode'),'value':p.get('reportedValue',{}).get('raw')}
            record.update(fields=fields,error=payload.get('timeseries',{}).get('error'),fields_present=len(fields),fields_requested=len(types),note='Convenience data only; issuer alignment and taxonomy reconciliation not yet verified.')
        results.append(record);print(json.dumps(record),flush=True)
        record,response=request('yahoo_price_'+symbol,f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}',{'range':'2y','interval':'1d','events':'div,splits'})
        if response:
            payload=response.json();rows=payload.get('chart',{}).get('result') or []
            if rows:
                row=rows[0];meta=row.get('meta',{});record.update(symbol=meta.get('symbol'),currency=meta.get('currency'),bar_count=len(row.get('timestamp',[])),has_adjusted_close=bool(row.get('indicators',{}).get('adjclose')),has_volume=bool(row.get('indicators',{}).get('quote',[{}])[0].get('volume')),quote_time=meta.get('regularMarketTime'),available_market_cap=meta.get('marketCap'),available_shares=meta.get('sharesOutstanding'))
        results.append(record);print(json.dumps(record),flush=True)
    target=OUT/'source-probe-2026-11-10.json';target.write_text(json.dumps({'run_at':datetime.now(timezone.utc).isoformat(),'scope':'Bounded feasibility sample; no accounts, no keys; does not establish universe-wide financial coverage','results':results},indent=2))
    print('Saved',target,flush=True)

if __name__=='__main__':run()
