
"""SS-2 : acquisition et qualification des mesures.

Responsable : Aboubacar Sidiki Yansané.

Concept A amendé :
- Erreur additive : biais et bruit gaussien.
- Dérive lente.
- Saut franc.
- Perte de communication.
- Valeur hors plage.
- Qualification des données reçues de SS-1.

Entrées :
    grandeurs_vraies : dict {Variable: float}
    horodatage_utc   : str

Sorties :
    mesures    : dict {Variable: Mesure}
    evenements : list[dict]

Le contrat commun et les interfaces des autres sous-systèmes
ne sont pas modifiés.
"""

from __future__ import annotations

import math

import numpy as np

from jumeau.contrat import PLAGES, T_CYCLE, Mesure, Statut, Variable
from jumeau.interface import SousSysteme


# Paramètres provisoires du squelette collectif.
# À confirmer avec les responsables du projet.
SIGMA_BRUIT = {
    Variable.T: 0.1,
    Variable.P: 0.0005,
    Variable.Q: 0.0005,
}

BIAIS = {
    Variable.T: 0.0,
    Variable.P: 0.0,
    Variable.Q: 0.0,
}


def valider_valeur_brute(valeur) -> bool:
    """Vérifie qu'une donnée est un nombre réel fini.

    Les chaînes, booléens, valeurs absentes, NaN et inf
    sont considérés comme invalides.
    """
    if isinstance(valeur, (bool, np.bool_)):
        return False

    if not isinstance(
        valeur, (int, float, np.integer, np.floating)
    ):
        return False

    try:
        return math.isfinite(float(valeur))
    except (ValueError, TypeError, OverflowError):
        return False


