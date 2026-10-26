import math
import time
import random

# ============================================================
#  KONSTANTEN
# ============================================================

NUM_RINGS = 359
STARS_PER_RING = 59

RING_RADII = [
    0.5 + i * 0.01
    for i in range(NUM_RINGS)
]

RING_PHASES = [
    (i * math.pi / 180) % (2 * math.pi)
    for i in range(NUM_RINGS)
]

MAX_HISTORY = 20
MAX_SNAPSHOTS = 5000000

TARGET_RING = 1
TASK_STRENGTH = 0.02
MAX_STEPS = 5000000


# ============================================================
#  PORTS (float-based)
# ============================================================

port_Z = 0.5   # Drift
port_M = 0.5   # Harmony
port_N = 0.5   # Awareness

def inject_Z(value: float):
    global port_Z
    port_Z = float(value)

def inject_M(value: float):
    global port_M
    port_M = float(value)

def inject_N(value: float):
    global port_N
    port_N = float(value)

def apply_Z(value: float):
    A["drift"] *= (0.5 + value)

def apply_M(value: float):
    global M
    M *= (0.5 + value)

def apply_N(value: float):
    global N
    N *= (0.5 + value)

# ============================================================
#  ZENTRUM / FELDER
# ============================================================

A = {
    "x": 0.0,
    "y": 0.0,
    "af": 0.5,
    "pf": 0.5,
    "rf": 0.5,
    "mass": 1000.0,
    "drift": 0.00005
}

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

AWARENESS = {
    "value": 0.0,
    "drive": 0.0
}

N_FIELD = {
    "value": 0.0,
    "drive": 0.0
}

MEMORY = {
    "snapshots": [],
    "links": []
}

M = 0.0
N = 0.0



# ============================================================
#  HILFSFUNKTIONEN
# ============================================================

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def bar(v, width=20):
    v = clamp(v)
    filled = int(v * width)
    return "█" * filled + "░" * (width - filled)

def random_color():
    return (random.random(), random.random(), random.random())

def blend(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))

def kernel_distance(k1, k2):
    keys = k1.keys()
    return sum((k1[key] - k2[key]) ** 2 for key in keys) ** 0.5


# ============================================================
#  FARBSPRACHE / RINGE
# ============================================================

def make_density_field(phase):
    return [
        0.5 + 0.5 * math.sin(i * 6 * math.pi / 180 + phase)
        for i in range(360)
    ]

DENSITY_FIELDS = [make_density_field(phase) for phase in RING_PHASES]

def make_star_pair(angle_deg, radius):
    base_angle = math.radians(angle_deg)

    points = []
    for i in range(6):
        a = base_angle + i * (math.pi / 3)
        points.append({
            "angle": a,
            "radius": radius,
            "af": 0.5,
            "pf": 0.5,
            "rf": 0.5,
            "x": radius * math.cos(a),
            "y": radius * math.sin(a)
        })

    # B und C als Alias für alte Engine
    B = points[0]
    C = points[3]

    return {
        "points": points,
        "B": B,
        "C": C,
        "history": [],
        "last_harmony": 0.5,
        "kernel": {k: 0.0 for k in ["R","G","B","Y","C","M","O","P","W","K","L","S"]},
        "pattern": None,
        "density": 0.0
    }


rings = []
for r_index in range(NUM_RINGS):
    radius = RING_RADII[r_index]
    ring_pairs = []

    for s_index in range(STARS_PER_RING):
        angle_deg = s_index * (360 / STARS_PER_RING)
        ring_pairs.append(make_star_pair(angle_deg, radius))

    rings.append(ring_pairs)


# ============================================================
#  PAAR-DYNAMIK
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

    B["angle"] += 0.01 + density * 0.004
    B["x"] = B["radius"] * math.cos(B["angle"])
    B["y"] = B["radius"] * math.sin(B["angle"])

    C["angle"] = B["angle"] + math.pi
    C["x"] = C["radius"] * math.cos(C["angle"])
    C["y"] = C["radius"] * math.sin(C["angle"])

    B["af"] += (A["af"] - B["af"]) * 0.02 * density
    C["af"] += (B["af"] - C["af"]) * 0.02 * (1 - density)

    B["af"] += (random.random() - 0.5) * 0.001
    C["af"] += (random.random() - 0.5) * 0.001

    h = harmony(A, B, C)
    A["af"] += (C["af"] - A["af"]) * A["drift"] * h

    print("update_pair called, h =", h)
    return density, h

