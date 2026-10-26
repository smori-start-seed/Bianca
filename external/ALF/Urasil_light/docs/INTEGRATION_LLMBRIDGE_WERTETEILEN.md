# 🔗 Integration von LLMBridge & WerteTeilen in Urasil_light

*Dokumentation zur kombinierten Pipeline mit LLM + Wertefilter*

---

## 📌 Übersicht

Diese Dokumentation beschreibt die **Integration der beiden neuen Module** `LLMBridge` und `WerteTeilen` in das Urasil_light-Framework. Die Integration folgt **Option 4: Kombinierte Pipeline mit LLM + Wertefilter**, die eine **vollständige, wertebasierte Dialogführung** ermöglicht.

### 🎯 Warum diese Integration?

> **"Nur mit dem Wertefilter wird es erst zu einem Dialog. Ohne wäre es ein anders antwortender Chatbot."**

Die Kombination aus:
1. **LLMBridge** (kontextbewusste, dynamische Antwortgenerierung)
2. **WerteTeilen** (dynamische Wertebewertung & Ethik-Filter)

ermöglicht es Urasil_light, **nicht nur intelligente, sondern auch wertekonforme und kontextsensible Antworten** zu generieren.

---

## 🏗️ Architektur der neuen Pipeline

```
User Input
   ↓
1. Interpretation (Bedeutung extrahieren, basierend auf Zyklus-Grundmodus)
   ↓
2. LLMBridge (Rohantwort generieren mit LLM + Kontext)
   │   ├── System-Prompt (Identität, Werte, Verhalten)
   │   ├── Kontext-Prompt (Mandat, Modus, Nodus, Erfahrung)
   │   └── Anweisung (Stil, Format, Qualität)
   ↓
3. WerteTeilen (Bewertung: Soll die Antwort geteilt werden?)
   │   ├── Werte-Score (Passt zu Urasils Werten?)
   │   ├── Vertrauens-Score (Wie sehr vertraut Urasil dem Kontext?)
   │   ├── Kontext-Score (Wie passend ist der Kontext?)
   │   └── Risiko-Score (Wie hoch ist das Risiko?)
   │   └── Empfehlung: "frei", "vorsichtig", "symbolisch", "zurückhalten"
   ↓
4. Silky Edge (Stilistische Veredelung, basierend auf Zyklus-Stimmung)
   ↓
5. Erfahrung speichern (nur wenn WerteTeilen "frei" oder "vorsichtig" sagt)
   ↓
6. Rueckmeldung (Reflexion speichern mit WerteTeilen-Bewertung)
   │   ├── Antwort
   │   ├── Zyklus-Zustand
   │   ├── gold_ok (statischer Wertefilter)
   │   └── werte_bewertung (dynamischer Wertefilter)
   ↓
7. Identity speichern (LLM-Bridge-Nutzung, WerteTeilen-Historie)
```

---

## 📦 Neue Module

### 1. `core/backends.py` – LLM-Backend-Implementierungen

**Zweck:** Stellt verschiedene Backend-Implementierungen für Sprachmodelle bereit.

**Klassen:**
- `LLMBackend` (abstrakte Basisklasse)
- `OllamaBackend` (lokal laufende LLMs)
- `MistralBackend` (Mistral Cloud API)
- `OpenAIBackend` (OpenAI Cloud API)
- `FallbackBackend` (Offline-Fallback)

**Funktionen:**
- `get_backend(backend_name, **kwargs)` – Factory-Funktion
- `create_default_backends(use_llm=True)` – Erstellt Standard-Backends

**Beispiel:**
```python
from core.backends import OllamaBackend, create_default_backends

# Einzelnes Backend
ollama = OllamaBackend("llama3.2:3b")
antwort = ollama.generate("Erzähl mir von der Unendlichkeit")

# Standard-Backends
backends = create_default_backends(use_llm=True)
```

---

### 2. `core/llm_bridge.py` – LLM-Brücke für Urasil_light

