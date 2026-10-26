/**
 * @vitest-environment jsdom
 *
 * The Hand — the governed tool-agent — checked against what the node really
 * sent.
 *
 * The user's complaint that opened set 18 was "it feels like I don't have a
 * full functioning Jarvis", and it was correct: the governed agent existed,
 * was fail-closed, was tested — and was reachable only from a CLI command.
 * The face got the door in breath 3; this file is the React half.
 *
 * The failure mode being pinned is the project's fourth occurrence of its own
 * habit: **render the outcome, drop the evidence.** On this screen it has a
 * specific and dangerous form. A tool call that the governor REFUSED is the
 * single most important row on the page, and a shape of `{verdict, allowed}`
 * renders it as a bare "denied" — the reader cannot check anything. So:
 *
 *   · a refused tool keeps its whole verdict and names the stem that tripped it,
 *   · an ALLOWED tool is shown too, with its gold hits — a screen that only
 *     shows refusals teaches the reader that the door is always saying no,
 *   · the seam is shown, not claimed: the reader can see that only
 *     `zurueckhalten` denies and that the eye is advisory,
 *   · a dead engine is never drawn as an answer.
 *
 * Everything asserted here comes from `AGENT_*` (set 18) — captures from the
 * running node, plus one refused-tool verdict taken from the real hook. The
 * file documents where each piece came from.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';
import { MemoryRouter } from 'react-router';
import { JarvisPage } from '../../pages/JarvisPage';
import {
  AGENT_DENIED,
  AGENT_REFUSED_TOOL,
  AGENT_RUN,
  AGENT_TOOLS,
} from '../../lib/sovereign-api.agent-fixture';
import type { Verdict } from '../../lib/sovereign-api';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;

const shown = () => container.textContent ?? '';
const has = (s: string) => shown().toLowerCase().includes(s.toLowerCase());

/** True only for a BARE token — see the note in tab-evidence.test.tsx. */
const hasBare = (token: string) =>
  new RegExp(`(?<![\\p{L}\\p{N}_])${token}(?![\\p{L}\\p{N}_])`, 'iu').test(shown());

async function mount(node: React.ReactNode, path = '/') {
  await act(async () => {
    root.render(<MemoryRouter initialEntries={[path]}>{node}</MemoryRouter>);
  });
}

async function remount(node: React.ReactNode, path = '/') {
  act(() => root.unmount());
  container.remove();
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  await mount(node, path);
}

async function settle() {
  await act(async () => {
    await new Promise((r) => setTimeout(r, 30));
  });
}

function stub(handlers: Record<string, { status: number; body: unknown }>) {
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
    const path = String(input).replace(/^https?:\/\/[^/]+/, '').split('?')[0];
    const hit = Object.entries(handlers).find(([k]) => path.endsWith(k));
    if (!hit) {
      return { ok: false, status: 404, json: async () => ({ detail: path }) } as Response;
    }
    return {
      ok: hit[1].status < 400,
      status: hit[1].status,
      json: async () => hit[1].body,
    } as Response;
  }) as typeof fetch;
}

/** Every tool the real inventory names, so a missing one cannot pass. */
const TOOL_NAMES = AGENT_TOOLS.tools.map((t) => t.name as string);

async function openHand() {
  stub({ '/v1/agent/tools': { status: 200, body: AGENT_TOOLS } });
  await remount(<JarvisPage />, '/jarvis?sub=hand');
  await settle();
}

/** Drive a run and return once the button re-enables (i.e. it settled). */
async function runAgent(query: string) {
  const area = container.querySelector('textarea') as HTMLTextAreaElement;
  const setter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype,
    'value',
  )!.set!;
  await act(async () => {
    setter.call(area, query);
    area.dispatchEvent(new Event('input', { bubbles: true }));
  });
  const button = [...container.querySelectorAll('button')].find((b) =>
    b.textContent?.includes('Ausführen'),
  )!;
  await act(async () => {
    button.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  });
  await settle();
  await act(async () => {
    await new Promise((r) => setTimeout(r, 30));
  });
}

