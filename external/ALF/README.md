# ALF – Artificial Life Framework

An experimental framework combining cellular evolution (Colorverse), a cyclic-state agent (Urasil_light), and optional LLM integration via Ollama.

**Current state:** Working core systems with tested LLM bridges on feature branch.

---

## What this actually is

ALF explores emergent behavior through three coupled systems:

1. **Colorverse**: Multi-layer cellular automata with hexagonal dynamics, cluster formation, and harmonic field evolution
2. **Urasil_light**: Cyclic state machine with persistent identity, experience logging, and values-based filtering
3. **Optional LLMBridge**: Context-aware response generation via local Ollama (or API: Mistral, OpenAI)
4. **WerteTeilen**: Dynamic values scoring that decides whether/how responses are shared

**NOT a chatbot.** No embeddings, no training. A **deterministic system with optional LLM augmentation**.

---

## Two branches, different maturity

| Feature | `main` | `feature/llm-bridge-werte-teilen-integration` |
|---------|--------|-----------------------------------------------|
| Colorverse | ✅ Stable | ✅ Stable |
| Zyklus (mood cycles) | ✅ Working | ✅ Working |
| Identity persistence | ✅ Working | ✅ Working |
| Interpretation | ⚠️ Templates only | ⚠️ Templates only |
| Seed generation | ⚠️ String concat | ✅ LLM-powered OR fallback |
| **LLMBridge** | ❌ No | ✅ Complete + Tested |
| **WerteTeilen** | ❌ No | ✅ Complete + Tested |
| **Tests** | ❌ None | ✅ 26+ tests |
| **Docs** | Minimal | Complete |

---

## Architecture (actual code structure)

ALF/ ├── Colorverse/ Cellular evolution (WORKS) │ ├── engine.py Main loop: cells → clusters → rings → spheres │ ├── config.py Tuning parameters │ ├── Zelle.py, Cluster.py Cell & cluster dynamics │ ├── Ring.py, Sphere.py Hierarchical aggregates │ └── MetaSphere.py Pattern detection layer │ ├── Urasil_light/ Agent core (STABLE + LLM-ENHANCED on feature branch) │ ├── core/ │ │ ├── zyklus.py Mood cycles (12/12/30 ticks) ✅ Works │ │ ├── identity.py JSON persistence ✅ Works │ │ ├── interpretation.py Input → mood-tagged meaning ⚠️ Basic │ │ ├── seed.py Response scaffold (template or LLM) │ │ ├── silky_edge.py Mood-based style suffix │ │ ├── erfahrung.py Experience storage with filtering │ │ ├── rueckmeldung.py Feedback loop + stats │ │ ├── mandate.py Load gold.txt values │ │ ├── ininity.py Maturity filtering │ │ ├── frequency.py Frequency tracking (skeleton) │ │ ├── llm_bridge.py [NEW] Ollama/Mistral/OpenAI bridge │ │ ├── backends.py [NEW] Backend implementations │ │ ├── werte_teilen.py [NEW] Values-based scoring │ │ └── session_manager.py Session tracking │ ├── data/ │ │ ├── gold.txt Values/ideals (22KB) │ │ ├── Ininity.txt Maturity criteria (25KB) │ │ ├── identity.json Persistent state │ │ └── baseline_identity.json Fresh start template │ ├── runtime/ │ │ └── main.py CLI + interactive mode │ ├── tests/ [NEW] Unit + integration tests │ ├── docs/ Architecture, pipeline, values docs │ └── alf_main.py (top-level orchestration) │ ├── EML/ Meaning bridge (thin layer) │ └── eml.py read_world → interpret → apply │ ├── SatuRings/ Ring visualization (Rust, untested) └── alf_main.py ALF loop orchestrator
Code


---

## What actually works (honest status)

### ✅ Production-ready
- **Zyklus (mood cycles)**: Deterministic, reliable, ~64 lines of Python
- **Identity persistence**: Load/save JSON, no data loss
- **Colorverse evolution**: Cells evolve, clusters form, metrics track believably
- **LLMBridge (feature branch)**: Ollama/Mistral/OpenAI + fallback (~430 lines, fully tested)
- **WerteTeilen (feature branch)**: Dynamic scoring with 4 components, 26+ tests (~410 lines)

