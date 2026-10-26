import math
import time
import os

MEMORY = {
    "rings": [],       # Wings
    "pairs": [],       # Rooms
    "snapshots": [],   # Closets
    "links": []        # Tunnels
}

# ----------------------------------------
# Meta-Feld M (emergentes Bewusstseinsfeld)
# ----------------------------------------

def compute_meta_field(A, ring_harmonies):
    # Disharmonie
    dish = sum(1.0 - h for h in ring_harmonies)

    # Stabilität von A
    center = 1.0 - abs(A["af"] - 0.5)

    # Gedächtnis-Effekt: M steigt, wenn Muster wiederkehren
    memory_boost = 0.0
    if len(MEMORY["snapshots"]) > 10:
        last = MEMORY["snapshots"][-1]["ring_harmonies"]
        prev = MEMORY["snapshots"][-10]["ring_harmonies"]
        similarity = sum(1 - abs(a - b) for a, b in zip(last, prev)) / len(last)
        memory_boost = similarity * 0.2

    M = 0.6 * dish + 0.4 * center + memory_boost
    return M
    
def apply_meta_to_A(A, M):
    # M zieht A in Richtung Gleichgewicht
    A["af"] += (0.5 - A["af"]) * 0.002 * M

def apply_meta_to_rings(A, rings, M):
    for ring in rings:
        for pair in ring:
            B = pair["B"]
            C = pair["C"]

            # M stabilisiert Frequenzen
            B["af"] += (A["af"] - B["af"]) * 0.01 * M
            C["af"] += (B["af"] - C["af"]) * 0.01 * M

# ----------------------------------------
# Aufgaben-System (Tasks)
# ----------------------------------------

# Beispiel: Ring 2 soll maximale Harmonie halten
TARGET_RING = 1  # Ring 2 (Index 1)
TASK_STRENGTH = 0.02

# Awareness-Level des Systems
AWARENESS = 0.0

def apply_task(A, rings, ring_harmonies):
    global AWARENESS

    # Harmonie des Zielrings
    target_h = ring_harmonies[TARGET_RING]

    # Erfolg = hohe Harmonie
    success = target_h

    # Fehler = Disharmonie
    failure = 1.0 - target_h

    # Awareness wächst bei Erfolg UND Fehlern
    AWARENESS += (success * 0.01) + (failure * 0.02)

    # Task-Effekt: Ringe werden angepasst
    for pair in rings[TARGET_RING]:
        B = pair["B"]
        C = pair["C"]

        # Erfolg → Stabilisierung
        B["af"] += (A["af"] - B["af"]) * TASK_STRENGTH * success
        C["af"] += (B["af"] - C["af"]) * TASK_STRENGTH * success

        # Fehler → Drift-Korrektur
        B["af"] -= (B["af"] - 0.5) * TASK_STRENGTH * failure
        C["af"] -= (C["af"] - 0.5) * TASK_STRENGTH * failure

    # Rückkopplung auf A
    A["af"] += (0.5 - A["af"]) * 0.001 * failure

    return success, failure, AWARENESS

# ----------------------------------------
# Aufgaben-System (Tasks)
# ----------------------------------------

# Beispiel-Task: Ring 2 soll maximale Harmonie halten
TARGET_RING = 1  # Ring 2 (Index 1)
TASK_STRENGTH = 0.02

# Awareness-Level des Systems
AWARENESS = 0.0

def apply_task(A, rings, ring_harmonies):
    global AWARENESS

    # Harmonie des Zielrings
    target_h = ring_harmonies[TARGET_RING]

    # Erfolg = hohe Harmonie
    success = target_h

    # Misserfolg = Disharmonie
    failure = 1.0 - target_h

    # Awareness wächst bei Erfolg UND bei Fehlern
    # (wie ein Nervensystem, das lernt)
    AWARENESS += (success * 0.01) + (failure * 0.02)

    # Task-Effekt: Ringe werden angepasst
    for pair in rings[TARGET_RING]:
        B = pair["B"]
        C = pair["C"]

        # Erfolg → Stabilisierung
        B["af"] += (A["af"] - B["af"]) * TASK_STRENGTH * success
        C["af"] += (B["af"] - C["af"]) * TASK_STRENGTH * success

        # Misserfolg → Drift-Korrektur
        B["af"] -= (B["af"] - 0.5) * TASK_STRENGTH * failure
        C["af"] -= (C["af"] - 0.5) * TASK_STRENGTH * failure

    # Rückkopplung auf A
    A["af"] += (0.5 - A["af"]) * 0.001 * failure

    return success, failure, AWARENESS

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
    "drift": 0.00005
}

# ----------------------------------------
# Ringe & Dichtefelder
# ----------------------------------------
NUM_RINGS = 4
PAIRS_PER_RING = 6

# Radien der Ringe
RING_RADII = [0.7, 1.0, 1.3, 1.6]

# Phasenoffsets für die Dichtefelder (versetzte Hexagone)
RING_PHASES = [0.0, math.pi / 6, math.pi / 3, math.pi / 2]

def make_density_field(phase):
    return [
        0.5 + 0.5 * math.sin(i * 6 * math.pi / 180 + phase)
        for i in range(360)
    ]

DENSITY_FIELDS = [make_density_field(phase) for phase in RING_PHASES]

