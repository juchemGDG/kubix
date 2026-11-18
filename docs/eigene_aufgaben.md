# Eigene Aufgaben erstellen

Diese Anleitung zeigt zwei Wege:

1. **Eine Aufgabe in die Aufgabensammlung aufnehmen.** Sie erscheint dann bei
   `aufgabe(nr)`, in `python -m kubix liste` und in Koalino unter
   *Python → kubix-Aufgaben*, und `pruefe()` prüft sie automatisch.
   Dafür ändert man den Quelltext von kubix (Datei `kubix/aufgaben.py`).
2. **Eine Übung für die eigene Klasse ohne Änderung an kubix** – eine einzelne
   Python-Datei, die die Welt aufbaut und das Ergebnis selbst prüft.

---

## Weg 1: Aufgabe in die Sammlung aufnehmen

Jede Aufgabe besteht aus drei Teilen in `kubix/aufgaben.py`:

| Teil | Wozu |
|---|---|
| **Aufbau-Funktion** | baut die Welt und gibt die Figur zurück |
| **Ziel-Prüfung** | sagt, ob die Aufgabe gelöst ist |
| **Eintrag in `AUFGABEN`** | Titel, Auftragstext, Musterlösung, Tipps … |

### Schritt 1: Die Welt aufbauen

Schreibe eine Funktion ohne Parameter, die eine `Welt` erzeugt, sie gestaltet
und eine `Figur` zurückgibt. Üblich ist der Name `_a<Nummer>`:

```python
# 9  Das Floß
def _a9():
    w = Welt(8, 3)                      # 8 Felder breit, 3 tief
    for y in range(3):
        w._spalten[4][y] = ["wasser"]   # ein Fluss quer durch die Welt
    w.stapel(2, 1, "holz")              # ein Holzblock zum Schieben
    _gold(w, 6, 1)                      # goldenes Zielfeld
    return Figur(w, 0, 1, "osten")      # Startfeld und Blickrichtung
```

Hilfsmittel zum Gestalten:

| Aufruf | Wirkung |
|---|---|
| `Welt(breite, tiefe, max_hoehe=6)` | neue Welt, alles Gras, Höhe 1 |
| `w.stapel(x, y, material, anzahl)` | Blöcke oben auf ein Feld setzen |
| `w.fuelle(material)` | Boden der ganzen Welt ersetzen |
| `_gold(w, x, y)` | Boden eines Feldes golden machen (Zielfeld) |
| `w._spalten[x][y] = ["wasser"]` | ein Feld komplett festlegen (unterster Eintrag = Boden) |
| `Figur(w, x, y, richtung)` | Figur aufstellen; `richtung`: `"norden"`, `"osten"`, `"sueden"`, `"westen"` |

Koordinaten: `x` läuft von 0 bis `breite − 1`, `y` von 0 bis `tiefe − 1`.
`osten` heißt „x wird größer“, `sueden` heißt „y wird größer“.
Ein Feld mit Höhe 1 ist nur Boden; jede Stufe mehr ist ein Block. Kubi kann
eine Stufe hinauf- oder hinuntergehen, aber nicht über Wasser laufen.

> **Tipp:** Wenn Türme höher als 5 Blöcke werden sollen, `max_hoehe` in
> `Welt(...)` größer setzen.

### Schritt 2: Das Ziel prüfen

Die Prüfung ist eine Funktion, die die Figur bekommt und

- `None` zurückgibt, wenn die Aufgabe **gelöst** ist,
- sonst einen **Hinweis in einfacher Sprache** (ein String), der den
  Schülerinnen und Schülern angezeigt wird.

Für „Kubi soll auf Feld (x|y) stehen“ gibt es schon `_steht_auf`:

```python
lambda f: _steht_auf(f, 6, 1)
```

Für alles andere schreibt man eine eigene Funktion `_z<Nummer>`. Nützlich sind:

| Abfrage | Bedeutung |
|---|---|
| `f.x`, `f.y`, `f.blickrichtung` | wo Kubi steht und wohin Kubi schaut |
| `f.welt.hoehe(x, y)` | Höhe eines Feldes (1 = nur Boden) |
| `f.welt.material(x, y)` | Material des obersten Blocks |
| `f._gesagt` | Liste aller Texte, die Kubi mit `sage()` gesagt hat |

Beispiel: Kubi soll einen Holzblock genau auf Feld (5|2) schieben.

```python
def _z10(figur):
    w = figur.welt
    if w.material(5, 2) != "holz":
        return "Auf Feld (5|2) soll der Holzblock liegen."
    return None
```

Hinweise, die gut funktionieren:

- Sag, **was** nicht stimmt, nicht nur „falsch“: „Kubi steht auf (3|1), das
  Ziel ist (6|1).“
- Prüfe vom Wichtigsten zum Kleinsten – die erste Meldung soll weiterhelfen.
- Verrate nicht die Lösung.

### Schritt 3: Den Eintrag in `AUFGABEN` ergänzen

Hänge am Ende der Liste `AUFGABEN` einen neuen Eintrag an:

```python
    Aufgabe(
        9, "floss", "Das Floß", "Schleife mit Schieben",
        # Auftrag (Markdown):
        "Ein Fluss versperrt den Weg zum **goldenen Feld**. Kubi kann nicht bauen – "
        "aber einen Holzblock schieben: `figur.schiebe()`.\n\n"
        "Holz schwimmt! Schiebe den Block ins Wasser und benutze ihn als Floß.",
        # Musterlösung (ohne die Zeilen mit import, aufgabe() und pruefe()):
        "figur.gehe()\nfor i in range(2):\n    figur.schiebe()\n    figur.gehe()\n"
        "figur.gehe(3)\n",
        _a9, lambda f: _steht_auf(f, 6, 1),
        verlangt=("schleife",),
        tipps=("Nach dem Schieben steht Kubi noch an derselben Stelle – erst danach gehen.",),
    ),
```

