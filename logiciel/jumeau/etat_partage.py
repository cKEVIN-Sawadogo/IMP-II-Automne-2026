"""État partagé entre l'orchestrateur et l'interface de l'opérateur.

Architecture retenue le 19 novembre (section 3.5 du rapport 13) :

    orchestrateur ──① écrit le cycle──► journal SS-6 (seule source de vérité)
          │
          └──② publie le cycle──► CacheEtat ──lu chaque seconde──► interface (Dash)
          ▲                                                             │
          └──③ prend les réponses au cycle suivant── FileConfirmations ◄┘

Règles :
1. Le journal fait foi. Le cache n'est qu'une copie des derniers cycles, publiée
   APRÈS l'écriture au journal : l'opérateur ne voit jamais rien qui ne soit
   déjà journalisé.
2. Le cache est jetable. Au redémarrage de l'interface, il se recharge depuis le
   journal (recharger_depuis_journal).
3. L'interface ne parle jamais aux sous-systèmes. Elle lit le cache et dépose
   les réponses de l'opérateur dans la file ; l'orchestrateur les prend au début
   du cycle suivant et les fait journaliser (EX-F-09). Aucune commande ne sort.
4. Tous les accès passent par un verrou, et l'interface reçoit des copies : le
   calcul et l'affichage ne se bloquent pas l'un l'autre.
"""
from __future__ import annotations

import copy
import json
import queue
import sqlite3
import threading
from collections import deque
from pathlib import Path

TAILLE_HISTORIQUE = 600  # cycles gardés en mémoire, soit 10 minutes à T = 1 s


class CacheEtat:
    """Copie en mémoire des derniers cycles journalisés, pour l'affichage."""

    def __init__(self, taille: int = TAILLE_HISTORIQUE):
        self._verrou = threading.Lock()
        self._cycles: deque[dict] = deque(maxlen=taille)

    def publier(self, cycle: dict) -> None:
        """Appelé par l'orchestrateur, une fois le cycle écrit au journal."""
        copie = copy.deepcopy(cycle)
        with self._verrou:
            self._cycles.append(copie)

    def dernier(self) -> dict | None:
        """Le cycle le plus récent, ou None avant le premier cycle."""
        with self._verrou:
            return copy.deepcopy(self._cycles[-1]) if self._cycles else None

    def historique(self, n: int | None = None) -> list[dict]:
        """Les n derniers cycles (tous si n est None), du plus ancien au plus récent."""
        with self._verrou:
            cycles = list(self._cycles)
        if n is not None:
            cycles = cycles[-n:] if n > 0 else []
        return copy.deepcopy(cycles)

    def __len__(self) -> int:
        with self._verrou:
            return len(self._cycles)

    def recharger_depuis_journal(self, chemin_journal: str | Path) -> int:
        """Remplit le cache avec les derniers cycles du journal, en lecture seule.

        Sert au redémarrage de l'interface : aucun historique n'est perdu.
        Renvoie le nombre de cycles rechargés.
        """
        uri = f"file:{Path(chemin_journal).as_posix()}?mode=ro"
        cx = sqlite3.connect(uri, uri=True)
        try:
            lignes = cx.execute(
                "SELECT sequence, contenu, empreinte FROM journal ORDER BY sequence DESC LIMIT ?",
                (self._cycles.maxlen,),
            ).fetchall()
        finally:
            cx.close()
        cycles = []
        for sequence, contenu, empreinte in reversed(lignes):
            cycle = json.loads(contenu)
            cycle["sequence"], cycle["empreinte"] = sequence, empreinte
            cycles.append(cycle)
        with self._verrou:
            self._cycles.clear()
            self._cycles.extend(cycles)
        return len(cycles)


class FileConfirmations:
    """Réponses de l'opérateur, déposées par l'interface et prises par l'orchestrateur."""

    def __init__(self):
        self._file: queue.Queue[dict] = queue.Queue()

    def deposer(self, reponse: dict) -> None:
        """Appelé par l'interface. La réponse dit à quelle demande elle répond et ce qui a été
        répondu : {"k_demande": 1267, "decision": "confirme"} ou « refuse ». La demande en cours
        est publiée dans le cache sous « demande_en_cours » ; k_demande reprend son champ « k »."""
        self._file.put(copy.deepcopy(reponse))

    def prendre_toutes(self) -> list[dict]:
        """Appelé par l'orchestrateur au début d'un cycle : vide la file, sans attendre."""
        reponses = []
        while True:
            try:
                reponses.append(self._file.get_nowait())
            except queue.Empty:
                return reponses
