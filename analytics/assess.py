"""Procedural assessment of synthetic VR session logs. No external packages."""
import argparse
import json
import math
from pathlib import Path


def finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def validate_session(scenario, session):
    if not isinstance(scenario, dict) or not isinstance(session, dict):
        raise ValueError('Scenario and journal must be objects')
    if not isinstance(scenario.get('scenario_id'), str):
        raise ValueError('Scenario scenario_id must be a string')
    for key in ('session_id', 'learner_id', 'scenario_id'):
        if not isinstance(session.get(key), str):
            raise ValueError(f'Journal {key} must be a string')

    steps = scenario.get('steps')
    if not isinstance(steps, list) or not steps:
        raise ValueError('Scenario steps must be a nonempty array')
    actions = set()
    for step in steps:
        if not isinstance(step, dict) or not isinstance(step.get('action'), str):
            raise ValueError('Each step must be an object with a string action')
        action = step['action']
        if action in actions:
            raise ValueError('Duplicate scenario action')
        actions.add(action)
        for key in ('weight', 'deadline_s'):
            value = step.get(key)
            if not finite_number(value) or value <= 0:
                raise ValueError(f'{key} must be a positive finite number')
        if not isinstance(step.get('critical'), bool):
            raise ValueError('critical must be boolean')

    if session['scenario_id'] != scenario['scenario_id']:
        raise ValueError('Scenario mismatch')
    threshold = scenario.get('pass_score')
    if not finite_number(threshold) or not 0 <= threshold <= 100:
        raise ValueError('Invalid threshold')

    events = session.get('events')
    if not isinstance(events, list):
        raise ValueError('Journal events must be an array')
    previous, ids = -1, set()
    for event in events:
        if not isinstance(event, dict):
            raise ValueError('Each event must be an object')
        t = event.get('t_s')
        if not finite_number(t) or t < previous or t < 0:
            raise ValueError('Events require nonnegative chronological finite time')
        event_id = event.get('event_id')
        if not isinstance(event_id, str) or event_id in ids:
            raise ValueError('Duplicate or invalid event_id')
        if not isinstance(event.get('action'), str):
            raise ValueError('action must be a string')
        ids.add(event_id)
        previous = t


def evaluate_session(scenario, session):
    validate_session(scenario, session)
    steps = scenario['steps']
    positions = {step['action']: i for i, step in enumerate(steps)}
    rows, seen, next_step, earned = [], set(), 0, 0
    for event in session['events']:
        action = event['action']
        index = positions.get(action)
        if index is None:
            status = 'unknown'
        elif action in seen:
            status = 'duplicate'
        elif index != next_step:
            status = 'out_of_order'
        else:
            seen.add(action)
            next_step += 1
            status = 'ok' if event['t_s'] <= steps[index]['deadline_s'] else 'late'
            if status == 'ok':
                earned += steps[index]['weight']
        rows.append(dict(event_id=event['event_id'], action=action, t_s=event['t_s'], status=status))
    missing = [s['action'] for s in steps if s['action'] not in seen]
    critical_actions = {s['action'] for s in steps if s['critical']}
    failed_set = critical_actions.intersection(missing) | {
        r['action'] for r in rows if r['action'] in critical_actions and r['status'] in ('late', 'out_of_order')
    }
    critical_failed = [s['action'] for s in steps if s['action'] in failed_set]
    raw_score = 100 * earned / sum(s['weight'] for s in steps)
    passed = raw_score >= scenario['pass_score'] and not critical_failed
    return dict(session_id=session['session_id'], learner_id=session['learner_id'],
                scenario_id=session['scenario_id'], score=round(raw_score, 2),
                passed=passed, recommendation='review_for_completion' if passed else 'repeat_training',
                missing=missing, critical_failed=critical_failed, events=rows)


def summarize_reports(reports):
    count, passed, total = 0, 0, 0
    for report in reports:
        count += 1
        passed += int(report['passed'])
        total += report['score']
    return dict(sessions=count, passed=passed, mean_score=round(total / count, 2) if count else None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', type=Path, required=True)
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    scenario = json.loads(args.scenario.read_text(encoding='utf-8'))
    session = json.loads(args.session.read_text(encoding='utf-8'))
    report = evaluate_session(scenario, session)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'events'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