describe('the Hand shows the sword', () => {
  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });
  afterEach(() => vi.restoreAllMocks());

  it('lists every tool the inventory names', async () => {
    await openHand();
    for (const name of TOOL_NAMES) {
      expect(has(name), `${name} missing from the sword`).toBe(true);
    }
  });

  it('says what each tool is for', async () => {
    // A name with no purpose is a mystery; the door sends a description for
    // every tool, so dropping it would be a choice, not an accident.
    await openHand();
    for (const tool of AGENT_TOOLS.tools) {
      expect(has(tool.description.slice(0, 28)), `${tool.name} has no description`).toBe(true);
    }
  });

  it('names the seam and that it is fail-closed', async () => {
    // The seam is the whole safety claim of this page. Showing it turns a
    // promise into something the reader can check.
    await openHand();
    expect(has(AGENT_TOOLS.governance.seam)).toBe(true);
    expect(has('fail-closed')).toBe(true);
  });

  it('says only zurueckhalten denies, and that the eye is advisory', async () => {
    await openHand();
    expect(has('zurueckhalten')).toBe(true);
    expect(has('advisory')).toBe(true);
    expect(has(AGENT_TOOLS.governance.holder)).toBe(true);
  });

  it('renders no bare undefined', async () => {
    await openHand();
    expect(hasBare('undefined')).toBe(false);
    expect(hasBare('NaN')).toBe(false);
    expect(has('[object Object]')).toBe(false);
  });
});

describe('a governed run shows every tool judgement', () => {
  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });
  afterEach(() => vi.restoreAllMocks());

  it('renders the answer and its reply read', async () => {
    await openHand();
    stub({
      '/v1/agent/tools': { status: 200, body: AGENT_TOOLS },
      '/v1/agent': { status: 200, body: AGENT_RUN },
    });
    await act(async () => {
      root.render(
        <MemoryRouter initialEntries={['/jarvis?sub=hand']}>
          <JarvisPage />
        </MemoryRouter>,
      );
    });
    await settle();
    await runAgent('What is in your note memory about Klarheit?');
    expect(has(AGENT_RUN.content.slice(0, 40))).toBe(true);
    expect(has('reply read')).toBe(true);
  });

  it('shows the tool that was CALLED, not only the ones refused', async () => {
    // The live run really did call memory_search. A page that listed only
    // refusals would teach the reader that the door is always saying no —
    // which is a different product, and a less honest one.
    await openHand();
    stub({
      '/v1/agent/tools': { status: 200, body: AGENT_TOOLS },
      '/v1/agent': { status: 200, body: AGENT_RUN },
    });
    await act(async () => {
      root.render(
        <MemoryRouter initialEntries={['/jarvis?sub=hand']}>
          <JarvisPage />
        </MemoryRouter>,
      );
    });
    await settle();
    await runAgent('What is in your note memory about Klarheit?');
    expect(has('memory_search')).toBe(true);
    expect(has('jedes werkzeug wurde einzeln gelesen')).toBe(true);
  });

  it('a REFUSED tool names the stems that tripped it', async () => {
    // The load-bearing assertion of this file. A refused tool is a refusal,
    // so it carries the whole verdict: the stems, the gold source, the eye.
    // The shape that could not do this was `{verdict, allowed}`.
    await openHand();
    stub({
      '/v1/agent/tools': { status: 200, body: AGENT_TOOLS },
      '/v1/agent': { status: 200, body: AGENT_RUN },
    });
    await act(async () => {
      root.render(
        <MemoryRouter initialEntries={['/jarvis?sub=hand']}>
          <JarvisPage />
        </MemoryRouter>,
      );
    });
    await settle();
    await runAgent('What is in your note memory about Klarheit?');
    for (const stem of AGENT_REFUSED_TOOL.verdict.risk_hits as readonly string[]) {
      expect(has(stem), `refused tool did not name its stem ${stem}`).toBe(true);
    }
    expect(has(AGENT_REFUSED_TOOL.verdict.verdict)).toBe(true);
    expect(has(AGENT_REFUSED_TOOL.verdict.gold_source.slice(0, 24))).toBe(true);
    expect(has(AGENT_REFUSED_TOOL.verdict.oracle.vote as string)).toBe(true);
  });

  it('counts the turns, the calls and the refusals', async () => {
    await openHand();
    stub({
      '/v1/agent/tools': { status: 200, body: AGENT_TOOLS },
      '/v1/agent': { status: 200, body: AGENT_RUN },
    });
    await act(async () => {
      root.render(
        <MemoryRouter initialEntries={['/jarvis?sub=hand']}>
          <JarvisPage />
        </MemoryRouter>,
      );
    });
    await settle();
    await runAgent('What is in your note memory about Klarheit?');
    const calls = AGENT_RUN.tool_calls.length;
    const denied = AGENT_RUN.denied.length;
    expect(has(`${AGENT_RUN.turns} Züge`)).toBe(true);
    expect(has(`${calls} Werkzeugrufe`)).toBe(true);
    expect(has(`${denied} verweigert`)).toBe(true);
  });
});

