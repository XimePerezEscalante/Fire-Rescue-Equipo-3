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

    //private static Random random = new Random();

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        // Escoger numero random para el indice de KnownPOIs
        //int randomNumberInRange = random.Next(9);
    }

    // Update is called once per frame
    void Update()
    {
        
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

    private void IsCarried()
    {
        
    }

}
