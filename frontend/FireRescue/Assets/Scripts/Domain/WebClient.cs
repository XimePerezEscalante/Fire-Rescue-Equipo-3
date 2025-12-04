using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;

public class WebClient : MonoBehaviour
{
    // Referencia a tu controlador principal en Unity
    public AgentController agentController;

    private string baseUrl = "http://localhost:8585";

    void Start()
    {
        // Paso 1: Obtener información del Mapa
        StartCoroutine(GetMapData());
    }

    // --- GET: Obtener Mapa ---
    IEnumerator GetMapData()
    {
        string url = baseUrl + "/getMap";
        Debug.Log("Solicitando mapa a: " + url);

        using (UnityWebRequest www = UnityWebRequest.Get(url))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Error obteniendo mapa: " + www.error);
            }
            else
            {
                string jsonResult = www.downloadHandler.text;
                Debug.Log("Mapa recibido: " + jsonResult);
                
                // Parseamos los datos básicos del mapa
                MapDataResponse mapData = JsonUtility.FromJson<MapDataResponse>(jsonResult);

                // Iniciamos la configuración del tablero en Unity (si tienes un método para ello)
                if (agentController != null)
                {
                    agentController.InitializeMap(mapData);
                }

                // Una vez tenemos el mapa, pedimos la simulación en aleatorio
                //StartCoroutine(PostSimulationIntelligent());
                StartCoroutine(PostSimulationRandom());
            }
        }
    }

    // --- POST: Correr Simulación en aleatorio ---
    IEnumerator PostSimulationRandom()
    {
        string url = baseUrl + "/simulation/random";
        Debug.Log("Solicitando simulación a: " + url);

        // Si quieres enviar configuración personalizada, hazlo aquí
        // Por ahora enviamos un JSON vacío para usar la config por defecto del servidor
        string jsonData = "{}"; 
        
        using (UnityWebRequest www = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            www.uploadHandler = new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Error en simulación: " + www.error);
            }
            else
            {
                string jsonResult = www.downloadHandler.text;
                Debug.Log("Simulación recibida (JSON crudo): " + jsonResult);

                try 
                {
                    SimulationResponse simResult = JsonUtility.FromJson<SimulationResponse>(jsonResult);

                    if (agentController != null)
                    {
                        Debug.Log($"Simulación exitosa. Score: {simResult.score}, Pasos: {simResult.steps_total}");
                        // Enviamos los datos listos para ser animados
                        agentController.StartSimulation(simResult);
                    }
                    else
                    {
                        Debug.LogError("AgentController no asignado en el Inspector.");
                    }
                }
                catch (System.Exception e)
                {
                    Debug.LogError("Error parseando JSON: " + e.Message);
                }
            }
        }
    }
    
    // --- POST: Correr Simulación en aleatorio ---
    IEnumerator PostSimulationIntelligent()
    {
        string url = baseUrl + "/simulation/intelligent";
        Debug.Log("Solicitando simulación a: " + url);

        // Si quieres enviar configuración personalizada, hazlo aquí
        // Por ahora enviamos un JSON vacío para usar la config por defecto del servidor
        string jsonData = "{}"; 
        
        using (UnityWebRequest www = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            www.uploadHandler = new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Error en simulación: " + www.error);
            }
            else
            {
                string jsonResult = www.downloadHandler.text;
                Debug.Log("Simulación recibida (JSON crudo): " + jsonResult);

                try 
                {
                    SimulationResponse simResult = JsonUtility.FromJson<SimulationResponse>(jsonResult);

                    if (agentController != null)
                    {
                        Debug.Log($"Simulación exitosa. Score: {simResult.score}, Pasos: {simResult.steps_total}");
                        // Enviamos los datos listos para ser animados
                        agentController.StartSimulation(simResult);
                    }
                    else
                    {
                        Debug.LogError("AgentController no asignado en el Inspector.");
                    }
                }
                catch (System.Exception e)
                {
                    Debug.LogError("Error parseando JSON: " + e.Message);
                }
            }
        }
    }
}