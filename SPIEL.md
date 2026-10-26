# SPIEL.md — das Abenteuer, das deine Maschine zurückgibt

*Stand: Set 32 (2026-10-01). Kein Fahrplan auf Papier, sondern das Dokument,
das neben dem spielbaren Keim liegt. Wer beides nicht mehr liest, versteht
trotzdem, was hier gebaut wird und warum es so gebaut ist.*

## Der Satz, um den es geht

> *I still want to have this a fun local AI that give sovereignty back to the
> HW owner. We went so deep we forgot the basic. The user playing field. It a game
> to reclaim digital sovereignty.*

Die letzten drei Sätze haben die Zahl der Türen verdoppelt und den Menschen
zugerechnet, der vor ihnen sitzt. Dieser Satz sagt: die Türen sind genug. Was
fehlt, ist der Grund, hinzusehen. Also bekommt die Hülle ein **Spiel** — und
damit eine Hülle, in der Souveränität etwas zum Anfassen hat, statt eine Liste
von Werten, die man richtig finden muss.

## Vier Regeln, und jede ist eine Tür

**1. Eine Quest IST eine Tür.** Kein Quest, keine verschlossene Schatztruhe,
kein erfundener Gegner. Jede Station ruft genau eine Tür dieses Knotens und
schreibt in ihre Karte, was die Tür gesagt hat — im Wortlaut, unter dem
Feldnamen, den die Tür selbst benutzt. Der Idle-Vertrag FAILt heute ehrlich, und
deshalb steht der Boss heute offen auf der Karte. Ein Spiel, das seinen Boss
schöner als die Wirklichkeit zeigt, wäre die vierte Fläche dieses Produkts, die
eine Behauptung ohne Beweis zeigt.

Geprüft wird das nicht durch ein Versprechen, sondern durch die Behauptung
`the-quests-are-real-doors`: sie liest die Quest-Tabelle aus dem Gesicht, liest
die Routen aus den Dekoratoren von `api.py` und fragt jede benannte Tür an
einem echten Knoten.

**2. Kein Fortschritt wird gespeichert.** Das Spiel besitzt keinen Zustand, es
**spiegelt**: eine Quest steht so gut da, wie ihre Tür gerade steht. Nichts
wird abgehakt, nichts bleibt „gewonnen", wenn die Tür es nicht mehr hergibt.
Wem das zu streng ist: der Idle-Boss wird *innerhalb* von 15 Sekunden gefallen
sein, ohne einen Neustart, sobald du ihn wirklich heilst — und das ist der
einzige Weg, auf dem diese Zahl hier jemals steigen wird.

**3. Ein Handgriff ist auch eine Tür.** Seit Set 32 *handelt* das Spiel zum
ersten Mal: Jarviss Station trägt einen Knopf, und der Knopf geht an genau eine
Tür — `POST /v1/engine/start`, **ohne Rumpf**. Damit gelten für den Schreibweg
dieselben Regeln wie für die Lesewege, nur strenger: die Regel *„eine Quest ist
eine Tür"* wird zu *„eine Quest ist eine Tür, und ein Schreibweg ist eine POST"*.
Geprüft wird das in derselben Behauptung: eine Quest mit einem Handgriff, deren
Tür ein `GET` ist, lässt sie FAILen — *ein Schreibweg, der auf GET antwortet, ist
ein Seitenaufruf mit Motor darin.*

Der Knopf ist ausdrücklich, genau wie `garden/start` und `idle start`: **eine
Ansicht darf niemals sein, was einen Prozess erscheinen lässt**, sonst wäre jeder
15-Sekunden-Takt ein Start. Das argv steht **einmal** in `motor.py`, es gibt kein
`stop`, und **es gibt kein `sudo`** — die Tür kann niemals erhöhen. Wann der Motor
tatsächlich antwortet, sagt die Tür selbst, mit den Worten des Kindes, das sie
gestartet hat (`child_words`), nicht mit einer Zusammenfassung.

**Und die Tür wird nicht von der Governance geprüft — mit Begründung, nicht mit
Auslassung.** Der `ValueGovernor` richtet über *Worte*, und hier trägt der Vorgang
keine und erzeugt nichts; Antworten entstehen nur hinter `/v1/ask`, `/v1/chat`,
`/v1/agent`, `/v1/trialog`, und diese vier Türen sind unverändert. Ein Vorgang ohne
Worte braucht keine Wortschleuse — er braucht eigene Grenzen, und die sind
unten aufgeschrieben.

**4. Der Boden kommt aus dem Garten.** Farbe, Höhe und Halte der Welt sind
`GET /v1/garden`: die Helligkeit des Feldes ist `drift / drift_threshold` — der
Kern gegen den **eigenen** Schwellwert. Ein zur Stillstand geborener Kern malt
deshalb ein flaches Feld, weil er eines ist. Die Büschel werden aus Tag und
Schritt **geeseedet**, nicht gewürfelt: dieselbe Welt bei zwei Öffnungen.

