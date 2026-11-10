"""Summarise stored public-source samples without creating rankings or forecasts."""
import csv,io,json,math
from pathlib import Path
ROOT=Path('.marketdesk/research-probes')


def finite(value):return type(value) in (int,float) and math.isfinite(value)


def annual_points(payload,field):
    points=[]
    for row in payload.get('timeseries',{}).get('result',[]) or []:
        points.extend(p for p in row.get(field,[]) if p.get('periodType')=='12M' and finite(p.get('reportedValue',{}).get('raw')))
    return sorted(points,key=lambda p:p['asOfDate'],reverse=True)


def summarise(symbol):
    raw=json.loads((ROOT/('yahoo_fundamentals_'+symbol+'.raw')).read_text())
    points={key:annual_points(raw,key) for key in ['annualTotalRevenue','annualGrossProfit','annualOperatingIncome','annualNetIncome','annualOperatingCashFlow','annualCapitalExpenditure','annualTotalAssets','annualTotalDebt','annualCashCashEquivalentsAndShortTermInvestments','annualOrdinarySharesNumber','annualStockholdersEquity']}
    dates={key:value[0]['asOfDate'] for key,value in points.items() if value}
    currencies={key:value[0].get('currencyCode') for key,value in points.items() if value}
    metrics={};values={key:value[0]['reportedValue']['raw'] for key,value in points.items() if value}
    aligned=len(set(dates.values()))==1
    if aligned:
        ocf=values.get('annualOperatingCashFlow');capex=values.get('annualCapitalExpenditure');revenue=values.get('annualTotalRevenue')
        # This field's sampled provider convention uses negative cash outflows.
        # A positive value is not silently flipped; production requires reconciliation.
        if finite(ocf) and finite(capex) and capex<=0:metrics['free_cash_flow_sample']=ocf+capex
        if revenue and finite(values.get('annualOperatingIncome')):metrics['operating_margin_pct_sample']=100*values['annualOperatingIncome']/revenue
        if revenue and finite(values.get('annualNetIncome')):metrics['net_margin_pct_sample']=100*values['annualNetIncome']/revenue
    series=json.loads((ROOT/('yahoo_price_'+symbol+'.raw')).read_text())['chart']['result'][0]
    shares=json.loads((ROOT/('shares_'+symbol+'.raw')).read_text()).get('timeseries',{}).get('result',[])
    sharepoints=[(t,s) for row in shares for t,s in zip(row.get('timestamp',[]),row.get('shares_out',[]))]
    return {'symbol':symbol,'annual_fields_present':len(values),'annual_fields_requested':len(points),'provider_periods':dates,'provider_currency_metadata':currencies,'aligned_provider_periods':aligned,'raw_capex_sign':values.get('annualCapitalExpenditure'),'sample_calculations_not_issuer_verified':metrics,'annual_revenue_observations':len(points['annualTotalRevenue']),'daily_bars':len(series.get('timestamp',[])),'quote_currency':series['meta'].get('currency'),'current_shares_available':bool(sharepoints),'latest_share_observation':max(sharepoints) if sharepoints else None,'rank':None,'qualification':'Not assessed; this is a data availability sample, not a strategy result.'}


def run():
    samples=[summarise(s) for s in ['QCOM','SHEL.L','SGE.L','JET2.L']]
    counts={};candidates=[]
    for label,symbol_key in [('nasdaq_listed','Symbol'),('other_listed','ACT Symbol')]:
        rows=list(csv.DictReader(io.StringIO((ROOT/(label+'.raw')).read_text()),delimiter='|'))
        rows=[r for r in rows if not str(next(iter(r.values()),'')).startswith('File Creation Time')]
        retained=[r for r in rows if r.get('ETF')=='N' and r.get('Test Issue')=='N']
        counts[label]={'security_rows':len(rows),'non_etf_non_test_rows':len(retained)}
        candidates.extend({'symbol':r[symbol_key],'name':r['Security Name'],'source_file':label,'classification_status':'Unverified: common/preferred/warrant/unit/ADR/fund and issuer deduplication still required'} for r in retained)
    with (ROOT/'us-directory-candidates-2026-11-10.csv').open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=['symbol','name','source_file','classification_status']);writer.writeheader();writer.writerows(candidates)
    report={'scope':'Bounded source feasibility only. No app database writes, portfolio, forecasts or full-market coverage claims.','directories':counts,'samples':samples,'limitations':['SEC HTTP requests returned 403 on this host.','No universe-wide financial completeness rate measured.','Provider period labels and currency metadata require issuer reconciliation.','Current shares and vendor valuation observations do not automatically satisfy a verified issuer-share-count gate.','No top-100 queue was run; screening and eligibility must precede AI selection.']}
    (ROOT/'feasibility-summary-2026-11-10.json').write_text(json.dumps(report,indent=2))
    for sample in samples:print(sample['symbol'],sample['annual_fields_present'],'fields',sample['daily_bars'],'daily bars; currency',sample['quote_currency'],'recent shares',sample['current_shares_available'])
    print('US candidate security rows',len(candidates),'not deduplicated companies')

if __name__=='__main__':run()
