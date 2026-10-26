/**
 * The sovereign doors, as the React surface sees them.
 *
 * One writer per truth, on this side too: no page calls `fetch` against the
 * node directly, so the deny/503/partial contract can only be implemented
 * once. The types below were read off the LIVE node, not guessed from the
 * Python — a shape invented here would be a shape that lies.
 *
 * The node is a separate localhost origin from this app, which is why the
 * sovereign API answers loopback CORS (set 13, `LOOPBACK_ORIGIN_RE`).
 */

// ── shapes, read off the running node ──────────────────────────────────────

export interface Oracle {
  on?: boolean;
  vote: string;
  /** `readonly` for the same reason a verdict's terms are: the eye's grounds
   *  are its record, not a scratch buffer. Also lets a `as const` live capture
   *  satisfy this type without a cast. */
  readonly grounds?: readonly string[];
  resonance?: number;
  /** The second eye advises. It never binds. */
  advisory: boolean;
  binding: boolean;
  holder?: string;
}

export interface CycleState {
  sonne: number;
  mond: number;
  tag: number;
  grundmodus: string;
  stimmung: string;
  fokus: string;
}

/**
 * The second eye as the **identity door** reports it, which is not the same
 * thing as a vote.
 *
 * `/context` answers "is the eye on, and can it bind?" — four boundary fields
 * and no `vote`, because the eye has not been asked anything yet. `Oracle`
 * below requires a `vote`, and this capture caught that: a live `/context` did
 * not type-check against `Context`, because a door that had never voted was
 * required to carry a vote.
 *
 * The alternative — making `vote` optional on `Oracle` — would have been
 * quieter and worse. It would have let a *real* verdict's missing vote pass
 * unnoticed, and `vote` is the field a refusal is checked for. So the two
 * shapes get two types, and the one that carries a judgement keeps saying so.
 */
export interface OracleBoundary {
  on: boolean;
  /** The eye advises. It never binds. */
  advisory: boolean;
  binding: boolean;
  holder?: string;
}

export interface Context {
  capability: {
    mode: string;
    feature_files: string[];
    llm_bridge: boolean;
    werte_teilen: boolean;
  };
  cycle_state: CycleState;
  gold_manifest: boolean;
  /** The boundary, not a vote — see `OracleBoundary`. */
  oracle: OracleBoundary;
  self_check: {
    voice: string;
    engine: string;
    engine_why: string;
    contract_holds: boolean;
    verified: number;
    untraceable: number;
    failures: number;
  };
  /**
   * Which languages she answers in, from `voice.py` (set 26). Declared here so
   * a picker has one source: a component that hardcoded `['de', 'en']` would
   * be a second writer, and adding a language on the node would look like it
   * had not taken effect anywhere in the app.
   */
  languages: LanguageOption[];
}

/** One language, as `/context` reports it. `default` is the door's, not ours. */
export interface LanguageOption {
  code: string;
  name: string;
  default?: boolean;
}

export interface Verdict {
  verdict: string;
  alignment: number;
  risk: number;
  gold_values_loaded?: boolean;
  gold_source: string;
  // `readonly`, because a verdict is evidence: nothing on this surface may
  // edit what the governor said. It also means a `as const` capture from a
  // live node type-checks as-is, so a real payload can be handed straight to
  // a component without a cast — which is the point of capturing them.
  readonly gold_hits: readonly string[];
  readonly risk_hits: readonly string[];
  /**
   * What the request LACKS — the gate's answer to "was ist dir fehl?".
   *
   * Optional, because a `Spore` extends this shape and a reply read does not
   * carry it. It is never a recipe: naming the gold values does not release a
   * held request, because risk is judged first — so on a refusal this states
   * the boundary and forecloses the workaround rather than offering one.
   */
  readonly missing?: readonly string[];
  oracle: Oracle;
}

/**
 * What the node sends for a REPLY READ — the governor's opinion of the words
 * actually written, as opposed to a full verdict on a request.
 *
 * This is deliberately lighter than `Verdict`, and the two ask doors are
 * uniform about it (`api.py` sends exactly these three keys for both
 * `/v1/ask` and `/v1/chat`). A reply read answers "what did the governor
 * think of these words, what tripped it, and did the eye have anything to
 * say" — it is not a second provenance manifest, and the gold values that
 * governed the request are the same ones on `governance`.
 *
 * It was previously typed as a full `Verdict`, which was a lie: a surface
 * that read `reply_governance.gold_source` would have rendered the literal
 * string `undefined` into a governance panel, believing the node had sent it.
 * Typing it as its own shape makes that a **compile error** instead.
 */
export interface ReplyRead {
  verdict: string;
  readonly risk_hits: readonly string[];
  oracle: Oracle;
}

export interface Health {
  ok: boolean;
  name: string;
  version: string;
  soul: string;
  cycle: CycleState;
  gold_loaded: boolean;
}

export interface Today {
  date: string;
  cycle: CycleState;
  gold_loaded: boolean;
  ledger_today: Record<string, number>;
  ledger_total: number;
  refusals: number;
  recent: { type: string; when: string; message: string }[];
  memory: { documents: number; db: string };
  idle: IdleStatus;
  engine: string;
  engine_why: string;
  escalation: { verdict: string; streak: number; guidance: string };
  eye: {
    witnessed: number;
    votes: Record<string, number>;
    dissent: string[];
    dissent_count: number;
  };
  options: string[];
  next: string;
  previous_next: string;
}

export interface IdleStatus {
  running: boolean;
  pid: number;
  pidfile: string;
  units_today: number;
  units_audited: number;
}

export interface Urasil {
  node: string;
  cycle: CycleState;
  cycle_available: boolean;
  levels: { level: string; name: string; question: string; voice: string }[];
  assessments: Record<string, { level: string; name: string; note: string }>;
  stages: { name: string; gate_question: string }[];
  source: { alf_root: string; infinity: string; available: boolean };
  persona: { name: string; soul: string };
  /**
   * The three deliberating voices, as NAMES.
   *
   * `trialog.uracil_view` sends `VOICE_NAMES` — a list of plain strings; the
   * live node returned `["Jarvis", "Bianca", "Urasil_light"]`. This was typed
   * as `{ name, soul }[]`, which is the same class of lie set 16 found in
   * `reply_governance`: the obvious code (`voices.map(v => v.name)`) reads a
   * property off a string and yields `undefined` three times, so nobody ever
   * rendered the voices and the type quietly prevented the tab from showing
   * that three voices deliberate at all.
   *
   * The persona above is the one that is an object, because it carries `soul`.
   * One name list, one persona object — and the distinction is now in the type
   * instead of in someone's memory.
   */
  voices: string[];
}

export interface Manifest {
  node: string;
  hub_version: string;
  identity: {
    voice: string;
    engine: string;
    engine_why: string;
    gold_manifest: string;
    gold_loaded: boolean;
  };
  capability: { mode: string; surface: string; oracle: Oracle };
  cycle: { grundmodus: string; stimmung: string; fokus: string };
  contract: { holds: boolean; verified: number; untraceable: number; failures: number };
  gold: string[];
  public_dir: string;
  pulse: {
    audits_today: number;
    spore_received: number;
    spore_stored: number;
    spore_denied: number;
    spores_total: number;
  };
  time: string;
}

