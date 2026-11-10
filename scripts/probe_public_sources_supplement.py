"""Follow-up bounded probes for price-sensitive inputs and official UK downloads."""
import json,csv,io,time
import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from probe_public_sources import request,OUT

results=[]
for label,url in [('lse_issuer_metadata','https://docs.londonstockexchange.com/reports/issuers/latest.json'),('lse_instrument_metadata','https://docs.londonstockexchange.com/reports/instruments/latest.json')]:
    record,response=request(label,url);results.append(record)
    if response is None:continue
    meta=response.json()
    item=next(item for item in meta['Data'] if item['fileType']=='xlsx')
    record,response=request(label+'_file',item['downloadLink'])
    record['publication_date']=item['publishedDate']
    record['valid_zip_header']=bool(response and response.content[:2]==b'PK')
    results.append(record);print(json.dumps(record),flush=True)
record,response=request('aquis_security_list','https://aquis-public-files.s3.eu-west-2.amazonaws.com/aqse/security_web.csv');results.append(record)
rows=list(csv.DictReader(io.StringIO(response.text))) if response is not None else []
print('Aquis security rows',len(rows),'ordinary rows',sum(r.get('instrument_type')=='ORD' for r in rows),'tradable ordinary non-test',sum(r.get('instrument_type')=='ORD' and r.get('is_tradeable')=='1' and r.get('test_stock')=='0' for r in rows),flush=True)
results.append({'label':'aquis_rows','rows':len(rows),'ordinary_rows':sum(r.get('instrument_type')=='ORD' for r in rows),'tradable_ordinary_non_test':sum(r.get('instrument_type')=='ORD' and r.get('is_tradeable')=='1' and r.get('test_stock')=='0' for r in rows),'fields':list(rows[0]) if rows else []})
end=int(datetime.now(timezone.utc).timestamp())
for symbol in ['QCOM','SHEL.L','SGE.L','JET2.L']:
    url=f'https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}'
    record,response=request('shares_'+symbol,url,{'symbol':symbol,'period1':end-180*86400,'period2':end})
    if response:
        payload=response.json();rows=payload.get('timeseries',{}).get('result') or []
        points=[(ts,value) for row in rows for ts,value in zip(row.get('timestamp',[]),row.get('shares_out',[]))]
        record['points']=len(points)
        if points:
            latest=max(points);record['latest']={'date':datetime.fromtimestamp(latest[0],timezone.utc).isoformat(),'shares':latest[1]}
    results.append(record);print(json.dumps(record),flush=True)
    fields=['trailingMarketCap','trailingEnterpriseValue','trailingPeRatio','annualCashAndCashEquivalents','quarterlyOrdinarySharesNumber','annualMinorityInterest','annualPreferredStockEquity']
    record,response=request('valuation_'+symbol,url,{'symbol':symbol,'type':','.join(fields),'period1':end-5*366*86400,'period2':end})
    if response:
        data=response.json();rows=data.get('timeseries',{}).get('result') or [];found={}
        for row in rows:
            for field in fields:
                points=row.get(field,[])
                if points:
                    latest=max(points,key=lambda p:p.get('asOfDate',''));found[field]={'as_of':latest.get('asOfDate'),'currency':latest.get('currencyCode'),'value':latest.get('reportedValue',{}).get('raw')}
        record['fields']=found
    results.append(record);print(json.dumps(record),flush=True)
record,response=request('ecb_fx','https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
if response is not None:
    root=ET.fromstring(response.content)
    rates={n.attrib['currency']:float(n.attrib['rate']) for n in root.iter() if 'currency' in n.attrib}
    record['reference_date']=next(n.attrib['time'] for n in root.iter() if 'time' in n.attrib)
    record['usd_per_gbp']=rates['USD']/rates['GBP']
    record['meaning']='Daily research reference rate, not an executable broker FX rate.'
results.append(record);print(json.dumps(record),flush=True)
(OUT/'supplemental-probe-2026-11-10.json').write_text(json.dumps({'run_at':datetime.now(timezone.utc).isoformat(),'results':results},indent=2))
