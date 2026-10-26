# Urasil_light/core/alf_bridge.py
# UrasilAgent — persistente Instanz für den ALF-Loop
#
# Löst das Bug-Problem von runtime/main.py:
# - Identity wird EINMAL geladen und gehalten
# - Zyklus läuft kontinuierlich weiter
# - Kein user_input() — autonome decide() Methode
# - Frequenzen aus EML direkt verarbeitet

from identity import Identity
from zyklus import Zyklus
from seed import Seed
from silky_edge import SilkyEdge
from erfahrung import Erfahrung
from interpretation import Interpretation
from rueckmeldung import Rueckmeldung
from frequency import FrequencyEngine, Frequency, FrequencyType


class UrasilAgent:
    def __init__(self):
        # Einmalig laden — bleibt für den gesamten ALF-Loop erhalten
        self.identity = Identity.load()
        self.zyklus = Zyklus(self.identity.data)
        self.freq_engine = FrequencyEngine()

        # Komponenten initialisieren
        self.interpretation = Interpretation(self.identity, self.zyklus)
        self.erfahrung = Erfahrung(self.identity, self.zyklus)
        self.seed = Seed(self.identity, self.zyklus)
        self.silky = SilkyEdge(self.identity, self.zyklus)
        self.rueck = Rueckmeldung(self.identity, self.zyklus)

        self.step_count = 0

    def decide(self, meaning: dict) -> dict:
        """
        Kernmethode für den ALF-Loop.
        Nimmt EML-Bedeutung, gibt Entscheidung zurück.
        """
        self.step_count += 1

        # 1. Frequenzen aus der Welt aufnehmen
        self._apply_frequencies(meaning)

        # 2. Bedeutung in Urasil-Text übersetzen
        text = self._meaning_to_text(meaning)

        # 3. Interpretation durch Zyklus-Modus
        bedeutung = self.interpretation.verarbeite(text)

        # 4. Erfahrung speichern (wenn reif)
        self.erfahrung.speichern(bedeutung)

        # 5. Antwort generieren
        rohantwort = self.seed.generiere(bedeutung)
        antwort = self.silky.veredeln(rohantwort, bedeutung)

        # 6. Reflexion
        self.rueck.verarbeite(antwort)

        # 7. Zyklus fortschreiben (alle 10 Schritte)
        if self.step_count % 10 == 0:
            self.zyklus.fortschritt()
            self.zyklus.speichern(self.identity.data)
            Identity.save(self.identity.data)

        # 8. Entscheidung zurückgeben
        return self._build_decision(meaning)

    def _apply_frequencies(self, meaning: dict):
        """Frequenzen aus EML in FrequencyEngine einspeisen."""
        af_map = {"erregt": 0.3, "neutral": 0.0, "ruhig": -0.1}
        pf_map = {"aktiv": 0.2, "stabil": 0.0, "träge": -0.1}
        rf_map = {"offen": -0.1, "balanciert": 0.0, "reguliert": 0.2}

        self.freq_engine.apply(Frequency(
            type=FrequencyType.AF,
            value=af_map.get(meaning.get("af_state", "neutral"), 0.0)
        ))
        self.freq_engine.apply(Frequency(
            type=FrequencyType.PF,
            value=pf_map.get(meaning.get("pf_state", "stabil"), 0.0)
        ))
        self.freq_engine.apply(Frequency(
            type=FrequencyType.RF,
            value=rf_map.get(meaning.get("rf_state", "balanciert"), 0.0)
        ))

    def _meaning_to_text(self, meaning: dict) -> str:
        """Übersetzt EML-Bedeutung in Text für Interpretation."""
        uni = meaning.get("universe_modus", "sanft")
        af  = meaning.get("af_state", "neutral")
        pf  = meaning.get("pf_state", "stabil")

        if meaning.get("chaos"):
            return f"Die Welt ist im Chaos. AF={af}, PF={pf}, Universe={uni}"
        elif meaning.get("stabil"):
            return f"Die Welt ist stabil. AF={af}, PF={pf}, Universe={uni}"
        else:
            return f"Die Welt ist fragil. AF={af}, PF={pf}, Universe={uni}"

    def _build_decision(self, meaning: dict) -> dict:
        """
        Baut die Entscheidung für EML.apply() auf Basis von
        Weltzustand + Frequenzzustand + Zyklus-Modus.
        """
        freq = self.freq_engine.snapshot()
        modus = self.zyklus.matrix()
        decision = {}

        # Chaos → Harmonie erhöhen, Störung dämpfen
        if meaning.get("chaos"):
            decision["increase_harmony"] = True
            decision["dampen_noise"] = True

        # Hoher Drift → regulieren
        if meaning.get("drift_hoch"):
            decision["decrease_drift"] = True
            decision["boost_rf"] = True

        # Energie niedrig → Impuls geben
        if meaning.get("energie_low"):
            decision["inject_noise"] = True
            decision["boost_af"] = True

        # Universe chaotisch → Performance hochfahren
        if meaning.get("universe_modus") == "chaotisch":
            decision["increase_drift"] = True

        # Zyklus-Modus beeinflusst Entscheidungsgewichtung
        if modus["grundmodus"] == "klarheit":
            # Klarheit bevorzugt Stabilisierung
            decision["dampen_noise"] = True
        elif modus["grundmodus"] == "kreativ":
            # Kreativ bevorzugt leichten Impuls
            if not meaning.get("chaos"):
                decision["inject_noise"] = True

        return decision