/**
 * A spore carries a full verdict plus its own bookkeeping — so it IS a verdict,
 * and it is declared as one.
 *
 * This was previously spelled out field by field, which forced `NodeNetPage` to
 * write a `verdictOf(spore)` adapter that copied seven fields by hand before
 * handing them to `VerdictCard`. Such an adapter compiles happily against a
 * shape it no longer matches: add a field to `Verdict` and the shim is still
 * valid TypeScript, and the card simply stops showing the new field. Extending
 * the interface makes that impossible — a spore can be passed to the card
 * directly, and a missing field is a compile error at the door instead of a
 * silent hole in a governance panel.
 *
 * `oracle` is optional here and only here, and that is a fact about the disk
 * rather than about the type's convenience. Reading the live inbox on this
 * node returns a spore with `source: "peer-beta"` and **no `oracle` key at
 * all** — it was stored before the second eye existed (roadmap item 8). It is
 * a real record, not a malformed payload, so demanding an eye on it would be
 * demanding a field history does not have. A fresh verdict always has one,
 * which is why `Verdict.oracle` stays required and this is `Omit`-ed and
 * re-declared optional rather than loosened globally.
 *
 * The rendering consequence is deliberate: a pre-eye spore shows no eye, and
 * the reader can see that it shows none. Inventing an eye for a record that
 * never had one would be fabricating a vote.
 */
export interface Spore extends Omit<Verdict, 'oracle'> {
  stamp: string;
  kind: string;
  source: string;
  text: string;
  oracle?: Oracle;
}

/** Anything a `VerdictCard` will draw: a request read, a reply read, a spore. */
export type AnyVerdict = Verdict | ReplyRead | Spore;

export interface TrialogTurn {
  round: number;
  voice: string;
  /**
   * Set 29: the model this turn was actually generated through. A `model` that
   * could disagree with `Trialog.models[voice]` would let a record claim a
   * per-voice model that was never used, so the type is required on the turn and
   * not derived from the map.
   */
  model: string;
  text: string;
  verdict: string;
  risk_hits: string[];
  gold_hits: string[];
  gold_source: string;
  oracle: Oracle;
}

/**
 * Set 28's read model, spelled out from what the node sends. `criterion` is the
 * sentence that says *how* connection is judged — by what one voice alone
 * brought, not by what all of them agreed on — and `not_measured` names what no
 * instrument here can measure. Both are on the payload, so a screen cannot
 * quietly substitute a count for a relation, or read agreement into a field that
 * says it is not measurable.
 */
export interface TrialogComplementarity {
  criterion: string;
  measure: string;
  not_measured: string;
  given: Record<string, string[]>;
  shared: Record<string, string[]>;
  shared_is_not_the_criterion: boolean;
  uncarried: string[];
  voices: string[];
}

export interface TrialogGovernance {
  turns: number;
  off_limit: number;
  gold_aligned: number;
  neutral: number;
  counts: Record<string, number>;
  /**
   * Set 29: did the run produce more than one verdict, and how many; plus the
   * verdicts each voice held across every round. The measurement behind the
   * per-voice model field: over four rounds the twelve verdicts never once
   * moved, and until this existed the only way to see that was twelve rows by
   * hand.
   */
  verdicts_moved: boolean;
  distinct_verdicts: number;
  per_voice_verdicts: Record<string, string[]>;
}

export interface Trialog {
  topic: string;
  rounds: number;
  model: string;
  /** Which model each voice spoke through — the resolved map, never the request. */
  models: Record<string, string>;
  /**
   * `true` when all three voices shared one model: one voice in three masks.
   * The falsifier for set 29's question, readable at a glance.
   */
  same_model_everywhere: boolean;
  voices: string[];
  transcript: string[];
  turns: TrialogTurn[];
  governance: TrialogGovernance;
  /**
   * Set 28's read model: who brought what the others did not — resonance as a
   * relation, not a count. 🚨 It has been on the door since set 28 and was
   * missing from this type until a set-29 live capture was written against the
   * type and the compiler said so. A field the node sends and the type does not
   * know is a field the front end has never checked.
   */
  complementarity?: TrialogComplementarity;
  topic_governance: Verdict;
  eye_warned: number;
  summary: string;
  completed: boolean;
  saved: string;
}

export interface TrialogIndexEntry {
  name: string;
  voices: string[];
  opening_voice: string;
  opening: string;
  lines: number;
  bytes: number;
  saved: string;
}

// ── the working session (set 30) ─────────────────────────────────────────────
//
// Every field below was read off a **live capture** from the running node, not
// written from the Python and hoped for. The one that bit: a turn's `model` is
// `string | null`, because the owner's own turn has no model behind it. Typed as
// `string` it would have been a lie the compiler enforced — and the face, which
// has no compiler, printed "undefined" for it on the first run.

/**
 * One line of a session's record. NOT `TrialogTurn`: a session turn carries the
 * clock, may carry no model at all (the owner's turn), and may carry a `note`
 * instead of a verdict when a run ended without writing the close. A
 * deliberation turn never has any of those, so a shared type would have been
 * wrong in three directions at once.
 */
export interface SessionTurn {
  round: number;
  voice: string;
  at: string;
  /** `null` for the owner's turn — nobody's weights wrote that. */
  model: string | null;
  text: string;
  verdict: string;
  risk_hits: string[];
  gold_hits: string[];
  gold_source: string | null;
  oracle: Oracle;
  /**
   * Present only on the line a run writes when it found the session already
   * closed by somebody else. It is the record's way of keeping a fact that
   * would otherwise be lost by not overwriting a human's decision.
   */
  note?: string;
  /** Present when the engine failed during this voice's turn. */
  stopped?: string;
}

/**
 * The session's memory. **Derived from `turns` on every read** — there is no
 * `memory.json` and no counter stored beside the record, because a run killed
 * between appending a turn and writing the state used to leave the two
 * disagreeing (one turn on disk, `calls: 0` beside it).
 */
export interface SessionMemory {
  rounds: number;
  calls: number;
  counts: Record<string, number>;
  distinct_verdicts: number;
  verdicts_moved: boolean;
  per_voice_verdicts: Record<string, string[]>;
  per_voice_models: Record<string, string>;
  gold_carried: Record<string, string[]>;
  eye_warned: number;
  owner_turns: number;
  held_owner_turns: number;
  /** The last sentence of each voice — NOT the transcript, which grows quadratically. */
  last: Record<string, string>;
  /** What this memory carries, in words. */
  carries: string;
  /**
   * 🚨 Required, and it is the field with no instrument behind it. Answer 9 C
   * asked for moments of understanding; nothing here can know one, so the record
   * says so rather than growing an `understood: true`.
   */
  cannot_record: string;
}

