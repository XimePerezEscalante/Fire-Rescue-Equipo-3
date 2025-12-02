using UnityEngine;

public class Door : MonoBehaviour
{
    public GameObject doorPrefab;
    private Animator animator;
    public bool isOpen;
    public int position;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        isOpen = false;
        // Obtener rotacion actual para asignar a position
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void SetPosition(int p)
    {
        position = p;
    }

    public void OpenDoor()
    {
        // Obtener componente Animator
        animator = GetComponent<Animator>();

        // Puerta en paredes frontales
        if (position == 0)
        {
            animator.SetTrigger("OpenFrontal");
            transform.rotation = Quaternion.Euler(0, 90, 0);
        }
        // Puerta en paredes laterales
        else if (position == 1)
        {
            animator.SetTrigger("OpenLateral");
            transform.rotation = Quaternion.Euler(0, 180, 0);
        }
        animator.SetTrigger("Stop");

        isOpen = true;
    }

    public void DestroyDoor()
    {
        // Play sound
        // Destroy object
    }
}
