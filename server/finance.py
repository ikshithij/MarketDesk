"""Pure deterministic calculations. Missing inputs remain missing."""
import math
from datetime import date
from statistics import mean, stdev

def ratio(a,b):
    return a/b if a is not None and b not in (None,0) else None

def pct(a,b):
    return (a/b-1)*100 if a is not None and b not in (None,0) else None

TAGS = {
 'revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'],
 'net_income':['NetIncomeLoss','ProfitLoss'], 'operating_income':['OperatingIncomeLoss'],
 'operating_cash_flow':['NetCashProvidedByUsedInOperatingActivities'],
 'capex':['PaymentsToAcquirePropertyPlantAndEquipment'],
 'assets':['Assets'],'liabilities':['Liabilities'],'equity':['StockholdersEquity'],
 'cash':['CashAndCashEquivalentsAtCarryingValue'],
 'debt':['LongTermDebtCurrent','LongTermDebtNoncurrent'],
}
INSTANT = {'assets','liabilities','equity','cash','debt'}

def statements(facts, frequency='annual'):
    """Keep exact fiscal durations, latest restatement for each period/tag.
    Quarterly cash flows are often YTD; never mislabel them as standalone quarters.
    """
    gaap = facts.get('facts',{}).get('us-gaap',{})
    periods = {}
    for metric, tags in TAGS.items():
        for tag in tags:
            points = gaap.get(tag,{}).get('units',{}).get('USD',[])
            for p in points:
                if p.get('form') not in ('10-K','10-Q','20-F') or 'end' not in p:
                    continue
                duration = (date.fromisoformat(p['end'])-date.fromisoformat(p.get('start',p['end']))).days
                if metric not in INSTANT and not ((300 <= duration <= 380) if frequency=='annual' else (65 <= duration <= 110)):
                    continue
                if metric in INSTANT:
                    continue  # align instantaneous facts to a verified duration period below
                key = (p.get('start'),p['end'])
                row = periods.setdefault(key,{'start':key[0],'end':key[1],'values':{},'sources':{}})
                old = row['sources'].get(metric)
                # Prefer primary tag even where alternate tags also exist.
                if old is None or (old['tag']==tag and p.get('filed','') > old['filed']):
                    row['values'][metric] = p['val']
                    row['sources'][metric] = {'tag':tag,'filed':p.get('filed',''),'accession':p.get('accn',''),'form':p.get('form')}
    for row in periods.values():
        for metric in INSTANT - {'debt'}:
            for tag in TAGS[metric]:
                points = [p for p in gaap.get(tag,{}).get('units',{}).get('USD',[]) if p.get('end')==row['end'] and p.get('form') in ('10-K','10-Q','20-F')]
                if points:
                    p = max(points,key=lambda p:p.get('filed',''))
                    row['values'][metric] = p['val']
                    row['sources'][metric] = {'tag':tag,'filed':p.get('filed',''),'accession':p.get('accn',''),'form':p.get('form')}
                    break
        # Debt is the sum of current and noncurrent long-term debt only if both exist.
        debt=[]
        for tag in TAGS['debt']:
            points=[p for p in gaap.get(tag,{}).get('units',{}).get('USD',[]) if p.get('end')==row['end'] and p.get('form') in ('10-K','10-Q','20-F')]
            if points: debt.append(max(points,key=lambda p:p.get('filed',''))['val'])
        if len(debt)==2: row['values']['debt']=sum(debt)
        v=row['values']
        v['free_cash_flow']=v['operating_cash_flow']-v['capex'] if all(k in v for k in ('operating_cash_flow','capex')) else None
        v['net_margin']=100*ratio(v.get('net_income'),v.get('revenue')) if ratio(v.get('net_income'),v.get('revenue')) is not None else None
    return sorted([r for r in periods.values() if r['values'].get('revenue') is not None],key=lambda r:r['end'],reverse=True)[:12]

def metrics(annual):
    if not annual: return {}
    latest=annual[0]; v=latest['values']
    # Only compare consecutive annual fiscal ends, never gaps or duplicate periods.
    previous=next((r for r in annual[1:] if 300 <= (date.fromisoformat(latest['end'])-date.fromisoformat(r['end'])).days <= 430),None)
    return {**v,'period':latest['end'],'revenue_growth':pct(v.get('revenue'),previous['values'].get('revenue')) if previous else None}

