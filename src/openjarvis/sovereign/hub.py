"""hub — the self-hosted hub surface of the mycelium net.

The node shows strangers only what it chooses: a public manifest (identity,
capability, gold manifest, cycle, contract), a curated ``public/`` surface
with secrets hard-excluded by construction, and — from breath 2 onward — a
governed spore ingress. Everything hangs off the same local door (``serve``),
inheriting the fail-closed soul: a foreign word entering the node is judged
by the ValueGovernor before anything is stored.
"""

from __future__ import annotations

import datetime as _dt
import fnmatch
import json
import os
from pathlib import Path

from openjarvis.sovereign import daily
from openjarvis.sovereign.link import default_link, default_module_root

NODE_NAME = "Bianca"
HUB_VERSION = "1.1.0"

GOLD_VALUES = ["klarheit", "integritaet", "resonanz", "tiefe", "harmonie"]

# Names that may never be served by the public surface, even if a file of
# that name exists inside public/ — defense in depth under the one-writer
# rule. Patterns use fnmatch against the basename.
HARD_EXCLUDED = (
    "config.toml", "secret", "secrets", "private", "ledger", "ledger.*",
    "gold.txt", ".env", ".env.*", "*.key", "*.pem", "*.p12", "SOUL.md",
    "id_*", "*_rsa", "*_ed25519",
)


def hub_dir() -> Path:
    """Single source of truth for the hub store (mirrors the paths hub)."""
    return Path(os.environ.get("BIANCA_HUB_DIR", "/home/sam/Repos/Bianca/hub"))


def public_dir() -> Path:
    return hub_dir() / "public"


def spores_dir() -> Path:
    return hub_dir() / "spores"


def _ensure_dirs() -> None:
    pub, spo = public_dir(), spores_dir()
    pub.mkdir(parents=True, exist_ok=True)
    spo.mkdir(parents=True, exist_ok=True)
    if not (pub / "about.md").exists():
        (pub / "about.md").write_text(
            "# about this node\n\n"
            "Bianca — a sovereign citizen node of a mycelium net.\n"
            "Curated here by its operator. One writer. No secrets served.\n",
            encoding="utf-8",
        )


def _is_excluded(name: str) -> bool:
    base = Path(name).name
    return any(fnmatch.fnmatch(base, pat) for pat in HARD_EXCLUDED)


