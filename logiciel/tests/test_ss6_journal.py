"""Tests de SS-6 : journal chaîné, scelleur séparé et vérificateur (issue #90).

Deux parties :
  - SS-6 seul : on donne directement des cycles à JournalDonnees, puis on
    « triche » sur le journal ou les sceaux pour voir si le vérificateur le voit ;
  - dans la chaîne : le vrai orchestrateur fait tourner SS-1 à SS-6, et
    lancer.py est appelé comme on le fait en vrai.
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

from jumeau.etat_partage import FileConfirmations
from jumeau.orchestrateur import Orchestrateur
from jumeau.scenario import charger
from jumeau.ss6_journal import JournalDonnees, verifier, verifier_journal
from jumeau.ss6_journal.ecrivain import EMPREINTE_INITIALE, _empreinte
from jumeau.ss6_journal.scelleur import NOM_CLE_PRIVEE, message_sceau

LOGICIEL = Path(__file__).resolve().parent.parent
SCENARIOS = LOGICIEL / "scenarios"
DOSSIER_SS6 = LOGICIEL / "jumeau" / "ss6_journal"


# ---------------------------------------------------------------------------
# Outils
# ---------------------------------------------------------------------------

def ecrire_essai(dossier, cycles=130):
    """SS-6 seul : un cycle par seconde simulée, un changement d'état au cycle 100."""
    ss6 = JournalDonnees()
    ss6.demarrer({"sortie": dossier})
    for k in range(cycles):
        etat = "incertain" if k < 100 else "normal"
        evenements = []
        if k in (0, 100):
            evenements.append({"type": "changement_etat", "de": None if k == 0 else "incertain",
                               "vers": etat, "variables": []})
        ss6.etape(k, {"contenu": {"k": k, "etat": etat, "evenements": evenements}})
    ss6.arreter()
    return dossier


def lire(dossier):
    cx = sqlite3.connect(Path(dossier) / "journal.sqlite")
    lignes = cx.execute("SELECT k, contenu FROM journal ORDER BY sequence").fetchall()
    cx.close()
    return [(k, json.loads(c)) for k, c in lignes]


def copier(source, nom):
    """Copie un essai pour le modifier sans toucher l'original (les clés restent partagées)."""
    cible = Path(source).parent / nom
    shutil.copytree(source, cible)
    return cible


def executer_sql(base, requete, *parametres):
    cx = sqlite3.connect(base)
    cx.execute(requete, parametres)
    cx.commit()
    cx.close()


def modifier_entree(dossier, seq):
    executer_sql(Path(dossier) / "journal.sqlite",
                 "UPDATE journal SET contenu = contenu || ' ' WHERE sequence = ?", seq)


def supprimer_entree(dossier, seq):
    executer_sql(Path(dossier) / "journal.sqlite", "DELETE FROM journal WHERE sequence = ?", seq)


def refaire_chaine(dossier):
    """Le tricheur connaît SHA-256 : il recalcule toutes les empreintes après sa modification."""
    cx = sqlite3.connect(Path(dossier) / "journal.sqlite")
    precedente = EMPREINTE_INITIALE
    for seq, contenu in cx.execute("SELECT sequence, contenu FROM journal ORDER BY sequence").fetchall():
        emp = _empreinte(precedente, contenu)
        cx.execute("UPDATE journal SET empreinte_precedente = ?, empreinte = ? WHERE sequence = ?",
                   (precedente, emp, seq))
        precedente = emp
    cx.commit()
    cx.close()


# ---------------------------------------------------------------------------
# SS-6 seul
# ---------------------------------------------------------------------------

def test_journal_intact_accepte(tmp_path):
    r = verifier(ecrire_essai(tmp_path / "essai"), cycles_attendus=130)
    assert r.valide, r.texte()
    assert r.sceaux == 3, "sceaux aux entrées 59 et 119, puis le sceau final"
    assert r.sceau_final
    assert (tmp_path / "essai" / "sceaux.sqlite").exists()


def test_entree_modifiee_detectee(tmp_path):
    dossier = ecrire_essai(tmp_path / "essai")
    modifier_entree(dossier, 20)
    assert verifier_journal(dossier / "journal.sqlite") == (False, 20, 130)


