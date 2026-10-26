# Bianca v1.0.4 — Release Notes

Bianca is a sovereign fork of OpenJarvis: a modular AI assistant backend with
composable intelligence primitives and a value-governed overlay
(`src/openjarvis/sovereign/`).

## Highlights

- ValueGovernor governance: only `zurueckhalten` denies; `frei` needs >= 2 real
  German gold words; English can neither launder a denial nor buy affirmation;
  hook failure = denial (fail-closed); `gold_source` on every verdict.
- Second eye (Oracle): advisory only — `advisory: True, binding: False,
  holder: "ValueGovernor"`. `oracle` exits 0 always; `govern` exits 1 on denial.
- Colorverse garden: read-only window onto the sibling kernel; 19 modules named.
- Idle daemon + ledger reconciliation; chain integrity checks.
- Native Rust extension (`openjarvis_rust`) via maturin/pyo3.
- Sovereign CLI: `bianca-sovereign ask|govern|oracle|today|context|serve|hub|ledg`.

## Legal

- License: Apache License 2.0 (see `LICENSE`).
- Copyright: OpenJarvis Contributors; Bianca fork by its maintainers.
- This release ships no proprietary model weights; models are pulled at runtime
  (Ollama/OpenAI/Anthropic/etc.) under their own licenses.

## Artifacts

- `bianca-1.0.4-py3-none-any.whl` (4.25 MiB)
- `bianca-1.0.4.tar.gz` (18.27 MiB) — within the 20 MiB upload budget.

## Install

```bash
pip install bianca-1.0.4-py3-none-any.whl
# or
uv tool install bianca==1.0.4
```

## Verify

```bash
bianca-sovereign --version   # or: bianca --version
bianca-sovereign idle verify
```
