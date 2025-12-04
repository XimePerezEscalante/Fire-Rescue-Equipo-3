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

    public void Move(int r, int c, Vector3 newPosition, Vector3 newRotation)
    {
        // Actualizar ubicacion
        row = r;
        column = c;

        // Tiempo para hacer el lerp
        float timer = 0;
        float timeElapsed = 0;
        float timeToMove = 3;
        float timePerStep = 0.5f;
        float t = timer / timePerStep;

        // Mover agente con la funcion lerp
        while(timer < timePerStep){
            timer += Time.deltaTime;
            t = timer / timePerStep;
            // Cambiar ubicacion
            transform.position = Vector3.Lerp(transform.position, newPosition, t);
            // Cambiar rotacion
            /*if (newRotation != Vector3.zero)
            {
                    transform.rotation = Quaternion.Slerp(
                        transform.rotation, 
                        Quaternion.LookRotation(newRotation), 
                        t * 5 // Velocidad de giro
                    );
            }*/
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
