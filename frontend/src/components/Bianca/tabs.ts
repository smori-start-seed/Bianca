/**
 * The five tabs — ONE writer.
 *
 * The same discipline that `sovereign/trialog.py` applies to the three voices
 * applies here to the navigation: the sovereign face and this app must not be
 * able to disagree about what the node's cast is. The tab bar, the command
 * palette and the tests all read this file, so a sixth tab cannot appear in
 * one place and be missing from another.
 *
 * Exactly five, and the set is the node's own cast: the three voices plus the
 * sovereign who rules them plus the substrate that hosts them.
 */

import {
  MessagesSquare,
  MessageSquare,
  Sparkles,
  Orbit,
  Network,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type TabId = 'trialog' | 'jarvis' | 'bianca' | 'urasil' | 'node';

export interface SubView {
  id: string;
  label: string;
  /** What this option is for. A label without a purpose is a mystery. */
  hint?: string;
  /**
   * True when this option is a platform page carried over unchanged. It lives
   * under the tab whose character matches it, because hiding a shipped
   * feature to tidy a tab bar would be a lie about the product.
   */
  platform?: boolean;
}

export interface TabDef {
  id: TabId;
  /** The tab's name. Shown in the bar. */
  label: string;
  /** One line: what this tab is FOR, in the tab's own character. */
  hint: string;
  icon: LucideIcon;
  /** Primary route. */
  path: string;
  /** The available options inside the tab. */
  subs: SubView[];
}

/** The gold values, in the order the doctrine states them. */
export const GOLD: { id: string; de: string; en: string }[] = [
  { id: 'klarheit', de: 'Klarheit', en: 'clarity' },
  { id: 'integritaet', de: 'Integrität', en: 'integrity' },
  { id: 'resonanz', de: 'Resonanz', en: 'resonance' },
  { id: 'tiefe', de: 'Tiefe', en: 'depth' },
  { id: 'harmonie', de: 'Harmonie', en: 'harmony' },
];

export const TABS: TabDef[] = [
  {
    id: 'trialog',
    label: 'Trialog',
    hint: 'drei Stimmen, eine Frage',
    icon: MessagesSquare,
    path: '/trialog',
    subs: [
      { id: 'run', label: 'Rat', hint: 'die drei Stimmen beraten' },
      { id: 'session', label: 'Sitzung', hint: 'eine Arbeitssitzung mit Ziel und Abschluß' },
      { id: 'archive', label: 'Protokoll', hint: 'was schon gesprochen wurde' },
    ],
  },
  {
    id: 'jarvis',
    label: 'Jarvis chat',
    hint: 'das Substrate',
    icon: MessageSquare,
    path: '/jarvis',
    subs: [
      { id: 'platform', label: 'Unterhaltung', hint: 'die Unterhaltung mit Jarvis' },
      { id: 'sovereign', label: 'Bewerteter Dialog', hint: 'jeder Zug wird vorher bewertet' },
      { id: 'hand', label: 'Hand', hint: 'das Schwert: Werkzeuge, jedes einzeln bewertet' },
    ],
  },
  {
    id: 'bianca',
    label: 'Bianca',
    hint: 'der Souverän',
    icon: Sparkles,
    path: '/bianca',
    subs: [
      { id: 'self', label: 'Ich', hint: 'wer ich bin und wo ich stehe' },
      { id: 'verdict', label: 'Tor', hint: 'das Urteil, ohne Inferenz' },
      { id: 'ask', label: 'Frage', hint: 'Harmony komponiert, dann antwortet der Motor' },
      { id: 'today', label: 'Heute', hint: 'das Briefing und das zweite Auge' },
      { id: 'settings', label: 'Grenzen', hint: 'meine eigenen Grenzen', platform: true },
    ],
  },
  {
    id: 'urasil',
    label: 'Urasil_light',
    hint: 'der Zyklus',
    icon: Orbit,
    path: '/urasil',
    subs: [
      { id: 'cycle', label: 'Zyklus', hint: 'Sonne, Mond und Tag, live gelesen' },
      { id: 'levels', label: 'Fünf Ebenen', hint: 'der Atem, in dem gearbeitet wird' },
      { id: 'gate', label: 'Torwächter', hint: 'die fünf Harmonie-Stufen' },
      { id: 'agents', label: 'Kräfte', hint: 'die Agenten des Zyklus', platform: true },
      // Set 25: the garden is its own screen, not a card inside the cycle. It
      // is a sibling kernel with two defects of its own and an ungated surface,
      // and burying that under "Zyklus" would have put a dead world in front of
      // a reader who came for the sun.
      { id: 'garden', label: 'Garten', hint: 'Colorverse, wie er ist — ungatet' },
    ],
  },
  {
    id: 'node',
    label: 'Node & Net',
    hint: 'der Knoten und das Myzel',
    icon: Network,
    path: '/node',
    subs: [
      { id: 'pulse', label: 'Puls', hint: 'Lebenszeichen, Vertrag, idle' },
      { id: 'netz', label: 'Netz', hint: 'Manifest, Sporen, öffentliche Fläche' },
      { id: 'sources', label: 'Quellen', hint: 'was der Knoten aufnimmt', platform: true },
      { id: 'ledger', label: 'Ledger', hint: 'jede Zeile ist ein Ereignis', platform: true },
      { id: 'telemetry', label: 'Telemetrie', hint: 'Energie, Tempo, Kosten', platform: true },
      { id: 'start', label: 'Anfang', hint: 'dieser Knoten, Schritt für Schritt', platform: true },
    ],
  },
];

export const TAB_IDS: TabId[] = TABS.map((t) => t.id);

export function tabById(id: string): TabDef | undefined {
  return TABS.find((t) => t.id === id);
}

/**
 * Which tab owns a legacy path.
 *
 * The old seven-route sidebar is being folded into five tabs, but those URLs
 * are already bookmarked, deep-linked from the desktop shell, and excluded
 * from the PWA navigation fallback. Deleting them would break working
 * software to make a tab bar prettier, so they redirect instead.
 */
export const LEGACY_ROUTES: Record<string, { tab: TabId; sub: string }> = {
  '/': { tab: 'jarvis', sub: 'platform' },
  '/dashboard': { tab: 'node', sub: 'telemetry' },
  '/data-sources': { tab: 'node', sub: 'sources' },
  '/logs': { tab: 'node', sub: 'ledger' },
  '/agents': { tab: 'urasil', sub: 'agents' },
  '/settings': { tab: 'bianca', sub: 'settings' },
  '/get-started': { tab: 'node', sub: 'start' },
};
