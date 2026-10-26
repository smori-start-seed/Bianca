# EML/eml.py

def read_world(engine):
    """Zustand aus Colorverse (saturings.py) extrahieren."""
    sphere = engine.spheren[0] if engine.spheren else None
    uni = engine.universe if hasattr(engine, "universe") else None

    return {
        "sphere": {
            "hue": sphere.hue_avg if sphere else None,
            "sat": sphere.sat_avg if sphere else None,
            "bri": sphere.bri_avg if sphere else None,
            "energy": sphere.energy_avg if sphere else None,
            "harmonie": sphere.harmonie_avg if sphere else None,
            "drift": sphere.drift_avg if sphere else None,
        },
        "universe": {
            "harmonie": uni.harmonie if uni else None,
            "drift": uni.drift if uni else None,
            "energy": uni.energy if uni else None,
        }
    }


def interpret(world_state):
    """Weltzustand → Bedeutung für Urasil."""
    s = world_state["sphere"]
    u = world_state["universe"]

    meaning = {}

    if s["harmonie"] is not None:
        meaning["stabil"] = s["harmonie"] > 0.6
        meaning["fragil"] = 0.3 < s["harmonie"] <= 0.6
        meaning["chaos"] = s["harmonie"] <= 0.3

    if s["drift"] is not None:
        meaning["drift_hoch"] = s["drift"] > 0.4

    if s["energy"] is not None:
        meaning["energie_low"] = s["energy"] < 0.3

    if u["harmonie"] is not None:
        meaning["universe_shift"] = abs(u["harmonie"] - 0.5)

    return meaning


def apply(engine, decision):
    """Urasil-Entscheidung → Modulation der Welt."""
    hf = engine.harmonie_feld

    if decision.get("increase_harmony"):
        hf["global_harmonie"] += 0.01

    if decision.get("decrease_harmony"):
        hf["global_harmonie"] -= 0.01

    if decision.get("increase_drift"):
        hf["global_drift"] += 0.01

    if decision.get("inject_noise"):
        hf["stoerimpulse"] += 0.02

