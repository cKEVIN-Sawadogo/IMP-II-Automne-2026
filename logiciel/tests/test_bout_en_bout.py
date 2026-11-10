"""Test de bout en bout : toute demande de fusion doit le réussir.

Il vérifie que la chaîne complète tourne avec les modules actuels, que le
journal est complet et intègre, et que chaque scénario d'EX-F-02 produit
l'état attendu. Il ne juge pas les performances statistiques (taux de
fausses alarmes, délai moyen) : c'est le rôle de la campagne d'essais.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from jumeau.contrat import N_INCERTAIN
from jumeau.orchestrateur import Orchestrateur
from jumeau.scenario import charger
from jumeau.ss6_journal import verifier_journal

SCENARIOS = Path(__file__).resolve().parent.parent / "scenarios"


def executer(nom: str, dossier: Path, cycles: int | None = None) -> tuple[dict, Path]:
    scenario = charger(SCENARIOS / f"{nom}.json")
    sortie = dossier / nom
    resume = Orchestrateur(scenario, sortie, silencieux=True).executer(cycles)
    return resume, sortie / "journal.sqlite"


def entrees(journal: Path) -> list[dict]:
    cx = sqlite3.connect(journal)
    lignes = [json.loads(c) for (c,) in cx.execute("SELECT contenu FROM journal ORDER BY sequence")]
    cx.close()
    return lignes


def premier(resume: dict, etat: str) -> int | None:
    return next((c["k"] for c in resume["changements_etat"] if c["vers"] == etat), None)


@pytest.mark.parametrize("nom", ["nominal", "derive_lente", "perte_communication", "hors_plage", "saut_franc"])
def test_chaine_complete_et_journal_integre(nom, tmp_path):
    resume, journal = executer(nom, tmp_path, cycles=700)
    integre, fautive, n = verifier_journal(journal)
    assert integre, f"chaîne rompue à l'entrée {fautive}"
    assert n == 700, "une entrée au journal par cycle (EX-Q-02)"
    assert (journal.parent / "verite.csv").exists()


def test_derive_lente_detectee_sur_la_temperature(tmp_path):
    resume, _ = executer("derive_lente", tmp_path)
    k = premier(resume, "derive")
    assert k is not None and 1200 <= k <= 1500
    assert "T" in next(c["variables"] for c in resume["changements_etat"] if c["vers"] == "derive")


def test_perte_de_communication_donne_incertain_au_troisieme_cycle(tmp_path):
    resume, _ = executer("perte_communication", tmp_path)
    assert premier(resume, "incertain") is not None
    k = [c["k"] for c in resume["changements_etat"] if c["vers"] == "incertain"][-1]
    assert k == 1200 + N_INCERTAIN - 1
    assert resume["etat_final"] == "normal", "retour à la normale après la coupure"


def test_valeur_hors_plage_rejetee_et_journalisee(tmp_path):
    _, journal = executer("hors_plage", tmp_path, cycles=1215)
    lignes = entrees(journal)
    cycle = lignes[1200]
    q = next(m for m in cycle["mesures"] if m["variable"] == "Q")
    assert q["statut"] == "hors_plage" and q["valeur"] is None, "valeur non propagée (EX-Q-04)"
    assert any(e["type"] == "mesure_rejetee" for e in cycle["evenements"])
    assert cycle["residus"]["Q"] is None


def test_saut_franc_donne_anomalie(tmp_path):
    resume, _ = executer("saut_franc", tmp_path)
    assert premier(resume, "anomalie") == 1200


def test_journal_altere_est_detecte(tmp_path):
    _, journal = executer("nominal", tmp_path, cycles=50)
    cx = sqlite3.connect(journal)
    # Modification après coup d'une seule entrée, même d'un seul caractère.
    cx.execute("UPDATE journal SET contenu = contenu || ' ' WHERE sequence = 20")
    cx.commit()
    cx.close()
    integre, fautive, _ = verifier_journal(journal)
    assert not integre and fautive == 20


def test_meme_graine_meme_resultat(tmp_path):
    a, _ = executer("derive_lente", tmp_path / "a")
    b, _ = executer("derive_lente", tmp_path / "b")
    assert a["changements_etat"] == b["changements_etat"], "reproductibilité (EX-F-02)"
