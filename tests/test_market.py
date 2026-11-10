import copy, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from server import store, providers

def payload():
    return {'chart':{'result':[{'meta':{'symbol':'QCOM','currency':'USD','regularMarketPrice':110,'regularMarketTime':1735909200,'exchangeTimezoneName':'America/New_York','chartPreviousClose':40},'timestamp':[1735650000,1735736400,1735822800], 'indicators':{'quote':[{'open':[99,101,None],'high':[101,106,None],'low':[98,100,None],'close':[100,105,None],'volume':[20,30,None]}],'adjclose':[{'adjclose':[99,104,None]}]}}]}}

class Market(unittest.TestCase):
    def test_london_pence_remain_distinct_from_pounds(self):
        raw=payload();raw['chart']['result'][0]['meta']['currency']='GBp'
        data=providers.normalize_yahoo(raw,'QCOM')
        self.assertEqual(data['quote']['currency'],'GBX')
        self.assertEqual(data['quote']['price'],110)
    def test_uses_prior_session_not_year_start_for_day_change(self):
        p=providers.normalize_yahoo(payload(),'QCOM')
        self.assertAlmostEqual(p['quote']['change_pct'],(110/105-1)*100)
        self.assertNotEqual(p['quote']['previous_close'],40)
    def test_skips_null_bars_and_keeps_provenance(self):
        p=providers.normalize_yahoo(payload(),'QCOM')
        self.assertEqual(len(p['bars']),2)
        self.assertEqual(p['bars'][0]['adjusted_close'],99)
        self.assertEqual(p['quote']['provider'],'Yahoo Finance')
        self.assertIn('T',p['quote']['as_of'])
        self.assertEqual(p['quote']['delay'],'Delay not specified by provider')
    def test_never_invents_adjusted_prices(self):
        raw=payload();raw['chart']['result'][0]['indicators'].pop('adjclose')
        self.assertIsNone(providers.normalize_yahoo(raw,'QCOM')['bars'][0]['adjusted_close'])
    def test_rejects_symbol_mismatch_and_nonfinite_price(self):
        with self.assertRaises(providers.ProviderError):providers.normalize_yahoo(payload(),'AAPL')
        raw=payload();raw['chart']['result'][0]['meta']['regularMarketPrice']=float('nan')
        with self.assertRaises(providers.ProviderError):providers.normalize_yahoo(raw,'QCOM')
    def test_provider_change_has_priority(self):
        raw=payload();raw['chart']['result'][0]['meta']['regularMarketChangePercent']=2.5
        self.assertEqual(providers.normalize_yahoo(raw,'QCOM')['quote']['change_pct'],2.5)
    def test_cache_and_failure_preserve_original_quote_time(self):
        with tempfile.TemporaryDirectory() as temp:
            original=store.DATA;store.DATA=Path(temp)
            try:
                store.init()
                with patch('server.providers.fetch',return_value=payload()) as fetch:
                    p=providers.market_data('QCOM');self.assertEqual(fetch.call_count,2)
                    cached=providers.market_data('QCOM');self.assertEqual(fetch.call_count,2)
                    self.assertEqual(cached['quote']['as_of'],p['quote']['as_of'])
                with patch('server.providers.fetch',side_effect=providers.ProviderError('Rate limited')):
                    stale=providers.market_data('QCOM',True)
                    self.assertTrue(stale['stale']);self.assertEqual(stale['quote']['as_of'],p['quote']['as_of'])
            finally:store.DATA=original
