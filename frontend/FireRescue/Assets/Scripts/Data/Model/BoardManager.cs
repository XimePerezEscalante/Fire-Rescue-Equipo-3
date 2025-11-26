using UnityEngine;

public class BoardManager : MonoBehaviour
{
    public GameObject wallPrefab;
    public GameObject wallDoorwayPrefab;
    public GameObject doorPrefab;
    public GameObject unknownPointOfInterestPrefab;
    public GameObject knownPointOfInterestPrefab;
    public GameObject firePrefab;
    public static float XWall{get; private set;}
    public static float YWall{get; private set;}
    public static float ZWall{get; private set;}
    private static string[,] walls = new string[,]
    {
        {
            {"1100"},{"1000"},{"1001"},{"1100"},{"1001"},{"1100"},{"1000"}, {"1001"}
        },
        {
            {"0100"},{"0000"},{"0011"},{"0110"},{"0011"},{"0110"},{"0010"},{"0011"}
        },
        {
            {"0100"},{"0001"},{"1100"},{"1000"},{"1000"},{"1001"},{"1100"},{"1001"}
        },
        {
            {"0110"},{"0011"},{"0110"},{"0010"},{"0010"},{"0011"},{"0110"},{"0011"}
        },
        {
            {"1100"},{"1000"},{"1000"},{"1000"},{"1001"},{"1100"},{"1001"},{"1101"}
        },
        {
            {"0110"},{"0010"},{"0010"},{"0010"},{"0011"},{"0110"},{"0011"},{"0111"}
        }
    };
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
