
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

def test_cu2_refus_present_dans_journal(tmp_path):
    """Vérifie le refus CU2 et sa journalisation dans SS-6."""
    import json
    import sqlite3

    from jumeau.orchestrateur import Orchestrateur
    from jumeau.ss6_journal import verifier_journal

    # Scénario utilisant les consignes officielles de SS-1.
    scenario = {
        "nom": "test_cu2_refus",
        "version": "0.1",
        "graine": 42,
        "cycles": 3,
        "consignes_initiales": {
            "vitesse_pompe": 1.0,
            "puissance_W": 1000.0,
        },
        "changements_consignes": [],
        "defauts": [
            {
                "type": "perte_communication",
                "variable": "P",
                "debut_s": 1,
                "duree_s": 0,
            }
        ],
    }

    sortie = tmp_path / "essai_cu2"

    # Exécuter la chaîne complète SS-1 à SS-6.
    Orchestrateur(
        scenario,
        sortie,
        silencieux=True,
    ).executer()

    chemin = sortie / "journal.sqlite"

    # Lire les événements réellement enregistrés par SS-6.
    with sqlite3.connect(chemin) as cx:
        lignes = cx.execute(
            "SELECT contenu FROM journal ORDER BY sequence"
        ).fetchall()

    evenements = [
        evenement
        for (contenu,) in lignes
        for evenement in json.loads(contenu)["evenements"]
    ]

    # Vérifier que le défaut invalide a été refusé.
    refus = [
        evenement
        for evenement in evenements
        if evenement["type"] == "defaut_refuse"
    ]

    assert len(refus) == 1
    assert refus[0]["index_defaut"] == 0
    assert refus[0]["motif"] == "duree_invalide"

    # Le défaut refusé ne doit jamais être injecté.
    injections = [
        evenement
        for evenement in evenements
        if evenement["type"] == "defaut_injecte"
    ]

    assert len(injections) == 0

    # Vérifier l'intégrité du journal SHA-256.
    integre, sequence_fautive, nombre = verifier_journal(chemin)

    assert integre is True
    assert sequence_fautive is None
    assert nombre == 3


@pytest.mark.parametrize(
    "defaut, motif_attendu",
    [
        (
            {
                "type": "derive",
                "variable": "T",
                "debut_s": -1,
                "pente_sigma_par_cycle": 0.01,
                "amplitude_max_pct_etendue": 2.5,
            },
            "debut_invalide",
        ),
        (
            {
                "type": "perte_communication",
                "variable": "P",
                "debut_s": 10,
                "duree_s": 0,
            },
            "duree_invalide",
        ),
        (
            {
                "type": "derive",
                "variable": "T",
                "debut_s": 10,
                "pente_sigma_par_cycle": -0.01,
                "amplitude_max_pct_etendue": 2.5,
            },
            "pente_invalide",
        ),
        (
            {
                "type": "saut",
                "variable": "Q",
                "debut_s": 10,
                "amplitude_sigma": float("nan"),
            },
            "amplitude_invalide",
        ),
    ],
)
def test_cu2_refuse_defaut_invalide(defaut, motif_attendu):
    """Vérifie le rejet des paramètres invalides (CU2)."""

    valide, motif = AcquisitionMesures.valider_defaut(defaut)

    assert valide is False
    assert motif == motif_attendu


def test_cu2_defaut_refuse_transmis_une_seule_fois():
    """Vérifie qu'un refus est transmis sans injecter le défaut."""

    defaut_invalide = {
        "type": "perte_communication",
        "variable": "P",
        "debut_s": 10,
        "duree_s": 0,
    }

    ss2 = AcquisitionMesures()

    ss2.demarrer({
        "graine": 42,
        "scenario": {
            "defauts": [defaut_invalide],
        },
    })

    entrees = {
        "grandeurs_vraies": {
            Variable.T: 60.0,
            Variable.P: 0.25,
            Variable.Q: 0.25,
        },
        "horodatage_utc": "2026-11-10T12:00:00Z",
    }

    resultat_0 = ss2.etape(0, entrees)
    resultat_1 = ss2.etape(1, entrees)

    refus_0 = [
        evenement
        for evenement in resultat_0["evenements"]
        if evenement["type"] == "defaut_refuse"
    ]

    refus_1 = [
        evenement
        for evenement in resultat_1["evenements"]
        if evenement["type"] == "defaut_refuse"
    ]

    assert len(refus_0) == 1
    assert refus_0[0]["motif"] == "duree_invalide"
    assert refus_1 == []

    # La pression reste valide : le défaut a été refusé.
    assert (
        resultat_0["mesures"][Variable.P].statut
        is Statut.VALIDE
    )