### ⚠️ Partial/basic implementations
- **Interpretation** (`~50 lines`): Just prepends mood strings. No real parsing. Example:
  ```python
  if modus == "kreativ":
      return f"Kreativer Impuls: {text}"  # That's literally it

    Seed (~30 lines): Templates + optional LLM call:
    Python

    if modus == "fokus":
        return f"Direkt: {bedeutung}"  # Template
    # OR calls llm_bridge if enabled

    SilkyEdge (~15 lines): Mood suffix only:
    Python

    if stimmung == "warm":
        return f"{rohantwort} — ich spüre da etwas Warmes."

    Experience replay: Logs experiences, doesn't integrate them into decisions
    EML bridge: Threshold-based (e.g., meaning["stabil"] = harmonie > 0.6), not semantic

❌ Not implemented

    Real semantic understanding
    Learning from past interactions
    Frequency (AF/PF/RF) modulation into actual outputs
    SatuRings Rust rendering (Python version only, untested)

The pipeline (what actually happens)
On main branch (no LLM):
Code

Input
  ↓
Interpretation (prepend mood string)
  ↓
Seed (template concat)
  ↓
SilkyEdge (append mood suffix)
  ↓
Erfahrung (log if passes Ininity filter)
  ↓
Rueckmeldung (check if matches gold.txt substring)
  ↓
Output

On feature branch (with LLM + WerteTeilen):
Code

Input
  ↓
Interpretation (prepend mood string)
  ↓
Seed (calls LLMBridge if use_llm=true, else template)
  LLMBridge builds context-rich prompt:
    - System prompt (identity + values)
    - Kontext prompt (mandat, modus, nodus, erfahrung)
    - Anweisung (style guidelines)
  Selects backend: tief/schnell/effizient based on mandat/modus
  Falls back to FallbackBackend if Ollama unavailable
  ↓
WerteTeilen scores the draft:
  - Werte-Score (40%): align with identity values?
  - Vertrauens-Score (30%): trust this context?
  - Kontext-Score (30%): is context suitable for sharing?
  - Risiko-Score (subtracted): risk of misunderstanding?
  Returns: "frei" (green), "vorsichtig" (yellow), "symbolisch" (blue), "zurückhalten" (red)
  ↓
SilkyEdge (append mood suffix)
  ↓
Erfahrung (log with WerteTeilen verdict)
  ↓
Rueckmeldung (feedback + stats)
  ↓
Output

Key modules (what's actually in the code)
llm_bridge.py (feature branch, ~430 lines)

Handles LLM integration. Key methods:

    _baue_system_prompt(): Creates identity-aware system prompt
    _baue_kontext_prompt(): Adds mandat, modus, nodus, erfahrung context
    _waehle_backend(): Selects OllamaBackend("tief"/"schnell"/"effizient") based on mandat/modus
    generiere_antwort(): Main method, calls backend, logs usage, falls back gracefully
    get_stats(): Returns call counts, preferred models

Important: LLM is optional. Falls back to templates if Ollama not available.
werte_teilen.py (feature branch, ~410 lines)

Dynamic values-based scoring. Key methods:

    _werte_score(): Checks if sharing aligns with identity (grundton, mandat, modus, deutung)
    _vertrauens_score(): Learns trust to contexts over time
    _kontext_score(): Scores context suitability (privat=0.9, öffentlich=0.3)
    _risiko_score(): Detects sensitive topics (identität, passwort, persönlich, etc.)
    bewerte_interaktion(): Combines 4 scores → recommendation
    format_bewertung(): Color-coded output (🟢🟡🔵🔴)

Learning mechanism: Trust adapts per context based on recommendations.
backends.py (feature branch, ~360 lines)

LLM backend implementations:

    OllamaBackend: Local via subprocess (llama3.2, mistral, phi3)
    MistralBackend: API via requests (mistral-tiny, mistral-small)
    OpenAIBackend: API via requests (gpt-3.5-turbo, gpt-4)
    FallbackBackend: Deterministic pattern matching for offline use
    create_default_backends(): Factory returning dict of available backends

All inherit from abstract LLMBackend base class.
main.py runtime (feature branch, ~315 lines)

Entry point. Implements:

    main(): Single execution with full pipeline
    run_interactive(): Persistent session with commands:
        /stats: Show LLMBridge + WerteTeilen + Erfahrung + Rueckmeldung stats
        /zyklus: Show current cycle (Sonne/Mond/Tag)
        /id: Show identity info
        exit/quit/beenden: End session

How to run
Prerequisites
bash

python3 --version  # 3.8+
# Optional: Ollama for LLM
curl https://ollama.ai/install.sh | sh
ollama pull llama3.2:3b mistral phi3

Single execution (both branches)
bash

cd Urasil_light
python3 -m runtime.main
# Prompts for input, runs pipeline once, outputs response

Interactive mode (feature branch recommended)
bash

git checkout feature/llm-bridge-werte-teilen-integration
python3 -m Urasil_light.runtime.main --interactive
# Persistent session, /stats, /zyklus, /id commands

Colorverse standalone
bash

cd Colorverse
python3 engine.py
# Outputs: Step, global_harmonie, global_drift, stoerimpulse

Run tests (feature branch)
bash

pip install pytest pytest-mock pytest-xdist pytest-cov
python3 -m pytest Urasil_light/tests/ -v
# 26+ tests covering backends, llm_bridge, werte_teilen, integration

Configuration
Enable/disable LLM (in Urasil_light/data/baseline_identity.json):
JSON

{
  "name": "URASIL",
  "version": "1.0",
  "grundton": "neutral",
  "use_llm": true,
  "mandat": {"name": "Dialog", "beschreibung": "Offener Austausch"},
  "werte": ["Klarheit", "Integrität", "Resonanz", "Tiefe"]
}

Set use_llm: false to use pure Python templates (works on both branches).
LLM backends (auto-created by create_default_backends()):
Python

backends = {
    "tief": OllamaBackend("llama3.2:3b"),      # Reflection
    "schnell": OllamaBackend("mistral:latest"), # Dialog
    "effizient": OllamaBackend("phi3:3.8b"),    # Neutral
    "fallback": FallbackBackend()               # Always available
}

If Ollama not found, falls back to FallbackBackend (returns pattern-matched responses).
Limitations (honest assessment)

    Interpretation is template-based: No NLP. Just prepends mood strings.
    Seed generation is template or LLM: No real synthesis without LLM. Templates are simple concat.
    Gold/Ininity matching is substring: if "wert" in text.lower(). Not semantic.
    No real learning: Experiences log, but don't reshape future behavior.
    Frequency system is skeleton: AF/PF/RF tracked but not integrated into outputs.
    Single-threaded: Sequential execution, no async.
    SatuRings is untested: Rust build not verified.
    WerteTeilen is learning-light: Trust adapts slightly (+0.02/-0.01 per interaction), not deep learning.
    LLM fallback is basic: FallbackBackend uses simple pattern matching, not ML.

Test coverage (feature branch)

    test_backends.py: OllamaBackend, MistralBackend, OpenAIBackend, FallbackBackend (4295 bytes)
    test_llm_bridge.py: Prompt building, backend selection, fallback behavior (7416 bytes)
    test_werte_teilen.py: Scoring components, learning, protocol, formatting (10873 bytes)
    test_integration.py: Full pipeline, LLM + WerteTeilen together (11727 bytes)

Total test code: ~30KB covering 26+ test cases

All tests use pytest fixtures and mocking. No external API calls in tests.
Documentation (feature branch)

    ARCHITECTURE.md: System design principles
    CYCLE.md: Zyklus (mood cycle) explanation
    PIPELINE.md: Data flow through the system
    VALUES.md: gold.txt and werte principles
    INTEGRATION_LLMBRIDGE_WERTETEILEN.md: Deep dive on LLM + WerteTeilen (23KB)
    TEST_SCENARIOS.md: Comprehensive test guide (45KB)

For deeper work (Plan A)

If you want real semantic understanding: → Use HALF repository (smori-start-seed/HALF)

ALF is the stable, honest, tested foundation. HALF is the ambitious, full-stack vision.
License

Apache 2.0
Quick answers

    How do cells evolve? → Colorverse/engine.py:step(), cells update → clusters form if evolutionskeim=true
    How do moods work? → Urasil_light/core/zyklus.py, 12/12/30 counters → matrix() → mood strings
    How does LLM integrate? → Urasil_light/core/llm_bridge.py, builds context-rich prompt, calls backend, logs usage
    How does WerteTeilen work? → Urasil_light/core/werte_teilen.py, 4-component scoring → recommendation
    How do I use it? → python3 -m Urasil_light.runtime.main --interactive (feature branch)
    Can I use it without Ollama? → Yes, FallbackBackend is always available (set use_llm: false in identity.json)
