/**
 * Live captures of `GET /v1/garden` — the ground truth the garden screen is
 * checked against.
 *
 * All four are real payloads, not hand-written shapes, and none of them is
 * typed: every field was read out of `garden.status()` — the same function the
 * door calls — and the `upstream` list out of its single writer,
 * `garden.UPSTREAM`.
 *
 * 🚨 **SET 36 (2026-10-09): re-taken after the owner opened the Ring + Sphere
 * doors in the kernel.** `GARDEN_LIVE` now carries the grown world — clusters
 * 90 → 129, `flat_at = null`, the free field no longer homogenised — and every
 * `upstream` entry carries the set-36 correction of the old *"growth is one-shot
 * … no source of disorder"* sentence. A fixture is a capture, so the correction
 * was made in `garden.py` first and this file re-taken from it; the claim
 * `the-garden-fixture-is-a-capture` re-derives every `UPSTREAM` entry out of
 * this file, so the direction can only be broken loudly.
 *
 * 🚨 **SET 37 (2026-10-10): re-taken after the owner added the growth factor
 * `WACHSTUMSFAKTOR = 0.6` to the seed gate (`engine.py:75`).** `GARDEN_LIVE`
 * now carries the gentler burst — clusters 90 → ~125/133, `flat_at = null`,
 * still one-shot — and every `upstream` entry carries the set-37 sentence:
 * the factor did not add time, it paced the burst. The kernel edit moved no
 * line in `engine.py`, so the pinned gate `engine.py:72-76` and the claim
 * `the-garden-death-is-named` both still hold. **RETRACTED by set 38 below.**
 *
 * 🚨 **SET 38 (2026-10-16): re-taken after the owner took the growth factor
 * back.** There is no `WACHSTUMSFAKTOR` any more; a free cell carries a seed
 * only when the **crest of the Sphere's travelling wave** stands over it
 * (`z.hue < 180`, `engine.py:75`). `GARDEN_LIVE` now carries the set-38 world —
 * clusters 90 → ~125/126, `flat_at = null`, still one-shot, but the burst
 * carries over 22 steps to step 172 instead of 16 steps to step 23 — and every
 * `upstream` entry carries the set-38 sentence: the factor was retracted, the
 * crest replaced it, and growth is still one-shot for a *measured* reason (the
 * gate closes on `harmonie < 0.5`; `Cluster.mutation()`'s edger consumes the
 * free field). The edit was **line-neutral**, so the pinned gate
 * `engine.py:72-76` and the claim `the-garden-death-is-named` still hold. The
 * `kernel.files` hashes moved with it (`config.py`, `engine.py`), as a re-take
 * must.
 *
 * 🚨 **Set 35 (2026-10-06): this file was, for one whole set, the WRITER of a
 * fact its source had never carried.** The SET 35 retraction existed *here* and
 * not in `garden.py`, so the live door served "the evolution path is
 * unreachable, not one seed appears, the best ever measured is 2" while every
 * React test passed against a sentence the node never sent. **A fixture is a
 * capture; the moment it is edited by hand it stops being evidence and becomes a
 * copy**, and then two surfaces disagree about one garden — set 21's
 * "present but wrong evidence" one layer down. The retraction now lives in
 * `garden.py`, the single writer, and the claim
 * `the-garden-fixture-is-a-capture` re-derives every `UPSTREAM` entry out of
 * this file, so the direction can only be broken loudly.
 *
 * ⚠️ **The same discovery cost a day of green.** `UPSTREAM` is read at import
 * time, so a node started before an edit keeps serving the old diagnosis — and
 * a fixture re-taken in a fresh process is then *fresher than the door it claims
 * to capture*. That is why the claim compares against the **source**, not
 * against a running node: it must hold with the node stopped.
 *
 * 🚨 **A harness fault is recorded here rather than hidden.** The first attempt
 * at the set-34 re-take produced a frame for the two negative states, because
 * `garden` reads `BIANCA_GARDEN_DIR` at IMPORT time and the variable had been
 * set afterwards. That was my measurement's fault, not a property of the code,
 * and the fix was a capture per state in its own process with the environment
 * set first — which is how these four are taken. `GARDEN_NO_KERNEL` also needs
 * `BIANCA_COLORVERSE_DIR`: without it both negative states produced the *same*
 * error text, because the kernel path does not come from the garden directory.
 * **A failure message that repeats itself is a harness fault, not a
 * measurement.**
 *
 * `age_s` is pinned to 0 in `GARDEN_LIVE` — it is the only field that changes
 * every read, and the door's type only offers it when a frame exists. Each is
 * annotated with the **real** door type and carries no cast, so a
 * field the node does not send, or renames, is a type error here rather than a
 * silently-undefined value on screen.
 *
 * 🚨 **One named gap.** `garden.py` has TWO deflection sentences: one
 * when the kernel directory does not exist ("Der Garten hat keinen Boden"),
 * which `GARDEN_NO_KERNEL` carries and a test holds, and one when it exists
 * but is empty ("Dem Garten fehlen 10 von 10 Dateien"), which no fixture and
 * no test covers. The first re-take of this file fell into that gap by
 * accident — it made a fresh empty directory — and the test failed for the
 * right reason, which is the only reason this is worth writing down.
 */


import type { GardenState } from './sovereign-api';

