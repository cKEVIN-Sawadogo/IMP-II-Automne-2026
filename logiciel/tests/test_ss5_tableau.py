"""Tests de l'interface web de SS-5 (session d'essai et rendu Dash).

Ils exécutent le jumeau complet au plus vite, sans navigateur : ils vérifient
que l'interface reçoit les sorties de chaque sous-système, que l'essai se
pilote (pause, arrêt) sans abîmer le journal, et que chaque page se construit.
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from jumeau.ss5_interface import tableau
from jumeau.ss5_interface.session import ARRETE, EN_COURS, PAUSE, TERMINE, Session, scenarios_disponibles

SCENARIOS = Path(__file__).resolve().parent.parent / "scenarios"


def executer(tmp_path, nom, cycles=None):
    session = Session(tmp_path)
    session.lancer(SCENARIOS / nom, vitesse=None, cycles=cycles)
    session._fil.join(timeout=60)
    return session


def test_les_scenarios_du_dossier_sont_proposes():
    fichiers = {s["fichier"] for s in scenarios_disponibles()}
    assert {"derive_lente.json", "nominal.json", "saut_franc.json"} <= fichiers


def test_la_session_enregistre_chaque_sous_systeme_a_chaque_cycle(tmp_path):
    session = executer(tmp_path, "derive_lente.json")
    inst = session.instantane(complet=True)
    assert session.statut == TERMINE
    assert inst["n"] == 2400
    for cle in ("vraie", "mesure", "attendu", "residu", "somme_haut"):
        assert all(len(serie) == 2400 for serie in inst[cle].values()), cle
    assert all(m["cycles"] == 2400 for m in inst["modules"].values())
    # La dérive de T injectée à 1 200 s est présentée, après le calage.
    assert [t["vers"] for t in inst["transitions"]] == ["incertain", "normal", "derive"]
    assert inst["transitions"][-1]["variables"] == ["T"] and inst["transitions"][-1]["k"] > 1200
    assert session.verifier_journal() == (True, None, 2400)


def test_le_saut_franc_est_presente_comme_une_anomalie(tmp_path):
    inst = executer(tmp_path, "saut_franc.json").instantane(complet=True)
    assert inst["etat"][-1] == "anomalie"
    assert inst["ss5"]["demande"]["etat"] == "anomalie"


def test_la_mesure_absente_n_est_jamais_tracee_comme_zero(tmp_path):
    inst = executer(tmp_path, "perte_communication.json", cycles=1300).instantane(complet=True)
    absentes = [i for i, s in enumerate(inst["statut_mesure"]["P"]) if s == "absent"]
    assert absentes and all(inst["mesure"]["P"][i] is None for i in absentes)


def test_pause_puis_arret_laissent_un_journal_integre(tmp_path):
    session = Session(tmp_path)
    session.lancer(SCENARIOS / "nominal.json", vitesse=200.0)
    time.sleep(0.3)
    session.mettre_en_pause()
    assert session.statut == PAUSE
    n = len(session.k)
    time.sleep(0.3)
    assert len(session.k) <= n + 1  # au plus le cycle en cours
    session.reprendre()
    assert session.statut == EN_COURS
    session.arreter(attendre=True)
    assert session.statut == ARRETE
    integre, _, entrees = session.verifier_journal()
    assert integre and entrees == len(session.k) > 0


def test_la_reponse_sans_essai_en_cours_est_refusee(tmp_path):
    assert Session(tmp_path).repondre("confirme") == "Aucun essai en cours."


def test_les_quatre_etats_ont_des_symboles_distincts():
    assert len(set(tableau.SYMBOLES_SVG.values())) == 4
    assert len(set(tableau.FORMES.values())) == 4


@pytest.mark.parametrize("nom", ["derive_lente.json", "perte_communication.json", "hors_plage.json"])
def test_chaque_page_se_construit(tmp_path, nom):
    session = executer(tmp_path, nom)
    app = tableau.creer_application(session)
    assert app.layout is not None
    inst = session.instantane(complet=True)
    sorties = tableau._rendre_conduite(session.instantane(), inst, detail_ouvert=True)
    assert len(sorties) == 21
    modules, classes = tableau._rendre_modules(inst)
    assert len(modules) == len(classes) == 6
    tableau._rendre_journal(inst, None)
    for figure in (tableau.figure_grandeurs, tableau.figure_residus, tableau.figure_sommes,
                   tableau.figure_chronologie):
        assert figure(inst).data


def test_les_pages_se_construisent_avant_le_premier_essai(tmp_path):
    session = Session(tmp_path)
    tableau.creer_application(session)
    inst = session.instantane()
    assert len(tableau._rendre_conduite(inst, inst, detail_ouvert=True)) == 21
    tableau._rendre_modules(inst)
    tableau._rendre_journal(inst, None)


def test_chaque_evenement_est_decrit_en_francais(tmp_path):
    inst = executer(tmp_path, "hors_plage.json").instantane(complet=True)
    categories = {tableau._decrire_evenement(e)[0] for e in inst["evenements"]}
    assert "Autre" not in categories
    assert {"Défaut injecté", "Mesure", "État", "Référence"} <= categories


def test_l_heure_affichee_est_celle_de_l_est_du_canada():
    from datetime import datetime, timezone
    # Le journal est en UTC ; l'affichage est en heure de l'Est (UTC-5 l'hiver, UTC-4 l'été).
    assert tableau._heure("2026-11-20T05:00:00.000+00:00") == "00:00:00"
    assert tableau._heure("2026-07-01T16:00:00.000+00:00") == "12:00:00"
    assert tableau._sigle(datetime(2026, 11, 20, 12, tzinfo=timezone.utc)) == "HNE"
    assert tableau._sigle(datetime(2026, 7, 1, 12, tzinfo=timezone.utc)) == "HAE"


def test_l_axe_du_temps_couvre_tout_le_scenario(tmp_path):
    session = executer(tmp_path, "saut_franc.json", cycles=300)
    inst = session.instantane(complet=True)
    for figure in (tableau.figure_grandeurs, tableau.figure_residus, tableau.figure_sommes):
        assert list(figure(inst).layout.xaxis.range) == [0, 300]


def _texte(span) -> str:
    return span.children if isinstance(span.children, str) else str(span.children)


def test_un_essai_en_pause_n_est_pas_annonce_comme_altere(tmp_path):
    # Pendant l'essai, les dernières entrées attendent le prochain sceau (tous les
    # 60 cycles) : la chaîne est intacte, l'interface ne doit pas crier à l'altération.
    session = Session(tmp_path)
    session.lancer(SCENARIOS / "nominal.json", vitesse=None)
    while len(session.k) < 200:
        time.sleep(0.01)
    session.mettre_en_pause()
    time.sleep(0.2)
    message = tableau._message_verification(session.rapport_journal(), en_cours=session.actif)
    session.arreter(attendre=True)
    assert "intacte" in _texte(message) and message.className == "ok"


def test_une_entree_modifiee_est_annoncee_comme_alteree(tmp_path):
    import sqlite3
    session = executer(tmp_path, "derive_lente.json", cycles=130)
    assert "sceau final présent" in _texte(tableau._message_verification(session.rapport_journal(), False))
    cx = sqlite3.connect(session.sortie / "journal.sqlite")
    cx.execute("UPDATE journal SET contenu = replace(contenu, 'incertain', 'normal') WHERE sequence = 100")
    cx.commit()
    cx.close()
    message = tableau._message_verification(session.rapport_journal(), en_cours=False)
    assert "altéré" in _texte(message) and message.className == "ko"
