using UnityEngine;

public class AudioSystem : MonoBehaviour
{
    [Header("-------------- Audio Source --------------")]
    [SerializeField] AudioSource musicSource;
    [SerializeField] AudioSource SFXSource;

[Header("---------------- Audio Clip ----------------")]
    public AudioClip backgroundMusic;
    public AudioClip explosion;
    public AudioClip extinguish;
    public AudioClip death;
    public AudioClip breakWall;
    public AudioClip stunned;
    public AudioClip falseAlarmPOI;

    private void Start()
    {
        musicSource.clip = backgroundMusic;
        musicSource.Play();
    }

    public void PlaySFX(AudioClip clip)
    {
        SFXSource.PlayOneShot(clip);
    }

}