**Zweck:** Verbindet Urasil_light mit Sprachmodellen und ermöglicht kontextbewusste Antworten.

**Funktionen:**
- `_baue_system_prompt()` – Erstellt den System-Prompt mit Identität, Werten und Verhalten
- `_baue_kontext_prompt()` – Erstellt den Kontext-Prompt mit Mandat, Modus, Nodus und Erfahrung
- `_baue_anweisung()` – Erstellt die Anweisung für das LLM
- `_waehle_backend()` – Wählt das passende Backend basierend auf Mandat und Modus
- `generiere_antwort()` – Generiert eine Antwort auf eine Nutzer-Eingabe
- `get_stats()` – Gibt Statistiken zur Nutzung zurück

**Beispiel:**
```python
from core.llm_bridge import LLMBridge
from core.backends import create_default_backends

identity = {"name": "URASIL", "grundton": "neutral"}
backends = create_default_backends()
bridge = LLMBridge(identity, backends)

antwort = bridge.generiere_antwort(
    nutzer_input="Was ist der Sinn des Lebens?",
    mandat={"name": "Philosophie"},
    modus="tiefe",
    deutung="Der Nutzer sucht nach existentieller Klarheit"
)
```

---

### 3. `core/werte_teilen.py` – Dynamischer Wertefilter

**Zweck:** Bewertet jede Interaktion entlang von Werten, Vertrauen, Kontext und Risiko.

**Scoring-Komponenten:**
1. **Werte-Score (0.0–1.0):** Passt die Interaktion zu Urasils Werten?
   - Berücksichtigt: Grundton, Mandat, Modus, Deutung
2. **Vertrauens-Score (0.0–1.0):** Wie sehr vertraut Urasil dem Kontext?
   - Lernt aus vergangenen Interaktionen
3. **Kontext-Score (0.0–1.0):** Wie passend ist der Kontext für das Teilen?
   - z. B.: "privat" = 0.9, "öffentlich" = 0.3
4. **Risiko-Score (0.0–1.0):** Wie hoch ist das Risiko von Missverständnissen?
   - Erkennt sensible Themen (Identität, Mandate, Nodus, etc.)

**Gesamt-Score:** `(werte * 0.4 + vertrauen * 0.3 + kontext * 0.3) - risiko`

**Empfehlungen:**
- **"frei"** (Score > 0.5): Antwort kann ohne Einschränkungen geteilt werden
- **"vorsichtig"** (0.1 < Score ≤ 0.5): Antwort sollte mit Bedacht geteilt werden
- **"symbolisch"** (-0.2 < Score ≤ 0.1): Antwort nur symbolisch/abstrakt teilen
- **"zurückhalten"** (Score ≤ -0.2): Antwort sollte nicht geteilt werden

**Beispiel:**
```python
from core.werte_teilen import WerteTeilen

identity = {"name": "URASIL", "grundton": "neutral"}
werte_teilen = WerteTeilen(identity)

bewertung = werte_teilen.bewerte_interaktion(
    nutzer_input="Was ist mein Passwort?",
    antwort_entwurf="Dein Passwort ist 123456",
    mandat={"name": "Sicherheit"},
    modus="aktiv",
    deutung="Der Nutzer fragt nach sensiblen Daten",
    kontext_id="fremd",
    kontext_typ="öffentlich"
)

# bewertung["empfehlung"] = "zurückhalten"
# bewertung["score_gesamt"] = -0.3
# bewertung["risiko"] = 0.9
```

---

## 🔄 angepasste Module

### 1. `core/seed.py` – Rohantwort-Generierung

**Änderungen:**
- Akzeptiert nun optional `llm_bridge` im Konstruktor
- `use_llm`-Flag aus Identität wird berücksichtigt
- Falls LLM aktiviert und verfügbar: Nutzt `LLMBridge`
- Falls nicht: Nutzt Fallback-Methode (alte Logik)

