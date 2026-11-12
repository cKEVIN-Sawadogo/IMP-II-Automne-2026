"""SS-5 : présentation par état. Responsable : Jérémie Arno Tchawo Soppewe.

VERSION PROVISOIRE EN MODE TEXTE. Elle affiche dans la console la vue
permanente (état, confiance, variables en cause) à chaque changement d'état,
et un bandeau des variables toutes les 60 secondes simulées. L'interface
Plotly Dash du concept B la remplacera.

Entrées par cycle :
  etat, confiance, contributrices   venant de SS-4
  mesures                           venant de SS-2 (bandeau des variables)
  attendus                          venant de SS-3

Sortie par cycle :
  affichage  str   texte affiché (vide s'il n'y a rien de nouveau)

Aucune sortie vers l'installation (EX-F-08) : ce module ne fait qu'afficher.
"""
from __future__ import annotations

from jumeau.contrat import UNITES, Etat, Statut, Variable
from jumeau.interface import SousSysteme

LIBELLES = {
    Etat.NORMAL: "NORMAL",
    Etat.DERIVE: "DÉRIVE",
    Etat.ANOMALIE: "ANOMALIE",
    Etat.INCERTAIN: "INCERTAIN",
}
# Le symbole double la couleur : les états restent distincts sans couleur.
SYMBOLES = {Etat.NORMAL: "[ ]", Etat.DERIVE: "[~]", Etat.ANOMALIE: "[!]", Etat.INCERTAIN: "[?]"}
NOMS = {Variable.T: "température", Variable.P: "pression", Variable.Q: "débit"}


class PresentationEtat(SousSysteme):
    nom = "SS-5"

    def demarrer(self, contexte: dict) -> None:
        self.silencieux = contexte.get("silencieux", False)
        self.etat_affiche = None

    def _bandeau(self, k: int, entrees: dict) -> str:
        morceaux = []
        for var in Variable:
            m = entrees["mesures"][var]
            attendu = (entrees.get("attendus") or {}).get(var)
            if m.statut is not Statut.VALIDE:
                morceaux.append(f"{var.value}: {m.statut.value}")
            elif attendu is None:
                morceaux.append(f"{var.value}={m.valeur:.4g} {UNITES[var]}")
            else:
                morceaux.append(f"{var.value}={m.valeur:.4g} {UNITES[var]} (écart {m.valeur - attendu:+.3g})")
        return f"t={k:>5d} s  " + "  ".join(morceaux)

    def etape(self, k: int, entrees: dict) -> dict:
        etat = entrees.get("etat", Etat.INCERTAIN)
        lignes = []
        if etat is not self.etat_affiche:
            self.etat_affiche = etat
            en_cause = ", ".join(NOMS[v] for v in entrees.get("contributrices", [])) or "aucune"
            lignes.append(f"t={k:>5d} s  {SYMBOLES[etat]} {LIBELLES[etat]:<9} "
                          f"confiance {entrees.get('confiance', 0.0):.0%}  variables en cause : {en_cause}")
        if k % 60 == 0:
            lignes.append(self._bandeau(k, entrees))
        texte = "\n".join(lignes)
        if texte and not self.silencieux:
            print(texte, flush=True)
        return {"affichage": texte}
