using UnityEngine;
//using System.Random;

public class UnknownPOI : MonoBehaviour
{
    AudioSystem audioSystem;
    public GameObject UnknownPOIPrefab;
    private Animator animator;
    public int id;
    public int row;
    public int column;
    public bool isFalseAlarm;

    private void Awake()
    {
        audioSystem = GameObject.FindGameObjectWithTag("Audio").GetComponent<AudioSystem>();
    }

    public void SetFalseAlarm(bool isFake)
    {
        isFalseAlarm = isFake;
    }

    public void SetLocation(int r, int c)
    {
        row = r;
        column = c;
    }

    public void DiscoverPOI()
    {
        // Obtener componente Animator
        animator = GetComponent<Animator>();
        // Habilitar animacion cuando es descubierto
        animator.SetTrigger("TurnAround");
        Debug.Log("DiscoverPOI");

        if (isFalseAlarm)
        {
            audioSystem.PlaySFX(audioSystem.falseAlarmPOI);
        }
        
        // Destruir POI
        Destroy(gameObject);
    }

}
