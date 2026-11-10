"""Temporary research fixtures: never served as public market observations."""
import copy
import io
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
from fastapi.testclient import TestClient
from server import store,market_sources as sources,market_screen as screen,market_universe as universe,company_analysis as ai,company_ratings as ratings,main

TODAY=date(2026,11,10)
def listing(symbol='TEST',country='US',issuer=None):
 return {'id':country+':X:'+symbol,'symbol':symbol,'name':'Test Operating Company '+symbol,'country':country,'sector':'Technology','industry':'Software','venue':'Nasdaq' if country=='US' else 'MAIN MARKET','isin':'','issuer_key':issuer or symbol,'classification':'candidate','exclusion':None,'currency':'USD','cik':''}
def facts():
 return {'period':'2026-06-30','annual':{'gross_profit':500e6,'operating_cash_flow':150e6,'net_income':120e6,'operating_income':180e6,'capital_expenditure':-20e6,'total_assets':1e9,'total_revenue':1.2e9,'total_debt':400e6,'cash_cash_equivalents_and_short_term_investments':200e6},'previous_period':'2025-06-30','previous_assets':800e6,'financial_currency':'USD','quote_currency':'USD','price_date':'2026-11-09','price':20.,'shares_date':'2026-11-01','shares':200e6,'median_daily_value':12e6,'liquidity_sessions':60}
FX={'date':'2026-11-10','per_eur':{'EUR':1.,'GBP':.8,'USD':1.2}}
def ranked_rows(n=21):
 return [{'listing':listing(f'T{i:02}'),'status':'ready','features':{k:float(i) for k in screen.SCORE_FIELDS},'reasons':[]} for i in range(n)]

class Screening(unittest.TestCase):
 def test_currency_and_pence_conversion_are_explicit(self):
  us,reasons,_=screen.features(listing(),facts(),FX,TODAY);self.assertFalse(reasons)
  self.assertAlmostEqual(us['market_cap_gbp'],4e9*.8/1.2)
  self.assertAlmostEqual(us['free_cash_flow'],130e6)
  self.assertAlmostEqual(us['gross_profit_to_assets'],500/900)
  uk=facts();uk.update(quote_currency='GBp',price=2000.,median_daily_value=1.2e9)
  result,reasons,_=screen.features(listing(country='UK'),uk,FX,TODAY);self.assertFalse(reasons)
  self.assertEqual(result['market_cap_gbp'],4e9);self.assertEqual(result['median_daily_value_gbp'],12e6)
  self.assertAlmostEqual(result['market_cap_reporting_currency'],6e9,delta=.01)
 def test_missing_zero_positive_capex_and_stale_inputs(self):
  for field,value in [('total_debt',None),('net_income',0),('capital_expenditure',20e6)]:
   data=facts();data['annual'][field]=value;_,reasons,_=screen.features(listing(),data,FX,TODAY);self.assertTrue(reasons)
  data=facts();data['annual']['total_debt']=0
  result,reasons,_=screen.features(listing(),data,FX,TODAY);self.assertFalse(reasons);self.assertIsNotNone(result['enterprise_value_proxy'])
  for key,value in [('price_date','2026-10-01'),('shares_date','2025-01-01'),('period','bad-date'),('price',float('nan')),('liquidity_sessions',59)]:
   data=facts();data[key]=value;_,reasons,_=screen.features(listing(),data,FX,TODAY);self.assertTrue(reasons)
 def test_small_groups_abstain_and_country_groups_do_not_mix(self):
  rows=ranked_rows(19);rows,short=screen.rank_rows(rows);self.assertFalse(short);self.assertTrue(all(r['score'] is None for r in rows))
  rows=ranked_rows(21)+[{**r,'listing':{**r['listing'],'id':'UK:'+r['listing']['id'],'country':'UK','issuer_key':'UK:'+r['listing']['issuer_key']}} for r in ranked_rows(10)]
  rows,short=screen.rank_rows(rows);self.assertEqual(len(short),5)
  self.assertTrue(all(r['score'] is None for r in rows if r['listing']['country']=='UK'))
 def test_ties_and_duplicate_issuers_cannot_inflate_peer_counts(self):
  self.assertEqual(screen.percentile(1,[1,1,2,3]),1/6)
  rows=ranked_rows(20);rows[-1]['listing']['issuer_key']=rows[0]['listing']['issuer_key']
  result,short=screen.rank_rows(rows);self.assertFalse(short);self.assertTrue(all(r['score'] is None for r in result))
 def test_top100_limit_and_score_is_reproducible(self):
  rows,short=screen.rank_rows(ranked_rows(600));self.assertEqual(len(short),100);self.assertAlmostEqual(short[0]['score'],100)
  self.assertAlmostEqual(short[0]['features']['quality_score'],100)
  self.assertEqual(short[0]['listing']['symbol'],'T599')

