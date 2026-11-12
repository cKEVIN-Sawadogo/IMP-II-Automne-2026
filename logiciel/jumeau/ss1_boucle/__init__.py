"""SS-1 : simulateur de la boucle (modèle 0D). Responsable : Ibrahima Diallo.

Entrée par cycle (clé de `entrees`) :
  consignes   dict  consignes en vigueur (vitesse_pompe, puissance_W)

Sortie par cycle :
  grandeurs_vraies  dict {Variable: float}  température, pression, débit

Les grandeurs vraies ne vont qu'à SS-2 et au banc d'essai. L'orchestrateur
ne les transmet jamais à SS-3 ni à SS-4 (tableau 7-1).
"""
from __future__ import annotations

import numpy as np

from jumeau.contrat import T_CYCLE, Variable
from jumeau.interface import SousSysteme
from jumeau.ss1_boucle.modele_0d import CP, M, matrices, regime_etabli


class SimulateurBoucle(SousSysteme):
    nom = "SS-1"

    def demarrer(self, contexte: dict) -> None:
        consignes = contexte["scenario"]["consignes_initiales"]
        self._appliquer(consignes)
        # Départ en régime établi, pour que les premiers cycles soient stables.
        self.temperatures = regime_etabli(self.vitesse, self.puissance)

    def _appliquer(self, consignes: dict) -> None:
        self.vitesse = float(consignes["vitesse_pompe"])
        self.puissance = float(consignes["puissance_W"])
        self.A, self.b, self.debit, self.pression = matrices(self.vitesse, self.puissance)

    def etape(self, k: int, entrees: dict) -> dict:
        consignes = entrees["consignes"]
        if (consignes["vitesse_pompe"], consignes["puissance_W"]) != (self.vitesse, self.puissance):
            self._appliquer(consignes)
        sortie = {
            "grandeurs_vraies": {
                Variable.T: float(self.temperatures[0]),
                Variable.P: float(self.pression),
                Variable.Q: float(self.debit),
            }
        }
        # Avance d'un pas (Euler explicite, pas fixe T_CYCLE), comme dans
        # simuler_ss1_0d.py. L'étude du pas de temps d'Ibrahima justifie T = 1 s.
        self.temperatures = self.temperatures + T_CYCLE * (self.A @ self.temperatures + self.b)
        return sortie

    def energie_J(self) -> float:
        """Énergie interne de la boucle, utile pour vérifier les bilans."""
        return float(np.dot(M * CP, self.temperatures))
