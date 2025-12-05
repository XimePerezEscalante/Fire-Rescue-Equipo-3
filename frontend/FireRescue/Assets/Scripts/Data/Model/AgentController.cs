using System.Collections;
using System.Collections.Generic;
using System.Linq; // Necesario para buscar agentes por ID en las listas
using UnityEngine;
using TMPro;

public class AgentController : MonoBehaviour
{
    [Header("Prefabs")]
    public BoardManager BM;
    public GameObject agentPrefab;
    public GameObject firePrefab; 
    public GameObject victimPrefab; 
    public GameObject doorPrefab;

    public TMP_Text savedText;
    public TMP_Text lostText;
    public TMP_Text damageText;


    [Header("Settings")]
    public float timePerStep = 0.5f; // Tiempo entre frames

    // Diccionarios para mantener referencia a los objetos vivos en la escena
    private Dictionary<int, GameObject> agents = new Dictionary<int, GameObject>();
    private List<GameObject> activeFires = new List<GameObject>();
    private List<GameObject> activePois = new List<GameObject>();
    private List<GameObject> activeDoors = new List<GameObject>();

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

    public void SetMatrices(Frame frame)
    {
        int lengthDoor = frame.doors.Length;
        int lengthWalls = frame.walls.Length;
        
        string[,] wallsFromMap = new string[lengthWalls, 8];
        int[,] doorsFromMap = new int[lengthDoor, 4];

        for (int row = 0;row < 6;row++)
        {
            string rowData = frame.walls[row];  

            for (int col = 0;col < 8;col++)
            {
                int startIndex = col * 4;     // posición donde inicia la celda
                string cell = rowData.Substring(startIndex, 4);
                wallsFromMap[row, col] = cell;
                
                // Si quieres cada uno de los 4 chars:
                char up    = cell[0];
                char right = cell[1];
                char down  = cell[2];
                char left  = cell[3];

            }
        }

        for (int i = 0; i < frame.doors.Length; i++)
        {
            doorsFromMap[i, 0] = frame.doors[i].p1[0]; // y1
            doorsFromMap[i, 1] = frame.doors[i].p1[1]; // x1
            doorsFromMap[i, 2] = frame.doors[i].p2[0]; // y2
            doorsFromMap[i, 3] = frame.doors[i].p2[1]; // x2
        }

        BM.Doors = doorsFromMap;
        BM.Walls = wallsFromMap;

        BM.AddDoorsToWallMatrix();
        BM.PlaceWalls();

    }

    public void InitializeMap(MapDataResponse mapResponse)
    {
        string[,] wallsFromMap = new string[6,8];
        int[,] doorsFromMap = new int[8,4];
        int[,] entryPointsFromMap = new int[4,2];
        int[,] poisFromMap = new int[3,3];

        for (int row = 0;row < 6;row++)
        {
            string rowData = mapResponse.walls[row];  

            for (int col = 0;col < 8;col++)
            {
                int startIndex = col * 4;     // posición donde inicia la celda
                string cell = rowData.Substring(startIndex, 4);
                wallsFromMap[row, col] = cell;

                
                // Cada uno de los 4 chars
                char up    = cell[0];
                char right = cell[1];
                char down  = cell[2];
                char left  = cell[3];
            }
        }

        Debug.Log("POIS LENGTH: " + mapResponse.pois.Length);

        for (int i = 0;i < mapResponse.pois.Length;i++)
        {
            // Fila
            poisFromMap[i,0] = mapResponse.pois[i].y;
            // Columna
            poisFromMap[i,1] = mapResponse.pois[i].x;
            // Falsa alarma
            poisFromMap[i,2] = mapResponse.pois[i].type;
        }

        for (int i = 0;i < mapResponse.doors.Length; i++)
        {
            doorsFromMap[i, 0] = mapResponse.doors[i].p1[0]; // y1
            doorsFromMap[i, 1] = mapResponse.doors[i].p1[1]; // x1
            doorsFromMap[i, 2] = mapResponse.doors[i].p2[0]; // y2
            doorsFromMap[i, 3] = mapResponse.doors[i].p2[1]; // x2
        }


        for (int i = 0;i < 4;i++)
        {
            for (int j = 0;j < 2;j++)
            {
                entryPointsFromMap[i, j] = mapResponse.entryPoints[i].values[j];
            }
        }

        BM.POI = poisFromMap;
        BM.Doors = doorsFromMap;
        BM.EntryPoints = entryPointsFromMap;
        BM.Walls = wallsFromMap;
        BM.AddEntryPointsToWallMatrix();
        BM.AddDoorsToWallMatrix();
        BM.PlaceWalls();
        BM.InstantiateUnknownPOI();
    }

