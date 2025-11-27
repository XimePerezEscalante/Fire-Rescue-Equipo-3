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
    private static string[,,] Walls = new string[6,8,1]
        {
            {
                {"1100"},{"1000"},{"1001"},{"1200"},{"1001"},{"3100"},{"1000"}, {"1001"}
            },
            {
                {"0100"},{"0000"},{"0011"},{"0110"},{"0011"},{"0210"},{"0010"},{"0021"}
            },
            {
                {"0100"},{"0001"},{"1200"},{"1000"},{"1000"},{"1001"},{"1100"},{"1001"}
            },
            {
                {"0110"},{"0011"},{"0110"},{"0010"},{"0010"},{"0011"},{"0210"},{"0011"}
            },
            {
                {"1100"},{"1000"},{"1000"},{"2000"},{"1001"},{"1100"},{"1001"},{"1101"}
            },
            {
                {"0110"},{"0010"},{"0030"},{"0010"},{"0011"},{"0210"},{"0011"},{"0211"}
            }
        };
    
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        XWall = 0;
        YWall = 0.5f;
        ZWall = 0;
        PlaceWalls();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private int CheckUp(string cell)
    {
        //Debug.Log(cell[0]);
        int intValue = cell[0] - '0';
        return intValue;
    }

    private int CheckLeft(string cell)
    {
        //Debug.Log(cell[1]);
        int intValue = cell[1] - '0';
        return intValue;
    }

    private int CheckDown(string cell)
    {
        //Debug.Log(cell[2]);
        int intValue = cell[2] - '0';
        return intValue;
    }

    private int CheckRight(string cell)
    {
        //Debug.Log(cell[3]);
        int intValue = cell[3] - '0';
        return intValue;
    }

    private void InstantiateWall(int type, float XCoord, float YCoord, float ZCoord, float YRotation)
    {
        Vector3 spawnPosition = new Vector3(XCoord, YCoord, ZCoord);
        Quaternion spawnRotation = Quaternion.Euler(0f, YRotation, 0f);

        if (type == 1)
        {
            // Crear instancia de pared
            Instantiate(wallPrefab, spawnPosition, spawnRotation);
        }
        else if (type == 2)
        {
            // Crear instancia de pared con marco para puerta
            Instantiate(wallDoorwayPrefab, spawnPosition, spawnRotation);

            if (YRotation == 0) {
                // Modificar posicion en x de la puerta para que quede en medio de la pared
                Vector3 doorSpawnPosition = new Vector3(XCoord + 1.3f, YCoord, ZCoord);
                // Crear instancia de puerta
                Instantiate(doorPrefab, doorSpawnPosition, spawnRotation);
            }
            else
            {
                Vector3 doorSpawnPosition = new Vector3(XCoord, YCoord, ZCoord - 1.3f);
                // Crear instancia de puerta
                Instantiate(doorPrefab, doorSpawnPosition, spawnRotation);
            }
        }
        else if (type == 3)
        {
            // Crear instancia de pared con marco para puerta
            Instantiate(wallDoorwayPrefab, spawnPosition, spawnRotation);
        }
    }

    private void PlaceWalls()
    {
        for (int i = 5;i >= 0;i--)
        {
            for (int j = 7;j >= 0;j--)
            {
                if (i == 5)
                {
                    if (j == 0)
                    {
                        Debug.Log(Walls[i,j,0]);
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 0, 0.5f, 3.2f, 0);
                        }
                        // Hay puerta
                        else if (CheckUp(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, 0, 0.5f, 3.2f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, -3, 0.5f, 0, 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckLeft(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, -3, 0.5f, 0, 90f);
                        }

                        // Checar pared de abajo
                        // Hay pared
                        if (CheckDown(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 0, 0.5f, -3, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckDown(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, 0, 0.5f, -3, 0);
                        }

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, -3, 0.5f, 0, 90f);
                        }
                    }
                    else if (j == 7)
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, j * 6.4f, 0.5f, 3.2f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) -3, 0.5f, 0, 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) -3, 0.5f, 0, 90f);
                        }

                        // Checar pared de abajo
                        // Hay pared
                        if (CheckDown(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, j * 6.4f, 0.5f, -3, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckDown(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, j * 6.4f, 0.5f, -3, 0);
                        }

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 47.71f, 0.5f, 0, 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckRight(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, 47.71f, 0.5f, 0, 90f);
                        }
                    }
                    else
                    {
                        Debug.Log(Walls[i,j,0]);
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, j * 6.4f, 0.5f, 3.2f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) -3, 0.5f, 0, 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) -3, 0.5f, 0, 90f);
                        }

                        // Checar pared de abajo
                        // Hay pared
                        if (CheckDown(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, j * 6.4f, 0.5f, -3, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckDown(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, j * 6.4f, 0.5f, -3, 0);
                        }
                    }
                }
                else if (i == 0)
                {
                    if (j == 0)
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 0, 0.5f, 35f, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckUp(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, 0, 0.5f, 35f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, -3, 0.5f, 32f, 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckLeft(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, -3, 0.5f, 32f, 90f);
                        }
                    }
                    else if (j == 7)
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 6.4f * j, 0.5f, 35f, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckUp(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, 6.4f * j, 0.5f, 35f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) - 3, 0.5f, 32f, 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) - 3, 0.5f, 32f, 90f);
                        }

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 47.71f, 0.5f, 32f, 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckRight(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, 47.71f, 0.5f, 32f, 90f);
                        }
                    }
                    else
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 6.4f * j, 0.5f, 35f, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckUp(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, 6.4f * j, 0.5f, 35f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) - 3, 0.5f, 32f, 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) - 3, 0.5f, 32f, 90f);
                        }
                    }
                }
                else
                {
                    if (j == 0)
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            Debug.Log("i: " + i);
                            InstantiateWall(1, 0, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }
                        // Hay puerta
                        else if (CheckUp(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, 0, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, -3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckLeft(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, -3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                    }
                    else if (j == 7)
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 6.4f * j, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckUp(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, 6.4f * j, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) - 3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) - 3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j,0]) == 1)
                        {
                            Debug.Log("RIGHT WALL i: " + i + " Z: " + 6.4f * (6 - i - 1));
                            InstantiateWall(1, 47.71f, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckRight(Walls[i,j,0]) == 3)
                        {
                            InstantiateWall(3, 47.71f, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                    }
                    else
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, 6.4f * j, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }
                        // Hay puerta
                        else if (CheckUp(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, 6.4f * j, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j,0]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) - 3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j,0]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) - 3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                    }
                }
            }
        }
    }
}
