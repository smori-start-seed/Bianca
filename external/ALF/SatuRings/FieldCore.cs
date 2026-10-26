using UnityEngine;

public class FieldCore : MonoBehaviour
{
    // --- Öffentliche Werte (UI steuert diese) ---
    [Range(0f, 1f)] public float growth = 0.5f;
    [Range(0f, 1f)] public float energy = 0.5f;
    [Range(0f, 1f)] public float drift = 0.5f;
    [Range(0f, 1f)] public float harmony = 0.5f;
    [Range(0f, 1f)] public float vortex = 0.5f;

    // --- Interne dynamische Werte ---
    public float growthSmooth;
    public float energySmooth;
    public float driftSmooth;
    public float harmonySmooth;
    public float vortexSmooth;

    // --- Glättungsfaktor ---
    public float smoothSpeed = 4f;

    // --- Material für Shader ---
    public Material fractalMaterial;

    void Update()
    {
        // Werte glätten (fühlt sich organisch an)
        growthSmooth = Mathf.Lerp(growthSmooth, growth, Time.deltaTime * smoothSpeed);
        energySmooth = Mathf.Lerp(energySmooth, energy, Time.deltaTime * smoothSpeed);
        driftSmooth = Mathf.Lerp(driftSmooth, drift, Time.deltaTime * smoothSpeed);
        harmonySmooth = Mathf.Lerp(harmonySmooth, harmony, Time.deltaTime * smoothSpeed);
        vortexSmooth = Mathf.Lerp(vortexSmooth, vortex, Time.deltaTime * smoothSpeed);

        // Werte an Shader senden
        if (fractalMaterial != null)
        {
            fractalMaterial.SetFloat("_Growth", growthSmooth);
            fractalMaterial.SetFloat("_Energy", energySmooth);
            fractalMaterial.SetFloat("_Drift", driftSmooth);
            fractalMaterial.SetFloat("_Harmony", harmonySmooth);
            fractalMaterial.SetFloat("_Vortex", vortexSmooth);
        }
    }
}

