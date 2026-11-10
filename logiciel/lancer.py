"""Lance un scénario d'essai sur le prototype.

Exemples :
    python lancer.py scenarios/derive_lente.json
    python lancer.py scenarios/nominal.json --cycles 600
    python lancer.py scenarios/derive_lente.json --temps-reel
    python lancer.py --verifier sorties/derive_lente_20261109-180000/journal.sqlite
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from jumeau.orchestrateur import Orchestrateur
from jumeau.scenario import charger
from jumeau.ss6_journal import verifier_journal


def main() -> int:
    p = argparse.ArgumentParser(description="Jumeau numérique de surveillance (IMP2)")
    p.add_argument("scenario", nargs="?", help="fichier JSON du scénario")
    p.add_argument("--cycles", type=int, help="nombre de cycles (par défaut : celui du scénario)")
    p.add_argument("--sortie", help="dossier de sortie (par défaut : sorties/<scénario>_<date>)")
    p.add_argument("--silencieux", action="store_true", help="n'affiche rien pendant l'essai")
    p.add_argument("--tolerant", action="store_true",
                   help="un module en défaut est journalisé au lieu d'arrêter l'essai")
    p.add_argument("--temps-reel", action="store_true", help="un cycle par seconde réelle")
    p.add_argument("--verifier", metavar="JOURNAL", help="vérifie l'intégrité d'un journal et quitte")
    args = p.parse_args()

    if args.verifier:
        integre, fautive, n = verifier_journal(args.verifier)
        if integre:
            print(f"Journal intègre : {n} entrées, chaîne SHA-256 vérifiée.")
            return 0
        print(f"Journal ALTÉRÉ : la chaîne est rompue à l'entrée {fautive} (sur {n}).")
        return 1

    if not args.scenario:
        p.error("indiquer un fichier de scénario, ou --verifier JOURNAL")

    scenario = charger(args.scenario)
    sortie = args.sortie or Path("sorties") / f"{Path(args.scenario).stem}_{datetime.now():%Y%m%d-%H%M%S}"
    print(f"Scénario : {scenario['nom']} (graine {scenario['graine']})")
    resume = Orchestrateur(scenario, sortie, silencieux=args.silencieux, tolerant=args.tolerant,
                           temps_reel=args.temps_reel).executer(args.cycles)
    integre, _, n = verifier_journal(Path(sortie) / "journal.sqlite")
    print(f"\nTerminé : {resume['cycles']} cycles, {n} entrées au journal "
          f"({'intègre' if integre else 'ALTÉRÉ'}). État final : {resume['etat_final']}.")
    print(f"Résultats dans {sortie}")
    print(json.dumps(resume["changements_etat"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
