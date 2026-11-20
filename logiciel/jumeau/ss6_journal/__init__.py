"""SS-6 : journal de données et scellement signé. Responsable : Djasra Wilson Thoroum
(prototype du rapport 12, section 2.6), intégration au squelette : issue #90.

Trois rôles, un fichier chacun :
  ecrivain.py      JournalDonnees : une entrée par cycle dans journal.sqlite
                   (mode WAL, ajout seul, chaînage SHA-256). Aucune clé.
  scelleur.py      processus séparé, lancé par l'écrivain au démarrage, seul à
                   lire la clé privée. Signe (Ed25519) l'empreinte de la dernière
                   entrée tous les 60 cycles, plus un sceau final à l'arrêt
                   normal, dans sceaux.sqlite.
  verificateur.py  après l'essai, avec la clé publique seulement :
                   « python lancer.py --verifier » ou « python -m jumeau.ss6_journal ».

Les clés sont dans « cles_ss6 », à côté du dossier de l'essai (sorties/cles_ss6
avec lancer.py), ou dans le dossier donné par la variable JUMEAU_CLES_SS6.

Entrées par cycle (préparées par l'orchestrateur) :
  contenu  dict   mesures, résidus, état, événements du cycle (sérialisables)

Sortie par cycle :
  sequence  int   numéro de l'entrée
  empreinte str   empreinte SHA-256 de l'entrée

SS-6 ne fait qu'écrire : il ne renvoie rien qui puisse changer le diagnostic.
Les changements d'état (SS-4) et les confirmations de l'opérateur (file des
confirmations, puis SS-5) arrivent dans les événements du cycle : SS-6 les
garde tels quels, et le vérificateur contrôle qu'il n'en manque aucun.
"""
from jumeau.ss6_journal.ecrivain import EMPREINTE_INITIALE, PERIODE_SCEAU, JournalDonnees
from jumeau.ss6_journal.verificateur import Rapport, verifier, verifier_journal

__all__ = ["EMPREINTE_INITIALE", "PERIODE_SCEAU", "JournalDonnees", "Rapport",
           "verifier", "verifier_journal"]
