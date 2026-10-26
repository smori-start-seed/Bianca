import math
import random
import time
import os

# ----------------------------------------
# Agent A = Schwarzes Loch (Zentrum)
# ----------------------------------------
A = {
    "x": 0.0,
    "y": 0.0,
    "af": 0.5,
    "pf": 0.5,
    "rf": 0.5,
    "mass": 1000.0,   # extrem hoch
    "drift": 0.0001   # minimale Bewegung
}

# ----------------------------------------
# Agenten B & C = Davidstern-Paar
# ----------------------------------------
RADIUS = 1.0  # Orbit-Radius

def make_davidstar_pair(angle_deg):
    angle = math.radians(angle_deg)
    angle2 = angle + math.pi  # 180° versetzt

    return {
        "B": {
            "angle": angle,
            "x": RADIUS * math.cos(angle),
            "y": RADIUS * math.sin(angle),
            "density": 1.0,
            "af": 0.4,
            "pf": 0.6,
            "rf": 0.5
        },
        "C": {
            "angle": angle2,
            "x": RADIUS * math.cos(angle2),
            "y": RADIUS * math.sin(angle2),
            "density": 0.7,
            "af": 0.6,
            "pf": 0.4,
            "rf": 0.5
        }
    }

# Erstes Davidstern-Paar
pair = make_davidstar_pair(0)

# ----------------------------------------
# Harmonie-Berechnung
# ----------------------------------------
def harmony(A, B, C):
    return 1.0 - (
        abs(A["af"] - B["af"]) +
        abs(B["af"] - C["af"]) +
        abs(C["af"] - A["af"])
    )

# ----------------------------------------
# Update-Regeln
# ----------------------------------------
def update_pair(A, B, C):
    # B folgt A (Orbit)
    B["angle"] += 0.01
    B["x"] = RADIUS * math.cos(B["angle"])
    B["y"] = RADIUS * math.sin(B["angle"])

    # C folgt B (Medium)
    C["angle"] = B["angle"] + math.pi
    C["x"] = RADIUS * math.cos(C["angle"])
    C["y"] = RADIUS * math.sin(C["angle"])

    # Frequenz-Drift durch Dichte
    B["af"] += (A["af"] - B["af"]) * 0.01 * B["density"]
    C["af"] += (B["af"] - C["af"]) * 0.01 * C["density"]

    # Rückkopplung auf A
    A["af"] += (C["af"] - A["af"]) * A["drift"]

# ----------------------------------------
# Visualisierung
# ----------------------------------------
def bar(v):
    filled = int(v * 20)
    return "█" * filled + "░" * (20 - filled)

# ----------------------------------------
# Main Loop
# ----------------------------------------
try:
    while True:
        os.system("clear")

        B = pair["B"]
        C = pair["C"]

        update_pair(A, B, C)
        h = harmony(A, B, C)

        print("ECOSYSTEM – DAVIDSTERN – 3 AGENTEN")
        print("----------------------------------")
        print(f"A (Zentrum):  AF {bar(A['af'])} {A['af']:.3f}")
        print(f"B (Orbit):    AF {bar(B['af'])} {B['af']:.3f}")
        print(f"C (Medium):   AF {bar(C['af'])} {C['af']:.3f}")
        print("----------------------------------")
        print(f"HARMONIE: {h:.4f}")
        print(f"POSITIONEN:")
        print(f"B: ({B['x']:.3f}, {B['y']:.3f})")
        print(f"C: ({C['x']:.3f}, {C['y']:.3f})")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nBeendet.")