class Directories(unittest.TestCase):
 def test_us_flags_and_symbol_mapping(self):
  text='Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\nABC|Example Common Stock|Q|N|N|100|N|N\nFUND|Example ETF|Q|N|N|100|Y|N\nTEST|Test Common Stock|Q|Y|N|100|N|N\nFile Creation Time: today|||||||\n'
  rows=sources.nasdaq_rows(text);self.assertEqual(len(rows),3);self.assertEqual(rows[0]['classification'],'candidate');self.assertEqual(rows[1]['classification'],'excluded');self.assertEqual(rows[2]['classification'],'excluded')
 def test_lse_input_adapter_retains_excluded_funds(self):
  headers={'A':'TIDM','B':'Issuer Name','C':'Instrument Name','D':'ISIN','E':'MiFIR Identifier Code','G':'ICB Industry','H':'ICB Super-Sector Name','K':'Trading Currency','L':'LSE Market'}
  cells=[headers,{'A':'ABC','B':'Example PLC','C':'ORD GBP1','D':'GB0000000001','E':'SHRS','G':'Technology','H':'Technology','K':'GBX','L':'AIM'},{'A':'ETF','B':'Example UCITS','C':'Fund','D':'GB0000000002','E':'ETFS','G':'Financials'}]
  with patch.object(sources,'xlsx_rows',return_value=iter(cells)):
   rows=sources.lse_rows('unused');self.assertEqual(rows[0]['symbol'],'ABC.L');self.assertEqual(rows[1]['classification'],'excluded')
 def test_aquis_no_guessed_prices(self):
  text='ticker,description,issuer,isin,mic,instrument_type,test_stock,is_tradeable,currency\nABC,Example PLC,Example PLC,GB0000000001,AQSE,ORD,0,1,GBX\n'
  rows=sources.aquis_rows(text);self.assertEqual(rows[0]['venue'],'Aquis');self.assertEqual(rows[0]['classification'],'candidate')

