"""Architecture d'exécution retenue le 19 novembre : journal d'abord, cache ensuite,
confirmations de l'opérateur par une file d'attente (jumeau/etat_partage.py)."""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from jumeau.etat_partage import CacheEtat, FileConfirmations
from jumeau.orchestrateur import Orchestrateur
from jumeau.scenario import charger
from jumeau.ss6_journal import verifier_journal

SCENARIOS = Path(__file__).resolve().parent.parent / "scenarios"


def contenus(journal: Path) -> list[dict]:
    cx = sqlite3.connect(journal)
    lignes = [json.loads(c) for (c,) in cx.execute("SELECT contenu FROM journal ORDER BY sequence")]
    cx.close()
    return lignes


# ---------- Cache ----------

def test_le_cache_rend_des_copies():
    cache = CacheEtat()
    cache.publier({"k": 0, "etat": "normal"})
    vu = cache.dernier()
    vu["etat"] = "anomalie"
    assert cache.dernier()["etat"] == "normal", "l'interface ne peut pas modifier le cache"


def test_le_cache_garde_seulement_les_derniers_cycles():
    cache = CacheEtat(taille=10)
    for k in range(25):
        cache.publier({"k": k})
    assert len(cache) == 10
    assert [c["k"] for c in cache.historique()] == list(range(15, 25))
    assert [c["k"] for c in cache.historique(3)] == [22, 23, 24]


def test_le_cache_supporte_l_ecriture_et_la_lecture_en_parallele():
    cache = CacheEtat(taille=100)
    erreurs = []

    def lire():
        try:
            for _ in range(2000):
                cache.historique()
                cache.dernier()
        except Exception as e:  # pragma: no cover
            erreurs.append(e)

    lecteur = threading.Thread(target=lire)
    lecteur.start()
    for k in range(2000):
        cache.publier({"k": k})
    lecteur.join()
    assert not erreurs
    assert cache.dernier()["k"] == 1999


# ---------- File des confirmations ----------

def test_la_file_rend_les_reponses_dans_l_ordre_puis_se_vide():
    file = FileConfirmations()
    file.deposer({"decision": "confirme", "k_demande": 10})
    file.deposer({"decision": "refuse", "k_demande": 12})
    assert [r["decision"] for r in file.prendre_toutes()] == ["confirme", "refuse"]
    assert file.prendre_toutes() == []


# ---------- Orchestrateur ----------

def test_le_journal_d_abord_le_cache_ensuite(tmp_path):
    orch = Orchestrateur(charger(SCENARIOS / "nominal.json"), tmp_path / "essai", silencieux=True)
    orch.executer(50)
    dernier = orch.cache.dernier()
    journal = contenus(tmp_path / "essai" / "journal.sqlite")
    assert dernier["k"] == 49 and dernier["sequence"] == 49
    assert dernier["etat"] == journal[-1]["etat"], "le cache montre le cycle journalisé"
    assert len(orch.cache) == 50


def test_une_confirmation_est_journalisee_au_cycle_suivant(tmp_path):
    confirmations = FileConfirmations()
    orch = Orchestrateur(charger(SCENARIOS / "nominal.json"), tmp_path / "essai",
                         silencieux=True, confirmations=confirmations)

    class Operateur:
        """Simule l'interface : répond pendant le cycle 20."""
        nom = "SS-5"

        def __init__(self, ss5):
            self.ss5 = ss5

        def demarrer(self, contexte):
            self.ss5.demarrer(contexte)

        def etape(self, k, entrees):
            if k == 20:
                confirmations.deposer({"k_demande": 20, "decision": "confirme"})
            return self.ss5.etape(k, entrees)

        def arreter(self):
            self.ss5.arreter()

    orch.modules["ss5"] = Operateur(orch.modules["ss5"])
    orch.executer(25)
    journal = contenus(tmp_path / "essai" / "journal.sqlite")
    trouves = [(c["k"], e) for c in journal for e in c["evenements"] if e["type"] == "confirmation_operateur"]
    assert trouves == [(21, {"type": "confirmation_operateur", "k_demande": 20, "decision": "confirme"})]
    assert verifier_journal(tmp_path / "essai" / "journal.sqlite")[0]


def test_la_premiere_entree_contient_l_entete_de_l_essai(tmp_path):
    scenario = charger(SCENARIOS / "nominal.json")
    Orchestrateur(scenario, tmp_path / "essai", silencieux=True).executer(5)
    entete = [e for e in contenus(tmp_path / "essai" / "journal.sqlite")[0]["evenements"]
              if e["type"] == "entete_essai"]
    assert len(entete) == 1
    assert entete[0]["graine"] == scenario["graine"]
    assert entete[0]["python"] and "numpy" in entete[0]["bibliotheques"]
    assert len(entete[0]["empreinte_scenario"]) == 64


def test_le_journal_est_en_mode_wal_et_lisible_pendant_l_ecriture(tmp_path):
    from jumeau.ss6_journal import JournalDonnees

    journal = JournalDonnees()
    journal.demarrer({"sortie": tmp_path})
    for k in range(5):
        journal.etape(k, {"contenu": {"k": k}})
    # Un lecteur séparé (le scelleur, ou l'interface qui redémarre) voit déjà les 5 cycles.
    cache = CacheEtat()
    assert cache.recharger_depuis_journal(tmp_path / "journal.sqlite") == 5
    assert cache.dernier()["k"] == 4
    mode = journal.cx.execute("PRAGMA journal_mode").fetchone()[0]
    journal.arreter()
    assert mode == "wal"


def test_l_interface_qui_redemarre_retrouve_l_historique(tmp_path):
    orch = Orchestrateur(charger(SCENARIOS / "nominal.json"), tmp_path / "essai", silencieux=True)
    orch.executer(30)
    neuf = CacheEtat()
    assert neuf.recharger_depuis_journal(tmp_path / "essai" / "journal.sqlite") == 30
    assert neuf.dernier()["etat"] == orch.cache.dernier()["etat"]
    assert [c["k"] for c in neuf.historique()] == [c["k"] for c in orch.cache.historique()]
