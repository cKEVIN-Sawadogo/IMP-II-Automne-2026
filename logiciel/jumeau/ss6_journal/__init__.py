"""SS-6 : journal de données. Responsable : Djasra Wilson Thoroum.

Version minimale du concept B : une entrée par cycle dans une base SQLite,
en ajout seul. Chaque entrée contient l'empreinte SHA-256 de la précédente,
si bien qu'une modification après coup est détectée par verifier_journal().

Entrées par cycle (préparées par l'orchestrateur) :
  contenu  dict   mesures, résidus, état, événements du cycle (sérialisables)

Sortie par cycle :
  sequence  int   numéro de l'entrée
  empreinte str   empreinte SHA-256 de l'entrée

À faire par le responsable : scellement signé d'un bloc d'entrées par un rôle
distinct (concept C ajouté), intervalle de scellement, sceau final à l'arrêt
et détection d'un arrêt brutal au démarrage suivant (CU6).
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from jumeau.interface import SousSysteme

EMPREINTE_INITIALE = "0" * 64


def _empreinte(precedente: str, contenu_json: str) -> str:
    return hashlib.sha256((precedente + contenu_json).encode("utf-8")).hexdigest()


class JournalDonnees(SousSysteme):
    nom = "SS-6"

    def demarrer(self, contexte: dict) -> None:
        self.chemin = Path(contexte["sortie"]) / "journal.sqlite"
        if self.chemin.exists():
            raise FileExistsError(f"Le journal {self.chemin} existe déjà : il ne doit jamais être écrasé.")
        self.cx = sqlite3.connect(self.chemin)
        self.cx.execute(
            "CREATE TABLE journal (sequence INTEGER PRIMARY KEY, k INTEGER NOT NULL, "
            "contenu TEXT NOT NULL, empreinte_precedente TEXT NOT NULL, empreinte TEXT NOT NULL)"
        )
        self.derniere = EMPREINTE_INITIALE
        self.sequence = 0

    def etape(self, k: int, entrees: dict) -> dict:
        contenu = json.dumps(entrees["contenu"], ensure_ascii=False, sort_keys=True)
        empreinte = _empreinte(self.derniere, contenu)
        self.cx.execute("INSERT INTO journal VALUES (?, ?, ?, ?, ?)",
                        (self.sequence, k, contenu, self.derniere, empreinte))
        if self.sequence % 100 == 0:
            self.cx.commit()
        sortie = {"sequence": self.sequence, "empreinte": empreinte}
        self.derniere = empreinte
        self.sequence += 1
        return sortie

    def arreter(self) -> None:
        self.cx.commit()
        self.cx.close()


def verifier_journal(chemin: str | Path) -> tuple[bool, int | None, int]:
    """Recalcule toute la chaîne.

    Renvoie (intègre, première séquence fautive ou None, nombre d'entrées).
    """
    cx = sqlite3.connect(chemin)
    lignes = cx.execute(
        "SELECT sequence, contenu, empreinte_precedente, empreinte FROM journal ORDER BY sequence"
    ).fetchall()
    cx.close()
    precedente = EMPREINTE_INITIALE
    for attendu, (sequence, contenu, emp_prec, emp) in enumerate(lignes):
        if sequence != attendu or emp_prec != precedente or emp != _empreinte(precedente, contenu):
            return False, sequence, len(lignes)
        precedente = emp
    return True, None, len(lignes)
