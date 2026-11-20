"""Vérifications de SS-1 : sorties et indépendance des défauts SS-2."""

import math

import numpy as np
import pytest

from jumeau.contrat import UNITES, Statut, Variable
from jumeau.ss1_boucle import SimulateurBoucle
from jumeau.ss2_mesures import AcquisitionMesures


def contexte(defauts=None):
    return {
        "graine": 2026,
        "scenario": {
            "consignes_initiales": {
                "vitesse_pompe": 1.0,
                "puissance_W": 1000.0,
            },
            "defauts": defauts or [],
        },
    }


def consignes(k):
    # Introduire un transitoire pour tester une trajectoire non constante.
    return {
        "vitesse_pompe": 1.0 if k < 50 else 0.7,
        "puissance_W": 1000.0,
    }


def test_ss1_100_cycles_sorties_et_unites():
    boucle = SimulateurBoucle()
    boucle.demarrer(contexte())

    assert UNITES == {
        Variable.T: "°C",
        Variable.P: "MPa",
        Variable.Q: "kg/s",
    }

    for k in range(100):
        valeurs = boucle.etape(k, {"consignes": consignes(k)})[
            "grandeurs_vraies"
        ]

        assert set(valeurs) == set(Variable)
        assert all(
            isinstance(v, float) and math.isfinite(v)
            for v in valeurs.values()
        )

        # Repères numériques indépendants pour détecter une mauvaise unité.
        assert 20.0 < valeurs[Variable.T] < 40.0  # °C
        assert valeurs[Variable.P] == pytest.approx(
            0.108 if k < 50 else 0.10392
        )  # MPa, et non kPa
        assert valeurs[Variable.Q] == pytest.approx(
            0.1 if k < 50 else 0.07
        )  # kg/s


@pytest.mark.parametrize("defaut", [
    {
        "type": "derive", "variable": "T", "debut_s": 10,
        "pente_sigma_par_cycle": 0.01,
        "amplitude_max_pct_etendue": 2.5,
    },
    {
        "type": "saut", "variable": "T", "debut_s": 10,
        "amplitude_sigma": 10.0,
    },
    {
        "type": "perte_communication", "variable": "T",
        "debut_s": 10, "duree_s": 20,
    },
    {
        "type": "hors_plage", "variable": "T",
        "debut_s": 10, "duree_s": 20,
    },
])
def test_ss1_independant_des_defauts_ss2(defaut):
    boucles = [SimulateurBoucle(), SimulateurBoucle()]
    acquisitions = [AcquisitionMesures(), AcquisitionMesures()]

    for boucle, acquisition, ctx in zip(
        boucles, acquisitions, [contexte(), contexte([defaut])]
    ):
        boucle.demarrer(ctx)
        acquisition.demarrer(ctx)

    assert acquisitions[1].defauts == [defaut]
    effet_observe = False

    for k in range(100):
        sorties = []
        mesures = []

        for boucle, acquisition in zip(boucles, acquisitions):
            vraies = boucle.etape(
                k, {"consignes": consignes(k)}
            )["grandeurs_vraies"]
            copie = dict(vraies)

            resultat = acquisition.etape(k, {
                "grandeurs_vraies": vraies,
                "horodatage_utc": "2026-11-19T12:00:00Z",
            })

            # SS-2 ne doit pas modifier les valeurs reçues de SS-1.
            assert vraies == copie
            sorties.append(vraies)
            mesures.append(resultat["mesures"][Variable.T])

        assert sorties[0] == sorties[1]
        np.testing.assert_array_equal(
            boucles[0].temperatures, boucles[1].temperatures
        )

        if k >= 10:
            effet_observe |= (
                mesures[0].valeur != mesures[1].valeur
                or mesures[0].statut != mesures[1].statut
            )

    # Éviter une réussite trompeuse si aucun défaut n'a réellement agi.
    assert effet_observe