using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

public class BoardManager : MonoBehaviour
{
    AudioSystem audioSystem;
    [Header("-------------- Prefabs --------------")]
    public GameObject wallPrefab;
    public GameObject wallDoorwayPrefab;
    public GameObject doorPrefab;
    public GameObject unknownPOIPrefab;
    public GameObject[] knownPOIPrefabs;
    public GameObject firePrefab;
    public GameObject smokePrefab;
    [Header("---------- Object Instances ----------")]
    public GameObject[] agents;
    public GameObject[] activeFires;
    public GameObject[] doors;
    public List<GameObject> unknownPOIInstances;
    public List<GameObject> knownPOIInstances;
    public List<GameObject> activeWalls;
    public static float XWall{get; private set;}
    public static float YWall{get; private set;}
    public static float ZWall{get; private set;}
    public string[,] Walls;//[,] Walls = new string[6,8];
    /*{
        {
            "1100",
            "1000",
            "1001",
            "1100",
            "1001",
            "1100",
            "1000",
            "1001"
        },
        {
            "0100",
            "0000",
            "0011",
            "0110",
            "0011",
            "0110",
            "0010",
            "0011"
        },
        {
            "0100",
            "0001",
            "1100",
            "1000",
            "1000",
            "1001",
            "1100",
            "1001"
        },
        {
            "0110",
            "0011",
            "0110",
            "0010",
            "0010",
            "0011",
            "0110",
            "0011"
        },
        {
            "1100",
            "1000",
            "1000",
            "1000",
            "1001",
            "1100",
            "1001",
            "1101"
        },
        {
            "0110",
            "0010",
            "0010",
            "0010",
            "0011",
            "0110",
            "0011",
            "0111"
        }
    };*/
    
    public int[,] Doors;/* = new int[8,4]
    {
        {1, 3, 1, 4},
        {2, 5, 2, 6},
        {2, 8, 3, 8},
        {3, 2, 3, 3},
        {4, 4, 5, 4},
        {4, 6, 4, 7},
        {6, 5, 6, 6},
        {6, 7, 6, 8}
    };*/

    public int[,] EntryPoints; /* = new int[4,2]
    {
        {1, 6}, 
        {3, 1},
        {4, 8}, 
        {6, 3}
    };*/

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

    private static int[,] POI = new int[3,3]
    {
        {2, 4, 1},
        {5, 1, 0},
        {5, 8, 1}
    };

    private void Awake()
    {
        audioSystem = GameObject.FindGameObjectWithTag("Audio").GetComponent<AudioSystem>();
    }
    
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        XWall = 0;
        YWall = 0.5f;
        ZWall = 0;
        //AddEntryPointsToWallMatrix();
        //AddDoorsToWallMatrix();
        //PlaceWalls();
        /*InstantiateFire();
        OpenDoor("p3");
        OpenDoor("p4");
        OpenDoor("p5");
        */
        InstantiateUnknownPOI();
        //TurnPOIAround(2, 4);
        //MoveAgent(1, 6, 1);
        // Explosion(1, 1);
        //UpdateValues("1100", 1, '2');
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

    public void DeleteNullObjects(int listNumber)
    {
        if (listNumber == 0)
        {
            for (int i = unknownPOIInstances.Count - 1;i >= 0;i--)
            {
                unknownPOIInstances.RemoveAt(i);
            }
        }
        else if (listNumber == 1)
        {
            for (int i = knownPOIInstances.Count - 1;i >= 0;i--)
            {
                knownPOIInstances.RemoveAt(i);
            }
        }
    }
    public void NewFire(bool isMapInitialized, int type, int x, int y)
    {
        if (isMapInitialized)
        {
            InstantiateOneFire(type, x, y);
        }
        else
        {
            InstantiateFire();
        }
    }

    public GameObject NewPOI(bool revealed, string type, int r, int c)
    {
        if (revealed && type == "v")
        {
            float XCoord = CorrectXCoordinates(c);
            float ZCoord = CorrectZCoordinates(r);
            return InstantiateKnownPOI(XCoord, ZCoord);
        }
        else
        {
            return InstantiateOneUnknownPOI(type, r, c);
        }
            
            /*if (revealed)
            {
                Debug.Log("POI REVEALED\n ROW: " + r + " COL: " + c);

                TurnPOIAround(r, c);
            }*/
    }

