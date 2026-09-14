#!/usr/bin/env python3
"""Validation TEI P5 automatique, en amont de l'extraction (point 1 de
la feuille de route "amelioration du pipeline") : detecter un fichier
XML mal forme ou non conforme au schema TEI AVANT de lancer dessus des
heures de traduction/NER, plutot que de le decouvrir a la fin.

Le schema officiel (tei_all.rng, recupere depuis tei-c.org) est
compile UNE SEULE FOIS a l'import (operation couteuse, ~1-2s) puis
reutilise pour valider chaque fichier (rapide, quelques dizaines de ms
par fichier) - meme principe que le script d'audit ponctuel de la
session du 10-11 septembre 2026 (DOCUMENTATION_SYSTEME_ZOO.md section
24), ici integre au pipeline au lieu de rester un outil manuel.
"""
import os
from lxml import etree

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tei_schema", "tei_all.rng")

_relaxng = None


def _get_validator():
    global _relaxng
    if _relaxng is None:
        schema_doc = etree.parse(SCHEMA_PATH)
        _relaxng = etree.RelaxNG(schema_doc)
    return _relaxng


def validate_tei_file(file_path):
    """Valide un fichier XML contre le schema TEI P5. Retourne
    (ok: bool, erreurs: list[str]). Une erreur de parsing XML (fichier
    mal forme) est traitee comme une non-conformite, avec un message
    distinct."""
    validator = _get_validator()
    try:
        doc = etree.parse(file_path)
    except etree.XMLSyntaxError as e:
        return False, [f"XML mal forme (pas meme parsable) : {e}"]

    if validator.validate(doc):
        return True, []

    errors = [f"ligne {err.line}: {err.message}" for err in validator.error_log]
    return False, errors


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 tei_validator.py <fichier.xml> [<fichier2.xml> ...]")
        sys.exit(1)
    any_invalid = False
    for path in sys.argv[1:]:
        ok, errors = validate_tei_file(path)
        if ok:
            print(f"OK   {path}")
        else:
            any_invalid = True
            print(f"INVALIDE {path}")
            for e in errors[:5]:
                print(f"    {e}")
    sys.exit(1 if any_invalid else 0)
