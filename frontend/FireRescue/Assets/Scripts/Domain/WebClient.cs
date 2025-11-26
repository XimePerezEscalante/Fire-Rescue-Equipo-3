// WebClient.cs
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class WebClient : MonoBehaviour
{
    // Referencia al controlador que moverá los agentes
    public AgentController agentController;

    void Start()
    {
        // Enviamos un JSON dummy para iniciar el POST
        StartCoroutine(SendData("{}"));
    }

    IEnumerator SendData(string data)
    {
        WWWForm form = new WWWForm();
        form.AddField("bundle", "the data");
        string url = "http://localhost:8585";

        using (UnityWebRequest www = UnityWebRequest.Post(url, form))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
            www.uploadHandler = new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.LogError(www.error);
            }
            else
            {
                string responseText = www.downloadHandler.text;
                Debug.Log("Datos recibidos: " + responseText);

                // 1. Deserializar usando JsonUtility y nuestras clases
                SimulationResult simData = JsonUtility.FromJson<SimulationResult>(responseText);

                // 2. Enviar los datos al controlador de agentes
                if (agentController != null)
                {
                    agentController.StartSimulation(simData);
                }
                else
                {
                    Debug.LogError("AgentController no asignado en el Inspector.");
                }
            }
        }
    }
}