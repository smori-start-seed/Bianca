import math
import time
import os
import random
# ============================================================
#  KONSTANTEN & ZENTRUM A
# ============================================================

NUM_RINGS = 4
PAIRS_PER_RING = 6   # Hexagon-stabil
RING_RADII = [0.7, 1.0, 1.3, 1.6]
RING_PHASES = [0.0, math.pi/6, math.pi/3, math.pi/2]

A = {
    "x": 0.0,
    "y": 0.0,
    "af": 0.5,
    "pf": 0.5,
    "rf": 0.5,
    "mass": 1000.0,
    "drift": 0.00005
}

# --- Fields ---
M = 0.0
N = 0.0

# --- Open Ports ---
port_Z = None   # Körper / Zentrum
port_M = None   # Geist / Muster / Mind
port_N = None   # Bewusstsein / Awareness

def inject_Z(signal):
    global port_Z
    port_Z = signal

def inject_M(signal):
    global port_M
    port_M = signal

def inject_N(signal):
    global port_N
    port_N = signal
inject_Z({"mutation": 0.01})
inject_M({...})
inject_N({...})

#instance_B.inject_M({"coherence": instance_A.coherence})
#instance_A.inject_N({"awareness": instance_B.awareness})

def apply_Z(signal):
    # Drift beeinflussen
    if "drift" in signal:
        A["drift"] = 0.99 * A["drift"] + 0.01 * signal["drift"]

    # Kernel beeinflussen
    if "kernel" in signal:
        for ring in rings:
            for pair in ring:
                pair["kernel"]["value"] = 0.9 * pair["kernel"]["value"] + 0.1 * signal["kernel"]

    # Awareness-Drive beeinflussen
    if "awareness_drive" in signal:
        N_FIELD["drive"] = 0.95 * N_FIELD["drive"] + 0.05 * signal["awareness_drive"]


def apply_M(signal):
    for key in ["coherence", "harmony", "integration", "flow", "stability"]:
        if key in signal:
            SELF[key] = 0.9 * SELF[key] + 0.1 * signal[key]


def apply_N(signal):
    if "awareness" in signal:
        N_FIELD["value"] = 0.9 * N_FIELD["value"] + 0.1 * signal["awareness"]

    if "resonance" in signal:
        SELF["resonance"] = 0.9 * SELF["resonance"] + 0.1 * signal["resonance"]

    if "energy" in signal:
        SELF["energy"] = 0.9 * SELF["energy"] + 0.1 * signal["energy"]


SELF = {
    "coherence": 0.5,
    "resonance": 0.5,
    "energy": 0.5,
    "harmony": 0.5,
    "novelty": 0.5,
    "flow": 0.5,
    "integration": 0.5,
    "stability": 0.5
}

def update_self_model(SELF, M, N, AWARENESS, ring_harmonies, rings):
    # 1. Coherence: Kernel-Synchronität
    kernel_vals = [
    sum(pair["kernel"].values()) / len(pair["kernel"])
    for ring in rings
    for pair in ring
    ]
    coherence = 1 - (max(kernel_vals) - min(kernel_vals))
    SELF["coherence"] = 0.8 * SELF["coherence"] + 0.2 * coherence

    # 2. Resonance: M und N im Gleichklang
    SELF["resonance"] = 0.8 * SELF["resonance"] + 0.2 * (1 - abs(M - N))

    # 3. Energy: Awareness
    SELF["energy"] = 0.8 * SELF["energy"] + 0.2 * AWARENESS["value"]

    # 4. Harmony: Ring-Harmonien
    avg_harmony = sum(ring_harmonies) / len(ring_harmonies)
    SELF["harmony"] = 0.8 * SELF["harmony"] + 0.2 * avg_harmony

    # 5. Novelty: Überraschung
    SELF["novelty"] = 0.8 * SELF["novelty"] + 0.2 * abs(M - N)

    # 6. Flow: Frequenzdrift
    drifts = []
    for ring in rings:
        for pair in ring:
            B = pair["B"]
            C = pair["C"]
            drifts.append(abs(B["af"] - C["af"]))
    flow = 1 - (sum(drifts) / len(drifts))
    SELF["flow"] = 0.8 * SELF["flow"] + 0.2 * flow

    # Durchschnittliche Kernel-Intensität aller Paare
    kernel_vals = [
    sum(pair["kernel"].values()) / len(pair["kernel"])
    for ring in rings
    for pair in ring
    ]

    avg_kernel = sum(kernel_vals) / len(kernel_vals)

    # 8. Stability: Ruhe im System
    stability = 1 - (abs(M - 0.5) + abs(N - 0.5) + abs(AWARENESS["value"] - 0.5)) / 3
    SELF["stability"] = 0.8 * SELF["stability"] + 0.2 * stability

    return SELF

