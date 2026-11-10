"""SS-3 : référence en boucle ouverte. Responsable : Abdoul Raouf Kabré.

Le sous-système SS-3 calcule les valeurs attendues de température,
pression et débit à partir d'un modèle 0D réduit.

Le modèle est volontairement plus simple que celui de SS-1 :
- SS-1 utilise cinq volumes thermiques ;
- SS-3 utilise un seul état thermique réduit ;
- pression et débit sont calculés directement à partir des consignes.

Le calage est effectué uniquement à partir des mesures saines de SS-2.
Les grandeurs vraies de SS-1 ne sont jamais utilisées.

Entrées par cycle :
  mesures    dict {Variable: Mesure} venant de SS-2
  consignes  dict avec vitesse_pompe et puissance_W

Sorties par cycle :
  residus     dict {Variable: float | None}
  pret        bool
  attendus    dict {Variable: float | None}
  evenements  list
"""

from __future__ import annotations

import numpy as np

from jumeau.contrat import Statut, T_CYCLE, Variable
from jumeau.interface import SousSysteme
from jumeau.ss3_reference.modele_reduit import (
    avancer_temperature,
    debit_attendu,
    pression_attendue,
    temperature_equilibre,
)


# Nombre de cycles utilisés pour le calage sain.
N_CALAGE = 600


class ReferenceBoucleOuverte(SousSysteme):
    nom = "SS-3"

    def demarrer(self, contexte: dict) -> None:
        # Consignes initiales du scénario.
        consignes = contexte["scenario"]["consignes_initiales"]

        # État interne du modèle thermique réduit.
        self.temperature_modele = temperature_equilibre(
            consignes["vitesse_pompe"],
            consignes["puissance_W"],
        )

        # Pendant le calage, on mémorise l'erreur entre les mesures SS-2
        # et les valeurs prédites par le modèle réduit.
        self.erreurs_calage = {v: [] for v in Variable}

        # Correction de biais obtenue avec SS-2.
        self.correction = {}

        # Écart-type des résidus obtenu pendant le calage.
        self.sigma = {}

        # Indique si le calage est terminé.
        self.calage_termine = False

    def _attendus_modele(self, consignes: dict) -> dict:
        """Calcule les valeurs attendues brutes du modèle réduit."""

        vitesse = float(consignes["vitesse_pompe"])
        puissance = float(consignes["puissance_W"])

        return {
            Variable.T: float(self.temperature_modele),
            Variable.P: float(pression_attendue(vitesse)),
            Variable.Q: float(debit_attendu(vitesse)),
        }

    def etape(self, k: int, entrees: dict) -> dict:
        mesures = entrees["mesures"]
        consignes = entrees["consignes"]

        evenements = []

        # 1. Valeurs attendues produites par le modèle réduit.
        attendus_bruts = self._attendus_modele(consignes)

        # 2. Phase de calage.
        # On utilise seulement les mesures valides de SS-2.
        if not self.calage_termine:
            for var, mesure in mesures.items():
                if mesure.statut is Statut.VALIDE:
                    erreur = mesure.valeur - attendus_bruts[var]
                    self.erreurs_calage[var].append(float(erreur))

            # Le calage se termine lorsque chaque variable possède
            # au moins N_CALAGE mesures valides.
            if all(
                len(self.erreurs_calage[var]) >= N_CALAGE
                for var in Variable
            ):
                for var in Variable:
                    erreurs = self.erreurs_calage[var][:N_CALAGE]

                    # Correction du biais du modèle réduit.
                    self.correction[var] = float(np.mean(erreurs))

                    # Écart-type utilisé pour normaliser les résidus.
                    sigma = float(np.std(erreurs, ddof=1))

                    # Protection contre une division par zéro.
                    self.sigma[var] = max(sigma, 1e-12)

                self.calage_termine = True

                evenements.append({
                    "type": "calage_termine",
                    "cycles": N_CALAGE,
                    "correction": {
                        var.value: self.correction[var]
                        for var in Variable
                    },
                    "sigma": {
                        var.value: self.sigma[var]
                        for var in Variable
                    },
                })

        # 3. Application de la correction obtenue pendant le calage.
        if self.calage_termine:
            attendus = {
                var: attendus_bruts[var] + self.correction[var]
                for var in Variable
            }
        else:
            attendus = {
                var: None
                for var in Variable
            }

        # 4. Calcul des résidus normalisés.
        residus = {}

        for var, mesure in mesures.items():
            if (
                self.calage_termine
                and mesure.statut is Statut.VALIDE
            ):
                residus[var] = (
                    mesure.valeur - attendus[var]
                ) / self.sigma[var]
            else:
                residus[var] = None

        # 5. Mise à jour de l'état thermique pour le cycle suivant.
        self.temperature_modele = avancer_temperature(
            self.temperature_modele,
            consignes["vitesse_pompe"],
            consignes["puissance_W"],
            T_CYCLE,
        )

        return {
            "residus": residus,
            "pret": self.calage_termine,
            "attendus": attendus,
            "evenements": evenements,
        }