import copy
import json
from pathlib import Path
import unittest
from assess import evaluate_session, summarize_reports

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = json.loads((ROOT/'data/scenario.json').read_text(encoding="utf-8"))
GOOD = json.loads((ROOT/'data/session_good.json').read_text(encoding="utf-8"))


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

    def test_invalid_container_types(self):
        examples = (
            ([], GOOD, 'objects'),
            (SCENARIO, None, 'objects'),
            (dict(SCENARIO, steps={}), GOOD, 'steps'),
            (dict(SCENARIO, steps=[None]), GOOD, 'step'),
            (SCENARIO, dict(GOOD, events={}), 'events'),
            (SCENARIO, dict(GOOD, events=[None]), 'event'),
        )
        for scenario, session, message in examples:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    evaluate_session(scenario, session)

    def test_invalid_required_field_types(self):
        for field, value in (('session_id', None), ('learner_id', 5), ('scenario_id', [])):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    evaluate_session(SCENARIO, dict(GOOD, **{field: value}))
        for field, value in (('event_id', 5), ('action', []), ('t_s', '3')):
            event = dict(GOOD['events'][0], **{field: value})
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    evaluate_session(SCENARIO, dict(GOOD, events=[event]))
        for field, value in (('action', []), ('critical', 0), ('weight', True), ('deadline_s', '5')):
            step = dict(SCENARIO['steps'][0], **{field: value})
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    evaluate_session(dict(SCENARIO, steps=[step]), GOOD)
        with self.assertRaisesRegex(ValueError, 'threshold'):
            evaluate_session(dict(SCENARIO, pass_score='80'), GOOD)
        journal = {key: value for key, value in GOOD.items() if key != 'events'}
        with self.assertRaisesRegex(ValueError, 'events'):
            evaluate_session(SCENARIO, journal)

    def test_empty_summary(self):
        self.assertEqual(summarize_reports([]), dict(sessions=0, passed=0, mean_score=None))

    def test_summary(self):
        self.assertEqual(summarize_reports([dict(score=100, passed=True), dict(score=60, passed=False)]),
                         dict(sessions=2, passed=1, mean_score=80))


if __name__ == '__main__': unittest.main(verbosity=2)
