using UnityEngine;

public class KnownPOI : MonoBehaviour
{
    AudioSystem audioSystem;
    public GameObject UnknownPOIPrefab;
    private Animator animator;
    public int id;
    public int row;
    public int column;
    public bool isAlive;
    public bool isInside;

    private void Awake()
    {
        audioSystem = GameObject.FindGameObjectWithTag("Audio").GetComponent<AudioSystem>();
    }

    public void SetIsAlive(bool alive)
    {
        isAlive = alive;
    }

    public void SetIsInside(bool inside)
    {
        isInside = inside;
    }

    public void SetLocation(int r, int c)
    {
        row = r;
        column = c;
    }

    private void Death()
    {
        
    }

    public void Move(int r, int c, Vector3 newPosition)
    {
        // Actualizar ubicacion
        row = r;
        column = c;

        // Tiempo para hacer el lerp
        float timer = 0;
        float timePerStep = 0.5f;
        float t = timer / timePerStep;

        // Mover POI con la funcion lerp
        while(timer < timePerStep){
            timer += Time.deltaTime;
            t = timer / timePerStep;
            // Cambiar ubicacion
            transform.position = Vector3.Lerp(transform.position, newPosition, t);
        }
    }

}
