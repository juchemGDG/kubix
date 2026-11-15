"""Zeichnen der Würfelwelt (isometrisch, alles selbst erzeugt – keine Fremd-Grafiken)."""
import math
import random

import pygame

TW, TH, BH, PX = 64, 32, 32, 4   # Kachelbreite/-höhe, Blockhöhe, „Pixel“-Größe der Textur
RAND = 10                         # Dicke des Grasrands an den Seiten
RAND_ABSTAND = 40                 # Außenrand des Fensters

# Material: (Oberseite, Seite, Rand oben an der Seite oder None)
MATERIALIEN = {
    "gras":   ((106, 176, 76), (139, 99, 66), (106, 176, 76)),
    "erde":   ((139, 99, 66), (139, 99, 66), None),
    "stein":  ((128, 132, 140), (128, 132, 140), None),
    "sand":   ((224, 208, 152), (224, 208, 152), None),
    "holz":   ((176, 132, 78), (160, 118, 68), None),
    "ziegel": ((184, 86, 68), (184, 86, 68), None),
    "schnee": ((242, 246, 252), (230, 236, 246), None),
    "gold":   ((244, 204, 64), (244, 204, 64), None),
    "wasser": ((74, 134, 214), (74, 134, 214), None),
}

_cache = {}


def _dunkler(farbe, f):
    return tuple(max(0, min(255, int(v * f))) for v in farbe[:3])


def _flaechen(material):
    """Die drei sichtbaren Flächen eines Blocks als Bilder (mit Pixel-Rauschen)."""
    if material in _cache:
        return _cache[material]
    oben, seite, rand = MATERIALIEN[material]
    rnd = random.Random(material)
    A, B, C, D = (TW // 2, 0), (TW, TH // 2), (TW // 2, TH), (0, TH // 2)
    polys = {
        "oben": [A, B, C, D],
        "links": [D, C, (C[0], C[1] + BH), (D[0], D[1] + BH)],
        "rechts": [B, C, (C[0], C[1] + BH), (B[0], B[1] + BH)],
    }
    licht = {"oben": 1.0, "links": 0.80, "rechts": 0.60}
    hoehe = TH + BH
    flaechen = {}
    for name, poly in polys.items():
        tex = pygame.Surface((TW, hoehe), pygame.SRCALPHA)
        grund = oben if name == "oben" else seite
        for cy in range(0, hoehe, PX):
            for cx in range(0, TW, PX):
                mx, my = cx + PX / 2, cy + PX / 2
                basis = grund
                if name != "oben" and rand:
                    kante = D[1] + mx / 2 if name == "links" else C[1] - (mx - C[0]) / 2
                    if my - kante < RAND:
                        basis = rand
                f = licht[name] * (1 + rnd.uniform(-0.06, 0.06))
                tex.fill(_dunkler(basis, f) + (255,), pygame.Rect(cx, cy, PX, PX))
        maske = pygame.Surface((TW, hoehe), pygame.SRCALPHA)
        pygame.draw.polygon(maske, (255, 255, 255, 255), poly)
        tex.blit(maske, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.polygon(tex, _dunkler(grund, licht[name] * 0.6) + (255,), poly, 1)
        flaechen[name] = tex
    _cache[material] = flaechen
    return flaechen


def _hintergrund(groesse):
    if _cache.get("bg_size") != groesse:
        bild = pygame.Surface(groesse)
        w, h = groesse
        for y in range(h):
            t = y / max(1, h - 1)
            farbe = (int(150 + 70 * t), int(200 + 40 * t), int(240 + 10 * t))
            pygame.draw.line(bild, farbe, (0, y), (w, y))
        _cache["bg"], _cache["bg_size"] = bild, groesse
    return _cache["bg"]


def fenstergroesse(breite, tiefe, max_hoehe):
    """(Breite, Höhe, Ursprung-x, Ursprung-y) des Zeichenbereichs."""
    ox = RAND_ABSTAND + tiefe * TW // 2
    oy = RAND_ABSTAND + max_hoehe * BH + 40
    w = (breite + tiefe) * TW // 2 + 2 * RAND_ABSTAND
    h = oy + (breite + tiefe) * TH // 2 + RAND_ABSTAND
    return w, h, ox, oy


def _hoehe(welt, x, y):
    if 0 <= x < welt.breite and 0 <= y < welt.tiefe:
        return len(welt._spalten[x][y])
    return 0


def _block(surf, welt, x, y, z, material, ox, oy):
    spalte_hoch = len(welt._spalten[x][y])
    fl = _flaechen(material)
    px = ox + (x - y) * TW // 2 - TW // 2
    py = oy + (x + y) * TH // 2 - (z + 1) * BH
    if _hoehe(welt, x, y + 1) <= z:
        surf.blit(fl["links"], (px, py))
    if _hoehe(welt, x + 1, y) <= z:
        surf.blit(fl["rechts"], (px, py))
    if z == spalte_hoch - 1:
        surf.blit(fl["oben"], (px, py))


def _proj(ox, oy, x, y, z):
    return (ox + (x - y) * TW / 2, oy + (x + y) * TH / 2 - z * BH)


def _quader(surf, ox, oy, x0, x1, y0, y1, z0, z1, farbe):
    """Ein kleiner Quader (für die Figur) mit drei beleuchteten Seiten."""
    P = lambda x, y, z: _proj(ox, oy, x, y, z)
    oben = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]
    links = [P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), P(x0, y1, z0)]
    rechts = [P(x1, y0, z1), P(x1, y1, z1), P(x1, y1, z0), P(x1, y0, z0)]
    pygame.draw.polygon(surf, _dunkler(farbe, 1.0), oben)
    pygame.draw.polygon(surf, _dunkler(farbe, 0.80), links)
    pygame.draw.polygon(surf, _dunkler(farbe, 0.60), rechts)