def manifest() -> dict:
    """The node's public self-description — deterministic, never fails."""
    _ensure_dirs()
    link = default_link()
    ctx = link.prepare()
    cap = ctx.get("capability") or {}
    cc = ctx.get("cycle_state") or {}
    sc = daily.node_self_check()
    eng = daily.engine_status()
    gold_file = default_module_root() / "data" / "gold.txt"
    return {
        "node": NODE_NAME,
        "hub_version": HUB_VERSION,
        "identity": {
            "voice": sc["voice"],
            "engine": eng["engine"],
            "engine_why": eng["why"],
            "gold_manifest": str(gold_file),
            "gold_loaded": gold_file.exists(),
        },
        "capability": {
            "mode": cap.get("mode", "?"),
            "surface": "read + governed spore ingress",
            "oracle": {  # the second eye — advisory, the boundary still holds
                "on": True,
                "advisory": True,
                "binding": False,
                "holder": "ValueGovernor",
            },
        },
        "cycle": {
            "grundmodus": cc.get("grundmodus", "?"),
            "stimmung": cc.get("stimmung", "?"),
            "fokus": cc.get("fokus", "?"),
        },
        "contract": {
            "holds": sc["contract_holds"],
            "verified": sc["verified"],
            "untraceable": sc["untraceable"],
            "failures": sc["failures"],
        },
        "gold": list(GOLD_VALUES),
        "public_dir": str(public_dir()),
        "pulse": pulse(),
        "time": _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


def public_list() -> list[str]:
    """Names served by the curated surface, secrets hard-excluded."""
    _ensure_dirs()
    return sorted(
        p.name for p in public_dir().iterdir()
        if p.is_file() and not _is_excluded(p.name)
    )


def public_read(name: str) -> tuple[bool, str]:
    """Read one curated file or a denied/excluded marker.

    Returns ``(found, content)``; ``found=False`` for both missing files
    and hard-excluded names — the door never confirms whether an excluded
    path exists. The resolved path must stay strictly inside public/.
    """
    _ensure_dirs()
    if _is_excluded(name):
        return False, ""
    root = public_dir().resolve()
    candidate = (root / name).resolve()
    if root not in candidate.parents or candidate == root:
        return False, ""
    if not candidate.is_file():
        return False, ""
    try:
        return True, candidate.read_text(encoding="utf-8")
    except OSError:
        return False, ""


def spore_count() -> int:
    _ensure_dirs()
    return sum(1 for p in spores_dir().iterdir() if p.is_file() and p.suffix == ".json")


def list_spores(limit: int = 10) -> list[dict]:
    """Accepted spores, newest first — the node's curated spore ledger."""
    _ensure_dirs()
    out: list[dict] = []
    for p in sorted(spores_dir().glob("*.json"), reverse=True):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue  # a broken receipt never takes the ledger down
        if len(out) >= limit:
            break
    return out


def pulse(ledger_dir: str | None = None) -> dict:
    """The audit pulse the manifest advertises — what the node did today."""
    where = Path(ledger_dir) if ledger_dir else daily.ledger_dir()
    evs = daily.read_ledger_events(where, daily.today_str())
    spore_events = [e for e in evs if e["type"] == "SPORE_RECEIVED"]
    return {
        "audits_today": len(evs),
        "spore_received": len(spore_events),
        "spore_stored": sum(1 for e in spore_events if "stored " in e["message"]),
        "spore_denied": sum(1 for e in spore_events if "denied " in e["message"]),
        "spores_total": spore_count(),
    }


def accept_spore(text: str, source: str = "<anonymous>", kind: str = "spore",
                 ledger_dir: str | None = None) -> tuple[int, dict]:
    """Judge a foreign contribution on arrival; store it only if accepted.

    Fail-closed, exactly like the ask door: ``zurueckhalten`` → 403 with the
    verdict body (the audit records what the governor thought — verdict,
    stems and a digest — but the denied words are never stored in the
    curated store); an evaluation hook failure → 503 (a hook failure IS a
    denial). Accepted spores get a stamped receipt file under
    ``hub/spores/`` and a ``SPORE_RECEIVED`` ledger line.
    """
    from openjarvis.sovereign.link import default_link
    from openjarvis.sovereign.logger import InteractionLogger
    _ensure_dirs()
    where = Path(ledger_dir) if ledger_dir else daily.ledger_dir()
    log = InteractionLogger(str(where))
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    try:
        verdict = default_link().govern(text)
    except Exception as exc:  # hook failure = denial, fail-closed
        log.log_event("SPORE_RECEIVED",
                      f"evaluation failed, {kind} from {source} denied "
                      f"({type(exc).__name__})", actor="hub")
        return 503, {"error": "evaluation failed, spore denied",
                     "detail": f"{type(exc).__name__}: {exc}"}
    v = verdict.get("verdict", "zurueckhalten")
    digest = _sha256(text)
    body = {
        "verdict": v,
        "gold_hits": verdict.get("gold_hits", []),
        "risk_hits": verdict.get("risk_hits", []),
        "alignment": verdict.get("alignment"),
        "risk": verdict.get("risk"),
        "gold_source": verdict.get("gold_source"),
        "oracle": verdict.get("oracle"),  # the second eye — advisory only
    }
    if v == "zurueckhalten":
        log.log_event("SPORE_RECEIVED",
                      f"denied {kind} from {source}: verdict {v}; "
                      f"stems {','.join(body['risk_hits'])}; sha {digest} "
                      f"eye={body['oracle'].get('vote') if body['oracle'] else '?'}",
                      actor="hub")
        return 403, {**body, "blocked": True,
                     "detail": f"spore denied by the value governor ({v}). "
                               "recorded, not stored."}
    path = spores_dir() / f"spore_{stamp}_{digest}.json"
    receipt = {
        "stamp": stamp, "kind": kind, "source": source, "text": text,
        # `verdict`, `risk`, `alignment`, `gold_hits` and `gold_source` below
        # are the gate's judgement OF THE DESCRIPTION — not of whatever the
        # contribution is about. Set 22 found the collision by carrying a
        # refusal, which has a verdict of its own: the receipt read
        # `verdict: symbolisch` beside a text saying `zurueckhalten`, same key,
        # two subjects, and nothing saying which was which. A record that can
        # be read two ways is a record that will be read the wrong way, so the
        # name of the subject is stated rather than left to be inferred.
        "judged": "this receipt's verdict/risk/alignment/gold_hits/gold_source "
                  "are the ValueGovernor's judgement of the text below. They "
                  "are not the contribution's own opinion of itself.",
        **body,
    }
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    log.log_event("SPORE_RECEIVED",
                  f"stored {kind} from {source}: verdict {v}; {path.name} "
                  f"eye={body['oracle'].get('vote') if body['oracle'] else '?'}",
                  actor="hub")
    return 200, receipt


def _sha256(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]