from jumeau.contrat import Etat, Variable
from jumeau.ss4_decision import DecisionSequentielle


def test_derive_au_cycle_9(monkeypatch):
    monkeypatch.setattr("jumeau.ss4_decision.SEUIL_H", 9.0)
    decision = DecisionSequentielle()
    decision.demarrer({})

    entrees = {
        "pret": True,
        "residus": {Variable.T: 1.5, Variable.P: 0.0, Variable.Q: 0.0},
    }

    for cycle in range(1, 9):
        sortie = decision.etape(cycle, entrees)
        assert sortie["etat"] == Etat.NORMAL

    sortie = decision.etape(9, entrees)
    assert sortie["sommes"][Variable.T]["haut"] == 9.0
    assert sortie["etat"] == Etat.DERIVE

def test_incertain_apres_trois_residus_absents():
    decision = DecisionSequentielle()
    decision.demarrer({})

    residus = {Variable.T: 1.5, Variable.P: 0.0, Variable.Q: 0.0}
    entrees = {"pret": True, "residus": residus}

    # Cycle 1 : la température fait monter la somme à 1.0.
    sortie = decision.etape(1, entrees)
    sommes_attendues = {"haut": 1.0, "bas": 0.0}
    assert sortie["sommes"][Variable.T] == sommes_attendues

    # Cycles 2, 3 et 4 : seule la température manque.
    residus[Variable.T] = None
    for cycle, etat_attendu in [(2, Etat.NORMAL),
                                (3, Etat.NORMAL),
                                (4, Etat.INCERTAIN)]:
        sortie = decision.etape(cycle, entrees)
        assert sortie["sommes"][Variable.T] == sommes_attendues
        assert sortie["etat"] == etat_attendu