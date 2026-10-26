# Antwort-Pipeline von Urasil_light

Die Antwort-Pipeline ist das zentrale Prozessmodell von Urasil_light.
Jede Antwort durchläuft mehrere klar getrennte Stufen, die jeweils
einen eigenen Zweck erfüllen.

Die Pipeline ist bewusst modular aufgebaut, sodass jede Stufe
unabhängig erweitert oder ersetzt werden kann.

---

# 🔄 Übersicht

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

## 1. Interpretation

**Modul:** `interpretation.py`  
**Beeinflusst durch:** Sonne (klar, kreativ, resonant, tief)

Die Interpretation erzeugt aus dem Nutzereingang eine Bedeutung.
Sie entscheidet, *wie* der Input verstanden wird:

- klar → direkt, nüchtern  
- kreativ → frei, assoziativ  
- resonant → emotional  
- tief → introspektiv  

Die Interpretation ist der erste Schritt, der den Zyklus nutzt.

---

## 2. Seed (Rohantwort)

**Modul:** `seed.py`  
**Beeinflusst durch:** Tag (fokus, variation, synthese), Reflexion

Seed erzeugt die strukturelle Rohantwort:

- fokus → direkt, kurz  
- variation → alternative Sicht  
- synthese → verbindend  

Zusätzlich reagiert Seed auf das Reflexionssignal:

- wenn letzte Antwort nicht gold‑konform → „Klarer:“  
- sonst → normaler Zyklusmodus  

Seed ist der „Kern“ der Antwort.

---

## 3. Silky Edge (Stil)

**Modul:** `silky_edge.py`  
**Beeinflusst durch:** Mond (warm, neutral, intuitiv)

Silky Edge veredelt die Rohantwort stilistisch:

- warm → weich, menschlich  
- neutral → sachlich  
- intuitiv → fließend  

Silky Edge ist die „Oberfläche“ der Antwort.

---

## 4. Reflexion

**Modul:** `rueckmeldung.py`  
**Beeinflusst durch:** gold.txt, Zyklus

Reflexion bewertet die erzeugte Antwort:

- war sie gold‑konform?  
- in welchem Zyklus wurde sie erzeugt?  

Sie speichert:

- Antwort  
- Zykluszustand  
- gold‑Bewertung  

Und erzeugt ein Selbstkorrektur‑Signal für Seed.

---

## 5. Erfahrung (Reifes Lernen)

**Modul:** `erfahrung.py`  
**Beeinflusst durch:** ininity.txt

Erfahrung speichert nur reife Inhalte:

- klar  
- kohärent  
- wertvoll  
- respektvoll  
- wahrhaftig  

Unreife Inhalte werden verworfen, um die Identität sauber zu halten.

---

## 6. Identität (Persistenz)

**Modul:** `identity.py`

Die Identität speichert:

- Zyklusverlauf  
- Reflexionen  
- Erfahrungen  
- Metadaten  

Sie wird bei jedem Lauf geladen und gespeichert.

---

# 🎯 Ziel der Pipeline

Die Pipeline macht Urasil_light:

- organisch  
- dynamisch  
- wertorientiert  
- selbstkorrigierend  
- lernfähig  
- nicht-deterministisch  

Jede Antwort ist das Ergebnis eines **inneren Prozesses**, nicht nur einer Funktion.

