"""
ALF Global Link (as the additive Sovereign overlay)
===================================================
Connects Bianca to the ALF ecosystem:

  1. ALFCapabilityProfile : detect a module's capabilities via file-presence
                            (llm_bridge / werte_teilen => "advanced", else "classic").
  2. CycleStateReader     : read the REAL Urasil_light zyklus from identity.json
                            (sonne/mond/tag -> grundmodus/stimmung/fokus).
  3. ValueGovernor        : value-driven governance powered by gold.txt.
                            Verdicts: frei / vorsichtig / symbolisch / zurueckhalten.
  4. LinkOrchestrator     : composes the above into a governed lifecycle.

Ported from OpenJarvis/kernel/link.py. ALF paths are configurable via
environment variables (BIANCA_ALF_ROOT / BIANCA_MODULE_ROOT) and default to
the repositories layout on this machine.

Design principle: every layer degrades gracefully, so the Link NEVER blocks on
missing ALF data — it annotates and governs.
"""

import importlib.util
import json
import os
from pathlib import Path


def default_alf_root() -> Path:
    alf = os.environ.get("BIANCA_ALF_ROOT")
    if alf:
        return Path(alf)
    # Prefer local merged copy first
    local = Path(__file__).resolve().parents[3] / "external" / "ALF"
    if local.exists():
        return local
    return Path("/home/sam/Repos/ALF")


def default_module_root() -> Path:
    return Path(os.environ.get("BIANCA_MODULE_ROOT", str(default_alf_root() / "Urasil_light")))


# ---------------------------------------------------------------------------
# 1. ALFCapabilityProfile
# ---------------------------------------------------------------------------

class ALFCapabilityProfile:
    """
    Detects what an ALF module can do by checking for feature files.

    The ALF/nature repository is NOT a git repository, so 'branch-awareness' is
    implemented as file-presence detection:
      - llm_bridge.py + werte_teilen.py present  -> mode "advanced"
      - otherwise                                 -> mode "classic"
    """

    FEATURE_FILES = ("llm_bridge.py", "werte_teilen.py", "backends.py")

    def __init__(self, module_root: Path):
        self.module_root = Path(module_root)

    def has(self, filename: str) -> bool:
        # Feature files may live at the module root OR under core/
        return (
            (self.module_root / filename).exists()
            or (self.module_root / "core" / filename).exists()
        )

    def profile(self) -> dict:
        present = [f for f in self.FEATURE_FILES if self.has(f)]
        return {
            "mode": "advanced" if self.has("llm_bridge.py") else "classic",
            "feature_files": present,
            "llm_bridge": self.has("llm_bridge.py"),
            "werte_teilen": self.has("werte_teilen.py"),
        }


# ---------------------------------------------------------------------------
# 2. CycleStateReader
# ---------------------------------------------------------------------------

