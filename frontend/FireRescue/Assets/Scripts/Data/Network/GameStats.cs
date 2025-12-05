// --- Estructuras para Mapear el JSON del Servidor ---

[System.Serializable]
public class SimulationResponse
{
    public float score;
    public string end_reason;
    public int steps_total;
    public SimulationData data; // El objeto "data" del JSON
}

[System.Serializable]
public class SimulationData
{
    public SimMetadata metadata;
    public Frame[] frames; // Lista de frames paso a paso
}

[System.Serializable]
public class SimMetadata
{
    public int width;
    public int height;
    public int agents;
}

[System.Serializable]
public class Frame
{
    public int step;
    public AgentData[] agents;
    public FireData[] fires;
    public PoiData[] pois;
    public StatsData stats;
    public DoorData[] doors;
    public string[] walls;
}

[System.Serializable]
public class AgentData
{
    public int id;
    public int x;
    public int y;
    public bool carrying;
    public string role;
}

[System.Serializable]
public class FireData
{
    public int x;
    public int y;
    public int state; // Dependiendo de cómo definas el estado en Python
}

[System.Serializable]
public class PoiData
{
    public int x;
    public int y;
    public string type; // "victim" o "false"
    public bool revealed;
}

[System.Serializable]
public class PoiDataMapResponse
{
    public int x;
    public int y;
    public int type; // "victim" o "false"
    public bool revealed;
}

[System.Serializable]
public class DoorData
{
    public int[] p1;
    public int[] p2;
    public string status;  
}

[System.Serializable]
public class EntryPointData
{
    public int[] values;
}

[System.Serializable]
public class WallData
{
    public string[] row;
}



[System.Serializable]
public class StatsData
{
    public int saved;
    public int lost;
    public int damage;
}

// Para la respuesta de /getMap
[System.Serializable]
public class MapDataResponse
{
    public int width;
    public int height;
    public FireData[] fires;
    public PoiDataMapResponse[] pois;
    public string[] walls;
    public DoorData[] doors;
    public EntryPointData[] entryPoints;
}