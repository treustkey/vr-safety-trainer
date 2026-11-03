using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class CreateTrainingScene {
    [MenuItem("Training/Create demo scene")]
    public static void Create() {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
        var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "Training floor";
        var marker = GameObject.CreatePrimitive(PrimitiveType.Cube);
        marker.name = "Training station";
        marker.transform.position = new Vector3(0,0.5f,0);
        new GameObject("Session recorder").AddComponent<SessionRecorder>();
        System.IO.Directory.CreateDirectory("Assets/Scenes");
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/Training.unity");
        AssetDatabase.SaveAssets();
    }
}
