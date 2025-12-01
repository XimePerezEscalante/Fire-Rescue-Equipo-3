using UnityEngine;
using System;

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
                {"1100"},{"1000"},{"1001"},{"1100"},{"1001"},{"3100"},{"1000"}, {"1001"}
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
                {"0110"},{"0010"},{"0030"},{"0010"},{"0011"},{"0110"},{"0011"},{"0111"}
            }
        };
    
    private static int[,] Doors = new int[8,4]
    {
        {1, 3, 1, 4},
        {2, 5, 2, 6},
        {2, 8, 3, 8},
        {3, 2, 3, 3},
        {4, 4, 5, 4},
        {4, 6, 4, 7},
        {6, 5, 6, 6},
        {6, 7, 6, 8}
    };

    private static int[,] EntryPoints = new int[4,2]
    {
        {1, 6}, 
        {3, 1},
        {4, 8}, 
        {6, 3}
    };

    private static int[,] Fire = new int[10,2]
    {
        {2, 2}, 
        {2, 3},
        {3, 2}, 
        {3, 3},
        {3, 4}, 
        {3, 5},
        {4, 4}, 
        {5, 6},
        {5, 7},
        {6, 6}
    };

    
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        XWall = 0;
        YWall = 0.5f;
        ZWall = 0;
        AddDoorsToWallMatrix();
        PlaceWalls();
        InstantiateFire();
        //updateValues("1100", 1, '2');
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

    private void InstantiateFire()
    {
        float XCoord = 0f;
        float ZCoord = 0f;

        for (int i = 0;i < 10;i++)
        {
            XCoord = (Fire[i, 1] - 1) * 6.4f;
            ZCoord = (6 - Fire[i, 0]) * 6.4f;
            Vector3 spawnPosition = new Vector3(XCoord, 1.72f, ZCoord);
            Quaternion spawnRotation = Quaternion.identity;
            Instantiate(firePrefab, spawnPosition, spawnRotation);
        }
    }

    private string updateValues(string currentValue, int place, char newValue)
    {
        // constructing a string from a char array, prefix it with some additional characters
        char[] chars = {'a', 'b', 'c', 'd', '\0'};
        int length = 4;
        string result = string.Create(length, chars, (Span<char> strContent, char[] charArray) =>
        {
            for (int i = 0;i < length;i++)
            {
                if (i == place)
                {
                    strContent[i] = newValue;
                }
                else 
                {
                    strContent[i] = currentValue[i];
                }
            }
        });

        Debug.Log(result);
        return result;
    }

    private void AddDoorsToWallMatrix()
    {
        int currentI;
        int currentJ;
        string currentValue;

        for (int i = 0;i < 8;i++)
        {
            currentI = Doors[i,0];
            currentJ = Doors[i,1];

            // La puerta conduce a la misma fila
            if (Doors[i,2] == currentI)
            {
                // Hacia la celda de la derecha
                if (Doors[i,3] > currentJ)
                {
                    currentValue = Walls[currentI - 1, currentJ, 0];
                    //currentValue[1] = '2';
                    Walls[currentI - 1, currentJ, 0] = updateValues(currentValue, 1, '2');;
                }
                // Hacia la celda de la izquierda
                else if (Doors[i,3] > currentJ)
                {
                    currentValue = Walls[currentI - 1, currentJ - 2, 0];
                    //currentValue[1] = '2';
                    Walls[currentI - 1, currentJ - 2, 0] = updateValues(currentValue, 1, '2');;
                }
            }
            // La puerta conduce a la fila de arriba
            else if (Doors[i,2] < currentI)
            {
                currentValue = Walls[currentI - 1, currentJ - 1, 0];
                //currentValue[0] = '2';
                Walls[currentI - 1, currentJ - 1, 0] = updateValues(currentValue, 0, '2');;
            }
            // La puerta conduce a la fila de abajo
            else if (Doors[i,2] > currentI)
            {
                currentValue = Walls[currentI, currentJ - 1, 0];
                //currentValue[0] = '2';
                Debug.Log("CURRENT VALUE " + currentValue + "CURRENT I = " + currentI);
                Walls[currentI, currentJ - 1, 0] = updateValues(currentValue, 0, '2');;
            }
            
        }
    }

    private void AddEntryPointsToWallMatrix()
    {
        for (int i = 0;i < 4;i++)
        {
            // Si [i,0] es 1 o 6
            if (EntryPoints[i,1] > 1 && EntryPoints[i,1] < 8)
            {
                
            }
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

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j,0]) == 1)
                        {
                            //Debug.Log("RIGHT WALL i: " + i + " Z: " + 6.4f * (6 - i - 1));
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
