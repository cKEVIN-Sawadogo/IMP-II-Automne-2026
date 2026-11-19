"""Tests spécifiques au sous-système SS-5.

Présentation par état : affichage des quatre états à partir d'états produits
à la main, vue de détail, demande de confirmation et journalisation de la
réponse de l'opérateur (EX-F-04, EX-F-05, EX-F-08, EX-F-09).
"""
from __future__ import annotations

import ast
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from jumeau.contrat import Etat, Mesure, Statut, Variable
from jumeau.ss5_interface import LIBELLES, LIBELLES_VARIABLES, SYMBOLES, PresentationEtat
from jumeau.ss5_interface import demo
from jumeau.ss6_journal import JournalDonnees, verifier_journal

ATTENDUS = {Variable.T: 60.0, Variable.P: 0.25, Variable.Q: 0.25}


def creer_ss5():
    ss5 = PresentationEtat()
    ss5.demarrer({"silencieux": True})
    return ss5


def mesures(k=0, valeurs=None, absentes=()):
    valeurs = {**ATTENDUS, **(valeurs or {})}
    h = f"2026-11-12T12:00:{k:02d}Z"
    return {v: (Mesure(k, float(k), h, v, None, Statut.ABSENT) if v in absentes
                else Mesure(k, float(k), h, v, valeurs[v], Statut.VALIDE)) for v in Variable}


def entrees(etat, contributrices=(), confiance=1.0, k=0, **kw):
    return {"etat": etat, "confiance": confiance, "contributrices": list(contributrices),
            "mesures": mesures(k, **kw), "attendus": ATTENDUS}


# ----- Affichage des quatre états (test attendu au rapport, section 2.5) ---

@pytest.mark.parametrize("etat", list(Etat))
def test_chaque_etat_produit_a_la_main_est_affiche(etat):
    ss5 = creer_ss5()
    sortie = ss5.etape(1, entrees(etat, [Variable.T] if etat is not Etat.NORMAL else []))
    assert SYMBOLES[etat] in sortie["affichage"]
    assert LIBELLES[etat] in sortie["affichage"]
    assert ss5.etat_affiche is etat


def test_les_quatre_etats_restent_distincts_sans_couleur():
    assert len(set(SYMBOLES.values())) == 4
    assert len(set(LIBELLES.values())) == 4


def test_le_changement_d_etat_est_affiche_au_cycle_meme():
    ss5 = creer_ss5()
    sequence = [Etat.NORMAL, Etat.NORMAL, Etat.DERIVE, Etat.DERIVE, Etat.INCERTAIN]
    for k, etat in enumerate(sequence, start=1):
        ss5.etape(k, entrees(etat, k=k))
        assert ss5.etat_affiche is etat
    assert [k for k, _ in ss5.historique] == [1, 3, 5]


def test_un_etat_inchange_n_est_pas_reaffiche():
    ss5 = creer_ss5()
    ss5.etape(1, entrees(Etat.NORMAL))
    assert ss5.etape(2, entrees(Etat.NORMAL, k=2))["affichage"] == ""


def test_le_bandeau_affiche_les_trois_variables_et_leur_ecart():
    ss5 = creer_ss5()
    texte = ss5.etape(60, entrees(Etat.NORMAL, k=0, valeurs={Variable.T: 61.0}))["affichage"]
    assert "T=61 °C (écart +1)" in texte and "P=" in texte and "Q=" in texte


# ----- Vue de détail (CU4, EX-F-05) -----------------------------------------

def test_la_vue_de_detail_met_en_evidence_les_variables_designees():
    ss5 = creer_ss5()
    e = entrees(Etat.ANOMALIE, [Variable.Q], valeurs={Variable.Q: 0.40})
    ss5.etape(1, e)
    detail = ss5.vue_detail()
    assert ">> débit supérieur à l'attendu" in detail
    assert ">> température" not in detail


def test_sans_variable_designee_la_mention_est_affichee():
    ss5 = creer_ss5()
    ss5.etape(1, entrees(Etat.DERIVE, []))
    assert "aucune variable désignée" in ss5.vue_detail()
    assert "aucune variable désignée" in ss5.vue_permanente(1, entrees(Etat.DERIVE, []))