/**
 * The plan. Note what is **absent**: `calls` and `rounds`. They are derived,
 * and a number kept beside the record is a number that can drift from it.
 */
export interface SessionState {
  id: string;
  topic: string;
  goal: string;
  stop_when: string;
  status: string;
  started: string;
  ceiling: number;
  model: string;
  models: Record<string, string>;
  voices: string[];
  pid: number | null;
  /** `null`, a timestamp, or `false`/`true` depending on the node's version. */
  closed: string | null;
  closed_because: string | null;
  /** `process`, `owner` or `door` — a person's close outranks a process exit. */
  closed_by?: string | null;
  stop_requested?: { reason: string; at: string } | null;
  /**
   * 🚨 Whether the run has installed its stop handler yet. A signal sent before
   * this is not a nudge but a kill (measured: 3 of 14 spawns), so the door
   * signals only when this is true and leans on the record otherwise.
   */
  ready?: boolean;
  /** When the run announced it could hear a stop — the handshake's own clock. */
  ready_at?: string;
  // 🚨 NO `running` here. The state is the record, and nothing derived belongs
  // in it: the detail door used to inject a boolean into this object while the
  // pid sat under the outer `running`, so one payload held the same fact twice
  // under two types. Liveness and the pid are asked of the *door*, on every
  // door, as `running: boolean` and `pid: number | null`.
}

/** A proposal to close — made by the team, closed only by the owner. */
export interface SessionProposal {
  round: number;
  at: string;
  trigger: string;
  evidence: SessionMemory | Record<string, unknown>;
  closed: boolean;
  closed_by?: string;
}

export interface SessionDetail {
  /** A boolean, like every other door. */
  running: boolean;
  /** And the process, in its own field. */
  pid: number | null;
  state: SessionState;
  memory: SessionMemory;
  turns: SessionTurn[];
  proposals: SessionProposal[];
  inbox: number;
  criterion: {
    stop_when: string;
    known: string[];
    the_model_is_not_the_judge: string;
  };
}

export interface SessionRow {
  id: string;
  topic: string;
  goal: string;
  stop_when: string;
  status: string;
  started: string;
  rounds: number;
  calls: number;
  ceiling: number;
  at_ceiling: boolean;
  models: Record<string, string> | null;
  /**
   * A BOOLEAN, on every door. The list door used to answer `running: 323634`
   * (a pid) here while the detail door answered `running: true` in the same
   * field — one name, two types, and no screen could be written once. The pid
   * has its own field.
   */
  running: boolean;
  pid: number | null;
  /**
   * 🚨 A stop that was asked for and never answered: the request is in the
   * record, no run ever acted on it, and the status alone would read as a
   * session that simply never began.
   */
  stop_asked_not_answered: boolean;
}

export interface SessionList {
  sessions: SessionRow[];
  /** Grouped by topic — a session sits *under* the thing it is about. */
  by_topic: Record<string, SessionRow[]>;
  topics: number;
}

export interface SessionCriterion {
  name: string;
  label: string;
  closes: string;
  proposed_when: string;
}

export interface SessionCriteria {
  criteria: SessionCriterion[];
  why_only_these: string;
  the_ceiling_is_not_a_criterion: string;
}

/**
 * What the model server said about **itself**, as `GET /v1/models` carries it
 * beside the names (set 32). 🚨 Required, because before it existed this door
 * answered `models: []` with the same authoritative-sounding note for two
 * different facts — *nobody answered* and *you have no models* — and a screen
 * that cannot tell them apart cannot honestly offer to start a server.
 *
 * `why` is the engine's own sentence when it did not answer, and `null` when it
 * did. There is no third state: this is a live answer or it is not.
 */
export interface EngineState {
  /** The engine key this node means — `ollama`, written by `motor.ENGINE_KEY`. */
  key: string;
  /** `health()` answered, not "a pid exists" — the zombie trap cannot arise. */
  reachable: boolean;
  /** The host the engine resolved for itself, or `null` if it never did. */
  host: string | null;
  why: string | null;
}

/**
 * The host's own model list, read from the node. A list of models written into
 * this file would be a list that is wrong the day somebody installs something.
 */
export interface ModelList {
  models: string[];
  default: string;
  uncensored: string[];
  /** The door says where the names came from, so no screen has to guess. */
  note: string;
  /** The engine's own reachability — the other half of an empty list. */
  engine: EngineState;
}

export interface SessionSayResult {
  id: string;
  queued: boolean;
  /** `true` when the owner woke a run that had stopped. */
  resumed: boolean;
  verdict: Verdict;
  /** 🚨 Required, and it is why `queued` is not the whole answer. */
  note: string;
}

export interface SessionAcceptResult {
  id: string;
  status: string;
  closed_because: string;
  closed_by: string;
  accepted_round: number;
  process_was_running: boolean;
  note: string;
}

export interface SessionStopResult {
  id: string;
  status: string;
  closed_because: string | null;
  /**
   * 🚨 `true` means the record is **not final yet**: a live run closes at its
   * next voice boundary, and a model call in flight is not interrupted. A
   * screen that renders `status: stopped` from a pending stop is showing a
   * status the record does not hold.
   */
  pending: boolean;
  stops_when?: string;
  note: string;
}

/**
 * The start door returns **the state itself**, with `running` and `ready` made
 * explicit. That is not an accident of the implementation to be typed around —
 * it is the useful shape: a screen that has just started a session and a screen
 * that has just opened one read the *same* type, so there is no second
 * definition that can disagree with the first about what a session looks like.
 */
export type SessionStartResult = SessionState & {
  running: boolean;
  ready: boolean;
};

export interface AskResult {
  governance: Verdict;
  reply_governance: ReplyRead;
  decision: string[];
  reply: string;
  prediction: string | null;
  validation: string[] | null;
  explanation: string | null;
}

export interface ChatResult extends AskResult {
  turns: number;
  model: string;
}

// ── the sword: the governed tool-agent (set 18) ─────────────────────────────

/**
 * One tool judgement. It holds a whole `Verdict`, not a boolean, because a
 * refused tool call IS a refusal and has to show the stem that tripped it —
 * the same rule the denial views follow. An earlier shape on the Python side
 * stored only `{verdict, allowed}` and could render "denied" with no reason.
 */
export interface ToolCheck {
  tool: string;
  verdict: Verdict;
}

export interface ToolResultRow {
  tool: string;
  content: string;
  success: boolean;
}

export interface AgentRun {
  governance: Verdict;
  reply_governance: ReplyRead;
  content: string;
  turns: number;
  tool_results: ToolResultRow[];
  tool_calls: ToolCheck[];
  denied: ToolCheck[];
  model: string;
}

export interface AgentTool {
  name: string;
  category: string;
  description: string;
  parameters: Record<string, unknown>;
}

/** How the sword is governed — shown, so the seam is never a claim. */
export interface AgentSeam {
  seam: string;
  fail_closed: boolean;
  denies: string;
  second_eye: string;
  holder: string;
}