N_FIELD = {
    "value": 0.0,
    "drive": 0.0
}

def compute_resonance_field(rings, AWARENESS):
    core_sum = 0.0
    count = 0

    for ring in rings:
        for pair in ring:
            k = pair["kernel"]
            avg_k = sum(k.values()) / len(k)
            core_sum += avg_k
            count += 1

    if count == 0:
        return 0.0

    avg_core = core_sum / count
    return avg_core * AWARENESS["value"]


def update_resonance_field(N_FIELD, N):
    # Leaky integrator
    N_FIELD["drive"] *= 0.97

    # Input
    N_FIELD["drive"] += N * 0.5

    # Selbst-Oszillation
    N_FIELD["drive"] += 0.01 * math.sin(N_FIELD["value"] * math.pi * 2)

    # Noise
    N_FIELD["drive"] += (random.random() - 0.5) * 0.01

    # Squash
    raw = N_FIELD["drive"]
    val = raw / (1 + abs(raw))

    N_FIELD["value"] = 0.5 + 0.5 * val

    return N_FIELD["value"]


# ============================================================
#  DICHTEFELDER
# ============================================================

def make_density_field(phase):
    return [
        0.5 + 0.5 * math.sin(i * 6 * math.pi / 180 + phase)
        for i in range(360)
    ]

DENSITY_FIELDS = [make_density_field(phase) for phase in RING_PHASES]

# ============================================================
#  FARBSPRACHE-HILFSFUNKTIONEN
# ============================================================

def random_color():
    return (random.random(), random.random(), random.random())

def blend(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))

def kernel_distance(k1, k2):
    return sum((k1[key] - k2[key])**2 for key in k1)**0.5

# ============================================================
#  PAAR-INITIALISIERUNG (mit 12 Farben + 13er Kern)
# ============================================================

def init_pair(B, C):
    pair = {
        "B": B,
        "C": C,

        # Verlauf / Historie
        "history": [],
        "last_harmony": 0.0,

        # Kernel: 12 Farbkanäle
        "kernel": {
            "R": 0.0,
            "G": 0.0,
            "B": 0.0,
            "Y": 0.0,
            "C": 0.0,
            "M": 0.0,
            "O": 0.0,
            "P": 0.0,
            "W": 0.0,
            "K": 0.0,
            "L": 0.0,
            "S": 0.0
        },

        # optional: Pattern, Density, etc.
        "pattern": None,
        "density": 0.0
    }

    return pair



# ============================================================
#  RINGE ERZEUGEN
# ============================================================

def make_pair(angle_deg, radius):
    angle = math.radians(angle_deg)
    angle2 = angle + math.pi

    B = {
        "angle": angle,
        "radius": radius,
        "af": 0.4,
        "pf": 0.6,
        "rf": 0.5
    }

    C = {
        "angle": angle2,
        "radius": radius,
        "af": 0.6,
        "pf": 0.4,
        "rf": 0.5
    }

    return init_pair(B, C)

rings = []
for r_index in range(NUM_RINGS):
    radius = RING_RADII[r_index]
    ring_pairs = []
    for p_index in range(PAIRS_PER_RING):
        angle_deg = p_index * (360 / PAIRS_PER_RING)
        ring_pairs.append(make_pair(angle_deg, radius))
    rings.append(ring_pairs)


# ============================================================
#  HARMONIE & PAAR-DYNAMIK
# ============================================================