class AcquisitionMesures(SousSysteme):
    """Acquisition et qualification des mesures T, P et Q."""

    nom = "SS-2"

    @staticmethod
    def valider_defaut(defaut: dict) -> tuple[bool, str | None]:
        """Vérifie les paramètres d'un défaut de mesure."""

        if not isinstance(defaut, dict):
            return False, "format_defaut_invalide"

        type_defaut = defaut.get("type")

        if type_defaut not in (
            "derive",
            "saut",
            "perte_communication",
            "hors_plage",
        ):
            return False, "type_defaut_invalide"

        if defaut.get("variable") not in (
            "T", "P", "Q", "toutes"
        ):
            return False, "variable_invalide"

        def nombre_valide(cle: str, strictement_positif=False) -> bool:
            valeur = defaut.get(cle)

            if not valider_valeur_brute(valeur):
                return False

            valeur = float(valeur)

            return (
                valeur > 0
                if strictement_positif
                else valeur >= 0
            )

        if not nombre_valide("debut_s"):
            return False, "debut_invalide"

        if type_defaut in ("perte_communication", "hors_plage"):
            if not nombre_valide("duree_s", strictement_positif=True):
                return False, "duree_invalide"

        elif type_defaut == "derive":
            if not nombre_valide(
                "pente_sigma_par_cycle", strictement_positif=True
            ):
                return False, "pente_invalide"

            if not nombre_valide(
                "amplitude_max_pct_etendue", strictement_positif=True
            ):
                return False, "amplitude_max_invalide"

        elif type_defaut == "saut":
            if not valider_valeur_brute(
                defaut.get("amplitude_sigma")
            ):
                return False, "amplitude_invalide"

            if float(defaut["amplitude_sigma"]) == 0:
                return False, "amplitude_nulle"

        return True, None


    def demarrer(self, contexte: dict) -> None:
        """Initialise le générateur et contrôle les défauts du scénario."""
        self.rng = np.random.default_rng([contexte["graine"], 2])

        self.defauts = []
        self.defauts_refuses = []
        self._annonces: set[int] = set()

        for i, defaut in enumerate(contexte["scenario"].get("defauts", [])):
            valide, motif = self.valider_defaut(defaut)

            if valide:
                self.defauts.append(defaut)
            else:
                self.defauts_refuses.append({
                    "type": "defaut_refuse",
                    "index_defaut": i,
                    "motif": motif,
                })

    def _actif(self, defaut: dict, t: float) -> bool:
        """Indique si un défaut est actif au temps simulé t."""
        debut = defaut["debut_s"]

        if t < debut:
            return False

        duree = defaut.get("duree_s")

        return duree is None or t < debut + duree

    def _concerne(self, defaut: dict, variable: Variable) -> bool:
        """Vérifie si un défaut concerne la variable étudiée."""
        return defaut["variable"] in ("toutes", variable.value)

   
    def etape(self, k: int, entrees: dict) -> dict:
        """Effectue un cycle d'acquisition et de qualification."""

        t = k * T_CYCLE
        vraies = entrees["grandeurs_vraies"]
        horodatage = entrees["horodatage_utc"]

        evenements = []
        mesures = {}

        # 0. Transmettre une seule fois les défauts refusés (CU2).
        if k == 0:
            evenements.extend(self.defauts_refuses)

        # 1. Annoncer chaque défaut valide lorsqu'il commence.
        for i, defaut in enumerate(self.defauts):
            if self._actif(defaut, t) and i not in self._annonces:
                self._annonces.add(i)

                evenements.append({
                    "type": "defaut_injecte",
                    **defaut,
                })

        # 2. Traiter successivement les trois capteurs.
        for var in Variable:
            sigma = SIGMA_BRUIT[var]

            # Validation de la donnée provenant de SS-1.
            valeur_brute = vraies.get(var)

            if not valider_valeur_brute(valeur_brute):
                mesures[var] = Mesure(
                    k=k,
                    t=t,
                    horodatage_utc=horodatage,
                    variable=var,
                    valeur=None,
                    statut=Statut.ABSENT,
                )

                evenements.append({
                    "type": "mesure_rejetee",
                    "variable": var.value,
                    "cycle": k,
                    "motif": "format_invalide",
                })

                continue

            # 3. Modèle d'erreur additive : biais + bruit.
            valeur = (
                float(valeur_brute)
                + BIAIS[var]
                + self.rng.normal(0.0, sigma)
            )

            statut = Statut.VALIDE

            # 4. Application des défauts valides du scénario.
            for defaut in self.defauts:
                if not (
                    self._actif(defaut, t)
                    and self._concerne(defaut, var)
                ):
                    continue

                type_ = defaut["type"]

                if type_ == "derive":
                    cycles = (
                        t - defaut["debut_s"]
                    ) / T_CYCLE

                    bas, haut = PLAGES[var]

                    plafond = (
                        defaut.get(
                            "amplitude_max_pct_etendue", 2.5
                        )
                        / 100
                        * (haut - bas)
                    )

                    derive = min(
                        defaut["pente_sigma_par_cycle"]
                        * sigma
                        * cycles,
                        plafond,
                    )

                    valeur += derive

                elif type_ == "saut":
                    valeur += (
                        defaut["amplitude_sigma"] * sigma
                    )

                elif type_ == "perte_communication":
                    statut = Statut.ABSENT

                elif type_ == "hors_plage":
                    valeur = PLAGES[var][1] * 2

            # 5. Qualification de la valeur après les défauts.
            bas, haut = PLAGES[var]

            if statut is Statut.VALIDE:
                if not math.isfinite(valeur):
                    statut = Statut.ABSENT

                    evenements.append({
                        "type": "mesure_rejetee",
                        "variable": var.value,
                        "cycle": k,
                        "motif": "valeur_non_finie",
                    })

                elif not (bas <= valeur <= haut):
                    statut = Statut.HORS_PLAGE

                    evenements.append({
                        "type": "mesure_rejetee",
                        "variable": var.value,
                        "cycle": k,
                        "valeur_brute": float(valeur),
                        "motif": "hors_plage",
                    })

            # 6. Création de la mesure selon le contrat collectif.
            mesures[var] = Mesure(
                k=k,
                t=t,
                horodatage_utc=horodatage,
                variable=var,
                valeur=(
                    float(valeur)
                    if statut is Statut.VALIDE
                    else None
                ),
                statut=statut,
            )

        # 7. Transmission des mesures et événements.
        return {
            "mesures": mesures,
            "evenements": evenements,
        }
