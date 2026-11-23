package training;

import java.util.List;

final class Assessment {
    final String session_id;
    final String learner_id;
    final String scenario_id;
    final double score;
    final boolean passed;
    final String recommendation;
    final List<String> missing;
    final List<String> critical_failed;
    final List<EvaluatedEvent> events;

    Assessment(Session session, double score, boolean passed, List<String> missing,
               List<String> criticalFailed, List<EvaluatedEvent> events) {
        this.session_id = session.id;
        this.learner_id = session.learnerId;
        this.scenario_id = session.scenarioId;
        this.score = score;
        this.passed = passed;
        this.recommendation = passed ? "review_for_completion" : "repeat_training";
        this.missing = List.copyOf(missing);
        this.critical_failed = List.copyOf(criticalFailed);
        this.events = List.copyOf(events);
    }
}

final class EvaluatedEvent {
    final String event_id;
    final String action;
    final double t_s;
    final Status status;

    EvaluatedEvent(Event event, Status status) {
        this.event_id = event.event_id;
        this.action = event.action;
        this.t_s = event.t_s;
        this.status = status;
    }
}

enum Status { unknown, duplicate, out_of_order, ok, late }