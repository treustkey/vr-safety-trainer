package training;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

final class Session {
    final String id;
    final String learnerId;
    final String scenarioId;
    final List<Event> events;

    Session(String id, String learnerId, String scenarioId, List<Event> events) {
        this.id = id;
        this.learnerId = learnerId;
        this.scenarioId = scenarioId;
        this.events = List.copyOf(events);
        Set<String> ids = new HashSet<>();
        double previous = 0;
        for (Event event : this.events) {
            if (event.t_s < previous || !ids.add(event.event_id)) {
                throw new IllegalArgumentException("Invalid event order, time or duplicate ID");
            }
            previous = event.t_s;
        }
    }
}

final class Event {
    final String event_id;
    final String action;
    final double t_s;

    Event(String id, String action, double time) {
        this.event_id = id;
        this.action = action;
        this.t_s = time;
    }
}