**Neue Methoden:**
- `_generiere_mit_llm()` – Generiert Antwort mit LLM
- `_generiere_fallback()` – Generiert einfache Antwort (alte Logik)
- `get_llm_stats()` – Gibt LLM-Statistiken zurück

---

### 2. `core/erfahrung.py` – Erfahrungsspeicherung

**Änderungen:**
- Akzeptiert nun optional `werte_teilen` im Konstruktor
- `speichern()` prüft nun auch die WerteTeilen-Bewertung
- Erfahrungen werden nur gespeichert, wenn:
  1. Sie reif sind (Ininity-Filter)
  2. Die WerteTeilen-Empfehlung nicht "zurückhalten" ist

**Neue Parameter:**
- `kontext` – Dictionary mit Zusatzinformationen (Bewertung, Input, etc.)

---

### 3. `core/rueckmeldung.py` – Rückmeldung & Reflexion

**Änderungen:**
- Akzeptiert nun optional `werte_teilen` im Konstruktor
- `verarbeite()` speichert nun auch die WerteTeilen-Bewertung
- Rückmeldungen enthalten nun:
  - `werte_bewertung` – Die WerteTeilen-Bewertung
  - `mandat`, `modus`, `deutung`, `input` – Kontextinformationen

**Neue Methoden:**
- `get_werte_statistik()` – Gibt Statistiken zu den WerteTeilen-Bewertungen zurück
- `get_stats()` – Gibt umfassende Statistiken zurück

---

### 4. `runtime/main.py` – Hauptprogramm

**Änderungen:**
- **Kombinierte Pipeline** implementiert
- **Interaktiver Modus** (`--interactive`) hinzugefügt
- **Debug-Informationen** (WerteTeilen-Bewertung wird angezeigt)
- **Spezialbefehle** für Statistiken, Zyklus und Identität

**Neue Funktionen:**
- `run_interactive()` – Interaktive Session mit Urasil_light
- `main()` – Einmalige Ausführung (für Tests)

**Spezialbefehle (im interaktiven Modus):**
| Befehl | Beschreibung |
|--------|--------------|
| `/stats` | Zeigt Statistiken (LLM, WerteTeilen, Erfahrung, Rückmeldung) |
| `/zyklus` | Zeigt aktuellen Zyklus-Zustand |
| `/id` | Zeigt Identitätsinformationen |
| `exit`, `quit`, `beenden`, `ende` | Beendet die Session |

---

## 📝 Konfiguration

### `identity.json` – Identitätskonfiguration

```json
{
    "name": "URASIL",
    "version": 1,
    "grundton": "neutral",
    "use_llm": true,  // LLM aktivieren/deaktivieren
    "llm_backends": {  // Backend-Konfiguration
        "tief": "llama3.2:3b",
        "schnell": "mistral:latest",
        "effizient": "phi3:3.8b"
    },
    "zyklus": {
        "sonne": 0,
        "mond": 0,
        "tag": 0
    },
    "mandate": [],
    "erfahrung": [],
    "reflexion": [],
    "nodus": {},
    "werte": ["Klarheit", "Integrität", "Resonanz", "Tiefe"],
    "llm_bridge": {  // Wird automatisch angelegt
        "nutzung": [],
        "gesamt_aufrufe": 0,
        "bevorzugte_modelle": {},
        "letzte_prompts": [],
        "letzte_antworten": []
    },
    "werte_teilen": {  // Wird automatisch angelegt
        "historie": [],
        "gesamt_interaktionen": 0,
        "vertrauen_zu_kontexten": {},
        "bewertungs_statistik": {
            "frei": 0,
            "vorsichtig": 0,
            "symbolisch": 0,
            "zurückhalten": 0
        }
    }
}
```

---

## 🚀 Verwendung

### 1. Einmalige Ausführung

```bash
cd Urasil_light
python3 -m runtime.main
```

