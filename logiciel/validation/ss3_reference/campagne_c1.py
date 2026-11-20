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
SCENARIO_BASE = RACINE / "scenarios" / "nominal.json"

NB_ESSAIS = 20
GRAINES = list(range(2001, 2001 + NB_ESSAIS))


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

    # Les 600 premiers cycles servent au calage.
    for cycle in lignes[600:]:
        r = cycle.get("residus", {})

        for variable in residus:
            valeur = r.get(variable)

            if valeur is not None:
                residus[variable].append(float(valeur))

    return residus


def charger_scenario_avec_graine(
    graine: int,
    dossier: Path,
) -> Path:
    with open(
        SCENARIO_BASE,
        "r",
        encoding="utf-8",
    ) as f:
        donnees = json.load(f)

    donnees["graine"] = graine
    donnees["nom"] = f"Nominal C1 graine {graine}"

    chemin = dossier / f"nominal_{graine}.json"

    with open(
        chemin,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            donnees,
            f,
            indent=2,
            ensure_ascii=False,
        )

    return chemin


def biais_moyen(valeurs: list[float]) -> float:
    return mean(valeurs)


def intervalle_confiance_95(
    valeurs: list[float],
) -> tuple[float, float]:
    moyenne = mean(valeurs)
    ecart_type = stdev(valeurs)

    # Approximation normale à 95 %.
    marge = (
        1.96
        * ecart_type
        / math.sqrt(len(valeurs))
    )

    return (
        moyenne - marge,
        moyenne + marge,
    )


