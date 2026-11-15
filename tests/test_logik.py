import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from kubix import Figur, KubixFehler, Welt


@pytest.fixture
def welt():
    return Welt(6, 6, fenster=False)


def test_gehen_und_drehen(welt):
    f = Figur(welt)
    f.gehe(3)
    assert (f.x, f.y) == (3, 0)
    f.drehe_rechts()
    assert f.blickrichtung == "sueden"
    f.gehe(2)
    assert (f.x, f.y) == (3, 2)
    f.drehe_links()
    f.drehe_links()
    assert f.blickrichtung == "norden"


def test_rand_der_welt(welt):
    f = Figur(welt)
    f.drehe_links()  # norden
    with pytest.raises(KubixFehler, match="zu Ende"):
        f.gehe()
    assert not f.vorne_frei()


def test_bauen_und_stufen(welt):
    f = Figur(welt)
    f.baue("stein")
    assert welt.hoehe(1, 0) == 2
    f.gehe()  # eine Stufe hinauf ist erlaubt
    assert f._fz == 2
    f.drehe_links(); f.drehe_links()  # nach westen
    f.gehe()  # eine Stufe hinunter
    assert f._fz == 1


def test_wand_im_weg(welt):
    f = Figur(welt)
    welt.stapel(1, 0, "stein", 2)  # Höhe 3 gegenüber Boden 1
    with pytest.raises(KubixFehler, match="Wand"):
        f.gehe()


def test_abbauen(welt):
    f = Figur(welt)
    with pytest.raises(KubixFehler, match="Boden"):
        f.baue_ab()
    f.baue("holz")
    f.baue_ab()
    assert welt.hoehe(1, 0) == 1


def test_max_hoehe():
    w = Welt(3, 3, max_hoehe=2, fenster=False)
    f = Figur(w)
    f.baue()
    with pytest.raises(KubixFehler, match="Höher"):
        f.baue()


def test_abfragen(welt):
    f = Figur(welt)
    welt.stapel(1, 0, "gold")
    assert f.material_vorne() == "gold"
    assert f.hoehe_vorne() == 2


def test_falsche_eingaben(welt):
    f = Figur(welt)
    with pytest.raises(KubixFehler, match="ganze Zahl"):
        f.gehe("3")
    with pytest.raises(KubixFehler, match="ganze Zahl"):
        f.gehe(1.5)
    with pytest.raises(KubixFehler, match="kenne ich nicht"):
        f.baue("steinn")
    with pytest.raises(KubixFehler, match="Meintest du „stein“"):
        f.baue("steinn")


def test_tippfehler_bei_befehlen(welt):
    f = Figur(welt)
    with pytest.raises(KubixFehler, match="Meintest du „gehe“"):
        f.geh(2)
    with pytest.raises(KubixFehler, match="Meintest du „drehe_links“"):
        f.dreh_links()
    with pytest.raises(KubixFehler, match="Meintest du „stapel“"):
        welt.stappel(0, 0)


def test_figur_ohne_welt_nutzt_standardwelt():
    Welt(4, 4, fenster=False)
    f = Figur()
    f.gehe(2)
    assert f.x == 2


def test_screenshot(welt, tmp_path):
    import pygame
    Figur(welt).sage("Hi", 0)
    welt.stapel(2, 2, "ziegel", 3)
    pfad = tmp_path / "welt.png"
    welt.screenshot(str(pfad))
    bild = pygame.image.load(str(pfad))
    farben = {tuple(bild.get_at((x, y)))[:3] for x in range(0, bild.get_width(), 5)
              for y in range(0, bild.get_height(), 5)}
    assert len(farben) > 20


def test_fenster_modus_mit_animation():
    """Echter Fenster-Pfad (mit Dummy-Treiber): Animation, Sprechblase, Schließen."""
    import pygame
    w = Welt(5, 5, fenster=True, tempo=50)
    assert w._offen
    f = Figur(w)
    f.gehe(2)
    f.drehe_rechts()
    f.baue("holz")
    f.sage("Hallo", 1)
    assert (f.x, f.y) == (2, 0) and w.hoehe(2, 1) == 2
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    with pytest.raises(SystemExit):
        f.gehe(1)
    assert not w._offen