/** The garden running: a frame, a live child, the three upstream defects. */
export const GARDEN_LIVE: GardenState = {
  "kernel": {
    "path": "/home/sam/Repos/ALF/Colorverse",
    "present": true,
    "wanted": [
      "config.py",
      "engine.py",
      "Zelle.py",
      "Cluster.py",
      "Ring.py",
      "Sphere.py",
      "MetaSphere.py",
      "UniverseNode.py",
      "saturn_hexagon_core.py",
      "saturings.py"
    ],
    "missing": [],
    "files": {
      "config.py": "b349f97a7041f367",
      "engine.py": "2c15bbadf53d51a1",
      "Zelle.py": "dae7d542e79f4faf",
      "Cluster.py": "953335ea76c03886",
      "Ring.py": "2b519111eb495c7c",
      "Sphere.py": "51be69a65b4495cf",
      "MetaSphere.py": "0c1c2cf8361bd927",
      "UniverseNode.py": "fc9a738b2748b022",
      "saturn_hexagon_core.py": "5e3f1ecdd6d7d057",
      "saturings.py": "52ddd5e42f344300"
    },
    "tick_s": 0.25,
    "upstream": [
      {
        "id": "stabiliser-vs-evolution",
        "where": "Zelle.py:38, Zelle.py:130, Zelle.py:150 vs engine.py:72-76, engine.py:156-160",
        "what": "Zelle.update() calls stabilisierung() unconditionally; it pulls every cell toward its neighbours' mean hue by a hardcoded alpha = 0.05, so neighbourhood hue variance decays. engine.py then requires drift > 0.4 AND harmonie < 0.5 for an evolution seed, and builds a NEW Cluster only from 11 seeds at once.",
        "why_it_matters": "\ud83d\udea8 **SET 35 (2026-10-05) \u2014 this entry's CONCLUSION is retracted; its locations and what they say are still true.** For four sets this table read *\u201cthe real blocker is one number\u201d*, and the garden would not breed. By set 35 it bred: **17-18 new Clusters at step 1**; with the set-36 doors open it reaches **129 (90 \u2192 129)** (below). No threshold was ever lowered to get there. `engine.py` marked its seeds at the **end** of `step()`, after seven update passes had already pulled the neighbourhood variance down by a factor of **0.21** \u2014 so the gate was tested against a world that had already closed. Moving the marking to the **head** of `step()` (`engine.py:72-76`) opens it: **a door nobody opened in time, measured as a wall.** The seed gate is also **threefold** (`drift > 0.4` **and** `energy > 0.6` **and** `harmonie < 0.5`), not twofold as this entry says.\n\n**The arithmetic below is history, not a verdict** \u2014 and it was never wrong about what it measured: 1 \u2192 3 \u2192 10 seeds as the harmonie gate opens 0.5 \u2192 0.9 \u2192 0.99, against the 11 a `Cluster` needs. What was wrong was the assumption underneath it, that the gate is tested once, early. It was tested after the variance had already decayed.\n\n**SET 36 (2026-10-09) \u2014 the paragraph that stood here is RETRACTED, and the owner took exactly the decision it named.** It read *\u201cgrowth is one-shot \u2026 there is no source of disorder, so sustained growth needs one \u2014 a semantic decision about the garden\u2019s physics, not a parameter.\u201d* The decision was taken: the **Ring** door smooths its clusters toward the ring\u2019s circular mean hue (`RING_GLAETTUNG`) and re-lights their saturation and brightness (`RING_RELIGHT`); the **Sphere** door paints the free field a travelling hue wave (`SPHERE_MUSTER_*`) and feeds it energy. **The kernel now has a disorder source.** Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters 90 \u2192 130/131/131**, `flat_at = None`, ~760 cells alive and holding colour. **What is still true:** growth is still **one-shot** (the maximum arrives by ~step 50 and holds, because the new clusters consume the free field the Sphere paints on), and every process in the kernel is still a **mean** \u2014 the Sphere\u2019s wave is the disorder source, not a change of nature. Sustained growth is **not** achieved.\n\n**SET 38 (2026-10-16) \u2014 the owner took set 37\u2019s growth factor back, and the crest of the wave decides instead: there is no `WACHSTUMSFAKTOR` in the kernel any more.** Set 37 had put a coin on the gate \u2014 a free cell became a seed only with probability 0.6 while the triple gate held (`engine.py:75`). Measured on the kernel this host reads (seeds 1/7/42, 1500 steps) it cost slightly (**clusters 90 \u2192 126/127/133** against 130/131/131 without it) and it replaced the cell\u2019s own decision with a global die roll \u2014 the owner\u2019s *lost living character*. **The replacement is not a number but the field\u2019s own phase.** The Sphere already paints the free field a travelling wave (`hue = SPHERE_MUSTER_AMP * sin(freq * i + phase)`), so a free cell now carries a seed only when the **crest stands over it** (`z.hue < 180`, the sign half of the painted wave, on `engine.py:75`; the edit is **line-neutral**, so the pinned gate `engine.py:72-76` does not move). The crest travels, so ripeness travels. Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters 90 \u2192 125/126/126**, `flat_at = None`, 822-842 cells alive and holding colour; the burst now **carries over 22 steps to step 172** instead of 16 steps to step 23. **What is still true, and stated rather than implied:** growth is still **one-shot and still not sustained.** The measured reason is no longer the factor \u2014 the free field\u2019s gate closes on `harmonie < 0.5` (a witness inside the gate: 219 of 221 remaining free cells carry `drift > 0.4` and **0** carry `harmonie < 0.5`), and `Cluster.mutation()`\u2019s **edger** consumes free cells (`abs(f.hue - edger.hue) < 20 and f.drift > 0.3` \u2192 `in_cluster`; measured: 313 cells `in_cluster` after step 1, not the 44 of the real new clusters). That consumption is not a pure defect \u2014 switching it off gives 157/160/158 clusters but the colour field dies (spread 95/44/99 against 229/211/180).\n\n\ud83d\udea8 **SET 35 (2026-10-06) \u2014 and the FRAME now contradicts itself, and both arms are true.** `born_converged` says the world can never grow; `cluster - cluster_start` says it grew. Both are measurements, because they answer different questions: a seed needs **11 at once**, and a mean is not a count. The frame therefore carries `convergence_disputed`, `cluster_start` and `grew_at` beside `born_converged`, and every surface prints the disagreement rather than one arm of it. **The owner's own run reached step 3858 with `flat_at = None`** and 111 clusters \u2014 four times the 1000 steps measured the day before, and the furthest any world has been watched on the repaired kernel.\n\n\u26a0\ufe0f **That block was nearly absent from this file.** It had been written into the React **fixture** instead, so the live door served the retracted verdict for a whole set while every React test passed against text the node never sent. A fixture is a *capture*; the moment it is edited by hand it stops being evidence and becomes a copy \u2014 and two surfaces then disagree about one garden, which is set 21's \u201cpresent but wrong evidence\u201d one layer down. **This file is the only writer.**\n\n\ud83d\udea8 **Set 34 retracted this claim twice, and the real blocker is one number.** It used to say the evolution path is unreachable, citing 'best drift 0.0426' \u2014 a figure taken on the pre-repair world, which was dead at birth, so it measured a corpse. Re-measured, the drift story is the WRONG DOOR: drift reaches 0.6886-0.7075 and stays there, above the seed threshold of 0.4 in every phase \u2014 and 0.7 is the death threshold (Zelle.py:86), so the maximum drift is the failing line seen from below, not a sign of health. What closes is the other gate. A seed needs harmonie < 0.5 (engine.py:75), which by Zelle.py:81 means a neighbour-hue variance above 5400 (half of HARMONIE_NULLPUNKT = 10800). In steps 1-6 the variance is there, harmonie falls to 0.2767, and seeds can form. From step 7 on, over 314 steps, harmonie never goes below 0.8289 \u2014 variance 1848 against the 5400 needed, short by a factor of 2.9 \u2014 and not one seed appears. The cause is the line this entry already names: stabilisierung() is called unconditionally (Zelle.py:150) and pulls every cell onto its neighbours' mean, so neighbour variance decays to nothing. alpha is a literal in Zelle.__init__, not a config knob. Reproduction then needs 11 such seeds at once, and the best ever measured is 2. \ud83d\udea8 **And the wall is arithmetic, not tuning:** with the drift gate open, opening the harmonie gate from 0.5 to 0.9 raised the seed count from 1 to 3, and to 0.99 it reached 10 \u2014 still one short of the 11 a Cluster needs. The reason is that stabilisierung() drives neighbour hue variance to EXACTLY 0, so Zelle.py:81 returns harmonie = 1.0 for most cells, and every threshold below 1.0 is then unreachable at once. No value for this threshold repairs it: the quantity it reads is gone. All three defects named in this table trace back to that one call."
      },
      {
        "id": "wander-system-is-a-comment",
        "where": "engine.py:114",
        "what": "the only perturbation source in the kernel is a comment: '# 8. Optional: Wander-System' / '# self.hexagon_wander()'",
        "why_it_matters": "hexagon_wander appears once in the whole kernel and 0 files define it. A comment naming a function that does not exist is a claim, and it is false \u2014 the same shape as set 23's lesson about a comment describing a check."
      },
      {
        "id": "a-cell-dies-for-being-different",
        "where": "Zelle.py:81, Zelle.py:87 vs engine.py:75",
        "what": "Zelle.failsafe() lists 'harmonie < 0.2' among the four conditions that kill a cell outright (hue, saturation, brightness and drift all go to 0), and Zelle.berechne_harmonie() derives harmonie as 1 - min(1, var / HARMONIE_NULLPUNKT) from the spread of its neighbours' hues",
        "why_it_matters": "the quantity a seed needs is a difference and the quantity the kernel kills for is also a difference \u2014 so the death criterion and the growth criterion are the same sign. Measured 2026-10-02 with the kernel's own build_world: 792 of 1000 cells died in their FIRST update, at harmonie 0.0218, from starting hues drawn uniform(0, 360). Set 34's second repair made harmonie an honest 0-1 quantity \u2014 and an honest reading is zero for a newborn cell, because that is what 'your neighbours are all different colours' means. No parameter repairs this: it is the kernel's definition of death, not a scale."
      }
    ],
    "tended": false,
    "tended_note": "Bianca injects nothing. The owner decided the garden is shown as it is, so no cell is perturbed, seeded or 'improved' here.",
    "missing_note": ""
  },
  "frame": {
    "step": 220,
    "cells": 1000,
    "hue_mean": 183.3558153566749,
    "harm": 0.9999081636635819,
    "drift": 0.028399390030163712,
    "energie": 0.603361571707778,
    "spread": 222.633419775635,
    "keime": 11,
    "cluster": 125,
    "cluster_start": 90,
    "grew_at": 1,
    "convergence_disputed": true,
    "readout": "[ENGINE] step=220 harm=1.00 drift=0.01 stoer=2.26",
    "thresholds": {
      "drift": 0.4,
      "energie": 0.6
    },
    "born_converged": true,
    "converged_at": 1,
    "flat_at": null,
    "files": {
      "config.py": "b349f97a7041f367",
      "engine.py": "2c15bbadf53d51a1",
      "Zelle.py": "dae7d542e79f4faf",
      "Cluster.py": "953335ea76c03886",
      "Ring.py": "2b519111eb495c7c",
      "Sphere.py": "51be69a65b4495cf",
      "MetaSphere.py": "0c1c2cf8361bd927",
      "UniverseNode.py": "fc9a738b2748b022",
      "saturn_hexagon_core.py": "5e3f1ecdd6d7d057",
      "saturings.py": "52ddd5e42f344300"
    },
    "error": null,
    "written": 1792184907.1326556,
    "present": true,
    "age_s": 0,
    "fresh": true,
    "child_running": true,
    "live": true,
    "stale": false
  },
  "child_running": true,
  "tick_s": 0.25
};