## Die vier Figuren

| Figur | Station | Tür | Gang |
|:--|:--|:--|:--|
| 🧭 **Du** | Der Knoten | `GET /health` | WASD / Pfeiltasten, oder Klick auf eine Station |
| ⚙️ **Jarvis** | Der Motor | `GET /v1/models` **+ `POST /v1/engine/start`** | patrouilliert, bleibt an seiner Station, misst — und startet den Motor, wenn du es ihm **sagst** |
| 🌗 **Urasil_light** | Die Welt | `GET /v1/garden` | patrouilliert, misst den Zyklus des Gartens |
| 🛡️ **Bianca** | Der Vertrag | `GET /idle/contract` | patrouilliert, misst den Vertrag |

Die drei Stimmen reden nicht frei — sie sagen, was **ihre** Station gemessen
hat. Ein Klick auf eine Figur fragt ihre Tür sofort ab und lässt sie antworten.
(Ein freier Dialog kommt als eigener Satz, wenn du ihn willst; diese Runde baut
noch keinen.)

## Der Einzug — das erste Abenteuer

Das Erststart-Abenteuer *ist* die Installation: vier Schritte, vier echte
Prüfungen deiner Maschine.

| Schritt | Station | gewonnen, wenn … |
|:--|:--|:--|
| 1 | Der Knoten | die Tür antwortet **und** `gold.txt` geladen ist |
| 2 | Der Motor | die Engine erreichbar ist (Modelle kommen zurück) — und wenn nicht, **startet der Knopf sie dir** |
| 3 | Die Welt | der Garten einen Rahmen hat, also **atmet** |
| 4 | Der Vertrag | `contract_holds` — kein verwaistes Audit |

Schritt 4 steht heute offen, und die Karte nennt den Waisen-Audit wörtlich
(`unit=2026-09-24_051141`). Der Weg zurück ist ein echter Befehl, kein Klick:

```
bianca-sovereign idle reconcile 2026-09-24_051141 "<Grund>"
```

### Der gemessene Vorbehalt zu Schritt 2

Wer den Knopf drückt, bekommt **nicht** automatisch die Modelle des
Eigentümers, und das Spiel behauptet das auch nicht. Gemessen am 2026-10-02 auf
dieser Maschine (die Prozessnummer ist ein **Datum**, kein Zustand — sie ändert
sich, wenn der Eigentümer seinen Server neu startet):

* Der laufende Modellserver (am 2026-10-02: pid **2180**) gehört dem Systembenutzer
  `ollama:ollama`. Sein `/proc/<pid>/environ` ist für `sam` **nicht lesbar**, und
  `sam`s `~/.ollama/models` enthält **0 Dateien**.
* Ein von diesem Knoten gestarteter `ollama serve` **antwortet** — aber mit einem
  **leeren Katalog**.

Darum sagt die Karte genau das, was sie gemessen hat: *„der Motor antwortet, aber
es ist kein Modell installiert"*, mit dem Hinweis auf `ollama pull`. Eine leere
Modellliste ist damit zwei Tatsachen in einer Form, und das Spiel sagt inzwischen,
welche es ist — seit Set 32 trägt `GET /v1/models` neben den Namen einen
`engine`-Block (`key`, `reachable`, `host`, `why`), und **die Tür wird hier nicht
hochgefahren, um das zu reproduzieren**. Wer den Eigentümer-Server nachahmen
müsste, um seinen Katalog zu sehen, hätte dafür einen zweiten Benutzer und einen
elevierten Befehl gebraucht — beides ist eine Entscheidung des Eigentümers und
nicht dieses Sets.

Schritt 3 zählt als gewonnen, wenn der Garten atmet — **und** benennt daneben
wörtlich, dass er zur Stillstand geboren ist und ab Schritt *N dieses Laufs*
eine einzige Farbe hat. Beides gleichzeitig: gewonnen und kaputt. Genau das
soll das Spiel können.

## Wie man spielt

```
bianca-sovereign serve            # der Knoten (einmal)
bianca-sovereign spiel            # öffnet das Gesicht auf dem Abenteuer
```

Im Gesicht: Tab **Trialog** → **Spiel**. Das Feld ist ein `<canvas>` (kein
Build, kein WebGL, keine Abhängigkeit). Pfeiltasten oder **WASD** bewegen
dich; ein Klick auf eine Station schickt dich hin; ein Klick auf eine Figur
lässt sie reden. Wer Bewegung nicht braucht, bekommt bei
`prefers-reduced-motion: reduce` ein stehendes Bild — dieselben Zahlen, kein
Geruckel.

## Was das Spiel **nicht** ist

