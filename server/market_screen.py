"""Deterministic, versioned exploratory discovery calculations; never forecasts."""
import bisect
import json
import math
from collections import defaultdict
from datetime import date,datetime,timezone
from pathlib import Path

POLICY=json.loads((Path(__file__).resolve().parents[1]/'research/public_screen_v1.json').read_text())
FIELDS=['gross_profit','operating_cash_flow','net_income','operating_income','capital_expenditure','total_assets','total_revenue','total_debt','cash_cash_equivalents_and_short_term_investments']
SCORE_FIELDS=['gross_profit_to_assets','cash_flow_to_assets','negative_accruals','fcf_yield','operating_yield_proxy']


def number(v):return type(v) in (int,float) and math.isfinite(v)

def age(day,today):
    try:return (today-date.fromisoformat(str(day)[:10])).days
    except (ValueError,TypeError):return None

def fx_factor(origin,target,fx):
    origin='GBP' if origin in ('GBp','GBX') else origin
    target='GBP' if target in ('GBp','GBX') else target
    if origin==target:return 1.0
    rates=fx.get('per_eur',{})
    if origin not in rates or target not in rates or rates[origin]<=0:return None
    return rates[target]/rates[origin]


def features(listing,data,fx,today=None):
    today=today or datetime.now(timezone.utc).date();reasons=[];warnings=[];out={}
    if listing['classification']!='candidate':return {},[listing.get('exclusion') or 'Listing classification unresolved'],[]
    if listing.get('sector') in ('Unclassified','',None):reasons.append('Sector unavailable')
    if listing.get('venue')=='Aquis':reasons.append('Aquis price mapping requires verification')
    period=data.get('period');a=age(period,today)
    if a is None or a<0 or a>POLICY['annual_age_max_days']:reasons.append('Annual financial period missing or stale')
    share_age=age(data.get('shares_date'),today)
    if share_age is None or not 0<=share_age<=POLICY['share_observation_age_max_days']:reasons.append('Recent shares outstanding unavailable')
    pa=age(data.get('price_date'),today)
    if pa is None or not 0<=pa<=POLICY['price_age_max_days']:reasons.append('Completed-session price missing or stale')
    fa=age(fx.get('date'),today)
    if fa is None or not 0<=fa<=POLICY['fx_age_max_days']:reasons.append('FX reference missing or stale')
    vals=data.get('annual',{});missing=[key for key in FIELDS if not number(vals.get(key))]
    if missing:reasons.append('Missing financial fields: '+', '.join(missing))
    previous_assets=data.get('previous_assets');previous_date=data.get('previous_period')
    try:span=age(previous_date,date.fromisoformat(period)) if period and previous_date else None
    except (ValueError,TypeError):span=None
    if not number(previous_assets) or previous_assets<=0 or span is None or not 300<=span<=430:reasons.append('Comparable opening annual assets unavailable')
    price=data.get('price');shares=data.get('shares');qcur=data.get('quote_currency');fcur=data.get('financial_currency')
    to_gbp=fx_factor(qcur,'GBP',fx);to_fin=fx_factor(qcur,fcur,fx)
    if qcur in ('GBp','GBX'):
        if to_gbp is not None:to_gbp/=100
        if to_fin is not None:to_fin/=100
    if to_gbp is None or to_fin is None or not fcur:reasons.append('Quote/reporting currency conversion unresolved')
    mcap_gbp=mcap_fin=None
    if number(price) and price>0 and number(shares) and shares>0 and to_gbp is not None and to_fin is not None:
        mcap_gbp=price*shares*to_gbp;mcap_fin=price*shares*to_fin
        if mcap_gbp<POLICY['market_cap_min_gbp']:reasons.append('Market cap below £1bn')
    else:reasons.append('Price or shares invalid')
    liquidity=data.get('median_daily_value');sessions=data.get('liquidity_sessions',0)
    liq_gbp=liquidity*to_gbp if number(liquidity) and to_gbp is not None else None
    if sessions<POLICY['liquidity_sessions'] or liq_gbp is None:reasons.append('60 completed liquidity observations unavailable')
    elif liq_gbp<POLICY['median_daily_value_min_gbp']:reasons.append('Median daily traded value below £5m')
    if number(vals.get('net_income')) and vals['net_income']<=0:reasons.append('Annual net income not positive')
    if number(vals.get('operating_cash_flow')) and vals['operating_cash_flow']<=0:reasons.append('Annual operating cash flow not positive')
    if number(vals.get('capital_expenditure')) and vals['capital_expenditure']>0:reasons.append('Capex sign needs source reconciliation')
    if number(vals.get('total_assets')) and vals['total_assets']<=0:reasons.append('Assets denominator not positive')
    out={'financial_period':period,'financial_currency':fcur,'price':price,'price_currency':'GBX' if qcur=='GBp' else qcur,'price_date':data.get('price_date'),'shares':shares,'shares_date':data.get('shares_date'),'market_cap_gbp':mcap_gbp,'median_daily_value_gbp':liq_gbp,'liquidity_sessions':sessions,'fx_date':fx.get('date'),'annual':vals,'previous_assets':previous_assets,'previous_period':previous_date}
    if not missing:
        capex=vals['capital_expenditure'];ocf=vals['operating_cash_flow'];revenue=vals['total_revenue']
        fcf=ocf+capex if capex<=0 else None
        ev=mcap_fin+vals['total_debt']-vals['cash_cash_equivalents_and_short_term_investments'] if mcap_fin is not None else None
        if ev is None or ev<=0:reasons.append('Enterprise value proxy not positive')
        average=(vals['total_assets']+previous_assets)/2 if number(previous_assets) else None
        out.update(free_cash_flow=fcf,enterprise_value_proxy=ev,market_cap_reporting_currency=mcap_fin,
                   gross_profit_to_assets=vals['gross_profit']/average if average and average>0 else None,
                   cash_flow_to_assets=ocf/average if average and average>0 else None,
                   negative_accruals=(ocf-vals['net_income'])/average if average and average>0 else None,
                   fcf_yield=fcf/mcap_fin if fcf is not None and mcap_fin and mcap_fin>0 else None,
                   operating_yield_proxy=vals['operating_income']/ev if ev and ev>0 else None,
                   operating_margin=vals['operating_income']/revenue if revenue>0 else None,
                   net_margin=vals['net_income']/revenue if revenue>0 else None)
    out['momentum_252_21']=data.get('momentum_252_21')
    warnings=['Exploratory vendor financials; original fiscal dates/publication times not reconciled.','EV and liquidity use the declared discovery proxies; not LT-QV-001.','Trading 212 listing availability and historical corporate actions are unverified.']
    if data.get('warning'):warnings.append(data['warning'])
    return out,list(dict.fromkeys(reasons)),warnings