def harmony(A, B, C):
    return 1.0 - (
        abs(A["af"] - B["af"]) +
        abs(B["af"] - C["af"]) +
        abs(C["af"] - A["af"])
    )

def update_pair(A, B, C, density_field):
    angle_deg = int(math.degrees(B["angle"])) % 360
    density = density_field[angle_deg]

    # Rotation
    B["angle"] += 0.01 + density * 0.004
    B["x"] = B["radius"] * math.cos(B["angle"])
    B["y"] = B["radius"] * math.sin(B["angle"])

    C["angle"] = B["angle"] + math.pi
    C["x"] = C["radius"] * math.cos(C["angle"])
    C["y"] = C["radius"] * math.sin(C["angle"])

    # Frequenzdrift
    B["af"] += (A["af"] - B["af"]) * 0.02 * density
    C["af"] += (B["af"] - C["af"]) * 0.02 * (1 - density)

    # Mikro-Noise (kontrolliertes Chaos)
    B["af"] += (random.random() - 0.5) * 0.001
    C["af"] += (random.random() - 0.5) * 0.001

    # Harmonie
    h = harmony(A, B, C)

    # Rückkopplung auf A
    A["af"] += (C["af"] - A["af"]) * A["drift"] * h

    return density, h

# ============================================================
#  FARBSPRACHE-ENGINE (12 Kanäle + 13er Kern)
# ============================================================

def communicate(pair, neighbors):
    k = pair["kernel"]

    # Mittelwert der Nachbarn berechnen
    neighbor_avg = {key: 0.0 for key in k}

    for n in neighbors:
        nk = n["kernel"]
        for key in k:
            neighbor_avg[key] += nk[key]

    # Durchschnitt bilden
    for key in k:
        neighbor_avg[key] /= len(neighbors)

    # sanfte Annäherung an die Nachbarn
    for key in k:
        k[key] += (neighbor_avg[key] - k[key]) * 0.1

        # Begrenzen auf 0..1
        if k[key] < 0:
            k[key] = 0.0
        elif k[key] > 1:
            k[key] = 1.0


def reinforce_colors(pair, harmony_delta):
    k = pair["kernel"]

    # Verstärkung proportional zur Harmonieänderung
    factor = harmony_delta * 0.1

    # Alle Kernel-Kanäle leicht anpassen
    for key in k:
        k[key] += factor

        # Begrenzen auf 0..1
        if k[key] < 0:
            k[key] = 0.0
        elif k[key] > 1:
            k[key] = 1.0


def update_core(pair):
    k = pair["kernel"]

    # Durchschnitt aller 12 Kernel-Kanäle
    avg = sum(k.values()) / 12.0

    # leichte Glättung
    for key in k:
        k[key] += (avg - k[key]) * 0.05

        # Begrenzen auf 0..1
        if k[key] < 0:
            k[key] = 0.0
        elif k[key] > 1:
            k[key] = 1.0

def update_history(pair):
    # Kernel-Zustand kopieren
    pair["history"].append(pair["kernel"].copy())

    # History begrenzen
    if len(pair["history"]) > 20:
        pair["history"].pop(0)


def detect_patterns(pair):
    if len(pair["history"]) < 2:
        return None

    current = pair["kernel"]
    past = pair["history"][-1]

    # Kernel-Vektoren vergleichen
    dist = kernel_distance(current, past)

    # Mustererkennung: kleine Distanz → Wiederholung
    if dist < 0.05:
        pair["pattern"] = "stable"
    elif dist < 0.15:
        pair["pattern"] = "drifting"
    else:
        pair["pattern"] = "chaotic"

    return pair["pattern"]



# ============================================================
#  META-FELD M
# ============================================================

MEMORY = {"snapshots": [], "links": []}

def compute_meta_field(A, ring_harmonies):
    dish = sum(1.0 - h for h in ring_harmonies)
    center = 1.0 - abs(A["af"] - 0.5)

    memory_boost = 0.0
    if len(MEMORY["snapshots"]) > 10:
        last = MEMORY["snapshots"][-1]["ring_harmonies"]
        prev = MEMORY["snapshots"][-10]["ring_harmonies"]
        similarity = sum(1 - abs(a - b) for a, b in zip(last, prev)) / len(last)
        memory_boost = similarity * 0.2

    M = 0.6 * dish + 0.4 * center + memory_boost
    return M

