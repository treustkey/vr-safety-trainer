using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

[Serializable] public class TrainingEvent {
    public string event_id;
    public string action;
    public float t_s;
}
[Serializable] public class TrainingSession {
    public string session_id;
    public string learner_id = "synthetic-001";
    public string scenario_id = "training-01-v1";
    public List<TrainingEvent> events = new List<TrainingEvent>();
}

public class SessionRecorder : MonoBehaviour {
    private TrainingSession session;
    private float started;
    private string savedPath = "";
    void Start() { ResetSession(); }
    public void ResetSession() {
        session = new TrainingSession { session_id = Guid.NewGuid().ToString() };
        started = Time.realtimeSinceStartup;
        savedPath = "";
    }
    public void RecordAction(string action) {
        session.events.Add(new TrainingEvent {
            event_id = Guid.NewGuid().ToString(), action = action,
            t_s = Time.realtimeSinceStartup - started
        });
    }
    public void SaveSession() {
        savedPath = Path.Combine(Application.persistentDataPath, session.session_id + ".json");
        File.WriteAllText(savedPath, JsonUtility.ToJson(session, true));
        Debug.Log("Session saved: " + savedPath);
    }
    void OnGUI() {
        GUILayout.BeginArea(new Rect(20,20,600,420), GUI.skin.box);
        GUILayout.Label("VR Safety Trainer / desktop telemetry prototype");
        GUILayout.Label("Synthetic educational sequence; not a safety procedure");
        if (GUILayout.Button("1 Recognize alarm")) RecordAction("recognize_alarm");
        if (GUILayout.Button("2 Notify instructor")) RecordAction("notify_instructor");
        if (GUILayout.Button("3 Leave training zone")) RecordAction("leave_zone");
        if (GUILayout.Button("Export session JSON")) SaveSession();
        if (GUILayout.Button("New session")) ResetSession();
        GUILayout.Label("Events: " + session.events.Count);
        GUILayout.Label(savedPath);
        GUILayout.EndArea();
    }
}
