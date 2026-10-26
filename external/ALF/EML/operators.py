# EML/operators.py
#
# Wendet Urasils Entscheidungen auf die Welt an,
# indem das Harmonie-Feld und verwandte Parameter moduliert werden.

def apply(engine, decision: dict):
    hf = engine.harmonie_feld

    # Harmonie
    if decision.get("increase_harmony"):
        hf["global_harmonie"] += 0.01
    if decision.get("decrease_harmony"):
        hf["global_harmonie"] -= 0.01

    # Drift
    if decision.get("increase_drift"):
        hf["global_drift"] += 0.01
    if decision.get("decrease_drift"):
        hf["global_drift"] -= 0.01

    # Störimpulse
    if decision.get("inject_noise"):
        hf["stoerimpulse"] += 0.02
    if decision.get("calm_noise"):
        hf["stoerimpulse"] -= 0.01