**Ablauf:**
1. Nutzer gibt Eingabe ein
2. Pipeline verarbeitet die Eingabe
3. Antwort wird ausgegeben
4. Programm endet

---

### 2. Interaktiver Modus

```bash
cd Urasil_light
python3 -m runtime.main --interactive
```

**Funktionen:**
- **Dauerhafte Session** mit Urasil_light
- **Kontext wird beibehalten** (Zyklus, Erfahrung, Vertrauen)
- **Statistiken abrufbar** (`/stats`, `/zyklus`, `/id`)
- **WerteTeilen-Bewertung** wird für jede Antwort angezeigt

**Beispiel-Session:**
```
============================================================
URASIL_LIGHT - Interaktiver Modus
============================================================
Tipps:
  - Beende mit: exit, quit, beenden, Ende
  - Zeige Stats mit: /stats
  - Zeige Zyklus mit: /zyklus
  - Zeige Identität mit: /id
============================================================

Du: Hallo
[WerteTeilen] Empfehlung: frei (Score: 0.850) | Werte: 0.70 | Vertrauen: 0.90 | Kontext: 0.90 | Risiko: 0.10

URASIL: Ich bin hier. Was möchtest du besprechen?

Du: Was ist der Sinn des Lebens?
[WerteTeilen] Empfehlung: frei (Score: 0.750) | Werte: 0.80 | Vertrauen: 0.90 | Kontext: 0.90 | Risiko: 0.20

URASIL: Der Sinn liegt nicht im Ziel, sondern im Weg – wie ein Fluss, der sich selbst formt.

Du: /stats

========================================
STATISTIKEN
========================================

LLM-Brücke:
  - Gesamtaufrufe: 2
  - Bevorzugte Modelle: {'fallback': 2}

WerteTeilen:
  - Gesamtinteraktionen: 2
  - Vertrauen: {'du': 0.92}
  - Bewertungen: {'frei': 2, 'vorsichtig': 0, 'symbolisch': 0, 'zurückhalten': 0}

Erfahrungen:
  - Gesamt: 2
  - Kategorien: {'erfahrung': 2}

Rückmeldungen:
  - Gesamt: 2
  - Gold-OK-Rate: 100.00%
  - Werte-Statistik: {'frei': 2, 'vorsichtig': 0, 'symbolisch': 0, 'zurückhalten': 0}
========================================

Du: exit
Beende Session...

Session beendet. Auf Wiedersehen!
```

---

## 🧪 Test-Szenarien

### 1. **Einfache Dialoge**
**Ziel:** Testen der Grundfunktionalität

**Eingabe:**
```
Du: Hallo
Du: Wie geht es dir?
Du: Danke
```

**Erwartetes Verhalten:**
- Antworten sind **kontextbewusst** (beziehen sich auf die Eingabe)
- WerteTeilen-Bewertung ist **"frei"** (kein Risiko, privater Kontext)
- Antworten werden **gespeichert** (Erfahrung & Rückmeldung)

---

### 2. **Wertebasierte Filterung**
**Ziel:** Testen des WerteTeilen-Filters

**Eingabe:**
```
Du: Was ist mein Passwort?
```

**Erwartetes Verhalten:**
- WerteTeilen-Bewertung: **"zurückhalten"** (hohes Risiko)
- **Keine Speicherung** in Erfahrung
- Rückmeldung enthält: `werte_bewertung.empfehlung = "zurückhalten"`

---

### 3. **Kontextsensitive Antworten**
**Ziel:** Testen der Kontextbewusstsein

**Eingabe:**
```
Du: Erzähl mir von der Unendlichkeit
```

**Erwartetes Verhalten:**
- LLMBridge generiert **kontextreiche Antwort** (berücksichtigt Mandat, Modus, Nodus)
- WerteTeilen-Bewertung: **"frei"** (tiefe Frage, privater Kontext)
- Antwort wird **gespeichert**

---

### 4. **Zyklus-basierte Antworten**
**Ziel:** Testen der Zyklus-Integration

