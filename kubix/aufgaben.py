"""Aufgabensammlung: kleine Rätsel, bei denen Kubi mit Programmen gesteuert wird.

Für Schülerinnen und Schüler sieht eine Aufgabe so aus::

    from kubix import *

    figur = aufgabe(1)      # baut die Welt für Aufgabe 1 auf und zeigt den Auftrag

    figur.gehe(4)

    pruefe()                # sagt, ob die Aufgabe gelöst ist

Die Aufgaben folgen den Grundbausteinen des Programmierens: Reihenfolge,
Schleife, Bedingung, Variable, Funktion.
"""
import ast
import json
import os
import sys
from dataclasses import dataclass
from typing import Callable, Optional

from .fehler import KubixFehler
from .figur import Figur
from .welt import Welt

# Wofür „verlangt“ steht: Welche Bausteine das Programm enthalten muss.
_BAUSTEINE = {
    "schleife": ((ast.For, ast.While), "eine Schleife (for oder while)"),
    "bedingung": ((ast.If, ast.While), "eine Bedingung (if oder while)"),
    "funktion": ((ast.FunctionDef,), "eine eigene Funktion (def)"),
}


@dataclass
class Aufgabe:
    nr: int
    schluessel: str
    titel: str
    konzept: str
    text: str                              # Auftrag in Markdown
    loesung: str                           # Musterlösung (Code, nach „figur = aufgabe(n)“)
    aufbau: Callable[[], Figur]            # baut Welt und Figur
    ziel: Callable[[Figur], Optional[str]]  # None = gelöst, sonst Hinweis
    verlangt: tuple = ()
    tipps: tuple = ()

    @property
    def dateiname(self):
        return f"Aufgabe_{self.nr:02d}_{self.schluessel}"

    def vorlage(self):
        return (
            "from kubix import *\n\n"
            f"figur = aufgabe({self.nr})\n\n"
            "# Dein Programm:\n\n\n"
            "pruefe()\n"
        )


def _gold(welt, x, y):
    welt._spalten[x][y] = ["gold"]


def _steht_auf(figur, x, y):
    if (figur.x, figur.y) == (x, y):
        return None
    return (f"Kubi steht auf Feld ({figur.x}|{figur.y}). "
            f"Das Ziel ist das goldene Feld ({x}|{y}).")


# ---------------------------------------------------------------------------
# 1  Erste Schritte
def _a1():
    w = Welt(8, 4)
    _gold(w, 4, 0)
    return Figur(w, 0, 0, "osten")


# 2  Um die Ecke
def _a2():
    w = Welt(8, 6)
    _gold(w, 4, 3)
    return Figur(w, 0, 0, "osten")


# 3  Zickzack
def _a3():
    w = Welt(8, 8)
    _gold(w, 6, 6)
    return Figur(w, 0, 0, "osten")


# 4  Brücke
def _a4():
    w = Welt(10, 5)
    for x in (3, 4, 5):
        for y in range(5):
            w._spalten[x][y] = ["wasser"]
    _gold(w, 8, 2)
    return Figur(w, 0, 2, "osten")


# 5  Treppe
def _a5():
    w = Welt(8, 5, max_hoehe=8)
    w._spalten[4][2] = ["gras", "stein", "stein", "stein", "gold"]
    return Figur(w, 0, 2, "osten")


# 6  Hindernisse
def _a6():
    w = Welt(10, 3, max_hoehe=8)
    for x, h in ((2, 3), (5, 4), (6, 2)):
        w.stapel(x, 1, "stein", h - 1)
    _gold(w, 8, 1)
    return Figur(w, 0, 1, "osten")


# 7  Stufen zählen
def _a7():
    w = Welt(10, 3, max_hoehe=9)
    for x in range(1, 8):
        w.stapel(x, 1, "stein", x)    # Höhe 2, 3, …, 8
    return Figur(w, 0, 1, "osten")


def _z7(figur):
    if (figur.x, figur.y) != (7, 1):
        return "Kubi soll die Treppe bis ganz nach oben steigen."
    if not figur._gesagt:
        return "Kubi soll am Ende die Anzahl der Stufen sagen (mit sage)."
    if figur._gesagt[-1].strip() != "7":
        return (f"Kubi hat „{figur._gesagt[-1]}“ gesagt. "
                "Zähle noch einmal genau: Wie viele Stufen hat die Treppe?")
    return None


# 8  Türme
def _a8():
    w = Welt(10, 4)
    return Figur(w, 0, 0, "sueden")


