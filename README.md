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

## Installation und Aktualisierung

Siehe [Installation in Koalino und Thonny](#installation-in-koalino-und-thonny) weiter unten.
Kurz: kubix wird direkt von GitHub installiert (es ist nicht auf PyPI):

```
pip install --upgrade https://github.com/juchemGDG/kubix/archive/refs/heads/main.zip
```

## Befehle (Stand 0.3)

| Befehl | Wirkung |
|---|---|
| `Welt(breite, tiefe)` | Erzeugt die Welt (Standard 10×10) |
| `Figur(welt)` / `Figur()` | Erzeugt die Figur (ohne Angabe: in der zuletzt erzeugten Welt) |
| `gehe(n)` | n Felder nach vorne; eine Stufe hinauf/hinunter ist erlaubt |
| `drehe_links()`, `drehe_rechts()` | Drehung um 90° |
| `baue(material)` | Block auf das Feld vor der Figur |
| `baue_ab()` | Obersten Block vor der Figur wegnehmen |
| `schiebe()` | Einen einzelnen Holzblock vor der Figur ein Feld weiterschieben (die Figur bleibt stehen) |
| `sage(text, sekunden)` | Sprechblase |
| `vorne_frei()`, `hoehe_vorne()`, `material_vorne()` | Abfragen für Verzweigungen und Schleifen |
| `welt.stapel(x, y, material, anzahl)` | Welt gestalten |
| `welt.fuelle(material)` | Boden der ganzen Welt setzen |
| `welt.screenshot("bild.png")` | Bild speichern (geht auch ohne Fenster) |

`schiebe()` meldet einen Fehler, wenn vor der Figur kein Block oder mehr als ein
Block liegt, wenn der Block nicht aus Holz ist oder wenn dahinter kein Platz ist.
Holz schwimmt: Auf Wasser geschoben wird es zu einem Floß.

Materialien: gras, erde, stein, sand, holz, ziegel, schnee, gold, wasser.
Blickrichtungen: norden (rechts oben), osten (rechts unten), sueden (links unten),
westen (links oben).

Fehlermeldungen sind in einfacher Sprache, Tippfehler bekommen einen Vorschlag
(„Meintest du „gehe"?“).

## Ohne Fenster / Tests

`KUBIX_FENSTER=0` oder `Welt(fenster=False)` rechnet ohne Fenster (z. B. für
Bildschirmfotos oder automatische Prüfung von Schüleraufgaben).

## Eigene Aufgaben

Wie man neue Aufgaben für `aufgabe(nr)` / `pruefe()` schreibt, steht in
[docs/eigene_aufgaben.md](docs/eigene_aufgaben.md).

## Installation in Koalino und Thonny

kubix liegt auf GitHub, nicht auf PyPI. Installation und Aktualisierung sind
derselbe Befehl – er holt immer den neuesten Stand von `main`. Wichtig ist nur,
dass kubix in **das Python** kommt, mit dem der Editor die Programme startet.
Am sichersten geht das mit diesem kleinen Programm, das man im Editor selbst
ausführt (gleich für Windows, macOS und Linux):

```python
# kubix installieren oder aktualisieren: einfach ausführen
import subprocess, sys

URL = "https://github.com/juchemGDG/kubix/archive/refs/heads/main.zip"
befehl = [sys.executable, "-m", "pip", "install", "--upgrade", URL]
if sys.prefix == sys.base_prefix:      # keine virtuelle Umgebung → ins Benutzerverzeichnis
    befehl.insert(4, "--user")
if subprocess.run(befehl).returncode == 0:
    # In einem frischen Python nachsehen: Das laufende Python findet ein eben
    # erst installiertes Paket manchmal noch nicht (bis zum Neustart).
    subprocess.run([sys.executable, "-c",
                    "import kubix; print('✓ kubix', kubix.__version__, 'ist installiert.')"])
else:
    print("✗ Die Installation hat nicht geklappt – siehe „Wenn es nicht klappt“ in der README.")
```

Danach prüfen, welche Version läuft: `import kubix; print(kubix.__version__)`.

### Koalino (Windows, macOS, Linux)

- **Erstinstallation:** In den fertigen Koalino-Downloads ist kubix schon
  enthalten (Menü *Python → kubix-Aufgaben*). Fehlt es – z. B. weil in den
  Einstellungen ein anderes Python gewählt ist –, das Programm oben in Koalino
  in eine neue Datei kopieren und mit ▶ ausführen.
- **Aktualisieren:** Dasselbe Programm erneut ausführen. Es installiert in das
  Python, das unter *Einstellungen → Python-Interpreter* gewählt ist.

### Thonny (Windows, macOS, Linux)

- **Mit dem Programm oben:** in Thonny in eine neue Datei kopieren, ▶ drücken.
  Danach *Ausführen → Backend stoppen/neu starten* (Strg+F2 bzw. ⌘F2), damit
  Thonny die neue Fassung lädt. Zum Aktualisieren genauso.
- **Oder über die Kommandozeile von Thonny:** *Extras → Systemkommandozeile
  öffnen …* und dort eingeben:

  ```
  pip install --upgrade https://github.com/juchemGDG/kubix/archive/refs/heads/main.zip
  ```

  Diese Kommandozeile benutzt automatisch das Python von Thonny.
- **Ohne Kommandozeile:** auf GitHub *Code → Download ZIP* wählen, dann in
  Thonny *Extras → Pakete verwalten …* und dort über den Link zum Installieren
  aus einer lokalen Datei die heruntergeladene ZIP-Datei auswählen. Für ein
  Update eine neue ZIP-Datei herunterladen und genauso installieren.

### Wenn es nicht klappt

| Meldung | Lösung |
|---|---|
| `No module named 'kubix'` | kubix ist in einem anderen Python installiert als dem, das der Editor benutzt. Das Programm oben **im Editor** ausführen. |
| `externally-managed-environment` (vor allem Linux) | Das System-Python darf nicht verändert werden. In Thonny unter *Extras → Optionen → Interpreter* Thonnys eigenes Python oder eine virtuelle Umgebung wählen; in Koalino die mitgelieferte Runtime wählen. |
| `Failed to build pygame` | Eine alte kubix-Fassung (vor 0.3.1) wollte unter Python 3.14 pygame selbst kompilieren. Das Programm oben erneut ausführen: Ab 0.3.1 wird dort automatisch **pygame-ce** installiert (gleiche Befehle, `import pygame` funktioniert genauso). |
| Alte Befehle trotz Update (Thonny) | Backend neu starten (Strg+F2 / ⌘F2). |
| Fehler beim Herunterladen | Internetverbindung bzw. Schul-Proxy prüfen; GitHub muss erreichbar sein. |

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