    // Crea los GameObjects iniciales
    void InitializeAgents(AgentData[] agentsData)
    {

        foreach (var data in agentsData)
        {
            // Llamar a la funcion de Move Agent BoardManager.MoveAgent(data.id, data.x, data.y)
            BM.MoveAgent(data.id, data.x, data.y, new Vector3(0,0,0));
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
            Frame previousFrame;
            if (i > 0)
            {
                previousFrame = frames[i - 1];
            }
            else
            {
                previousFrame = frames[0];
            }
            

            // A. Actualizar entorno (Fuego y Víctimas) instantáneamente al inicio del paso
            UpdateEnvironment(currentFrame, previousFrame);

            // B. Mover Agentes suavemente hacia la posición del siguiente frame
            yield return StartCoroutine(MoveAgentsSmoothly(currentFrame, nextFrame));
        }

        // Renderizar el estado final del último frame
        UpdateEnvironment(frames[frames.Length-1], frames[frames.Length-2]);
        Debug.Log("Simulación finalizada.");
    }

    // Interpolación de movimiento (Lerp)
    IEnumerator MoveAgentsSmoothly(Frame currentFrame, Frame nextFrame)
    {
        int[] newX = new int[6];
        int[] newY = new int[6];

        // Pre-calcular posiciones objetivo para optimizar el bucle while
        // Dictionary: ID del Agente -> Posición Destino
        Dictionary<int, Vector3> targetPositions = new Dictionary<int, Vector3>();
        Dictionary<int, Vector3> startPositions = new Dictionary<int, Vector3>();

        foreach (var agentData in nextFrame.agents)
        {
            if (agents.ContainsKey(agentData.id))
            {
                targetPositions[agentData.id] = new Vector3(agentData.x, 0, agentData.y);
                // La posición inicial es donde está el objeto actualmente
                startPositions[agentData.id] = agents[agentData.id].transform.position;
                newX[agentData.id] = agentData.x;
                newY[agentData.id] = agentData.y;
                //BM.MoveAgent(agentData.id, agentData.x, agentData.y);
            }
        }

        foreach (var kvp in agents)
            {
                int id = kvp.Key;
                GameObject agentObj = kvp.Value;

                // Solo movemos si el agente existe en el siguiente frame (por si murió o desapareció)
                if (targetPositions.ContainsKey(id))
                {
                    Vector3 start = startPositions[id];
                    Vector3 end = targetPositions[id];

                    // Rotación suave hacia el destino
                    Vector3 dir = end - start;
                    BM.MoveAgent(id, newX[id], newY[id], dir);
                }
            }
            yield return null; // Esperar al siguiente frame de Unity
        
    }

    public void UpdateWalls(Frame frame) 
    {
        string[,] wallsFromMap = new string[6,8];

        for (int row = 0;row < 6;row++)
        {
            string rowData = frame.walls[row];  

            for (int col = 0;col < 8;col++)
            {
                int startIndex = col * 4;     // posición donde inicia la celda
                string cell = rowData.Substring(startIndex, 4);
                wallsFromMap[row, col] = cell;
                
                // Cada uno de los 4 chars
                char up    = cell[0];
                char right = cell[1];
                char down  = cell[2];
                char left  = cell[3];
            }
        }
        BM.Walls = wallsFromMap;
        BM.PlaceWalls();
    }

    private GameObject InstantiateDoor(float XCoord, float YCoord, float ZCoord, float YRotation)
    {
        Quaternion spawnRotation = Quaternion.Euler(0f, YRotation, 0f);
        GameObject newDoor;
        if (YRotation == 0) {
            // Modificar posicion en x de la puerta para que quede en medio de la pared
            Vector3 doorSpawnPosition = new Vector3(XCoord + 1.3f, YCoord, ZCoord);
            // Crear instancia de puerta
            newDoor = Instantiate(doorPrefab, doorSpawnPosition, spawnRotation);
            // Asignar posicion 0 -> "frontal"
            newDoor.GetComponent<Door>().position = 0;
        }
        else
        {
            Vector3 doorSpawnPosition = new Vector3(XCoord, YCoord, ZCoord - 1.3f);
            // Crear instancia de puerta
            newDoor = Instantiate(doorPrefab, doorSpawnPosition, spawnRotation);
            // Asignar posicion 1 -> "lateral"
            newDoor.GetComponent<Door>().position = 1;
        }

        return newDoor;
    }

    private float CorrectXCoordinates(int col)
    {
        // Restar 1 al valor para ajustarse a las coordenadas correctas
        return (col - 1) * 6.4f;
    }

    private float CorrectZCoordinates(int row)
    {
        // Restarle a 6 el valor para ajustarse a las coordenadas del tablero
        return (6 - row) * 6.4f;
    }

