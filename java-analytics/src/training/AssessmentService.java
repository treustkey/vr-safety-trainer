package training;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

final class AssessmentService {
    Assessment evaluate(Scenario scenario, Session session) {
        if (!scenario.id.equals(session.scenarioId)) {
            throw new IllegalArgumentException("Scenario mismatch");
        }

        List<EvaluatedEvent> events = new ArrayList<>();
        Set<String> failed = new HashSet<>();
        int next = 0;
        double earned = 0;
        for (Event event : session.events) {
            Integer position = scenario.positionOf(event.action);
            Status status;
            if (position == null) {
                status = Status.unknown;
            } else {
                Step step = scenario.steps.get(position);
                if (position < next) {
                    status = Status.duplicate;
                } else if (position > next) {
                    status = Status.out_of_order;
                } else {
                    next++;
                    status = event.t_s <= step.deadline ? Status.ok : Status.late;
                }
                if (status == Status.ok) {
                    earned += step.weight;
                }
                if (step.critical && (status == Status.late || status == Status.out_of_order)) {
                    failed.add(step.action);
                }
            }
            events.add(new EvaluatedEvent(event, status));
        }

        List<String> missing = new ArrayList<>();
        List<String> criticalFailed = new ArrayList<>();
        double total = 0;
        for (int i = 0; i < scenario.steps.size(); i++) {
            Step step = scenario.steps.get(i);
            total += step.weight;
            if (i >= next) {
                missing.add(step.action);
            }
            if (step.critical && (i >= next || failed.contains(step.action))) {
                criticalFailed.add(step.action);
            }
        }
        if (!Double.isFinite(total)) {
            throw new IllegalArgumentException("Total weight is out of range");
        }
        double rawScore = 100 * earned / total;
        if (!Double.isFinite(rawScore)) {
            rawScore = 100 * (earned / total);
        }
        double rounded = new BigDecimal(rawScore).setScale(2, RoundingMode.HALF_EVEN).doubleValue();
        boolean passed = rawScore >= scenario.passScore && criticalFailed.isEmpty();
        return new Assessment(session, rounded, passed, missing, criticalFailed, events);
    }
}