# ============================================================
#  KERNEL / KOMMUNIKATION
# ============================================================

def communicate(pair, neighbors):
    if not neighbors:
        return

    k = pair["kernel"]
    neighbor_avg = {key: 0.0 for key in k}

    for n in neighbors:
        nk = n["kernel"]
        for key in k:
            neighbor_avg[key] += nk[key]

    for key in k:
        neighbor_avg[key] /= len(neighbors)
        k[key] += (neighbor_avg[key] - k[key]) * 0.1
        k[key] = clamp(k[key])

def reinforce_colors(pair, harmony_delta):
    k = pair["kernel"]
    factor = harmony_delta * 0.1
    for key in k:
        k[key] = clamp(k[key] + factor)

def update_core(pair):
    k = pair["kernel"]
    avg = sum(k.values()) / len(k)
    for key in k:
        k[key] = clamp(k[key] + (avg - k[key]) * 0.05)

def update_history(pair):
    pair["history"].append(pair["kernel"].copy())
    if len(pair["history"]) > MAX_HISTORY:
        pair["history"].pop(0)

def detect_patterns(pair):
    if len(pair["history"]) < 2:
        pair["pattern"] = None
        return None

    current = pair["history"][-1]
    past = pair["history"][-2]
    dist = kernel_distance(current, past)

    if dist < 0.05:
        pair["pattern"] = "stable"
    elif dist < 0.15:
        pair["pattern"] = "drifting"
    else:
        pair["pattern"] = "chaotic"

    return pair["pattern"]

    print("Kernel Communication loaded")

# ============================================================
#  META / AWARENESS
# ============================================================

def compute_ring_harmonies(rings):
    harmonies = []
    for ring in rings:
        if not ring:
            harmonies.append(0.5)
            continue
        h_sum = sum(pair.get("last_harmony", 0.5) for pair in ring)
        harmonies.append(h_sum / len(ring))
    return harmonies

def compute_meta_field(A, ring_harmonies):
    if not ring_harmonies:
        return 0.0

    dish = sum(1.0 - clamp(h) for h in ring_harmonies)
    center = 1.0 - abs(A["af"] - 0.5)

    memory_boost = 0.0
    if len(MEMORY["snapshots"]) >= 10:
        last = MEMORY["snapshots"][-1]["ring_harmonies"]
        prev = MEMORY["snapshots"][-10]["ring_harmonies"]
        if last and prev and len(last) == len(prev):
            similarity = sum(1.0 - abs(a - b) for a, b in zip(last, prev)) / len(last)
            memory_boost = similarity * 0.2

    M_val = 0.6 * dish + 0.4 * center + memory_boost
    return M_val

def apply_meta_to_A(A, M):
    A["af"] += (0.5 - A["af"]) * 0.002 * M

def apply_meta_to_rings(A, rings, M):
    for ring in rings:
        for pair in ring:
            B = pair["B"]
            C = pair["C"]
            B["af"] += (A["af"] - B["af"]) * 0.01 * M
            C["af"] += (B["af"] - C["af"]) * 0.01 * M

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
def update_resonance_field(N_FIELD, N_input):
    N_FIELD["drive"] *= 0.97
    N_FIELD["drive"] += N_input * 0.5
    N_FIELD["drive"] += 0.01 * math.sin(N_FIELD["value"] * math.pi * 2)
    N_FIELD["drive"] += (random.random() - 0.5) * 0.01

    raw = N_FIELD["drive"]
    val = raw / (1 + abs(raw))
    N_FIELD["value"] = 0.5 + 0.5 * val
    return N_FIELD["value"]

