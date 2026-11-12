"""Tests des règles d'architecture qui ne doivent jamais être cassées."""
from __future__ import annotations

import pytest

from jumeau.contrat import Mesure, Statut, Variable
from jumeau.interface import SousSysteme
from jumeau.orchestrateur import Orchestrateur, modules_par_defaut
from jumeau.scenario import charger
from pathlib import Path

SCENARIOS = Path(__file__).resolve().parent.parent / "scenarios"


def test_une_absence_n_est_jamais_codee_par_zero():
    with pytest.raises(ValueError):
        Mesure(0, 0.0, "2026-11-09T00:00:00Z", Variable.T, 0.0, Statut.ABSENT)
    with pytest.raises(ValueError):
        Mesure(0, 0.0, "2026-11-09T00:00:00Z", Variable.T, None, Statut.VALIDE)


class Espion(SousSysteme):
    """Enveloppe un module et retient toutes les clés qu'il a reçues."""

    def __init__(self, module):
        self.module, self.nom, self.cles = module, module.nom, set()

    def demarrer(self, contexte):
        self.module.demarrer(contexte)

    def etape(self, k, entrees):
        self.cles |= set(entrees)
        return self.module.etape(k, entrees)

    def arreter(self):
        self.module.arreter()


def test_les_grandeurs_vraies_ne_vont_jamais_a_ss3_ni_a_ss4(tmp_path):
    modules = modules_par_defaut()
    espions = {c: Espion(modules[c]) for c in ("ss3", "ss4")}
    modules.update(espions)
    Orchestrateur(charger(SCENARIOS / "derive_lente.json"), tmp_path, modules=modules,
                  silencieux=True).executer(50)
    for espion in espions.values():
        assert "grandeurs_vraies" not in espion.cles


class EnPanne(SousSysteme):
    nom = "SS-3"

    def etape(self, k, entrees):
        raise RuntimeError("panne simulée")


def test_un_module_en_panne_n_est_jamais_silencieux(tmp_path):
    modules = modules_par_defaut()
    modules["ss3"] = EnPanne()
    resume = Orchestrateur(charger(SCENARIOS / "nominal.json"), tmp_path, modules=modules,
                           silencieux=True, tolerant=True).executer(20)
    assert resume["etat_final"] == "incertain"


def test_sans_mode_tolerant_une_panne_arrete_l_essai(tmp_path):
    modules = modules_par_defaut()
    modules["ss3"] = EnPanne()
    with pytest.raises(RuntimeError):
        Orchestrateur(charger(SCENARIOS / "nominal.json"), tmp_path, modules=modules,
                      silencieux=True).executer(5)