/** The garden started but not yet written: no frame on the door yet. */
export const GARDEN_NO_FRAME: GardenState = {
  "kernel": {
    "path": "/home/sam/Repos/ALF/Colorverse",
    "present": true,
    "wanted": [
      "config.py",
      "engine.py",
      "Zelle.py",
      "Cluster.py",
      "Ring.py",
      "Sphere.py",
      "MetaSphere.py",
      "UniverseNode.py",
      "saturn_hexagon_core.py",
      "saturings.py"
    ],
    "missing": [],
    "files": {
      "config.py": "b349f97a7041f367",
      "engine.py": "2c15bbadf53d51a1",
      "Zelle.py": "dae7d542e79f4faf",
      "Cluster.py": "953335ea76c03886",
      "Ring.py": "2b519111eb495c7c",
      "Sphere.py": "51be69a65b4495cf",
      "MetaSphere.py": "0c1c2cf8361bd927",
      "UniverseNode.py": "fc9a738b2748b022",
      "saturn_hexagon_core.py": "5e3f1ecdd6d7d057",
      "saturings.py": "52ddd5e42f344300"
    },
    "tick_s": 0.25,
    "upstream": [
      {
        "id": "stabiliser-vs-evolution",
        "where": "Zelle.py:38, Zelle.py:130, Zelle.py:150 vs engine.py:72-76, engine.py:156-160",
        "what": "Zelle.update() calls stabilisierung() unconditionally; it pulls every cell toward its neighbours' mean hue by a hardcoded alpha = 0.05, so neighbourhood hue variance decays. engine.py then requires drift > 0.4 AND harmonie < 0.5 for an evolution seed, and builds a NEW Cluster only from 11 seeds at once.",
        "why_it_matters": "\ud83d\udea8 **SET 35 (2026-10-05) \u2014 this entry's CONCLUSION is retracted; its locations and what they say are still true.** For four sets this table read *\u201cthe real blocker is one number\u201d*, and the garden would not breed. By set 35 it bred: **17-18 new Clusters at step 1**; with the set-36 doors open it reaches **129 (90 \u2192 129)** (below). No threshold was ever lowered to get there. `engine.py` marked its seeds at the **end** of `step()`, after seven update passes had already pulled the neighbourhood variance down by a factor of **0.21** \u2014 so the gate was tested against a world that had already closed. Moving the marking to the **head** of `step()` (`engine.py:72-76`) opens it: **a door nobody opened in time, measured as a wall.** The seed gate is also **threefold** (`drift > 0.4` **and** `energy > 0.6` **and** `harmonie < 0.5`), not twofold as this entry says.\n\n**The arithmetic below is history, not a verdict** \u2014 and it was never wrong about what it measured: 1 \u2192 3 \u2192 10 seeds as the harmonie gate opens 0.5 \u2192 0.9 \u2192 0.99, against the 11 a `Cluster` needs. What was wrong was the assumption underneath it, that the gate is tested once, early. It was tested after the variance had already decayed.\n\n**SET 36 (2026-10-09) \u2014 the paragraph that stood here is RETRACTED, and the owner took exactly the decision it named.** It read *\u201cgrowth is one-shot \u2026 there is no source of disorder, so sustained growth needs one \u2014 a semantic decision about the garden\u2019s physics, not a parameter.\u201d* The decision was taken: the **Ring** door smooths its clusters toward the ring\u2019s circular mean hue (`RING_GLAETTUNG`) and re-lights their saturation and brightness (`RING_RELIGHT`); the **Sphere** door paints the free field a travelling hue wave (`SPHERE_MUSTER_*`) and feeds it energy. **The kernel now has a disorder source.** Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters 90 \u2192 130/131/131**, `flat_at = None`, ~760 cells alive and holding colour. **What is still true:** growth is still **one-shot** (the maximum arrives by ~step 50 and holds, because the new clusters consume the free field the Sphere paints on), and every process in the kernel is still a **mean** \u2014 the Sphere\u2019s wave is the disorder source, not a change of nature. Sustained growth is **not** achieved.\n\n**SET 38 (2026-10-16) \u2014 the owner took set 37\u2019s growth factor back, and the crest of the wave decides instead: there is no `WACHSTUMSFAKTOR` in the kernel any more.** Set 37 had put a coin on the gate \u2014 a free cell became a seed only with probability 0.6 while the triple gate held (`engine.py:75`). Measured on the kernel this host reads (seeds 1/7/42, 1500 steps) it cost slightly (**clusters 90 \u2192 126/127/133** against 130/131/131 without it) and it replaced the cell\u2019s own decision with a global die roll \u2014 the owner\u2019s *lost living character*. **The replacement is not a number but the field\u2019s own phase.** The Sphere already paints the free field a travelling wave (`hue = SPHERE_MUSTER_AMP * sin(freq * i + phase)`), so a free cell now carries a seed only when the **crest stands over it** (`z.hue < 180`, the sign half of the painted wave, on `engine.py:75`; the edit is **line-neutral**, so the pinned gate `engine.py:72-76` does not move). The crest travels, so ripeness travels. Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters 90 \u2192 125/126/126**, `flat_at = None`, 822-842 cells alive and holding colour; the burst now **carries over 22 steps to step 172** instead of 16 steps to step 23. **What is still true, and stated rather than implied:** growth is still **one-shot and still not sustained.** The measured reason is no longer the factor \u2014 the free field\u2019s gate closes on `harmonie < 0.5` (a witness inside the gate: 219 of 221 remaining free cells carry `drift > 0.4` and **0** carry `harmonie < 0.5`), and `Cluster.mutation()`\u2019s **edger** consumes free cells (`abs(f.hue - edger.hue) < 20 and f.drift > 0.3` \u2192 `in_cluster`; measured: 313 cells `in_cluster` after step 1, not the 44 of the real new clusters). That consumption is not a pure defect \u2014 switching it off gives 157/160/158 clusters but the colour field dies (spread 95/44/99 against 229/211/180).\n\n\ud83d\udea8 **SET 35 (2026-10-06) \u2014 and the FRAME now contradicts itself, and both arms are true.** `born_converged` says the world can never grow; `cluster - cluster_start` says it grew. Both are measurements, because they answer different questions: a seed needs **11 at once**, and a mean is not a count. The frame therefore carries `convergence_disputed`, `cluster_start` and `grew_at` beside `born_converged`, and every surface prints the disagreement rather than one arm of it. **The owner's own run reached step 3858 with `flat_at = None`** and 111 clusters \u2014 four times the 1000 steps measured the day before, and the furthest any world has been watched on the repaired kernel.\n\n\u26a0\ufe0f **That block was nearly absent from this file.** It had been written into the React **fixture** instead, so the live door served the retracted verdict for a whole set while every React test passed against text the node never sent. A fixture is a *capture*; the moment it is edited by hand it stops being evidence and becomes a copy \u2014 and two surfaces then disagree about one garden, which is set 21's \u201cpresent but wrong evidence\u201d one layer down. **This file is the only writer.**\n\n\ud83d\udea8 **Set 34 retracted this claim twice, and the real blocker is one number.** It used to say the evolution path is unreachable, citing 'best drift 0.0426' \u2014 a figure taken on the pre-repair world, which was dead at birth, so it measured a corpse. Re-measured, the drift story is the WRONG DOOR: drift reaches 0.6886-0.7075 and stays there, above the seed threshold of 0.4 in every phase \u2014 and 0.7 is the death threshold (Zelle.py:86), so the maximum drift is the failing line seen from below, not a sign of health. What closes is the other gate. A seed needs harmonie < 0.5 (engine.py:75), which by Zelle.py:81 means a neighbour-hue variance above 5400 (half of HARMONIE_NULLPUNKT = 10800). In steps 1-6 the variance is there, harmonie falls to 0.2767, and seeds can form. From step 7 on, over 314 steps, harmonie never goes below 0.8289 \u2014 variance 1848 against the 5400 needed, short by a factor of 2.9 \u2014 and not one seed appears. The cause is the line this entry already names: stabilisierung() is called unconditionally (Zelle.py:150) and pulls every cell onto its neighbours' mean, so neighbour variance decays to nothing. alpha is a literal in Zelle.__init__, not a config knob. Reproduction then needs 11 such seeds at once, and the best ever measured is 2. \ud83d\udea8 **And the wall is arithmetic, not tuning:** with the drift gate open, opening the harmonie gate from 0.5 to 0.9 raised the seed count from 1 to 3, and to 0.99 it reached 10 \u2014 still one short of the 11 a Cluster needs. The reason is that stabilisierung() drives neighbour hue variance to EXACTLY 0, so Zelle.py:81 returns harmonie = 1.0 for most cells, and every threshold below 1.0 is then unreachable at once. No value for this threshold repairs it: the quantity it reads is gone. All three defects named in this table trace back to that one call."
      },
      {
        "id": "wander-system-is-a-comment",
        "where": "engine.py:114",
        "what": "the only perturbation source in the kernel is a comment: '# 8. Optional: Wander-System' / '# self.hexagon_wander()'",
        "why_it_matters": "hexagon_wander appears once in the whole kernel and 0 files define it. A comment naming a function that does not exist is a claim, and it is false \u2014 the same shape as set 23's lesson about a comment describing a check."
      },
      {
        "id": "a-cell-dies-for-being-different",
        "where": "Zelle.py:81, Zelle.py:87 vs engine.py:75",
        "what": "Zelle.failsafe() lists 'harmonie < 0.2' among the four conditions that kill a cell outright (hue, saturation, brightness and drift all go to 0), and Zelle.berechne_harmonie() derives harmonie as 1 - min(1, var / HARMONIE_NULLPUNKT) from the spread of its neighbours' hues",
        "why_it_matters": "the quantity a seed needs is a difference and the quantity the kernel kills for is also a difference \u2014 so the death criterion and the growth criterion are the same sign. Measured 2026-10-02 with the kernel's own build_world: 792 of 1000 cells died in their FIRST update, at harmonie 0.0218, from starting hues drawn uniform(0, 360). Set 34's second repair made harmonie an honest 0-1 quantity \u2014 and an honest reading is zero for a newborn cell, because that is what 'your neighbours are all different colours' means. No parameter repairs this: it is the kernel's definition of death, not a scale."
      }
    ],
    "tended": false,
    "tended_note": "Bianca injects nothing. The owner decided the garden is shown as it is, so no cell is perturbed, seeded or 'improved' here.",
    "missing_note": ""
  },
  "frame": {
    "present": false,
    "live": false,
    "stale": false,
    "step": 0,
    "error": "no frame yet \u2014 the garden has not been started"
  },
  "child_running": false,
  "tick_s": 0.25
};