def _z8(figur):
    w = figur.welt
    for x in (0, 2, 4, 6):
        if w.hoehe(x, 1) != 4:
            return (f"Auf Feld ({x}|1) soll ein Turm aus 3 Blöcken stehen "
                    f"(Gesamthöhe 4), dort sind es {w.hoehe(x, 1) - 1}.")
        if w.material(x, 1) != "ziegel":
            return f"Der Turm auf ({x}|1) soll aus Ziegel („ziegel“) sein."
    for x in (1, 3, 5, 7):
        if w.hoehe(x, 1) != 1:
            return f"Zwischen den Türmen darf nichts stehen – Feld ({x}|1) ist bebaut."
    return None


AUFGABEN = [
    Aufgabe(
        1, "erste_schritte", "Erste Schritte", "Reihenfolge von Befehlen",
        "Kubi steht am linken Rand. Bring Kubi auf das **goldene Feld**.\n\n"
        "Mit `figur.gehe(3)` geht Kubi drei Felder nach vorne.",
        "figur.gehe(4)\n", _a1, lambda f: _steht_auf(f, 4, 0),
        tipps=("Zähle die Felder bis zum goldenen Feld.",),
    ),
    Aufgabe(
        2, "um_die_ecke", "Um die Ecke", "Reihenfolge von Befehlen",
        "Das goldene Feld liegt nicht mehr geradeaus. Kubi muss sich drehen: "
        "`figur.drehe_rechts()` und `figur.drehe_links()`.\n\n"
        "Die Reihenfolge deiner Befehle ist wichtig – Kubi führt sie von oben nach unten aus.",
        "figur.gehe(4)\nfigur.drehe_rechts()\nfigur.gehe(3)\n", _a2, lambda f: _steht_auf(f, 4, 3),
        tipps=("Nach `drehe_rechts()` schaut Kubi in Richtung „süden“ (links unten).",),
    ),
    Aufgabe(
        3, "zickzack", "Zickzack", "Schleife (for)",
        "Kubi soll im Zickzack zum **goldenen Feld** in der Ecke: "
        "ein Schritt, rechts, ein Schritt, links – und das immer wieder.\n\n"
        "Du könntest die vier Befehle sechsmal untereinander schreiben. "
        "Besser: Lass Python wiederholen!\n\n"
        "```python\nfor i in range(6):\n    figur.gehe()\n```\n\n"
        "Alles, was **eingerückt** unter dem `for` steht, wird wiederholt.",
        "for i in range(6):\n    figur.gehe()\n    figur.drehe_rechts()\n"
        "    figur.gehe()\n    figur.drehe_links()\n",
        _a3, lambda f: _steht_auf(f, 6, 6), verlangt=("schleife",),
        tipps=("Die Einrückung (4 Leerzeichen oder Tab) zeigt, was zur Schleife gehört.",),
    ),
    Aufgabe(
        4, "bruecke", "Die Brücke", "Schleife mit Bauen",
        "Ein Fluss versperrt den Weg. In **Wasser** kann Kubi nicht gehen – "
        "aber Kubi kann bauen: `figur.baue(\"holz\")` setzt einen Block auf das Feld vor sich.\n\n"
        "Baue eine Brücke über den Fluss und gehe zum **goldenen Feld**. "
        "Benutze eine Schleife, statt alles mehrfach hinzuschreiben.",
        "figur.gehe(2)\nfor i in range(3):\n    figur.baue(\"holz\")\n    figur.gehe()\n"
        "figur.gehe(3)\n",
        _a4, lambda f: _steht_auf(f, 8, 2), verlangt=("schleife",),
        tipps=("Erst bauen, dann gehen – sonst steht Kubi vor dem Wasser.",
               "Wie breit ist der Fluss? Zähle die blauen Felder."),
    ),
    Aufgabe(
        5, "treppe", "Die Treppe", "Schleife mit Zähler",
        "Auf dem **goldenen Feld** ist eine Plattform, 5 Blöcke hoch. Kubi kann immer nur "
        "**eine Stufe** auf einmal steigen. Baue eine Treppe: "
        "Stufe 1 ist 1 Block hoch, Stufe 2 ist 2 Blöcke hoch, Stufe 3 ist 3 Blöcke hoch.\n\n"
        "Die Schleifenvariable zählt dir die Stufen:\n\n"
        "```python\nfor hoehe in range(1, 4):\n    print(hoehe)   # 1, 2, 3\n```\n\n"
        "Du kannst `hoehe` auch als Anzahl für eine zweite Schleife nutzen.",
        "for hoehe in range(1, 4):\n    for i in range(hoehe):\n        figur.baue(\"stein\")\n"
        "    figur.gehe()\nfigur.gehe()\n",
        _a5, lambda f: _steht_auf(f, 4, 2), verlangt=("schleife",),
        tipps=("Eine Schleife in einer Schleife ist erlaubt.",
               "Zum Schluss ist die Plattform nur noch eine Stufe höher."),
    ),
    Aufgabe(
        6, "hindernisse", "Hindernisse", "Bedingung (if / while)",
        "Auf dem Weg zum **goldenen Feld** stehen Mauern aus Stein. Kubi darf nicht "
        "wissen, wo sie stehen – das Programm soll **selbst entscheiden**:\n\n"
        "```python\nif figur.vorne_frei():\n    figur.gehe()\nelse:\n    figur.baue_ab()\n```\n\n"
        "`vorne_frei()` ist `True`, wenn Kubi gehen kann. `baue_ab()` nimmt einen Block weg.\n\n"
        "**Knobelaufgabe:** Manche Mauern sind höher als einen Block. "
        "Mit `while` kannst du so lange abbauen, bis der Weg frei ist.",
        "for i in range(8):\n    while not figur.vorne_frei():\n        figur.baue_ab()\n"
        "    figur.gehe()\n",
        _a6, lambda f: _steht_auf(f, 8, 1), verlangt=("schleife", "bedingung"),
        tipps=("`not` dreht um: `not figur.vorne_frei()` heißt „vorne ist NICHT frei“.",),
    ),
    Aufgabe(
        7, "stufen_zaehlen", "Stufen zählen", "Variable",
        "Wie viele Stufen hat die Treppe? Schau nicht nach – lass Kubi **zählen**.\n\n"
        "Eine **Variable** merkt sich einen Wert:\n\n"
        "```python\nanzahl = 0\nanzahl = anzahl + 1\n```\n\n"
        "Kubi soll die Treppe hinaufsteigen, dabei jede Stufe mitzählen und oben die "
        "Anzahl mit `figur.sage(anzahl)` verkünden.\n\n"
        "Mit `figur.hoehe_vorne()` und `figur.hoehe_hier()` erfährt Kubi die Höhe des "
        "Feldes vor sich und unter sich.",
        "anzahl = 0\nwhile figur.hoehe_vorne() > figur.hoehe_hier():\n    figur.gehe()\n"
        "    anzahl = anzahl + 1\nfigur.sage(anzahl)\n",
        _a7, _z7, verlangt=("schleife",),
        tipps=("Die Schleife läuft, solange das Feld vor Kubi **höher** ist als das Feld, auf dem Kubi steht.",),
    ),
    Aufgabe(
        8, "tuerme", "Vier Türme", "Funktion",
        "Kubi soll **vier Türme** aus je 3 Ziegelblöcken bauen, mit einem freien Feld "
        "dazwischen. Die Türme stehen auf der Reihe vor Kubi (y = 1).\n\n"
        "Einen Turm zu bauen ist immer dasselbe. Gib dieser Handlung einen **Namen** – "
        "mit einer Funktion:\n\n"
        "```python\ndef turm():\n    for i in range(3):\n        figur.baue(\"ziegel\")\n```\n\n"
        "Danach genügt `turm()`, um einen Turm zu bauen.",
        "def turm():\n    for i in range(3):\n        figur.baue(\"ziegel\")\n\n"
        "for i in range(4):\n    turm()\n    figur.drehe_links()\n    figur.gehe(2)\n"
        "    figur.drehe_rechts()\n",
        _a8, _z8, verlangt=("funktion",),
        tipps=("Zwischen zwei Türmen: nach links drehen, 2 Schritte gehen, wieder nach rechts drehen.",),
    ),
]
_NACH_NR = {a.nr: a for a in AUFGABEN}