    private void InstantiateOneFire(int type, int r, int c)
    {
        float XCoord = 0f;
        float ZCoord = 0f;

        int currentIndex = 0;

        foreach (GameObject fire in activeFires)
        {
            if (fire != null)
            {
                currentIndex += 1;
            }
        }

        XCoord = CorrectXCoordinates(c);
        ZCoord = CorrectZCoordinates(r);
        // Crear valores para instanciar el objeto
        Vector3 spawnPosition = new Vector3(XCoord, 1.72f, ZCoord);
        Quaternion spawnRotation = Quaternion.identity;

        if (type == 1)
        {
            activeFires[currentIndex] = Instantiate(smokePrefab, spawnPosition, spawnRotation);
        }
        else if (type == 2) {
            activeFires[currentIndex] = Instantiate(firePrefab, spawnPosition, spawnRotation);
        }
        
    }

    private GameObject InstantiateOneUnknownPOI(string type, int r, int c)
    {
        float XCoord = 0f;
        float ZCoord = 0f;

        int currentIndex = 0;

        foreach (GameObject oneUnknownPOI in unknownPOIInstances)
        {
            if (oneUnknownPOI != null)
            {
                currentIndex += 1;
            }
        }

        XCoord = CorrectXCoordinates(c);
        ZCoord = CorrectZCoordinates(r);

        // Crear valores para instanciar el objeto
        Vector3 spawnPosition = new Vector3(XCoord, 0.5f, ZCoord);
        Quaternion spawnRotation = Quaternion.identity;
        // Crear instancia de objeto
        GameObject newPOI = Instantiate(unknownPOIPrefab, spawnPosition, spawnRotation);
        // Establecer celda donde se encuentra
        newPOI.GetComponent<UnknownPOI>().SetLocation(r, c); 
        // Es falsa alarma
        if (type == "f")
        {
            newPOI.GetComponent<UnknownPOI>().SetFalseAlarm(true);
        }
        // Es comida
        else if (type == "v")
        {
            newPOI.GetComponent<UnknownPOI>().SetFalseAlarm(false);
        }
        // Agregar objeto a la lista unknownPOI
        unknownPOIInstances.Add(newPOI);

        return newPOI;
    }

    private void InstantiateWall(int type, float XCoord, float YCoord, float ZCoord, float YRotation)
    {
        Vector3 spawnPosition = new Vector3(XCoord, YCoord, ZCoord);
        Quaternion spawnRotation = Quaternion.Euler(0f, YRotation, 0f);

        if (type == 1)
        {
            // Crear instancia de pared
            activeWalls.Add(Instantiate(wallPrefab, spawnPosition, spawnRotation));
        }
        else if (type == 2)
        {
            // Crear instancia de pared con marco para puerta
            activeWalls.Add(Instantiate(wallDoorwayPrefab, spawnPosition, spawnRotation));

            // Checar si aún hay espacio para más puertas
            bool isFull = true;
            foreach (var d in doors)
            {
                if (d == null)   // hay espacio disponible
                {
                    isFull = false;
                    break;
                }
            }

            if (isFull == false) {
                // Obtener indice en el que se agregara la puerta
                int currentIndex = 0;

                foreach (GameObject door in doors)
                {
                    if (door != null)
                    {
                        currentIndex += 1;
                    }
                }

                // Crear nombre de la puerta para ajustarse al JSON
                string doorName = "p" + (currentIndex + 1);

                if (YRotation == 0) {
                    // Modificar posicion en x de la puerta para que quede en medio de la pared
                    Vector3 doorSpawnPosition = new Vector3(XCoord + 1.3f, YCoord, ZCoord);
                    // Crear instancia de puerta
                    doors[currentIndex] = Instantiate(doorPrefab, doorSpawnPosition, spawnRotation);
                    // Asignar posicion 0 -> "frontal"
                    doors[currentIndex].GetComponent<Door>().position = 0;
                }
                else
                {
                    Vector3 doorSpawnPosition = new Vector3(XCoord, YCoord, ZCoord - 1.3f);
                    // Crear instancia de puerta
                    doors[currentIndex] = Instantiate(doorPrefab, doorSpawnPosition, spawnRotation);
                    // Asignar posicion 1 -> "lateral"
                    doors[currentIndex].GetComponent<Door>().position = 1;
                }

                doors[currentIndex].GetComponent<Door>().name = doorName;
            }
            
        }
        else if (type == 3)
        {
            // Crear instancia de pared con marco para puerta
            activeWalls.Add(Instantiate(wallDoorwayPrefab, spawnPosition, spawnRotation));
        }
    }