def portfolio(transactions, quotes, base='USD', gbp_usd=None):
    positions={}; realized=0
    for t in sorted(transactions,key=lambda t:(t['date'],t.get('id',0))):
        key=(t['symbol'],t['currency'])
        p=positions.setdefault(key,{'symbol':t['symbol'],'currency':t['currency'],'quantity':0.,'cost':0.,'realized':0.})
        qty=t['quantity']; fee=t.get('fees',0)
        if t['side']=='buy':
            p['quantity']+=qty; p['cost']+=qty*t['price']+fee
        else:
            if qty>p['quantity']+1e-9: raise ValueError('Sale exceeds available shares on transaction date')
            basis=p['cost']/p['quantity']*qty
            p['quantity']-=qty; p['cost']-=basis
            p['realized']+=qty*t['price']-fee-basis
    result=[]; incomplete=False; total=0.; total_cost=0.; total_realized=0.
    for p in positions.values():
        factor=1 if p['currency']==base else (gbp_usd if p['currency']=='GBP' else ratio(1,gbp_usd))
        # Quote currency must match transaction currency; no implicit conversion.
        q=quotes.get(p['symbol'],{})
        price=q.get('price') if q.get('currency')==p['currency'] else None
        value=p['quantity']*price if price is not None else (0 if p['quantity']==0 else None)
        p.update(price=price,as_of=q.get('as_of'),value=value,unrealized=value-p['cost'] if value is not None else None)
        p['base_value']=value*factor if value is not None and factor is not None else None
        p['base_cost']=p['cost']*factor if factor is not None else None
        if p['base_value'] is None or factor is None: incomplete=True
        else: total+=p['base_value'];total_cost+=p['base_cost'];total_realized+=p['realized']*factor
        result.append(p)
    return {'positions':result,'value':None if incomplete else total,'cost':None if incomplete else total_cost,'unrealized':None if incomplete else total-total_cost,'realized':None if incomplete else total_realized,'incomplete':incomplete,'base':base,'method':'Weighted average cost; FX uses supplied spot rate, not historical FX. Not a tax calculation.'}

def backtest(bars, lookback=50, cost_bps=10, slippage_bps=5):
    """Long/cash SMA, yesterday's signal executed at next adjusted open."""
    if len(bars)<lookback+30: raise ValueError('Need at least lookback + 30 adjusted daily bars')
    if any(not b.get('adjusted_close') or not b.get('open') or not b.get('close') for b in bars): raise ValueError('Adjusted prices are required')
    cash=10000.; shares=0.; curve=[]; trades=[]; closes=[]; peak=10000.; mdd=0.; entry=None
    cost=(cost_bps+slippage_bps)/10000
    for i,b in enumerate(bars):
        adjusted=b['adjusted_close']; adj_open=b['open']*adjusted/b['close']
        if i>=lookback:
            signal=closes[-1]>mean(closes[-lookback:])
            if signal and shares==0:
                shares=cash/(adj_open*(1+cost));entry=cash;cash=0
                trades.append({'date':b['time'],'side':'buy','price':adj_open,'shares':shares})
            elif not signal and shares>0:
                cash=shares*adj_open*(1-cost)
                trades.append({'date':b['time'],'side':'sell','price':adj_open,'shares':shares,'pnl':cash-entry})
                shares=0
            value=cash+shares*adjusted; peak=max(peak,value);mdd=min(mdd,value/peak-1)
            curve.append({'time':b['time'],'value':value,'benchmark':10000*adjusted/bars[lookback]['adjusted_close']})
        closes.append(adjusted)
    returns=[curve[i]['value']/curve[i-1]['value']-1 for i in range(1,len(curve))]
    years=(date.fromisoformat(curve[-1]['time'])-date.fromisoformat(curve[0]['time'])).days/365.25
    closed=[t['pnl'] for t in trades if 'pnl' in t]; wins=[p for p in closed if p>0]; losses=[p for p in closed if p<0]
    return {'curve':curve,'trades':trades,'total_return':(curve[-1]['value']/10000-1)*100,'cagr':((curve[-1]['value']/10000)**(1/years)-1)*100 if years else None,'max_drawdown':mdd*100,'sharpe':mean(returns)/stdev(returns)*math.sqrt(252) if len(returns)>1 and stdev(returns)>0 else None,'win_rate':100*len(wins)/len(closed) if closed else None,'profit_factor':sum(wins)/abs(sum(losses)) if losses else None,'benchmark_return':(curve[-1]['benchmark']/10000-1)*100,'assumptions':['Single current security; survivorship bias is not corrected.','Split/dividend-adjusted prices model total-return exposure approximately; no dividend cash ledger.','Previous close signal; next adjusted open execution.','Long/cash, full allocation, no leverage; cash earns zero.','No parameter optimisation. This is an in-sample educational test, not out-of-sample evidence.','Costs and slippage charged on every buy and sell.']}
