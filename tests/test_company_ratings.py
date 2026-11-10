"""Ratings are evidence-linked opinions; aggregates, gates and persistence are deterministic."""
import json
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from unittest.mock import patch
from server import company_ratings as ratings, company_analysis as ai, store


def row(symbol='QCOM',value=4):
    return {'symbol':symbol,'thesis':'Test-only company opinion','main_risk':'Concentration',
            'why_now':'Current results','valuation_basis':'A test ratio','change_my_mind':'Cash deteriorates',
            'limitations':['Exploratory only'],
            'ratings':[{'id':d['id'],'value':value,'reason':'A test-supported interpretation','source_ids':['S1']} for d in ratings.DIMENSIONS],
            'sources':[{'id':f'S{i}','title':'Test document','url':f'https://example.com/{i}',
                        'publisher':'Test publisher','published_at':None,'access':'read','primary':i==1} for i in range(1,4)]}


def context():return {'quote':{'price':100,'as_of':store.now()},'stale':False,'excluded':False}


class RatingMath(unittest.TestCase):
    def test_fixed_rubric_weights_and_anchors(self):
        self.assertEqual(sum(d['weight'] for d in ratings.DIMENSIONS),100)
        self.assertEqual([d['id'] for d in ratings.DIMENSIONS if d['weight']],['business','financials','growth','valuation','long_term'])
        self.assertEqual(ratings.RUBRIC['id'],'AI-COMPANY-001')

    def test_overall_is_weighted_in_python_and_auxiliary_scores_do_not_change_it(self):
        value=row();value['ratings'][0]['value']=5;value['ratings'][1]['value']=2
        result=ratings.assessment(value,context(),store.now())
        self.assertEqual(result['sort_score'],3.7)
        for key in ['short_term','leadership_news','risks']:next(r for r in value['ratings'] if r['id']==key)['value']=0
        self.assertEqual(ratings.assessment(value,context(),store.now())['sort_score'],3.7)

    def test_missing_required_score_never_zero_fills(self):
        value=row();value['ratings'][3]['value']=None
        self.assertIsNone(ratings.assessment(value,context(),store.now())['overall'])
        self.assertIn('A required rating is missing',ratings.assessment(value,context(),store.now())['unranked_reasons'])
        value=row();next(r for r in value['ratings'] if r['id']=='short_term')['value']=None
        self.assertEqual(ratings.assessment(value,context(),store.now())['overall'],4)

    def test_stale_prices_dates_exclusions_and_weak_sources_block_rank(self):
        old=(datetime.now(timezone.utc)-timedelta(days=8)).isoformat()
        cases=[(row(),{**context(),'stale':True},store.now()),(row(),context(),old),
               (row(),{**context(),'excluded':True},store.now()),
               (row(),{**context(),'quote':{'price':100,'as_of':old}},store.now()),
               (row(),{**context(),'quote':{'price':0,'as_of':store.now()}},store.now())]
        value=row();value['sources'][0]['primary']=False;cases.append((value,context(),store.now()))
        value=row();value['ratings'][-1]['value']=2;cases.append((value,context(),store.now()))
        for value,ctx,date in cases:
            with self.subTest(context=ctx,date=date):self.assertIsNone(ratings.assessment(value,ctx,date)['overall'])

    def test_invalid_scores_citations_and_batch_membership_rejected(self):
        for field,value in [('value',6),('value',4.2),('value',True),('source_ids',['missing']),('reason','')]:
            company=row();company['ratings'][0][field]=value
            with self.assertRaises(ai.AnalysisError):ratings.validate_batch({'companies':[company]},['QCOM'])
        with self.assertRaises(ai.AnalysisError):ratings.validate_batch({'companies':[row('MSFT')]},['QCOM'])
        company=row();company['thesis']='85% probability of gains'
        with self.assertRaises(ai.AnalysisError):ratings.validate_batch({'companies':[company]},['QCOM'])
        company=row();company['sources'][0]['url']='https://127.0.0.1/private'
        with self.assertRaises(ai.AnalysisError):ratings.validate_batch({'companies':[company]},['QCOM'])
        company=row();company['sources'][1]['url']=company['sources'][0]['url']
        with self.assertRaises(ai.AnalysisError):ratings.validate_batch({'companies':[company]},['QCOM'])
        self.assertEqual(ratings.validate_batch({'companies':[row()]},['QCOM'])['companies'][0]['symbol'],'QCOM')


class RatingPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.original=store.DATA;store.DATA=Path(self.tmp.name)
        store.init();ai.initialize();ratings.initialize()
    def tearDown(self):store.DATA=self.original;self.tmp.cleanup()
    def save(self,symbol='QCOM',value=4,date=None):
        import uuid
        with store.db() as c:c.execute('INSERT INTO company_ratings VALUES(?,?,?,?,?,?,?,?)',(uuid.uuid4().hex,symbol,'job',date or store.now(),ratings.VERSION,json.dumps(row(symbol,value)),json.dumps(context()),'{}'))

    def test_table_includes_unresearched_companies_and_preserves_older_assessments(self):
        self.save(value=2);self.save(value=4)
        data=ratings.comparison();self.assertEqual(data['total'],20);self.assertEqual(data['assessed'],1)
        q=data['rows'][0];self.assertEqual(q['symbol'],'QCOM');self.assertEqual(q['rank'],1);self.assertEqual(q['assessment']['overall'],4)
        self.assertTrue(all(r['rank'] is None for r in data['rows'][1:]))
        with store.db() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM company_ratings').fetchone()[0],2)

    def test_global_job_dedup_and_restart_does_not_erase_completed_ratings(self):
        self.save()
        with patch.object(ai,'ai_status',return_value={'available':True}),patch.object(ai.POOL,'submit') as submit:
            first=ratings.start(['qcom'],force=True);self.assertEqual(first['symbols'],['QCOM']);again=ratings.start(['MSFT'],force=True)
            self.assertEqual(first['id'],again['id']);submit.assert_called_once()
        ratings.initialize()
        self.assertEqual(ratings.get_job(first['id'])['status'],'failed')
        self.assertEqual(ratings.comparison()['assessed'],1)

    def test_recent_assessment_reused_without_new_ai_and_csv_uses_blank_missing_cells(self):
        self.save()
        with patch.object(ai,'ai_status',side_effect=AssertionError('cached ratings must not start AI')):
            self.assertEqual(ratings.start(['QCOM'])['status'],'complete')
        output=ratings.csv_export();self.assertIn('Overall /5',output);self.assertIn('Not researched',output)
        self.assertNotIn('None',output)

    def test_batch_failure_does_not_remove_prior_ratings(self):
        self.save()
        with patch.object(ai,'ai_status',return_value={'available':True}),patch.object(ai.POOL,'submit'):
            job=ratings.start(['QCOM'],force=True)
        with patch.object(ratings,'market_data',side_effect=ratings.ProviderError('Unavailable')),patch.object(ai,'run_codex',side_effect=ai.AnalysisError('No online web research recorded')):
            ratings.run_job(job['id'],['QCOM'])
        self.assertEqual(ratings.get_job(job['id'])['status'],'failed')
        self.assertEqual(ratings.comparison()['rows'][0]['assessment']['overall'],4)
