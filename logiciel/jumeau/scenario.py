"""Lecture et contrôle d'un fichier de scénario (EX-F-02)."""
from __future__ import annotations

import json
from pathlib import Path

from jumeau.contrat import Variable

CLES_OBLIGATOIRES = ("nom", "version", "graine", "cycles", "consignes_initiales")
TYPES_DEFAUT = ("derive", "saut", "perte_communication", "hors_plage")


def charger(chemin: str | Path) -> dict:
    scenario = json.loads(Path(chemin).read_text(encoding="utf-8"))
    manquantes = [c for c in CLES_OBLIGATOIRES if c not in scenario]
    if manquantes:
        raise ValueError(f"Clés manquantes dans le scénario : {', '.join(manquantes)}")
    for defaut in scenario.get("defauts", []):
        if defaut.get("type") not in TYPES_DEFAUT:
            raise ValueError(f"Type de défaut inconnu : {defaut.get('type')}")
        if defaut.get("variable") not in [v.value for v in Variable] + ["toutes"]:
            raise ValueError(f"Variable inconnue : {defaut.get('variable')}")
    return scenario