# ---------------------------------------------------------------------------
# Bewertung

def fehlende_bausteine(quelltext, verlangt):
    """Welche verlangten Bausteine (Schleife, Bedingung, Funktion) fehlen im Programm?"""
    try:
        baum = ast.parse(quelltext)
    except SyntaxError:
        return []
    knoten = list(ast.walk(baum))
    fehlt = []
    for name in verlangt:
        typen, beschreibung = _BAUSTEINE[name]
        if not any(isinstance(k, typen) for k in knoten):
            fehlt.append(beschreibung)
    return fehlt


def bewerte(aufgabe, figur, quelltext=None):
    """None, wenn gelöst – sonst ein Hinweis in einfacher Sprache."""
    if quelltext is not None:
        fehlt = fehlende_bausteine(quelltext, aufgabe.verlangt)
        if fehlt:
            return "Dein Programm soll " + " und ".join(fehlt) + " benutzen."
    return aufgabe.ziel(figur)


_aktuell = {"aufgabe": None, "figur": None}


def aufgabe(nr):
    """Baut die Welt für Aufgabe ``nr`` auf, zeigt den Auftrag und gibt Kubi zurück."""
    if nr not in _NACH_NR:
        raise KubixFehler(f"Die Aufgabe {nr} gibt es nicht. Es gibt die Aufgaben 1 bis {len(AUFGABEN)}.")
    a = _NACH_NR[nr]
    figur = a.aufbau()
    figur.welt.titel = f"kubix – Aufgabe {a.nr}: {a.titel}"
    _aktuell["aufgabe"], _aktuell["figur"] = a, figur
    print(f"Aufgabe {a.nr}: {a.titel}  ({a.konzept})")
    return figur


