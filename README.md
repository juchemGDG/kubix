# kubix

Programmieren lernen mit einer Figur in einer Würfelwelt – gedacht für den Umstieg
von Scratch/Snap auf Python (Klasse 8). Ähnlich wie `turtle`: Man schreibt Befehle
von oben nach unten, das Fenster zeigt, was passiert. Alle Befehle und
Fehlermeldungen sind deutsch.

```python
from kubix import Figur

figur = Figur()
figur.gehe(3)
figur.drehe_rechts()
figur.baue("stein")
figur.sage("Fertig!")
```

## Installation

```
pip install kubix
```

(In Koalino: *Python → Pakete installieren (pip)*.)

## Befehle (Stand 0.1)

| Befehl | Wirkung |
|---|---|
| `Welt(breite, tiefe)` | Erzeugt die Welt (Standard 10×10) |
| `Figur(welt)` / `Figur()` | Erzeugt die Figur (ohne Angabe: in der zuletzt erzeugten Welt) |
| `gehe(n)` | n Felder nach vorne; eine Stufe hinauf/hinunter ist erlaubt |
| `drehe_links()`, `drehe_rechts()` | Drehung um 90° |
| `baue(material)` | Block auf das Feld vor der Figur |
| `baue_ab()` | Obersten Block vor der Figur wegnehmen |
| `sage(text, sekunden)` | Sprechblase |
| `vorne_frei()`, `hoehe_vorne()`, `material_vorne()` | Abfragen für Verzweigungen und Schleifen |
| `welt.stapel(x, y, material, anzahl)` | Welt gestalten |
| `welt.fuelle(material)` | Boden der ganzen Welt setzen |
| `welt.screenshot("bild.png")` | Bild speichern (geht auch ohne Fenster) |

Materialien: gras, erde, stein, sand, holz, ziegel, schnee, gold, wasser.
Blickrichtungen: norden (rechts oben), osten (rechts unten), sueden (links unten),
westen (links oben).

Fehlermeldungen sind in einfacher Sprache, Tippfehler bekommen einen Vorschlag
(„Meintest du „gehe"?“).

## Ohne Fenster / Tests

`KUBIX_FENSTER=0` oder `Welt(fenster=False)` rechnet ohne Fenster (z. B. für
Bildschirmfotos oder automatische Prüfung von Schüleraufgaben).

## Urheberrecht

Alle Grafiken werden zur Laufzeit vom Code selbst erzeugt (Farben, Rauschen,
Kanten) – es gibt keine Fremd-Texturen, -Figuren oder -Sounds. Die Würfelwelt-
Optik ist ein eigenes, einfaches Design. Lizenz: MIT.

## Entwicklung

```
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest
```

## Geplant

Tasten und Maus (`bei_taste`), Arena mit Gegnern/Punkten/Kollision, Aufgabensammlung
mit Lösungsprüfung, Blockly-Blöcke für den Koalino-Block-Editor.
