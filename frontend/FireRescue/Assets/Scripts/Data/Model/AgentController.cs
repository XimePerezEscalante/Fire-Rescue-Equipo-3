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

    public void InitializeMap(MapDataResponse mapResponse)
    {
        string[,] wallsFromMap = new string[6,8];
        int[,] doorsFromMap = new int[8,4];
        int[,] entryPointsFromMap = new int[4,2];

        // Inicializar mapa
        Debug.Log("Walls length: " + mapResponse.walls.Length);
        string currentCell = "";

        for (int row = 0;row < 6;row++)
        {
            string rowData = mapResponse.walls[row];  

            for (int col = 0;col < 8;col++)
            {
                int startIndex = col * 4;     // posición donde inicia la celda
                string cell = rowData.Substring(startIndex, 4);
                wallsFromMap[row, col] = cell;

                Debug.Log($"Cell[{row},{col}] = {cell}");
                
                // Si quieres cada uno de los 4 chars:
                char up    = cell[0];
                char right = cell[1];
                char down  = cell[2];
                char left  = cell[3];

                Debug.Log($"U:{up} R:{right} D:{down} L:{left}");
            }
        }

        int doorIndex = 0;

        for (int i = 0; i < mapResponse.doors.Length; i++)
        {
            doorsFromMap[i, 0] = mapResponse.doors[i].p1[0]; // y1
            doorsFromMap[i, 1] = mapResponse.doors[i].p1[1]; // x1
            doorsFromMap[i, 2] = mapResponse.doors[i].p2[0]; // y2
            doorsFromMap[i, 3] = mapResponse.doors[i].p2[1]; // x2
        }

        
        Debug.Log("EntryPoints length: " + mapResponse.entryPoints.Length);
        foreach (var ep in mapResponse.entryPoints)
        {
            //Debug.Log("values length: " + ep);
        }
        

        for (int i = 0;i < 4;i++)
        {
            for (int j = 0;j < 2;j++)
            {
                entryPointsFromMap[i, j] = mapResponse.entryPoints[i].values[j];
                Debug.Log("values length: " + mapResponse.entryPoints[i].values[j]);
            }
        }



        /*for (int i = 0;i < mapResponse.doors.Length;i++)
        {
            Debug.Log(mapResponse.doors[i].status);
        
            doorsFromMap[i, 0] = mapResponse.doors[i].p1[0];
            doorsFromMap[i, 1] = mapResponse.doors[i].p1[1];

            doorsFromMap[i, 2] = mapResponse.doors[i].p2[0];
            doorsFromMap[i, 3] = mapResponse.doors[i].p2[1];
            
        }*/


        /*foreach (string row in mapResponse.walls)
        {
            Debug.Log("ROW: " + row);
            foreach (char col in row)
            {
                Debug.Log("COL: " + col);
            }
        }

        for (int i = 0;i < 6;i++)
        {
            for (int j = 0;j < 8;j++)
            {
                for (int k = 0;k < 4;k++)
                {
                    //currentCell += mapResponse.walls[i][j + k];
                }
                Debug.Log(wallsFromMap[i, j]);
                wallsFromMap[i, j] = currentCell;
                currentCell = "";
            }
        }
        */

        BM.Doors = doorsFromMap;
        BM.EntryPoints = entryPointsFromMap;
        BM.Walls = wallsFromMap;
        BM.AddEntryPointsToWallMatrix();
        BM.AddDoorsToWallMatrix();
        BM.PlaceWalls();
        
        
        

        //Debug.Log("Walls length: " + mapResponse.walls.Count);
        //Debug.Log(mapResponse.walls[0].row[0]);

        /*
        for (int i = 5;i >= 0;i--)
        {
            for (int j = 7;j >= 0;j--)
            {
                Debug.Log(mapResponse.walls[i, j]);
            }
        }*/
        //Debug.Log("EntryPoints length: " + mapResponse.entryPoints.Count);

        /*for (int i = 0;i < mapResponse.fires.Length;i++)
        {
            for (int j = 0; j < 2;j++)
            {
                Debug.Log(mapResponse.fires[i,j]);
            }
            
        }*/



        Debug.Log("Doors length: " + mapResponse.doors.Length);

        Debug.Log("Fires length: " + mapResponse.fires.Length);
    }

    // Crea los GameObjects iniciales
    void InitializeAgents(AgentData[] agentsData)
    {

        foreach (var data in agentsData)
        {
            //Vector3 pos = new Vector3(data.x, 0, data.y);
            //GameObject newAgent = Instantiate(agentPrefab, pos, Quaternion.identity);
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

                    // Interpolación lineal
                    //agentObj.transform.position = Vector3.Lerp(start, end, t);

                    // Rotación suave hacia el destino
                    Vector3 dir = end - start;
                    BM.MoveAgent(id, newX[id], newY[id], dir);
                    /*if (dir != Vector3.zero)
                    {
                        agentObj.transform.rotation = Quaternion.Slerp(
                            agentObj.transform.rotation, 
                            Quaternion.LookRotation(dir), 
                            t * 5 // Velocidad de giro
                        );
                    }*/
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

                Debug.Log($"Cell[{row},{col}] = {cell}");
                
                // Si quieres cada uno de los 4 chars:
                char up    = cell[0];
                char right = cell[1];
                char down  = cell[2];
                char left  = cell[3];

                Debug.Log($"U:{up} R:{right} D:{down} L:{left}");
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
            string currentValue;
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
                        //currentValue[1] = '2';
                    }
                    // Hacia la celda de la izquierda
                    else if (doorsFromMap[i,3] > currentJ)
                    {
                        XCoord = CorrectXCoordinates(currentJ - 2);
                        ZCoord = CorrectZCoordinates(currentI - 1);
                        YRotation = 90;
                        //currentValue[1] = '2'; currentI - 1, currentJ - 2
                    }
                }
                // La puerta conduce a la fila de arriba
                else if (doorsFromMap[i,2] < currentI)
                {
                    XCoord = CorrectXCoordinates(currentJ - 1);
                    ZCoord = CorrectZCoordinates(currentI - 1);
                    
                    //currentValue[0] = '2';
                    
                }
                // La puerta conduce a la fila de abajo
                else if (doorsFromMap[i,2] > currentI)
                {
                    XCoord = CorrectXCoordinates(currentJ - 1);
                    ZCoord = CorrectZCoordinates(currentI);
                    //currentValue[0] = '2';
                    //Debug.Log("CURRENT VALUE " + currentValue + "CURRENT I = " + currentI);
                    
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
        //BM.unknownPOIInstances = new GameObject[3];
        //BM.knownPOIInstances = new GameObject[3];
        BM.unknownPOIInstances.Clear();
        BM.knownPOIInstances.Clear();
        BM.activeWalls.Clear();
        activePois.Clear();

        BM.DeleteNullObjects(0);
        BM.DeleteNullObjects(1);
        InstantiateDoorsFromFrame(frame);
        UpdateWalls(frame);


        /*foreach (string wall in frame.walls)
        {
            foreach (char row in wall)
            {
                Debug.Log(row);
            }
            //Debug.Log(wall.GetType());
        }*/

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
            //Debug.Log(revealedPOI);

            //Debug.Log(frame.pois.Length + " VS " + previousFrame.pois.Length);
            /*int currentLength = frame.pois.Length;
            int previousLength = previousFrame.pois.Length;

            if (previousLength != currentLength) {
                int cont = 0;
                int indexPOIDestroyed = 0;

                foreach (var poi in previousFrame.pois)
                {
                    if (poi.revealed == false && poi.type == "f")
                    {
                        indexPOIDestroyed = cont;
                    }
                    cont += 1;
                    
                }

                for (int i = 0;i < currentLength;i++)
                {
                    if (i == indexPOIDestroyed)
                    {
                        BM.TurnPOIAround(frame.pois[i].y, frame.pois[i].x);
                    }
                    else
                    {
                        BM.MovePOI(frame.pois[i].y, frame.pois[i].x, true);
                    }
                
                }
            }
            else
            {
                for (int i = 0;i < frame.pois.Length;i++)
                {
                    if (frame.pois[i].revealed == true && previousFrame.pois[i].revealed == false)
                    {
                        BM.TurnPOIAround(frame.pois[i].y, frame.pois[i].x);
                    }
                    else if (previousFrame.pois[i].x != frame.pois[i].x || previousFrame.pois[i].y != frame.pois[i].y)
                    {
                        BM.MovePOI(frame.pois[i].y, frame.pois[i].x, true);
                    }
                
                }
            }*/

            foreach (var poi in frame.pois)
            {
                activePois.Add(BM.NewPOI(poi.revealed, poi.type, poi.y, poi.x));
                //BM.MovePOI(poi.y, poi.x, true);
                //Debug.Log("COMPARING: " + poi.revealed);
                // Solo instanciar si no ha sido salvada/recogida (depende de tu lógica en Python)
                // Aquí asumo que si está en la lista 'pois' es que está en el mapa
                //Vector3 pos = new Vector3(poi.x, 0.72f, poi.y);
                //activePois.Add(Instantiate(victimPrefab, pos, Quaternion.identity));
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
                /*if (previousFrame.doors[i].status == "Closed" && frame.doors[i].status != "Closed")
                {
                    BM.doors[i].GetComponent<Door>().OpenDoor();
                }*/
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