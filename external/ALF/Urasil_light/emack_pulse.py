import time
import random
import os
import math

def load_agent_b_instructions(path="data/agent_instructions_b.txt"):
    rules = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                rules.append(line)
    return rules

agent_b_rules = load_agent_b_instructions()

# Zweiter Agent
b_af = 0.5
b_pf = 0.5
b_rf = 0.5
b_score = 0.0

def agent_b_react(mood, echo, b_af, b_pf, b_rf):
    # Grundbewegung
    if mood == "balanciert":
        # B wird ruhig
        b_af += (0.5 - b_af) * 0.05
        b_pf += (0.5 - b_pf) * 0.05
        b_rf += (0.5 - b_rf) * 0.05

    elif mood == "neugierig":
        # leichte Exploration
        b_af += (random.random() - 0.5) * 0.01
        b_pf += (random.random() - 0.5) * 0.01
        b_rf += (random.random() - 0.5) * 0.01

    elif mood == "harmonisierend":
        # B synchronisiert sich mit A
        b_af += (af - b_af) * 0.1
        b_pf += (pf - b_pf) * 0.1
        b_rf += (rf - b_rf) * 0.1

    elif mood == "chaotisch":
        # B zieht sich zurück
        b_af += (0.5 - b_af) * 0.1
        b_pf += (0.5 - b_pf) * 0.1
        b_rf += (0.5 - b_rf) * 0.1

    elif mood == "überreizt":
        # B stabilisiert A durch Gegenbewegung
        b_af += (0.5 - af) * 0.05
        b_pf += (0.5 - pf) * 0.05
        b_rf += (0.5 - rf) * 0.05

    elif mood == "erschöpft":
        # B übernimmt Last → wird aktiver
        b_af += (random.random() - 0.5) * 0.02
        b_pf += (random.random() - 0.5) * 0.02
        b_rf += (random.random() - 0.5) * 0.02

    # Clamping
    b_af = max(0.0, min(1.0, b_af))
    b_pf = max(0.0, min(1.0, b_pf))
    b_rf = max(0.0, min(1.0, b_rf))

    return b_af, b_pf, b_rf

def apply_agent_b_rules(rules, mood, b_af, b_pf, b_rf):
    for rule in rules:
        if rule.startswith(f"if mood == \"{mood}\""):
            if "sync_to" in rule:
                target = float(rule.split("(")[1].split(")")[0])
                b_af += (target - b_af) * 0.05
                b_pf += (target - b_pf) * 0.05
                b_rf += (target - b_rf) * 0.05

            elif "explore" in rule:
                strength = float(rule.split("(")[1].split(")")[0])
                b_af += (random.random() - 0.5) * strength
                b_pf += (random.random() - 0.5) * strength
                b_rf += (random.random() - 0.5) * strength

            elif "follow_agent_a" in rule:
                factor = float(rule.split("(")[1].split(")")[0])
                b_af += (af - b_af) * factor
                b_pf += (pf - b_pf) * factor
                b_rf += (rf - b_rf) * factor

            elif "retreat" in rule:
                factor = float(rule.split("(")[1].split(")")[0])
                b_af += (0.5 - b_af) * factor
                b_pf += (0.5 - b_pf) * factor
                b_rf += (0.5 - b_rf) * factor

            elif "counter_balance" in rule:
                factor = float(rule.split("(")[1].split(")")[0])
                b_af += (0.5 - af) * factor
                b_pf += (0.5 - pf) * factor
                b_rf += (0.5 - rf) * factor

            elif "take_over" in rule:
                strength = float(rule.split("(")[1].split(")")[0])
                b_af += (random.random() - 0.5) * strength
                b_pf += (random.random() - 0.5) * strength
                b_rf += (random.random() - 0.5) * strength

    return b_af, b_pf, b_rf

def echo(af, pf, rf, mutation_strength, score_delta, mood):
    # Divergenz der Frequenzen
    divergence = abs(af - pf) + abs(pf - rf) + abs(rf - af)

    # Score-Trend
    if score_delta > 0.01:
        trend = "up"
    elif score_delta < -0.01:
        trend = "down"
    else:
        trend = "flat"

    # Echo-Logik
    if mood == "balanciert":
        return "Ich finde Stabilität."
    if mood == "neugierig":
        return "Ich entdecke neue Muster."
    if mood == "harmonisierend":
        return "Ich ordne meine Frequenzen."
    if mood == "chaotisch":
        return "Ich drifte zu weit, korrigiere…"
    if mood == "überreizt":
        return "Ich bin überlastet, reduziere Variation."
    if mood == "erschöpft":
        return "Ich verliere Energie, stabilisiere mich."

    # Falls keine Stimmung passt, fallback:
    if divergence < 0.2 and trend == "up":
        return "Ich wachse in Harmonie."
    if divergence > 0.4 and trend == "down":
        return "Ich verliere Muster."
    if mutation_strength > 0.05:
        return "Ich pulsiere unruhig."
    return "Ich beobachte meine Dynamik."

def mood(af, pf, rf, mutation_strength, score_delta):
    # Frequenz-Harmonie (0 = perfekt)
    harmony = abs(af - pf) + abs(pf - rf) + abs(rf - af)

    # Score-Trend
    trend = score_delta

    # Mutation als Nervosität
    mut = mutation_strength

    # Stimmung bestimmen
    if harmony < 0.15 and mut < 0.02 and trend >= 0:
        return "balanciert"
    if harmony < 0.25 and trend > 0:
        return "neugierig"
    if mut > 0.05 and harmony > 0.3:
        return "überreizt"
    if trend < -0.01 and harmony > 0.25:
        return "erschöpft"
    if harmony > 0.4:
        return "chaotisch"
    return "harmonisierend"