    private void InstantiateFire()
    {
        float XCoord = 0f;
        float ZCoord = 0f;

        for (int i = 0;i < (Fire.Length / 2);i++)
        {
            // Restar 1 al valor para ajustarse a las coordenadas correctas
            XCoord = (Fire[i, 1] - 1) * 6.4f;
            // Restarle a 6 el valor para ajustarse a las coordenadas del tablero
            ZCoord = (6 - Fire[i, 0]) * 6.4f;
            // Crear valores para instanciar el objeto
            Vector3 spawnPosition = new Vector3(XCoord, 1.72f, ZCoord);
            Quaternion spawnRotation = Quaternion.identity;
            activeFires[i] = Instantiate(firePrefab, spawnPosition, spawnRotation);
        }
    }

    private void InstantiateUnknownPOI()
    {
        float XCoord = 0f;
        float ZCoord = 0f;

        
        for (int i = 0;i < (POI.Length / 3);i++)
        {
            // Obtener cooredenadas correctas
            XCoord = CorrectXCoordinates(POI[i, 1]);
            ZCoord = CorrectZCoordinates(POI[i, 0]);

            // Crear valores para instanciar el objeto
            Vector3 spawnPosition = new Vector3(XCoord, 0.5f, ZCoord);
            Quaternion spawnRotation = Quaternion.identity;
            // Crear instancia de objeto
            GameObject newPOI = Instantiate(unknownPOIPrefab, spawnPosition, spawnRotation);
            // Establecer celda donde se encuentra
            newPOI.GetComponent<UnknownPOI>().SetLocation(POI[i, 0], POI[i, 1]); 
            // Es falsa alarma
            if (POI[i,2] == 0)
            {
                newPOI.GetComponent<UnknownPOI>().SetFalseAlarm(true);
            }
            // Es comida
            else if (POI[i,2] == 1)
            {
                newPOI.GetComponent<UnknownPOI>().SetFalseAlarm(false);
            }
            // Agregar objeto al arreglo unknownPOI
            unknownPOIInstances.Add(newPOI);
        }

    }

    private GameObject InstantiateKnownPOI(float XCoord, float ZCoord)
    {
        // Generar indice random para escoger del arreglo de knownPOIPrefabs
        int indexPOI = UnityEngine.Random.Range(1, 9);
        // Obtener indice donde se agregara
        int currentIndex = 0;

        foreach (GameObject oneKnownPOI in knownPOIInstances)
        {
            if (oneKnownPOI != null)
            {
                currentIndex += 1;
            }
        }

        // Crear instancia del objeto
        Vector3 spawnPosition = new Vector3(XCoord, 0.5f, ZCoord);
        Quaternion spawnRotation = Quaternion.identity;
        GameObject newPOI = Instantiate(knownPOIPrefabs[0], spawnPosition, spawnRotation);
        // Agregar objeto al arreglo knownPOI
        knownPOIInstances.Add(newPOI);
        return newPOI;
    }

    public void MoveAgent(int agentIndex, int r, int c, Vector3 rotation)
    {
        float XCoord = CorrectXCoordinates(c);
        float ZCoord = CorrectZCoordinates(r);
        // Crear vector de posicion de objeto
        Vector3 newPosition = new Vector3(XCoord, 3.29f, ZCoord);
        // Crear vector de rotacion de objeto
        // Quaternion spawnRotation = Quaternion.identity;
        // Mover agente
        agents[agentIndex].GetComponent<Agent>().Move(r, c, newPosition, rotation);

    }

    public void MovePOI(int r, int c, bool isBeingCarried)
    {
        GameObject[] allPOIS;
        allPOIS = GameObject.FindGameObjectsWithTag("KnownPOI");

        // Establecer coordenadas
        float XCoord = CorrectXCoordinates(c);
        float ZCoord = CorrectZCoordinates(r);
        float YCoord;

        // Crear vector de posicion de objeto
        if (isBeingCarried == true)
        {
            YCoord = 3.29f;
        }
        else
        {
            YCoord = 0.5f;
        }

        Vector3 newPosition = new Vector3(XCoord, YCoord, ZCoord);

        // Encontrar POI
        foreach (GameObject onePOI in allPOIS)
        {
            if (onePOI.GetComponent<KnownPOI>().row == r && onePOI.GetComponent<KnownPOI>().column == c)
            {
                onePOI.GetComponent<KnownPOI>().Move(r, c, newPosition);
            }
        }
    }

