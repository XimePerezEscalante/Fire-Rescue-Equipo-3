// AgentController.cs
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AgentController : MonoBehaviour
{
    public GameObject agentPrefab; // Arrastra tu prefab aquí
    public float timePerStep = 1.0f; // Tiempo que tarda cada paso

    private Dictionary<int, GameObject> agents = new Dictionary<int, GameObject>();
    private bool isPlaying = false;

    public void StartSimulation(SimulationResult data)
    {
        // Limpiar simulación anterior si existe
        foreach(var kvp in agents) Destroy(kvp.Value);
        agents.Clear();

        // Instanciar agentes en su posición inicial (Paso 0)
        foreach (var agentData in data.results)
        {
            if (agentData.path.Count > 0)
            {
                Vector3 startPos = agentData.path[0].ToVector();
                GameObject newAgent = Instantiate(agentPrefab, startPos, Quaternion.identity);
                // Opcional: Ponerle nombre o color según ID
                newAgent.name = "Agent_" + agentData.id;
                agents[agentData.id] = newAgent;
            }
        }

        // Iniciar la corrutina de animación
        StartCoroutine(AnimateAgents(data));
    }

    IEnumerator AnimateAgents(SimulationResult data)
    {
        // Asumimos que todos tienen la misma longitud de pasos
        int totalSteps = data.results[0].path.Count;

        for (int i = 0; i < totalSteps - 1; i++)
        {
            float timer = 0;
            
            // Diccionario temporal para guardar posiciones origen y destino de este paso
            // para no recalcularlas en cada frame del Update
            Dictionary<int, Vector3> startPositions = new Dictionary<int, Vector3>();
            Dictionary<int, Vector3> endPositions = new Dictionary<int, Vector3>();

            // Preparamos los datos del paso actual para todos los agentes
            foreach (var agentData in data.results)
            {
                if (agents.ContainsKey(agentData.id) && (i + 1) < agentData.path.Count)
                {
                    startPositions[agentData.id] = agentData.path[i].ToVector();
                    endPositions[agentData.id] = agentData.path[i + 1].ToVector();
                }
            }

            // Interpolación (Lerp) durante timePerStep
            while (timer < timePerStep)
            {
                timer += Time.deltaTime;
                float t = timer / timePerStep;

                foreach (var kvp in agents)
                {
                    int id = kvp.Key;
                    GameObject agentObj = kvp.Value;

                    if (startPositions.ContainsKey(id) && endPositions.ContainsKey(id))
                    {
                        // Lerp suave
                        agentObj.transform.position = Vector3.Lerp(startPositions[id], endPositions[id], t);
                        
                        // Opcional: Que mire hacia donde va
                        Vector3 dir = endPositions[id] - startPositions[id];
                        if(dir != Vector3.zero) 
                            agentObj.transform.rotation = Quaternion.LookRotation(dir);
                    }
                }
                yield return null; // Esperar al siguiente frame
            }
        }
        Debug.Log("Simulación finalizada.");
    }
}