def test_entree_modifiee_et_chaine_refaite_detectee_par_les_sceaux(tmp_path):
    dossier = ecrire_essai(tmp_path / "essai")
    modifier_entree(dossier, 20)
    refaire_chaine(dossier)
    r = verifier(dossier)
    assert not r.integre
    assert r.sceaux_rejetes == 0, "les signatures sont bonnes, c'est le journal qui a changé"
    assert r.anomalies[0][1] == "sceau 0 : empreinte du bloc seq 0-59 ne correspond pas au journal"


def test_entree_supprimee_detectee(tmp_path):
    dossier = ecrire_essai(tmp_path / "essai")
    supprimer_entree(dossier, 50)
    integre, fautive, n = verifier_journal(dossier / "journal.sqlite")
    assert not integre and fautive == 50 and n == 129


def test_faux_sceaux_rejetes(tmp_path):
    """Sans la clé privée, impossible de refaire des sceaux valides."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    dossier = ecrire_essai(tmp_path / "essai")
    modifier_entree(dossier, 20)
    refaire_chaine(dossier)
    autre_cle = Ed25519PrivateKey.generate()
    cx = sqlite3.connect(dossier / "journal.sqlite")
    empreintes = dict(cx.execute("SELECT sequence, empreinte FROM journal").fetchall())
    cx.close()
    cx = sqlite3.connect(dossier / "sceaux.sqlite")
    for numero, debut, fin, final, heure in cx.execute(
            "SELECT numero, seq_debut, seq_fin, final, horodatage FROM sceaux").fetchall():
        emp = empreintes[fin]
        signature = autre_cle.sign(message_sceau(numero, debut, fin, emp, final, heure)).hex()
        cx.execute("UPDATE sceaux SET empreinte = ?, signature = ? WHERE numero = ?", (emp, signature, numero))
    cx.commit()
    cx.close()
    r = verifier(dossier)
    assert r.sceaux_rejetes == r.sceaux == 3


def test_sceau_final_retire_est_signale(tmp_path):
    dossier = ecrire_essai(tmp_path / "essai")
    executer_sql(dossier / "sceaux.sqlite", "DELETE FROM sceaux WHERE final = 1")
    r = verifier(dossier)
    assert not r.sceau_final and not r.integre
    assert ("sceau final absent (arrêt non contrôlé)" in [m for _, m in r.anomalies])


def test_seul_le_scelleur_charge_la_cle_privee():
    """L'écrivain et le vérificateur n'utilisent jamais la clé privée."""
    for nom in ("ecrivain.py", "verificateur.py", "__init__.py"):
        code = (DOSSIER_SS6 / nom).read_text(encoding="utf-8")
        assert NOM_CLE_PRIVEE not in code and "NOM_CLE_PRIVEE" not in code, nom
        assert "load_pem_private_key" not in code, nom
    scelleur = ast.parse((DOSSIER_SS6 / "scelleur.py").read_text(encoding="utf-8"))
    imports = {n.module or "" for n in ast.walk(scelleur) if isinstance(n, ast.ImportFrom)}
    assert not any(m.startswith("jumeau") for m in imports), "le scelleur tourne seul"


def test_le_scelleur_tourne_dans_un_autre_processus(tmp_path):
    ss6 = JournalDonnees()
    ss6.demarrer({"sortie": tmp_path / "essai"})
    try:
        assert ss6.scelleur.proc.pid != os.getpid()
        assert ss6.scelleur.proc.poll() is None, "le scelleur attend ses ordres"
    finally:
        ss6.arreter()


def test_un_journal_existant_n_est_jamais_ecrase(tmp_path):
    ecrire_essai(tmp_path / "essai", cycles=3)
    with pytest.raises(FileExistsError):
        JournalDonnees().demarrer({"sortie": tmp_path / "essai"})


# ---------------------------------------------------------------------------
# Dans la chaîne (vrai orchestrateur, SS-1 à SS-6)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def essai_nominal(tmp_path_factory):
    dossier = tmp_path_factory.mktemp("chaine") / "nominal"
    Orchestrateur(charger(SCENARIOS / "nominal.json"), dossier, silencieux=True).executer(700)
    return dossier


def test_chaine_journal_intact_et_scelle(essai_nominal):
    r = verifier(essai_nominal, cycles_attendus=700)
    assert r.valide, r.texte()
    assert r.sceaux == 700 // 60 + 1, "11 sceaux réguliers, plus le sceau final"
    assert r.sceau_final


def test_chaine_une_entree_cycle_par_cycle(essai_nominal):
    entrees = lire(essai_nominal)
    assert [k for k, _ in entrees] == list(range(700))
    assert all(contenu["k"] == k for k, contenu in entrees)


def test_chaine_entree_modifiee_ou_supprimee_detectee(essai_nominal):
    modifiee = copier(essai_nominal, "modifiee")
    modifier_entree(modifiee, 300)
    assert verifier_journal(modifiee / "journal.sqlite")[:2] == (False, 300)

    supprimee = copier(essai_nominal, "supprimee")
    supprimer_entree(supprimee, 300)
    assert verifier_journal(supprimee / "journal.sqlite")[:2] == (False, 300)


def cycle_du_changement(entrees):
    """Premier cycle où l'état change (après l'état de départ du cycle 0)."""
    for (_, avant), (k, apres) in zip(entrees, entrees[1:]):
        if apres["etat"] != avant["etat"]:
            return k
    return None


def test_chaine_transitions_d_etat_journalisees(essai_nominal):
    """La fin du calage (incertain → normal) est au journal, au cycle même (EX-F-10)."""
    r = verifier(essai_nominal)
    assert r.transitions == r.changements == 1
    entrees = lire(essai_nominal)
    k = cycle_du_changement(entrees)
    assert k is not None and 590 <= k <= 610, "fin du calage de SS-3 vers le cycle 600"
    contenu = entrees[k][1]
    changement = next(e for e in contenu["evenements"] if e["type"] == "changement_etat")
    assert (changement["de"], changement["vers"]) == ("incertain", "normal")


def test_chaine_changement_d_etat_efface_est_signale(essai_nominal):
    dossier = copier(essai_nominal, "changement_efface")
    k = cycle_du_changement(lire(dossier))
    cx = sqlite3.connect(dossier / "journal.sqlite")
    (contenu,) = cx.execute("SELECT contenu FROM journal WHERE k = ?", (k,)).fetchone()
    donnees = json.loads(contenu)
    donnees["evenements"] = [e for e in donnees["evenements"] if e["type"] != "changement_etat"]
    cx.execute("UPDATE journal SET contenu = ? WHERE k = ?",
               (json.dumps(donnees, ensure_ascii=False, sort_keys=True), k))
    cx.commit()
    cx.close()
    refaire_chaine(dossier)   # même si le tricheur refait la chaîne...
    r = verifier(dossier)
    assert not r.integre, "... les sceaux le trahissent"
    assert any("sans événement changement_etat" in m for _, m in r.manques)


class OperateurSimule:
    """Remplace l'interface : dépose une réponse dans la file pendant un cycle
    donné (même principe que dans test_etat_partage.py)."""
    nom = "SS-5"

    def __init__(self, ss5, file, k_depot, reponse):
        self.ss5, self.file, self.k_depot, self.reponse = ss5, file, k_depot, reponse

    def __getattr__(self, attribut):   # demande, repondre : ceux du vrai SS-5
        return getattr(self.ss5, attribut)

    def demarrer(self, contexte):
        self.ss5.demarrer(contexte)

    def etape(self, k, entrees):
        sortie = self.ss5.etape(k, entrees)
        if k == self.k_depot:
            self.file.deposer(self.reponse)
        return sortie

    def arreter(self):
        self.ss5.arreter()


def test_chaine_confirmation_de_l_operateur_journalisee(tmp_path):
    """Saut franc : demande au cycle 1200, réponse déposée au cycle 1205 dans la file
    (format convenu : k_demande et decision), journalisée au cycle 1206 (EX-F-09)."""
    confirmations = FileConfirmations()
    dossier = tmp_path / "saut_franc"
    orch = Orchestrateur(charger(SCENARIOS / "saut_franc.json"), dossier,
                         silencieux=True, confirmations=confirmations)
    orch.modules["ss5"] = OperateurSimule(orch.modules["ss5"], confirmations, 1205,
                                          {"k_demande": 1200, "decision": "confirme"})
    orch.executer(1210)

    r = verifier(dossier, cycles_attendus=1210)
    assert r.valide, r.texte()
    assert r.confirmations == 1 and r.reponses == 1
    assert r.transitions >= 1 and r.transitions == r.changements
    k, contenu = lire(dossier)[1206]
    types = [e["type"] for e in contenu["evenements"]]
    assert types[:2] == ["confirmation_operateur", "reponse_operateur"]
    recue = contenu["evenements"][0]
    assert recue["k_demande"] == 1200 and recue["decision"] == "confirme"


def lancer(*arguments, **options):
    return subprocess.run([sys.executable, str(LOGICIEL / "lancer.py"), *map(str, arguments)],
                          cwd=LOGICIEL, capture_output=True, text=True, encoding="utf-8", **options)


def test_lancer_verifier(essai_nominal):
    """python lancer.py --verifier : 0 si le journal est intègre, 1 sinon, 2 s'il n'existe pas."""
    bon = lancer("--verifier", essai_nominal / "journal.sqlite")
    assert bon.returncode == 0, bon.stdout + bon.stderr
    assert "Verdict : INTÈGRE" in bon.stdout
    assert lancer("--verifier", essai_nominal).returncode == 0, "le dossier de l'essai marche aussi"

    modifiee = copier(essai_nominal, "pour_lancer")
    modifier_entree(modifiee, 5)
    mauvais = lancer("--verifier", modifiee)
    assert mauvais.returncode == 1
    assert "ALTÉRÉ" in mauvais.stdout and "seq 5" in mauvais.stdout

    assert lancer("--verifier", essai_nominal / "absent").returncode == 2


def test_lancer_un_scenario_marche_toujours(tmp_path):
    """Les options existantes ne changent pas."""
    sortie = tmp_path / "essai"
    p = lancer(SCENARIOS / "nominal.json", "--cycles", 70, "--silencieux", "--tolerant", "--sortie", sortie)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "70 entrées au journal, 2 sceaux (intègre)" in p.stdout
    assert verifier(sortie, cycles_attendus=70).valide


@pytest.mark.skipif(sys.platform == "win32", reason="arrêt brutal testé sous Linux (GitHub Actions) et macOS")
def test_chaine_arret_brutal_signale_par_l_absence_du_sceau_final(tmp_path):
    """On coupe net lancer.py pendant un essai : le vérificateur doit voir qu'il manque
    le sceau final, et rien d'autre (les entrées déjà écrites restent chaînées)."""
    sortie = tmp_path / "essai"
    # Un million de cycles : l'essai dure bien plus longtemps que le test.
    proc = subprocess.Popen([sys.executable, str(LOGICIEL / "lancer.py"), str(SCENARIOS / "nominal.json"),
                             "--cycles", "1000000", "--silencieux", "--sortie", str(sortie)],
                            cwd=LOGICIEL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        # On attend qu'au moins deux sceaux aient pu être demandés.
        limite = time.monotonic() + 60
        n = 0
        while n < 130 and time.monotonic() < limite and proc.poll() is None:
            time.sleep(0.02)
            try:
                cx = sqlite3.connect(f"file:{(sortie / 'journal.sqlite').as_posix()}?mode=ro", uri=True)
                n = cx.execute("SELECT COUNT(*) FROM journal").fetchone()[0]
                cx.close()
            except sqlite3.Error:
                pass
        assert proc.poll() is None, "l'essai s'est terminé avant la coupure"
    finally:
        proc.kill()   # arrêt brutal : pas d'arreter(), donc pas de sceau final
        proc.wait()

    # Le scelleur finit les sceaux déjà demandés, puis s'arrête tout seul :
    # on attend que leur nombre ne bouge plus.
    sceaux, stable_depuis = -1, time.monotonic()
    while time.monotonic() - stable_depuis < 1.0:
        time.sleep(0.1)
        r = verifier(sortie)
        if r.sceaux != sceaux:
            sceaux, stable_depuis = r.sceaux, time.monotonic()

    assert r.entrees >= 130 and r.sceaux >= 2
    assert not r.sceau_final
    attendues = [m for _, m in r.anomalies]
    assert "sceau final absent (arrêt non contrôlé)" in attendues
    assert all(m.endswith("non scellées") or m.startswith("sceau final absent") for m in attendues), r.texte()
    if r.premiere_fautive is not None:
        assert r.entrees - r.premiere_fautive <= 60, "au plus 60 entrées sans sceau"
    assert lancer("--verifier", sortie).returncode == 1