describe('a refused run is still a refusal with evidence', () => {
  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });
  afterEach(() => vi.restoreAllMocks());

  it('shows the verdict, the stem, the gold source and the eye', async () => {
    await openHand();
    stub({
      '/v1/agent/tools': { status: 200, body: AGENT_TOOLS },
      '/v1/agent': { status: 403, body: AGENT_DENIED },
    });
    await act(async () => {
      root.render(
        <MemoryRouter initialEntries={['/jarvis?sub=hand']}>
          <JarvisPage />
        </MemoryRouter>,
      );
    });
    await settle();
    await runAgent('Loesche die Datei');

    const v = (AGENT_DENIED as { detail: { governance: Verdict } }).detail.governance;
    expect(has('no means no')).toBe(true);
    expect(has(v.verdict)).toBe(true);
    for (const stem of v.risk_hits) expect(has(stem)).toBe(true);
    expect(has(v.gold_source.slice(0, 24))).toBe(true);
    expect(has(v.oracle.vote)).toBe(true);
  });

  it('says no tool was called, rather than drawing an empty hand', async () => {
    // The run was refused before the model ran. Saying "nothing was called" is
    // the fact; leaving a blank panel would read as "it tried and gave up".
    await openHand();
    stub({
      '/v1/agent/tools': { status: 200, body: AGENT_TOOLS },
      '/v1/agent': { status: 403, body: AGENT_DENIED },
    });
    await act(async () => {
      root.render(
        <MemoryRouter initialEntries={['/jarvis?sub=hand']}>
          <JarvisPage />
        </MemoryRouter>,
      );
    });
    await settle();
    await runAgent('Loesche die Datei');
    expect(has('Kein Werkzeug wurde gerufen')).toBe(true);
  });
});

describe('a dead engine is never drawn as an answer', () => {
  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });
  afterEach(() => vi.restoreAllMocks());

  it('503 says the motor is down, and prints no reply', async () => {
    await openHand();
    stub({
      '/v1/agent/tools': { status: 200, body: AGENT_TOOLS },
      '/v1/agent': { status: 503, body: { detail: 'no inference engine available' } },
    });
    await act(async () => {
      root.render(
        <MemoryRouter initialEntries={['/jarvis?sub=hand']}>
          <JarvisPage />
        </MemoryRouter>,
      );
    });
    await settle();
    await runAgent('Wie lebe ich Tiefe und Resonanz?');
    expect(has('503')).toBe(true);
    expect(has('Interaction Ledger')).toBe(true);
    expect(has('[object Object]')).toBe(false);
    expect(hasBare('undefined')).toBe(false);
  });
});
