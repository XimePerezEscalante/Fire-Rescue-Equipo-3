using UnityEngine;

public class Agent : MonoBehaviour
{
    AudioSystem audioSystem;
    public GameObject AgentPrefab;
    public int row;
    public int column;
    public bool isCarryingPOI;

    private void Awake()
    {
        audioSystem = GameObject.FindGameObjectWithTag("Audio").GetComponent<AudioSystem>();
    }

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
    }

    public void Move(int r, int c, Vector3 newPosition, Quaternion newRotation)
    {
        // Actualizar ubicacion
        row = r;
        column = c;

        // Tiempo para hacer el lerp
        float timeElapsed = 0;
        float timeToMove = 3;

        // Mover agente con la funcion lerp
        while(timeElapsed < timeToMove){
            transform.position = Vector3.Lerp(transform.position, newPosition, timeElapsed/timeToMove);
            timeElapsed += Time.deltaTime;
        }
    }

    public void GetStunned()
    {
        audioSystem.PlaySFX(audioSystem.stunned);
    }

    public void ExtinguishFire()
    {
        audioSystem.PlaySFX(audioSystem.extinguish);
    }
}