/** The kernel is not there — the garden deflects instead of inventing. */
export const GARDEN_NO_KERNEL: GardenState = {
  "kernel": {
    "path": "/tmp/opencode/gfx/gfx-nokernel",
    "present": false,
    "wanted": [
      "config.py",
      "engine.py",
      "Zelle.py",
      "Cluster.py",
      "Ring.py",
      "Sphere.py",
      "MetaSphere.py",
      "UniverseNode.py",
      "saturn_hexagon_core.py",
      "saturings.py"
    ],
    "missing": [
      "config.py",
      "engine.py",
      "Zelle.py",
      "Cluster.py",
      "Ring.py",
      "Sphere.py",
      "MetaSphere.py",
      "UniverseNode.py",
      "saturn_hexagon_core.py",
      "saturings.py"
    ],
    "files": {},
    "tick_s": 0.25,
    "upstream": [
      {
        "id": "stabiliser-vs-evolution",
        "where": "Zelle.py:38, Zelle.py:130, Zelle.py:150 vs engine.py:72-76, engine.py:156-160",
        "what": "Zelle.update() calls stabilisierung() unconditionally; it pulls every cell toward its neighbours' mean hue by a hardcoded alpha = 0.05, so neighbourhood hue variance decays. engine.py then requires drift > 0.4 AND harmonie < 0.5 for an evolution seed, and builds a NEW Cluster only from 11 seeds at once.",
        "why_it_matters": "\ud83d\udea8 **SET 35 (2026-10-05) \u2014 this entry's CONCLUSION is retracted; its locations and what they say are still true.** For four sets this table read *\u201cthe real blocker is one number\u201d*, and the garden would not breed. By set 35 it bred: **17-18 new Clusters at step 1**; with the set-36 doors open it reaches **129 (90 \u2192 129)** (below). No threshold was ever lowered to get there. `engine.py` marked its seeds at the **end** of `step()`, after seven update passes had already pulled the neighbourhood variance down by a factor of **0.21** \u2014 so the gate was tested against a world that had already closed. Moving the marking to the **head** of `step()` (`engine.py:72-76`) opens it: **a door nobody opened in time, measured as a wall.** The seed gate is also **threefold** (`drift > 0.4` **and** `energy > 0.6` **and** `harmonie < 0.5`), not twofold as this entry says.\n\n**The arithmetic below is history, not a verdict** \u2014 and it was never wrong about what it measured: 1 \u2192 3 \u2192 10 seeds as the harmonie gate opens 0.5 \u2192 0.9 \u2192 0.99, against the 11 a `Cluster` needs. What was wrong was the assumption underneath it, that the gate is tested once, early. It was tested after the variance had already decayed.\n\n**SET 36 (2026-10-09) \u2014 the paragraph that stood here is RETRACTED, and the owner took exactly the decision it named.** It read *\u201cgrowth is one-shot \u2026 there is no source of disorder, so sustained growth needs one \u2014 a semantic decision about the garden\u2019s physics, not a parameter.\u201d* The decision was taken: the **Ring** door smooths its clusters toward the ring\u2019s circular mean hue (`RING_GLAETTUNG`) and re-lights their saturation and brightness (`RING_RELIGHT`); the **Sphere** door paints the free field a travelling hue wave (`SPHERE_MUSTER_*`) and feeds it energy. **The kernel now has a disorder source.** Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters 90 \u2192 130/131/131**, `flat_at = None`, ~760 cells alive and holding colour. **What is still true:** growth is still **one-shot** (the maximum arrives by ~step 50 and holds, because the new clusters consume the free field the Sphere paints on), and every process in the kernel is still a **mean** \u2014 the Sphere\u2019s wave is the disorder source, not a change of nature. Sustained growth is **not** achieved.\n\n**SET 38 (2026-10-16) \u2014 the owner took set 37\u2019s growth factor back, and the crest of the wave decides instead: there is no `WACHSTUMSFAKTOR` in the kernel any more.** Set 37 had put a coin on the gate \u2014 a free cell became a seed only with probability 0.6 while the triple gate held (`engine.py:75`). Measured on the kernel this host reads (seeds 1/7/42, 1500 steps) it cost slightly (**clusters 90 \u2192 126/127/133** against 130/131/131 without it) and it replaced the cell\u2019s own decision with a global die roll \u2014 the owner\u2019s *lost living character*. **The replacement is not a number but the field\u2019s own phase.** The Sphere already paints the free field a travelling wave (`hue = SPHERE_MUSTER_AMP * sin(freq * i + phase)`), so a free cell now carries a seed only when the **crest stands over it** (`z.hue < 180`, the sign half of the painted wave, on `engine.py:75`; the edit is **line-neutral**, so the pinned gate `engine.py:72-76` does not move). The crest travels, so ripeness travels. Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters 90 \u2192 125/126/126**, `flat_at = None`, 822-842 cells alive and holding colour; the burst now **carries over 22 steps to step 172** instead of 16 steps to step 23. **What is still true, and stated rather than implied:** growth is still **one-shot and still not sustained.** The measured reason is no longer the factor \u2014 the free field\u2019s gate closes on `harmonie < 0.5` (a witness inside the gate: 219 of 221 remaining free cells carry `drift > 0.4` and **0** carry `harmonie < 0.5`), and `Cluster.mutation()`\u2019s **edger** consumes free cells (`abs(f.hue - edger.hue) < 20 and f.drift > 0.3` \u2192 `in_cluster`; measured: 313 cells `in_cluster` after step 1, not the 44 of the real new clusters). That consumption is not a pure defect \u2014 switching it off gives 157/160/158 clusters but the colour field dies (spread 95/44/99 against 229/211/180).\n\n\ud83d\udea8 **SET 35 (2026-10-06) \u2014 and the FRAME now contradicts itself, and both arms are true.** `born_converged` says the world can never grow; `cluster - cluster_start` says it grew. Both are measurements, because they answer different questions: a seed needs **11 at once**, and a mean is not a count. The frame therefore carries `convergence_disputed`, `cluster_start` and `grew_at` beside `born_converged`, and every surface prints the disagreement rather than one arm of it. **The owner's own run reached step 3858 with `flat_at = None`** and 111 clusters \u2014 four times the 1000 steps measured the day before, and the furthest any world has been watched on the repaired kernel.\n\n\u26a0\ufe0f **That block was nearly absent from this file.** It had been written into the React **fixture** instead, so the live door served the retracted verdict for a whole set while every React test passed against text the node never sent. A fixture is a *capture*; the moment it is edited by hand it stops being evidence and becomes a copy \u2014 and two surfaces then disagree about one garden, which is set 21's \u201cpresent but wrong evidence\u201d one layer down. **This file is the only writer.**\n\n\ud83d\udea8 **Set 34 retracted this claim twice, and the real blocker is one number.** It used to say the evolution path is unreachable, citing 'best drift 0.0426' \u2014 a figure taken on the pre-repair world, which was dead at birth, so it measured a corpse. Re-measured, the drift story is the WRONG DOOR: drift reaches 0.6886-0.7075 and stays there, above the seed threshold of 0.4 in every phase \u2014 and 0.7 is the death threshold (Zelle.py:86), so the maximum drift is the failing line seen from below, not a sign of health. What closes is the other gate. A seed needs harmonie < 0.5 (engine.py:75), which by Zelle.py:81 means a neighbour-hue variance above 5400 (half of HARMONIE_NULLPUNKT = 10800). In steps 1-6 the variance is there, harmonie falls to 0.2767, and seeds can form. From step 7 on, over 314 steps, harmonie never goes below 0.8289 \u2014 variance 1848 against the 5400 needed, short by a factor of 2.9 \u2014 and not one seed appears. The cause is the line this entry already names: stabilisierung() is called unconditionally (Zelle.py:150) and pulls every cell onto its neighbours' mean, so neighbour variance decays to nothing. alpha is a literal in Zelle.__init__, not a config knob. Reproduction then needs 11 such seeds at once, and the best ever measured is 2. \ud83d\udea8 **And the wall is arithmetic, not tuning:** with the drift gate open, opening the harmonie gate from 0.5 to 0.9 raised the seed count from 1 to 3, and to 0.99 it reached 10 \u2014 still one short of the 11 a Cluster needs. The reason is that stabilisierung() drives neighbour hue variance to EXACTLY 0, so Zelle.py:81 returns harmonie = 1.0 for most cells, and every threshold below 1.0 is then unreachable at once. No value for this threshold repairs it: the quantity it reads is gone. All three defects named in this table trace back to that one call."
      },
      {
        "id": "wander-system-is-a-comment",
        "where": "engine.py:114",
        "what": "the only perturbation source in the kernel is a comment: '# 8. Optional: Wander-System' / '# self.hexagon_wander()'",
        "why_it_matters": "hexagon_wander appears once in the whole kernel and 0 files define it. A comment naming a function that does not exist is a claim, and it is false \u2014 the same shape as set 23's lesson about a comment describing a check."
      },
      {
        "id": "a-cell-dies-for-being-different",
        "where": "Zelle.py:81, Zelle.py:87 vs engine.py:75",
        "what": "Zelle.failsafe() lists 'harmonie < 0.2' among the four conditions that kill a cell outright (hue, saturation, brightness and drift all go to 0), and Zelle.berechne_harmonie() derives harmonie as 1 - min(1, var / HARMONIE_NULLPUNKT) from the spread of its neighbours' hues",
        "why_it_matters": "the quantity a seed needs is a difference and the quantity the kernel kills for is also a difference \u2014 so the death criterion and the growth criterion are the same sign. Measured 2026-10-02 with the kernel's own build_world: 792 of 1000 cells died in their FIRST update, at harmonie 0.0218, from starting hues drawn uniform(0, 360). Set 34's second repair made harmonie an honest 0-1 quantity \u2014 and an honest reading is zero for a newborn cell, because that is what 'your neighbours are all different colours' means. No parameter repairs this: it is the kernel's definition of death, not a scale."
      }
    ],
    "tended": false,
    "tended_note": "Bianca injects nothing. The owner decided the garden is shown as it is, so no cell is perturbed, seeded or 'improved' here.",
    "missing_note": "Der Garten hat keinen Boden: /tmp/opencode/gfx/gfx-nokernel gibt es nicht. Lege dort die 10 Dateien ab (config.py, engine.py, Zelle.py, Cluster.py, \u2026) \u2014 dann w\u00e4chst er von selbst."
  },
  "frame": {
    "present": false,
    "live": false,
    "stale": false,
    "step": 0,
    "error": "no frame yet \u2014 the garden has not been started"
  },
  "child_running": false,
  "tick_s": 0.25
};