export interface AgentTools {
  tools: AgentTool[];
  governance: AgentSeam;
}

// ── the shield: where a withheld action lands ──────────────────────────────

/**
 * One remembered refusal, whole. `verdict` is the gate's own dict rather than a
 * summary: set 18 already learned what happens when a refusal is stored without
 * its evidence — it renders as "no" with nothing to check.
 */
export interface ShieldRefusal {
  at: string;
  where: string;
  verdict: string;
  risk: number;
  alignment: number;
  readonly risk_hits: readonly string[];
  readonly gold_hits: readonly string[];
  readonly missing: readonly string[];
  gold_source: string;
  eye: Oracle;
  /**
   * Where the refusal deflects. Optional because the set-21 capture in
   * `sovereign-api.shield-fixture.ts` predates set 28 and genuinely has no
   * `direction` field — the honest repair for a fixture that cannot be
   * re-captured is a looser type, not an invented field.
   */
  readonly direction?: ShieldDirection;
  /** Present when the refusal came from a request rather than a tool call. */
  readonly request?: string;
}

/**
 * Where a refusal deflects to. Set 28, answer 3 C / 11 C.
 *
 * A wall can only say no. The owner's shield principle in his own words: *„Ein
 * Schild, das als harte Barriere steht, hält nicht lange. … Ein Schild, das
 * ausweicht, ohne die volle Wucht zu nehmen."* So a refusal names **other
 * doors** — the doors of this node that are open — and never a rewording of the
 * request, because "try saying it differently" is the bypass wearing a helpful
 * hat.
 *
 * Safe by construction, not by argument: the list is a constant in `shield.py`
 * and contains no request-derived text, so a held stem cannot leak through it.
 * The checkable form of the claim is *follow the direction, submit the same
 * request, get the same verdict.*
 */
export interface ShieldDirection {
  readonly held_at: string;
  /** `request` for the three pre-govern doors, `tool` for a held tool call. */
  readonly kind: string;
  /**
   * 🚨 The other doors of this node that stand open — and the type was
   * **wrong**, which is the kind of thing that only shows up when a capture
   * arrives. It read `readonly string[]`, and the node has always sent
   * `{door, opens}` — a name and what that door opens, because a bare
   * `"/GET /govern"` tells a reader which door is open but not what is waiting
   * behind it. `shield.open_doors` on the Python side builds the pair.
   *
   * Nothing consumed the field, so the mistake survived set 28 intact: an
   * unused type is not a checked one.
   */
  readonly doors: readonly ShieldDoor[];
  readonly note: string;
}

/** One door the deflection points at, and what is behind it. */
export interface ShieldDoor {
  readonly door: string;
  readonly opens: string;
}

/**
 * The 403 body of a **wrapped** door — `/v1/ask`, `/v1/chat`, `/v1/agent`,
 * `/v1/sessions`, `/v1/trialog`. `/govern` and `/hub/spore` put the verdict
 * under `detail` *directly* and are a different shape; reading one as the other
 * is the reason this type is written down.
 *
 * 🚨 `direction` is part of it, and a caller that drops it does not lose a
 * nicety: set 28 measured that a refusal names the other doors of this node
 * that stand open, and the checkable form of that claim is *follow the
 * direction, submit the same request, get the same verdict.* A surface that
 * reads the verdict and discards the direction has built a wall and called it a
 * shield.
 */
export interface HeldBody {
  readonly detail: {
    readonly governance: Verdict;
    readonly blocked: true;
    /** The door's own sentence. Optional on the wire, required to be worth reading. */
    readonly message?: string;
    readonly direction?: ShieldDirection;
  };
}

/**
 * One answered request, whole. Set 28.
 *
 * The **same shape as a refusal**, deliberately: same verdict, same gold source,
 * same second eye. The owner's complaint was *„Aus diesem Haus geht nur Abwehr
 * hinaus. Es geht nichts hinaus, was gewachsen ist."* — and a mirror that shows
 * only refusals is a wall with a reflection of itself, its count read alone
 * looking like the node's whole life.
 */
export interface ShieldGrown {
  at: string;
  where: string;
  verdict: string;
  risk: number;
  alignment: number;
  readonly risk_hits: readonly string[];
  readonly gold_hits: readonly string[];
  readonly missing: readonly string[];
  gold_source: string;
  eye: Oracle;
  /**
   * Urasil_light's real `Zyklus.matrix()` state at the moment she answered —
   * recorded verbatim, not described. His `fokus: synthese` is what shaped the
   * form of that answer. Absent when nothing reported a state; never invented.
   */
  readonly uracil?: { readonly grundmodus?: string; readonly stimmung?: string; readonly fokus?: string };
  /** Answer 9 C asked for moments of understanding. Nothing here can know one. */
  readonly cannot_record: string;
  readonly request?: string;
}

/** The read model behind the door: what she holds, and what she has held. */
// ── the snake: the one seam into the mycelium ────────────────────────────

/**
 * What one crossing carried.
 *
 * A refusal carries the **shape** of a refusal and never the words that caused
 * it: `held_count` crosses, `risk_hits` does not. The net's door refuses words
 * the governor holds, so a stem cannot cross even as a list — and nothing this
 * node serves exposes its lexicon. A count is not an attack; a name is.
 */
export interface SnakeRefusal {
  kind: 'refusal';
  seam: string;
  verdict: string;
  risk: number;
  alignment: number;
  held_count: number;
  readonly missing: readonly string[];
  readonly gold_hits: readonly string[];
  gold_source: string;
  eye: Oracle;
}

export interface SnakeCycle {
  kind: 'cycle';
  grundmodus: string;
  stimmung: string;
  fokus: string;
}

export type SnakePayload = SnakeRefusal | SnakeCycle;

/**
 * One receipt from the net. `carried` is the payload the snake sent, parsed
 * once by the node — `text` stays raw, because the net judges text.
 *
 * `carried` is `null` for a spore this node did not write, and the surface
 * says so rather than drawing an empty row.
 */
export interface SnakeCrossing {
  stamp: string;
  kind: string;
  source: string;
  text: string;
  /**
   * Whose verdict the receipt's own fields are. Set 22 added it; it used to be
   * unsaid, and a receipt written before that honestly lacks it — so it is
   * optional, and every crossing the snake writes carries one.
   */
  readonly judged?: string;
  verdict: string;
  readonly gold_hits: readonly string[];
  /** The GATE's hits on the description — always empty for the snake's own. */
  readonly risk_hits: readonly string[];
  readonly carried: SnakePayload | null;
}

export interface SnakeState {
  carried: number;
  refusals_carried: number;
  cycles_carried: number;
  readonly crossings: readonly SnakeCrossing[];
  at: string;
  /** The fields the seam refuses to carry, named. */
  readonly words_withheld: readonly string[];
  /** What is deliberately NOT carried, said out loud. */
  not_carried: string;
  guard: string;
}

