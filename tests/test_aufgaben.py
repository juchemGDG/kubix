import json
import subprocess
import sys

import pytest

from kubix import aufgaben as A


@pytest.mark.parametrize("a", A.AUFGABEN, ids=lambda a: a.schluessel)
def test_musterloesung_loest_die_aufgabe(a):
    figur = A.aufgabe(a.nr)
    exec(a.loesung, {"figur": figur})
    assert A.bewerte(a, figur, a.loesung) is None


@pytest.mark.parametrize("a", A.AUFGABEN, ids=lambda a: a.schluessel)
def test_leeres_programm_loest_nicht(a):
    figur = A.aufgabe(a.nr)
    assert A.bewerte(a, figur, a.vorlage()) is not None


def test_ohne_schleife_wird_abgelehnt():
    a = A._NACH_NR[3]
    figur = A.aufgabe(3)
    code = "figur.gehe()\nfigur.drehe_rechts()\nfigur.gehe()\nfigur.drehe_links()\n" * 6
    exec(code, {"figur": figur})
    assert A.bewerte(a, figur, code) is not None and "Schleife" in A.bewerte(a, figur, code)
    assert A._steht_auf(figur, 6, 6) is None  # Ziel erreicht, nur der Baustein fehlt


def test_falsche_zahl_bei_stufen():
    a = A._NACH_NR[7]
    figur = A.aufgabe(7)
    code = "while figur.hoehe_vorne() > figur.hoehe_hier():\n    figur.gehe()\nfigur.sage(8, 0)\n"
    exec(code, {"figur": figur})
    assert "Zähle" in A.bewerte(a, figur, code)


def test_unbekannte_aufgabe():
    with pytest.raises(A.KubixFehler, match="1 bis 8"):
        A.aufgabe(99)


def test_pruefe_ohne_aufgabe():
    A._aktuell["aufgabe"] = None
    with pytest.raises(A.KubixFehler, match="Aufgabe"):
        A.pruefe()


def test_pruefe_im_echten_programm(tmp_path):
    prog = tmp_path / "p.py"
    prog.write_text("from kubix import *\nfigur = aufgabe(1)\nfigur.gehe(4)\npruefe()\n")
    r = subprocess.run([sys.executable, str(prog)], capture_output=True, text=True)
    assert "✓ Aufgabe 1 geschafft" in r.stdout, r.stdout + r.stderr
    prog.write_text("from kubix import *\nfigur = aufgabe(1)\nfigur.gehe(2)\npruefe()\n")
    r = subprocess.run([sys.executable, str(prog)], capture_output=True, text=True)
    assert "Noch nicht ganz" in r.stdout and "(2|0)" in r.stdout


def test_export_ohne_und_mit_loesung(tmp_path):
    py, md = A.exportiere(3, str(tmp_path))
    text = open(md, encoding="utf-8").read()
    assert "figur = aufgabe(3)" in open(py).read()
    assert "Lösung" not in text and "```python" in text
    _, md2 = A.exportiere(3, str(tmp_path), mit_loesung=True)
    assert "[!loesung]" in open(md2, encoding="utf-8").read()


def test_export_ueberschreibt_schuelerarbeit_nie(tmp_path):
    py, _ = A.exportiere(1, str(tmp_path))
    open(py, "w").write("# meine Arbeit\n")
    A.exportiere(1, str(tmp_path))
    assert open(py).read() == "# meine Arbeit\n"


def test_cli(tmp_path):
    r = subprocess.run([sys.executable, "-m", "kubix", "liste"], capture_output=True, text=True)
    daten = json.loads(r.stdout)
    assert len(daten) == 8 and daten[0]["titel"] == "Erste Schritte"
    r = subprocess.run([sys.executable, "-m", "kubix", "export", "2", str(tmp_path)],
                       capture_output=True, text=True)
    pfade = json.loads(r.stdout)
    assert pfade["py"].endswith("Aufgabe_02_um_die_ecke.py")
