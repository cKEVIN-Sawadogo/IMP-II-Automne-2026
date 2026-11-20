# Décisions d'architecture du 19 novembre

**Projet.** Jumeau numérique de surveillance d'une boucle thermohydraulique (6GEN135 IMP2, UQAC)
**Décidé par.** Christian, Sidiki, Jérémie et Ibrahima, à partir de la proposition de l'équipe · **Issue.** #70
**Sert à.** Section 3.2 (démarche de conception) et section 3.5 (vue d'exécution et de déploiement) du rapport 13.

---

## Exigences visées

1. **Traçabilité complète** : savoir quelles mesures et quels événements ont conduit à un état donné.
2. **Reconstitution** : retrouver l'état du système à un cycle passé, en lisant l'entrée de ce cycle au journal ; refaire tout l'essai avec la même graine (EX-F-02).
3. **Audit** : prouver que le journal n'a pas été modifié, et que ce que l'opérateur a vu était journalisé.
4. **Reprise de l'interface** : redémarrer l'interface sans perdre l'historique.
5. **Validation** : comparer les résultats du jumeau aux grandeurs vraies de SS-1 (`verite.csv`), qui restent hors du chemin de l'opérateur. Le prototype n'a pas de données réelles.

---

## Décision 1 : partage d'état entre l'interface et l'orchestrateur

**Options.**

1. L'interface lit directement le journal à chaque seconde.
2. Un cache en mémoire, alimenté par l'orchestrateur après l'écriture au journal, lu par l'interface.

**Critères.** Traçabilité de ce que voit l'opérateur, réactivité à 1 s, reprise de l'interface après un arrêt, simplicité.

**Décision : option 2, un modèle hybride.**

1. Le journal de SS-6 est la seule source de vérité. Le cache n'en est qu'une copie partielle.
2. Le journal d'abord, le cache ensuite : l'opérateur ne voit jamais rien qui ne soit déjà journalisé.
3. Le cache garde les 600 derniers cycles (10 minutes) et se recharge depuis le journal quand l'interface redémarre.
4. L'interface ne parle jamais aux sous-systèmes. Les réponses de l'opérateur passent par une file d'attente ; l'orchestrateur les journalise au cycle suivant (EX-F-09). Aucune commande ne sort du poste.
5. Les accès au cache passent par un verrou, et l'interface reçoit des copies.

**Raison.** L'option 1 lirait le disque à chaque seconde et lierait l'affichage au format du journal. L'option 2 garde la traçabilité de l'option 1, puisque tout passe d'abord par le journal, tout en découplant le calcul de l'affichage. Elle permet aussi de redémarrer l'interface sans perte.

**Limite déclarée.** Redémarrer l'orchestrateur en cours d'essai commence un nouvel essai. L'historique est conservé et l'arrêt brutal est détecté, mais les sommes cumulées et le calage, gardés en mémoire, repartent de zéro.

**Mise en œuvre.** `logiciel/jumeau/etat_partage.py` (classes `CacheEtat` et `FileConfirmations`), ordre d'écriture dans `orchestrateur.py`, journal en mode WAL validé à chaque cycle. Neuf tests dans `tests/test_etat_partage.py`.

---

## Décision 2 : scelleur de SS-6 dans un processus séparé

**Options.** Scelleur dans le même programme que l'écrivain, ou dans un processus séparé.

**Décision : processus séparé dès le J3.** Lancé par `lancer.py`, il est le seul à connaître la clé privée ; l'orchestrateur ne la charge jamais. Il lit le journal en lecture seule (mode WAL), pose un sceau tous les 60 cycles et un sceau final à l'arrêt.

**Raison.** Si l'écrivain détenait la clé, il pourrait réécrire le journal et le resceller : la signature ne prouverait plus rien. C'est l'argument de sécurité du concept C ajouté à SS-6.

**Repli.** Si ce n'est pas prêt pour la démonstration du 20 novembre, le scellement reste dans le même programme pour le J3, et l'écart est déclaré, avec une séparation au J4.

---

## Décision 3 : reproductibilité

**Options.** Versions exactes dans `requirements.txt`, image Docker, ou les deux.

**Décision.**

1. Versions exactes dans `requirements.txt` (`numpy==2.5.4`, `pytest==9.2.0`). Toute nouvelle bibliothèque, comme Dash, y entre avec sa version exacte.
2. Chaque journal commence par une **entrée d'en-tête** : version de Python et des bibliothèques, commit Git, graine et empreinte du scénario. Le journal prouve lui-même dans quelles conditions il a été produit.
3. Docker reste optionnel (priorité P2).

**Raison.** Les versions figées et l'en-tête couvrent l'essentiel de la reproductibilité, sans ajouter d'installation pour le professeur ni pour les participants de l'essai d'utilisabilité. L'image Docker que le rapport de concept prévoyait de figer à la fin d'I1 ne l'a pas été : l'écart est déclaré à la section 3.2.

---

## Texte pour la section 3.2

> **Partage d'état entre l'interface et l'orchestrateur.** Options : interface qui lit directement le journal, ou cache en mémoire alimenté après l'écriture au journal. Critères : traçabilité de ce que voit l'opérateur, réactivité à 1 s, reprise de l'interface après un arrêt. Décision : cache en mémoire, écrit après le journal et rechargé depuis le journal au démarrage. Raison : l'opérateur ne voit jamais rien qui ne soit déjà journalisé, l'affichage ne lit pas le disque à chaque seconde, et l'interface redémarre sans perte d'historique.
