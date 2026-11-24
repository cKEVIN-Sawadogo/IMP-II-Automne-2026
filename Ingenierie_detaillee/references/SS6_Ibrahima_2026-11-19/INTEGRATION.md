# Remise de SS-6 à Wilson

## Contenu
- logiciel/jumeau/ss6_journal/ : écrivain, scelleur, vérificateur et points d'entrée.
- logiciel/tests/test_ss6.py : 13 essais, avec arrêt brutal activé sous Windows
  et affichage des mesures du test E9 (seuil inchangé : maximum < 100 ms).
- logiciel/tests/test_ss6_integration.py : 4 tests d'intégration.
- logiciel/lancer.py : affichage du rapport complet et code de sortie non nul si non intègre.

Base de compatibilité : squelette au commit b024fad. Ce paquet contient les fichiers SS-6
et le lanceur, pas tout le logiciel. Le code SS-1 et son test séparé ne sont pas remplacés.
Ne pas écraser un lancer.py qui aurait évolué sans examiner ses différences.

## Corrections par rapport au ZIP de Wilson
Le journal utilise les colonnes sequence, k, contenu, empreinte_precedente, empreinte.
Le module renvoie sequence et empreinte, comme l'attend l'orchestrateur.
Le scelleur conserve son propre processus, les sceaux sont dans sceaux.sqlite.
La journalisation utilise WAL et synchronous=FULL.
L'écrivain refuse les doublons de cycles et les incohérences de k.
Le vérificateur contrôle aussi le k SQL par rapport au contenu.
Les confirmations SS-5 passent par le circuit existant, sans changer le format.
La commande de vérification expose le rapport de chaînage, signatures et sceau final.

## Procédure GitHub
Dans ton dépôt, à la racine (dossier contenant logiciel), commence par :
    git status

Si tu as des modifications non enregistrées, conserve-les avant de changer de branche.
Avec un dossier de travail propre :
    git fetch origin
    git switch -c integration-ss6-wilson origin/main

Décompresse ce paquet ailleurs et ouvre les deux dossiers dans VS Code.
Compare d'abord les fichiers avec ceux de main pour préserver les évolutions récentes.
Reporte les fichiers du paquet vers les mêmes chemins dans le dépôt.
Dans logiciel/requirements.txt, ajoute cryptography==50.0.2 si absente.
Si cryptography y figure déjà avec une autre version, harmonise le choix avec l'équipe
et refais les tests. Ne remplace pas les autres dépendances par celles d'un ancien fichier.

Ensuite, dans logiciel (avec ton environnement Python activé) :
    python -m pip install -r requirements.txt
    python -m pytest tests/test_ss6.py tests/test_ss6_integration.py -v -s
    python -m pytest -rs

Le paquet ajoute 17 cas. Le total dépend des autres tests déjà fusionnés dans main.
L'essai d'arrêt brutal doit être exécuté et non ignoré.

## Essai intégré
Dans logiciel :
    python lancer.py scenarios/derive_lente.json --sortie sorties/validation_wilson_01 --silencieux
    python lancer.py --verifier sorties/validation_wilson_01/journal.sqlite

Utilise un dossier neuf à chaque essai.
Attendu pour ce scénario : 2 400 cycles et entrées, 41 sceaux, deux transitions,
sceau final présent et verdict INTÈGRE.
Les fichiers journal.sqlite et sceaux.sqlite doivent être présents.

## Commit et demande de fusion
Reviens à la racine du dépôt :
    git status
    git diff --check
    git diff -- logiciel/lancer.py logiciel/requirements.txt
    git add logiciel/jumeau/ss6_journal logiciel/tests/test_ss6.py logiciel/tests/test_ss6_integration.py logiciel/lancer.py logiciel/requirements.txt
    git diff --cached --stat
    git commit -m "Integre le scellement signe et la verification de SS-6"
    git push -u origin integration-ss6-wilson

Ouvre une demande de fusion vers main. Décris les corrections et indique les résultats
effectivement obtenus sur ta machine. Ajoute Ferme #n avec le numéro de l'issue couverte.
L'issue #90 concerne le scelleur séparé : ne la ferme que si cette demande la couvre
et si la responsabilité est confirmée dans l'équipe.
Le réviseur complète la liste de revue en six points ; Christian effectue la fusion.

N'ajoute pas les clés privées, .venv, __pycache__ ni sorties/ au commit.
Les fichiers de preuve se conservent localement ; joindre uniquement les résultats utiles
à la demande de fusion, selon les règles du dépôt.

## Limites à signaler
- Un scelleur séparé charge seul la clé dans le code, mais le même compte système
  pourrait accéder au fichier : permissions Windows et gestion de la clé publique à préciser.
- L'endurance de 120 minutes en temps réel reste à exécuter.
- Une alerte de dérive à t=5362 s dans le nominal doit être examinée côté SS-3/SS-4.
  Le verdict INTÈGRE ne valide pas la pertinence de cette alerte.
- Après arrêt brutal, absence de sceau final = journal incomplet ; la cause n'est pas prouvée.
- Les anciens journaux non signés ne deviennent pas intègres avec ce vérificateur.