# Teile der Figur im Figuren-Koordinatensystem: (vorne_von, vorne_bis, seite_von, seite_bis, z_von, z_bis, Farbe)
_FELL = (150, 156, 168)
_FELL_DUNKEL = (104, 110, 122)
_TEILE = [
    (-0.10, 0.10, -0.24, -0.04, 0.00, 0.22, _FELL_DUNKEL),   # Bein
    (-0.10, 0.10, 0.04, 0.24, 0.00, 0.22, _FELL_DUNKEL),     # Bein
    (-0.18, 0.18, -0.26, 0.26, 0.22, 0.58, _FELL),           # Körper
    (-0.21, 0.21, -0.25, 0.25, 0.58, 0.98, (166, 172, 184)),  # Kopf
    (-0.06, 0.06, -0.38, -0.20, 0.78, 1.06, _FELL_DUNKEL),   # Ohr
    (-0.06, 0.06, 0.20, 0.38, 0.78, 1.06, _FELL_DUNKEL),     # Ohr
    (0.21, 0.28, -0.07, 0.07, 0.64, 0.78, (40, 40, 48)),     # Nase
    (0.21, 0.24, -0.19, -0.11, 0.82, 0.90, (30, 30, 40)),    # Auge
    (0.21, 0.24, 0.11, 0.19, 0.82, 0.90, (30, 30, 40)),      # Auge
]
_VORNE = [(0, -1), (1, 0), (0, 1), (-1, 0)]   # Norden, Osten, Süden, Westen


def _figur(surf, f, ox, oy):
    vx, vy = _VORNE[f._anzeige_richtung % 4]
    sx, sy = -vy, vx
    px, py = f._fx, f._fy
    zf = f._fz
    # Schatten
    sx_, sy_ = _proj(ox, oy, px + 0.5, py + 0.5, zf)
    schatten = pygame.Surface((TW, TH), pygame.SRCALPHA)
    pygame.draw.ellipse(schatten, (0, 0, 0, 70), pygame.Rect(TW * 0.25, TH * 0.25, TW * 0.5, TH * 0.5))
    surf.blit(schatten, (sx_ - TW / 2, sy_ - TH / 2))
    zf += f._huepf
    teile = []
    for fv0, fv1, s0, s1, z0, z1, farbe in _TEILE:
        xs = sorted((px + 0.5 + fv0 * vx + s0 * sx, px + 0.5 + fv1 * vx + s1 * sx))
        ys = sorted((py + 0.5 + fv0 * vy + s0 * sy, py + 0.5 + fv1 * vy + s1 * sy))
        teile.append(((xs[0] + xs[1] + ys[0] + ys[1], z0), xs, ys, z0, z1, farbe))
    teile.sort(key=lambda t: t[0])
    for _, xs, ys, z0, z1, farbe in teile:
        _quader(surf, ox, oy, xs[0], xs[1], ys[0], ys[1], zf + z0, zf + z1, farbe)


def _sprechblase(surf, f, ox, oy, schrift):
    text, _ = f._sprech
    bild = schrift.render(text, True, (30, 30, 40))
    bx, by = _proj(ox, oy, f._fx + 0.5, f._fy + 0.5, f._fz + 1.25 + f._huepf)
    rect = bild.get_rect(midbottom=(bx, by - 8)).inflate(20, 12)
    rect.clamp_ip(surf.get_rect())
    pygame.draw.rect(surf, (255, 255, 255), rect, border_radius=10)
    pygame.draw.rect(surf, (60, 60, 70), rect, 2, border_radius=10)
    spitze = [(bx - 6, rect.bottom - 1), (bx + 6, rect.bottom - 1), (bx, rect.bottom + 8)]
    pygame.draw.polygon(surf, (255, 255, 255), spitze)
    pygame.draw.lines(surf, (60, 60, 70), False, spitze, 2)
    surf.blit(bild, bild.get_rect(center=rect.center))


_schrift = {}


def zeichne(surf, welt):
    """Zeichnet die ganze Welt samt Figuren auf ``surf``."""
    if "f" not in _schrift:
        pygame.font.init()
        _schrift["f"] = pygame.font.Font(None, 26)
    ox, oy = welt._ursprung
    surf.blit(_hintergrund(surf.get_size()), (0, 0))
    figuren = sorted(welt.figuren, key=lambda f: f._fx + f._fy)
    i = 0
    for d in range(welt.breite + welt.tiefe - 1):
        for x in range(max(0, d - welt.tiefe + 1), min(welt.breite - 1, d) + 1):
            y = d - x
            for z, material in enumerate(welt._spalten[x][y]):
                _block(surf, welt, x, y, z, material, ox, oy)
        while i < len(figuren) and figuren[i]._fx + figuren[i]._fy < d + 1:
            _figur(surf, figuren[i], ox, oy)
            i += 1
    while i < len(figuren):
        _figur(surf, figuren[i], ox, oy)
        i += 1
    for f in figuren:
        if f._sprech:
            _sprechblase(surf, f, ox, oy, _schrift["f"])
