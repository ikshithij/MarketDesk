"""Research pipeline boundaries; fixtures are isolated and never served as company data."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from server import company_analysis as analysis, store


def dossier():
    return {'headline':'Test research','summary':'Unvalidated research only.',
            'business_in_one_sentence':'A test company.','research_view':'Mixed evidence',
            'bull_case':['Potential growth'],'bear_case':['Execution risk'],
            'sections':[{'id':sid,'title':sid,'summary':'Evidence summary',
                         'findings':[{'text':'Reported observation','kind':'reported','source_ids':['S1']}],
                         'gaps':[]} for sid in analysis.SECTION_IDS],
            'sources':[{'id':f'S{i}','title':'Public document','url':f'https://example.com/{i}',
                        'publisher':'Test publisher','published_at':None,'access':'read','primary':True} for i in range(1,4)],
            'limitations':['No predictive qualification.']}


class ReportValidation(unittest.TestCase):
    def test_missing_sections_or_unattributed_facts_are_rejected(self):
        report=dossier();report['sections'].pop()
        with self.assertRaises(analysis.AnalysisError):analysis.validate_report(report)
        report=dossier();report['sections'][0]['findings'][0]['source_ids']=[]
        with self.assertRaises(analysis.AnalysisError):analysis.validate_report(report)
        report=dossier();report['sections'][0]['findings'][0]['source_ids']=['unknown']
        with self.assertRaises(analysis.AnalysisError):analysis.validate_report(report)

    def test_private_and_unsafe_source_urls_are_rejected(self):
        for url in ['http://example.com','https://localhost/a','https://127.0.0.1/a',
                    'https://10.0.0.1/a','https://[::1]/','https://user:password@example.com/a']:
            with self.subTest(url=url):self.assertFalse(analysis.safe_source_url(url))
        self.assertTrue(analysis.safe_source_url('https://www.sec.gov/Archives/a'))

    def test_duplicate_sources_and_invented_confidence_are_rejected(self):
        report=dossier();report['sources'][1]['id']='S1'
        with self.assertRaises(analysis.AnalysisError):analysis.validate_report(report)
        report=dossier();report['summary']='There is an 85% probability of rising.'
        with self.assertRaises(analysis.AnalysisError):analysis.validate_report(report)
        self.assertEqual(analysis.validate_report(dossier())['research_view'],'Mixed evidence')

    def test_adjusted_history_gaps_do_not_produce_partial_returns(self):
        bars=[{'time':'2026-01-01','adjusted_close':100+i} for i in range(70)]
        self.assertAlmostEqual(analysis.observations({'bars':bars})['total_return_20_sessions_pct'],(169/149-1)*100)
        bars[10]['adjusted_close']=None
        self.assertNotIn('total_return_20_sessions_pct',analysis.observations({'bars':bars}))

    def test_cli_has_live_web_but_no_shell_or_user_plugins(self):
        command=analysis.codex_command('codex','schema','temp')
        self.assertIn('--ignore-user-config',command);self.assertIn('web_search="live"',command)
        self.assertEqual(command[command.index('--sandbox')+1],'read-only')
        self.assertIn('shell_tool',command);self.assertIn('plugins',command)

    def test_no_web_use_means_no_report_published(self):
        process=MagicMock(returncode=0,pid=999)
        process.communicate.return_value=(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':json.dumps(dossier())}}),'')
        analysis.SHUTTING_DOWN.clear()
        with patch.object(analysis,'codex_binary',return_value='codex'),patch.object(analysis.subprocess,'Popen',return_value=process) as spawn,patch.dict('os.environ',{'OPENAI_API_KEY':'secret-not-for-research'}):
            with self.assertRaisesRegex(analysis.AnalysisError,'No online web research'):analysis.run_codex('Public company only','test',lambda _:None)
            self.assertNotIn('OPENAI_API_KEY',spawn.call_args.kwargs['env'])
        self.assertNotIn('test',analysis.ACTIVE)


class PersistentResearch(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.original=store.DATA;store.DATA=Path(self.tmp.name)
        store.init();analysis.initialize()
    def tearDown(self):store.DATA=self.original;self.tmp.cleanup()

    def test_company_name_resolution_needs_no_sec_or_network(self):
        with patch.object(analysis,'fetch') as fetch:
            self.assertEqual(analysis.lookup('Qualcomm')[0]['symbol'],'QCOM')
            fetch.assert_not_called()

    def test_one_active_run_per_company_and_focus_even_on_forced_refresh(self):
        with patch.object(analysis,'ai_status',return_value={'available':True}),patch.object(analysis.POOL,'submit') as submit:
            first=analysis.start_report('QCOM','cash flow')
            again=analysis.start_report('QCOM','cash flow',True)
            self.assertEqual(first['id'],again['id']);submit.assert_called_once()
            analysis.initialize()
            self.assertEqual(analysis.get_report(first['id'])['status'],'failed')

    def test_cached_report_can_be_read_without_ai_and_refresh_preserves_it(self):
        with patch.object(analysis,'ai_status',return_value={'available':True}),patch.object(analysis.POOL,'submit'):
            first=analysis.start_report('QCOM')
            with store.db() as conn:conn.execute("UPDATE company_reports SET status='complete',result_json=? WHERE id=?",(json.dumps(dossier()),first['id']))
            with patch.object(analysis,'ai_status',side_effect=AssertionError('cache must not start AI')):
                self.assertEqual(analysis.start_report('QCOM')['id'],first['id'])
            second=analysis.start_report('QCOM',force=True)
            self.assertNotEqual(first['id'],second['id'])
            self.assertEqual(analysis.get_report(first['id'])['status'],'complete')

    def test_worker_succeeds_without_sec_or_quote_and_marks_failed_ai_cleanly(self):
        with patch.object(analysis,'ai_status',return_value={'available':True}),patch.object(analysis.POOL,'submit'):
            first=analysis.start_report('QCOM')
        with patch.object(analysis,'market_data',side_effect=analysis.ProviderError('Quote temporarily unavailable')),patch.object(analysis,'run_codex',return_value=(dossier(),{'web_searches':1})) as ai:
            analysis.run_report(first['id'],analysis.identity('QCOM'),'')
            result=analysis.get_report(first['id'])
            self.assertEqual(result['status'],'complete');self.assertIn('not a qualified',result['report']['predictive_status'])
            self.assertTrue(result['context']['gaps']);self.assertIn('UNVALIDATED',ai.call_args.args[0])
            self.assertIn('probability_publication_gate',ai.call_args.args[0])
            self.assertEqual(len(result['engine']['request']['standard_sha256']),64)
        with patch.object(analysis,'ai_status',return_value={'available':True}),patch.object(analysis.POOL,'submit'):
            second=analysis.start_report('QCOM',force=True)
        with patch.object(analysis,'market_data',side_effect=analysis.ProviderError('No quote')),patch.object(analysis,'run_codex',side_effect=analysis.AnalysisError('Usage limit')):
            analysis.run_report(second['id'],analysis.identity('QCOM'),'')
        self.assertEqual(analysis.get_report(second['id'])['status'],'failed')
        self.assertIsNone(analysis.get_report(second['id'])['report'])
        self.assertEqual(analysis.get_report(first['id'])['status'],'complete')

if __name__=='__main__':unittest.main()