def update_awareness(AWARENESS, success, failure, M):
    stim = success * 0.5 + failure * 1.0
    sensitivity = 0.5 + 0.5 * min(1.0, abs(M))

    AWARENESS["drive"] *= 0.98
    AWARENESS["drive"] += stim * sensitivity
    AWARENESS["drive"] -= 0.01 * AWARENESS["value"]
    AWARENESS["drive"] += 0.002 * math.sin(AWARENESS["value"] * math.pi)
    AWARENESS["drive"] += (random.random() - 0.5) * 0.002

    raw = AWARENESS["drive"]
    val = raw / (1.0 + abs(raw))
    AWARENESS["value"] = clamp(0.5 + 0.5 * val)
    return AWARENESS["value"]

def update_kernel(pair, M, N, AWARENESS):
    k = pair["kernel"]
    avg_intensity = sum(k.values()) / len(k)

    m_factor = M * 0.05
    n_factor = N * 0.05
    a_factor = AWARENESS["value"] * 0.1

    for key in k:
        k[key] += (avg_intensity - k[key]) * 0.05
        k[key] += m_factor + n_factor + a_factor
        k[key] = clamp(k[key])

def apply_self_resonance_to_kernel(pair, SELF):
    k = pair["kernel"]
    r = SELF.get("resonance", 0.5)
    delta = 0.05 * (r - 0.5)
    for key in k:
        k[key] = clamp(k[key] + delta)

def update_self_model(SELF, M, N, AWARENESS, ring_harmonies, rings):
    kernel_vals = [
        sum(pair["kernel"].values()) / len(pair["kernel"])
        for ring in rings
        for pair in ring
    ]

    if kernel_vals:
        coherence = 1.0 - (max(kernel_vals) - min(kernel_vals))
    else:
        coherence = 0.5
    SELF["coherence"] = 0.8 * SELF["coherence"] + 0.2 * clamp(coherence)

    SELF["resonance"] = 0.8 * SELF["resonance"] + 0.2 * clamp(1.0 - abs(M - N))
    SELF["energy"] = 0.8 * SELF["energy"] + 0.2 * clamp(AWARENESS["value"])

    avg_harmony = sum(ring_harmonies) / len(ring_harmonies) if ring_harmonies else 0.5
    SELF["harmony"] = 0.8 * SELF["harmony"] + 0.2 * clamp(avg_harmony)

    SELF["novelty"] = 0.8 * SELF["novelty"] + 0.2 * clamp(abs(M - N))

    drifts = []
    for ring in rings:
        for pair in ring:
            B = pair["B"]
            C = pair["C"]
            drifts.append(abs(B["af"] - C["af"]))

    flow = 1.0 - (sum(drifts) / len(drifts)) if drifts else 0.5
    SELF["flow"] = 0.8 * SELF["flow"] + 0.2 * clamp(flow)

    stability = 1.0 - (abs(M - 0.5) + abs(N - 0.5) + abs(AWARENESS["value"] - 0.5)) / 3
    SELF["stability"] = 0.8 * SELF["stability"] + 0.2 * clamp(stability)

    return SELF



# ============================================================
#  TASK-SYSTEM
# ============================================================

def apply_task(A, rings, ring_harmonies, AWARENESS, M):
    if len(ring_harmonies) <= TARGET_RING:
        return 0.5, 0.5, AWARENESS["value"]

    target_h = clamp(ring_harmonies[TARGET_RING])
    success = target_h
    failure = 1.0 - target_h

    awareness_value = update_awareness(AWARENESS, success, failure, M)
    eff = TASK_STRENGTH * (0.3 + 0.7 * awareness_value)

    for pair in rings[TARGET_RING]:
        B = pair["B"]
        C = pair["C"]

        B["af"] += (A["af"] - B["af"]) * eff * success
        C["af"] += (B["af"] - C["af"]) * eff * success

        B["af"] -= (B["af"] - 0.5) * eff * failure
        C["af"] -= (C["af"] - 0.5) * eff * failure

    A["af"] += (0.5 - A["af"]) * 0.001 * failure * (0.5 + awareness_value)

    return success, failure, awareness_value

print("Task loaded")


# ============================================================
#  MAIN LOOP
# ============================================================

