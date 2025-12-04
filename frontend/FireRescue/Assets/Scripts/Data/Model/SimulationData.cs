using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class SimplePosition
{
    public float x;
    public float y;
    public float z;

    public Vector3 ToVector()
    {
        // Puedes ajustar la escala aquí si tu grid es muy pequeño
        // Ejemplo: return new Vector3(x, y, z) * 2.0f;
        return new Vector3(x, y, z);
    }
}

[System.Serializable]
public class AgentPath
{
    public int id;
    public List<SimplePosition> path;
}

[System.Serializable]
public class SimulationResult
{
    public List<AgentPath> results;
}