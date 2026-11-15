"""Die Welt: ein Raster aus Türmen von Blöcken, optional mit Fenster."""
import atexit
import os
import sys
import time

import pygame

from . import render
from .fehler import KubixFehler, vorschlag


class _Zustand:
    fehler = False          # Programm endete mit Fehler → Fenster nicht offen halten
    hook = False
    aktiv = None            # Welt, die gerade das Fenster besitzt
    standard = None         # Welt, die Figur() ohne Angabe verwendet


def _hook_installieren():
    if _Zustand.hook:
        return
    _Zustand.hook = True
    original = sys.excepthook

    def neu(typ, wert, tb):
        _Zustand.fehler = True
        original(typ, wert, tb)

    sys.excepthook = neu


class Welt:
    """Eine Würfelwelt.

    >>> welt = Welt(10, 10)

    ``fenster=False`` (oder Umgebungsvariable ``KUBIX_FENSTER=0``) rechnet nur,
    ohne Fenster – praktisch für Tests und Bildschirmfotos.
    """

    def __init__(self, breite=10, tiefe=10, max_hoehe=6, titel="kubix", fenster=None, tempo=1.0):
        for name, wert in (("breite", breite), ("tiefe", tiefe), ("max_hoehe", max_hoehe)):
            if not isinstance(wert, int) or not 1 <= wert <= 40:
                raise KubixFehler(f"Welt: „{name}“ muss eine ganze Zahl zwischen 1 und 40 sein.")
        self.breite, self.tiefe, self.max_hoehe = breite, tiefe, max_hoehe
        self.titel = titel
        self.tempo = tempo
        self.figuren = []
        self._spalten = [[["gras"] for _ in range(tiefe)] for _ in range(breite)]
        w, h, ox, oy = render.fenstergroesse(breite, tiefe, max_hoehe)
        self._groesse, self._ursprung = (w, h), (ox, oy)
        self._screen = None
        self._offen = False
        if fenster is None:
            fenster = os.environ.get("KUBIX_FENSTER", "1") != "0"
        if fenster:
            self._oeffne()
        _Zustand.standard = self

    # ---- Fenster -----------------------------------------------------
    def _oeffne(self):
        try:
            pygame.display.init()
            pygame.font.init()
            self._screen = pygame.display.set_mode(self._groesse)
        except pygame.error as e:
            print(f"kubix: Kein Fenster möglich ({e}). Es läuft ohne Anzeige weiter.", file=sys.stderr)
            return
        pygame.display.set_caption(self.titel)
        if _Zustand.aktiv and _Zustand.aktiv is not self:
            _Zustand.aktiv._offen = False
        _Zustand.aktiv = self
        self._offen = True
        self._uhr = pygame.time.Clock()
        _hook_installieren()
        atexit.register(self._am_ende)
        self._frame()

    def _frame(self):
        if self._offen:
            render.zeichne(self._screen, self)
            pygame.display.flip()

    def _ereignisse(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self._schliessen()
                raise SystemExit(0)

    def _schliessen(self):
        if self._offen:
            self._offen = False
            pygame.quit()

    def _am_ende(self):
        """Nach dem letzten Befehl: Fenster offen lassen, bis es geschlossen wird."""
        if not self._offen or _Zustand.fehler:
            return
        pygame.display.set_caption(f"{self.titel} – Fenster schließen zum Beenden")
        try:
            while self._offen:
                self._ereignisse()
                self._frame()
                self._uhr.tick(30)
        except SystemExit:
            pass

    def _animiere(self, dauer, schritt):
        """Ruft ``schritt(t)`` mit t von 0 bis 1 auf, während das Fenster läuft."""
        if not self._offen or not self.tempo or self.tempo <= 0:
            schritt(1.0)
            return
        dauer = dauer / self.tempo
        start = time.perf_counter()
        while True:
            self._ereignisse()
            t = min(1.0, (time.perf_counter() - start) / dauer) if dauer > 0 else 1.0
            schritt(t)
            self._frame()
            self._uhr.tick(60)
            if t >= 1.0:
                break

    # ---- Welt gestalten ----------------------------------------------
    def im_raster(self, x, y):
        return 0 <= x < self.breite and 0 <= y < self.tiefe

    def _pruefe(self, x, y):
        if not (isinstance(x, int) and isinstance(y, int)):
            raise KubixFehler("Die Koordinaten x und y müssen ganze Zahlen sein.")
        if not self.im_raster(x, y):
            raise KubixFehler(
                f"Das Feld ({x}|{y}) gibt es nicht. x geht von 0 bis {self.breite - 1}, "
                f"y von 0 bis {self.tiefe - 1}.")

    def hoehe(self, x, y):
        """Wie viele Blöcke übereinander stehen auf diesem Feld."""
        self._pruefe(x, y)
        return len(self._spalten[x][y])

    def material(self, x, y):
        """Material des obersten Blocks auf diesem Feld."""
        self._pruefe(x, y)
        return self._spalten[x][y][-1]

    def _pruefe_material(self, material):
        if material not in render.MATERIALIEN:
            raise KubixFehler(
                f"Das Material „{material}“ kenne ich nicht.{vorschlag(material, render.MATERIALIEN)} "
                f"Möglich sind: {', '.join(render.MATERIALIEN)}.")

    def stapel(self, x, y, material="stein", anzahl=1):
        """Setzt ``anzahl`` Blöcke aus ``material`` oben auf das Feld."""
        self._pruefe(x, y)
        self._pruefe_material(material)
        if len(self._spalten[x][y]) + anzahl > self.max_hoehe:
            raise KubixFehler(f"Höher als {self.max_hoehe} Blöcke geht es auf einem Feld nicht.")
        self._spalten[x][y].extend([material] * anzahl)
        self._frame()

    def fuelle(self, material="gras"):
        """Setzt den Boden der ganzen Welt auf ein Material (alle Türme verschwinden)."""
        self._pruefe_material(material)
        self._spalten = [[[material] for _ in range(self.tiefe)] for _ in range(self.breite)]
        self._frame()

    def pause(self, sekunden=1):
        """Wartet, ohne dass das Fenster einfriert."""
        self._animiere(sekunden, lambda t: None)

    def screenshot(self, pfad):
        """Speichert ein Bild der Welt (auch ohne Fenster)."""
        bild = pygame.Surface(self._groesse)
        render.zeichne(bild, self)
        pygame.image.save(bild, pfad)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        befehle = [n for n in dir(type(self)) if not n.startswith("_")]
        raise KubixFehler(f"Die Welt kennt „{name}“ nicht.{vorschlag(name, befehle)}")


def standard_welt():
    return _Zustand.standard or Welt()
