"""SS-4 : décision séquentielle. Responsable : Rayane Arèmou Akorede Alimi.

Version minimale du concept retenu (sections 8.1 et 8.2 du rapport de
concept) : somme cumulée bilatérale par variable, avec δ = 1 σ (k = 0,5) et
h = 9, seuil instantané à 5 σ, état incertain après N cycles sans résidu.
Le script de test d'Abdramane (test_concept_c_sequentiel.py) sert de
référence pour la logique.

Entrées par cycle :
  residus  dict {Variable: float | None}   venant de SS-3
  pret     bool                            venant de SS-3

Sortie par cycle :
  etat            Etat
  confiance       float entre 0 et 1  (provisoire)
  contributrices  list[Variable]
  sommes          dict {Variable: {"haut": float, "bas": float}}
  evenements      list   un événement par changement d'état

Choix à confirmer par la responsable : priorité entre une alarme déjà
confirmée et l'état incertain, calcul de la confiance, remise à zéro.
"""
from __future__ import annotations

from jumeau.contrat import N_INCERTAIN, Etat, Variable
from jumeau.interface import SousSysteme

K_REF = 0.5           # moitié du décalage minimal détectable δ = 1 σ
SEUIL_H = 9.0         # seuil de la somme cumulée (repli : 10)
SEUIL_INSTANT = 5.0   # seuil instantané, en σ


class DecisionSequentielle(SousSysteme):
    nom = "SS-4"

    def demarrer(self, contexte: dict) -> None:
        self.haut = {v: 0.0 for v in Variable}
        self.bas = {v: 0.0 for v in Variable}
        self.manquants = {v: 0 for v in Variable}
        self.alarme: dict = {}   # variable -> Etat.DERIVE ou Etat.ANOMALIE, verrouillée
        self.etat_precedent = None

    def etape(self, k: int, entrees: dict) -> dict:
        residus = entrees.get("residus") or {}
        pret = entrees.get("pret", False)

        incertaines = []
        for var in Variable:
            r = residus.get(var)
            if not pret or r is None:
                self.manquants[var] += 1
                if not pret or self.manquants[var] >= N_INCERTAIN:
                    incertaines.append(var)
                continue
            self.manquants[var] = 0
            self.haut[var] = max(0.0, self.haut[var] + r - K_REF)
            self.bas[var] = max(0.0, self.bas[var] - r - K_REF)
            if var not in self.alarme:
                # Règle d'ordre : si la somme cumulée a déclenché à un cycle
                # antérieur, l'état reste « dérive » (alarme verrouillée). Au
                # même cycle, le seuil instantané l'emporte : c'est un saut.
                if abs(r) > SEUIL_INSTANT:
                    self.alarme[var] = Etat.ANOMALIE
                elif max(self.haut[var], self.bas[var]) > SEUIL_H:
                    self.alarme[var] = Etat.DERIVE

        if Etat.ANOMALIE in self.alarme.values():
            etat, confiance = Etat.ANOMALIE, 1.0
        elif self.alarme:
            etat, confiance = Etat.DERIVE, 1.0
        elif incertaines:
            etat, confiance = Etat.INCERTAIN, 0.0
        else:
            plus_grande = max(max(self.haut.values()), max(self.bas.values()))
            etat, confiance = Etat.NORMAL, 1.0 - min(plus_grande / SEUIL_H, 1.0)

        contributrices = list(self.alarme) if self.alarme else incertaines
        evenements = []
        if etat is not self.etat_precedent:
            evenements.append({"type": "changement_etat",
                               "de": self.etat_precedent.value if self.etat_precedent else None,
                               "vers": etat.value,
                               "variables": [v.value for v in contributrices]})
            self.etat_precedent = etat

        return {
            "etat": etat,
            "confiance": confiance,
            "contributrices": contributrices,
            "sommes": {v: {"haut": self.haut[v], "bas": self.bas[v]} for v in Variable},
            "evenements": evenements,
        }
