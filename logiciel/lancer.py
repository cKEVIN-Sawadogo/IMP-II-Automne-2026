"""Lance un scénario d'essai sur le prototype.

Exemples :
    python lancer.py scenarios/derive_lente.json
    python lancer.py scenarios/nominal.json --cycles 600
    python lancer.py scenarios/derive_lente.json --temps-reel           (interface web)
    python lancer.py scenarios/derive_lente.json --temps-reel --console (texte seul)
    python lancer.py --interface                                        (choix dans l'interface)
    python lancer.py --verifier sorties/derive_lente_20261109-180000/journal.sqlite
    python lancer.py --verifier sorties/derive_lente_20261109-180000
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from jumeau.orchestrateur import Orchestrateur
from jumeau.scenario import charger
from jumeau.ss6_journal import verifier


def main() -> int:
    p = argparse.ArgumentParser(description="Jumeau numérique de surveillance (IMP2)")
    p.add_argument("scenario", nargs="?", help="fichier JSON du scénario")
    p.add_argument("--cycles", type=int, help="nombre de cycles (par défaut : celui du scénario)")
    p.add_argument("--sortie", help="dossier de sortie (par défaut : sorties/<scénario>_<date>)")
    p.add_argument("--silencieux", action="store_true", help="n'affiche rien pendant l'essai")
    p.add_argument("--tolerant", action="store_true",
                   help="un module en défaut est journalisé au lieu d'arrêter l'essai")
    p.add_argument("--temps-reel", action="store_true",
                   help="un cycle par seconde réelle, avec l'interface web de SS-5")
    p.add_argument("--console", action="store_true",
                   help="avec --temps-reel : affichage texte seul, sans interface web")
    p.add_argument("--interface", action="store_true",
                   help="ouvre l'interface web ; sans scénario, il se choisit dans l'interface")
    p.add_argument("--port", type=int, default=8050, help="port de l'interface web (8050)")
    p.add_argument("--sans-navigateur", action="store_true",
                   help="n'ouvre pas le navigateur automatiquement")
    p.add_argument("--verifier", metavar="JOURNAL",
                   help="vérifie un journal (journal.sqlite ou dossier de l'essai) et ses sceaux, puis quitte")
    args = p.parse_args()

    if args.verifier:
        # Vérificateur de SS-6 : chaîne SHA-256, sceaux Ed25519 et complétude du journal.
        try:
            rapport = verifier(args.verifier)
        except FileNotFoundError as erreur:
            print(f"Journal introuvable : {erreur}")
            return 2
        print(rapport.texte(max_affiche=10))
        return 0 if rapport.valide else 1

    if args.interface or (args.temps_reel and not args.console):
        from jumeau.ss5_interface.tableau import servir
        if args.scenario:
            # Un scénario invalide est refusé avant d'ouvrir l'interface.
            print(f"Scénario : {charger(args.scenario)['nom']}")
        return servir(args.scenario, cycles=args.cycles, sortie=args.sortie,
                      vitesse=1.0 if args.temps_reel or not args.scenario else None,
                      tolerant=args.tolerant, silencieux=args.silencieux, port=args.port,
                      ouvrir=not args.sans_navigateur,
                      a_la_fin=_afficher_fin)

    if not args.scenario:
        p.error("indiquer un fichier de scénario, ou --verifier JOURNAL")

    scenario = charger(args.scenario)
    sortie = args.sortie or Path("sorties") / f"{Path(args.scenario).stem}_{datetime.now():%Y%m%d-%H%M%S}"
    print(f"Scénario : {scenario['nom']} (graine {scenario['graine']})")
    resume = Orchestrateur(scenario, sortie, silencieux=args.silencieux, tolerant=args.tolerant,
                           temps_reel=args.temps_reel).executer(args.cycles)
    rapport = verifier(Path(sortie) / "journal.sqlite")
    print(f"\nTerminé : {resume['cycles']} cycles, {rapport.entrees} entrées au journal, "
          f"{rapport.sceaux} sceaux ({rapport.verdict.lower() if rapport.valide else rapport.verdict}). "
          f"État final : {resume['etat_final']}.")
    print(f"Résultats dans {sortie}")
    print(json.dumps(resume["changements_etat"], ensure_ascii=False))
    return 0


def _afficher_fin(session) -> None:
    """Bilan dans la console quand un essai lancé depuis l'interface se termine."""
    resume = session.resume or {}
    print(f"\nEssai {session.statut} : {len(session.k)} cycles journalisés. "
          f"État final : {resume.get('etat_final') or (session.etat[-1] if session.etat else '-')}.")
    print(f"Résultats dans {session.sortie}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
