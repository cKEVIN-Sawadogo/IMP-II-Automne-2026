"""Orchestrateur à pas fixe.

Il fait avancer les six sous-systèmes au même pas T, dans l'ordre SS-1,
SS-2, SS-3, SS-4, SS-5, puis l'écriture au journal (section 7.1 du rapport
de concept). C'est lui qui achemine les données d'un module à l'autre : la
règle « les grandeurs vraies ne vont jamais à SS-3 ni à SS-4 » est donc
garantie ici, par construction.
"""
from __future__ import annotations

import csv
import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from jumeau.contrat import T_CYCLE, Etat, Mesure, Statut, Variable
from jumeau.interface import SousSysteme
from jumeau.ss1_boucle import SimulateurBoucle
from jumeau.ss2_mesures import AcquisitionMesures
from jumeau.ss3_reference import ReferenceBoucleOuverte
from jumeau.ss4_decision import DecisionSequentielle
from jumeau.ss5_interface import PresentationEtat
from jumeau.ss6_journal import JournalDonnees


def modules_par_defaut() -> dict[str, SousSysteme]:
    return {
        "ss1": SimulateurBoucle(),
        "ss2": AcquisitionMesures(),
        "ss3": ReferenceBoucleOuverte(),
        "ss4": DecisionSequentielle(),
        "ss5": PresentationEtat(),
        "ss6": JournalDonnees(),
    }


def consignes_a(scenario: dict, t: float) -> dict:
    """Consignes en vigueur à l'instant t (flux F1)."""
    consignes = dict(scenario["consignes_initiales"])
    for changement in sorted(scenario.get("changements_consignes", []), key=lambda c: c["instant_s"]):
        if changement["instant_s"] <= t:
            consignes.update({c: v for c, v in changement.items() if c != "instant_s"})
    return consignes


def _serialiser(valeur):
    """Rend une sortie de module écrivable en JSON pour le journal."""
    if isinstance(valeur, Mesure):
        return valeur.en_dict()
    if isinstance(valeur, (Variable, Etat, Statut)):
        return valeur.value
    if isinstance(valeur, dict):
        return {(c.value if isinstance(c, (Variable, Etat, Statut)) else c): _serialiser(v)
                for c, v in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return [_serialiser(v) for v in valeur]
    return valeur


class Orchestrateur:
    def __init__(self, scenario: dict, sortie: str | Path, *, modules: dict | None = None,
                 silencieux: bool = False, tolerant: bool = False, temps_reel: bool = False):
        self.scenario = scenario
        self.sortie = Path(sortie)
        self.modules = modules or modules_par_defaut()
        self.silencieux = silencieux
        self.tolerant = tolerant      # True : un module en défaut ne coupe pas la chaîne
        self.temps_reel = temps_reel  # True : un cycle par seconde réelle

    def _appel(self, cle: str, k: int, entrees: dict, evenements: list) -> dict:
        module = self.modules[cle]
        try:
            return module.etape(k, entrees)
        except Exception as erreur:
            if not self.tolerant or cle == "ss6":
                raise
            # Un composant en défaut n'est jamais silencieux : il est journalisé,
            # et les modules en aval reçoivent des données absentes.
            evenements.append({"type": "defaut_composant", "module": module.nom,
                               "message": repr(erreur), "trace": traceback.format_exc(limit=3)})
            return {}

    def executer(self, cycles: int | None = None) -> dict:
        cycles = cycles if cycles is not None else self.scenario["cycles"]
        self.sortie.mkdir(parents=True, exist_ok=True)
        contexte = {"graine": self.scenario["graine"], "scenario": self.scenario,
                    "sortie": str(self.sortie), "silencieux": self.silencieux}
        for module in self.modules.values():
            module.demarrer(contexte)

        changements_etat = []
        consignes_prec = None
        with open(self.sortie / "verite.csv", "w", newline="", encoding="utf-8") as f_verite:
            verite = csv.writer(f_verite)
            verite.writerow(["k", "t_s", "T_C", "P_MPa", "Q_kg_s"])
            try:
                for k in range(cycles):
                    debut = time.monotonic()
                    t = k * T_CYCLE
                    horodatage = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
                    evenements: list = []

                    consignes = consignes_a(self.scenario, t)
                    if consignes != consignes_prec:
                        evenements.append({"type": "consignes", **consignes})
                        consignes_prec = consignes

                    # SS-1 : seule la boucle simulée voit les consignes et produit la vérité.
                    s1 = self._appel("ss1", k, {"consignes": consignes}, evenements)
                    vraies = s1.get("grandeurs_vraies")
                    if vraies is not None:
                        verite.writerow([k, t, vraies[Variable.T], vraies[Variable.P], vraies[Variable.Q]])

                    # SS-2 : seul module à recevoir les grandeurs vraies.
                    if vraies is not None:
                        s2 = self._appel("ss2", k, {"grandeurs_vraies": vraies,
                                                    "horodatage_utc": horodatage}, evenements)
                    else:
                        s2 = {}
                    mesures = s2.get("mesures") or {
                        v: Mesure(k, t, horodatage, v, None, Statut.ABSENT) for v in Variable}

                    # SS-3 : mesures et consignes, jamais les grandeurs vraies.
                    s3 = self._appel("ss3", k, {"mesures": mesures, "consignes": consignes}, evenements)

                    # SS-4 : résidus seulement.
                    s4 = self._appel("ss4", k, {"residus": s3.get("residus", {}),
                                                "pret": s3.get("pret", False)}, evenements)
                    etat = s4.get("etat", Etat.INCERTAIN)

                    # SS-5 : affichage, sans aucune sortie vers l'installation.
                    s5 = self._appel("ss5", k, {"etat": etat,
                                                "confiance": s4.get("confiance", 0.0),
                                                "contributrices": s4.get("contributrices", []),
                                                "mesures": mesures,
                                                "attendus": s3.get("attendus", {})}, evenements)

                    for sortie in (s1, s2, s3, s4, s5):
                        evenements.extend(sortie.get("evenements", []))
                    for ev in evenements:
                        if ev.get("type") == "changement_etat":
                            changements_etat.append({"k": k, "vers": ev["vers"], "variables": ev["variables"]})

                    # SS-6 : une entrée par cycle, en dernier.
                    contenu = _serialiser({
                        "k": k, "t": t, "horodatage_utc": horodatage, "consignes": consignes,
                        "mesures": list(mesures.values()), "residus": s3.get("residus", {}),
                        "etat": etat, "confiance": s4.get("confiance", 0.0),
                        "contributrices": s4.get("contributrices", []), "evenements": evenements,
                    })
                    self.modules["ss6"].etape(k, {"contenu": contenu})

                    if self.temps_reel:
                        time.sleep(max(0.0, T_CYCLE - (time.monotonic() - debut)))
            finally:
                for module in self.modules.values():
                    module.arreter()

        resume = {
            "scenario": self.scenario["nom"],
            "version_scenario": self.scenario.get("version"),
            "graine": self.scenario["graine"],
            "cycles": cycles,
            "changements_etat": changements_etat,
            "etat_final": changements_etat[-1]["vers"] if changements_etat else None,
        }
        (self.sortie / "resume.json").write_text(json.dumps(resume, indent=2, ensure_ascii=False),
                                                 encoding="utf-8")
        return resume