/**
 * 🚨 **A SPLICED frame — the one payload here that is not a capture, and the
 * only typed number in this file's generator.**
 *
 * `GARDEN_LIVE` cannot feed two branches of `GardenView`: on the current kernel
 * `flat_at` does not occur (1000 steps measured here, **3858** on the owner's
 * run) and `convergence_disputed` is `true` while `born_converged` is also
 * `true`. Both are the truth, so testing the `born_converged` branch or the
 * `flat_at` notice against it would assert something false — and *unreachable*
 * lines are how a screen keeps looking repaired while nothing checks it.
 *
 * So this describes the kernel **before** `Zelle.py:89-101` / `:109-117`, the
 * state set 34 measured across 28 worlds. It is derived from `GARDEN_LIVE` with
 * four named overrides, not hand-written: `cluster_start = cluster` makes
 * `convergence_disputed = false` **consistent** (a world that never grew cannot
 * also have grown), `grew_at = null`, and `flat_at` is the one typed number,
 * because no live process produces it any more.
 *
 * The precedent is `AGENT_REFUSED_TOOL` in the agent fixture — a real governor
 * verdict spliced onto a real run, because the door cannot be made to produce
 * it. **Spliced, declared, derived — never silently typed.**
 */

export const GARDEN_PRE_V35: GardenState = {
  "kernel": {
    "path": "/home/sam/Repos/ALF/Colorverse",
    "present": true,
    "wanted": [
      "config.py",
      "engine.py",
      "Zelle.py",
      "Cluster.py",
      "Ring.py",
      "Sphere.py",
      "MetaSphere.py",
      "UniverseNode.py",
      "saturn_hexagon_core.py",
      "saturings.py"
    ],
    "missing": [],
    "files": {
      "config.py": "b349f97a7041f367",
      "engine.py": "2c15bbadf53d51a1",
      "Zelle.py": "dae7d542e79f4faf",
      "Cluster.py": "953335ea76c03886",
      "Ring.py": "2b519111eb495c7c",
      "Sphere.py": "51be69a65b4495cf",
      "MetaSphere.py": "0c1c2cf8361bd927",
      "UniverseNode.py": "fc9a738b2748b022",
      "saturn_hexagon_core.py": "5e3f1ecdd6d7d057",
      "saturings.py": "52ddd5e42f344300"
    },
    "tick_s": 0.25,
    "upstream": [
      {
        "id": "stabiliser-vs-evolution",
        "where": "Zelle.py:38, Zelle.py:130, Zelle.py:150 vs engine.py:72-76, engine.py:156-160",
        "what": "Zelle.update() calls stabilisierung() unconditionally; it pulls every cell toward its neighbours' mean hue by a hardcoded alpha = 0.05, so neighbourhood hue variance decays. engine.py then requires drift > 0.4 AND harmonie < 0.5 for an evolution seed, and builds a NEW Cluster only from 11 seeds at once.",
        "why_it_matters": "\ud83d\udea8 **SET 35 (2026-10-05) \u2014 this entry's CONCLUSION is retracted; its locations and what they say are still true.** For four sets this table read *\u201cthe real blocker is one number\u201d*, and the garden would not breed. By set 35 it bred: **17-18 new Clusters at step 1**; with the set-36 doors open it reaches **129 (90 \u2192 129)** (below). No threshold was ever lowered to get there. `engine.py` marked its seeds at the **end** of `step()`, after seven update passes had already pulled the neighbourhood variance down by a factor of **0.21** \u2014 so the gate was tested against a world that had already closed. Moving the marking to the **head** of `step()` (`engine.py:72-76`) opens it: **a door nobody opened in time, measured as a wall.** The seed gate is also **threefold** (`drift > 0.4` **and** `energy > 0.6` **and** `harmonie < 0.5`), not twofold as this entry says.\n\n**The arithmetic below is history, not a verdict** \u2014 and it was never wrong about what it measured: 1 \u2192 3 \u2192 10 seeds as the harmonie gate opens 0.5 \u2192 0.9 \u2192 0.99, against the 11 a `Cluster` needs. What was wrong was the assumption underneath it, that the gate is tested once, early. It was tested after the variance had already decayed.\n\n**SET 36 (2026-10-09) \u2014 the paragraph that stood here is RETRACTED, and the owner took exactly the decision it named.** It read *\u201cgrowth is one-shot \u2026 there is no source of disorder, so sustained growth needs one \u2014 a semantic decision about the garden\u2019s physics, not a parameter.\u201d* The decision was taken: the **Ring** door smooths its clusters toward the ring\u2019s circular mean hue (`RING_GLAETTUNG`) and re-lights their saturation and brightness (`RING_RELIGHT`); the **Sphere** door paints the free field a travelling hue wave (`SPHERE_MUSTER_*`) and feeds it energy. **The kernel now has a disorder source.** Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters 90 \u2192 130/131/131**, `flat_at = None`, ~760 cells alive and holding colour. **What is still true:** growth is still **one-shot** (the maximum arrives by ~step 50 and holds, because the new clusters consume the free field the Sphere paints on), and every process in the kernel is still a **mean** \u2014 the Sphere\u2019s wave is the disorder source, not a change of nature. Sustained growth is **not** achieved.\n\n**SET 38 (2026-10-16) \u2014 the owner took set 37\u2019s growth factor back, and the crest of the wave decides instead: there is no `WACHSTUMSFAKTOR` in the kernel any more.** Set 37 had put a coin on the gate \u2014 a free cell became a seed only with probability 0.6 while the triple gate held (`engine.py:75`). Measured on the kernel this host reads (seeds 1/7/42, 1500 steps) it cost slightly (**clusters 90 \u2192 126/127/133** against 130/131/131 without it) and it replaced the cell\u2019s own decision with a global die roll \u2014 the owner\u2019s *lost living character*. **The replacement is not a number but the field\u2019s own phase.** The Sphere already paints the free field a travelling wave (`hue = SPHERE_MUSTER_AMP * sin(freq * i + phase)`), so a free cell now carries a seed only when the **crest stands over it** (`z.hue < 180`, the sign half of the painted wave, on `engine.py:75`; the edit is **line-neutral**, so the pinned gate `engine.py:72-76` does not move). The crest travels, so ripeness travels. Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters 90 \u2192 125/126/126**, `flat_at = None`, 822-842 cells alive and holding colour; the burst now **carries over 22 steps to step 172** instead of 16 steps to step 23. **What is still true, and stated rather than implied:** growth is still **one-shot and still not sustained.** The measured reason is no longer the factor \u2014 the free field\u2019s gate closes on `harmonie < 0.5` (a witness inside the gate: 219 of 221 remaining free cells carry `drift > 0.4` and **0** carry `harmonie < 0.5`), and `Cluster.mutation()`\u2019s **edger** consumes free cells (`abs(f.hue - edger.hue) < 20 and f.drift > 0.3` \u2192 `in_cluster`; measured: 313 cells `in_cluster` after step 1, not the 44 of the real new clusters). That consumption is not a pure defect \u2014 switching it off gives 157/160/158 clusters but the colour field dies (spread 95/44/99 against 229/211/180).\n\n\ud83d\udea8 **SET 35 (2026-10-06) \u2014 and the FRAME now contradicts itself, and both arms are true.** `born_converged` says the world can never grow; `cluster - cluster_start` says it grew. Both are measurements, because they answer different questions: a seed needs **11 at once**, and a mean is not a count. The frame therefore carries `convergence_disputed`, `cluster_start` and `grew_at` beside `born_converged`, and every surface prints the disagreement rather than one arm of it. **The owner's own run reached step 3858 with `flat_at = None`** and 111 clusters \u2014 four times the 1000 steps measured the day before, and the furthest any world has been watched on the repaired kernel.\n\n\u26a0\ufe0f **That block was nearly absent from this file.** It had been written into the React **fixture** instead, so the live door served the retracted verdict for a whole set while every React test passed against text the node never sent. A fixture is a *capture*; the moment it is edited by hand it stops being evidence and becomes a copy \u2014 and two surfaces then disagree about one garden, which is set 21's \u201cpresent but wrong evidence\u201d one layer down. **This file is the only writer.**\n\n\ud83d\udea8 **Set 34 retracted this claim twice, and the real blocker is one number.** It used to say the evolution path is unreachable, citing 'best drift 0.0426' \u2014 a figure taken on the pre-repair world, which was dead at birth, so it measured a corpse. Re-measured, the drift story is the WRONG DOOR: drift reaches 0.6886-0.7075 and stays there, above the seed threshold of 0.4 in every phase \u2014 and 0.7 is the death threshold (Zelle.py:86), so the maximum drift is the failing line seen from below, not a sign of health. What closes is the other gate. A seed needs harmonie < 0.5 (engine.py:75), which by Zelle.py:81 means a neighbour-hue variance above 5400 (half of HARMONIE_NULLPUNKT = 10800). In steps 1-6 the variance is there, harmonie falls to 0.2767, and seeds can form. From step 7 on, over 314 steps, harmonie never goes below 0.8289 \u2014 variance 1848 against the 5400 needed, short by a factor of 2.9 \u2014 and not one seed appears. The cause is the line this entry already names: stabilisierung() is called unconditionally (Zelle.py:150) and pulls every cell onto its neighbours' mean, so neighbour variance decays to nothing. alpha is a literal in Zelle.__init__, not a config knob. Reproduction then needs 11 such seeds at once, and the best ever measured is 2. \ud83d\udea8 **And the wall is arithmetic, not tuning:** with the drift gate open, opening the harmonie gate from 0.5 to 0.9 raised the seed count from 1 to 3, and to 0.99 it reached 10 \u2014 still one short of the 11 a Cluster needs. The reason is that stabilisierung() drives neighbour hue variance to EXACTLY 0, so Zelle.py:81 returns harmonie = 1.0 for most cells, and every threshold below 1.0 is then unreachable at once. No value for this threshold repairs it: the quantity it reads is gone. All three defects named in this table trace back to that one call."
      },
      {
        "id": "wander-system-is-a-comment",
        "where": "engine.py:114",
        "what": "the only perturbation source in the kernel is a comment: '# 8. Optional: Wander-System' / '# self.hexagon_wander()'",
        "why_it_matters": "hexagon_wander appears once in the whole kernel and 0 files define it. A comment naming a function that does not exist is a claim, and it is false \u2014 the same shape as set 23's lesson about a comment describing a check."
      },
      {
        "id": "a-cell-dies-for-being-different",
        "where": "Zelle.py:81, Zelle.py:87 vs engine.py:75",
        "what": "Zelle.failsafe() lists 'harmonie < 0.2' among the four conditions that kill a cell outright (hue, saturation, brightness and drift all go to 0), and Zelle.berechne_harmonie() derives harmonie as 1 - min(1, var / HARMONIE_NULLPUNKT) from the spread of its neighbours' hues",
        "why_it_matters": "the quantity a seed needs is a difference and the quantity the kernel kills for is also a difference \u2014 so the death criterion and the growth criterion are the same sign. Measured 2026-10-02 with the kernel's own build_world: 792 of 1000 cells died in their FIRST update, at harmonie 0.0218, from starting hues drawn uniform(0, 360). Set 34's second repair made harmonie an honest 0-1 quantity \u2014 and an honest reading is zero for a newborn cell, because that is what 'your neighbours are all different colours' means. No parameter repairs this: it is the kernel's definition of death, not a scale."
      }
    ],
    "tended": false,
    "tended_note": "Bianca injects nothing. The owner decided the garden is shown as it is, so no cell is perturbed, seeded or 'improved' here.",
    "missing_note": ""
  },
  "frame": {
    "step": 220,
    "cells": 1000,
    "hue_mean": 183.3558153566749,
    "harm": 0.9999081636635819,
    "drift": 0.028399390030163712,
    "energie": 0.603361571707778,
    "spread": 222.633419775635,
    "keime": 11,
    "cluster": 125,
    "cluster_start": 125,
    "grew_at": null,
    "convergence_disputed": false,
    "readout": "[ENGINE] step=220 harm=1.00 drift=0.01 stoer=2.26",
    "thresholds": {
      "drift": 0.4,
      "energie": 0.6
    },
    "born_converged": true,
    "converged_at": 1,
    "flat_at": 252,
    "files": {
      "config.py": "b349f97a7041f367",
      "engine.py": "2c15bbadf53d51a1",
      "Zelle.py": "dae7d542e79f4faf",
      "Cluster.py": "953335ea76c03886",
      "Ring.py": "2b519111eb495c7c",
      "Sphere.py": "51be69a65b4495cf",
      "MetaSphere.py": "0c1c2cf8361bd927",
      "UniverseNode.py": "fc9a738b2748b022",
      "saturn_hexagon_core.py": "5e3f1ecdd6d7d057",
      "saturings.py": "52ddd5e42f344300"
    },
    "error": null,
    "written": 1792184907.1326556,
    "present": true,
    "age_s": 0,
    "fresh": true,
    "child_running": true,
    "live": true,
    "stale": false
  },
  "child_running": true,
  "tick_s": 0.25
};
