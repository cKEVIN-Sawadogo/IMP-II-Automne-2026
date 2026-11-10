from __future__ import annotations

from jumeau.contrat import Mesure, Statut, Variable
from jumeau.ss3_reference import ReferenceBoucleOuverte


def mesure_valide(k: int, variable: Variable, valeur: float) -> Mesure:
    return Mesure(
        k=k,
        t=float(k),
        horodatage_utc="2026-11-10T00:00:00Z",
        variable=variable,
        valeur=valeur,
        statut=Statut.VALIDE,
    )


def test_ss3_n_est_pas_pret_avant_fin_calage():
    ss3 = ReferenceBoucleOuverte()

    contexte = {
        "scenario": {
            "consignes_initiales": {
                "vitesse_pompe": 1.0,
                "puissance_W": 1000.0,
            }
        }
    }

    ss3.demarrer(contexte)

    for k in range(599):
        mesures = {
            Variable.T: mesure_valide(k, Variable.T, 32.4),
            Variable.P: mesure_valide(k, Variable.P, 0.108),
            Variable.Q: mesure_valide(k, Variable.Q, 0.100),
        }

        sortie = ss3.etape(
            k,
            {
                "mesures": mesures,
                "consignes": {
                    "vitesse_pompe": 1.0,
                    "puissance_W": 1000.0,
                },
            },
        )

        assert sortie["pret"] is False


def test_ss3_devient_pret_apres_600_cycles():
    ss3 = ReferenceBoucleOuverte()

    contexte = {
        "scenario": {
            "consignes_initiales": {
                "vitesse_pompe": 1.0,
                "puissance_W": 1000.0,
            }
        }
    }

    ss3.demarrer(contexte)

    sortie = None

    for k in range(600):
        mesures = {
            Variable.T: mesure_valide(k, Variable.T, 32.4),
            Variable.P: mesure_valide(k, Variable.P, 0.108),
            Variable.Q: mesure_valide(k, Variable.Q, 0.100),
        }

        sortie = ss3.etape(
            k,
            {
                "mesures": mesures,
                "consignes": {
                    "vitesse_pompe": 1.0,
                    "puissance_W": 1000.0,
                },
            },
        )

    assert sortie is not None
    assert sortie["pret"] is True

    assert sortie["attendus"][Variable.T] is not None
    assert sortie["attendus"][Variable.P] is not None
    assert sortie["attendus"][Variable.Q] is not None


def test_ss3_produit_des_residus_apres_calage():
    ss3 = ReferenceBoucleOuverte()

    contexte = {
        "scenario": {
            "consignes_initiales": {
                "vitesse_pompe": 1.0,
                "puissance_W": 1000.0,
            }
        }
    }

    ss3.demarrer(contexte)

    for k in range(600):
        mesures = {
            Variable.T: mesure_valide(
                k,
                Variable.T,
                32.4 + 0.01 * ((k % 3) - 1),
            ),
            Variable.P: mesure_valide(
                k,
                Variable.P,
                0.108 + 0.0001 * ((k % 3) - 1),
            ),
            Variable.Q: mesure_valide(
                k,
                Variable.Q,
                0.100 + 0.0001 * ((k % 3) - 1),
            ),
        }

        sortie = ss3.etape(
            k,
            {
                "mesures": mesures,
                "consignes": {
                    "vitesse_pompe": 1.0,
                    "puissance_W": 1000.0,
                },
            },
        )

    assert sortie["pret"] is True

    for variable in Variable:
        assert sortie["residus"][variable] is not None


def test_mesure_invalide_donne_residu_none_apres_calage():
    ss3 = ReferenceBoucleOuverte()

    contexte = {
        "scenario": {
            "consignes_initiales": {
                "vitesse_pompe": 1.0,
                "puissance_W": 1000.0,
            }
        }
    }

    ss3.demarrer(contexte)

    for k in range(600):
        mesures = {
            Variable.T: mesure_valide(
                k,
                Variable.T,
                32.4 + 0.01 * ((k % 3) - 1),
            ),
            Variable.P: mesure_valide(
                k,
                Variable.P,
                0.108 + 0.0001 * ((k % 3) - 1),
            ),
            Variable.Q: mesure_valide(
                k,
                Variable.Q,
                0.100 + 0.0001 * ((k % 3) - 1),
            ),
        }

        ss3.etape(
            k,
            {
                "mesures": mesures,
                "consignes": {
                    "vitesse_pompe": 1.0,
                    "puissance_W": 1000.0,
                },
            },
        )

    k = 600

    mesures = {
        Variable.T: mesure_valide(k, Variable.T, 32.4),
        Variable.P: Mesure(
            k=k,
            t=float(k),
            horodatage_utc="2026-11-10T00:00:00Z",
            variable=Variable.P,
            valeur=None,
            statut=Statut.ABSENT,
        ),
        Variable.Q: mesure_valide(k, Variable.Q, 0.100),
    }

    sortie = ss3.etape(
        k,
        {
            "mesures": mesures,
            "consignes": {
                "vitesse_pompe": 1.0,
                "puissance_W": 1000.0,
            },
        },
    )

    assert sortie["residus"][Variable.P] is None
    assert sortie["residus"][Variable.T] is not None
    assert sortie["residus"][Variable.Q] is not None


def test_ss3_suit_une_nouvelle_consigne():
    ss3 = ReferenceBoucleOuverte()

    contexte = {
        "scenario": {
            "consignes_initiales": {
                "vitesse_pompe": 1.0,
                "puissance_W": 1000.0,
            }
        }
    }

    ss3.demarrer(contexte)

    for k in range(600):
        mesures = {
            Variable.T: mesure_valide(
                k,
                Variable.T,
                32.4 + 0.01 * ((k % 3) - 1),
            ),
            Variable.P: mesure_valide(
                k,
                Variable.P,
                0.108 + 0.0001 * ((k % 3) - 1),
            ),
            Variable.Q: mesure_valide(
                k,
                Variable.Q,
                0.100 + 0.0001 * ((k % 3) - 1),
            ),
        }

        ss3.etape(
            k,
            {
                "mesures": mesures,
                "consignes": {
                    "vitesse_pompe": 1.0,
                    "puissance_W": 1000.0,
                },
            },
        )

    mesures = {
        Variable.T: mesure_valide(600, Variable.T, 32.4),
        Variable.P: mesure_valide(600, Variable.P, 0.108),
        Variable.Q: mesure_valide(600, Variable.Q, 0.100),
    }

    sortie = ss3.etape(
        600,
        {
            "mesures": mesures,
            "consignes": {
                "vitesse_pompe": 0.8,
                "puissance_W": 800.0,
            },
        },
    )

    assert sortie["pret"] is True

    assert sortie["attendus"][Variable.P] is not None
    assert sortie["attendus"][Variable.Q] is not None