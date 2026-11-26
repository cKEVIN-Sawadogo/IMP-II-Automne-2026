"""Exécution du jumeau complet pour l'interface web de SS-5.

L'essai tourne dans un fil d'exécution à part, avec l'orchestrateur tel quel.
Chaque sous-système est enveloppé par une enveloppe d'enregistrement qui
garde ses sorties cycle par cycle, sans rien changer à ce qu'il reçoit ni à
ce qu'il renvoie. L'interface lit ces enregistrements.

La seule action de l'interface sur le jumeau est la réponse de l'opérateur à
une demande de confirmation. Elle passe par PresentationEtat.repondre(),
exactement comme dans la version texte, et elle est journalisée par SS-6.
Aucune commande n'est émise vers l'installation (EX-F-08).

La cadence (×1, ×10, ×60 ou au plus vite), la pause et l'arrêt sont appliqués
après l'écriture au journal de chaque cycle : un cycle commencé est toujours
journalisé en entier.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime
from pathlib import Path

from jumeau.contrat import Variable
from jumeau.interface import SousSysteme
from jumeau.orchestrateur import Orchestrateur, modules_par_defaut
from jumeau.scenario import charger
from jumeau.ss5_interface import libelle_variable
from jumeau.ss6_journal import verifier as verifier_ss6
from jumeau.ss6_journal import verifier_journal

DOSSIER_SCENARIOS = Path(__file__).resolve().parents[2] / "scenarios"

# Cadences proposées, en cycles par seconde réelle. None : au plus vite.
VITESSES = {"1": 1.0, "10": 10.0, "60": 60.0, "max": None}

ORDRE_MODULES = ("ss1", "ss2", "ss3", "ss4", "ss5", "ss6")

PRET, EN_COURS, PAUSE, TERMINE, ARRETE, ERREUR = (
    "pret", "en_cours", "pause", "termine", "arrete", "erreur")


class ArretDemande(Exception):
    """L'essai a été arrêté depuis l'interface."""


def scenarios_disponibles() -> list[dict]:
    """Scénarios du dossier scenarios/, avec leur nom et leur description."""
    liste = []
    for chemin in sorted(DOSSIER_SCENARIOS.glob("*.json")):
        try:
            sc = charger(chemin)
        except (ValueError, OSError):
            continue
        liste.append({"chemin": str(chemin), "fichier": chemin.name, "nom": sc["nom"],
                      "description": sc.get("description", ""), "cycles": sc["cycles"]})
    return liste


class _Enveloppe(SousSysteme):
    """Transmet tout au module enveloppé et en garde la trace."""

    def __init__(self, cle: str, module: SousSysteme, session: "Session"):
        self.cle, self.module, self.session, self.nom = cle, module, session, module.nom

    def demarrer(self, contexte: dict) -> None:
        self.module.demarrer(contexte)

    def etape(self, k: int, entrees: dict) -> dict:
        debut = time.perf_counter()
        try:
            sortie = self.module.etape(k, entrees)
        except Exception as erreur:
            self.session._noter_defaut(self.cle, k, erreur)
            raise
        self.session._noter(self.cle, k, entrees, sortie, time.perf_counter() - debut)
        if self.cle == "ss6":
            self.session._cadencer(k)
        return sortie

    def arreter(self) -> None:
        self.module.arreter()


class Session:
    """Un essai à la fois, piloté depuis l'interface."""

    def __init__(self, dossier_sorties: str | Path = "sorties"):
        self.dossier_sorties = Path(dossier_sorties)
        self._verrou = threading.Lock()
        self._fil: threading.Thread | None = None
        self._pause = threading.Event()
        self._arret = threading.Event()
        self.vitesse: float | None = 1.0
        self._ref: tuple[float, int, float | None] | None = None
        self.a_la_fin = None  # fonction appelée avec la session quand l'essai se termine
        self._modules: dict = {}
        self._remettre_a_zero()

    # ----- État de l'enregistrement ----------------------------------------

    def _remettre_a_zero(self, scenario: dict | None = None, sortie: Path | None = None,
                         chemin: str | None = None) -> None:
        self.numero = getattr(self, "numero", 0) + (1 if scenario else 0)
        self.scenario = scenario
        self.chemin_scenario = chemin
        self.sortie = sortie
        self.statut = PRET
        self.erreur: str | None = None
        self.resume: dict | None = None
        self.debut_reel: float | None = None
        self.fin_reelle: float | None = None
        self._ss5 = None
        self._brouillon: dict = {}
        self.cycles_prevus = scenario["cycles"] if scenario else 0
        # Une liste par grandeur, un élément par cycle journalisé.
        self.k: list[int] = []
        self.horodatage: list[str] = []
        self.etat: list[str] = []
        self.confiance: list[float] = []
        self.contributrices: list[list[str]] = []
        self.pret: list[bool] = []
        self.vraie = {v.value: [] for v in Variable}
        self.mesure = {v.value: [] for v in Variable}
        self.statut_mesure = {v.value: [] for v in Variable}
        self.attendu = {v.value: [] for v in Variable}
        self.residu = {v.value: [] for v in Variable}
        self.somme_haut = {v.value: [] for v in Variable}
        self.somme_bas = {v.value: [] for v in Variable}
        self.evenements: list[dict] = []
        self.transitions: list[dict] = []
        self.ss5: dict = {}
        self.journal: dict = {"sequence": None, "empreinte": None}
        self.modules_stats = {c: {"nom": None, "cycles": 0, "duree_s": 0.0, "defauts": 0,
                                  "dernier_defaut": None} for c in ORDRE_MODULES}

    def _noter_defaut(self, cle: str, k: int, erreur: Exception) -> None:
        with self._verrou:
            st = self.modules_stats[cle]
            st["defauts"] += 1
            st["dernier_defaut"] = f"cycle {k} : {erreur!r}"

    def _noter(self, cle: str, k: int, entrees: dict, sortie: dict, duree: float) -> None:
        b = self._brouillon
        if cle == "ss1":
            b.clear()
            b["vraies"] = {v.value: x for v, x in sortie.get("grandeurs_vraies", {}).items()}
        elif cle == "ss3":
            b["attendus"] = {v.value: x for v, x in sortie.get("attendus", {}).items()}
            b["pret"] = sortie.get("pret", False)
        elif cle == "ss4":
            b["sommes"] = {v.value: s for v, s in sortie.get("sommes", {}).items()}
        elif cle == "ss5":
            b["ss5"] = self._lire_ss5(entrees)

        with self._verrou:
            st = self.modules_stats[cle]
            st["nom"] = st["nom"] or getattr(self._modules.get(cle), "nom", cle)
            st["cycles"] += 1
            st["duree_s"] += duree
            if cle == "ss6":
                self._enregistrer_cycle(k, entrees["contenu"], sortie)

    def _lire_ss5(self, entrees: dict) -> dict:
        """Ce que SS-5 a calculé ce cycle, lu dans le même fil que lui."""
        ss5 = self._ss5
        attendus = entrees.get("attendus") or {}
        contributrices = entrees.get("contributrices", [])
        severite, biais = ss5.severite(contributrices)
        return {
            "etat_affiche": ss5.etat_affiche.value if ss5.etat_affiche else None,
            "k_entree": ss5.k_entree,
            "demande": dict(ss5.demande) if ss5.demande else None,
            "severite": severite,
            "biais": biais,
            "tendance": {v.value: ss5._tendance(v) for v in Variable},
            "derniere_valide": {v.value: ss5.derniere_valide.get(v) for v in Variable},
            "libelle": {v.value: libelle_variable(v, entrees["mesures"][v], attendus.get(v))
                        for v in Variable},
        }

    def _enregistrer_cycle(self, k: int, contenu: dict, sortie_ss6: dict) -> None:
        b = self._brouillon
        self.k.append(k)
        self.horodatage.append(contenu["horodatage_utc"])
        self.etat.append(contenu["etat"])
        self.confiance.append(float(contenu["confiance"]))
        self.contributrices.append(list(contenu["contributrices"]))
        self.pret.append(bool(b.get("pret", False)))
        mesures = {m["variable"]: m for m in contenu["mesures"]}
        for v in self.mesure:
            m = mesures.get(v, {})
            self.vraie[v].append(b.get("vraies", {}).get(v))
            self.mesure[v].append(m.get("valeur"))
            self.statut_mesure[v].append(m.get("statut", "absent"))
            self.attendu[v].append(b.get("attendus", {}).get(v))
            self.residu[v].append(contenu["residus"].get(v))
            s = b.get("sommes", {}).get(v, {})
            self.somme_haut[v].append(s.get("haut"))
            self.somme_bas[v].append(s.get("bas"))
        for ev in contenu["evenements"]:
            ev = {"cycle": k, "horodatage_utc": contenu["horodatage_utc"], **ev}
            self.evenements.append(ev)
            if ev.get("type") == "changement_etat":
                self.transitions.append({"k": k, "horodatage_utc": contenu["horodatage_utc"],
                                         "de": ev.get("de"), "vers": ev["vers"],
                                         "variables": ev.get("variables", []),
                                         "confiance": float(contenu["confiance"])})
        if "ss5" in b:
            self.ss5 = b["ss5"]
        self.journal = dict(sortie_ss6)

    # ----- Cadence ---------------------------------------------------------

    def _cadencer(self, k: int) -> None:
        while self._pause.is_set() and not self._arret.is_set():
            time.sleep(0.05)
            self._ref = None
        if self._arret.is_set():
            raise ArretDemande()
        v = self.vitesse
        maintenant = time.monotonic()
        if v is None:
            self._ref = None
            if k % 50 == 0:
                time.sleep(0)  # laisse respirer le serveur web
            return
        if self._ref is None or self._ref[2] != v or maintenant - (self._ref[0] + (k - self._ref[1]) / v) > 1.0:
            self._ref = (maintenant, k, v)
            return
        cible = self._ref[0] + (k - self._ref[1]) / v
        while not self._arret.is_set() and not self._pause.is_set():
            reste = cible - time.monotonic()
            if reste <= 0:
                break
            time.sleep(min(reste, 0.05))

    # ----- Commandes de l'interface ----------------------------------------

    @property
    def actif(self) -> bool:
        return self._fil is not None and self._fil.is_alive()

    def lancer(self, chemin_scenario: str | Path, *, vitesse: float | None = 1.0,
               cycles: int | None = None, tolerant: bool = False, silencieux: bool = True,
               sortie: str | Path | None = None) -> None:
        if self.actif:
            self.arreter(attendre=True)
        scenario = charger(chemin_scenario)
        nom = Path(chemin_scenario).stem
        sortie = Path(sortie) if sortie else self.dossier_sorties / f"{nom}_{datetime.now():%Y%m%d-%H%M%S}"
        with self._verrou:
            self._remettre_a_zero(scenario, sortie, str(chemin_scenario))
            if cycles:
                self.cycles_prevus = cycles
            modules = modules_par_defaut()
            self._modules = modules
            self._ss5 = modules["ss5"]
            enveloppes = {c: _Enveloppe(c, m, self) for c, m in modules.items()}
            self.vitesse = vitesse
            self._ref = None
            self._pause.clear()
            self._arret.clear()
            self.statut = EN_COURS
            self.debut_reel = time.time()
        orch = Orchestrateur(scenario, sortie, modules=enveloppes, silencieux=silencieux,
                             tolerant=tolerant, temps_reel=False)
        self._fil = threading.Thread(target=self._executer, args=(orch, cycles), daemon=True,
                                     name="jumeau")
        self._fil.start()

    def _executer(self, orch: Orchestrateur, cycles: int | None) -> None:
        try:
            self.resume = orch.executer(cycles)
            self.statut = TERMINE
        except ArretDemande:
            self.statut = ARRETE
        except Exception as erreur:  # l'essai s'arrête, l'interface reste ouverte
            self.erreur = repr(erreur)
            self.statut = ERREUR
        finally:
            self.fin_reelle = time.time()
            if self.a_la_fin:
                try:
                    self.a_la_fin(self)
                except Exception:
                    pass

    def mettre_en_pause(self) -> None:
        if self.actif:
            self._pause.set()
            self.statut = PAUSE

    def reprendre(self) -> None:
        if self.actif:
            self._pause.clear()
            self.statut = EN_COURS

    def arreter(self, attendre: bool = False) -> None:
        self._arret.set()
        self._pause.clear()
        if attendre and self._fil is not None:
            self._fil.join(timeout=10)

    def regler_vitesse(self, vitesse: float | None) -> None:
        self.vitesse = vitesse
        self._ref = None

    def repondre(self, reponse: str) -> str:
        """Transmet la réponse de l'opérateur à SS-5. Renvoie un message d'état."""
        if self._ss5 is None or not self.actif:
            return "Aucun essai en cours."
        try:
            self._ss5.repondre(reponse)
        except ValueError as erreur:
            return str(erreur)
        verbe = "confirmé" if reponse == "confirme" else "refusé"
        return f"Passage en fonctionnement dégradé {verbe}. Réponse journalisée au cycle suivant."

    def verifier_journal(self) -> tuple[bool, int | None, int] | None:
        if self.sortie is None:
            return None
        chemin = self.sortie / "journal.sqlite"
        if not chemin.exists():
            return None
        return verifier_journal(chemin)

    def rapport_journal(self):
        """Rapport complet du vérificateur de SS-6 (chaîne, sceaux, complétude), ou None."""
        if self.sortie is None or not (self.sortie / "journal.sqlite").exists():
            return None
        return verifier_ss6(self.sortie)

    # ----- Lecture pour l'interface ----------------------------------------

    def instantane(self, complet: bool = False, fenetre: int = 300) -> dict:
        """Copie cohérente des enregistrements.

        complet=False : dernier cycle, transitions, et les `fenetre` derniers
        cycles des écarts (assez pour la vue de conduite).
        """
        with self._verrou:
            n = len(self.k)
            debut = 0 if complet else max(0, n - fenetre)
            tranche = slice(debut, n)
            serie = lambda d: {v: x[tranche] for v, x in d.items()}  # noqa: E731
            return {
                "numero": self.numero,
                "statut": self.statut,
                "erreur": self.erreur,
                "scenario": self.scenario,
                "chemin_scenario": self.chemin_scenario,
                "sortie": str(self.sortie) if self.sortie else None,
                "vitesse": self.vitesse,
                "cycles_prevus": self.cycles_prevus,
                "n": n,
                "debut_reel": self.debut_reel,
                "fin_reelle": self.fin_reelle,
                "k": self.k[tranche],
                "horodatage": self.horodatage[tranche],
                "etat": self.etat[tranche],
                "confiance": self.confiance[tranche],
                "contributrices": self.contributrices[tranche],
                "pret": self.pret[tranche],
                "vraie": serie(self.vraie),
                "mesure": serie(self.mesure),
                "statut_mesure": serie(self.statut_mesure),
                "attendu": serie(self.attendu),
                "residu": serie(self.residu),
                "somme_haut": serie(self.somme_haut),
                "somme_bas": serie(self.somme_bas),
                "transitions": list(self.transitions),
                "evenements": list(self.evenements) if complet else self.evenements[-400:],
                "nb_evenements": len(self.evenements),
                "ss5": dict(self.ss5),
                "journal": dict(self.journal),
                "modules": {c: dict(s) for c, s in self.modules_stats.items()},
                "resume": self.resume,
            }