- **Kein Ersatz für `bianca doctor`.** Zwölf HW-Diagnosen sind eine CLI, keine
  Quest; sie gehören in eine spätere HW-Runde, die Station werden *kann*.
- **Kein Speicher.** Es gibt keinen Spielstand, weil es nichts zu gewinnen gibt
  außer einer reparierten Maschine.
- **Keine Umgehung der Herrschaft.** Das Spiel fragt dieselben Türen, die die
  Schreibwege benutzen — und der eine Schreibweg, den es seit Set 32 gibt, ist
  eine echte POST-Tür mit demselben Namen im argv wie im Code und **ohne**
  Bestätigungsdialog. Wer einen Motor starten will, drückt einmal; wer das nicht
  will, drückt nichts. Ein Dialog wäre hier ein Spielmechanik, kein Schutz.
- **Kein Profiler.** Ein Knopf ohne Ende: es gibt **kein `stop`**, nur die
  Elternlosigkeit von `ollama serve`. `ollama` ist ein Dienst des Eigentümers; wer
  ihn beenden will, tut das mit `pkill` — und diese Tür hat dafür keine Taste
  bekommen, weil ein Kill-Knopf auf einem Port, den jemand anderes gestartet
  haben könnte, niemals die Hand des Eigentümers ist. Das ist eine bewusst
  offene Lücke, keine vergessene.
- **Kein React-Spiel.** Der Knopf existiert nur im Gesicht (`web/ui.html`). Die
  React-Fläche *liest* den neuen `engine`-Block (sie unterscheidet jetzt
  „der Motor antwortet nicht" von „der Motor nennt keine Modelle"), startet aber
  nichts: eine zweite Fläche, die einen Prozess starten kann, wäre eine zweite
  Tür, die niemand gezählt hat.

## Die Straße danach

1. **Bosskämpfe aus echten FAILs.** Der Vertrag ist der erste; die übrigen
   FAIL-Zeilen der Doors (`/v1/garden`-Diagnose, ein FAIL im Mirror) werden
   Stationen mit demselben Muster: Ring in der Zustandsfarbe, ehrlicher Text.
2. **HW-Anpassung als Questkette.** Der RAPL-Sampler, der Speicher, die
   Modelle — eine Station pro Gerät, jede mit einem Befehl, der etwas ändert.
   Voraussetzung ist eine Tür, die die Arztberichte heute nur als CLI kennt;
   das ist die einzige echte Neuentwicklung, die dieser Satz sich leistet.
3. **Sitzungen als Gruppenabenteuer.** Die Arbeitssitzung (Set 30) ist bereits
   ein Team, das bleibt; sie ist nur noch kein Ort auf der Karte. Eine
   Session, die eine Quest als Ziel nennt, wäre die natürlichste Brücke.
4. **Stimmen sprechen lassen.** Der Keim zeigt die *Tür*, nicht die *Stimme*.
   Ein Durchlauf durch die drei Stimmen gehört durch dieselben Schilde wie
   jeder andere Schreibweg — sonst wäre das Spiel die Hintertür, die die
   Governance ausschließt.
5. **Die Fläche ist noch nicht gesehen worden.** Auf dieser Maschine ist kein
   Pixel-Beweis möglich (Firefox-Kompositor scheitert, jsdom kann keine ES
   Module). Der Beweis für diesen Satz ist ein Live-Abruf des ausgelieferten
   Gesichts — **ein menschlicher Blick auf jede Fläche ist weiterhin offen.**

## Woher das kommt

| | |
|:--|:--|
| **Geschrieben von** | dem OpenCode-Agenten, in Set 31, auf Weisung des Eigentümers; Set 32 ergänzt den Handgriff (auf dieselbe Weisung: *„we do have already ollama included, so lets add ollama lauche into the game"*) |
| **Abgeleitet von** | dem Gesicht (`web/ui.html`, Set 31 **+ 32**), den vier Lesetüren (`/health`, `/v1/models`, `/v1/garden`, `/idle/contract`) und der einen Schreibtür (`POST /v1/engine/start`), den Behauptungen `the-quests-are-real-doors` und `the-launch-is-not-the-browsers-to-decide`, und den Notizen von Set 31 **+ 32** |
| **Zuletzt geprüft** | 2026-10-01 — 4 Quests, 4 Lesetüren, 1 Schreibtür; alle an einem echten Knoten, **zwei echte Kaltstarts** (0,26 s / 0,30 s bis `ready`), Behauptungen 26/26 |
| **Prüf es selbst** | `python3 scripts/verify_claims.py` |
| **Nicht behauptet** | dass ein Boss je fällt, dass das Feld hübsch ist, dass jemand es angesehen hat, oder dass der Knopf deinen Modellkatalog wiederherstellt — er startet einen leeren Motor, wenn der Eigentümer-Server unter einem anderen Benutzer läuft |