    private void InstantiateDoorsFromFrame(Frame frame)
    {
        // Limpiar puertas anteriores
        foreach (GameObject d in activeDoors)
        {
            if (d != null)
                Destroy(d);
        }
        activeDoors.Clear();

        // Verificar si hay puertas en el frame
        if (frame.doors == null || frame.doors.Length == 0)
        {
            Debug.Log("No hay puertas en el frame.");
            return;
        }

        Debug.Log("Instanciando " + frame.doors.Length + " puertas...");

        // Recorrer datos del JSON
        int[,] doorsFromMap = new int[frame.doors.Length, 4];

        // Obtener posiciones p1 y p2 del JSON
        for (int i = 0; i < frame.doors.Length / 4; i++)
        {
            doorsFromMap[i, 0] = frame.doors[i].p1[0]; // y1
            doorsFromMap[i, 1] = frame.doors[i].p1[1]; // x1
            doorsFromMap[i, 2] = frame.doors[i].p2[0]; // y2
            doorsFromMap[i, 3] = frame.doors[i].p2[1]; // x2
        }
        
            int currentI;
            int currentJ;
            float YRotation = 0;
            float XCoord = 0;
            float YCoord = 0.5f;
            float ZCoord = 0;

            for (int i = 0;i < frame.doors.Length;i++)
            {
                currentI = doorsFromMap[i,0];
                currentJ = doorsFromMap[i,1];

                // La puerta conduce a la misma fila
                if (doorsFromMap[i,2] == currentI)
                {
                    // Hacia la celda de la derecha
                    if (doorsFromMap[i,3] > currentJ)
                    {
                        XCoord = CorrectXCoordinates(currentJ);
                        ZCoord = CorrectZCoordinates(currentI - 1);
                        YRotation = 90;
                    }
                    // Hacia la celda de la izquierda
                    else if (doorsFromMap[i,3] > currentJ)
                    {
                        XCoord = CorrectXCoordinates(currentJ - 2);
                        ZCoord = CorrectZCoordinates(currentI - 1);
                        YRotation = 90;
                    }
                }
                // La puerta conduce a la fila de arriba
                else if (doorsFromMap[i,2] < currentI)
                {
                    XCoord = CorrectXCoordinates(currentJ - 1);
                    ZCoord = CorrectZCoordinates(currentI - 1);
                    
                }
                // La puerta conduce a la fila de abajo
                else if (doorsFromMap[i,2] > currentI)
                {
                    XCoord = CorrectXCoordinates(currentJ - 1);
                    ZCoord = CorrectZCoordinates(currentI);
                    
                }

            GameObject newDoor = InstantiateDoor(XCoord, YCoord, ZCoord, YRotation);
            activeDoors.Add(newDoor);
        }
    }



    // Actualiza objetos estáticos o que no se mueven suavemente (Fuego, POIs)
    void UpdateEnvironment(Frame frame, Frame previousFrame)
    {
        // Nota: Para optimizar, lo ideal sería usar Object Pooling, 
        // pero para empezar, destruir y crear es más fácil de entender.

        // 1. Limpiar fuegos y pois anteriores
        foreach (var f in BM.activeFires) Destroy(f);
        foreach (var p in BM.unknownPOIInstances) Destroy(p);
        foreach (var p in BM.knownPOIInstances) Destroy(p);
        foreach (var w in BM.activeWalls) Destroy(w);
        foreach (var d in BM.doors) Destroy(d);
        foreach (var p in activePois) Destroy(p);
        BM.Walls = null;
        BM.doors = new GameObject[8];
        BM.activeFires = new GameObject[30];
        BM.unknownPOIInstances.Clear();
        BM.knownPOIInstances.Clear();
        BM.activeWalls.Clear();
        activePois.Clear();

        BM.DeleteNullObjects(0);
        BM.DeleteNullObjects(1);
        SetMatrices(frame);

        // 2. Instanciar Fuegos
        if (firePrefab != null && frame.fires != null)
        {
            foreach (var fire in frame.fires)
            {
                // Solo dibujamos si el estado indica fuego activo (asumiendo state > 0 es fuego)
                if (fire.state > 0) 
                {
                    Vector3 pos = new Vector3(fire.x, 0.72f, fire.y);
                    // activeFires.Add(Instantiate(firePrefab, pos, Quaternion.identity));
                    BM.NewFire(true, fire.state, fire.x, fire.y);
                }
            }
        }

        // 3. Instanciar POIs (Víctimas)
        if (victimPrefab != null && frame.pois != null)
        {

            foreach (var poi in frame.pois)
            {
                activePois.Add(BM.NewPOI(poi.revealed, poi.type, poi.y, poi.x));
            }
        }

        if (BM.doors != null)
        {
            for (int i = 0; i < frame.doors.Length;i++)
            {
                if (frame.doors[i].status == "Open" && BM.doors[i] != null)
                {
                    BM.doors[i].GetComponent<Door>().OpenDoor();
                }
            }
        }

        

        savedText.text = "" + frame.stats.saved;
        lostText.text = "" + frame.stats.lost;
        damageText.text = "" + frame.stats.damage;
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