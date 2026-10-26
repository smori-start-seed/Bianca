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
    "mass": 1000.0,
    "drift": 0.00005  # minimale Bewegung
}

# ----------------------------------------
# Davidstern-Paar (B & C)
# ----------------------------------------
RADIUS = 1.0

def make_pair(angle_deg):
    angle = math.radians(angle_deg)
    angle2 = angle + math.pi

    return {
        "B": {
            "angle": angle,
            "density": 1.0,
            "af": 0.4,
            "pf": 0.6,
            "rf": 0.5
        },
        "C": {
            "angle": angle2,
            "density": 0.7,
            "af": 0.6,
            "pf": 0.4,
            "rf": 0.5
        }
    }

pair = make_pair(0)

# ----------------------------------------
# Harmonie = Grundlage des Hexagons
# ----------------------------------------
def harmony(A, B, C):
    return 1.0 - (
        abs(A["af"] - B["af"]) +
        abs(B["af"] - C["af"]) +
        abs(C["af"] - A["af"])
    )

# ----------------------------------------
# Hexagon-Punkte berechnen
# ----------------------------------------
def hex_points(A, B, C):
    return [
        (A["af"], B["af"]),
        (B["af"], C["af"]),
        (C["af"], A["af"]),
        (A["pf"], C["pf"]),
        (C["pf"], B["pf"]),
        (B["pf"], A["pf"])
    ]

# ----------------------------------------
# Update-Regeln
# ----------------------------------------
def update(A, B, C):
    # B rotiert
    B["angle"] += 0.015
    B["x"] = RADIUS * math.cos(B["angle"])
    B["y"] = RADIUS * math.sin(B["angle"])

    # C folgt B (180° versetzt)
    C["angle"] = B["angle"] + math.pi
    C["x"] = RADIUS * math.cos(C["angle"])
    C["y"] = RADIUS * math.sin(C["angle"])

    # Frequenz-Drift durch Dichte
    B["af"] += (A["af"] - B["af"]) * 0.02 * B["density"]
    C["af"] += (B["af"] - C["af"]) * 0.02 * C["density"]

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

        update(A, B, C)
        h = harmony(A, B, C)
        hexagon = hex_points(A, B, C)

        print("SATURN-HEXAGON ECOSYSTEM")
        print("-------------------------")
        print(f"A (Zentrum):  AF {bar(A['af'])} {A['af']:.3f}")
        print(f"B (Orbit):    AF {bar(B['af'])} {B['af']:.3f}")
        print(f"C (Medium):   AF {bar(C['af'])} {C['af']:.3f}")
        print("-------------------------")
        print(f"HARMONIE: {h:.4f}")
        print("HEXAGON-PUNKTE:")
        for p in hexagon:
            print(f"  {p[0]:.3f} | {p[1]:.3f}")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nBeendet.")

