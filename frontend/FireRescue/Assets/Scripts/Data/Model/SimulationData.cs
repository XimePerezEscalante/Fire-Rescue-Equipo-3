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