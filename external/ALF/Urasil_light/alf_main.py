# alf_main.py
# Artificial Life Framework — vereinigter Loop
#
# Pipeline:
#   Colorverse → EML → Urasil → EML → Colorverse → …

import time
import sys
import os

# Pfade setzen
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Urasil_light"))

from engine import Engine
from saturings import build_world
from EML.eml import read_world, interpret, apply
from Urasil_light.core.alf_bridge import UrasilAgent


def alf_loop(steps=500, delay=0.05):

    print("=" * 50)
    print("  ALF — Artificial Life Framework")
    print("  Colorverse + EML + Urasil")
    print("=" * 50)

    # 1. Colorverse initialisieren
    engine = Engine()
    build_world(engine)
    print("[ALF] Colorverse bereit.")

    # 2. Urasil-Agent initialisieren (persistent)
    agent = UrasilAgent()
    print("[ALF] Urasil bereit.")
    print("[ALF] Loop startet...\n")

    for step in range(steps):

        # ── 1. Welt weiterentwickeln ──────────────────────
        engine.step()

        # ── 2. Weltzustand lesen ──────────────────────────
        world_state = read_world(engine)

        # ── 3. EML: Zustand → Bedeutung ──────────────────
        meaning = interpret(world_state)

        # ── 4. Urasil: Bedeutung → Entscheidung ──────────
        decision = agent.decide(meaning)

        # ── 5. EML: Entscheidung → Weltmodulation ────────
        apply(engine, decision)

        # ── 6. Debug-Ausgabe ──────────────────────────────
        if step % 20 == 0:
            freq = agent.freq_engine.snapshot()
            modus = agent.zyklus.matrix()
            print(f"\n[ALF STEP {step}]")
            print(f"  Universe:  {world_state['universe']['modus']}")
            print(f"  Meaning:   chaos={meaning.get('chaos')} stabil={meaning.get('stabil')} drift={meaning.get('drift_hoch')}")
            print(f"  Zyklus:    {modus['grundmodus']} / {modus['stimmung']} / {modus['fokus']}")
            print(f"  Decision:  {decision}")
            print(f"  Freq:      AF={freq.get('FrequencyType.AF', 0):.2f} PF={freq.get('FrequencyType.PF', 0):.2f} RF={freq.get('FrequencyType.RF', 0):.2f}")

        time.sleep(delay)

    print("\n[ALF] Loop beendet.")


if __name__ == "__main__":
    alf_loop(steps=200, delay=0.05)
