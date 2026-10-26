# saturings.py – Colorverse Evolution
import random
import time
from config import *
from Zelle import Zelle
from Cluster import Cluster
from Ring import Ring
from Sphere import Sphere
from MetaSphere import MetaSphere
from UniverseNode import UniverseNode
from engine import Engine
from saturn_hexagon_core import SaturnHexagon


# ============================================================
#  HEX-NACHBARN
# ============================================================

def set_initial_hex_neighbors(zellen):
    n = len(zellen)
    for i, z in enumerate(zellen):
        z.nachbarn = [
            zellen[(i - 1) % n],
            zellen[(i + 1) % n],
            zellen[(i - 2) % n],
            zellen[(i + 2) % n],
            zellen[(i - 3) % n],
            zellen[(i + 3) % n],
        ]


# ============================================================
#  MICRO-HEXAGON (Regelkern)
# ============================================================

class MicroHexagon:
    def __init__(self):
        self.energy_decay = MICRO_ENERGY_DECAY
        self.hue_shift = MICRO_HUE_SHIFT
        self.brightness_drift = MICRO_BRIGHTNESS_DRIFT

    def apply(self, zelle):
        zelle.energy -= self.energy_decay
        zelle.hue = (zelle.hue + self.hue_shift) % 1.0
        zelle.brightness = max(0.0, min(1.0, zelle.brightness + self.brightness_drift))


# ============================================================
#  WELT AUFBAUEN
# ============================================================

def build_world(engine: Engine):

    # Ebene 1: Zellen
    engine.zellen = [
        Zelle(
            hue=random.uniform(0, 360),
            saturation=random.uniform(0.3, 0.8),
            brightness=random.uniform(0.3, 0.8),
            energy=random.uniform(0.4, 1.0)
        )
        for _ in range(WORLD_SIZE)
    ]

    # MicroHexagon zuweisen
    hexagon = SaturnHexagon()
    for z in engine.zellen:
        z.hex = hexagon
        z.in_cluster = False
        z.evolutionskeim = False

    # Hexagon-Layout
    set_initial_hex_neighbors(engine.zellen)

    # Geburtszustand wirklich berechnen, nicht setzen (Set 35, G). Vorher stand
    # hier nur `drift = 0.0` aus dem Konstruktor, und die einzige Bedingung, die
    # eine Geburt auslösen konnte (`drift > 0.4`), war damit exakt 0.0 — in
    # jeder Konfiguration. Erst nach dem Layout, weil beide Werte die Nachbarn
    # brauchen.
    for _z in engine.zellen:
        _z.berechne_drift()
        _z.berechne_harmonie()

    # Ebene 2: Cluster
    engine.cluster = []
    if ENABLE_CLUSTER:
        for i in range(0, len(engine.zellen), CLUSTER_SIZE):
            chunk = engine.zellen[i:i+CLUSTER_SIZE]
            if len(chunk) == CLUSTER_SIZE:
                engine.cluster.append(Cluster(chunk, engine=engine))

    # Ebene 3: Ring
    engine.ringe = []
    if ENABLE_RING:
        engine.ringe = [Ring(engine.cluster)]

    # Ebene 4: Sphere
    engine.spheren = []
    if ENABLE_SPHERE:
        engine.spheren = [Sphere(engine.ringe)]

    # Ebene 5: MetaSphere
    # NICHT neu erzeugen – Engine hat sie bereits!
    # Nur verdrahten, NICHT updaten. engine.metasphere.update() laesst ueber
    # Sphere -> Ring -> Cluster einmal z.update() ueber alle 990 Cluster-Zellen
    # laufen (gemessen: 990 Aufrufe, Zaehler am Objekt, 2026-10-02). build_world
    # BAUT die Welt; das Schrittieren gehoert in engine.step(). Die Aggregate
    # bleiben bis zum ersten Schritt auf ihren __init__-Werten stehen.
    if ENABLE_METASPHERE:
        engine.metasphere.spheren = engine.spheren

    # Ebene 6: UniverseNode
    # NICHT neu erzeugen – Engine hat sie bereits!
    # Aus demselben Grund nur verdrahten. update() ruft update_universe() und
    # schreibt in engine.harmonie_feld — and harmonie_feld wird direkt darunter
    # ohnehin mit GLOBAL_* ueberschrieben, der Rueckkopplungseffekt war also
    # schon vorher lost (gemessen: Stufe 8 aendert keine Zelle, 360 -> 360).
    if ENABLE_UNIVERSE:
        engine.universe.metasphere = engine.metasphere

    # Harmonie-Feld
    engine.harmonie_feld = {
        "global_harmonie": GLOBAL_HARMONIE_START,
        "global_drift": GLOBAL_DRIFT_START,
        "stoerimpulse": GLOBAL_STOER_START,
    }