def test_une_mesure_absente_donne_l_horodatage_de_la_derniere_acquisition_valide():
    ss5 = creer_ss5()
    ss5.etape(1, entrees(Etat.NORMAL, k=1))
    ss5.etape(2, entrees(Etat.INCERTAIN, [Variable.P], k=2, absentes=(Variable.P,)))
    detail = ss5.vue_detail()
    assert "pression : mesure absente" in detail
    assert "dernière acquisition valide : 2026-11-12T12:00:01Z" in detail


def test_tous_les_libelles_viennent_de_la_liste_fermee():
    ss5 = creer_ss5()
    cas = [entrees(Etat.NORMAL), entrees(Etat.DERIVE, [Variable.T], valeurs={Variable.T: 62.0}),
           entrees(Etat.ANOMALIE, [Variable.P], valeurs={Variable.P: 0.1}),
           entrees(Etat.INCERTAIN, [Variable.Q], absentes=(Variable.Q,))]
    for k, e in enumerate(cas, start=1):
        ss5.etape(k, e)
        for ligne in ss5.vue_detail().splitlines()[1:]:
            libelle = ligne.strip().lstrip(">").strip().split(" : ")[0]
            if libelle == "aucune variable désignée":
                continue
            assert any(l.startswith(libelle) for l in LIBELLES_VARIABLES), ligne


# ----- Confirmation et journal (CU5, EX-F-09) ---------------------------------

@pytest.mark.parametrize("etat,attendu", [(Etat.DERIVE, True), (Etat.ANOMALIE, True),
                                          (Etat.NORMAL, False), (Etat.INCERTAIN, False)])
def test_une_confirmation_est_demandee_pour_derive_et_anomalie(etat, attendu):
    ss5 = creer_ss5()
    evenements = ss5.etape(1, entrees(etat, [Variable.T]))["evenements"]
    assert any(e["type"] == "demande_confirmation" for e in evenements) is attendu


def test_la_reponse_de_l_operateur_arrive_au_journal_avec_son_instantane(tmp_path):
    ss5, ss6 = creer_ss5(), JournalDonnees()
    ss6.demarrer({"sortie": str(tmp_path)})
    ss5.etape(1, entrees(Etat.DERIVE, [Variable.T], valeurs={Variable.T: 61.0}))
    ss5.repondre("confirme")
    sortie = ss5.etape(2, entrees(Etat.DERIVE, [Variable.T], k=2, valeurs={Variable.T: 61.2}))
    ss6.etape(2, {"contenu": {"k": 2, "evenements": sortie["evenements"]}})
    ss6.arreter()

    integre, _, n = verifier_journal(tmp_path / "journal.sqlite")
    assert integre and n == 1
    cx = sqlite3.connect(tmp_path / "journal.sqlite")
    (contenu,) = cx.execute("SELECT contenu FROM journal").fetchone()
    cx.close()
    reponse = next(e for e in json.loads(contenu)["evenements"] if e["type"] == "reponse_operateur")
    assert reponse["reponse"] == "confirme" and reponse["etat"] == "derive" and reponse["variables"] == ["T"]
    assert reponse["severite"] == "non_critique"
    assert reponse["empreinte_instantane"] == hashlib.sha256(reponse["instantane"].encode("utf-8")).hexdigest()
    assert "[~] DÉRIVE" in reponse["instantane"]


def test_sans_reponse_la_demande_reste_en_attente_et_rien_n_est_journalise():
    ss5 = creer_ss5()
    ss5.etape(1, entrees(Etat.ANOMALIE, [Variable.Q]))
    for k in range(2, 10):
        evenements = ss5.etape(k, entrees(Etat.ANOMALIE, [Variable.Q], k=k))["evenements"]
        assert not any(e["type"] == "reponse_operateur" for e in evenements)
    assert ss5.demande is not None


def test_la_demande_est_retiree_si_l_etat_change_avant_la_reponse():
    ss5 = creer_ss5()
    ss5.etape(1, entrees(Etat.DERIVE, [Variable.T]))
    evenements = ss5.etape(2, entrees(Etat.NORMAL, k=2))["evenements"]
    assert [e["type"] for e in evenements] == ["demande_confirmation_retiree"]
    assert ss5.demande is None


