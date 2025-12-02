using System.Collections;
using System.Collections.Generic;
using System.Linq; // Necesario para buscar agentes por ID en las listas
using UnityEngine;

public class AgentController : MonoBehaviour
{
    [Header("Prefabs")]
    public BoardManager BM;
    public GameObject agentPrefab;
    public GameObject firePrefab; 
    public GameObject victimPrefab; 

    [Header("Settings")]
    public float timePerStep = 0.5f; // Tiempo entre frames

    // Diccionarios para mantener referencia a los objetos vivos en la escena
    private Dictionary<int, GameObject> agents = new Dictionary<int, GameObject>();
    private List<GameObject> activeFires = new List<GameObject>();
    private List<GameObject> activePois = new List<GameObject>();

    // --- PUNTO DE ENTRADA ---
    public void StartSimulation(SimulationResponse response)
    {
        // 1. Limpiar escena anterior
        CleanUpScene();

        // 2. Validar datos
        if (response.data == null || response.data.frames == null || response.data.frames.Length == 0)
        {
            Debug.LogError("Datos de simulación vacíos o nulos.");
            return;
        }

        // 3. Inicializar Agentes en el Frame 0
        Frame initialFrame = response.data.frames[0];
        InitializeAgents(initialFrame.agents);

        // 4. Iniciar la animación
        StartCoroutine(AnimateFrames(response.data.frames));
    }

    // Crea los GameObjects iniciales
    void InitializeAgents(AgentData[] agentsData)
    {

        foreach (var data in agentsData)
        {
            //Vector3 pos = new Vector3(data.x, 0, data.y);
            //GameObject newAgent = Instantiate(agentPrefab, pos, Quaternion.identity);
            // Llamar a la funcion de Move Agent BoardManager.MoveAgent(data.id, data.x, data.y)
            BM.MoveAgent(data.id, data.x, data.y);
            // Asignar nombre y guardar en diccionario
            BM.agents[data.id].name = $"Agent_{data.id}";
            agents[data.id] = BM.agents[data.id];//newAgent;
        }
    }

    // Corrutina principal que mueve todo paso a paso
    IEnumerator AnimateFrames(Frame[] frames)
    {
        // Iteramos desde el frame 0 hasta el penúltimo
        for (int i = 0; i < frames.Length - 1; i++)
        {
            Frame currentFrame = frames[i];
            Frame nextFrame = frames[i+1];

            // A. Actualizar entorno (Fuego y Víctimas) instantáneamente al inicio del paso
            UpdateEnvironment(currentFrame);

            // B. Mover Agentes suavemente hacia la posición del siguiente frame
            yield return StartCoroutine(MoveAgentsSmoothly(currentFrame, nextFrame));
        }

        // Renderizar el estado final del último frame
        UpdateEnvironment(frames[frames.Length-1]);
        Debug.Log("Simulación finalizada.");
    }

    // Interpolación de movimiento (Lerp)
    IEnumerator MoveAgentsSmoothly(Frame currentFrame, Frame nextFrame)
    {
        float timer = 0;

        // Pre-calcular posiciones objetivo para optimizar el bucle while
        // Dictionary: ID del Agente -> Posición Destino
        Dictionary<int, Vector3> targetPositions = new Dictionary<int, Vector3>();
        Dictionary<int, Vector3> startPositions = new Dictionary<int, Vector3>();

        foreach (var agentData in nextFrame.agents)
        {
            if (agents.ContainsKey(agentData.id))
            {
                /*targetPositions[agentData.id] = new Vector3(agentData.x, 0, agentData.y);
                // La posición inicial es donde está el objeto actualmente
                startPositions[agentData.id] = agents[agentData.id].transform.position;*/
                BM.MoveAgent(agentData.id, agentData.x, agentData.y);
            }
        }

        // Bucle de animación suave
        /*while (timer < timePerStep)
        {
            timer += Time.deltaTime;
            float t = timer / timePerStep;

            foreach (var kvp in agents)
            {
                int id = kvp.Key;
                GameObject agentObj = kvp.Value;

                // Solo movemos si el agente existe en el siguiente frame (por si murió o desapareció)
                if (targetPositions.ContainsKey(id))
                {
                    Vector3 start = startPositions[id];
                    Vector3 end = targetPositions[id];

                    // Interpolación lineal
                    agentObj.transform.position = Vector3.Lerp(start, end, t);

                    // Rotación suave hacia el destino
                    Vector3 dir = end - start;
                    if (dir != Vector3.zero)
                    {
                        agentObj.transform.rotation = Quaternion.Slerp(
                            agentObj.transform.rotation, 
                            Quaternion.LookRotation(dir), 
                            t * 5 // Velocidad de giro
                        );
                    }
                }
            }
            yield return null; // Esperar al siguiente frame de Unity
        }*/
        yield return null;
    }

    // Actualiza objetos estáticos o que no se mueven suavemente (Fuego, POIs)
    void UpdateEnvironment(Frame frame)
    {
        // Nota: Para optimizar, lo ideal sería usar Object Pooling, 
        // pero para empezar, destruir y crear es más fácil de entender.

        // 1. Limpiar fuegos y pois anteriores
        foreach (var f in activeFires) Destroy(f);
        foreach (var p in activePois) Destroy(p);
        activeFires.Clear();
        activePois.Clear();

        // 2. Instanciar Fuegos
        /*if (firePrefab != null && frame.fires != null)
        {
            foreach (var fire in frame.fires)
            {
                // Solo dibujamos si el estado indica fuego activo (asumiendo state > 0 es fuego)
                if (fire.state > 0) 
                {
                    Vector3 pos = new Vector3(fire.x, 0, fire.y);
                    activeFires.Add(Instantiate(firePrefab, pos, Quaternion.identity));
                }
            }
        }

        // 3. Instanciar POIs (Víctimas)
        if (victimPrefab != null && frame.pois != null)
        {
            foreach (var poi in frame.pois)
            {
                // Solo instanciar si no ha sido salvada/recogida (depende de tu lógica en Python)
                // Aquí asumo que si está en la lista 'pois' es que está en el mapa
                Vector3 pos = new Vector3(poi.x, 0, poi.y);
                activePois.Add(Instantiate(victimPrefab, pos, Quaternion.identity));
            }
        }*/
    }

    void CleanUpScene()
    {
        foreach (var kvp in agents) Destroy(kvp.Value);
        agents.Clear();
        foreach (var f in activeFires) Destroy(f);
        activeFires.Clear();
        foreach (var p in activePois) Destroy(p);
        activePois.Clear();
    }
}