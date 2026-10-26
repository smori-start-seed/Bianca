# engine.py – Colorverse Evolution Engine
from config import *
from Cluster import Cluster
from Ring import Ring
from Sphere import Sphere
from MetaSphere import MetaSphere
from UniverseNode import UniverseNode

class Engine:
    def __init__(self):
        self.zellen = []
        self.cluster = []
        self.ringe = []
        self.spheren = []

        self.metasphere = MetaSphere(self.spheren)

        self.harmonie_feld = {
            "global_harmonie": 0.87,
            "global_drift": 0.4,
            "stoerimpulse": 0.515,
        }

        self.universe = UniverseNode(self, self.metasphere)
        self.step_count = 0


    def hexagon_fluidity(self):
        n = len(self.zellen)

        for idx, z in enumerate(self.zellen):

            # Cluster-Zellen bleiben stabil
            if z.in_cluster:
                continue

            # Fluidität abhängig von Drift + Harmonie + Energie
            if z.drift > 0.2 and z.energy > 0.3:

                # Fluiditätsfaktor: Drift + Disharmonie
                shift = int((z.drift + (1 - z.harmonie)) * 6)
                shift = (shift + idx) % n

                z.nachbarn = [
                    self.zellen[(idx - 1 + shift) % n],
                    self.zellen[(idx + 1 + shift) % n],
                    self.zellen[(idx - 2 + shift) % n],
                    self.zellen[(idx + 2 + shift) % n],
                    self.zellen[(idx - 3 + shift) % n],
                    self.zellen[(idx + 3 + shift) % n],
                ]

    # =====================================================================
    #  HAUPT-SCHRITT DER EVOLUTION
    # =====================================================================
    def step(self):
    
        self.step_count += 1

        # Die Sphere-Tuer (Set 36): das freie Feld als wandernde Hue-Welle.
        # Sie steht VOR der Saatpruefung — hinten gemessen nur 90 → 117.
        # Set 38: der Wuerfel ist weg; die Saat entscheidet am Wellenkamm.
        if self.spheren:
            self.spheren[0].rueckkopplung_ins_evolutionsfeld(self.zellen)

        # Freie Zellen → Evolutionskeime markieren, VOR den Update-Durchlaeufen:
        # nach `stabilisierung` ist die Varianz um Faktor 0.21 gefallen
        # (gemessen) und die Tuer ist zu. Der Ort ist der Kopf von `step()`,
        # nicht das Ende — sonst saet die Welt nur einmal.
        freie = [z for z in self.zellen if not z.in_cluster]
        for z in freie:
            z.evolutionskeim = (
                z.drift > 0.4 and
                z.energy > 0.6 and
                z.harmonie < 0.5 and z.hue < 180.0
            )

        # 1. Zellen updaten
        for z in self.zellen:
            z.update()

        # 2. Cluster updaten
        for c in self.cluster:
            c.update()

        # Set 39: in_cluster == Mitglied in irgendeinem Cluster.
        gehalten = set()
        for c in self.cluster:
            gehalten.update(id(z) for z in c.zellen)
        for z in self.zellen:
            if z.in_cluster and id(z) not in gehalten:
                z.in_cluster = False
    
        # 3. Ringe updaten
        for r in self.ringe:
            r.update()

        # 4. Sphären updaten
        for s in self.spheren:
            s.update()

        # 5. MetaSphere updaten
        if self.metasphere:
            self.metasphere.update()

        # 6. UniverseNode updaten
        if ENABLE_UNIVERSE and self.universe:
            self.universe.update_universe()

        # 7. Hexagon-Fluidity (Dynamische Nachbarschaften)
        self.hexagon_fluidity()

        # 8. Optional: Wander-System
        # self.hexagon_wander()

        # ===================== EVOLUTIONSSYSTEM ==============
        # =====================================================

        #------------------------------------------------------
        # Harmonie-Feld aktualisieren
        #------------------------------------------------------
        if self.zellen:
            self.harmonie_feld["global_harmonie"] = (
                sum(z.harmonie for z in self.zellen) / len(self.zellen)
            )
            self.harmonie_feld["global_drift"] = (
                sum(z.drift for z in self.zellen) / len(self.zellen)
            )

        # ---------------------------------------------------------
        # 3er-Störimpulse erzeugen
        # ---------------------------------------------------------
        keime = [z for z in freie if z.evolutionskeim]
        dreier = [
            keime[i:i+3]
            for i in range(0, len(keime), 3)
            if len(keime[i:i+3]) == 3
        ]

        for gruppe in dreier:
            for z in gruppe:
                z.energy += 0.1
                z.drift += 0.05
            self.harmonie_feld["stoerimpulse"] += 0.2

        # ---------------------------------------------------------
        # Harmonie-Feld-Resonanz auf alle Zellen anwenden
        # ---------------------------------------------------------
        for z in self.zellen:
            z.drift += self.harmonie_feld["stoerimpulse"] * 0.01
            z.energy += (1 - self.harmonie_feld["global_harmonie"]) * 0.005

        # ---------------------------------------------------------
        # automatische Clusterbildung aus Evolutionskeimen
        # ---------------------------------------------------------
        neue_cluster = []
        keime = [z for z in self.zellen if z.evolutionskeim and not z.in_cluster]

        # Set 40: Cluster koennen aus 1..11 Samen bestehen (Moleküle).
        fusionsenergie = 0.0
        if isinstance(self.harmonie_feld, dict):
            fusionsenergie = self.harmonie_feld.get("fusionsenergie", 0.0)

        i = 0
        while i < len(keime):
            rest = len(keime) - i
            if rest >= 11:
                chunk = keime[i:i+11]
                i += 11
            elif rest >= 1:
                chunk = keime[i:i+rest]
                i += rest
            else:
                break
            if len(chunk) >= 1:
                c = Cluster(chunk, engine=self)
                neue_cluster.append(c)
                for z in chunk:
                    z.in_cluster = True
                    z.evolutionskeim = False
                    z.energy *= 0.5
                    z.drift *= 0.2
                    z.harmonie = 1.0
                self.harmonie_feld["stoerimpulse"] *= max(0.3, 0.5 - fusionsenergie * 0.01)

        if isinstance(self.harmonie_feld, dict):
            self.harmonie_feld["fusionsenergie"] = max(0.0, fusionsenergie * 0.9)

        self.cluster.extend(neue_cluster)
        print(f"[ENGINE] step={self.step_count} harm={self.harmonie_feld['global_harmonie']:.2f} drift={self.harmonie_feld['global_drift']:.2f} stoer={self.harmonie_feld['stoerimpulse']:.2f}")
