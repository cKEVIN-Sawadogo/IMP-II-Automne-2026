# Gel des fonctionnalités au jalon J3

**Date.** Vendredi 20 novembre 2026, après la démonstration du J3 (issue #72).
**Version gelée.** Étiquette `gel-j3`, commit `f17f6e2` de `main` (fusion de la demande #124).
**Décidé par.** Christian, chargé de projet. **Sert à.** Sections 4.8 et 5 du rapport 13, campagne du sprint 2, livrable L06.

À partir de maintenant, on ne développe plus de fonction nouvelle : on corrige, on vérifie et on rédige. Toute la campagne du sprint 2 se fait sur cette version, pour que les résultats du rapport 13 soient reproductibles.

---

## 1. Ce que contient la version gelée

| Sous-système | Contenu | Responsable |
|---|---|---|
| SS-1 | Modèle 0D à cinq volumes, tests de contrat et d'indépendance vis-à-vis de SS-2 (#122) | Ibrahima |
| SS-2 | Bruit, biais et défauts d'EX-F-02, qualification des mesures | Sidiki |
| SS-3 | Référence 0D réduite en boucle ouverte, calée sur 600 cycles ; C1 préliminaire réussie sur 20 graines (#78) | Raouf |
| SS-4 | Sommes cumulées bilatérales, seuil h = 10 retenu sur 20 graines (#121), état incertain après N = 3 cycles | Rayane |
| SS-5 | Version texte et interface Plotly Dash : conduite, analyse, journal, demande de confirmation en D2 (#46, #124) | Jérémie |
| SS-6 | Écrivain (SQLite en mode WAL, chaînage SHA-256), scelleur Ed25519 dans un processus séparé, vérificateur (#123) | Wilson, Ibrahima |
| Orchestrateur | T = 1 s, journal d'abord puis cache, file des confirmations, en-tête d'essai (#119, #120) | Christian |

**Environnement.** Python 3.13 et les versions exactes de `logiciel/requirements.txt` : numpy 2.5.4, pytest 9.2.0, cryptography 50.0.2, dash 3.2.0, plotly 7.1.0, tzdata 2025.2.

**Tests.** 118 tests réussis (`python -m pytest` dans `logiciel`), vérification GitHub « tests » au vert.

## 2. Résultats de référence de la version gelée

Chaque scénario lancé une fois, en entier, avec sa graine. Ils servent de point de comparaison : un correctif qui change une de ces lignes doit l'expliquer.

| Scénario | Graine | Cycles | Changements d'état (cycle, état) | Vérification du journal |
|---|:-:|:-:|---|---|
| `nominal` | 2026 | 7 200 | 0 incertain ; 599 normal ; 5 363 dérive (T) | INTÈGRE, 7 200 entrées, 121 sceaux |
| `derive_lente` | 2026 | 2 400 | 0 incertain ; 599 normal ; 1 270 dérive (T) | INTÈGRE, 2 400 entrées, 41 sceaux |
| `perte_communication` | 2026 | 1 500 | 0 incertain ; 599 normal ; 1 202 incertain (P) ; 1 260 normal | INTÈGRE, 1 500 entrées, 26 sceaux |
| `saut_franc` | 2026 | 1 500 | 0 incertain ; 599 normal ; 1 200 anomalie (Q) | INTÈGRE, 1 500 entrées, 26 sceaux |
| `hors_plage` | 2026 | 1 500 | 0 incertain ; 599 normal ; 1 202 incertain (Q) ; 1 210 normal | INTÈGRE, 1 500 entrées, 26 sceaux |

La dérive sur T au cycle 5 363 du scénario nominal est une fausse alarme. Elle reste dans le critère de C1 (au plus une par essai de 120 minutes) : c'est un résultat que la campagne mesure, pas un défaut à corriger.

## 3. Paramètres gelés

Ces valeurs ne changent plus. Les modifier invaliderait la campagne statistique et le bilan exigence par exigence.

1. Pas de temps T = 1 s.
2. Calage de la référence de SS-3 sur 600 cycles.
3. Seuil des sommes cumulées h = 10, avec la convention S ≥ h.
4. État incertain après N = 3 cycles sans donnée valide.
5. Seuil de criticité de 2,5 % de l'étendue pour la demande de confirmation.
6. Un sceau tous les 60 cycles, plus le sceau final.
7. Les scénarios de `logiciel/scenarios/` et leurs graines.

## 4. Règles après le gel

1. **Seules les corrections sont acceptées.** Un correctif répare un comportement contraire à une exigence, au contrat de données ou aux décisions du 19 novembre. Les tests, la documentation et les rapports restent ouverts.
2. **Chaque demande de fusion après le gel** porte un titre qui commence par « Correctif : », décrit le défaut, ajoute un test qui le reproduit, et s'inscrit au registre de la section 5. Christian fusionne seulement après la revue.
3. **Les essais de la campagne se font sur l'étiquette.** `git checkout gel-j3` (ou la dernière étiquette `gel-j3.n`), puis on contrôle que le commit écrit dans l'en-tête du journal est bien celui de l'étiquette.
4. **Un correctif qui touche SS-1 à SS-4, SS-6 ou l'orchestrateur** crée une nouvelle étiquette (`gel-j3.1`, `gel-j3.2`…), et les essais de la campagne déjà faits et concernés sont refaits. Un correctif limité à l'affichage de SS-5 ne change pas la campagne statistique, mais il doit être fait avant l'essai d'utilisabilité.
5. **Une idée de fonction nouvelle** va dans la recommandation d'ingénierie de la section 10 du rapport 13 (L08), pas dans le code.

## 5. Registre des correctifs

Écarts connus au moment du gel. Ce ne sont pas des fonctions nouvelles : ils remettent le prototype en conformité avec ce qui était décidé.

| N° | Écart | Ce qui est attendu | Touche la campagne ? | Responsable | Demande | Étiquette |
|:-:|---|---|:-:|---|---|---|
| G1 | L'interface Dash appelle SS-5 directement au lieu de déposer la réponse dans la file des confirmations ; la réception (`confirmation_operateur`) n'est pas journalisée | La réponse passe par `orchestrateur.confirmations` (décision 1, point 4) ; le vérificateur compte les confirmations reçues | Non (SS-5) | Jérémie | | |
| G2 | L'interface affiche les grandeurs vraies de SS-1 (page Analyse, résumé de la chaîne) | Un mode opérateur sans grandeurs vraies, utilisé pour l'essai d'utilisabilité EX-Q-03 | Non (SS-5) | Jérémie | | |
| G3 | L'essai d'arrêt brutal du scelleur est sauté sous Windows | Arrêt brutal vérifié à la main sous Windows (Ctrl+C, puis `--verifier` : seul le sceau final manque), résultat noté ici | À vérifier | Ibrahima | | |
| G4 | `Decisions-architecture.md` dit que `lancer.py` lance le scelleur | « Lancé par SS-6 au démarrage de l'essai » | Non (document) | Christian | Corrigé avec ce document | sans objet |

## 6. Ce qui reste à faire sur la version gelée (sprint 2)

1. Campagne statistique : 20 à 30 essais sains et dérive lente (Rayane, Raouf, #84).
2. Confirmation de C1 sur la version gelée (Raouf, #79).
3. Essais E1 à E9 de SS-6 dans la chaîne complète, dont la rapidité (Ibrahima, section 4.7).
4. Essai d'endurance de 120 minutes en temps réel (Wilson, #114), analyse (Sidiki, #98).
5. Essais fonctionnels d'EX-F-02, EX-F-05, EX-F-06, EX-F-09, EX-F-10 et EX-Q-04 (Sidiki, #97).
6. Essai d'utilisabilité EX-Q-03 après les correctifs G1 et G2 (Jérémie, Ibrahima, Abdramane, #106).
