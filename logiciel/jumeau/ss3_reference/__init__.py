"""SS-3 : référence en boucle ouverte. Responsable : Abdoul Raouf Kabré.

VERSION PROVISOIRE. Elle ne contient pas encore le modèle 0D réduit. La
valeur attendue est la moyenne des mesures de SS-2 sur une période de calage
en fonctionnement sain, à un seul point de fonctionnement. Cette version
respecte déjà la règle de C1 : le calage se fait sur les mesures de SS-2,
jamais sur les grandeurs vraies de SS-1.

Entrées par cycle :
  mesures    dict {Variable: Mesure}   venant de SS-2
  consignes  dict                      consignes en vigueur (une référence en
                                       boucle ouverte doit connaître les
                                       commandes ; flux à ajouter au tableau 7-1)

Sortie par cycle :
  residus     dict {Variable: float | None}  résidu normalisé (mesure - attendu) / σ ;
                                             None si la mesure n'est pas valide
  pret        bool                           False pendant le calage ou hors domaine
  attendus    dict {Variable: float | None}  valeurs attendues, pour SS-5
  evenements  list

À faire par le responsable : remplacer la moyenne par le modèle 0D réduit
qui suit les consignes, puis mesurer le biais résiduel pour C1.
"""
from __future__ import annotations

import numpy as np

from jumeau.contrat import Statut, Variable
from jumeau.interface import SousSysteme

# Cycles de calage en fonctionnement sain. Avec 120 cycles, le biais résiduel
# de la moyenne (environ σ/√120 ≈ 0,09 σ) frôle la borne de C1 et produit des
# fausses alarmes sur l'essai nominal, comme le prévoit le tableau 8-5 du
# rapport de concept. 600 cycles le ramènent vers 0,04 σ.
N_CALAGE = 600


class ReferenceBoucleOuverte(SousSysteme):
    nom = "SS-3"

    def demarrer(self, contexte: dict) -> None:
        self.consignes_calage = dict(contexte["scenario"]["consignes_initiales"])
        self.echantillons = {v: [] for v in Variable}
        self.attendu: dict = {}
        self.sigma: dict = {}
        self.hors_domaine = False

    def etape(self, k: int, entrees: dict) -> dict:
        mesures = entrees["mesures"]
        evenements = []

        if entrees["consignes"] != self.consignes_calage and not self.hors_domaine:
            # La version provisoire ne connaît qu'un point de fonctionnement.
            self.hors_domaine = True
            evenements.append({"type": "reference_hors_domaine",
                               "consignes": entrees["consignes"]})

        if not self.attendu:
            for var, m in mesures.items():
                if m.statut is Statut.VALIDE:
                    self.echantillons[var].append(m.valeur)
            if all(len(e) >= N_CALAGE for e in self.echantillons.values()):
                for var, e in self.echantillons.items():
                    self.attendu[var] = float(np.mean(e))
                    self.sigma[var] = float(np.std(e, ddof=1))
                evenements.append({"type": "calage_termine", "cycles": N_CALAGE,
                                   "sigma": {v.value: s for v, s in self.sigma.items()}})

        pret = bool(self.attendu) and not self.hors_domaine
        residus = {}
        for var, m in mesures.items():
            if pret and m.statut is Statut.VALIDE:
                residus[var] = (m.valeur - self.attendu[var]) / self.sigma[var]
            else:
                residus[var] = None
        return {
            "residus": residus,
            "pret": pret,
            "attendus": {v: self.attendu.get(v) for v in Variable},
            "evenements": evenements,
        }
