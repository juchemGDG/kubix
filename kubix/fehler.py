"""Verständliche Fehler für Einsteiger."""
import difflib


class KubixFehler(Exception):
    """Ein Fehler im kubix-Programm, mit Meldung in einfacher Sprache."""


def vorschlag(name, kandidaten):
    """' Meintest du „x“?' oder leerer String."""
    treffer = difflib.get_close_matches(name, list(kandidaten), n=1, cutoff=0.6)
    return f" Meintest du „{treffer[0]}“?" if treffer else ""