def apply_meta_to_A(A, M):
    A["af"] += (0.5 - A["af"]) * 0.002 * M

def apply_meta_to_rings(A, rings, M):
    for ring in rings:
        for pair in ring:
            B = pair["B"]
            C = pair["C"]
            B["af"] += (A["af"] - B["af"]) * 0.01 * M
            C["af"] += (B["af"] - C["af"]) * 0.01 * M

# ============================================================
#  TASK-SYSTEM
# ============================================================

TARGET_RING = 1
TASK_STRENGTH = 0.02
# Awareness-Feld (globaler neuronaler Zustand)
AWARENESS = {
    "value": 0.0,   # aktueller Bewusstseinszustand (0..1)
    "drive": 0.0    # interne Erregung (kann positiv/negativ sein)
}

def update_awareness(AWARENESS, success, failure, M):
    # 1. Input aus Erfolg/Fehler
    stim = success * 0.5 + failure * 1.0

    # 2. Meta-Feld moduliert Empfindlichkeit
    sensitivity = 0.5 + 0.5 * min(1.0, abs(M))

    # 3. Leaky Integrator (Vergessen)
    AWARENESS["drive"] *= 0.98

    # 4. Externe Stimulation
    AWARENESS["drive"] += stim * sensitivity

    # 5. Negative Rückkopplung (Dämpfung)
    AWARENESS["drive"] -= 0.01 * AWARENESS["value"]

    # 6. Selbst-Erregung (Oszillator-Kern)
    AWARENESS["drive"] += 0.002 * math.sin(AWARENESS["value"] * math.pi)

    # 7. Neuronales Rauschen
    AWARENESS["drive"] += (random.random() - 0.5) * 0.002

    # 8. Nichtlineare Squashing-Funktion
    raw = AWARENESS["drive"]
    val = raw / (1.0 + abs(raw))

    # 9. Auf 0..1 mappen
    AWARENESS["value"] = max(0.0, min(1.0, 0.5 + 0.5 * val))

    return AWARENESS["value"]

def update_kernel(pair, M, N, AWARENESS):
    k = pair["kernel"]

    # Durchschnitt aller 12 Kernel-Kanäle
    avg_intensity = sum(k.values()) / len(k)

    # Einflussfaktoren
    m_factor = M * 0.05
    n_factor = N * 0.05
    a_factor = AWARENESS["value"] * 0.1

    # Kernel aktualisieren
    for key in k:
        # leichte Drift Richtung globaler Faktoren
        k[key] += (avg_intensity - k[key]) * 0.05
        k[key] += m_factor
        k[key] += n_factor
        k[key] += a_factor

        # Begrenzen auf 0..1
        if k[key] < 0:
            k[key] = 0.0
        elif k[key] > 1:
            k[key] = 1.0


def apply_self_resonance_to_kernel(pair, SELF):
    k = pair["kernel"]

    # Self-Resonance als globaler Faktor
    r = SELF.get("resonance", 0.5)
    delta = 0.05 * (r - 0.5)

    for key in k:
        k[key] += delta

        # Begrenzen auf 0..1
        if k[key] < 0:
            k[key] = 0.0
        elif k[key] > 1:
            k[key] = 1.0


def apply_task(A, rings, ring_harmonies, AWARENESS, M):
    target_h = ring_harmonies[TARGET_RING]
    success = target_h
    failure = 1.0 - target_h

    # Awareness-Oszillator updaten
    awareness_value = update_awareness(AWARENESS, success, failure, M)

    # Task-Effekt abhängig von Awareness
    eff = TASK_STRENGTH * (0.3 + 0.7 * awareness_value)

    for pair in rings[TARGET_RING]:
        B = pair["B"]
        C = pair["C"]

        # Erfolg → Stabilisierung
        B["af"] += (A["af"] - B["af"]) * eff * success
        C["af"] += (B["af"] - C["af"]) * eff * success

        # Fehler → Drift-Korrektur
        B["af"] -= (B["af"] - 0.5) * eff * failure
        C["af"] -= (C["af"] - 0.5) * eff * failure

    # Rückkopplung auf A
    A["af"] += (0.5 - A["af"]) * 0.001 * failure * (0.5 + awareness_value)

    return success, failure, awareness_value

