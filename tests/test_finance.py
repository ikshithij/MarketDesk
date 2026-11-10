import unittest
from datetime import date, timedelta
from server.finance import statements, metrics, portfolio, backtest

# Synthetic fixtures are test-only and are never served by the application.
def point(value,start='2023-01-01',end='2023-12-31',filed='2024-02-01',form='10-K'):
    return {'val':value,'start':start,'end':end,'filed':filed,'form':form,'accn':'test-accession'}
def facts(tags):
    return {'facts':{'us-gaap':{tag:{'units':{'USD':points}} for tag,points in tags.items()}}}
def tx(side='buy',qty=10,price=100,fees=0,currency='USD',day='2024-01-01',id=1):
    return {'id':id,'symbol':'AAPL','side':side,'quantity':qty,'price':price,'fees':fees,'currency':currency,'date':day}
def bars(count=120):
    return [{'time':str(date(2024,1,1)+timedelta(days=i)),'open':100+i,'close':100+i,'adjusted_close':100+i} for i in range(count)]

class Statements(unittest.TestCase):
    def test_latest_restatement(self):
        result=statements(facts({'Revenues':[point(100),point(110,filed='2025-02-01')]}))
        self.assertEqual(result[0]['values']['revenue'],110)
        self.assertEqual(result[0]['sources']['revenue']['filed'],'2025-02-01')
    def test_ytd_cash_flow_is_not_quarter(self):
        data=facts({'Revenues':[point(50,'2024-04-01','2024-06-30',form='10-Q')],'NetCashProvidedByUsedInOperatingActivities':[point(90,'2024-01-01','2024-06-30',form='10-Q')]})
        row=statements(data,'quarterly')[0]
        self.assertNotIn('operating_cash_flow',row['values'])
        self.assertIsNone(row['values']['free_cash_flow'])
    def test_missing_is_not_zero(self):
        row=statements(facts({'Revenues':[point(100)]}))[0]
        self.assertIsNone(row['values']['net_margin'])
        self.assertIsNone(row['values']['free_cash_flow'])
    def test_instant_balance_aligned(self):
        data=facts({'Revenues':[point(100)],'Assets':[point(300,start='2023-12-31'),point(500,start='2024-12-31',end='2024-12-31')]})
        self.assertEqual(statements(data)[0]['values']['assets'],300)
    def test_growth_and_fcf(self):
        data=facts({'Revenues':[point(120),point(100,'2022-01-01','2022-12-31')],'NetIncomeLoss':[point(24)],'NetCashProvidedByUsedInOperatingActivities':[point(40)],'PaymentsToAcquirePropertyPlantAndEquipment':[point(10)]})
        m=metrics(statements(data))
        self.assertAlmostEqual(m['revenue_growth'],20)
        self.assertEqual(m['net_margin'],20)
        self.assertEqual(m['free_cash_flow'],30)
    def test_no_growth_across_missing_year(self):
        data=facts({'Revenues':[point(120),point(100,'2020-01-01','2020-12-31')]})
        self.assertIsNone(metrics(statements(data))['revenue_growth'])

class Portfolio(unittest.TestCase):
    def test_weighted_average_cost_and_fees(self):
        result=portfolio([tx(fees=10),tx('sell',4,150,2,day='2024-02-01',id=2)],{'AAPL':{'price':120,'currency':'USD'}})
        p=result['positions'][0]
        self.assertEqual(p['quantity'],6)
        self.assertAlmostEqual(p['cost'],606)
        self.assertAlmostEqual(p['realized'],194)
        self.assertAlmostEqual(p['unrealized'],114)
    def test_oversell_rejected(self):
        with self.assertRaises(ValueError): portfolio([tx('sell')],{})
    def test_missing_quote_prevents_partial_total(self):
        result=portfolio([tx()],{})
        self.assertTrue(result['incomplete']);self.assertIsNone(result['value'])
    def test_missing_fx_is_not_one(self):
        result=portfolio([tx()],{'AAPL':{'price':120,'currency':'USD'}},'GBP')
        self.assertIsNone(result['value'])
    def test_explicit_fx(self):
        result=portfolio([tx()],{'AAPL':{'price':120,'currency':'USD'}},'GBP',1.25)
        self.assertEqual(result['value'],960)
    def test_no_currency_mismatch(self):
        result=portfolio([tx(currency='GBP')],{'AAPL':{'price':120,'currency':'USD'}})
        self.assertIsNone(result['value'])
    def test_backdated_sale_rejected(self):
        with self.assertRaises(ValueError): portfolio([tx(day='2024-02-01'),tx('sell',day='2024-01-01',id=2)],{})

class Backtest(unittest.TestCase):
    def test_signal_executes_next_open(self):
        result=backtest(bars(),lookback=10)
        self.assertEqual(result['trades'][0]['date'],bars()[10]['time'])
        self.assertEqual(result['trades'][0]['price'],110)
    def test_future_changes_do_not_change_past(self):
        original=bars();modified=bars();modified[-1]['adjusted_close']=1
        a=backtest(original,10);b=backtest(modified,10)
        self.assertEqual(a['curve'][:-1],b['curve'][:-1])
    def test_costs_reduce_return(self):
        a=backtest(bars(),10,0,0);b=backtest(bars(),10,100,50)
        self.assertLess(b['total_return'],a['total_return'])
    def test_adjustment_required(self):
        data=bars();data[0].pop('adjusted_close')
        with self.assertRaises(ValueError):backtest(data,10)
    def test_insufficient_history_rejected(self):
        with self.assertRaises(ValueError):backtest(bars(20),10)

if __name__=='__main__': unittest.main()
