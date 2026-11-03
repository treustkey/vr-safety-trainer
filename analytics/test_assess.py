import copy
import json
from pathlib import Path
import unittest
from assess import evaluate_session, summarize_reports

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = json.loads((ROOT/'data/scenario.json').read_text())
GOOD = json.loads((ROOT/'data/session_good.json').read_text())


class AssessmentTests(unittest.TestCase):
    def test_correct(self):
        r = evaluate_session(SCENARIO, GOOD)
        self.assertEqual((r['score'], r['passed']), (100, True))

    def test_missing_critical(self):
        s = copy.deepcopy(GOOD); s['events'].pop()
        r = evaluate_session(SCENARIO, s)
        self.assertFalse(r['passed']); self.assertIn('leave_zone', r['critical_failed'])

    def test_late_critical(self):
        s = copy.deepcopy(GOOD); s['events'][-1]['t_s'] = 41
        r = evaluate_session(SCENARIO, s)
        self.assertEqual(r['score'], 60); self.assertFalse(r['passed'])

    def test_out_of_order_critical_is_not_erased(self):
        s = copy.deepcopy(GOOD)
        s['events'].insert(0, dict(event_id='early', action='leave_zone', t_s=1))
        r = evaluate_session(SCENARIO, s)
        self.assertEqual(r['score'], 100); self.assertFalse(r['passed'])

    def test_duplicate_has_no_credit(self):
        s = copy.deepcopy(GOOD); s['events'].append(dict(event_id='again', action='leave_zone', t_s=30))
        r = evaluate_session(SCENARIO, s)
        self.assertEqual(r['score'], 100); self.assertEqual(r['events'][-1]['status'], 'duplicate')

    def test_unknown_has_no_credit(self):
        s = copy.deepcopy(GOOD); s['events'].insert(0, dict(event_id='x', action='look', t_s=0))
        r = evaluate_session(SCENARIO, s)
        self.assertEqual(r['score'], 100); self.assertEqual(r['events'][0]['status'], 'unknown')

    def test_empty_session(self):
        s = copy.deepcopy(GOOD); s['events'] = []
        r = evaluate_session(SCENARIO, s)
        self.assertEqual(r['score'], 0); self.assertFalse(r['passed'])

    def test_bad_time(self):
        for value in (-1, float('nan'), float('inf'), True):
            s = copy.deepcopy(GOOD); s['events'][0]['t_s'] = value
            with self.assertRaises(ValueError): evaluate_session(SCENARIO, s)

    def test_unsorted(self):
        s = copy.deepcopy(GOOD); s['events'].reverse()
        with self.assertRaises(ValueError): evaluate_session(SCENARIO, s)

    def test_duplicate_id(self):
        s = copy.deepcopy(GOOD); s['events'][1]['event_id'] = s['events'][0]['event_id']
        with self.assertRaises(ValueError): evaluate_session(SCENARIO, s)

    def test_wrong_scenario(self):
        s = copy.deepcopy(GOOD); s['scenario_id'] = 'other'
        with self.assertRaises(ValueError): evaluate_session(SCENARIO, s)

    def test_exact_deadline(self):
        s = copy.deepcopy(GOOD)
        for event, step in zip(s['events'], SCENARIO['steps']): event['t_s'] = step['deadline_s']
        self.assertTrue(evaluate_session(SCENARIO, s)['passed'])

    def test_empty_summary(self):
        self.assertEqual(summarize_reports([]), dict(sessions=0, passed=0, mean_score=None))

    def test_summary(self):
        self.assertEqual(summarize_reports([dict(score=100, passed=True), dict(score=60, passed=False)]),
                         dict(sessions=2, passed=1, mean_score=80))


if __name__ == '__main__': unittest.main(verbosity=2)