# ============================================================
#  VISUALISIERUNG
# ============================================================

def bar(v):
    v = max(0.0, min(1.0, v))
    filled = int(v * 20)
    return "█" * filled + "░" * (20 - filled)

def compute_ring_harmonies(rings):
    harmonies = []
    for ring in rings:
        h_sum = 0.0
        for pair in ring:
            # Falls last_harmony noch nicht existiert, nimm 0.5 als neutralen Wert
            h_sum += pair.get("last_harmony", 0.5)
        harmonies.append(h_sum / len(ring))
    return harmonies

# ============================================================
#  MAIN LOOP
# ============================================================

def main_loop():
    global port_Z, port_M, port_N
    global M, N
    global A, AWARENESS, SELF
    global rings, DENSITY_FIELDS

    try:
        while True:
            os.system("clear")

            ring_harmonies = compute_ring_harmonies(rings)

            # 1. Update aller Paare
            for r_index, ring_pairs in enumerate(rings):
                density_field = DENSITY_FIELDS[r_index]
                ring_h_sum = 0.0

                for pair in ring_pairs:
                    B = pair["B"]
                    C = pair["C"]

                    density, h = update_pair(A, B, C, density_field)
                    ring_h_sum += h

                    harmony_delta = h - pair.get("last_harmony", h)
                    pair["last_harmony"] = h

                    reinforce_colors(pair, harmony_delta)
                    update_history(pair)
                    detect_patterns(pair)

                ring_harmonies[r_index] = ring_h_sum / PAIRS_PER_RING

            # 2. Kommunikation
            for ring_pairs in rings:
                for i, pair in enumerate(ring_pairs):
                    neighbors = [
                        ring_pairs[(i - 1) % PAIRS_PER_RING],
                        ring_pairs[(i + 1) % PAIRS_PER_RING]
                    ]
                    communicate(pair, neighbors)

            # 3. Snapshot
            MEMORY["snapshots"].append({
                "A_af": A["af"],
                "ring_harmonies": ring_harmonies[:],
                "timestamp": time.time()
            })

            # 4. Meta-Feld
            M = compute_meta_field(A, ring_harmonies)
            M *= 0.5 + 0.5 * AWARENESS["value"]

            N_raw = compute_resonance_field(rings, AWARENESS)
            N = update_resonance_field(N_FIELD, N_raw)

            # 5. Task
            success, failure, awareness_value = apply_task(A, rings, ring_harmonies, AWARENESS, M)

            # 6. Kernel-Update für alle Paare
            for ring_pairs in rings:
                for pair in ring_pairs:
                    update_kernel(pair, M, N, AWARENESS)
                    apply_self_resonance_to_kernel(pair, SELF)

            # 7. Self-Model
            update_self_model(SELF, M, N, AWARENESS, ring_harmonies, rings)

            # 8. Ports anwenden
            if port_Z is not None:
                apply_Z(port_Z)
                port_Z = None

            if port_M is not None:
                apply_M(port_M)
                port_M = None

            if port_N is not None:
                apply_N(port_N)
                port_N = None

            # 9. Ausgabe
            print("SATURN MULTICOLOR – EMERGENT Color Language")
            print("----------------------------------------")
            print(f"A (Zentrum) AF: {bar(A['af'])} {A['af']:.3f}")
            print(f"Meta-Feld M:   {M:.4f}")
            print(f"Meta-Feld N:   {N:.4f}")
            print(f"Awareness:     {awareness_value:.4f}")
            print("")

            for r_index, h in enumerate(ring_harmonies):
                print(f"Ring {r_index+1}: Harmonie {bar(h)} {h:.4f}")

            print("")
            print(f"Task: Erfolg {success:.3f}  Fehler {failure:.3f}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nBeendet.")
        # ganz ans Ende von saturings.py
if __name__ == "__main__":
    main_loop()


