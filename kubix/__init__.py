"""kubix – Programmieren lernen mit einer Figur in einer Würfelwelt.

    from kubix import Figur
    figur = Figur()
    figur.gehe(3)
"""
import os
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")   # kein pygame-Banner in der Schüler-Konsole

from .fehler import KubixFehler
from .aufgaben import aufgabe, pruefe
from .figur import Figur
from .render import MATERIALIEN
from .welt import Welt, standard_welt

__version__ = "0.3.0"
__all__ = ["Welt", "Figur", "KubixFehler", "MATERIALIEN", "pause", "fertig", "aufgabe", "pruefe"]


def pause(sekunden=1):
    """Wartet kurz (das Fenster bleibt bedienbar)."""
    standard_welt().pause(sekunden)


def fertig():
    """Hält das Fenster offen, bis es geschlossen wird. (Passiert am Programmende sowieso.)"""
    welt = standard_welt()
    welt._am_ende()