def pruefe():
    """Prüft, ob die aktuelle Aufgabe gelöst ist, und Kubi sagt das Ergebnis."""
    a, figur = _aktuell["aufgabe"], _aktuell["figur"]
    if a is None:
        raise KubixFehler("Es gibt keine Aufgabe zum Prüfen. Starte mit: figur = aufgabe(1)")
    quelltext = None
    try:
        datei = sys._getframe(1).f_code.co_filename
        if os.path.isfile(datei):
            with open(datei, encoding="utf-8") as f:
                quelltext = f.read()
    except (OSError, ValueError, UnicodeDecodeError):
        pass
    hinweis = bewerte(a, figur, quelltext)
    if hinweis is None:
        print(f"✓ Aufgabe {a.nr} geschafft!")
        figur.sage("Geschafft!", 2)
        return True
    print(f"✗ Noch nicht ganz: {hinweis}")
    for t in a.tipps[:1]:
        print(f"  Tipp: {t}")
    figur.sage("Noch nicht ganz …", 2)
    return False


# ---------------------------------------------------------------------------
# Arbeitsblatt-Export (für Koalino und andere Editoren)

def arbeitsblatt(a, mit_loesung=False):
    """Markdown-Arbeitsblatt zu einer Aufgabe (Obsidian-Callouts wie in Koalino)."""
    teile = [f"# Aufgabe {a.nr}: {a.titel}", "", f"*Baustein: {a.konzept}*", "", a.text, "",
             "## Dein Programm", "", "Starte mit dieser Vorlage:", "",
             "```python", a.vorlage().rstrip("\n"), "```", ""]
    for t in a.tipps:
        teile += [f"> [!tip] Tipp", f"> {t}", ""]
    teile += ["Wenn du fertig bist, prüft `pruefe()` dein Ergebnis.", ""]
    if mit_loesung:
        teile += ["> [!loesung]- Lösung (Lehrkräfte)", "> ```python", "> from kubix import *",
                  f"> figur = aufgabe({a.nr})", ">"]
        teile += [f"> {z}" if z else ">" for z in a.loesung.rstrip("\n").splitlines()]
        teile += ["> ", "> pruefe()", "> ```", ""]
    return "\n".join(teile)


def exportiere(nr, ordner, mit_loesung=False):
    """Schreibt Vorlage (.py) und Arbeitsblatt (.md) in ``ordner``; gibt beide Pfade zurück.

    Eine vorhandene Programmdatei wird nie überschrieben (Schülerarbeit!), das
    Arbeitsblatt schon.
    """
    if nr not in _NACH_NR:
        raise KubixFehler(f"Die Aufgabe {nr} gibt es nicht.")
    a = _NACH_NR[nr]
    os.makedirs(ordner, exist_ok=True)
    py = os.path.join(ordner, a.dateiname + ".py")
    md = os.path.join(ordner, a.dateiname + ".md")
    if not os.path.exists(py):
        with open(py, "w", encoding="utf-8") as f:
            f.write(a.vorlage())
    with open(md, "w", encoding="utf-8") as f:
        f.write(arbeitsblatt(a, mit_loesung))
    return py, md


def als_liste():
    return [{"nr": a.nr, "titel": a.titel, "konzept": a.konzept} for a in AUFGABEN]


def _cli(argv):
    """python -m kubix liste | export <nr> <ordner> [--loesung]"""
    if not argv or argv[0] == "liste":
        print(json.dumps(als_liste(), ensure_ascii=False))
        return 0
    if argv[0] == "export" and len(argv) >= 3:
        try:
            nr = int(argv[1])
        except ValueError:
            print("Aufgabennummer muss eine Zahl sein.", file=sys.stderr)
            return 2
        py, md = exportiere(nr, argv[2], "--loesung" in argv[3:])
        print(json.dumps({"py": py, "md": md}, ensure_ascii=False))
        return 0
    print(_cli.__doc__, file=sys.stderr)
    return 2