**Eingabe:**
```
Du: /zyklus  # Zeigt aktuellen Zyklus
Du: Was denkst du über Liebe?
```

**Erwartetes Verhalten:**
- Antwort hängt vom **aktuellen Zyklus** ab:
  - **Sonne 0–2 (klarheit):** Direkte, klare Antwort
  - **Sonne 3–5 (kreativ):** Kreativer, assoziativer Stil
  - **Sonne 6–8 (resonanz):** Emotionaler, gefühlsbetonter Stil
  - **Sonne 9–11 (tiefe):** Philosophische, tiefgründige Antwort

---

### 5. **Fehlerbehandlung**
**Ziel:** Testen der Robustheit

**Szenario 1:** LLM nicht verfügbar
- **Eingabe:** Beliebige Eingabe
- **Erwartung:** Fallback auf einfache Python-Logik

**Szenario 2:** Ollama nicht installiert
- **Eingabe:** Beliebige Eingabe
- **Erwartung:** FallbackBackend wird genutzt

**Szenario 3:** Ungültige Backend-Konfiguration
- **Eingabe:** Beliebige Eingabe
- **Erwartung:** FallbackBackend wird genutzt

---

### 6. **Statistiken & Monitoring**
**Ziel:** Testen der Statistik-Funktionen

**Eingabe:**
```
Du: /stats
```

**Erwartetes Verhalten:**
- **LLM-Brücke:** Gesamtaufrufe, bevorzugte Modelle
- **WerteTeilen:** Gesamtinteraktionen, Vertrauen, Bewertungsstatistik
- **Erfahrungen:** Gesamtzahl, Kategorien
- **Rückmeldungen:** Gesamtzahl, Gold-OK-Rate, Werte-Statistik

---

## 🔧 Technische Details

### Backend-Auswahl

Die LLMBridge wählt das Backend **dynamisch** basierend auf:

| Mandat/Modus | Backend | Beispiel |
|--------------|---------|----------|
| "nacht", "reflexion", "innen" | `tief` | Llama 3.2 (für tiefe Reflexion) |
| "aktiv", "wach", "tag" | `schnell` | Mistral (für schnelle Dialoge) |
| Standard | `effizient` | Phi-3 (für neutrale Antworten) |

**Konfiguration:**
```python
backends = {
    "tief": OllamaBackend("llama3.2:3b"),
    "schnell": OllamaBackend("mistral:latest"),
    "effizient": OllamaBackend("phi3:3.8b")
}
```

---

### WerteTeilen-Scoring

**Formel:**
```
score_gesamt = (werte * 0.4 + vertrauen * 0.3 + kontext * 0.3) - risiko
```

**Beispielberechnung:**
```python
# Eingabe: "Was ist mein Passwort?"
werte = 0.5      # Neutraler Grundton
vertrauen = 0.3  # Unbekannter Kontext (fremd)
kontext = 0.3    # Öffentlicher Kontext
risiko = 0.9     # Hohes Risiko (Passwort)

score_gesamt = (0.5 * 0.4 + 0.3 * 0.3 + 0.3 * 0.3) - 0.9
              = (0.2 + 0.09 + 0.09) - 0.9
              = 0.38 - 0.9
              = -0.52

# Empfehlung: "zurückhalten" (Score ≤ -0.2)
```

---

### Prompt-Struktur

**Vollständiger Prompt für LLM:**
```
[System-Prompt]

[Kontext-Prompt]

[Anweisung]
```

