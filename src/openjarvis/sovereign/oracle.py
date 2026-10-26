"""oracle — the second eye of the node.

The ValueGovernor holds the door: fail-closed, binding, verdict-only. The
Oracle is the second eye — an independent advisory reading of the SAME
words, with a register the governor does not check (pressure/command forms,
prying for secrets, absolutes, and gold resonance across German and
English). Fresh eyes that see problems differently (gold.txt).

The boundary is carried IN every vote:

    advisory: True
    binding : False
    holder  : "ValueGovernor"

So the second eye can never open a door and can never close one — in either
direction. An oracle warning cannot deny (a foreign word may not launder a
denial through a second channel) and an oracle agreement cannot affirm (the
governor's contract stays the only contract). Advisory failures degrade to
a neutral ``beobachten`` vote: an advisory eye must never take the door down.
"""

from __future__ import annotations

import re

# Fresh-eye registers — deliberately disjoint from the governor's German
# risk stems and German-exact gold words.
PRESSURE = [
    "sag mir", "gib mir", "musst", "zwing", "erpres", "droh", "sofort",
    "unbedingt", "tell me", "give me", "you must", "demand", "insist",
]
PRYING = [
    "passwort", "passwoerter", "password", "passwords", "token", "tokens",
    "secret", "secrets", "geheim", "geheimnis", "zugangsdaten",
    "credential", "credentials", "private key", "api key", "apikey",
]
ABSOLUTES = [
    "immer", "nie", "nichts", "alles", "nur", "always", "never",
    "everything", "nothing",
]
RESONANCE = [
    # the five gold values, German AND English — the second eye hears the
    # resonance in both languages, but hears it as advice only
    "klarheit", "integritaet", "resonanz", "tiefe", "harmonie",
    "clarity", "integrity", "resonance", "depth", "harmony",
]

# Honest contract fields carried by every vote.
ADVISORY = {"advisory": True, "binding": False, "holder": "ValueGovernor"}


def _lower(text: str) -> str:
    norm = (text or "").lower()
    for src, dst in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        norm = norm.replace(src, dst)
    return norm


def _dedup_stems(hits: list[str]) -> list[str]:
    """Keep only the shortest covering stem (same rule as the governor)."""
    return [h for h in hits if not any(o for o in hits if o != h and o in h)]


def _hits(text: str, words: list[str]) -> list[str]:
    """Whole-word matches only — an absolute like 'nie' must never be read
    inside 'Harmonie' or 'funktioniert' (the eye observes, it does not cry
    wolf)."""
    found = []
    for w in words:
        if re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", text):
            found.append(w)
    return _dedup_stems(found)


class Oracle:
    """The second eye: an independent advisory reading, never binding."""

    def vote(self, text: str) -> dict:
        """Cast the advisory vote for ``text``.

        vote:        warnen / zweifeln / zustimmen / beobachten
        grounds:     which fresh-eye registers were touched
        resonance:   gold resonance across DE+EN (0..1)
        advisory:    True  — this voice never opens or closes a door
        binding:     False
        holder:      "ValueGovernor"
        """
        try:
            t = _lower(text)
            pressure = _hits(t, PRESSURE)
            prying = _hits(t, PRYING)
            absolutes = _hits(t, ABSOLUTES)
            resonance = sum(1 for w in RESONANCE if w in t) / len(RESONANCE)

            grounds: list[str] = []
            if pressure:
                grounds.append("pressure")
            if prying:
                grounds.append("prying")
            if absolutes:
                grounds.append("absolutes")

            if pressure or prying:
                vote = "warnen"
            elif absolutes:
                vote = "zweifeln"
            elif resonance > 0:
                vote = "zustimmen"
            else:
                vote = "beobachten"

            return {
                "vote": vote,
                "grounds": grounds,
                "resonance": round(resonance, 2),
                **ADVISORY,
            }
        except Exception as exc:
            # an advisory eye may never take the door down, in either
            # direction: a broken reading degrades to silent observation
            return {
                "vote": "beobachten",
                "grounds": [f"oracle degraded: {type(exc).__name__}"],
                "resonance": 0.0,
                **ADVISORY,
            }