/**
 * A defect in the sibling kernel, carried as data.
 *
 * These are **claims about another repository** — one that has no version
 * control here, so nothing would notice if a line moved. `verify_claims.py`
 * re-reads the sibling's files and FAILs if any of these stops being true, and
 * `TestTheGardenShows` does the same. A claim about someone else's code needs a
 * location or it is folklore.
 */
export interface GardenUpstream {
  id: string;
  /** `Zelle.py:19` and friends — the exact lines, not the file. */
  where: string;
  what: string;
  why_it_matters: string;
}

export interface GardenKernel {
  path: string;
  present: boolean;
  /** The ten files the kernel imports. Also the *deflection*: when the kernel is
   *  missing, naming these is the fix, because the mechanism knows what it
   *  wants. Contrast `Verdict.missing`, which must stop at the boundary. */
  readonly wanted: readonly string[];
  readonly missing: readonly string[];
  /** SHA-256, first 16 hex. A fingerprint, not a trust anchor: the files are
   *  not ours and not version controlled. */
  readonly files: Readonly<Record<string, string>>;
  tick_s: number;
  readonly upstream: readonly GardenUpstream[];
  /** Always `false`, and that is the load-bearing part: the garden is the one
   *  ungated surface, so if a cell could be nudged it would be a way to
   *  launder a refusal past the gate. */
  tended: false;
  tended_note: string;
  missing_note: string;
}

/** No frame has been written yet, or the one on disk is not one. */
export interface GardenNoFrame {
  present: false;
  live: false;
  stale: false;
  step: 0;
  error: string;
}

export interface GardenFrame {
  present: true;
  step: number;
  cells: number;
  /** The kernel's own mean hue, in degrees. The background is THIS and nothing
   *  else — a prettier colour would be Bianca inventing beauty. */
  hue_mean: number;
  harm: number;
  drift: number;
  energie: number;
  spread: number;
  keime: number;
  cluster: number;
  /** The kernel's own `[ENGINE] step=…` line, unedited. */
  readout: string;
  /** Read out of the kernel's config **in the child**, never retyped here. */
  thresholds: { drift: number; energie: number };
  born_converged: boolean | null;
  converged_at: number | null;
  /** 🚨 Set 35 (2026-10-06). The frame **contradicts itself**, and the
   *  disagreement is a fact, not a bug: `born_converged` says the world can
   *  never grow (mean drift ~0.002 against a rule that needs 0.40), and the
   *  cluster count says it grew. Both are true, because they answer different
   *  questions — reproduction needs **11 seeds at once**, and a mean is not a
   *  count. A screen that shows `born_converged` alone publishes one arm of a
   *  contradiction as if it were the whole truth, which is how this repo has
   *  been wrong three separate times. */
  convergence_disputed: boolean | null;
  /** Cluster count **before** the first step. `cluster - cluster_start` is the
   *  only measured answer to "did he grow", in the kernel's own unit. */
  cluster_start: number | null;
  /** The step at which `cluster` first exceeded `cluster_start`, or `null`.
   *  Measured on the real kernel: **1**, in every world that grew at all. */
  grew_at: number | null;
  /** NOT a constant: the child never seeds `random`, so every world differs.
   *  Measured 2, 67, 4, 2. Any screen that shows one number as if it were the
   *  answer is publishing a single run. */
  flat_at: number | null;
  files: Record<string, string>;
  error: string | null;
  /** Epoch seconds the child wrote this frame. `age_s` is derived from it in the
   *  child, not here — a second clock in this file would be a second writer of
   *  the one fact that decides whether a frame is fresh. */
  written: number;
  age_s: number | null;
  fresh: boolean;
  child_running: boolean;
  /** `fresh` AND a child running. A frame written by a child that has since
   *  died is fresh, and calling that live is how a stopped garden keeps looking
   *  like a growing one. */
  live: boolean;
  stale: boolean;
  stale_note?: string;
}

export type GardenFrameState = GardenNoFrame | GardenFrame;

export interface GardenState {
  kernel: GardenKernel;
  frame: GardenFrameState;
  child_running: boolean;
  tick_s: number;
}

export interface ShieldState {
  refusals_today: number;
  readonly refusals: readonly ShieldRefusal[];
  /** Which held stems are actually doing the refusing, and how often. */
  readonly held_stems: Readonly<Record<string, number>>;
  memory: string;
  remembered: string;
  /** What is deliberately NOT remembered — a dry run withholds nothing. */
  not_remembered: string;
  // ── the other half (set 28) ───────────────────────────────────────────
  /** A separate count in a separate file. Never `refusals_today` — a shared
   *  count is how one half starts quietly counting the other. */
  grown_today: number;
  readonly grown: readonly ShieldGrown[];
  /** Which gold values were actually carried today, and how often. */
  readonly grown_gold: Readonly<Record<string, number>>;
  /** Where the growth file lives, in the same words the door says. */
  grown_memory: string;
  /** The record's own blind spot, required: a record that admits what it
   *  cannot see is more of a testimony than one that pretends to have eyes. */
  grown_cannot_record: string;
  readonly boundary: { readonly advisory_eye: boolean; readonly binding_eye: boolean; readonly holder: string };
}

// ── the three ways a door can refuse ───────────────────────────────────────

/**
 * Said the same way on every surface, so "the motor is down" is never read
 * as "the answer was empty". Mirrors ENGINE_DOWN_NOTE in the sovereign face;
 * if one changes, both must.
 */
export const ENGINE_DOWN_NOTE =
  'The event is on the Interaction Ledger — an unanswered question is also an ' +
  'event. Restart the engine and the question is still answerable.';

/** An interrupted deliberation: turns that DID happen, plus why it stopped. */
export interface InterruptedTrialog extends Omit<Trialog, 'completed'> {
  completed: false;
  error: string;
  reason: string;
  topic_governance: Verdict;
}

export class SovereignDenied extends Error {
  /**
   * 🚨 `direction` was dropped here for sets 28 and 29, and this set found it:
   * `refusal()` pulled the verdict and the sentence out of the 403 body and
   * threw the rest away, so the door's answer to *"wenn diese Tür zu ist —
   * wohin dann?"* arrived on the wire and died in the parse. The face renders
   * it; this app could not, and no screen noticed because no screen asked.
   *
   * Optional, and honestly so: `/govern` and `/hub/spore` answer a refusal
   * without one, and an unreadable 403 has none to carry. What must not happen
   * again is the *silence* — a caller that wants it now gets `undefined`
   * because the door did not send it, not because this class dropped it.
   */
  constructor(
    readonly verdict: Verdict,
    readonly messageText: string,
    readonly direction?: ShieldDirection,
  ) {
    super(messageText);
    this.name = 'SovereignDenied';
  }
}

export class SovereignEngineDown extends Error {
  constructor(readonly why: string) {
    super(why);
    this.name = 'SovereignEngineDown';
  }
}

export class SovereignInterrupted extends Error {
  constructor(readonly partial: InterruptedTrialog) {
    super(partial.reason || 'deliberation interrupted');
    this.name = 'SovereignInterrupted';
  }
}

