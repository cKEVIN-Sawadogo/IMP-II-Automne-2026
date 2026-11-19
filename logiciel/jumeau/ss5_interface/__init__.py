"""SS-5 : présentation par état. Responsable : Jérémie Arno Tchawo Soppewe.

VERSION EN MODE TEXTE. Elle réalise les fonctions du concept B dans la
console, en attendant l'interface Plotly Dash :

  vue permanente      état, symbole, libellé, confiance et heure d'entrée
                      dans l'état, à chaque changement d'état (CU3) ;
  bandeau             les trois variables, leur écart à l'attendu ou leur
                      statut, toutes les 60 secondes simulées (EX-F-04) ;
  vue de détail       une ligne par variable, variables désignées par SS-4
                      mises en évidence (CU4, EX-F-05), obtenue par
                      vue_detail() ;
  confirmation        demande non préremplie quand l'état passe à dérive ou
                      anomalie de sévérité non critique (CU5, D2) ; la réponse de l'opérateur, donnée par
                      repondre(), est journalisée avec un instantané de
                      l'écran (EX-F-09).

Entrées par cycle :
  etat, confiance, contributrices   venant de SS-4
  mesures                           venant de SS-2 (bandeau des variables)
  attendus                          venant de SS-3

Sortie par cycle :
  affichage   str    texte affiché (vide s'il n'y a rien de nouveau)
  evenements  list   demandes de confirmation et réponses de l'opérateur ;
                     l'orchestrateur les transmet au journal de SS-6 (flux E)

Aucune sortie vers l'installation (EX-F-08) : ce module affiche et
journalise, il n'émet aucune commande.

Sévérité. La demande de confirmation est réservée aux états dérive ou
anomalie « de sévérité non critique » (D2). La criticité suit la synthèse
« Paramètres manquants selon la NRC » (logique MAVD et ADVOLM de
NUREG/CR-6895) : une variable désignée par SS-4 est critique quand son biais
estimé, la moyenne glissante de l'écart mesure − attendu sur
FENETRE_TENDANCE cycles, atteint SEUIL_CRITICITE de l'étendue du capteur
(PLAGES du contrat). Un état critique ne donne lieu à aucune demande : un
événement « etat_critique » est journalisé à la place. Une demande en attente
est retirée si l'état devient critique avant la réponse. Le seuil de 2,5 %
est la valeur proposée (plage 1 à 2,5 %), à confirmer par l'équipe.
"""
from __future__ import annotations

import hashlib
from collections import deque

from jumeau.contrat import PLAGES, UNITES, Etat, Statut, Variable
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

# Liste fermée des libellés descriptifs (tableau 7-3 du rapport de concept).
# Ils décrivent un constat et ne prescrivent jamais d'action.
LIBELLES_VARIABLES = (
    "température supérieure à l'attendu",
    "température inférieure à l'attendu",
    "température conforme à l'attendu",
    "pression supérieure à l'attendu",
    "pression inférieure à l'attendu",
    "pression conforme à l'attendu",
    "débit supérieur à l'attendu",
    "débit inférieur à l'attendu",
    "débit conforme à l'attendu",
    "température : mesure absente",
    "pression : mesure absente",
    "débit : mesure absente",
    "température : mesure hors plage",
    "pression : mesure hors plage",
    "débit : mesure hors plage",
    "température : valeur attendue indisponible",
    "pression : valeur attendue indisponible",
    "débit : valeur attendue indisponible",
)

ETATS_A_CONFIRMER = (Etat.DERIVE, Etat.ANOMALIE)
REPONSES = ("confirme", "refuse")
FENETRE_TENDANCE = 60  # cycles, soit 60 s à T = 1 s
SEUIL_CRITICITE = 0.025  # fraction de l'étendue du capteur (plage 1 à 2,5 %)
CRITIQUE, NON_CRITIQUE = "critique", "non_critique"


def libelle_variable(var: Variable, mesure, attendu: float | None) -> str:
    """Libellé descriptif d'une variable, toujours tiré de LIBELLES_VARIABLES."""
    nom = NOMS[var]
    if mesure.statut is Statut.ABSENT:
        texte = f"{nom} : mesure absente"
    elif mesure.statut is Statut.HORS_PLAGE:
        texte = f"{nom} : mesure hors plage"
    elif attendu is None:
        texte = f"{nom} : valeur attendue indisponible"
    else:
        feminin = var is not Variable.Q
        if mesure.valeur > attendu:
            sens = "supérieure" if feminin else "supérieur"
        elif mesure.valeur < attendu:
            sens = "inférieure" if feminin else "inférieur"
        else:
            sens = "conforme"
        texte = f"{nom} {sens} à l'attendu"
    assert texte in LIBELLES_VARIABLES, f"libellé hors de la liste fermée : {texte}"
    return texte


