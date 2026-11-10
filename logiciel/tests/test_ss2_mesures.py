
"""Tests spécifiques au sous-système SS-2.

Acquisition, qualification et rejet des données invalides.
"""

import math

import pytest

from jumeau.contrat import Mesure, Statut, Variable
from jumeau.ss2_mesures import AcquisitionMesures, valider_valeur_brute


HORODATAGE = "2026-11-10T12:00:00Z"


def creer_ss2(defauts=None):
    """Crée un SS-2 avec une graine fixe."""
    ss2 = AcquisitionMesures()
    ss2.demarrer({
        "graine": 2026,
        "scenario": {"defauts": defauts or []},
    })
    return ss2


def executer_cycle(ss2, valeurs, k=0):
    """Exécute un cycle avec les données fournies."""
    return ss2.etape(k, {
        "grandeurs_vraies": valeurs,
        "horodatage_utc": HORODATAGE,
    })


def valeurs_nominales():
    return {
        Variable.T: 60.0,
        Variable.P: 0.25,
        Variable.Q: 0.25,
    }


def test_trois_mesures_valides():
    ss2 = creer_ss2()
    resultat = executer_cycle(ss2, valeurs_nominales())

    assert len(resultat["mesures"]) == 3
    assert resultat["evenements"] == []

    for var in Variable:
        mesure = resultat["mesures"][var]

        assert isinstance(mesure, Mesure)
        assert mesure.variable == var
        assert mesure.statut is Statut.VALIDE
        assert math.isfinite(mesure.valeur)


@pytest.mark.parametrize(
    "valeur_invalide",
    [
        "erreur",
        None,
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
    ],
)
def test_rejet_temperature_malformee(valeur_invalide):
    ss2 = creer_ss2()
    valeurs = valeurs_nominales()
    valeurs[Variable.T] = valeur_invalide

    resultat = executer_cycle(ss2, valeurs)
    mesure = resultat["mesures"][Variable.T]

    assert mesure.statut is Statut.ABSENT
    assert mesure.valeur is None

    assert any(
        e["type"] == "mesure_rejetee"
        and e["variable"] == "T"
        and e["motif"] == "format_invalide"
        for e in resultat["evenements"]
    )


def test_donnee_manquante():
    ss2 = creer_ss2()
    valeurs = valeurs_nominales()
    del valeurs[Variable.P]

    resultat = executer_cycle(ss2, valeurs)

    assert resultat["mesures"][Variable.P].statut is Statut.ABSENT
    assert resultat["mesures"][Variable.P].valeur is None


def test_autres_capteurs_restent_valides():
    ss2 = creer_ss2()
    valeurs = valeurs_nominales()
    valeurs[Variable.T] = "erreur"

    resultat = executer_cycle(ss2, valeurs)

    assert resultat["mesures"][Variable.T].valeur is None
    assert resultat["mesures"][Variable.P].statut is Statut.VALIDE
    assert resultat["mesures"][Variable.Q].statut is Statut.VALIDE


def test_reproductibilite():
    a = creer_ss2()
    b = creer_ss2()

    for k in range(30):
        resultat_a = executer_cycle(a, valeurs_nominales(), k)
        resultat_b = executer_cycle(b, valeurs_nominales(), k)

        assert resultat_a == resultat_b


def test_hors_plage():
    ss2 = creer_ss2()
    valeurs = valeurs_nominales()
    valeurs[Variable.Q] = 1.0

    resultat = executer_cycle(ss2, valeurs)

    assert resultat["mesures"][Variable.Q].statut is Statut.HORS_PLAGE
    assert resultat["mesures"][Variable.Q].valeur is None


def test_validation_directe():
    assert valider_valeur_brute(60.5)
    assert valider_valeur_brute(0.25)

    assert not valider_valeur_brute("erreur")
    assert not valider_valeur_brute(None)
    assert not valider_valeur_brute(float("nan"))
    assert not valider_valeur_brute(float("inf"))
    assert not valider_valeur_brute(True)