    public void TurnPOIAround(int r, int c)
    {
        GameObject[] allPOIS;
        allPOIS = GameObject.FindGameObjectsWithTag("UnknownPOI");

        bool createPOI;

        int cont = 0;
        
        foreach (GameObject onePOI in allPOIS) {
            Debug.Log("POI " + cont);
            Debug.Log("Inside Turn POI - ROW: " + onePOI.GetComponent<UnknownPOI>().row);
            Debug.Log("Inside Turn POI - COL:" + onePOI.GetComponent<UnknownPOI>().column);
            // Se encontro el POI
            if (onePOI.GetComponent<UnknownPOI>().row == r && onePOI.GetComponent<UnknownPOI>().column == c){
                // Checar si es falsa alarma
                createPOI = onePOI.GetComponent<UnknownPOI>().isFalseAlarm;
                // Funcion de descubrir POI
                onePOI.GetComponent<UnknownPOI>().DiscoverPOI();
                // Si el POI no es falsa alarma, se crea uno con un prefab de KnownPOIs
                if (!createPOI)
                {
                    // Coordenada en X actual
                    float XCoord = CorrectXCoordinates(c);
                    // Coordenada en Z actual
                    float ZCoord = CorrectZCoordinates(r);
                    // Crear instancia de POI descubierto
                    InstantiateKnownPOI(XCoord, ZCoord);
                }
            }
            cont += 1;
        }
    }

    public void OpenDoor(string doorName)
    {
        foreach (GameObject door in doors)
        {
            if (door.GetComponent<Door>().name == doorName)
            {
                door.GetComponent<Door>().OpenDoor();
            }
        }
    }

    private void Explosion(int row, int col)
    {
        audioSystem.PlaySFX(audioSystem.explosion);
    }

    private string UpdateValues(string currentValue, int place, char newValue)
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

        //Debug.Log(result);
        return result;
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

    public void AddDoorsToWallMatrix()
    {
        for (int i = 0; i < Doors.GetLength(0); i++)
        {
            string row = "";
            for (int j = 0; j < Doors.GetLength(1); j++)
            {
                row += Doors[i, j] + " ";
            }
            Debug.Log("Door " + i + ": " + row);
        }

        int currentI;
        int currentJ;
        string currentValue;

        for (int i = 0;i < Doors.GetLength(0);i++)
        {
            currentI = Doors[i,0];
            currentJ = Doors[i,1];

            if (currentI <= 0 || currentJ <= 0)
            {
                currentI += 1;
                currentJ += 1;
            }

            // La puerta conduce a la misma fila
            if (Doors[i,2] == currentI)
            {
                // Hacia la celda de la derecha
                if (Doors[i,3] > currentJ)
                {
                    currentValue = Walls[currentI - 1, currentJ];
                    //currentValue[1] = '2';
                    Walls[currentI - 1, currentJ] = UpdateValues(currentValue, 1, '2');;
                }
                // Hacia la celda de la izquierda
                else if (Doors[i,3] > currentJ)
                {
                    currentValue = Walls[currentI - 1, currentJ - 2];
                    //currentValue[1] = '2';
                    Walls[currentI - 1, currentJ - 2] = UpdateValues(currentValue, 1, '2');;
                }
            }
            // La puerta conduce a la fila de arriba
            else if (Doors[i,2] < currentI)
            {
                currentValue = Walls[currentI - 1, currentJ - 1];
                //currentValue[0] = '2';
                Walls[currentI - 1, currentJ - 1] = UpdateValues(currentValue, 0, '2');;
            }
            // La puerta conduce a la fila de abajo
            else if (Doors[i,2] > currentI)
            {
                currentValue = Walls[currentI, currentJ - 1];
                //currentValue[0] = '2';
                //Debug.Log("CURRENT VALUE " + currentValue + "CURRENT I = " + currentI);
                Walls[currentI, currentJ - 1] = UpdateValues(currentValue, 0, '2');;
            }
            
        }
    }

    public void AddEntryPointsToWallMatrix()
    {
        string currentValue;

        for (int i = 0;i < 4;i++)
        {
            // Celda a modificar
            currentValue = Walls[EntryPoints[i,0] - 1, EntryPoints[i,1] - 1];

            // Columna 1
            if (EntryPoints[i,1] == 1)
            {
                // Entry Point va en la pared izquierda
                Walls[EntryPoints[i,0] - 1, EntryPoints[i,1] - 1] = UpdateValues(currentValue, 1, '3');
            }
            // Columna 8
            else if (EntryPoints[i,1] == 8)
            {
                // Entry Point va en la pared derecha
                Walls[EntryPoints[i,0] - 1, EntryPoints[i,1] - 1] = UpdateValues(currentValue, 3, '3');
            }
            else
            {
                // Fila 1
                if (EntryPoints[i,0] == 1)
                {
                    // Entry Point va en la pared de arriba
                    Walls[EntryPoints[i,0] - 1, EntryPoints[i,1] - 1] = UpdateValues(currentValue, 0, '3');
                }
                // Fila 6
                else if (EntryPoints[i,0] == 6)
                {
                    // Entry Point va en la pared de abajo
                    Walls[EntryPoints[i,0] - 1, EntryPoints[i,1] - 1] = UpdateValues(currentValue, 2, '3');
                }
            }
        }
    }