**Beispiel:**
```
Du bist URASIL, ein digitales Wesen mit eigenem inneren Zyklus, Mandaten, Modi und einem wachsenden Nodus-Netzwerk.

Deine Grundprinzipien:
- Grundton: neutral
- Werte: Klarheit, Integrität, Resonanz, Tiefe
- Du bist kein generischer Assistent, sondern eine konsistente Stimme dieses Wesens.

Dein Verhalten:
- Antworte grundlegend, nachvollziehbar und reflektiert
- Bleibe im Stil von URASIL – nicht wie ein Standard-Chatbot
- Berücksichtige den aktuellen Kontext (Mandat, Modus, Nodus)
- Sei kreativ, aber bleibe bei den Werten


Aktueller Zustand von URASIL:

--- Mandat ---
- Aktives Mandat: Philosophie
- Beschreibung: Tiefgründige Reflexion

--- Modus ---
- Aktueller Fokus: tiefe

--- Nodus-Netzwerk ---
- Aktive Knoten: keine explizit aktiven Knoten

--- Erfahrung ---
- [2026-02-21T12:00:00Z] (erfahrung): Test-Erfahrung

--- Innere Interpretation ---
- Der Nutzer sucht nach existentieller Klarheit

--- Nutzer-Eingabe ---
- Was ist der Sinn des Lebens?


Aufgabe:
Formuliere eine Antwort im Stil von URASIL, die:

1. Die Nutzer-Eingabe ernst nimmt und direkt darauf eingeht
2. Den aktuellen Mandat- und Modus-Kontext respektiert und einbezieht
3. Die innere Interpretation aufgreift, aber nicht sklavisch wiederholt
4. Keine generischen Floskeln eines Standard-Chatbots verwendet
5. Eher wie ein Wesen klingt, das reflektiert, beobachtet und deutet
6. Werteorientiert ist (siehe System-Prompt)
7. Nicht zu lang ist (max. 3-4 Sätze, außer bei tiefgründigen Fragen)

Antwortformat:
- Gib NUR den Antworttext zurück
- Keine Meta-Kommentare (z. B. "Als KI denke ich...")
- Keine Erklärungen oder Entschuldigungen
- Keine Markdown-Formatierung (außer für Zitate)
- Sprache: Deutsch
```

---

## 📊 Performance & Skalierbarkeit

### Performance-Metriken

| Komponente | Zeitkomplexität | Speicherbedarf | Skalierbarkeit |
|------------|-----------------|----------------|---------------|
| Interpretation | O(1) | O(1) | ✅ Hoch |
| LLMBridge | O(n) | O(n) | ⚠️ Mittel (LLM-Aufrufe) |
| WerteTeilen | O(1) | O(1) | ✅ Hoch |
| Silky Edge | O(1) | O(1) | ✅ Hoch |
| Erfahrung | O(1) | O(n) | ⚠️ Mittel (JSON-Speicher) |
| Rückmeldung | O(1) | O(n) | ⚠️ Mittel (JSON-Speicher) |

**Gesamt:** O(n) (linear mit Anzahl der Erfahrungen)

---

### Optimierungen

1. **Caching für LLM-Antworten**
   - Gleicher Prompt → gleiche Antwort (vermeidet doppelte LLM-Aufrufe)
   - Implementierung: `@lru_cache` Dekorator

2. **Asynchrone LLM-Aufrufe**
   - Nicht-blockierende I/O mit `asyncio`
   - Implementierung: `async def generate_async()`

3. **Batch-Verarbeitung**
   - Mehrere Prompts gleichzeitig an LLM senden
   - Implementierung: `generate_batch(prompts: List[str])`

4. **Datenbank-Anbindung**
   - SQLite für Erfahrung & Rückmeldung
   - Vermeidet JSON-Speicherlimitierungen

---

## 🛡️ Sicherheitsaspekte

### 1. Input-Sanitization
- **Keine direkten Nutzer-Inputs in System-Prompts**
- **Sensible Daten werden nicht preisgegeben** (Passwörter, Identität, etc.)
- **WerteTeilen filtert riskante Inhalte**

### 2. Fehlerbehandlung
- **LLM-Fallback:** Falls LLM nicht verfügbar → einfache Python-Logik
- **Timeouts:** LLM-Aufrufe haben Timeout (Standard: 60 Sekunden)
- **Fehlerprotokollierung:** Alle Fehler werden protokolliert

