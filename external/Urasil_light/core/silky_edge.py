class SilkyEdge:
    def __init__(self, identity, zyklus):
        self.identity = identity
        self.zyklus = zyklus

    def veredeln(self, rohantwort, bedeutung):
        modus = self.zyklus.matrix()

        if modus["stimmung"] == "neutral":
            return rohantwort
        elif modus["stimmung"] == "warm":
            return f"{rohantwort} — ich spüre da etwas Warmes."
        else:
            return f"{rohantwort} — intuitiv betrachtet…"
