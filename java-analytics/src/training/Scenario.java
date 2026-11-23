package training;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

final class Scenario {
    final String id;
    final double passScore;
    final List<Step> steps;
    private final Map<String, Integer> positions = new HashMap<>();

    Scenario(String id, double passScore, List<Step> steps) {
        if (passScore < 0 || passScore > 100 || steps.isEmpty()) {
            throw new IllegalArgumentException("Invalid threshold or empty scenario");
        }
        this.id = id;
        this.passScore = passScore;
        this.steps = List.copyOf(steps);
        for (int i = 0; i < steps.size(); i++) {
            if (positions.putIfAbsent(steps.get(i).action, i) != null) {
                throw new IllegalArgumentException("Duplicate scenario action");
            }
        }
    }

    Integer positionOf(String action) {
        return positions.get(action);
    }
}

final class Step {
    final String action;
    final double weight;
    final double deadline;
    final boolean critical;

    Step(String action, double weight, double deadline, boolean critical) {
        if (weight <= 0 || deadline <= 0) {
            throw new IllegalArgumentException("Weights and deadlines must be positive");
        }
        this.action = action;
        this.weight = weight;
        this.deadline = deadline;
        this.critical = critical;
    }
}