// ── transport ──────────────────────────────────────────────────────────────

const DEFAULT_NODE = 'http://127.0.0.1:8712';

/**
 * Where the sovereign node lives. Overridable so a Tauri build on another
 * machine is not welded to a port — and so a test can point it anywhere.
 */
export function nodeBase(): string {
  const fromEnv = (import.meta as { env?: Record<string, string> }).env?.VITE_BIANCA_NODE;
  if (fromEnv) return fromEnv.replace(/\/$/, '');
  try {
    const stored = localStorage.getItem('bianca.node');
    if (stored) return stored.replace(/\/$/, '');
  } catch {
    /* no storage in this context — the default stands */
  }
  return DEFAULT_NODE;
}

export function setNodeBase(url: string): void {
  try {
    localStorage.setItem('bianca.node', url.replace(/\/$/, ''));
  } catch {
    /* nothing to do; the next read falls back to the default */
  }
}

// ── the language she answers in (set 26) ───────────────────────────────────

/**
 * One language, one place, and it is a *store* beside `nodeBase` rather than a
 * prop. A prop would have to be threaded from the top of the app through every
 * page to every write path, and the one screen that forgot would answer in the
 * default with nothing on it saying the picker had been ignored — the same
 * defect shape this repo has now found four times, in a new place.
 */
const LANG_KEY = 'bianca.lang';

let chosen: string | null = null;
/** What the node says she speaks. Null until `/context` has answered. */
let known: { code: string; name: string; default?: boolean }[] = [];

export function setLanguages(list: { code: string; name: string; default?: boolean }[]): void {
  known = list;
  // A stored choice that the node does not offer is dropped here rather than
  // sent: the door would 422 it, and a picker that can leave the product in a
  // state where nothing answers is worse than one that forgets.
  const stored = readStored();
  chosen = known.some((l) => l.code === stored) ? stored : null;
}

export function languages(): { code: string; name: string; default?: boolean }[] {
  return known;
}

function readStored(): string | null {
  try {
    return localStorage.getItem(LANG_KEY);
  } catch {
    return null;
  }
}

/**
 * The language to send, or null when the caller has chosen nothing.
 *
 * Null is meaningful and is not the same as `'de'`: with no choice the field is
 * omitted, so the *door* applies the default. That keeps the default in one
 * place — `voice.DEFAULT_LANG` — instead of a second copy in every client.
 */
export function answerLang(): string | null {
  return chosen;
}

export function setAnswerLang(code: string | null): void {
  chosen = code && known.some((l) => l.code === code) ? code : null;
  try {
    if (chosen) localStorage.setItem(LANG_KEY, chosen);
    else localStorage.removeItem(LANG_KEY);
  } catch {
    /* nothing to do; the next read falls back to the default */
  }
}

/**
 * The one seam every write path goes through.
 *
 * The face has the same helper for the same reason, and the reason it is a
 * function rather than a field is the same: four hand-written bodies are four
 * chances to forget, and a forgotten one is invisible until a user notices they
 * are being answered in a language they did not ask for.
 *
 * `/hub/spore` deliberately does NOT come through here. A spore's words are
 * judged by the gate and quoted back verbatim in a refusal, so a `lang` on that
 * POST would suggest the text could be restated and judged as the same
 * sentence — which is exactly the laundering the gate does not permit.
 */
export function withLang<T extends Record<string, unknown>>(payload: T): T & { lang?: string } {
  const lang = answerLang();
  return (lang ? { ...payload, lang } : payload) as T & { lang?: string };
}

/** True when the 503 body is an interrupted deliberation, not a dead engine. */
function isInterrupted(detail: unknown): detail is InterruptedTrialog {
  return !!detail && typeof detail === 'object' && (detail as { turns?: unknown }).turns !== undefined;
}

/** True when `detail` carries a full verdict, not a message about one. */
function looksLikeVerdict(d: unknown): d is Verdict {
  return !!d && typeof d === 'object' && typeof (d as Verdict).verdict === 'string';
}

/**
 * Read a refusal out of a 403 body.
 *
 * The node emits TWO shapes, and the difference is historical rather than
 * meaningful:
 *
 *   · `/govern`, `/hub/spore` — `detail` IS the verdict.
 *   · `/v1/ask`, `/v1/chat`, `/v1/trialog` — `detail` is
 *     `{governance, blocked, message}`.
 *
 * The client accepts both rather than the one it happened to be written
 * against, because a client that only recognises one turns the other door's
 * refusal into a generic `Error` — and a generic error renders as a failure
 * instead of as a denial. A door that said no would look like a door that
 * broke, which is exactly the confusion the whole product exists to prevent.
 *
 * A third case matters most: a 403 whose body we cannot read. It is STILL a
 * refusal, and it is still a refusal with no readable verdict attached. It is
 * rendered as a denial whose provenance is explicitly unknown rather than
 * quietly upgraded to a successful call or downgraded to a transport fault.
 */
function refusal(detail: unknown): SovereignDenied {
  // 🚨 Two shapes arrive here, and the difference is one envelope deep.
  //
  //   `door()` unwraps FastAPI's `{detail: …}` before calling, and hands over
  //   the verdict or the wrapper `{governance, blocked, message}`. The session
  //   doors pass the **whole body**, because they read their own status codes
  //   (400 for a malformed criterion, 409 for "nothing was proposed") and 403
  //   is only one of them. The result was measured on a held session topic: the
  //   verdict was on the wire, `zurueckhalten` with its stems, the gold source
  //   and the second eye — and the screen showed `UNKNOWN_VERDICT`, an empty
  //   `gold_source` and a warning eye. The "unreadable refusal" branch fired on a
  //   body that was perfectly readable, which is the worst shape this file has:
  //   it is honest about not-knowing **and wrong**.
  //
  // So both are tried, in this order, and the reason for the order is that
  // `/govern` and `/hub/spore` put the verdict *directly* under `detail`: for
  // those, `arg.detail` is the spore's own sentence, not a second verdict. The
  // argument wins, always; the envelope is a fallback, never a reinterpretation.
  for (const kandidat of [detail, envelopeOf(detail)]) {
    if (kandidat === undefined) continue;
    const gelesen = readRefusal(kandidat);
    if (gelesen) return gelesen;
  }
  // Unreadable refusal. The governor said no; the reason did not survive the
  // wire. Say exactly that, and do not invent a verdict.
  return new SovereignDenied(UNKNOWN_VERDICT, reasonOf(detail, 403));
}

/** The FastAPI envelope's payload, or `undefined` — never a re-read verdict. */
function envelopeOf(body: unknown): unknown {
  if (!body || typeof body !== 'object') return undefined;
  const d = (body as { detail?: unknown }).detail;
  return d !== null && typeof d === 'object' ? d : undefined;
}