def percentile(value,ordered):
    # rank starts at one, ties get average rank; matches the frozen contract.
    lo=bisect.bisect_left(ordered,value);hi=bisect.bisect_right(ordered,value)
    return ((lo+hi-1)/2)/(len(ordered)-1) if len(ordered)>1 else None


def rank_rows(rows):
    groups=defaultdict(list)
    seen=set()
    for row in sorted(rows,key=lambda r:r['listing']['id']):
        row.update(score=None,rank=None,peer_count=0,top_candidate=False)
        if row['status']=='ready' and all(number(row['features'].get(k)) for k in SCORE_FIELDS):
            issuer=row['listing']['issuer_key']
            if issuer in seen:row['rank_reason']='Duplicate inferred issuer identity';continue
            seen.add(issuer);groups[(row['listing']['country'],row['listing']['sector'])].append(row)
    scored=[]
    for group in groups.values():
        for row in group:row['peer_count']=len(group)
        if len(group)<POLICY['minimum_country_sector_peers']:
            for row in group:row['rank_reason']='Fewer than 20 complete country/sector peers'
            continue
        arrays={key:sorted(row['features'][key] for row in group) for key in SCORE_FIELDS}
        for row in group:
            p=[percentile(row['features'][k],arrays[k]) for k in SCORE_FIELDS]
            row['score']=100*(.5*sum(p[:3])/3+.5*sum(p[3:])/2)
            row['features'].update(quality_score=100*sum(p[:3])/3,value_score=100*sum(p[3:])/2,component_percentiles=dict(zip(SCORE_FIELDS,p)))
        order=sorted(row['score'] for row in group)
        for row in group:
            row['group_percentile']=percentile(row['score'],order)
            row['top_candidate']=row['group_percentile']>=.8;scored.append(row)
    # Deduplicate inferred issuer keys before the frozen top 100 research queue.
    scored.sort(key=lambda r:(-r['score'],r['listing']['id']));issuers=set();position=0
    for row in scored:
        issuer=row['listing']['issuer_key']
        if issuer in issuers:
            row['top_candidate']=False;row['rank_reason']='Duplicate inferred issuer identity';continue
        issuers.add(issuer);position+=1;row['rank']=position
    shortlist=[r for r in scored if r['rank'] is not None and r['top_candidate']][:100]
    ids={r['listing']['id'] for r in shortlist}
    for row in rows:row['shortlisted']=row['listing']['id'] in ids
    return rows,shortlist