# ----------------------------------------
# Davidstern-Paare pro Ring
# ----------------------------------------
def make_pair(angle_deg, radius):
    angle = math.radians(angle_deg)
    angle2 = angle + math.pi

    return {
        "B": {
            "angle": angle,
            "radius": radius,
            "af": 0.4,
            "pf": 0.6,
            "rf": 0.5
        },
        "C": {
            "angle": angle2,
            "radius": radius,
            "af": 0.6,
            "pf": 0.4,
            "rf": 0.5
        }
    }

# Ringe: Liste von Ringen, jeder Ring = Liste von Paaren
rings = []
for r_index in range(NUM_RINGS):
    radius = RING_RADII[r_index]
    ring_pairs = []
    for p_index in range(PAIRS_PER_RING):
        angle_deg = p_index * (360 / PAIRS_PER_RING)
        ring_pairs.append(make_pair(angle_deg, radius))
    rings.append(ring_pairs)

# ----------------------------------------
# Harmonie eines Paares mit A
# ----------------------------------------
def harmony(A, B, C):
    return 1.0 - (
        abs(A["af"] - B["af"]) +
        abs(B["af"] - C["af"]) +
        abs(C["af"] - A["af"])
    )

# ----------------------------------------
# Update eines einzelnen Paares
# ----------------------------------------
def update_pair(A, B, C, density_field):
    # Winkel in Grad für Dichtefeld
    angle_deg = int(math.degrees(B["angle"])) % 360
    density = density_field[angle_deg]

    # B rotiert abhängig von Dichte
    B["angle"] += 0.01 + density * 0.004
    B["x"] = B["radius"] * math.cos(B["angle"])
    B["y"] = B["radius"] * math.sin(B["angle"])

    # C folgt B (180° versetzt)
    C["angle"] = B["angle"] + math.pi
    C["x"] = C["radius"] * math.cos(C["angle"])
    C["y"] = C["radius"] * math.sin(C["angle"])

    # Frequenzdrift durch Dichte
    B["af"] += (A["af"] - B["af"]) * 0.02 * density
    C["af"] += (B["af"] - C["af"]) * 0.02 * (1 - density)

    # Harmonie
    h = harmony(A, B, C)

    # Rückkopplung auf A (minimal, gewichtet mit Harmonie)
    A["af"] += (C["af"] - A["af"]) * A["drift"] * h

    return density, h

# ----------------------------------------
# Visualisierung
# ----------------------------------------
def bar(v):
    v = max(0.0, min(1.0, v))
    filled = int(v * 20)
    return "█" * filled + "░" * (20 - filled)

# ----------------------------------------
# Main Loop
# ----------------------------------------

try:
    while True:
        os.system("clear")

        # 1. Ringe updaten und Ring-Harmonien sammeln
        ring_harmonies = []

        for r_index, ring_pairs in enumerate(rings):
            density_field = DENSITY_FIELDS[r_index]
            ring_h_sum = 0.0

            for p_index, pair in enumerate(ring_pairs):
                B = pair["B"]
                C = pair["C"]
                density, h = update_pair(A, B, C, density_field)
                ring_h_sum += h

            ring_h_avg = ring_h_sum / PAIRS_PER_RING
            ring_harmonies.append(ring_h_avg)

        # 2. Snapshot speichern (erst NACHDEM ring_harmonies existiert)
        snapshot = {
            "A_af": A["af"],
            "ring_harmonies": ring_harmonies[:],
            "timestamp": time.time()
        }
        MEMORY["snapshots"].append(snapshot)

        # 3. Tunnels (Ring-Links) erzeugen
        for i in range(len(ring_harmonies)):
            for j in range(i+1, len(ring_harmonies)):
                if abs(ring_harmonies[i] - ring_harmonies[j]) < 0.05:
                    MEMORY["links"].append({
                        "from": i,
                        "to": j,
                        "type": "harmony_sync",
                        "timestamp": time.time()
                    })

        # 4. Meta-Feld berechnen
        M = compute_meta_field(A, ring_harmonies)

        # 5. Meta-Feld anwenden
        apply_meta_to_A(A, M)
        apply_meta_to_rings(A, rings, M)

        # 6. Ausgabe
        print(f"Meta-Feld M: {M:.4f}")
        print(f"A (Zentrum) AF: {A['af']:.4f}")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nBeendet.")

try:
    while True:
        os.system("clear")

        print("SATURN MULTI-RING ECOSYSTEM (4 RINGE, 6 DAVIDSTERNE JE RING)")
        print("-----------------------------------------------------------")
        print(f"A (Zentrum):  AF {bar(A['af'])} {A['af']:.3f}")
        print("-----------------------------------------------------------")

        # Für Übersicht: pro Ring eine aggregierte Harmonie
        for r_index, ring_pairs in enumerate(rings):
            density_field = DENSITY_FIELDS[r_index]
            ring_h_sum = 0.0

            print(f"RING {r_index+1} (Radius {RING_RADII[r_index]:.2f})")

            for p_index, pair in enumerate(ring_pairs):
                B = pair["B"]
                C = pair["C"]

                density, h = update_pair(A, B, C, density_field)
                ring_h_sum += h

                print(f"  Paar {p_index+1}: H {h:.4f}  Dichte {density:.3f}  B_AF {B['af']:.3f}  C_AF {C['af']:.3f}")

            ring_h_avg = ring_h_sum / PAIRS_PER_RING
            print(f"  -> Ring-Harmonie (Ø): {ring_h_avg:.4f}")
            print("")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nBeendet.")

