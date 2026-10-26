# EML/meaning.py
#
# Übersetzt den Weltzustand in ein Bedeutungsobjekt,
# das Urasil_light verstehen und verarbeiten kann.

def interpret(world_state: dict) -> dict:
    s = world_state.get("sphere", {})
    m = world_state.get("meta", {})
    u = world_state.get("universe", {})

    meaning = {}

    # Sphere-Harmonie
    h_s = s.get("harmonie")
    if h_s is not None:
        meaning["sphere_stabil"] = h_s > 0.6
        meaning["sphere_fragil"] = 0.3 < h_s <= 0.6
        meaning["sphere_chaos"] = h_s <= 0.3

    # Sphere-Drift
    d_s = s.get("drift")
    if d_s is not None:
        meaning["sphere_drift_hoch"] = d_s > 0.4

    # Meta-Harmonie
    h_m = m.get("harmonie")
    if h_m is not None:
        meaning["meta_stabil"] = h_m > 0.6
        meaning["meta_chaos"] = h_m <= 0.3

    # Energie
    e_s = s.get("energy")
    if e_s is not None:
        meaning["energie_low"] = e_s < 0.3
        meaning["energie_rich"] = e_s > 0.7

    # Universe-Shift
    h_u = u.get("harmonie")
    if h_u is not None:
        meaning["universe_shift"] = abs(h_u - 0.5)

    return meaning

