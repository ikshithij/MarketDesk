import json, tempfile, unittest, time
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from server import store, main

class API(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.original=store.DATA;store.DATA=Path(cls.tmp.name)
        cls.client=TestClient(main.app);cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None,None,None);store.DATA=cls.original;cls.tmp.cleanup()
    def test_company_identity_without_fabricated_financials(self):
        r=self.client.get('/api/company/AAPL');self.assertEqual(r.status_code,200)
        self.assertIsNone(r.json()['financials']);self.assertIsNone(r.json()['market'])
    def test_search_and_compare(self):
        r=self.client.post('/api/search',json={'query':'Compare Nvidia and AMD'}).json()
        self.assertEqual(r['intent'],'compare');self.assertEqual(set(r['symbols']),{'NVDA','AMD'})
    def test_screen_intent_shows_structured_query(self):
        r=self.client.post('/api/search',json={'query':'Find profitable semiconductor stocks with revenue growth above 20%'}).json()
        self.assertEqual(r['filters']['growth_min'],20);self.assertEqual(r['filters']['margin_min'],0)
    def test_unfiltered_discovery_keeps_company_identities(self):
        r=self.client.post('/api/screen',json={}).json()
        self.assertEqual(len(r['matches']),20);self.assertEqual(r['missing'],0)
    def test_missing_fcf_is_counted(self):
        r=self.client.post('/api/screen',json={'fcf_positive':True}).json()
        self.assertEqual(r['matches'],[]);self.assertEqual(r['missing'],20)
    def test_directory_does_not_accept_invented_identity(self):
        r=self.client.post('/api/directory/add',json={'ticker':'MADEUP'})
        self.assertEqual(r.status_code,404)
    def test_note_and_portfolio_writes_are_durable(self):
        r=self.client.post('/api/transactions',json={'symbol':'AAPL','side':'buy','quantity':3,'price':100,'fees':2,'date':'2024-01-01'})
        self.assertEqual(r.status_code,200)
        p=self.client.get('/api/portfolio').json()
        self.assertEqual(p['positions'][0]['cost'],302)
        self.assertIsNone(p['value'])
        self.client.delete('/api/transactions/'+str(p['transactions'][0]['id']))
    def test_price_access_does_not_require_sec(self):
        with patch('server.main.market_data',return_value={'quote':{'price':123,'provider':'Yahoo Finance'}}) as market, patch('server.main.sec_company') as sec:
            response=self.client.get('/api/market/QCOM')
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json()['quote']['price'],123)
            market.assert_called_once_with('QCOM');sec.assert_not_called()
    def test_missing_data_excluded(self):
        r=self.client.post('/api/screen',json={'growth_min':20}).json()
        self.assertEqual(r['matches'],[]);self.assertEqual(r['missing'],20)
    def test_note_fts_and_delete(self):
        r=self.client.post('/api/notes',json={'symbol':'AAPL','title':'Test thesis','body':'Revenue concentration research'});self.assertEqual(r.status_code,200)
        nid=r.json()['id'];self.assertEqual(len(self.client.get('/api/notes?q=concentration').json()),1)
        self.assertEqual(self.client.get('/api/notes?q=%22OR%22').status_code,200)
        self.client.delete('/api/notes/'+str(nid));self.assertEqual(self.client.get('/api/notes?q=concentration').json(),[])
    def test_watchlist_roundtrip(self):
        self.client.put('/api/watchlist/NVDA');self.assertIn('NVDA',self.client.get('/api/watchlist').json())
        self.client.delete('/api/watchlist/NVDA');self.assertNotIn('NVDA',self.client.get('/api/watchlist').json())
    def test_reject_short_sale_and_nan(self):
        payload={'symbol':'AAPL','side':'sell','quantity':2,'price':10,'date':'2024-01-01'}
        self.assertEqual(self.client.post('/api/transactions',json=payload).status_code,422)
        payload.update(side='buy',price='NaN');self.assertEqual(self.client.post('/api/transactions',json=payload).status_code,422)
    def test_invalid_origin_and_host(self):
        self.assertEqual(self.client.get('/api/export',headers={'origin':'https://evil.example'}).status_code,403)
        self.assertEqual(self.client.get('/api/export',headers={'host':'evil.example'}).status_code,403)
    def test_keys_never_returned(self):
        with patch.dict('os.environ',{'OPENAI_API_KEY':'private-test-secret'}):
            r=self.client.get('/api/settings');self.assertNotIn('private-test-secret',r.text);self.assertTrue(r.json()['providers']['ai'])
    def test_fx_requires_date(self):
        self.assertEqual(self.client.put('/api/settings',json={'gbp_usd':1.25}).status_code,422)
    def test_job_handles_provider_failure(self):
        with patch('server.main.sec_company',side_effect=main.ProviderError('Rate limited')):
            r=self.client.post('/api/refresh',json={'symbols':['AAPL']});self.assertEqual(r.status_code,200)
            jid=r.json()['id']
            for _ in range(30):
                j=self.client.get('/api/jobs/'+jid).json()
                if j['status']!='running':break
                time.sleep(.01)
            self.assertEqual(j['status'],'failed');self.assertIn('Rate limited',j['detail']['errors'][0])
    def test_ai_requires_real_evidence(self):
        r=self.client.post('/api/research',json={'symbol':'AAPL','question':'How is revenue growing?'})
        self.assertEqual(r.status_code,422)

if __name__=='__main__':unittest.main()