Die Felder der Reihe nach:

| Feld | Bedeutung | Regeln |
|---|---|---|
| `nr` | Nummer der Aufgabe | fortlaufend (nach 8 kommt 9), keine Lücken – die Fehlermeldung „Es gibt die Aufgaben 1 bis N“ setzt das voraus |
| `schluessel` | Kurzname für Dateinamen, z. B. `Aufgabe_09_floss.py` | nur Kleinbuchstaben, Ziffern, `_`; **keine Umlaute, kein ß** |
| `titel` | Überschrift | kurz |
| `konzept` | welcher Programmier-Baustein geübt wird | wird in Liste und Arbeitsblatt angezeigt |
| `text` | Auftrag in Markdown | Codebeispiele mit ` ```python `; Zeilenumbrüche als `\n\n` |
| `loesung` | Musterlösung | nur der Teil zwischen `figur = aufgabe(n)` und `pruefe()`; darf nur `figur` benutzen |
| `aufbau` | Funktion aus Schritt 1 | |
| `ziel` | Funktion aus Schritt 2 | |
| `verlangt` | Bausteine, die im Programm vorkommen müssen | Auswahl aus `"schleife"`, `"bedingung"`, `"funktion"`; leer lassen = beliebig |
| `tipps` | Tipps fürs Arbeitsblatt | `pruefe()` zeigt bei einem Fehlversuch den **ersten** Tipp |

`verlangt` prüft den Quelltext der Schülerdatei: Wer z. B. bei
`verlangt=("schleife",)` das Ziel ohne `for`/`while` erreicht, bekommt
„Dein Programm soll eine Schleife (for oder while) benutzen.“

### Schritt 4: Testen

Die Tests probieren **jede** Aufgabe automatisch aus: Die Musterlösung muss die
Aufgabe lösen, ein leeres Programm darf sie nicht lösen. Neue Aufgaben sind
damit ohne weiteren Testcode abgedeckt.

```
python -m pytest
```

Dann von Hand anschauen – mit Fenster:

```python
from kubix import aufgabe, pruefe

figur = aufgabe(9)
figur.gehe()
# …
pruefe()
```

und das Arbeitsblatt erzeugen (mit Lösung für Lehrkräfte):

```
python -m kubix export 9 ./test_export --loesung
```

Das schreibt `Aufgabe_09_floss.py` (Vorlage) und `Aufgabe_09_floss.md`
(Arbeitsblatt). Eine schon vorhandene `.py`-Datei wird nie überschrieben –
zum erneuten Testen also vorher löschen.

### Schritt 5: Verteilen

Wenn die Änderung auf GitHub (`main`) liegt, erscheint die Aufgabe nach einem
Update von kubix (siehe README, *Aktualisieren*) in Koalino und bei
`aufgabe(9)`. Es lohnt sich, dabei die Versionsnummer in `pyproject.toml` und
`kubix/__init__.py` zu erhöhen, damit man sieht, welcher Stand installiert ist
(`import kubix; print(kubix.__version__)`).

---

## Weg 2: Eigene Übung ohne Änderung an kubix

Für eine schnelle Übung in der eigenen Klasse genügt eine Datei, die die Welt
aufbaut. Die Schülerinnen und Schüler schreiben ihr Programm darunter, die
Prüfung am Ende ist gewöhnliches Python.

```python
from kubix import Welt, Figur

# ---- Aufbau (nicht verändern) ----
welt = Welt(8, 3)
welt.stapel(2, 1, "holz")
welt.stapel(6, 1, "gold")      # goldener Zielblock (eine Stufe hoch)
figur = Figur(welt, 0, 1, "osten")

# ---- Dein Programm ----



# ---- Prüfung ----
if (figur.x, figur.y) == (6, 1):
    figur.sage("Geschafft!")
else:
    figur.sage("Noch nicht ganz …")
```

Vorteile: keine Änderung an kubix, sofort einsetzbar.
Nachteile: keine Liste in Koalino, kein Arbeitsblatt-Export, keine Prüfung auf
Schleife/Bedingung/Funktion. Wenn sich eine solche Übung bewährt, lässt sie sich
später nach Weg 1 in die Sammlung übernehmen.

---

## Befehle, die Kubi kennt (zum Planen von Aufgaben)

| Befehl | Wirkung |
|---|---|
| `gehe(n)` | n Felder vorwärts (eine Stufe rauf/runter erlaubt, kein Wasser) |
| `drehe_links()`, `drehe_rechts()` | Drehung um 90° |
| `baue(material)` | Block auf das Feld vor Kubi |
| `baue_ab()` | obersten Block vor Kubi entfernen (der Boden bleibt) |
| `schiebe()` | einen einzelnen Holzblock vor Kubi ein Feld weiterschieben; Kubi bleibt stehen |
| `sage(text)` | Sprechblase (wird in `_gesagt` gemerkt) |
| `vorne_frei()`, `hoehe_vorne()`, `hoehe_hier()`, `material_vorne()` | Abfragen für `if` und `while` |

Regeln für `schiebe()`: Vor Kubi muss **genau ein** Block auf dem Boden liegen,
und zwar aus **Holz**. Kubi muss auf Bodenhöhe stehen, und hinter dem Block muss
ein freies Feld (nur Boden, keine Figur) innerhalb der Welt sein. Auf Wasser
geschoben wird der Block zu einem Floß, über das Kubi gehen kann.