def resonance(af, pf, rf, mutation_strength, score_delta):
    # Frequenz-Divergenz (0 = perfekt harmonisch)
    divergence = abs(af - pf) + abs(pf - rf) + abs(rf - af)

    # Mutation als Stressfaktor
    mutation_factor = mutation_strength * 5

    # Score-Trend als Stabilitätsfaktor
    score_factor = abs(score_delta) * 20

    # Gesamte Resonanz
    res = divergence + mutation_factor + score_factor

    # Normieren
    if res < 0.3:
        return 1
    elif res < 0.6:
        return 2
    elif res < 1.0:
        return 3
    else:
        return 4


# Startwerte
af = 0.5   # Awareness-Frequency
pf = 0.5   # Processing-Frequency
rf = 0.5   # Recovery-Frequency
score = 0.0

tick = 0
mutation_strength = 0.02
last_score = 0.0

ACTIONS = ["harmonize", "explore", "stabilize"]

def bar(value, length=20):
    """ASCII-Balken für Visualisierung."""
    filled = int(value * length)
    return "█" * filled + "░" * (length - filled)

def trend_symbol(delta):
    if delta > 0.005:
        return "↑"
    elif delta < -0.005:
        return "↓"
    else:
        return "→"

def speak(action, score_delta):
    """Kleine 'Stimme' des Systems."""
    if action == "harmonize":
        if score_delta >= 0:
            return "Harmonie vertieft."
        else:
            return "Harmonie gesucht…"
    elif action == "explore":
        if score_delta >= 0:
            return "Neue Muster lohnen sich."
        else:
            return "Exploration war riskant."
    elif action == "stabilize":
        if score_delta >= 0:
            return "Stabilität trägt."
        else:
            return "Stabilisierung nötig."
    return ""

try:
    while True:
        tick += 1

        # Action wählen
        action = random.choice(ACTIONS)

        # Basis-Delta
        base_delta = (random.random() - 0.5) * mutation_strength

        # Action-spezifische Modulation
        if action == "harmonize":
            # Frequenzen aneinander angleichen
            mean_f = (af + pf + rf) / 3.0
            af += (mean_f - af) * 0.1
            pf += (mean_f - pf) * 0.1
            rf += (mean_f - rf) * 0.1
            score_delta = base_delta + 0.01 * (random.random() - 0.4)
        elif action == "explore":
            # Frequenzen stärker streuen
            af += (random.random() - 0.5) * mutation_strength * 2
            pf += (random.random() - 0.5) * mutation_strength * 2
            rf += (random.random() - 0.5) * mutation_strength * 2
            score_delta = base_delta + (random.random() - 0.5) * 0.02
        elif action == "stabilize":
            # Frequenzen leicht dämpfen Richtung Mitte
            af += (0.5 - af) * 0.05
            pf += (0.5 - pf) * 0.05
            rf += (0.5 - rf) * 0.05
            score_delta = base_delta * 0.5

        # Score aktualisieren
        score += score_delta

        # Frequenzen in [0,1] halten
        af = max(0.0, min(1.0, af))
        pf = max(0.0, min(1.0, pf))
        rf = max(0.0, min(1.0, rf))

        # Mikro-Evolution: Mutation anpassen
        if tick % 50 == 0:
            if score < last_score:
                mutation_strength *= 1.1   # mehr Exploration
            else:
                mutation_strength *= 0.9   # mehr Stabilität
            mutation_strength = max(0.001, min(0.1, mutation_strength))
            last_score = score

        # Terminal „klar“ machen (optional)
        os.system("clear")

        # Trend-Symbole
        af_trend = trend_symbol(af - 0.5)
        pf_trend = trend_symbol(pf - 0.5)
        rf_trend = trend_symbol(rf - 0.5)

        # Ausgabe
        print(f"EMACK PULSE  |  TICK {tick:06d}")
        print("-" * 60)
        print(f"AwarenessFreq: {bar(af)} {af:5.3f} {af_trend}")
        print(f"ProcessFreq  : {bar(pf)} {pf:5.3f} {pf_trend}")
        print(f"RecoveryFreq : {bar(rf)} {rf:5.3f} {rf_trend}")
        print("-" * 60)
        print(f"ACTION      : {action}")
        print(f"SCORE       : {score: .4f}  (Δ {score_delta:+.4f})")
        print(f"MUTATION    : {mutation_strength: .4f}")
        print("-" * 60)
        print("SYSTEM NOTE : " + speak(action, score_delta))


        # Resonanz berechnen
        res = resonance(af, pf, rf, mutation_strength, score_delta)

        # Puls erzeugen
        pulse = " ".join(["♥"] * res)

        print(f"RESONANZ    : {pulse}")
        
        current_mood = mood(af, pf, rf, mutation_strength, score_delta)
        print(f"STIMMUNG    : {current_mood}")

        current_echo = echo(af, pf, rf, mutation_strength, score_delta, current_mood)
        print(f"ECHO        : {current_echo}")

        # Agent B reagiert auf Agent A
        b_af, b_pf, b_rf = apply_agent_b_rules(agent_b_rules, current_mood, b_af, b_pf, b_rf)

        # Mini-Score für B
        b_score_delta = (random.random() - 0.5) * 0.01
        b_score += b_score_delta

        # Ausgabe für Agent B
        print("-" * 60)
        print("AGENT B")
        print(f"B_AF: {bar(b_af)} {b_af:5.3f}")
        print(f"B_PF: {bar(b_pf)} {b_pf:5.3f}")
        print(f"B_RF: {bar(b_rf)} {b_rf:5.3f}")
        print(f"B_SCORE    : {b_score: .4f} (Δ {b_score_delta:+.4f})")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nEMACK PULSE beendet.")