    public void PlaceWalls()
    {
        for (int i = 5;i >= 0;i--)
        {
            for (int j = 7;j >= 0;j--)
            {
                if (i == 5)
                {
                    if (j == 0)
                    {
                        //Debug.Log(Walls[i,j,0]);
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 0, 0.5f, 3.2f, 0);
                        }
                        // Hay puerta
                        else if (CheckUp(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, 0, 0.5f, 3.2f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, -3, 0.5f, 0, 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckLeft(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, -3, 0.5f, 0, 90f);
                        }

                        // Checar pared de abajo
                        // Hay pared
                        if (CheckDown(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 0, 0.5f, -3, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckDown(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, 0, 0.5f, -3, 0);
                        }

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, -3, 0.5f, 0, 90f);
                        }
                    }
                    else if (j == 7)
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, j * 6.4f, 0.5f, 3.2f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) -3, 0.5f, 0, 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) -3, 0.5f, 0, 90f);
                        }

                        // Checar pared de abajo
                        // Hay pared
                        if (CheckDown(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, j * 6.4f, 0.5f, -3, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckDown(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, j * 6.4f, 0.5f, -3, 0);
                        }

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 47.71f, 0.5f, 0, 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckRight(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, 47.71f, 0.5f, 0, 90f);
                        }
                    }
                    else
                    {
                        //Debug.Log(Walls[i,j,0]);
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, j * 6.4f, 0.5f, 3.2f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) -3, 0.5f, 0, 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) -3, 0.5f, 0, 90f);
                        }

                        // Checar pared de abajo
                        // Hay pared
                        if (CheckDown(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, j * 6.4f, 0.5f, -3, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckDown(Walls[i,j]) == 3)
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
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 0, 0.5f, 35f, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckUp(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, 0, 0.5f, 35f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, -3, 0.5f, 32f, 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckLeft(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, -3, 0.5f, 32f, 90f);
                        }
                    }
                    else if (j == 7)
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 6.4f * j, 0.5f, 35f, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckUp(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, 6.4f * j, 0.5f, 35f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) - 3, 0.5f, 32f, 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) - 3, 0.5f, 32f, 90f);
                        }

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 47.71f, 0.5f, 32f, 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckRight(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, 47.71f, 0.5f, 32f, 90f);
                        }
                    }
                    else
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 6.4f * j, 0.5f, 35f, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckUp(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, 6.4f * j, 0.5f, 35f, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) - 3, 0.5f, 32f, 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j]) == 2)
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
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            //Debug.Log("i: " + i);
                            InstantiateWall(1, 0, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }
                        // Hay puerta
                        else if (CheckUp(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, 0, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, -3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckLeft(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, -3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                    }
                    else if (j == 7)
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 6.4f * j, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }
                        // Hay punto de entrada
                        else if (CheckUp(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, 6.4f * j, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) - 3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) - 3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }

                        // Checar pared de la derecha
                        // Hay pared
                        if (CheckRight(Walls[i,j]) == 1)
                        {
                            //Debug.Log("RIGHT WALL i: " + i + " Z: " + 6.4f * (6 - i - 1));
                            InstantiateWall(1, 47.71f, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                        // Hay punto de entrada
                        else if (CheckRight(Walls[i,j]) == 3)
                        {
                            InstantiateWall(3, 47.71f, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                    }
                    else
                    {
                        // Checar pared de arriba
                        // Hay pared
                        if (CheckUp(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, 6.4f * j, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }
                        // Hay puerta
                        else if (CheckUp(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, 6.4f * j, 0.5f, 6.4f * (6 - i) - 3, 0);
                        }

                        // Checar pared de la izquierda
                        // Hay pared
                        if (CheckLeft(Walls[i,j]) == 1)
                        {
                            InstantiateWall(1, (6.4f * j) - 3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                        // Hay puerta
                        else if (CheckLeft(Walls[i,j]) == 2)
                        {
                            InstantiateWall(2, (6.4f * j) - 3, 0.5f, 6.4f * (6 - i - 1), 90f);
                        }
                    }
                }
            }
        }
    }
}
