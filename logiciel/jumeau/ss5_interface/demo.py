"""Démonstration de SS-5 à partir d'états produits à la main.

Elle réalise les deux tests attendus pour SS-5 au rapport d'ingénierie
préliminaire (section 2.5) :
  1. l'affichage de chacun des quatre états, à partir d'états produits à la
     main plutôt que par SS-4 ;
  2. la présence de la réponse de l'opérateur au journal de SS-6 (EX-F-09).

SS-5 est exécuté seul, contre son contrat d'interface : les entrées de SS-2,
SS-3 et SS-4 sont injectées par le script. Un échec désigne donc SS-5 seul.
Le journal est le vrai module SS-6, et son intégrité est vérifiée à la fin.

Exécution, depuis le dossier logiciel :
    python -m jumeau.ss5_interface.demo
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from jumeau.contrat import T_CYCLE, Etat, Mesure, Statut, Variable
from jumeau.orchestrateur import _serialiser
from jumeau.ss5_interface import LIBELLES, SYMBOLES, PresentationEtat
from jumeau.ss6_journal import JournalDonnees, verifier_journal

ATTENDUS = {Variable.T: 60.0, Variable.P: 0.25, Variable.Q: 0.25}

# Scénario produit à la main : (premier cycle, état, confiance, variables en cause).
# Chaque ligne s'applique jusqu'à la suivante.
SEQUENCE = [
    (0, Etat.NORMAL, 0.92, []),
    (5, Etat.DERIVE, 1.0, [Variable.T]),
    (10, Etat.ANOMALIE, 1.0, [Variable.Q]),
    (15, Etat.INCERTAIN, 0.0, [Variable.P]),
    (20, Etat.NORMAL, 0.85, []),
]
CYCLES = 25
# Réponses de l'opérateur, données juste avant le cycle indiqué.
REPONSES = {7: "confirme", 12: "refuse"}


def decision(k: int):
    courant = SEQUENCE[0]
    for ligne in SEQUENCE:
        if ligne[0] <= k:
            courant = ligne
    return courant[1:]


def mesures(k: int, etat: Etat) -> dict:
    """Mesures cohérentes avec l'état injecté, pour un affichage réaliste."""
    horodatage = f"2026-11-12T12:00:{k:02d}Z"
    valeurs = dict(ATTENDUS)
    if etat is Etat.DERIVE:
        valeurs[Variable.T] += 0.15 * (k - 4)        # température qui monte
    if etat is Etat.ANOMALIE:
        valeurs[Variable.Q] = 0.30                   # saut franc du débit, non critique
    resultat = {}
    for var in Variable:
        if etat is Etat.INCERTAIN and var is Variable.P:
            resultat[var] = Mesure(k, k * T_CYCLE, horodatage, var, None, Statut.ABSENT)
        else:
            resultat[var] = Mesure(k, k * T_CYCLE, horodatage, var, valeurs[var], Statut.VALIDE)
    return resultat


def executer(sortie: Path, silencieux: bool = False) -> dict:
    sortie.mkdir(parents=True, exist_ok=True)
    contexte = {"sortie": str(sortie), "silencieux": silencieux}
    ss5, ss6 = PresentationEtat(), JournalDonnees()
    ss5.demarrer(contexte)
    ss6.demarrer(contexte)

    conformes, affichages, cles_sorties = 0, [], set()
    try:
        for k in range(CYCLES):
            if k in REPONSES:
                if not silencieux:
                    print(f"          (l'opérateur répond : {REPONSES[k]})")
                ss5.repondre(REPONSES[k])
            etat, confiance, contributrices = decision(k)
            entrees = {"etat": etat, "confiance": confiance, "contributrices": contributrices,
                       "mesures": mesures(k, etat), "attendus": ATTENDUS}
            sortie_ss5 = ss5.etape(k, entrees)
            cles_sorties |= set(sortie_ss5)
            affichages.append(sortie_ss5["affichage"])
            # L'état affiché doit être celui injecté, au cycle même.
            conformes += ss5.etat_affiche is etat
            if sortie_ss5["affichage"] and etat is not Etat.NORMAL and ss5.k_entree == k and not silencieux:
                print(ss5.vue_detail(entrees))
            ss6.etape(k, {"contenu": _serialiser({"k": k, "etat": etat, "confiance": confiance,
                                                  "evenements": sortie_ss5["evenements"]})})
    finally:
        ss6.arreter()

    journal = Path(sortie) / "journal.sqlite"
    integre, _, n = verifier_journal(journal)
    cx = sqlite3.connect(journal)
    evenements = [e for (c,) in cx.execute("SELECT contenu FROM journal ORDER BY sequence")
                  for e in json.loads(c)["evenements"]]
    cx.close()
    reponses = [e for e in evenements if e["type"] == "reponse_operateur"]
    demandes = [e for e in evenements if e["type"] == "demande_confirmation"]
    etats_vus = [e for _, e in ss5.historique]

    return {
        "quatre_etats_affiches": set(etats_vus) == set(Etat),
        "etat_conforme_a_chaque_cycle": conformes == CYCLES,
        "demandes_pour_derive_et_anomalie": [d["etat"] for d in demandes] == ["derive", "anomalie"],
        "deux_reponses_au_journal": [r["reponse"] for r in reponses] == ["confirme", "refuse"],
        "instantane_avec_empreinte": all(len(r["empreinte_instantane"]) == 64 for r in reponses),
        "aucune_sortie_vers_installation": cles_sorties <= {"affichage", "evenements"},
        "journal_integre": integre and n == CYCLES,
        "_historique": [(k, SYMBOLES[e], LIBELLES[e]) for k, e in ss5.historique],
        "_dossier": str(sortie),
    }


INTITULES = {
    "quatre_etats_affiches": "Les quatre états sont affichés",
    "etat_conforme_a_chaque_cycle": "L'état affiché est celui injecté, à chaque cycle",
    "demandes_pour_derive_et_anomalie": "Une demande de confirmation pour la dérive et pour l'anomalie",
    "deux_reponses_au_journal": "Les deux réponses de l'opérateur sont au journal (EX-F-09)",
    "instantane_avec_empreinte": "Chaque réponse porte un instantané de l'écran et son empreinte",
    "aucune_sortie_vers_installation": "Aucune sortie vers l'installation (EX-F-08)",
    "journal_integre": "Journal intègre, une entrée par cycle",
}


def main() -> int:
    sortie = Path("sorties") / f"demo_ss5_{datetime.now():%Y%m%d-%H%M%S}"
    print("Démonstration de SS-5 : états produits à la main, journal SS-6 réel\n")
    resultat = executer(sortie)
    print("\nÉtats affichés :", ", ".join(f"t={k} s {s} {l}" for k, s, l in resultat["_historique"]))
    print("\nVérifications :")
    ok = True
    for cle, valeur in resultat.items():
        if cle.startswith("_"):
            continue
        ok &= valeur
        print(f"  [{'OK' if valeur else 'ÉCHEC'}] {INTITULES[cle]}")
    print(f"\nJournal : {resultat['_dossier']}")
    print("Résultat :", "toutes les vérifications réussissent." if ok else "au moins une vérification échoue.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
