"""Die Figur, die man mit Befehlen steuert."""
import math
import time

from . import render
from .fehler import KubixFehler, vorschlag
from .welt import Welt, standard_welt

RICHTUNGEN = ["norden", "osten", "sueden", "westen"]
_SCHRITT = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def _ganzzahl(befehl, name, wert, minimum=0):
    if isinstance(wert, bool) or not isinstance(wert, int):
        raise KubixFehler(f"{befehl}() braucht eine ganze Zahl, zum Beispiel {befehl}(3) – nicht {wert!r}.")
    if wert < minimum:
        raise KubixFehler(f"{befehl}(): „{name}“ darf nicht kleiner als {minimum} sein.")
    return wert


class Figur:
    """Eine Figur in einer Welt.

    >>> figur = Figur()
    >>> figur.gehe(3)
    >>> figur.drehe_rechts()

    Blickrichtungen: norden (rechts oben), osten (rechts unten),
    sueden (links unten), westen (links oben).
    """

    def __init__(self, welt=None, x=0, y=0, richtung="osten", name="Kubi"):
        self.welt = welt if welt is not None else standard_welt()
        self.name = name
        self.welt._pruefe(x, y)
        if richtung not in RICHTUNGEN:
            raise KubixFehler(f"Die Richtung „{richtung}“ gibt es nicht.{vorschlag(richtung, RICHTUNGEN)} "
                              f"Möglich sind: {', '.join(RICHTUNGEN)}.")
        self.x, self.y = x, y
        self._richtung = RICHTUNGEN.index(richtung)
        self._fx, self._fy = float(x), float(y)
        self._fz = float(self.welt.hoehe(x, y))
        self._anzeige_richtung = self._richtung
        self._huepf = 0.0
        self._sprech = None
        self._gesagt = []          # alle bisher gesagten Texte (für die Aufgabenprüfung)
        self.welt.figuren.append(self)
        self.welt._frame()

    # ---- Abfragen ----------------------------------------------------
    @property
    def blickrichtung(self):
        return RICHTUNGEN[self._richtung]

    def _vorne(self):
        dx, dy = _SCHRITT[self._richtung]
        return self.x + dx, self.y + dy

    def _hindernis(self, nx, ny):
        """None, wenn man hingehen kann, sonst der Grund (in einfacher Sprache)."""
        if not self.welt.im_raster(nx, ny):
            return "Hier ist die Welt zu Ende."
        if self.welt.material(nx, ny) == "wasser":
            return "Da ist Wasser. Baue eine Brücke!"
        diff = self.welt.hoehe(nx, ny) - self.welt.hoehe(self.x, self.y)
        if diff > 1:
            return "Da ist eine Wand im Weg – sie ist höher als eine Stufe."
        if diff < -1:
            return "Da geht es zu tief hinunter."
        return None

    def vorne_frei(self):
        """True, wenn die Figur einen Schritt nach vorne gehen kann."""
        return self._hindernis(*self._vorne()) is None

    def hoehe_hier(self):
        """Anzahl der Blöcke auf dem Feld, auf dem die Figur steht."""
        return self.welt.hoehe(self.x, self.y)

    def hoehe_vorne(self):
        """Anzahl der Blöcke auf dem Feld vor der Figur (0 am Rand der Welt)."""
        nx, ny = self._vorne()
        return self.welt.hoehe(nx, ny) if self.welt.im_raster(nx, ny) else 0

    def material_vorne(self):
        """Material des obersten Blocks vor der Figur (None am Rand der Welt)."""
        nx, ny = self._vorne()
        return self.welt.material(nx, ny) if self.welt.im_raster(nx, ny) else None

    # ---- Befehle -----------------------------------------------------
    def gehe(self, schritte=1):
        """Geht ``schritte`` Felder nach vorne. Eine Stufe rauf oder runter ist kein Problem."""
        schritte = _ganzzahl("gehe", "schritte", schritte)
        for _ in range(schritte):
            nx, ny = self._vorne()
            grund = self._hindernis(nx, ny)
            if grund:
                raise KubixFehler(f"{self.name} kann nicht gehen. {grund}")
            x0, y0, z0 = self.x, self.y, self._fz
            z1 = float(self.welt.hoehe(nx, ny))

            def schritt(t, x0=x0, y0=y0, z0=z0, nx=nx, ny=ny, z1=z1):
                self._fx = x0 + (nx - x0) * t
                self._fy = y0 + (ny - y0) * t
                self._fz = z0 + (z1 - z0) * t
                self._huepf = math.sin(math.pi * t) * 0.12

            self.welt._animiere(0.35, schritt)
            self.x, self.y = nx, ny
            self._fx, self._fy, self._fz, self._huepf = float(nx), float(ny), z1, 0.0

    def _drehe(self, delta):
        def schritt(t):
            if t >= 0.5:
                self._anzeige_richtung = (self._richtung + delta) % 4
        self.welt._animiere(0.25, schritt)
        self._richtung = (self._richtung + delta) % 4
        self._anzeige_richtung = self._richtung

    def drehe_links(self):
        """Dreht die Figur um 90° nach links."""
        self._drehe(-1)

    def drehe_rechts(self):
        """Dreht die Figur um 90° nach rechts."""
        self._drehe(1)

    def baue(self, material="stein"):
        """Setzt einen Block auf das Feld vor der Figur."""
        nx, ny = self._vorne()
        if not self.welt.im_raster(nx, ny):
            raise KubixFehler(f"{self.name} kann nicht bauen. Hier ist die Welt zu Ende.")
        self.welt.stapel(nx, ny, material)
        self.welt._animiere(0.2, lambda t: None)

    def baue_ab(self):
        """Nimmt den obersten Block vom Feld vor der Figur weg."""
        nx, ny = self._vorne()
        if not self.welt.im_raster(nx, ny):
            raise KubixFehler(f"{self.name} kann nichts abbauen. Hier ist die Welt zu Ende.")
        spalte = self.welt._spalten[nx][ny]
        if len(spalte) <= 1:
            raise KubixFehler(f"{self.name} kann nichts abbauen. Hier ist nur noch der Boden.")
        spalte.pop()
        self.welt._frame()
        self.welt._animiere(0.2, lambda t: None)

    def schiebe(self):
        """Schiebt einen einzelnen Holzblock vor der Figur ein Feld weiter.

        Die Figur selbst bleibt stehen. Der Block muss allein auf dem Boden
        liegen und aus Holz sein; dahinter muss das Feld frei sein (nur Boden).
        Holz schwimmt – auf Wasser geschoben wird es zu einem Floß.
        """
        nx, ny = self._vorne()
        if not self.welt.im_raster(nx, ny):
            raise KubixFehler(f"{self.name} kann nichts schieben. Hier ist die Welt zu Ende.")
        spalte = self.welt._spalten[nx][ny]
        bloecke = len(spalte) - 1                      # ohne den Boden
        if bloecke == 0:
            raise KubixFehler(f"{self.name} kann nichts schieben. Vor {self.name} liegt kein Block.")
        if bloecke > 1:
            raise KubixFehler(
                f"{self.name} kann nicht schieben. Dort liegen {bloecke} Blöcke übereinander – "
                f"{self.name} kann nur einen einzelnen Block schieben.")
        if spalte[-1] != "holz":
            raise KubixFehler(
                f"{self.name} kann nicht schieben. Der Block ist aus „{spalte[-1]}“ – "
                f"{self.name} kann nur Blöcke aus Holz („holz“) schieben.")
        if self.hoehe_hier() > 1:
            raise KubixFehler(
                f"{self.name} kann nicht schieben. {self.name} steht zu hoch und kommt nicht an den Block.")
        dx, dy = _SCHRITT[self._richtung]
        zx, zy = nx + dx, ny + dy
        if not self.welt.im_raster(zx, zy):
            raise KubixFehler(f"{self.name} kann nicht schieben. Hinter dem Block ist die Welt zu Ende.")
        if len(self.welt._spalten[zx][zy]) > 1:
            raise KubixFehler(f"{self.name} kann nicht schieben. Hinter dem Block ist kein Platz.")
        if any((f.x, f.y) == (zx, zy) for f in self.welt.figuren):
            raise KubixFehler(f"{self.name} kann nicht schieben. Hinter dem Block steht jemand.")
        self.welt._spalten[zx][zy].append(spalte.pop())
        self.welt._frame()
        self.welt._animiere(0.25, lambda t: None)

    def sage(self, text, sekunden=2):
        """Eine Sprechblase über der Figur."""
        self._gesagt.append(str(text))
        self._sprech = (str(text), time.perf_counter())
        self.welt._frame()
        self.welt._animiere(sekunden, lambda t: None)
        self._sprech = None
        self.welt._frame()

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        befehle = [n for n in dir(type(self)) if not n.startswith("_")]
        raise KubixFehler(f"{self.name} kennt den Befehl „{name}“ nicht.{vorschlag(name, befehle)}")
