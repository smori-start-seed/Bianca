# Architektur von Urasil_light

Urasil_light ist ein modular aufgebautes KI‑Kernsystem, das zyklische Zustände,
Werteorientierung und reifeabhängiges Lernen kombiniert. Die Architektur ist
bewusst leichtgewichtig gehalten, aber intern klar strukturiert und stark
entkoppelt.

Dieses Dokument beschreibt die wichtigsten Module, ihre Aufgaben und die
Interaktionen zwischen ihnen.

---

## 🧱 Grundprinzip

Urasil_light folgt einem Pipeline‑Ansatz:

1. Zyklus bestimmt den inneren Zustand
2. Interpretation erzeugt Bedeutung
3. Seed erzeugt die Rohantwort
4. Silky Edge veredelt den Stil
5. Reflexion bewertet die Antwort
6. Erfahrung speichert reife Inhalte
7. Identität hält alles persistent

Jedes Modul ist klein, fokussiert und austauschbar.

---

## 📁 Modulübersicht

### 1. `zyklus.py`
Steuert den inneren Zustand des Systems:
- Sonne → Stimmung (klar, kreativ, resonant, tief)
- Mond → Stil (warm, neutral, intuitiv)
- Tag → Fokus (fokus, variation, synthese)

Der Zyklus beeinflusst Interpretation, Seed und Silky Edge.

---

### 2. `interpretation.py`
Erzeugt aus dem Nutzereingang eine Bedeutung.
Der Modus hängt von der Sonne ab:
- klar → direkte Bedeutung
- kreativ → freiere Assoziation
- resonant → emotionale Bedeutung
- tief → introspektive Bedeutung

---

### 3. `seed.py`
Erzeugt die Rohantwort basierend auf:
- Bedeutung
- Tag‑Fokus (fokus, variation, synthese)
- Reflexionssignal (Selbstkorrektur)
- gold‑Werten (indirekt)

Seed ist der „Kern“ der Antwort.

---

### 4. `silky_edge.py`
Veredelt die Rohantwort stilistisch.
Der Stil hängt vom Mond ab:
- warm
- neutral
- intuitiv

Silky Edge ist die „Oberfläche“ der Antwort.

---

### 5. `rueckmeldung.py`
Bewertet jede Antwort:
- war sie gold‑konform?
- in welchem Zyklus wurde sie erzeugt?

Speichert Reflexionen in der Identität und erzeugt ein
Selbstkorrektur‑Signal für Seed.

---

### 6. `erfahrung.py`
Speichert nur reife Erfahrungen.
Reife wird über `ininity.txt` definiert.

Unreife Inhalte werden verworfen, um die Identität sauber zu halten.

---

### 7. `mandate.py`
Lädt die Idealwerte aus `gold.txt`:
- Klarheit
- Integrität
- Resonanz
- Tiefe
- Harmonie

Diese Werte beeinflussen Seed und Reflexion.

---

### 8. `ininity.py`
Reife‑Filter:
- lädt Kriterien aus `ininity.txt`
- prüft, ob ein Text reif genug ist, um gespeichert zu werden

Schützt das System vor „Identitätsmüll“.

---

### 9. `identity.py`
Persistente Speicherung aller Zustände:
- Zyklus
- Reflexion
- Erfahrung
- Metadaten

Wird bei jedem Lauf geladen und gespeichert.

---

### 10. `runtime/main.py`
Einstiegspunkt des Systems.
Steuert:
- Einlesen des Nutzereingangs
- Ausführen der Pipeline
- Speichern der Identität

---

## 🔄 Datenfluss

User Input
↓
Interpretation
↓
Seed (Rohantwort)
↓
Silky Edge (Stil)
↓
Reflexion (Bewertung)
↓
Erfahrung (Reifes Lernen)
↓
Identität (Persistenz)


---

## 🎯 Designziele

- **Modularität**  
  Jedes Modul ist klein und austauschbar.

- **Organisches Verhalten**  
  Antworten hängen vom inneren Zustand ab.

- **Werteorientierung**  
  gold.txt definiert Idealverhalten.

- **Reifes Lernen**  
  Nur wertvolle Erfahrungen prägen die Identität.

- **Transparenz**  
  Architektur ist klar dokumentiert und leicht erweiterbar.

---

## 🧩 Erweiterbarkeit

Die Architektur erlaubt einfache Erweiterungen:
- Charakter‑Module
- Memory‑Compression
- Agent‑Interfaces
- Web‑UI
- Debug‑Tools
- neue Zyklus‑Modelle

Urasil_light ist bewusst offen gehalten, um kreative Experimente zu ermöglichen.

