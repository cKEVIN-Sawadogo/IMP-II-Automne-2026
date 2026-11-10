from __future__ import annotations

import json
import math
import sqlite3
import tempfile
from pathlib import Path
from statistics import mean, stdev

from jumeau.orchestrateur import Orchestrateur
from jumeau.scenario import charger


RACINE = Path(__file__).resolve().parents[2]
SCENARIO = RACINE / "scenarios" / "nominal.json"


def lire_residus(journal: Path) -> dict[str, list[float]]:
    cx = sqlite3.connect(journal)

    lignes = [
        json.loads(contenu)
        for (contenu,) in cx.execute(
            "SELECT contenu FROM journal ORDER BY sequence"
        )
    ]

    cx.close()

    residus = {
        "T": [],
        "P": [],
        "Q": [],
    }

    # On ignore les 600 cycles de calage.
    for cycle in lignes[600:]:
        r = cycle.get("residus", {})

        for variable in residus:
            valeur = r.get(variable)

            if valeur is not None:
                residus[variable].append(float(valeur))

    return residus


def afficher_resultat(variable: str, valeurs: list[float]) -> None:
    n = len(valeurs)

    biais = mean(valeurs)
    sigma = stdev(valeurs)

    erreur_standard = sigma / math.sqrt(n)
    marge_95 = 1.96 * erreur_standard

    ic_bas = biais - marge_95
    ic_haut = biais + marge_95

    verdict = "RESPECTEE - PRELIMINAIRE" if abs(biais) <= 0.1 else "NON RESPECTEE"

    print()
    print(f"{variable}")
    print(f"  n = {n}")
    print(f"  biais normalise = {biais:.6f} sigma")
    print(f"  ecart-type = {sigma:.6f} sigma")
    print(f"  IC 95 % = [{ic_bas:.6f} ; {ic_haut:.6f}] sigma")
    print(f"  limite C1 = +/- 0.1 sigma")
    print(f"  verdict = {verdict}")


def main() -> None:
    scenario = charger(SCENARIO)

    with tempfile.TemporaryDirectory() as dossier_temp:
        dossier = Path(dossier_temp)

        Orchestrateur(
            scenario,
            dossier,
            silencieux=True,
        ).executer()

        journal = dossier / "journal.sqlite"

        residus = lire_residus(journal)

        print("=== MESURE PRELIMINAIRE DU BIAIS SS-3 ===")
        print("Scenario : nominal")
        print("Calage : 600 cycles")
        print("Attention : ceci est un essai preliminaire unique.")
        print("Le verdict final C1 exige 20 a 30 essais sains et sera rendu le 18 novembre.")

        for variable in ("T", "P", "Q"):
            afficher_resultat(variable, residus[variable])


if __name__ == "__main__":
    main()