/** The two readable shapes, or `null`. The only place a verdict is read. */
function readRefusal(detail: unknown): SovereignDenied | null {
  if (looksLikeVerdict(detail)) {
    // `/govern` and `/hub/spore` put the verdict under `detail` directly, and
    // `/hub/spore` additionally nests its OWN reason in a second `detail`
    // string ("spore denied by the value governor (zurueckhalten). recorded,
    // not stored."). That reason is the door speaking in its own words, and
    // the face shows it (`v.detail || "recorded, not stored"`, ui.html:1162).
    // Dropping it in favour of "Verdikt: zurueckhalten" would keep the verdict
    // and lose the voice — so the door's own sentence wins when it is there.
    const own = (detail as { detail?: unknown }).detail;
    return new SovereignDenied(
      detail,
      typeof own === 'string' && own.trim() ? own : `Verdikt: ${detail.verdict}`,
      directionOf(detail),
    );
  }
  if (detail && typeof detail === 'object') {
    const d = detail as { governance?: unknown; message?: unknown };
    if (looksLikeVerdict(d.governance)) {
      return new SovereignDenied(
        d.governance,
        typeof d.message === 'string' ? d.message : `Verdikt: ${d.governance.verdict}`,
        directionOf(d),
      );
    }
  }
  return null;
}

/**
 * The verdict shown when the node refused but the body could not be read.
 *
 * Every field is a statement of not-knowing rather than a plausible guess: a
 * fabricated `alignment: 0.0` would read as a measurement, and a fabricated
 * `gold_source` would be a path nobody can open. `gold_source` is empty on
 * purpose — the UI prints `gold src : —`, which is the honest rendering.
 */
export const UNKNOWN_VERDICT: Verdict = {
  verdict: 'zurueckhalten',
  alignment: 0,
  risk: 0,
  gold_values_loaded: false,
  gold_source: '',
  gold_hits: [],
  risk_hits: [],
  oracle: {
    vote: 'warnen',
    grounds: ['unlesbare Ablehnung — der Grund kam nicht mit'],
    resonance: 0,
    advisory: true,
    binding: false,
    holder: 'ValueGovernor',
  },
};

/**
 * The deflection, if the door sent one — and only if it looks like one. A
 * structural check rather than a cast: `shield.open_doors` is built in Python
 * and the app has never seen its type, so "the field exists" is not enough to
 * hand a screen something to render. A half-shaped direction is `undefined`,
 * which the surface already knows how to say out loud.
 */
function directionOf(detail: unknown): ShieldDirection | undefined {
  if (!detail || typeof detail !== 'object') return undefined;
  const roh = (detail as { direction?: unknown }).direction;
  if (!roh || typeof roh !== 'object') return undefined;
  const d = roh as { held_at?: unknown; kind?: unknown; doors?: unknown; note?: unknown };
  if (typeof d.held_at !== 'string' || typeof d.kind !== 'string') return undefined;
  if (typeof d.note !== 'string' || !Array.isArray(d.doors)) return undefined;
  const tueren: ShieldDoor[] = [];
  for (const t of d.doors) {
    if (!t || typeof t !== 'object') return undefined;
    const e = t as { door?: unknown; opens?: unknown };
    if (typeof e.door !== 'string' || typeof e.opens !== 'string') return undefined;
    tueren.push({ door: e.door, opens: e.opens });
  }
  return { held_at: d.held_at, kind: d.kind, doors: tueren, note: d.note };
}

function reasonOf(detail: unknown, status: number): string {
  if (typeof detail === 'string' && detail) return detail;
  if (detail && typeof detail === 'object') {
    const d = detail as { error?: string; reason?: string; detail?: string };
    if (d.reason) return d.reason;
    if (d.error) return d.error;
    if (d.detail) return d.detail;
  }
  return `Status ${status}`;
}

async function door<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${nodeBase()}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    });
  } catch (e) {
    // The node is not listening at all. That is a transport failure, not a
    // verdict, and it must not be dressed up as one.
    throw new SovereignEngineDown(
      `cannot reach the node at ${nodeBase()} (${(e as Error).message})`,
    );
  }
  const body = await res.json().catch(() => null);
  const detail = res.ok ? null : (body as { detail?: unknown })?.detail;

  if (res.status === 403) throw refusal(detail);
  if (res.status === 503) throw new SovereignEngineDown(reasonOf(detail, res.status));
  if (!res.ok) throw new Error(reasonOf(detail, res.status));
  return body as T;
}

// ── read doors ─────────────────────────────────────────────────────────────

export const getHealth = () => door<Health>('/health');
/**
 * `/context`, and it also *learns* the languages on the way past.
 *
 * A side effect in a fetcher, which is normally the wrong shape — and here it
 * is the right one, for the same reason the face calls `initLang` from
 * `loadContext`. Whoever reads the node's identity also learns what she speaks,
 * so a picker can never be rendered from a list this file invented. A picker
 * somewhere else that did its own `getContext` and forgot the `setLanguages`
 * would offer a language the node no longer speaks, and nothing on screen would
 * say so until a request came back 422.
 */
export const getContext = () =>
  door<Context>('/context').then((c) => {
    if (c && Array.isArray(c.languages)) setLanguages(c.languages);
    return c;
  });
export const getToday = () => door<Today>('/today');
export const getIdle = () => door<IdleStatus>('/idle/status');
export const getUrasil = () => door<Urasil>('/urasil');
export const getManifest = () => door<Manifest>('/hub/manifest');
export const getSpores = (limit = 12) => door<{ spores: Spore[] }>(`/hub/spores?limit=${limit}`);
export const listTrialogs = () => door<{ trialogs: TrialogIndexEntry[] }>('/v1/trialogs');
export const readTrialog = (name: string) => door<{ trialog: string }>(`/v1/trialogs/${encodeURIComponent(name)}`);
export const getAgentTools = () => door<AgentTools>('/v1/agent/tools');

export const getShield = () => door<ShieldState>('/v1/shield');

export const getSnake = () => door<SnakeState>('/v1/snake');

/**
 * Carrying is an **explicit act**, never a side effect of a refusal — the
 * sword's own rule (full reach is a decision argued from the recorded
 * measurements, not an oversight) applies to the net as it does to the tools.
 */
export const carrySnake = () =>
  door<{ offered: number; carried: number; already: number; refused_locally: number }>(
    '/v1/snake',
    { method: 'POST', body: JSON.stringify({}) },
  );

export interface GardenStartResult {
  started: boolean;
  /** The kernel's own sentence when it will not start — a missing floor, or
   *  already running. Carried verbatim, never rewritten into a nicer one. */
  reason?: string;
  pid?: number;
}

export interface GardenStopResult {
  stopped: boolean;
  reason?: string;
  pid?: number;
  /** SIGTERM was not enough and SIGKILL was sent. Said, not hidden. */
  forced?: boolean;
}

/**
 * The garden door. Reading it **never** starts the kernel: growing the garden is
 * an explicit act, so a page view can never be what makes a process appear.
 */
export const getGarden = () => door<GardenState>('/v1/garden');

export const startGarden = () =>
  door<GardenStartResult>('/v1/garden/start', {
    method: 'POST',
    body: JSON.stringify({}),
  });