class MarketDatabase(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.original=store.DATA;store.DATA=Path(self.tmp.name);store.init();ai.initialize();ratings.initialize();universe.initialize()
 def tearDown(self):universe.STOP.set();sources.STOP.set();store.DATA=self.original;self.tmp.cleanup()

class Persistence(MarketDatabase):
 def test_restart_resumes_scan_and_keeps_legacy_data(self):
  with store.db() as c:c.execute("INSERT INTO notes(symbol,title,body,updated_at) VALUES('QCOM','Keep me','Original thesis',?)",(store.now(),))
  run=universe.create();universe.save_initial(run['id'],[listing()],{'url':'https://example.com/source'})
  with store.db() as c:c.execute("UPDATE market_runs SET status='running' WHERE id=?",(run['id'],))
  universe.initialize();self.assertEqual(universe.state(run['id'])['status'],'queued')
  self.assertEqual(universe.rows(run['id'])['total'],1)
  with store.db() as c:self.assertEqual(c.execute('SELECT title FROM notes').fetchone()[0],'Keep me')
 def test_pause_resume_and_idempotent_start(self):
  first=universe.create();again=universe.create();self.assertEqual(first['id'],again['id'])
  universe.control(first['id'],'pause');self.assertEqual(universe.state(first['id'])['status'],'paused')
  universe.control(first['id'],'resume');self.assertEqual(universe.state(first['id'])['status'],'queued')
 def test_freeze_has_immutable_manifest_and_bounded_research_queue(self):
  run=universe.create();fixtures=ranked_rows(120)
  universe.save_initial(run['id'],[r['listing'] for r in fixtures],{'url':'https://example.com/source'})
  for r in fixtures:universe.save_result(run['id'],r['listing'],r['features'],[],[],[])
  universe.refresh_ranks(run['id'],True)
  before=universe.state(run['id'])['cohort_hash'];self.assertEqual(len(before),64)
  with store.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM market_ai_queue').fetchone()[0],24)
  universe.refresh_ranks(run['id'],True)
  self.assertEqual(universe.state(run['id'])['cohort_hash'],before)
  with store.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM market_ai_queue').fetchone()[0],24)
 def test_filters_are_literal_and_csv_preserves_missing_values(self):
  run=universe.create();r=listing('A%');universe.save_initial(run['id'],[r,listing('B')],{'url':'https://example.com/source'})
  self.assertEqual(universe.rows(run['id'],q='%')['total'],1)
  self.assertEqual(universe.rows(run['id'],country='UK')['total'],0)
  self.assertIn('Discovery score /100',universe.export_csv(run['id']))
  with self.assertRaises(ai.AnalysisError):universe.rows(run['id'],view='fake')
 def test_unsupported_ai_input_check_is_flagged_without_mutating_screen(self):
  run=universe.create();r=listing();universe.save_initial(run['id'],[r],{'url':'https://example.com/source'})
  universe.queue_update(run['id'],r['id'],status='pending')
  item={'run_id':run['id'],'listing_id':r['id'],'status':'dossier','report_id':'existing','attempts':1}
  with store.db() as c:c.execute('INSERT INTO market_ai_queue VALUES(?,?,?,?,?,?,?,?,?)',(run['id'],r['id'],1,'dossier','existing',None,1,None,store.now()))
  with patch.object(ai,'get_report',return_value={'status':'complete','report':{'screening_review':{'status':'contradicted','summary':'Primary cash flow differs.'}}}),patch.object(ratings,'start') as start:
   universe.research_step(item);start.assert_not_called()
  with store.db() as c:self.assertEqual(c.execute('SELECT status FROM market_ai_queue').fetchone()[0],'needs_review')
 def test_api_version_pagination_and_input_validation(self):
  client=TestClient(main.app)
  self.assertEqual(client.get('/api/version').json()['version'],'0.2.0')
  run=universe.create(False)
  self.assertEqual(client.get('/api/market-runs/'+run['id']+'/rows?limit=201').status_code,422)
  self.assertEqual(client.get('/api/market-runs/'+run['id']+'/rows?offset=-1').status_code,422)
  self.assertEqual(client.get('/api/market-runs/'+run['id']+'/rows').status_code,200)
  self.assertEqual(client.get('/api/market-universe').json()['run']['id'],run['id'])

class SourceSnapshots(MarketDatabase):
 def test_content_addressed_cache_and_checksum_failure(self):
  import hashlib,httpx
  original=httpx.Client;calls=[]
  def handler(request):calls.append(str(request.url));return httpx.Response(200,content=b'public-test-data')
  def client(**kwargs):return original(transport=httpx.MockTransport(handler),**kwargs)
  expected=hashlib.sha256(b'public-test-data').hexdigest()
  with patch.object(sources.httpx,'Client',side_effect=client),patch.object(sources,'LAST',0):
   first,path=sources.acquire('https://example.com/data','Test',expected_hash=expected)
   second,again=sources.acquire('https://example.com/data','Test',expected_hash=expected)
   self.assertEqual(first['id'],second['id']);self.assertEqual(path,again);self.assertEqual(len(calls),1)
   with self.assertRaises(sources.SourceError):sources.acquire('https://example.com/bad','Test',expected_hash='0'*64)
  self.assertTrue(path.exists());self.assertFalse(list((store.DATA/'market-snapshots').glob('*.part')))
 def test_pipeline_freezes_only_after_all_listing_sources_and_scan_finish(self):
  run=universe.create();companies=[listing(f'S{i:02}') for i in range(21)]
  def discover(rid):universe.save_initial(rid,companies,{'url':'https://example.com/directory'});universe.progress(rid,'Discovered',discovered=True);return True
  catalog={r['symbol']:{'cik_str':i+1,'title':r['name'],'financial_currency':'USD'} for i,r in enumerate(companies)}
  profiles={r['symbol']:{'sector':'Technology','industry':'Software'} for r in companies}
  observations={}
  for i,r in enumerate(companies):
   value=facts();value['annual']['gross_profit']+=(i*10e6);value['annual']['operating_cash_flow']+=(i*5e6);observations[r['symbol']]=value
  with patch.object(universe,'discover',side_effect=discover),patch.object(sources,'fx_rates',return_value=FX),patch.object(universe.data,'bulk_files',return_value=({},[])),patch.object(universe.data,'read_bulk',return_value=(catalog,profiles,observations)):
   universe.scan(run['id'])
  final=universe.state(run['id']);self.assertEqual(final['status'],'complete');self.assertTrue(final['cohort_hash'])
  self.assertEqual(universe.rows(run['id'],view='top100')['total'],5)
  self.assertEqual(universe.overview()['queue']['pending'],5)
 def test_ai_reconciliation_needs_distinct_primary_numeric_checks(self):
  report={'sources':[{'id':'S1','primary':True,'access':'read'}],'screening_review':{'status':'supported','summary':'Source matches','checks':[{'metric':'revenue','reported_value':1,'unit':'USD','period':'2026','source_ids':['S1'],'note':''} for _ in range(3)]}}
  with patch.object(ai,'validate_report',return_value=report):self.assertEqual(ai.validate_screened_report(report)['screening_review']['status'],'insufficient_evidence')