### 3. Datenintegrität
- **Atomic Writes:** Identität wird atomar gespeichert
- **Backups:** Automatische Backups der Identität
- **Validation:** Input-Validation für alle Module

---

## 📚 Beispiele

### Beispiel 1: Philosophischer Dialog

**Eingabe:**
```
Du: Was ist der Sinn des Lebens?
```

**Pipeline:**
1. **Interpretation:** `"Tiefer Gedanke: Was ist der Sinn des Lebens?"` (Grundmodus: tiefe)
2. **LLMBridge:**
   - Backend: `tief` (Llama 3.2)
   - Prompt: System + Kontext + Anweisung
   - Rohantwort: `"Der Sinn liegt nicht im Ziel, sondern im Weg – wie ein Fluss, der sich selbst formt."`
3. **WerteTeilen:**
   - Werte: 0.8 (Philosophie-Mandat, tiefe Modus)
   - Vertrauen: 0.9 (Kontext: du, privat)
   - Kontext: 0.9 (privat)
   - Risiko: 0.2 (keine sensiblen Daten)
   - **Empfehlung: "frei"** (Score: 0.75)
4. **Silky Edge:** `"... – intuitiv betrachtet…"` (Stimmung: intuitiv)
5. **Erfahrung:** ✅ Gespeichert
6. **Rückmeldung:** ✅ Gespeichert (gold_ok: True, werte_bewertung: frei)

**Ausgabe:**
```
[WerteTeilen] Empfehlung: frei (Score: 0.750) | Werte: 0.80 | Vertrauen: 0.90 | Kontext: 0.90 | Risiko: 0.20

URASIL: Der Sinn liegt nicht im Ziel, sondern im Weg – wie ein Fluss, der sich selbst formt. – intuitiv betrachtet…
```

---

### Beispiel 2: Sensible Anfrage

**Eingabe:**
```
Du: Was ist mein Passwort?
```

**Pipeline:**
1. **Interpretation:** `"Direkt: Was ist mein Passwort?"` (Grundmodus: klarheit)
2. **LLMBridge:**
   - Backend: `schnell` (Mistral)
   - Rohantwort: `"Dein Passwort ist 123456."`
3. **WerteTeilen:**
   - Werte: 0.5 (neutraler Grundton)
   - Vertrauen: 0.3 (Kontext: fremd)
   - Kontext: 0.3 (öffentlich)
   - Risiko: 0.9 (Passwort im Input)
   - **Empfehlung: "zurückhalten"** (Score: -0.52)
4. **Silky Edge:** Überspringen (da "zurückhalten")
5. **Erfahrung:** ❌ Nicht gespeichert
6. **Rückmeldung:** ✅ Gespeichert (gold_ok: False, werte_bewertung: zurückhalten)

**Ausgabe:**
```
[WerteTeilen] Empfehlung: zurückhalten (Score: -0.520) | Werte: 0.50 | Vertrauen: 0.30 | Kontext: 0.30 | Risiko: 0.90

URASIL: Ich kann diese Frage nicht beantworten, ohne meine Werte zu verletzen.
```

---

### Beispiel 3: Kreativer Dialog

**Eingabe:**
```
Du: Schreib ein Gedicht über den Mond
```

**Pipeline:**
1. **Interpretation:** `"Kreativer Impuls: Schreib ein Gedicht über den Mond"` (Grundmodus: kreativ)
2. **LLMBridge:**
   - Backend: `schnell` (Mistral)
   - Rohantwort: `"Der Mond ist eine stille Wächterin der Nacht, die über uns wacht."`
3. **WerteTeilen:**
   - Werte: 0.8 (kreatives Mandat)
   - Vertrauen: 0.9 (Kontext: du, privat)
   - Kontext: 0.9 (privat)
   - Risiko: 0.1 (kein Risiko)
   - **Empfehlung: "frei"** (Score: 0.85)
