"""Contrat de données commun aux six sous-systèmes.

Ce fichier traduit en code le tableau 7-2 du rapport d'ingénierie de concept.
Il est partagé par toute l'équipe : on ne le modifie qu'avec l'accord du
chargé de projet, parce qu'un changement ici touche tous les modules.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from enum import Enum

# Durée d'un cycle, en secondes (tableau 8-6 du rapport de concept).
T_CYCLE = 1.0

# Nombre de cycles sans donnée valide avant l'état « incertain » (EX-F-06).
N_INCERTAIN = 3


class Variable(str, Enum):
    """Les trois grandeurs surveillées (HYP1)."""
    T = "T"  # température en sortie du volume V1
    P = "P"  # pression absolue
    Q = "Q"  # débit massique


UNITES = {Variable.T: "°C", Variable.P: "MPa", Variable.Q: "kg/s"}

# Étendue de mesure de chaque capteur. Une valeur hors de cette plage est
# rejetée par SS-2 (EX-Q-04). Valeurs provisoires, à confirmer par le lot SS-2.
PLAGES = {
    Variable.T: (0.0, 100.0),
    Variable.P: (0.0, 0.5),
    Variable.Q: (0.0, 0.5),
}


class Statut(str, Enum):
    """Statut de qualité d'une mesure."""
    VALIDE = "valide"
    ABSENT = "absent"
    HORS_PLAGE = "hors_plage"


class Etat(str, Enum):
    """Les quatre états présentés à l'opérateur (EX-F-04, EX-F-06)."""
    NORMAL = "normal"
    DERIVE = "derive"
    ANOMALIE = "anomalie"
    INCERTAIN = "incertain"


@dataclass(frozen=True)
class Mesure:
    """Une mesure produite par SS-2, selon le tableau 7-2.

    Règle du contrat : une mesure qui n'est pas valide n'a pas de valeur.
    Une absence n'est jamais codée par zéro.
    """
    k: int
    t: float
    horodatage_utc: str
    variable: Variable
    valeur: float | None
    statut: Statut

    def __post_init__(self) -> None:
        if self.k < 0:
            raise ValueError("Le numéro de cycle doit être positif ou nul.")
        if not math.isclose(self.t, self.k * T_CYCLE):
            raise ValueError("Le temps simulé doit valoir k × T.")
        if self.statut is Statut.VALIDE:
            if self.valeur is None or not math.isfinite(self.valeur):
                raise ValueError("Une mesure valide doit porter une valeur finie.")
        elif self.valeur is not None:
            raise ValueError("Une mesure non valide ne doit pas porter de valeur.")

    def en_dict(self) -> dict:
        d = asdict(self)
        d["variable"] = self.variable.value
        d["statut"] = self.statut.value
        return d
