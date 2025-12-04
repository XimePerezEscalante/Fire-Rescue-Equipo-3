using UnityEngine;

public class CameraController : MonoBehaviour
{
    public Transform cameraTransform;      // La cámara a mover
    public Transform targetTransform;      // Posición y rotación final
    public float duration = 20f;           // 20 segundos

    private void Start()
    {
        StartCoroutine(MoveCamera());
    }

    private System.Collections.IEnumerator MoveCamera()
    {
        Vector3 startPos = cameraTransform.position;
        Quaternion startRot = cameraTransform.rotation;

        Vector3 endPos = targetTransform.position;
        Quaternion endRot = targetTransform.rotation;

        float elapsed = 0f;

        while (elapsed < duration)
        {
            float t = elapsed / duration;

            cameraTransform.position = Vector3.Lerp(startPos, endPos, t);
            cameraTransform.rotation = Quaternion.Slerp(startRot, endRot, t);

            elapsed += Time.deltaTime;
            yield return null;
        }

        // Asegurar llegar exactamente al final
        cameraTransform.position = endPos;
        cameraTransform.rotation = endRot;
    }
}
