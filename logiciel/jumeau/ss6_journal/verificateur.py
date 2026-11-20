"""SS-6 : le vérificateur.

On le lance après l'essai. Il a seulement la clé publique : il peut vérifier
les sceaux, mais pas en fabriquer. Il fait cinq contrôles (rapport 12, 2.6) :

Intégrité (le journal n'a pas été modifié après coup) :
 (1) l'empreinte recalculée de chaque entrée est celle enregistrée ;
 (2) les numéros d'entrée se suivent et chaque entrée pointe vers la précédente ;
 (3) chaque sceau a une signature valide et correspond bien au journal ;
 (4) les sceaux couvrent tout le journal, sans trou, et le sceau final est là.

Complétude (il ne manque rien au journal) :
 (5) une entrée par cycle (EX-Q-02), un événement « changement_etat » de SS-4
     à chaque changement d'état (EX-F-10), et une suite donnée à chaque
     confirmation de l'opérateur reçue (EX-F-09).

verifier_journal() ne rend que l'intégrité (contrôles 1 à 4), comme avant.
verifier() rend le rapport complet, utilisé par « python lancer.py --verifier ».
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Pour pouvoir aussi le lancer avec « python verificateur.py dossier/ ».
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from jumeau.ss6_journal.ecrivain import (EMPREINTE_INITIALE, NOM_JOURNAL, NOM_SCEAUX,
                                         _empreinte, dossier_cles)
from jumeau.ss6_journal.scelleur import NOM_CLE_PUBLIQUE, message_sceau

# Ce qui doit suivre une confirmation reçue, dans la même entrée : la réponse
# journalisée par SS-5, ou la raison pour laquelle elle est restée sans effet.
SUITES_CONFIRMATION = {"reponse_operateur", "confirmation_sans_effet", "demande_confirmation_retiree"}


@dataclass
class Rapport:
    entrees: int = 0
    sceaux: int = 0
    sceaux_rejetes: int = 0
    transitions: int = 0      # changements d'état vus d'une entrée à l'autre
    changements: int = 0      # événements « changement_etat » journalisés
    confirmations: int = 0    # confirmations de l'opérateur reçues
    reponses: int = 0         # réponses de l'opérateur journalisées par SS-5
    sceau_final: bool = False
    anomalies: list = field(default_factory=list)   # intégrité : (seq ou None, message)
    manques: list = field(default_factory=list)     # complétude : (seq ou None, message)

    @property
    def integre(self) -> bool:
        return not self.anomalies

    @property
    def complet(self) -> bool:
        return not self.manques

    @property
    def valide(self) -> bool:
        return self.integre and self.complet

    @property
    def verdict(self) -> str:
        if not self.integre:
            return "ALTÉRÉ OU INCOMPLET"
        if not self.complet:
            return "INTÈGRE MAIS INCOMPLET"   # rien n'a été modifié, mais il manque quelque chose
        return "INTÈGRE"

    @property
    def premiere_fautive(self):
        """Plus petit numéro d'entrée qui pose un problème d'intégrité (None s'il n'y en a pas)."""
        seqs = [seq for seq, _ in self.anomalies if seq is not None]
        return min(seqs) if seqs else None

    def texte(self, max_affiche=None) -> str:
        lignes = [
            f"Verdict : {self.verdict}",
            f"entrées={self.entrees} sceaux={self.sceaux} transitions={self.transitions} "
            f"CHANGEMENT_ETAT={self.changements} confirmations={self.confirmations} "
            f"sceau final={'oui' if self.sceau_final else 'non'}",
        ]
        problemes = self.anomalies + self.manques
        a_montrer = problemes if max_affiche is None else problemes[:max_affiche]
        for _, message in a_montrer:
            lignes.append(f"! {message}")
        if len(problemes) > len(a_montrer):
            lignes.append(f"... {len(problemes) - len(a_montrer)} autre(s) problème(s)")
        return "\n".join(lignes)


def verifier(chemin, cle_publique=None, cycles_attendus=None) -> Rapport:
    """Vérifie un essai. `chemin` : le dossier de l'essai ou son journal.sqlite."""
    chemin = Path(chemin)
    journal = chemin / NOM_JOURNAL if chemin.is_dir() else chemin
    if not journal.exists():
        raise FileNotFoundError(journal)
    if cle_publique is None:
        cle_publique = dossier_cles(journal.parent) / NOM_CLE_PUBLIQUE

    r = Rapport()
    cx = sqlite3.connect(f"file:{journal.as_posix()}?mode=ro", uri=True)
    try:
        lignes = cx.execute("SELECT sequence, k, contenu, empreinte_precedente, empreinte "
                            "FROM journal ORDER BY sequence").fetchall()
    finally:
        cx.close()
    r.entrees = len(lignes)

    # ---- Contrôles (1), (2) et (5) : on parcourt les entrées une par une.
    empreintes = {}
    seq_attendue, precedente = 0, EMPREINTE_INITIALE
    k_prec = etat_prec = None
    for seq, k, contenu, emp_prec, emp in lignes:
        if seq != seq_attendue:
            r.anomalies.append((seq_attendue, f"seq {seq_attendue} : entrée absente ou séquence rompue (lu seq {seq})"))
        if emp_prec != precedente:
            r.anomalies.append((seq, f"seq {seq} : maillon rompu (empreinte_precedente ne correspond pas)"))
        if _empreinte(emp_prec, contenu) != emp:
            r.anomalies.append((seq, f"seq {seq} : empreinte recalculée différente (contenu altéré)"))
        empreintes[seq] = emp
        seq_attendue, precedente = seq + 1, emp

        # Une entrée par cycle : les numéros de cycle se suivent.
        if k_prec is not None and k != k_prec + 1:
            if k == k_prec + 2:
                r.manques.append((seq, f"cycle {k_prec + 1} absent du journal (EX-Q-02)"))
            elif k > k_prec + 2:
                r.manques.append((seq, f"cycles {k_prec + 1} à {k - 1} absents du journal (EX-Q-02)"))
            else:
                r.manques.append((seq, f"cycle {k} : en double ou en recul (EX-Q-02)"))
        k_prec = k

        try:
            donnees = json.loads(contenu)
        except ValueError:
            r.anomalies.append((seq, f"seq {seq} : contenu illisible"))
            continue
        if not isinstance(donnees, dict):
            continue
        evenements = [e for e in donnees.get("evenements") or [] if isinstance(e, dict)]
        types = [e.get("type") for e in evenements]

        # Chaque changement d'état doit avoir son événement (EX-F-10).
        changement = next((e for e in evenements if e.get("type") == "changement_etat"), None)
        if changement is not None and changement.get("de") is not None:
            r.changements += 1
        etat = donnees.get("etat")
        if etat is not None:
            if etat_prec is not None and etat != etat_prec:
                r.transitions += 1
                if changement is None or changement.get("vers") != etat or changement.get("de") != etat_prec:
                    r.manques.append((seq, f"cycle {k} : changement d'état {etat_prec} → {etat} "
                                           f"sans événement changement_etat (EX-F-10)"))
            elif changement is not None and etat_prec is not None:
                r.manques.append((seq, f"cycle {k} : événement changement_etat sans changement d'état"))
            etat_prec = etat

        # Chaque confirmation reçue a une suite dans la même entrée (EX-F-09).
        r.reponses += types.count("reponse_operateur")
        for _ in range(types.count("confirmation_operateur")):
            r.confirmations += 1
            if not SUITES_CONFIRMATION & set(types):
                r.manques.append((seq, f"cycle {k} : confirmation de l'opérateur reçue sans suite (EX-F-09)"))

    if cycles_attendus is not None and r.entrees != cycles_attendus:
        r.manques.append((None, f"{r.entrees} entrées au journal au lieu de {cycles_attendus} (EX-Q-02)"))

    # ---- Contrôles (3) et (4) : les sceaux.
    derniere_seq = lignes[-1][0] if lignes else -1
    fichier_sceaux = journal.parent / NOM_SCEAUX
    if not fichier_sceaux.exists():
        r.anomalies.append((0 if lignes else None, "aucun sceau (sceaux.sqlite absent)"))
        return r
    cx = sqlite3.connect(f"file:{fichier_sceaux.as_posix()}?mode=ro", uri=True)
    try:
        sceaux = cx.execute("SELECT numero, seq_debut, seq_fin, empreinte, final, horodatage, signature "
                            "FROM sceaux ORDER BY numero").fetchall()
    finally:
        cx.close()
    r.sceaux = len(sceaux)

    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        cle = load_pem_public_key(Path(cle_publique).read_bytes())
    except (ImportError, OSError, ValueError) as erreur:
        r.anomalies.append((None, f"clé publique ou bibliothèque cryptography indisponible : {erreur}"))
        return r

    fin_couverte = -1   # dernière entrée couverte par un sceau
    for numero, debut, fin, emp, final, horodatage, signature in sceaux:
        # La signature doit venir de notre clé privée.
        try:
            cle.verify(bytes.fromhex(signature), message_sceau(numero, debut, fin, emp, final, horodatage))
        except (InvalidSignature, ValueError):
            r.sceaux_rejetes += 1
            r.anomalies.append((debut, f"sceau {numero} : signature invalide"))
            continue

        # L'empreinte signée doit être celle du journal.
        attendue = EMPREINTE_INITIALE if fin < 0 else empreintes.get(fin)
        if attendue is None:
            r.anomalies.append((debut, f"sceau {numero} : l'entrée seq {fin} n'est plus au journal"))
        elif attendue != emp:
            r.anomalies.append((debut, f"sceau {numero} : empreinte du bloc seq {debut}-{fin} "
                                       f"ne correspond pas au journal"))

        # Pas de trou entre les sceaux, et rien après le sceau final.
        if r.sceau_final:
            r.anomalies.append((debut, f"sceau {numero} : posé après le sceau final"))
        if debut > fin_couverte + 1:
            r.anomalies.append((fin_couverte + 1, f"entrées seq {fin_couverte + 1} à {debut - 1} sans sceau"))
        fin_couverte = max(fin_couverte, fin)
        if final:
            r.sceau_final = True

    if fin_couverte < derniere_seq:
        r.anomalies.append((fin_couverte + 1, f"entrées seq {fin_couverte + 1} à {derniere_seq} non scellées"))
    if not r.sceau_final:
        r.anomalies.append((None, "sceau final absent (arrêt non contrôlé)"))
    return r


def verifier_journal(chemin, cle_publique=None) -> tuple[bool, int | None, int]:
    """Intégrité du journal : chaîne SHA-256 et sceaux.

    Renvoie (intègre, première séquence fautive ou None, nombre d'entrées).
    """
    r = verifier(chemin, cle_publique)
    return r.integre, r.premiere_fautive, r.entrees


def main(arguments=None) -> int:
    parser = argparse.ArgumentParser(description="Vérifie un journal SS-6 (chaîne SHA-256 et sceaux Ed25519).")
    parser.add_argument("journal", help="journal.sqlite, ou le dossier de l'essai")
    parser.add_argument("--cle-publique", help="clé publique de confiance (par défaut : cles_ss6/ à côté)")
    parser.add_argument("--cycles-attendus", type=int, help="nombre d'entrées attendu (EX-Q-02)")
    args = parser.parse_args(arguments)

    r = verifier(args.journal, args.cle_publique, args.cycles_attendus)
    print(r.texte())
    return 0 if r.valide else 1


if __name__ == "__main__":
    sys.exit(main())