class PresentationEtat(SousSysteme):
    nom = "SS-5"

    def demarrer(self, contexte: dict) -> None:
        self.silencieux = contexte.get("silencieux", False)
        self.etat_affiche = None
        self.k_entree = None
        self.historique: list[tuple[int, Etat]] = []
        self.ecarts = {v: deque(maxlen=FENETRE_TENDANCE) for v in Variable}
        self.derniere_valide: dict = {v: None for v in Variable}
        self.demande: dict | None = None
        self.reponse: str | None = None
        self.dernieres_entrees: dict = {}

    # ----- Action de l'opérateur -------------------------------------------

    def repondre(self, reponse: str) -> None:
        """Réponse de l'opérateur à la demande en cours : « confirme » ou « refuse ».

        Elle est journalisée au cycle suivant, avec un instantané de l'écran.
        Aucune commande n'est émise vers l'installation.
        """
        if reponse not in REPONSES:
            raise ValueError(f"Réponse invalide : {reponse!r}. Réponses possibles : {REPONSES}.")
        if self.demande is None:
            raise ValueError("Aucune demande de confirmation en cours.")
        self.reponse = reponse

    # ----- Vues ------------------------------------------------------------

    def vue_permanente(self, k: int, entrees: dict) -> str:
        etat = entrees.get("etat", Etat.INCERTAIN)
        contributrices = entrees.get("contributrices", [])
        if contributrices:
            en_cause = ", ".join(NOMS[v] for v in contributrices)
        else:
            en_cause = "aucune" if etat is Etat.NORMAL else "aucune variable désignée"
        return (f"t={k:>5d} s  {SYMBOLES[etat]} {LIBELLES[etat]:<9} "
                f"confiance {entrees.get('confiance', 0.0):.0%}  variables en cause : {en_cause}")

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

    def biais_estime(self, var: Variable) -> float | None:
        """Moyenne glissante de l'écart mesure − attendu, en unités physiques."""
        e = self.ecarts[var]
        return sum(e) / len(e) if e else None

    def severite(self, contributrices) -> tuple[str, dict]:
        """Sévérité de l'état courant et biais estimé, en fraction de l'étendue, par variable désignée.

        Critique dès qu'une variable désignée atteint SEUIL_CRITICITE. Sans
        variable désignée ou sans écart connu, l'état est non critique.
        """
        biais = {}
        for var in contributrices:
            b = self.biais_estime(var)
            if b is not None:
                bas, haut = PLAGES[var]
                biais[var.value] = abs(b) / (haut - bas)
        critique = any(f >= SEUIL_CRITICITE for f in biais.values())
        return (CRITIQUE if critique else NON_CRITIQUE), biais

    def _tendance(self, var: Variable) -> str:
        e = list(self.ecarts[var])
        if len(e) < 2:
            return "tendance : historique insuffisant"
        moitie = len(e) // 2
        debut, fin = e[:moitie], e[moitie:]
        variation = sum(fin) / len(fin) - sum(debut) / len(debut)
        return f"tendance de l'écart {variation:+.3g} sur {len(e)} cycles"

    def vue_detail(self, entrees: dict | None = None) -> str:
        """Vue de détail (CU4) : une ligne par variable.

        Les variables désignées par SS-4 sont marquées « >> ». Sans variable
        désignée, la mention « aucune variable désignée » est affichée.
        """
        entrees = entrees if entrees is not None else self.dernieres_entrees
        if not entrees:
            return "Vue de détail : aucune donnée reçue."
        etat = entrees.get("etat", Etat.INCERTAIN)
        contributrices = entrees.get("contributrices", [])
        attendus = entrees.get("attendus") or {}
        lignes = [f"Vue de détail : {SYMBOLES[etat]} {LIBELLES[etat]}"]
        if etat is not Etat.NORMAL and not contributrices:
            lignes.append("  aucune variable désignée")
        for var in Variable:
            m = entrees["mesures"][var]
            attendu = attendus.get(var)
            marque = ">>" if var in contributrices else "  "
            if m.statut is Statut.VALIDE and attendu is not None:
                chiffres = (f"mesure {m.valeur:.4g} {UNITES[var]}, attendu {attendu:.4g} {UNITES[var]}, "
                            f"écart {m.valeur - attendu:+.3g}, {self._tendance(var)}")
            elif m.statut is Statut.VALIDE:
                chiffres = f"mesure {m.valeur:.4g} {UNITES[var]}"
            else:
                derniere = self.derniere_valide.get(var)
                chiffres = (f"dernière acquisition valide : {derniere}" if derniere
                            else "aucune acquisition valide reçue")
            lignes.append(f"  {marque} {libelle_variable(var, m, attendu)} : {chiffres}")
        return "\n".join(lignes)

    def ecran(self, k: int, entrees: dict) -> str:
        """Contenu complet de l'écran : sert d'instantané lors d'une confirmation."""
        return "\n".join([self.vue_permanente(k, entrees), self._bandeau(k, entrees), self.vue_detail(entrees)])

    # ----- Cycle -----------------------------------------------------------

    def etape(self, k: int, entrees: dict) -> dict:
        etat = entrees.get("etat", Etat.INCERTAIN)
        self.dernieres_entrees = entrees
        attendus = entrees.get("attendus") or {}
        for var, m in entrees["mesures"].items():
            if m.statut is Statut.VALIDE:
                self.derniere_valide[var] = m.horodatage_utc
                if attendus.get(var) is not None:
                    self.ecarts[var].append(m.valeur - attendus[var])

        lignes, evenements = [], []
        contributrices = entrees.get("contributrices", [])
        severite, biais = self.severite(contributrices)

        if etat is not self.etat_affiche:
            self.etat_affiche = etat
            self.k_entree = k
            self.historique.append((k, etat))
            lignes.append(self.vue_permanente(k, entrees))
            if self.demande is not None:
                # La demande portait sur un état qui n'est plus affiché.
                evenements.append({"type": "demande_confirmation_retiree", "k": k, "motif": "changement_etat",
                                   "etat_demande": self.demande["etat"], "nouvel_etat": etat.value})
                self.demande, self.reponse = None, None
            if etat in ETATS_A_CONFIRMER:
                variables = [v.value for v in contributrices]
                if severite == CRITIQUE:
                    evenements.append({"type": "etat_critique", "k": k, "etat": etat.value,
                                       "confiance": entrees.get("confiance", 0.0), "variables": variables,
                                       "biais_fraction_etendue": biais})
                    lignes.append(f"          -> Sévérité critique : aucune demande de confirmation "
                                  f"(biais estimé ≥ {SEUIL_CRITICITE:.1%} de l'étendue)")
                else:
                    self.demande = {"k": k, "etat": etat.value, "confiance": entrees.get("confiance", 0.0),
                                    "variables": variables, "severite": severite,
                                    "biais_fraction_etendue": biais}
                    evenements.append({"type": "demande_confirmation", **self.demande})
                    noms = ", ".join(NOMS[v] for v in contributrices) or "aucune variable désignée"
                    lignes.append(f"          -> Confirmation demandée : passage en fonctionnement dégradé ? "
                                  f"(état {LIBELLES[etat]}, confiance {entrees.get('confiance', 0.0):.0%}, "
                                  f"variables : {noms})")
        elif self.demande is not None and severite == CRITIQUE:
            # L'état est devenu critique avant la réponse : la demande ne s'applique plus.
            evenements.append({"type": "demande_confirmation_retiree", "k": k, "motif": "etat_critique",
                               "etat_demande": self.demande["etat"], "nouvel_etat": etat.value,
                               "biais_fraction_etendue": biais})
            lignes.append(f"t={k:>5d} s  Sévérité critique : demande de confirmation retirée")
            self.demande, self.reponse = None, None

        if self.reponse is not None:
            instantane = self.ecran(k, entrees)
            evenements.append({
                "type": "reponse_operateur", "k": k, "reponse": self.reponse,
                "demande_k": self.demande["k"], "etat": self.demande["etat"],
                "confiance": self.demande["confiance"], "variables": self.demande["variables"],
                "severite": self.demande["severite"], "instantane": instantane,
                "empreinte_instantane": hashlib.sha256(instantane.encode("utf-8")).hexdigest(),
            })
            verbe = "confirmé" if self.reponse == "confirme" else "refusé"
            lignes.append(f"t={k:>5d} s  Opérateur : passage en fonctionnement dégradé {verbe} (journalisé)")
            self.demande, self.reponse = None, None

        if k % 60 == 0:
            lignes.append(self._bandeau(k, entrees))

        texte = "\n".join(lignes)
        if texte and not self.silencieux:
            print(texte, flush=True)
        return {"affichage": texte, "evenements": evenements}