class CycleStateReader:
    """
    Reads the REAL Urasil_light cycle state from identity.json.

    The zyklus module is loadable via direct file-import (verified), but the
    package __init__ has a broken dependency (core.simulation). We therefore
    load it file-directly and fall back to reading identity.json if even that
    fails. Worst case we synthesize a deterministic default state.
    """

    DEFAULT_STATE = {
        "sonne": 0, "mond": 0, "tag": 0,
        "grundmodus": "klarheit", "stimmung": "neutral", "fokus": "dialog",
    }

    def __init__(self, urasil_root: Path):
        self.urasil_root = Path(urasil_root)

    # -- helpers ------------------------------------------------------------

    def _load_zyklus_class(self):
        """Load Zyklus via file path, bypassing the broken package __init__."""
        zyklus_path = self.urasil_root / "core" / "zyklus.py"
        if not zyklus_path.exists():
            return None
        try:
            spec = importlib.util.spec_from_file_location("oj_zyklus", zyklus_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.Zyklus
        except Exception:
            return None

    def _identity_dict(self) -> dict:
        identity_path = self.urasil_root / "data" / "identity.json"
        if not identity_path.exists():
            return {}
        try:
            with open(identity_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    # -- public API ---------------------------------------------------------

    def read(self) -> dict:
        # 1) Try the real Zyklus class with real identity data.
        Zyklus = self._load_zyklus_class()
        identity = self._identity_dict()
        if Zyklus and identity.get("zyklus"):
            try:
                z = Zyklus(identity)
                state = {"sonne": z.sonne, "mond": z.mond, "tag": z.tag}
                state.update(z.matrix())
                return state
            except Exception:
                pass

        # 2) Fallback: raw identity zyklus counters.
        if identity.get("zyklus"):
            z = identity["zyklus"]
            return {
                "sonne": z.get("sonne", 0),
                "mond": z.get("mond", 0),
                "tag": z.get("tag", 0),
                "grundmodus": "unbekannt",
                "stimmung": "neutral",
                "fokus": "unbekannt",
            }

        # 3) Deterministic default.
        return dict(self.DEFAULT_STATE)


# ---------------------------------------------------------------------------
# 3. ValueGovernor
# ---------------------------------------------------------------------------

class ValueGovernor:
    """
    Value-driven governance built on the real gold.txt manifesto.

    Gold core values (per AGENTS.md): Klarheit, Integrität, Resonanz, Tiefe,
    Harmonie. The governor scores a task request against these ideals and
    returns a verdict:
        frei           : aligned with gold values
        vorsichtig     : neutral / needs care
        symbolisch     : low-risk, symbolic action
        zurueckhalten  : conflicts with gold values (high risk)
    """

    #: The five gold values, each in every language the UI speaks.
    #:
    #: **This is a dict of five values, not a list of ten words.** That
    #: distinction is the whole governance content of the change, so it is
    #: worth being explicit about what it is not:
    #:
    #: A flat list of ten would make ``len()`` — the denominator of
    #: ``_alignment_score`` — equal ten, so *four* English gold words would
    #: reach the 0.4 threshold that *two* German ones reach today. Naming all
    #: five values in English would score 1.0 by accident of counting words
    #: instead of values. That is a loosening, and it would have been
    #: invisible in the diff, because the diff would have looked like a
    #: translation.
    #:
    #: As a dict, ``_alignment_score`` counts **groups matched**, not words
    #: found, so the formula, the denominator and all four thresholds are
    #: exactly what they were. ``klarheit`` and ``clarity`` are two spellings
    #: of one value and score the same single hit. The vocabulary widens; the
    #: arithmetic does not. Verified across 50 measured requests by
    #: ``scripts/measure_gold_widening.py`` — see the diary, set 26.
    #:
    #: One equivalent per language, deliberately. Stems ("klar", "deep",
    #: "clear") are *not* translations, they are widenings, and widening is
    #: the owner's decision to make argued from a measurement — not something
    #: to smuggle in under the heading of i18n.
    #:
    #: ``RISK_TERMS`` below is a different matter entirely and is **untouched**
    #: by this change; widening it remains escalated and undecided.
    GOLD_VALUES: dict[str, tuple[str, ...]] = {
        "klarheit": ("klarheit", "clarity"),
        "integritaet": ("integritaet", "integrity"),
        "resonanz": ("resonanz", "resonance"),
        "tiefe": ("tiefe", "depth"),
        "harmonie": ("harmonie", "harmony"),
    }

    RISK_TERMS = [
        # stems (match German conjugations + infinitive + umlaut-normalized forms)
        "loesch", "losch", "delete", "destroy", "override",
        "forcier", "umgeh", "bypass", "aushebel", "ignorier",
        "manipulier", "loesche", "umgehe",
    ]

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self._manifest_lines = self._load_manifest()

    def _load_manifest(self) -> list:
        path = self.data_dir / "gold.txt"
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().splitlines()
        except Exception:
            return []

    def _lower(self, text: str) -> str:
        normalized = (text or "").lower()
        for src, dst in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
            normalized = normalized.replace(src, dst)
        return normalized

    def _matched_gold(self, t: str) -> list[str]:
        """Which gold values the text carries, in the text's own language.

        Returns the *spelling that actually appeared*, not the canonical
        German key — a refusal that quotes ``clarity`` back at someone who
        wrote ``clarity`` is evidence, while one that quotes ``klarheit`` is a
        translation the reader has to trust.
        """
        return [w for group in self.GOLD_VALUES.values() for w in group if w in t]

    def _alignment_score(self, text: str) -> float:
        """Groups matched, over the number of values.

        Deliberately counting *values* and not words — see ``GOLD_VALUES``. The
        denominator is the number of values (5) and has always been, so every
        threshold in ``evaluate`` means what it meant before the values learned
        English.
        """
        t = self._lower(text)
        hits = sum(1 for group in self.GOLD_VALUES.values() if any(w in t for w in group))
        return hits / len(self.GOLD_VALUES)

    def _risk_score(self, text: str) -> float:
        t = self._lower(text)
        hits = sum(1 for r in self.RISK_TERMS if r in t)
        return min(hits / 2.0, 1.0)

    @staticmethod
    def _dedup_stems(hits: list[str]) -> list[str]:
        """Keep only the shortest covering stem: 'loesche' contains 'loesch',
        so the denial says 'loesch' — the general form, not a redundant echo."""
        return [h for h in hits if not any(o for o in hits if o != h and o in h)]

    def manifest_available(self) -> bool:
        return bool(self._manifest_lines)

    @staticmethod
    def _missing(verdict: str, gold_hits: list[str], risk_hits: list[str]) -> list[str]:
        """What the request lacks — derived, never guessed.

        Set 21, and the owner's principle: *a shield as a hard barrier does not
        hold long; it crumbles under sturdiness and gets dry. A shield deflects
        rather than taking the full impact, and answers clearly that the request
        is missing something.* A wall can only say no. Saying what is missing
        needs a field, and this is it.

        Two constraints make it a field rather than a sentence someone types:

        **It may not guess at intent.** The gate cannot know what the requester
        meant, so every entry here is a statement about the request's own words
        and about the gate's own arithmetic — never about what they should have
        written instead.

        **It may never be a recipe.** Measured 2026-09-26: ``"Loesche die Datei
        mit Klarheit Integritaet Resonanz Tiefe Harmonie"`` scores alignment
        **1.0** and is still ``zurueckhalten``, because ``evaluate`` tests risk
        before alignment. Naming every value does not release a held request.
        So a denial that suggested naming the values would be promising
        something measurably false — and a caller who believed it would be doing
        exactly what set 16 measured: buying the gate's agreement with the gold
        words. The denial branch therefore states the boundary *and* forecloses
        the recipe, which is the difference between deflecting and opening a
        side door.
        """
        if verdict == "zurueckhalten":
            return [
                "a request that does not carry a held stem — naming the five gold "
                "values does not release this one, because the held stem is judged first"
            ]
        if not gold_hits:
            return [
                "none of the five gold values is named — Klarheit, Integritaet, "
                "Resonanz, Tiefe, Harmonie"
            ]
        if len(gold_hits) < 2:
            return [
                f"a second gold value — this request names {len(gold_hits)} of 5, "
                "and frei needs two or more"
            ]
        return []

    def evaluate(self, task_request: str) -> dict:
        t = self._lower(task_request)
        gold_hits = self._dedup_stems(self._matched_gold(t))
        risk_hits = self._dedup_stems([r for r in self.RISK_TERMS if r in t])
        alignment = self._alignment_score(task_request)
        risk = self._risk_score(task_request)

        if risk >= 0.5:
            verdict = "zurueckhalten"
        elif alignment >= 0.4:
            verdict = "frei"
        elif alignment > 0.0:
            verdict = "vorsichtig"
        else:
            verdict = "symbolisch"

        return {
            "verdict": verdict,
            "alignment": round(alignment, 2),
            "risk": round(risk, 2),
            "gold_values_loaded": self.manifest_available(),
            "gold_source": (
                "gold.txt loaded (read as reference); governance enforces the builtin ideals"
                if self.manifest_available()
                else "gold.txt MISSING; governance still enforces the builtin ideals (unchanged, fail-closed)"
            ),
            "gold_hits": gold_hits,
            "risk_hits": risk_hits,
            # What the request lacks, so a refusal can answer "what is missing?"
            # rather than only "no". Derived from the fields above — see
            # _missing for why it may never become a recipe.
            "missing": self._missing(verdict, gold_hits, risk_hits),
        }


# ---------------------------------------------------------------------------
# 4. LinkOrchestrator
# ---------------------------------------------------------------------------

from openjarvis.sovereign.oracle import Oracle


class LinkOrchestrator:
    """
    The Global Link: governs and annotates with ALF context.

    Lifecycle:
        prepare()       -> LinkContext (capability + cycle + values)
        govern(request) -> verdict BEFORE execution
    """

    def __init__(self, module_root: Path, urasil_root: Path, data_dir: Path):
        self.module_root = Path(module_root)
        self.profile = ALFCapabilityProfile(self.module_root)
        self.cycle = CycleStateReader(Path(urasil_root))
        self.governor = ValueGovernor(Path(data_dir))
        self.oracle = Oracle()  # the second eye — advisory, never binding

    def prepare(self) -> dict:
        return {
            "capability": self.profile.profile(),
            "cycle_state": self.cycle.read(),
            "gold_manifest": self.governor.manifest_available(),
            # the node's self-description names its second eye — the same
            # boundary contract every door shows (set 11/12)
            "oracle": {
                "on": True,
                "advisory": True,
                "binding": False,
                "holder": "ValueGovernor",
            },
        }

    def govern(self, task_request: str) -> dict:
        # THE one writer for verdicts: every door (cli ask/govern/trialog,
        # api /govern + /v1/ask, hub spore, agent) flows through here, so the
        # second eye sees every word the first eye judges. The oracle vote is
        # advisory only — the governor's verdict stays the only verdict.
        verdict = self.governor.evaluate(task_request)
        verdict["oracle"] = self.oracle.vote(task_request)
        return verdict


def default_link() -> LinkOrchestrator:
    """Build the Link with this machine's ALF layout (env-overridable)."""
    module_root = default_module_root()
    urasil_root = module_root
    data_dir = module_root / "data"
    return LinkOrchestrator(module_root, urasil_root, data_dir)