# ============================================================
#  MAIN LOOP – COLORVERSE EVOLUTION
# ============================================================

def main(steps=500, delay=0.05):
    engine = Engine()
    build_world(engine)

    step_count = 0
    while True:

        engine.step()
        step_count += 1

        if ENABLE_UNIVERSE:
            engine.universe.update()

        # ---------------------------------------------
        # DEBUG-KONSOLE (alle 20 Schritte)
        # ---------------------------------------------
        if step_count % 20 == 0:

            # Sphere & MetaSphere & Universe sind garantiert vorhanden
            sphere = engine.spheren[0] if engine.spheren else None
            meta = engine.metasphere
            uni = engine.universe

            print("\n==================== DEBUG ====================")
            print(f"STEP: {step_count}")

            # Zellen (nur Durchschnitt, sonst zu viel)
            z_hue = sum(z.hue for z in engine.zellen) / len(engine.zellen)
            z_sat = sum(z.saturation for z in engine.zellen) / len(engine.zellen)
            z_bri = sum(z.brightness for z in engine.zellen) / len(engine.zellen)
            z_energy = sum(z.energy for z in engine.zellen) / len(engine.zellen)
            print(f"ZELLEN: hue={z_hue:.2f} sat={z_sat:.2f} bri={z_bri:.2f} energy={z_energy:.2f}")

            # Cluster
            if engine.cluster:
                c = engine.cluster[0]
                print(f"CLUSTER: hue={c.farbsatz_hue:.2f} sat={c.farbsatz_saturation:.2f} "
                      f"bri={c.farbsatz_brightness:.2f} harm={c.harmonie_avg:.2f} drift={c.drift_avg:.2f}")

            # Ring
            if engine.ringe:
                r = engine.ringe[0]
                print(f"RING: hue={r.hue_avg:.2f} sat={r.sat_avg:.2f} bri={r.bri_avg:.2f}")

            # Sphere
            if sphere:
                print(f"SPHERE: hue={sphere.hue_avg:.2f} sat={sphere.sat_avg:.2f} bri={sphere.bri_avg:.2f} "
                      f"energy={sphere.energy_avg:.2f} harm={sphere.harmonie_avg:.2f} drift={sphere.drift_avg:.2f}")

            # MetaSphere
            if meta:
                print(f"METASPHERE: hue={meta.hue_avg:.2f} sat={meta.sat_avg:.2f} bri={meta.bri_avg:.2f} "
                      f"energy={meta.energy_avg:.2f} harm={meta.harmonie_avg:.2f} drift={meta.drift_avg:.2f}")

            # Universe
            if uni:
                print(f"UNIVERSE: harm={uni.harmonie:.2f} drift={uni.drift:.2f} energy={uni.energy:.2f}")

            print("===============================================\n")

        # ---------------------------------------------
        # STOP-BEDINGUNG
        # ---------------------------------------------
        if steps is not None and step_count >= steps:
            break

        # ---------------------------------------------
        # WICHTIG: sleep gehört NICHT in den Debug-Block
        # ---------------------------------------------
        time.sleep(delay)



if __name__ == "__main__":
    main(steps=100, delay=0.05)

