"""SS-6 : le scelleur.

C'est le seul programme qui lit la clé privée (décision du 19 novembre).
L'écrivain le lance dans un autre processus au démarrage de l'essai :
    python scelleur.py journal.sqlite sceaux.sqlite dossier_cles
puis lui envoie un ordre par ligne :
    SCELLER n   signer l'empreinte de la ligne n
    FINAL n     poser le sceau final, puis s'arrêter
Si le programme principal est coupé net, l'entrée se ferme sans FINAL :
on s'arrête alors sans sceau final, et le vérificateur le verra.

Les sceaux vont dans sceaux.sqlite, une base que l'écrivain n'ouvre jamais.
Ce fichier n'importe rien de jumeau, pour pouvoir tourner tout seul.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

NOM_CLE_PRIVEE = "cle_privee_ss6.pem"
NOM_CLE_PUBLIQUE = "cle_publique_ss6.pem"
EMPREINTE_INITIALE = "0" * 64


def message_sceau(numero, seq_debut, seq_fin, empreinte, final, horodatage) -> bytes:
    """Ce qui est signé. On signe tous les champs du sceau, pas seulement
    l'empreinte : comme ça, personne ne peut changer « final » après coup."""
    donnees = {"numero": numero, "seq_debut": seq_debut, "seq_fin": seq_fin,
               "empreinte": empreinte, "final": bool(final), "horodatage": horodatage}
    return json.dumps(donnees, sort_keys=True, separators=(",", ":")).encode("utf-8")


def charger_ou_creer_cle(dossier: Path):
    # Importé ici pour que le reste de jumeau marche même sans cryptography.
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    dossier.mkdir(parents=True, exist_ok=True)
    chemin_prive = dossier / NOM_CLE_PRIVEE
    if not chemin_prive.exists():
        # Première fois : on crée la paire de clés Ed25519.
        pem = Ed25519PrivateKey.generate().private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())
        try:
            # 0o600 : seul l'utilisateur peut lire la clé privée.
            fd = os.open(chemin_prive, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(pem)
        except FileExistsError:
            pass   # un autre scelleur vient de la créer

    cle = serialization.load_pem_private_key(chemin_prive.read_bytes(), password=None)

    # La clé publique est celle que le vérificateur utilise.
    publique = cle.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    chemin_public = dossier / NOM_CLE_PUBLIQUE
    if not chemin_public.exists() or chemin_public.read_bytes() != publique:
        chemin_public.write_bytes(publique)
    return cle


class Scelleur:
    def __init__(self, journal: Path, sceaux: Path, cles: Path):
        self.cle = charger_ou_creer_cle(cles)
        # Journal ouvert en lecture seule : le scelleur ne peut rien y changer.
        self.journal = sqlite3.connect(journal.resolve().as_uri() + "?mode=ro", uri=True)
        self.sceaux = sqlite3.connect(sceaux)
        self.sceaux.execute("CREATE TABLE IF NOT EXISTS sceaux (numero INTEGER PRIMARY KEY,"
                            " seq_debut INTEGER NOT NULL, seq_fin INTEGER NOT NULL,"
                            " empreinte TEXT NOT NULL, final INTEGER NOT NULL,"
                            " horodatage TEXT NOT NULL, signature TEXT NOT NULL)")
        self.sceaux.commit()
        self.numero = 0
        self.dernier_fin = -1   # dernière ligne déjà couverte par un sceau

    def sceller(self, seq_fin: int, final: bool = False) -> None:
        if seq_fin <= self.dernier_fin and not final:
            return   # déjà scellé

        if seq_fin < 0:
            emp = EMPREINTE_INITIALE   # journal vide
        else:
            ligne = self.journal.execute("SELECT empreinte FROM journal WHERE sequence = ?",
                                         (seq_fin,)).fetchone()
            if ligne is None:
                print(f"SS-6 scelleur : la ligne {seq_fin} n'existe pas, pas de sceau", file=sys.stderr)
                return
            emp = ligne[0]

        heure = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        debut = self.dernier_fin + 1
        signature = self.cle.sign(message_sceau(self.numero, debut, seq_fin, emp, final, heure)).hex()
        with self.sceaux:
            self.sceaux.execute("INSERT INTO sceaux VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (self.numero, debut, seq_fin, emp, int(final), heure, signature))
        self.numero += 1
        self.dernier_fin = max(self.dernier_fin, seq_fin)


def main(arguments: list[str]) -> int:
    journal, sceaux, cles = [Path(a) for a in arguments]
    scelleur = Scelleur(journal, sceaux, cles)
    try:
        # On lit les ordres de l'écrivain jusqu'à FINAL ou jusqu'à la fin de l'entrée.
        for ligne in sys.stdin:
            ordre, _, n = ligne.strip().partition(" ")
            if ordre == "SCELLER":
                scelleur.sceller(int(n))
            elif ordre == "FINAL":
                scelleur.sceller(int(n), final=True)
                break
    finally:
        scelleur.journal.close()
        scelleur.sceaux.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
