"""Small cross-sector ticker sample, not a universe-wide coverage estimate."""
import json
from datetime import datetime,timezone
from probe_public_sources import request,OUT

SYMBOLS=['QCOM','MSFT','NVDA','JPM','XOM','KO','JNJ','CAT','RGR','IRDM','HRL','HD','SHEL.L','SGE.L','JET2.L','AZN.L','RR.L','GAW.L','NXT.L','FEVR.L','W7L.L','CAPD.L','HSBA.L','BNZL.L']
FIELDS=['annualTotalRevenue','annualGrossProfit','annualOperatingIncome','annualNetIncome','annualOperatingCashFlow','annualCapitalExpenditure','annualTotalAssets','annualTotalDebt','annualCashCashEquivalentsAndShortTermInvestments','annualOrdinarySharesNumber','annualStockholdersEquity']
results=[];end=int(datetime.now(timezone.utc).timestamp())
for symbol in SYMBOLS:
    record,response=request('coverage_'+symbol,f'https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}',{'symbol':symbol,'type':','.join(FIELDS),'period1':1577836800,'period2':end})
    if response:
        data=response.json();rows=data.get('timeseries',{}).get('result') or [];found={}
        for row in rows:
            for field in FIELDS:
                points=row.get(field,[])
                if points:
                    p=max(points,key=lambda p:p.get('asOfDate',''));found[field]={'as_of':p.get('asOfDate'),'currency':p.get('currencyCode'),'value':p.get('reportedValue',{}).get('raw')}
        record.update(symbol=symbol,field_count=len(found),missing_fields=[f for f in FIELDS if f not in found],latest_fields=found)
    else:record.update(symbol=symbol,field_count=0,missing_fields=FIELDS)
    results.append(record);print(symbol,record['status'] if 'status' in record else 'error',record['field_count'],flush=True)
summary={'retrieved_at':datetime.now(timezone.utc).isoformat(),'scope':'24 named ticker requests, selected for variety, not a random or representative market sample; availability is not validated accuracy or eligibility.','fields_requested':FIELDS,'results':results}
(OUT/'financial-coverage-sample-2026-11-10.json').write_text(json.dumps(summary,indent=2))
print('At least 9/11:',sum(r['field_count']>=9 for r in results),'of',len(results),'All 11:',sum(r['field_count']==11 for r in results),flush=True)
