"""SS-2 : acquisition et qualification des mesures. Responsable : Aboubacar Sidiki Yansané.

Version minimale du concept A amendé : erreur additive (biais et bruit
gaussien), plus les défauts d'EX-F-02 lus dans le scénario.

Entrées par cycle :
  grandeurs_vraies  dict {Variable: float}   venant de SS-1
  horodatage_utc    str                      ajouté par l'orchestrateur

Sortie par cycle :
  mesures     dict {Variable: Mesure}   selon le contrat de données
  evenements  list                      défauts injectés, mesures rejetées

Défauts reconnus dans scenario["defauts"] (instants en secondes simulées) :
  derive               variable, debut_s, pente_sigma_par_cycle, amplitude_max_pct_etendue
  saut                 variable, debut_s, amplitude_sigma
  perte_communication  variable (ou "toutes"), debut_s, duree_s
  hors_plage           variable, debut_s, duree_s

À faire par le responsable : biais réalistes par capteur, donnée malformée
(EX-Q-04), refus d'un défaut dont les paramètres sont hors bornes (CU2).
"""
from __future__ import annotations

import numpy as np

from jumeau.contrat import PLAGES, T_CYCLE, Mesure, Statut, Variable
from jumeau.interface import SousSysteme

# Écart type du bruit de chaque capteur. Valeurs provisoires.
SIGMA_BRUIT = {Variable.T: 0.1, Variable.P: 0.0005, Variable.Q: 0.0005}
BIAIS = {Variable.T: 0.0, Variable.P: 0.0, Variable.Q: 0.0}


class AcquisitionMesures(SousSysteme):
    nom = "SS-2"

    def demarrer(self, contexte: dict) -> None:
        self.rng = np.random.default_rng([contexte["graine"], 2])
        self.defauts = contexte["scenario"].get("defauts", [])
        self._annonces: set[int] = set()

    def _actif(self, defaut: dict, t: float) -> bool:
        debut = defaut["debut_s"]
        if t < debut:
            return False
        duree = defaut.get("duree_s")
        return duree is None or t < debut + duree

    def _concerne(self, defaut: dict, variable: Variable) -> bool:
        return defaut["variable"] in ("toutes", variable.value)

    def etape(self, k: int, entrees: dict) -> dict:
        t = k * T_CYCLE
        vraies = entrees["grandeurs_vraies"]
        evenements = []
        for i, defaut in enumerate(self.defauts):
            if self._actif(defaut, t) and i not in self._annonces:
                self._annonces.add(i)
                evenements.append({"type": "defaut_injecte", **defaut})

        mesures = {}
        for var in Variable:
            sigma = SIGMA_BRUIT[var]
            valeur = vraies[var] + BIAIS[var] + self.rng.normal(0.0, sigma)
            statut = Statut.VALIDE
            for defaut in self.defauts:
                if not (self._actif(defaut, t) and self._concerne(defaut, var)):
                    continue
                type_ = defaut["type"]
                if type_ == "derive":
                    cycles = (t - defaut["debut_s"]) / T_CYCLE
                    bas, haut = PLAGES[var]
                    plafond = defaut.get("amplitude_max_pct_etendue", 2.5) / 100 * (haut - bas)
                    valeur += min(defaut["pente_sigma_par_cycle"] * sigma * cycles, plafond)
                elif type_ == "saut":
                    valeur += defaut["amplitude_sigma"] * sigma
                elif type_ == "perte_communication":
                    statut = Statut.ABSENT
                elif type_ == "hors_plage":
                    valeur = PLAGES[var][1] * 2  # valeur brute impossible

            bas, haut = PLAGES[var]
            if statut is Statut.VALIDE and not (bas <= valeur <= haut):
                statut = Statut.HORS_PLAGE
                evenements.append({"type": "mesure_rejetee", "variable": var.value,
                                   "valeur_brute": valeur, "motif": "hors_plage"})
            mesures[var] = Mesure(
                k=k, t=t, horodatage_utc=entrees["horodatage_utc"], variable=var,
                valeur=float(valeur) if statut is Statut.VALIDE else None, statut=statut,
            )
        return {"mesures": mesures, "evenements": evenements}