def main() -> None:
    biais_par_variable = {
        "T": [],
        "P": [],
        "Q": [],
    }

    # Nombre d'alarmes produit par chacun des 20 essais.
    alarmes_par_essai: list[int] = []

    # Nombre d'essais dans chaque catégorie.
    essais_zero_alarme = 0
    essais_une_alarme = 0
    essais_plus_une_alarme = 0

    # Nombre total de transitions vers derive/anomalie.
    total_fausses_alarmes = 0

    # Compte toutes les alarmes impliquant chaque variable.
    compte_variables = {
        "T": 0,
        "P": 0,
        "Q": 0,
    }

    # Cycles des premières alarmes de chaque essai.
    cycles_premieres_alarmes = []

    print("=== CAMPAGNE PRELIMINAIRE C1 SS-3 ===")
    print(f"Nombre d'essais : {NB_ESSAIS}")
    print("Calage : 600 cycles")
    print(
        "Critere fausses alarmes : "
        "au plus 1 alarme par essai nominal"
    )
    print()

    for numero, graine in enumerate(
        GRAINES,
        start=1,
    ):
        with tempfile.TemporaryDirectory() as dossier_temp:
            dossier_temp = Path(dossier_temp)

            chemin_scenario = charger_scenario_avec_graine(
                graine,
                dossier_temp,
            )

            scenario = charger(
                chemin_scenario
            )

            dossier_sortie = (
                dossier_temp / "sortie"
            )

            resume = Orchestrateur(
                scenario,
                dossier_sortie,
                silencieux=True,
            ).executer()

            journal = (
                dossier_sortie
                / "journal.sqlite"
            )

            residus = lire_residus(
                journal
            )

            biais_essai = {}

            for variable in (
                "T",
                "P",
                "Q",
            ):
                b = biais_moyen(
                    residus[variable]
                )

                biais_par_variable[
                    variable
                ].append(b)

                biais_essai[
                    variable
                ] = b

            # Dans un scénario nominal, chaque transition
            # vers "derive" ou "anomalie" est considérée
            # comme une fausse alarme.
            fausses = [
                changement
                for changement
                in resume[
                    "changements_etat"
                ]
                if changement["vers"]
                in (
                    "derive",
                    "anomalie",
                )
            ]

            nb_alarmes = len(fausses)

            alarmes_par_essai.append(
                nb_alarmes
            )

            total_fausses_alarmes += (
                nb_alarmes
            )

            if nb_alarmes == 0:
                essais_zero_alarme += 1

            elif nb_alarmes == 1:
                essais_une_alarme += 1

            else:
                essais_plus_une_alarme += 1

            # Diagnostic détaillé des alarmes.
            details_alarmes = []

            for alarme in fausses:
                cycle_alarme = alarme["k"]
                type_alarme = alarme["vers"]

                variables_alarme = (
                    alarme.get(
                        "variables",
                        [],
                    )
                )

                for variable in variables_alarme:
                    if variable in compte_variables:
                        compte_variables[
                            variable
                        ] += 1

                texte_variables = (
                    ",".join(
                        variables_alarme
                    )
                )

                details_alarmes.append(
                    f"k={cycle_alarme}, "
                    f"type={type_alarme}, "
                    f"variables="
                    f"{texte_variables}"
                )

            if nb_alarmes > 0:
                premiere = fausses[0]

                cycles_premieres_alarmes.append(
                    premiere["k"]
                )

            if nb_alarmes <= 1:
                verdict_essai = "CONFORME"
            else:
                verdict_essai = "NON CONFORME"

            print(
                f"Essai {numero:02d} | "
                f"graine={graine} | "
                f"T={biais_essai['T']:+.4f} sigma | "
                f"P={biais_essai['P']:+.4f} sigma | "
                f"Q={biais_essai['Q']:+.4f} sigma | "
                f"alarmes={nb_alarmes} | "
                f"{verdict_essai}"
            )

            for detail in details_alarmes:
                print(
                    f"           -> {detail}"
                )

    print()
    print(
        "=== RESULTATS GLOBAUX C1 ==="
    )

    for variable in (
        "T",
        "P",
        "Q",
    ):
        valeurs = (
            biais_par_variable[
                variable
            ]
        )

        moyenne = mean(valeurs)
        sigma_essais = stdev(valeurs)

        ic_bas, ic_haut = (
            intervalle_confiance_95(
                valeurs
            )
        )

        conforme_moyenne = (
            abs(moyenne) <= 0.1
        )

        conforme_ic = (
            ic_bas >= -0.1
            and ic_haut <= 0.1
        )

        print()
        print(variable)

        print(
            f"  essais = "
            f"{len(valeurs)}"
        )

        print(
            f"  biais moyen = "
            f"{moyenne:+.6f} sigma"
        )

        print(
            f"  ecart-type entre essais = "
            f"{sigma_essais:.6f} sigma"
        )

        print(
            f"  IC 95 % du biais moyen = "
            f"[{ic_bas:+.6f} ; "
            f"{ic_haut:+.6f}] sigma"
        )

        print(
            "  limite C1 = "
            "+/- 0.1 sigma"
        )

        print(
            "  biais moyen sous "
            "la limite = "
            f"{'OUI' if conforme_moyenne else 'NON'}"
        )

        print(
            "  IC 95 % entier "
            "dans la limite = "
            f"{'OUI' if conforme_ic else 'NON'}"
        )

    print()
    print(
        "=== FAUSSES ALARMES ==="
    )

    print(
        f"Nombre total de fausses alarmes : "
        f"{total_fausses_alarmes}"
    )

    print(
        f"Essais avec 0 alarme : "
        f"{essais_zero_alarme}"
    )

    print(
        f"Essais avec exactement 1 alarme : "
        f"{essais_une_alarme}"
    )

    print(
        f"Essais avec plus de 1 alarme : "
        f"{essais_plus_une_alarme}"
    )

    print()

    # Le critère du rapport est :
    # au plus une fausse alarme PAR ESSAI.
    if essais_plus_une_alarme == 0:
        print(
            "Critere 'au plus une fausse "
            "alarme par essai' : RESPECTE."
        )
    else:
        print(
            "Critere 'au plus une fausse "
            "alarme par essai' : "
            "NON RESPECTE."
        )

        print(
            f"{essais_plus_une_alarme} essai(s) "
            f"sur {NB_ESSAIS} ont produit "
            "plus d'une fausse alarme."
        )

    print()
    print(
        "=== NOMBRE D'ALARMES PAR ESSAI ==="
    )

    for numero, (
        graine,
        nb_alarmes,
    ) in enumerate(
        zip(
            GRAINES,
            alarmes_par_essai,
        ),
        start=1,
    ):
        verdict = (
            "CONFORME"
            if nb_alarmes <= 1
            else "NON CONFORME"
        )

        print(
            f"Essai {numero:02d} | "
            f"graine={graine} | "
            f"alarmes={nb_alarmes} | "
            f"{verdict}"
        )

    print()
    print(
        "=== DIAGNOSTIC DES "
        "FAUSSES ALARMES ==="
    )

    print(
        f"Alarmes impliquant T : "
        f"{compte_variables['T']}"
    )

    print(
        f"Alarmes impliquant P : "
        f"{compte_variables['P']}"
    )

    print(
        f"Alarmes impliquant Q : "
        f"{compte_variables['Q']}"
    )

    if cycles_premieres_alarmes:
        cycle_moyen = mean(
            cycles_premieres_alarmes
        )

        premier_cycle = min(
            cycles_premieres_alarmes
        )

        dernier_cycle = max(
            cycles_premieres_alarmes
        )

        print()

        print(
            "Cycle moyen de la premiere "
            "fausse alarme : "
            f"{cycle_moyen:.1f}"
        )

        print(
            "Premiere fausse alarme "
            "la plus tot : "
            f"k={premier_cycle}"
        )

        print(
            "Premiere fausse alarme "
            "la plus tard : "
            f"k={dernier_cycle}"
        )

    print()
    print(
        "Conclusion : campagne "
        "preliminaire uniquement."
    )

    print(
        "Le verdict officiel C1 reste "
        "celui de l'essai de coherence "
        "du 18 novembre."
    )


if __name__ == "__main__":
    main()