def main_loop(max_steps=MAX_SNAPSHOTS, sleep_time=0.01):
    global M, N

    for step in range(max_steps):

        # ----------------------------------------------------
        # 1. RING-HARMONIEN BERECHNEN
        # ----------------------------------------------------
        ring_harmonies = compute_ring_harmonies(rings)

        for r_index, ring_pairs in enumerate(rings):
            density_field = DENSITY_FIELDS[r_index]
            ring_h_sum = 0.0

            for pair in ring_pairs:
                B = pair["B"]
                C = pair["C"]

                density, h = update_pair(A, B, C, density_field)
                ring_h_sum += h
                pair["density"] = density

                harmony_delta = h - pair.get("last_harmony", h)
                pair["last_harmony"] = h

                reinforce_colors(pair, harmony_delta)
                update_history(pair)
                detect_patterns(pair)
                update_core(pair)

            ring_harmonies[r_index] = ring_h_sum / len(ring_pairs) if ring_pairs else 0.5

        # ----------------------------------------------------
        # 2. KOMMUNIKATION
        # ----------------------------------------------------
        for ring_pairs in rings:
            for i, pair in enumerate(ring_pairs):
                neighbors = [
                    ring_pairs[(i - 1) % len(ring_pairs)],
                    ring_pairs[(i + 1) % len(ring_pairs)]
                ]
                communicate(pair, neighbors)

        # ----------------------------------------------------
        # 3. MEMORY SNAPSHOT
        # ----------------------------------------------------
        MEMORY["snapshots"].append({
            "A_af": A["af"],
            "ring_harmonies": ring_harmonies[:],
            "timestamp": time.time()
        })
        if len(MEMORY["snapshots"]) > MAX_SNAPSHOTS:
            MEMORY["snapshots"].pop(0)

        # ----------------------------------------------------
        # 4. META-FELD M & RESONANZ N
        # ----------------------------------------------------
        M = compute_meta_field(A, ring_harmonies)
        M *= 0.5 + 0.5 * AWARENESS["value"]

        N_input = compute_resonance_field(rings, AWARENESS)
        N = update_resonance_field(N_FIELD, N_input)

        # ----------------------------------------------------
        # 5. TASK-SYSTEM
        # ----------------------------------------------------
        success, failure, awareness_value = apply_task(A, rings, ring_harmonies, AWARENESS, M)

        # ----------------------------------------------------
        # 6. KERNEL-UPDATES
        # ----------------------------------------------------
        for ring_pairs in rings:
            for pair in ring_pairs:
                update_kernel(pair, M, N, AWARENESS)
                apply_self_resonance_to_kernel(pair, SELF)

        # ----------------------------------------------------
        # 7. SELF-MODELL
        # ----------------------------------------------------
        update_self_model(SELF, M, N, AWARENESS, ring_harmonies, rings)

        # ----------------------------------------------------
        # 8. META-EINFLUSS AUF A UND RINGE
        # ----------------------------------------------------
        apply_meta_to_A(A, M)
        apply_meta_to_rings(A, rings, M)

        # ----------------------------------------------------
        # 9. PORTS ANWENDEN (UI → ENGINE)
        # ----------------------------------------------------
        apply_Z(port_Z)   # Drift modulieren
        apply_M(port_M)   # Meta-Feld modulieren
        apply_N(port_N)   # Resonanz modulieren

        # ----------------------------------------------------
        # 10. AUSGABE
        # ----------------------------------------------------
        print("\033[H\033[J", end="")
        print("SATURN MULTICOLOR – EMERGENT Color Language")
        print("----------------------------------------")
        print(f"Step:          {step + 1}/{max_steps}")
        print(f"A (Zentrum) AF: {bar(A['af'])} {A['af']:.3f}")
        print(f"Meta-Feld M:   {M:.4f}")
        print(f"Meta-Feld N:   {N:.4f}")
        print(f"Awareness:     {awareness_value:.4f}")
        print("")

        for r_index, h in enumerate(ring_harmonies):
            print(f"Ring {r_index + 1}: Harmonie {bar(h)} {h:.4f}")

        print("")
        print(f"Task: Erfolg {success:.3f}  Fehler {failure:.3f}")
        print(f"SELF coherence: {SELF['coherence']:.3f}  resonance: {SELF['resonance']:.3f}")
        print(f"Pattern ring 1, pair 1: {rings[0][0]['pattern']}")

        time.sleep(sleep_time)

    print("\nBeendet.")
if __name__ == "__main__":
    print("saturings.py loaded, starting main_loop()")
    main_loop()