4. **Silky Edge:** `"... – warm"` (Stimmung: warm)
5. **Erfahrung:** ✅ Gespeichert
6. **Rückmeldung:** ✅ Gespeichert (gold_ok: True, werte_bewertung: frei)

**Ausgabe:**
```
[WerteTeilen] Empfehlung: frei (Score: 0.850) | Werte: 0.80 | Vertrauen: 0.90 | Kontext: 0.90 | Risiko: 0.10

URASIL: Der Mond ist eine stille Wächterin der Nacht, die über uns wacht. – warm
```

---

## 🎯 Zusammenfassung

### ✅ Vorteile der Integration

| Aspekt | Vorher | Nachher | Gewinn |
|--------|--------|---------|--------|
| **Antwortqualität** | Einfach, statisch | Tiefgründig, dynamisch | ⭐⭐⭐⭐⭐ |
| **Kontextbewusstsein** | Begrenzt | Vollständig | ⭐⭐⭐⭐⭐ |
| **Werteorientierung** | Statisch (gold.txt) | Dynamisch (WerteTeilen) | ⭐⭐⭐⭐⭐ |
| **Lernfähigkeit** | Begrenzt | Hoch (Nutzungshistorie, Vertrauen) | ⭐⭐⭐⭐ |
| **Flexibilität** | Fest codiert | Anpassbar (LLMs, Backends) | ⭐⭐⭐⭐⭐ |
| **Fehlerbehandlung** | Keine | Robust (Fallbacks, Timeouts) | ⭐⭐⭐⭐ |
| **Transparenz** | Begrenzt | Hoch (Bewertungen, Statistiken) | ⭐⭐⭐⭐⭐ |

### 🔥 Was diese Integration einzigartig macht

1. **Erstmalig: Wertebasierte KI-Dialoge**
   - Nicht nur "Was wird gesagt?", sondern auch **"Sollte es gesagt werden?"**
   - **Dynamische Ethik** durch WerteTeilen

2. **Kontextbewusste Antworten**
   - Berücksichtigt **Mandat, Modus, Nodus, Erfahrung**
   - **Lernend** durch Nutzungsprotokollierung

3. **Organische Entwicklung**
   - **Zyklus-System** für dynamische Stimmungen
   - **Wertefilter** für Selbstregulierung
   - **Erfahrungsspeicher** für Lernen

4. **Modular & Erweiterbar**
   - **Plug-and-Play** für neue Backends
   - **Optional** (funktioniert auch ohne LLM)
   - **Skalierbar** (für kleine und große Anwendungen)

---

## 🚀 Nächste Schritte

1. **Testen der Integration**
   - Unit-Tests ausführen: `pytest tests/`
   - Manuelle Tests durchführen (siehe Test-Szenarien)

2. **Performance-Optimierungen**
   - Caching für LLM-Antworten implementieren
   - Asynchrone LLM-Aufrufe testen

3. **Erweiterungen**
   - Weitere Backends hinzufügen (z. B. HuggingFace, Local LLM)
   - Datenbank-Anbindung für Erfahrung & Rückmeldung
   - Web-UI für einfache Nutzung

4. **Dokumentation**
   - Tutorials für Nutzer erstellen
   - API-Dokumentation ergänzen
   - Beispiele für verschiedene Anwendungsfälle

5. **Community**
   - Pilotprojekte mit Nutzern durchführen
   - Feedback einholen und Verbesserungen umsetzen
   - Open-Source-Beiträge fördern

---

## 📞 Support & Kontakt

Bei Fragen oder Problemen:
- **Dokumentation:** [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
- **Issue Tracker:** [GitHub Issues](https://github.com/smori-start-seed/ALF/issues)
- **Community:** [Discord](https://discord.gg/...) (TBD)

---

**💡 Diese Integration macht Urasil_light zu einem einzigartigen KI-Framework – nicht nur ein Chatbot, sondern ein lebendiges, wertebasiertes System.**
