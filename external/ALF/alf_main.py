# alf_main.py

import time
from engine import Engine
from saturings import build_world
from EML.eml import read_world, interpret, apply
from Urasil_light.core.alf_bridge import UrasilAgent

def alf_loop(steps=500, delay=0.05):
    engine = Engine()
    build_world(engine)

    agent = UrasilAgent()

    for step in range(steps):
        # 1. Welt weiterentwickeln
        engine.step()
        if hasattr(engine, "universe"):
            engine.universe.update()

        # 2. Weltzustand lesen
        world_state = read_world(engine)

        # 3. Bedeutung erzeugen (EML)
        meaning = interpret(world_state)

        # 4. Urasil entscheiden lassen
        decision = agent.decide(meaning)

        # 5. Entscheidung in die Welt zurückspeisen
        apply(engine, decision)

        # 6. (optional) Debug / Logging
        if step % 20 == 0:
            print(f"[STEP {step}] meaning={meaning} decision={decision}")

        time.sleep(delay)


if __name__ == "__main__":
    alf_loop(steps=200, delay=0.05)

