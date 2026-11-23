package training;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;
import com.google.gson.Strictness;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

final class JsonFiles {
    private final Gson gson = new GsonBuilder().setStrictness(Strictness.STRICT)
        .setPrettyPrinting().create();

    Scenario readScenario(Path path) throws IOException {
        JsonObject json = read(path);
        List<Step> steps = new ArrayList<>();
        for (JsonElement element : array(json, "steps")) {
            JsonObject row = element.getAsJsonObject();
            JsonPrimitive critical = primitive(row, "critical");
            if (!critical.isBoolean()) {
                throw new IllegalArgumentException("critical must be boolean");
            }
            steps.add(new Step(string(row, "action"), number(row, "weight"),
                number(row, "deadline_s"), critical.getAsBoolean()));
        }
        return new Scenario(string(json, "scenario_id"), number(json, "pass_score"), steps);
    }

    Session readSession(Path path) throws IOException {
        JsonObject json = read(path);
        List<Event> events = new ArrayList<>();
        for (JsonElement element : array(json, "events")) {
            JsonObject row = element.getAsJsonObject();
            events.add(new Event(string(row, "event_id"), string(row, "action"), number(row, "t_s")));
        }
        return new Session(string(json, "session_id"), string(json, "learner_id"),
            string(json, "scenario_id"), events);
    }

    void write(Path path, Assessment assessment) throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        Files.writeString(path, gson.toJson(assessment) + System.lineSeparator());
    }

    private JsonObject read(Path path) throws IOException {
        return gson.fromJson(Files.readString(path), JsonObject.class);
    }

    private static JsonArray array(JsonObject row, String key) {
        JsonElement value = row == null ? null : row.get(key);
        if (value == null || !value.isJsonArray()) {
            throw new IllegalArgumentException(key + " must be an array");
        }
        return value.getAsJsonArray();
    }

    private static JsonPrimitive primitive(JsonObject row, String key) {
        JsonElement value = row.get(key);
        if (value == null || !value.isJsonPrimitive()) {
            throw new IllegalArgumentException("Missing or invalid field: " + key);
        }
        return value.getAsJsonPrimitive();
    }

    private static String string(JsonObject row, String key) {
        JsonPrimitive value = primitive(row, key);
        if (!value.isString()) {
            throw new IllegalArgumentException(key + " must be a string");
        }
        return value.getAsString();
    }

    private static double number(JsonObject row, String key) {
        JsonPrimitive value = primitive(row, key);
        if (!value.isNumber() || !Double.isFinite(value.getAsDouble())) {
            throw new IllegalArgumentException(key + " must be a finite number");
        }
        return value.getAsDouble();
    }
}