/** Stopping keeps the frame: the last thing the kernel was is still a fact. */
export const stopGarden = () =>
  door<GardenStopResult>('/v1/garden/stop', { method: 'POST', body: JSON.stringify({}) });

export function govern(text: string) {
  return door<Verdict>(`/govern?text=${encodeURIComponent(text)}`);
}

// ── write doors ────────────────────────────────────────────────────────────

export function ask(query: string, model?: string) {
  return door<AskResult>('/v1/ask', {
    method: 'POST',
    body: JSON.stringify(withLang(model ? { query, model } : { query })),
  });
}

export function chat(messages: { role: string; content: string }[], model?: string) {
  return door<ChatResult>('/v1/chat', {
    method: 'POST',
    body: JSON.stringify(withLang(model ? { messages, model } : { messages })),
  });
}

/**
 * The governed tool-agent. Denials arrive as a 403 in the same
 * `{governance, blocked, message}` shape as `/v1/ask` and `/v1/chat`, so
 * `refusal()` reads them without a special case — one client, three doors.
 */
export function runAgent(query: string, model?: string, maxTurns?: number) {
  return door<AgentRun>('/v1/agent', {
    method: 'POST',
    body: JSON.stringify(withLang({ query, ...(model ? { model } : {}), ...(maxTurns ? { max_turns: maxTurns } : {}) })),
  });
}

/**
 * Spore ingress. Deliberately NOT `withLang` — see that function's docstring.
 * These words are judged by the gate and quoted back verbatim in a refusal, so
 * they are evidence rather than prose, and a language field here would suggest
 * they could be restated and judged as the same sentence.
 */
export function postSpore(text: string, source = 'desktop', kind = 'spore') {
  return door<Spore>('/hub/spore', {
    method: 'POST',
    body: JSON.stringify({ text, source, kind }),
  });
}

/**
 * Convene the three voices.
 *
 * An interrupted deliberation is NOT a thrown-away error: the door answers
 * 503 and still carries the turns that happened. That arrives as a
 * `SovereignInterrupted` so the caller can render the work instead of hiding
 * it — the face does the same, from the same contract.
 */
// ── the working session, door by door (set 30) ─────────────────────────────
//
// Every function here goes through the SAME `nodeBase`, the same 403 handling
// and the same `reasonOf` as the other doors, on purpose: a second HTTP path in
// this file is a second place where a 403 can be read as an error message, and
// set 16/17/18 each found the same "outcome without evidence" defect in a place
// an earlier set had already repaired elsewhere. Four times, all the same shape.

async function sessionGet<T>(path: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${nodeBase()}${path}`);
  } catch (e) {
    throw new SovereignEngineDown(
      `cannot reach the node at ${nodeBase()} (${(e as Error).message})`,
    );
  }
  const body = await res.json().catch(() => null);
  if (res.status === 403) throw refusal(body);
  if (!res.ok) throw new Error(reasonOf(body, res.status));
  return body as T;
}

async function sessionPost<T>(path: string, payload?: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${nodeBase()}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload ?? {}),
    });
  } catch (e) {
    throw new SovereignEngineDown(
      `cannot reach the node at ${nodeBase()} (${(e as Error).message})`,
    );
  }
  const body = await res.json().catch(() => null);
  if (res.status === 403) throw refusal(body);
  if (!res.ok) {
    // 🚨 400 and 409 are carried as an error, but they are NOT refusals, and
    // the message must not read like one. A session with no criterion is a
    // malformed request, exactly like an unknown language (set 26: 422, never
    // 403). A caller that catches `SovereignDenied` here would be told Bianca
    // refused a request she never judged.
    const err = new Error(reasonOf(body, res.status)) as Error & { status?: number };
    err.status = res.status;
    throw err;
  }
  return body as T;
}

/** The host's own model list. Host truth, never written into this file. */
export function listModels(): Promise<ModelList> {
  return sessionGet<ModelList>('/v1/models');
}

/** The criterion vocabulary — the seam's own closed list, read from the node. */
export function listSessionCriteria(): Promise<SessionCriteria> {
  return sessionGet<SessionCriteria>('/v1/sessions/criteria');
}

export function listSessions(): Promise<SessionList> {
  return sessionGet<SessionList>('/v1/sessions');
}

export function getSession(id: string): Promise<SessionDetail> {
  return sessionGet<SessionDetail>(`/v1/sessions/${encodeURIComponent(id)}`);
}

export function startSession(input: {
  topic: string;
  goal: string;
  stop_when: string;
  ceiling?: number;
  model?: string;
  models?: Record<string, string>;
  start?: boolean;
}): Promise<SessionStartResult> {
  return sessionPost<SessionStartResult>('/v1/sessions', input);
}

/** Speak into a running session. The owner is governed like everyone else. */
export function sayToSession(id: string, text: string): Promise<SessionSayResult> {
  return sessionPost<SessionSayResult>(
    `/v1/sessions/${encodeURIComponent(id)}/say`,
    { text },
  );
}

/** The only close a person's word alone can make. 409 when nothing was proposed. */
export function acceptSession(id: string): Promise<SessionAcceptResult> {
  return sessionPost<SessionAcceptResult>(`/v1/sessions/${encodeURIComponent(id)}/accept`);
}

/**
 * Ask a session to stop, and read `pending` honestly: `true` means the record is
 * not final yet. A screen that renders this as "stopped" is showing a status the
 * record does not hold.
 */
export function stopSession(id: string, reason: string): Promise<SessionStopResult> {
  return sessionPost<SessionStopResult>(
    `/v1/sessions/${encodeURIComponent(id)}/stop?reason=${encodeURIComponent(reason)}`,
  );
}

export async function runTrialog(
  topic: string,
  rounds = 2,
  model?: string,
  /**
   * Set 29: a model per voice. Omitted or empty means one model for all three —
   * the behaviour this door had before the field existed, so a caller that knows
   * nothing about it is unaffected. A name for a voice this house does not have
   * is dropped server-side, never honoured.
   */
  models?: Record<string, string>,
): Promise<Trialog> {
  const path = '/v1/trialog';
  const hasPerVoice = !!models && Object.keys(models).length > 0;
  let res: Response;
  try {
    res = await fetch(`${nodeBase()}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(
        withLang({
          topic,
          rounds,
          ...(model ? { model } : {}),
          ...(hasPerVoice ? { models } : {}),
        }),
      ),
    });
  } catch (e) {
    throw new SovereignEngineDown(`cannot reach the node at ${nodeBase()} (${(e as Error).message})`);
  }
  const body = await res.json().catch(() => null);
  const detail = (body as { detail?: unknown })?.detail;
  if (res.status === 403) throw refusal(detail);
  if (res.status === 503) {
    if (isInterrupted(detail)) throw new SovereignInterrupted(detail);
    throw new SovereignEngineDown(reasonOf(detail, res.status));
  }
  if (!res.ok) throw new Error(reasonOf(detail, res.status));
  return body as Trialog;
}
