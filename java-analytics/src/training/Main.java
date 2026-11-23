package training;

import com.google.gson.JsonParseException;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Locale;

public final class Main {
    public static void main(String[] args) {
        if (args.length != 3) {
            System.err.println("Usage: training.Main SCENARIO.json SESSION.json OUTPUT.json");
            System.exit(2);
        }
        try {
            JsonFiles files = new JsonFiles();
            Scenario scenario = files.readScenario(Path.of(args[0]));
            Session session = files.readSession(Path.of(args[1]));
            Assessment result = new AssessmentService().evaluate(scenario, session);
            files.write(Path.of(args[2]), result);
            System.out.printf(Locale.ROOT, "%s: score=%.2f, passed=%s, critical=%s%n",
                result.session_id, result.score, result.passed, result.critical_failed);
        } catch (IOException | JsonParseException | IllegalArgumentException | IllegalStateException error) {
            System.err.println("Assessment error: " + error.getMessage());
            System.exit(2);
        }
    }
}