# ----- Sévérité : demande réservée aux états non critiques (D2) --------------

def test_la_demande_porte_la_severite_non_critique():
    ss5 = creer_ss5()
    evenements = ss5.etape(1, entrees(Etat.DERIVE, [Variable.T], valeurs={Variable.T: 60.5}))["evenements"]
    demande = next(e for e in evenements if e["type"] == "demande_confirmation")
    assert demande["severite"] == "non_critique"
    assert demande["biais_fraction_etendue"]["T"] == pytest.approx(0.005)


def test_une_anomalie_critique_ne_donne_aucune_demande_et_est_journalisee():
    ss5 = creer_ss5()
    # Écart de 0,15 kg/s sur une étendue de 0,5 kg/s : 30 %, bien au-delà de 2,5 %.
    evenements = ss5.etape(1, entrees(Etat.ANOMALIE, [Variable.Q], valeurs={Variable.Q: 0.40}))["evenements"]
    assert [e["type"] for e in evenements] == ["etat_critique"]
    assert evenements[0]["variables"] == ["Q"]
    assert ss5.demande is None
    with pytest.raises(ValueError):
        ss5.repondre("confirme")


def test_le_seuil_de_criticite_est_a_2_5_pourcent_de_l_etendue():
    # Étendue de T : 100 °C. Un biais de 2,4 °C est non critique, 2,5 °C est critique.
    for ecart, attendu in [(2.4, "demande_confirmation"), (2.5, "etat_critique")]:
        ss5 = creer_ss5()
        evenements = ss5.etape(1, entrees(Etat.DERIVE, [Variable.T], valeurs={Variable.T: 60.0 + ecart}))
        assert [e["type"] for e in evenements["evenements"]] == [attendu]


def test_la_demande_est_retiree_si_l_etat_devient_critique_avant_la_reponse():
    ss5 = creer_ss5()
    ss5.etape(1, entrees(Etat.DERIVE, [Variable.T], valeurs={Variable.T: 60.5}))
    evenements = ss5.etape(2, entrees(Etat.DERIVE, [Variable.T], k=2, valeurs={Variable.T: 70.0}))["evenements"]
    assert [(e["type"], e["motif"]) for e in evenements] == [("demande_confirmation_retiree", "etat_critique")]
    assert ss5.demande is None


def test_repondre_sans_demande_en_cours_est_refuse():
    with pytest.raises(ValueError):
        creer_ss5().repondre("confirme")


def test_une_reponse_hors_liste_est_refusee():
    ss5 = creer_ss5()
    ss5.etape(1, entrees(Etat.DERIVE, [Variable.T]))
    with pytest.raises(ValueError):
        ss5.repondre("oui")


# ----- Aucune sortie vers l'installation (EX-F-08) ---------------------------

def test_ss5_ne_renvoie_que_l_affichage_et_les_evenements():
    ss5 = creer_ss5()
    for k, etat in enumerate(Etat):
        assert set(ss5.etape(k, entrees(etat, [Variable.T], k=k))) == {"affichage", "evenements"}


def test_ss5_n_importe_aucun_module_de_communication():
    dossier = Path(__file__).resolve().parent.parent / "jumeau" / "ss5_interface"
    interdits = {"socket", "serial", "requests", "urllib", "http", "subprocess", "pymodbus", "opcua", "paho"}
    for fichier in dossier.glob("*.py"):
        arbre = ast.parse(fichier.read_text(encoding="utf-8"))
        for noeud in ast.walk(arbre):
            if isinstance(noeud, (ast.Import, ast.ImportFrom)):
                noms = [a.name for a in noeud.names] if isinstance(noeud, ast.Import) else [noeud.module or ""]
                for nom in noms:
                    assert nom.split(".")[0] not in interdits, f"{fichier.name} importe {nom}"


# ----- Démonstration de bout en bout -----------------------------------------

def test_la_demonstration_reussit_toutes_ses_verifications(tmp_path):
    resultat = demo.executer(tmp_path / "demo", silencieux=True)
    echecs = [cle for cle, valeur in resultat.items() if not cle.startswith("_") and not valeur]
    assert not echecs, echecs
