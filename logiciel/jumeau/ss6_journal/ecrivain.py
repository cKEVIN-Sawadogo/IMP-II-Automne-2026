"""SS-6 : l'écrivain du journal.

À chaque cycle, on ajoute une entrée dans journal.sqlite. Chaque entrée garde
l'empreinte de l'entrée d'avant, ce qui forme une chaîne :
    empreinte(i) = SHA-256(empreinte(i-1) + contenu(i))
La première entrée pointe vers EMPREINTE_INITIALE (64 zéros).

L'écrivain n'a aucune clé. Au démarrage, il lance le scelleur (scelleur.py)
dans un autre processus. Tous les 60 cycles, il lui demande de signer la
dernière empreinte ; à l'arrêt normal, il demande le sceau final.
"""
from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from jumeau.interface import SousSysteme

EMPREINTE_INITIALE = "0" * 64
PERIODE_SCEAU = 60      # un sceau tous les 60 cycles
NOM_JOURNAL = "journal.sqlite"
NOM_SCEAUX = "sceaux.sqlite"
NOM_DOSSIER_CLES = "cles_ss6"


def _empreinte(precedente: str, contenu_json: str) -> str:
    return hashlib.sha256((precedente + contenu_json).encode("utf-8")).hexdigest()


def en_json(valeur):
    """Transforme les objets du contrat (Variable, Etat, Mesure, numpy...)
    en types simples que json sait écrire. L'orchestrateur le fait déjà ;
    on le refait ici pour qu'un module qui écrit directement au journal
    (la démo de SS-5, par exemple) n'ait pas à y penser."""
    if isinstance(valeur, enum.Enum):
        return en_json(valeur.value)
    if dataclasses.is_dataclass(valeur) and not isinstance(valeur, type):
        return en_json(dataclasses.asdict(valeur))
    if isinstance(valeur, dict):
        resultat = {}
        for cle, v in valeur.items():
            if isinstance(cle, enum.Enum):   # Variable.T devient "T"
                cle = cle.value
            resultat[str(cle)] = en_json(v)
        return resultat
    if isinstance(valeur, (list, tuple)):
        return [en_json(v) for v in valeur]
    if isinstance(valeur, Path):
        return str(valeur)
    if hasattr(valeur, "tolist"):   # nombres et tableaux numpy
        return valeur.tolist()
    return valeur


def dossier_cles(sortie) -> Path:
    """Les clés vont dans « cles_ss6 », à côté du dossier de l'essai
    (sorties/cles_ss6 avec lancer.py), sauf si la variable d'environnement
    JUMEAU_CLES_SS6 donne un autre dossier."""
    if os.environ.get("JUMEAU_CLES_SS6"):
        return Path(os.environ["JUMEAU_CLES_SS6"])
    return Path(sortie).resolve().parent / NOM_DOSSIER_CLES


class JournalDonnees(SousSysteme):
    nom = "SS-6"

    def __init__(self, periode_sceau: int = PERIODE_SCEAU):
        super().__init__()
        self.periode_sceau = periode_sceau
        self.cx = None
        self.scelleur = None

    def demarrer(self, contexte: dict) -> None:
        sortie = Path(contexte["sortie"])
        sortie.mkdir(parents=True, exist_ok=True)
        self.chemin = sortie / NOM_JOURNAL
        if self.chemin.exists() or (sortie / NOM_SCEAUX).exists():
            raise FileExistsError(f"Le journal {self.chemin} existe déjà : il ne doit jamais être écrasé.")

        self.cx = sqlite3.connect(self.chemin)
        # Mode WAL : le scelleur et l'interface peuvent lire pendant qu'on écrit.
        self.cx.execute("PRAGMA journal_mode=WAL")
        self.cx.execute("PRAGMA synchronous=NORMAL")
        self.cx.execute(
            "CREATE TABLE journal (sequence INTEGER PRIMARY KEY, k INTEGER NOT NULL, "
            "contenu TEXT NOT NULL, empreinte_precedente TEXT NOT NULL, empreinte TEXT NOT NULL)"
        )
        self.cx.commit()
        self.derniere = EMPREINTE_INITIALE
        self.sequence = 0

        cles = contexte.get("cles") or dossier_cles(sortie)
        self.scelleur = LienScelleur(self.chemin, sortie / NOM_SCEAUX, Path(cles))

    def etape(self, k: int, entrees: dict) -> dict:
        contenu = json.dumps(en_json(entrees["contenu"]), ensure_ascii=False, sort_keys=True)
        empreinte = _empreinte(self.derniere, contenu)
        self.cx.execute("INSERT INTO journal VALUES (?, ?, ?, ?, ?)",
                        (self.sequence, k, contenu, self.derniere, empreinte))
        self.cx.commit()  # validé à chaque cycle : le journal d'abord, l'affichage ensuite
        sortie = {"sequence": self.sequence, "empreinte": empreinte}
        self.derniere = empreinte
        self.sequence += 1

        if self.sequence % self.periode_sceau == 0:
            self.scelleur.demander(sortie["sequence"])
        return sortie

    def arreter(self) -> None:
        if self.cx is None:
            return   # pas démarré, ou déjà arrêté
        self.cx.commit()
        if self.scelleur is not None:
            self.scelleur.finir(self.sequence - 1)   # sceau final (arrêt normal)
            self.scelleur = None
        self.cx.close()
        self.cx = None


class LienScelleur:
    """Lance scelleur.py dans un autre processus et lui envoie les ordres
    « SCELLER n » et « FINAL n » par son entrée standard."""

    def __init__(self, journal: Path, sceaux: Path, cles: Path):
        programme = Path(__file__).parent / "scelleur.py"
        self.proc = subprocess.Popen(
            [sys.executable, str(programme), str(journal), str(sceaux), str(cles)],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, encoding="utf-8")
        self.en_panne = False

    def envoyer(self, ordre: str) -> None:
        if self.en_panne:
            return
        try:
            self.proc.stdin.write(ordre + "\n")
            self.proc.stdin.flush()
        except (OSError, ValueError):
            # Le scelleur ne répond plus : on continue d'écrire le journal (il ne doit
            # jamais bloquer le cycle), mais on le signale. Le vérificateur verra les
            # entrées sans sceau.
            self.en_panne = True
            print("SS-6 : le scelleur ne répond plus, les prochains cycles ne seront pas scellés",
                  file=sys.stderr)

    def demander(self, seq_fin: int) -> None:
        self.envoyer(f"SCELLER {seq_fin}")

    def finir(self, seq_fin: int) -> None:
        self.envoyer(f"FINAL {seq_fin}")
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        # On attend que le scelleur ait fini d'écrire ses sceaux.
        try:
            code = self.proc.wait(timeout=60)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            code = None
        if code != 0:
            print(f"SS-6 : le scelleur s'est arrêté avec le code {code}, sceau final non garanti",
                  file=sys.stderr)
