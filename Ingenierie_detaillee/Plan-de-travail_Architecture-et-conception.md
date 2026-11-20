# Plan de travail : architecture et conception du logiciel (ingénierie détaillée)

**Projet.** Jumeau numérique de surveillance d'une boucle thermohydraulique (6GEN135 IMP2, UQAC)
**Gabarit.** `13-Architecture-et-conception-du-logiciel.doc` du carnet de développement de logiciels. Il remplace le gabarit 09 « Rapport d'ingénierie détaillée » du carnet classique, dont on garde le contenu attendu (calculs et tests, programmes réalisés, revue de conception).
**Remise.** Jeudi 24 décembre 2026, le même jour que le rapport final.
**Gabarit adapté.** `Ingenierie_detaillee/13-Architecture-et-conception-du-logiciel.docx`, avec la consigne de chaque lot en gris italique.
**Auteur.** Christian Kévin Sawadogo, chargé de projet · **Version.** v1.1, 19 novembre 2026 (décisions d'architecture)

Le travail est découpé en trois sprints, calés sur les jalons du plan de projet : J3 le 20 novembre, J4 le 4 décembre et J5 le 18 décembre. Le rapport 13 se rédige à partir du sprint 2, une fois les fonctionnalités gelées, et il est déposé avec le rapport final.

La répartition ci-dessous est une proposition. Elle se valide au laboratoire de la semaine du 16 novembre.

---

## 1. Ce que le rapport doit contenir

Le gabarit 13 demande les parties prenantes de la conception, l'architecture logicielle décrite par vues, puis la conception détaillée de chaque élément (vue structurelle, vue comportementale, autres vues, raisonnement). Il garde les mises à jour de gestion et les références.

Le professeur a précisé que le contenu attendu reste celui du carnet classique. Le gabarit 09 demande en plus :

1. Les calculs et les tests qui finalisent la solution (09, section 1.1).
2. Les plans, programmes, simulations ou prototypages réalisés (09, section 1.2).
3. La revue de conception réalisée avec le client, les intervenants ou des experts (09, section 1.3).

Les deux premiers points vont dans la conception détaillée de chaque élément et dans une section de vérification de la chaîne intégrée. Le troisième devient une section à part.

Le rapport 12 décrivait **ce que fait** chaque composant. Le rapport 13 décrit **comment il est construit** : modules et classes, séquences d'appel, états internes, choix de conception et leurs raisons. On ne recopie pas le rapport 12 : on y renvoie et on donne ce qui est nouveau.

Le professeur corrige seulement le rapport. Aucun renvoi au dépôt GitHub ni à un fichier : chaque diagramme, résultat ou extrait de code utile se trouve dans le rapport ou ses annexes.

---

## 2. Grille d'évaluation et structure retenue

### La grille

La structure suit la grille d'évaluation de l'ingénierie détaillée. Les points montrent où mettre l'effort : l'élaboration de la solution vaut presque la moitié de la note.

| Critère de la grille | Points | Sections du rapport |
|---|:-:|---|
| Résumé exécutif | 1 | Résumé |
| Introduction | 1,5 | 1 |
| Élaboration de la solution | 10 | 3, 4 et 5 |
| Mise à jour des coûts et des bénéfices | 2 | 7 |
| Mise à jour de l'échéancier | 1 | 8 |
| Mise à jour de la performance financière | 1 | 9 |
| Revue de conception et avancement du projet | 4 | 6 |
| Conclusion | 1 | 10 |
| Références | 0,5 | 11 |
| **Total** | **22** | |

La grille répète pour presque chaque critère qu'il faut **un texte argumentatif qui explique le raisonnement et les décisions**. Un tableau de résultats sans explication ne suffit pas.

Ce que la grille demande et que le rapport 12 n'avait pas :

1. **Introduction en cinq parties** : contexte et objectif, portée, méthodologie, importance et impact, structure du rapport.
2. **Validation de la solution préliminaire** : erreurs relevées, correctifs, avis au client.
3. **Spécifications techniques complètes**, éléments mineurs compris.
4. **Calculs organisés par thème**, avec les méthodes statistiques justifiées, les données qui permettent de les refaire, un calcul manuel qui valide chaque outil et une vérification par un autre membre.
5. **Matrices des risques**, obligatoires, et un budget fondé sur les risques.
6. **Revue de conception exhaustive**, avec l'avis de toutes les parties prenantes du RACI (professeur, auxiliaire, technicien).
7. **Retour sur les sprints, le Kanban et un post-mortem.**
8. **Analyse de développement durable** (environnement, économie, société) et du contexte social, politique et socio-économique.
9. **Conclusion** qui traite les contraintes légales, budgétaires, socio-économiques, environnementales et technologiques.

### Structure retenue

0. Résumé exécutif, environ 250 mots, rédigé en dernier.
1. Introduction : 1.1 Contexte et objectif ; 1.2 Portée ; 1.3 Méthodologie ; 1.4 Importance et impact ; 1.5 Structure du rapport.
2. Parties prenantes de la conception et leurs préoccupations.
3. Architecture logicielle : 3.1 Validation de la solution retenue à l'étape préliminaire ; 3.2 Démarche de conception ; 3.3 Vue d'ensemble ; 3.4 Vue logique ; 3.5 Vue d'exécution et de déploiement ; 3.6 Vue des modes de marche.
4. Conception détaillée : 4.1 Vue d'ensemble ; 4.2 à 4.7 SS-1 à SS-6 ; 4.8 Orchestrateur et informations communes ; 4.9 Spécifications techniques.
5. Calculs détaillés, vérification et validation : 5.1 Calculs de dimensionnement ; 5.2 Essai de cohérence et condition C1 ; 5.3 Performances de détection ; 5.4 Utilisabilité ; 5.5 Endurance et temps de cycle ; 5.6 Bilan exigence par exigence.
6. Revue de conception et avancement du projet : 6.1 Revue de conception ; 6.2 Avancement du projet ; 6.3 Développement durable et contexte socio-économique.
7. Mise à jour de l'estimation des coûts et des bénéfices : 7.1 Révision finale des risques ; 7.2 Révision finale du budget.
8. Mise à jour de l'échéancier.
9. Mise à jour de la performance financière.
10. Conclusion.
11. Références.
12. Annexes.

### Rubriques communes

Les vues d'architecture (3.4 à 3.6) suivent les six rubriques du gabarit : vue d'ensemble ; contraintes de conception ; exigences et préoccupations ; description des éléments et de leurs interfaces ; raisonnement ; autres vues pertinentes.

Les composants (4.2 à 4.7) suivent sept rubriques :

1. **Vue structurelle.** Modules, classes et données internes, avec un diagramme.
2. **Vue comportementale.** Ce qui se passe à chaque appel de `etape`, avec un diagramme de séquence ou d'états.
3. **Autres vues pertinentes.** Seulement si elles apportent quelque chose.
4. **Raisonnement.** Pourquoi cette conception, et quelles options ont été écartées.
5. **Calculs et tests réalisés.** Pour chaque test : ce qui est mesuré, le critère, le résultat obtenu et le verdict.
6. **Programme réalisé.** Ce qui fonctionne au gel des fonctionnalités, avec une figure ou une capture.
7. **Limites.** Ce qui n'est pas démontré, et pourquoi.

Une section de composant tient en trois à quatre pages, diagrammes compris.

---

## 3. Les sprints

### Répartition des membres

Abdramane et Wilson gardent de petites tâches, peu complexes. Leurs tâches principales sont redistribuées :

| Tâche | Avant | Après |
|---|---|---|
| Intégration du scelleur et du vérificateur dans le squelette | Wilson | Ibrahima, qui devait déjà relire ce code |
| Section 4.7 SS-6 | Wilson | Ibrahima |
| Vue de déploiement | Wilson | Sidiki, fusionnée avec la vue d'exécution (3.5) |
| Essai d'endurance et temps de cycle (EX-Q-01, EX-Q-02) | Wilson et Abdramane | Wilson lance l'essai et consigne les chiffres ; Sidiki l'analyse et rédige la section 5.5 |
| Section 7.2 Révision finale du budget | Wilson | Christian, avec les heures compilées par Wilson |
| Section 3.4 Vue logique et figure 2-1 | Abdramane | Christian, qui a redessiné la figure 2-1 |
| Section 4.9 Spécifications techniques | Abdramane | Raouf |
| Section 7.1 Révision finale des risques | Abdramane | Raouf |
| Bilan exigence par exigence (livrable L06 et section 5.6) | Abdramane | Rayane |
| Section 3.6 Vue des modes de marche | Ibrahima | Jérémie, qui décrit les mêmes états dans SS-5 |
| Section 6.3 Développement durable | Ibrahima | Abdramane |

Les petites tâches d'Abdramane : section 2 (parties prenantes), section 6.3 (développement durable), aide à l'accueil des participants de l'essai d'utilisabilité, mise en forme du rapport final, révision du lot G.

Les petites tâches de Wilson : remise de son module SS-6 avec les noms de champs du contrat, lancement de l'essai d'endurance et relevé des chiffres, compilation des heures au 4 décembre pour les sections 7.2 et 9, relecture du rapport final, révision du lot A.

### Capacité

Les heures disponibles valent 135 h moins les heures consignées au 8 novembre (section 4.1 du rapport 12). Elles sont à mettre à jour avec la feuille de temps.

| Membre | Disponibles | Sprint 1 | Sprint 2 | Rapport 13 | Rapport final et présentation | Révision | Réunions | Planifiées | Charge |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Christian | 62,65 h | 9 | 4 | 23 | 11 | 2 | 8 | 57 h | 91 % |
| Raouf | 53,75 h | 8 | 6 | 18 | 6 | 2 | 8 | 48 h | 89 % |
| Rayane | 66,25 h | 8 | 16 | 18 | 6 | 2 | 8 | 58 h | 88 % |
| Ibrahima | 62,75 h | 12 | 8 | 15 | 11 | 2 | 8 | 56 h | 89 % |
| Sidiki | 50,50 h | 4 | 10 | 15 | 5 | 2 | 8 | 44 h | 87 % |
| Jérémie | 59,95 h | 18 | 8 | 12 | 7 | 2 | 8 | 55 h | 92 % |
| Abdramane | 55,00 h | 0 | 2 | 5 | 2 | 2 | 8 | 19 h | 35 % |
| Wilson | 54,00 h | 2 | 3 | 2 | 2 | 2 | 8 | 19 h | 35 % |
| **Équipe** | **464,85 h** | **61** | **57** | **108** | **50** | **16** | **64** | **356 h** | **77 %** |

Les six membres actifs sont tous entre 87 % et 92 % de leurs heures disponibles : la marge individuelle est mince. La marge de l'équipe (environ 109 h) se trouve presque entièrement chez Abdramane et Wilson. Si un imprévu survient, on leur confie d'abord une tâche simple de plus, puis on retire du contenu ajustable (lot L8), jamais des essais.

### Sprint 1 : du lundi 16 au vendredi 20 novembre

**Objectif.** Le prototype intégré est démontré au jalon J3, et ses fonctionnalités sont gelées.

**Décisions d'architecture prises le 19 novembre** (détail dans `Decisions-architecture.md`) : cache en mémoire écrit après le journal et lu par l'interface, confirmations par une file d'attente, journal SQLite en mode WAL ; scelleur dans un processus séparé dès le J3 ; versions exactes dans `requirements.txt` et en-tête d'essai dans le journal, Docker optionnel. Le cache, la file et le mode WAL sont déjà dans le squelette.

| Priorité | Élément | Estimation | Responsable | Dépend de |
|:-:|---|:-:|---|---|
| P0 | Essai de cohérence du 18 novembre : verdict sur C1 et jalon J2-b | 8 h | Raouf | Version finale de SS-2 |
| P0 | Interface Plotly Dash : vue permanente, bandeau des variables, vue de détail, historique | 14 h | Jérémie | Aucune |
| P0 | Demande de confirmation en D2, avec événement vers SS-6 (EX-F-09) | 4 h | Jérémie | Interface Dash |
| P0 | Remise du module SS-6 avec les noms de champs du tableau 2-1 | 2 h | Wilson | Aucune |
| P0 | Scelleur et vérificateur dans le squelette : rôles séparés, réception de la confirmation | 8 h | Ibrahima | Module remis par Wilson |
| P0 | SS-4 : convention S ≥ h vérifiée par test, données invalides, choix entre h = 9 et h = 10 sur la chaîne intégrée | 8 h | Rayane | Essai de cohérence |
| P0 | SS-1 : essai d'interface sur 100 cycles, défauts de SS-2 sans effet sur SS-1 | 4 h | Ibrahima | Aucune |
| P0 | Démonstration du J3 : scénario, déroulé et compte rendu | 4 h + 3 h | Sidiki, Christian | Tous les éléments P0 |
| P1 | Figure 2-1 et contrat de données en PlantUML | 1 h | Christian | Aucune |
| P1 | Intégration et revue des demandes de fusion | 5 h | Christian | Aucune |

**Si C1 échoue le 18 novembre.** SS-3 bascule vers la référence recalée (environ 30 h). Raouf la construit avec Christian ; Abdramane et Wilson reprennent alors des tâches simples de Raouf (mise en forme des spécifications techniques, relevés pour la matrice des risques). L'historique des transitions de l'interface est retiré en premier (lot L8), jamais les essais.

### Sprint 2 : du samedi 21 novembre au vendredi 4 décembre

**Objectif.** La campagne d'essais est terminée au jalon J4, et les sections d'architecture du rapport 13 sont rédigées.

| Priorité | Élément | Estimation | Responsable | Dépend de |
|:-:|---|:-:|---|---|
| P0 | Campagne statistique sur la chaîne intégrée : 20 à 30 essais sains (fausses alarmes, confirmation de C1), dérive lente (délai moyen et 95e centile) | 10 h + 6 h | Rayane, Raouf | Gel du J3 |
| P0 | Essai d'endurance de 120 minutes en temps réel (EX-Q-02), avec le temps de cycle (EX-Q-01) : lancement et relevés | 3 h | Wilson | Scellement intégré |
| P0 | Analyse de l'essai d'endurance | 2 h | Sidiki | Relevés de Wilson |
| P0 | Scénarios d'EX-F-02 rejoués ; essais EX-F-05, EX-F-06, EX-F-09, EX-F-10 et EX-Q-04 | 8 h | Sidiki | Gel du J3 |
| P0 | Essai d'utilisabilité (EX-Q-03) : 20 présentations à cinq participants qui n'ont pas développé l'interface | 8 h + 4 h + 2 h | Jérémie, Ibrahima, Abdramane (accueil) | Interface Dash |
| P0 | Bilan exigence par exigence (livrable L06) : exigence, essai, résultat, verdict | 6 h | Rayane | Essais P0 |
| P0 | Brouillons des sections 2 à 4 du rapport 13, déposés le mercredi 2 décembre | voir section 4 | Tous | Gel du J3 |
| P1 | Annexe des comparaisons expérimentales de SS-1, avec leurs sources | 4 h | Ibrahima | Aucune |
| P1 | Coordination, mise à jour du tableau de suivi | 4 h | Christian | Aucune |

### Sprint 3 : du samedi 5 au vendredi 18 décembre

**Objectif.** Les deux rapports sont complets et la présentation orale du J5 est prête.

| Priorité | Élément | Estimation | Responsable | Dépend de |
|:-:|---|:-:|---|---|
| P0 | Section 5 du rapport 13 : calculs et résultats de la campagne, avec verdicts | voir section 4 | Rayane, Raouf, Jérémie, Sidiki | Fin de la campagne |
| P0 | Heures au 4 décembre, compilées pour les sections 7.2 et 9 | 2 h | Wilson | Feuilles de temps à jour |
| P0 | Sections 6 à 10 du rapport 13 : revue de conception, avancement et post-mortem, développement durable, risques et budget, Gantt, performance financière, conclusion | voir section 4 | Sidiki, Christian, Abdramane, Raouf, Jérémie | Heures au 4 décembre |
| P0 | Avis des parties prenantes du RACI sur la conception (professeur, auxiliaire, technicien), consigné par compte rendu | 3 h | Sidiki | Démonstration du J3 |
| P0 | Recommandation d'ingénierie (L08) et rapport final | voir capacité | Tous, coordination Christian | Rapport 13 |
| P0 | Présentation orale : support et répétition le mercredi 16 décembre | 4 h de plus | Ibrahima | Rapport final |
| P1 | Mise en forme du rapport final (Abdramane) et relecture (Wilson) | 2 h + 2 h | Abdramane, Wilson | Rapport final complet |
| P1 | Revue des deux rapports par M. Otis, si possible avant le 18 décembre | 2 h | Christian | Brouillons complets |

### Finalisation : du samedi 19 au jeudi 24 décembre

1. **Lundi 21 décembre.** Versions complètes des deux rapports, intégrées dans les gabarits.
2. **Mardi 22 décembre.** Relecture d'ensemble et contrôle de cohérence entre les deux rapports (mêmes chiffres, mêmes verdicts).
3. **Mercredi 23 décembre.** Mise en forme finale, table des matières, export PDF.
4. **Jeudi 24 décembre.** Dépôt.

Les dates du 22 au 24 décembre servent de réserve : le travail doit être fini le 21.

---

## 4. Répartition du rapport 13

### Principes

1. **Chaque composant revient à son développeur.** SS-6 passe à Ibrahima, qui l'intègre au squelette.
2. **Chaque vue d'architecture revient à celui qui l'a construite** ou qui en dépend le plus.
3. **Celui qui analyse un essai rédige ses résultats.**
4. **Chaque lot a un réviseur différent de son auteur.**

### Tableau des lots

Les heures sont des estimations de rédaction, figures comprises. Elles excluent le développement et les essais, comptés dans les sprints.

| Lot | Sections | Auteur | Heures | Réviseur |
|:-:|---|---|:-:|---|
| A | Résumé ; 3.2 Démarche de conception ; 3.3 Vue d'ensemble ; 3.4 Vue logique ; 4.1 Vue d'ensemble de la conception détaillée ; 4.8 Orchestrateur ; 6.2 Avancement, sprints et post-mortem ; 7.2 Révision finale du budget ; 9 Performance financière ; 10 Conclusion ; intégration et export | Christian | 23 | Wilson |
| B | 2 Parties prenantes ; 6.3 Développement durable et contexte socio-économique | Abdramane | 5 | Ibrahima |
| C | 1 Introduction ; 4.2 SS-1 ; 4.7 SS-6 ; annexe des comparaisons de SS-1 | Ibrahima | 15 | Sidiki |
| D | 3.5 Vue d'exécution et de déploiement ; 4.3 SS-2 ; 5.5 Endurance et temps de cycle ; 6.1 Revue de conception | Sidiki | 15 | Raouf |
| E | 3.1 Validation de la solution préliminaire ; 4.4 SS-3 ; 4.9 Spécifications techniques ; 5.2 Essai de cohérence et condition C1 ; 7.1 Révision finale des risques | Raouf | 18 | Rayane |
| F | 4.5 SS-4 ; 5.1 Calculs de dimensionnement ; 5.3 Performances de détection ; 5.6 Bilan exigence par exigence ; 11 Références | Rayane | 18 | Jérémie |
| G | 3.6 Vue des modes de marche ; 4.6 SS-5 ; 5.4 Utilisabilité ; 8 Gantt révisé | Jérémie | 12 | Abdramane |
| H | Heures au 4 décembre pour les sections 7.2 et 9 | Wilson | 2 | Christian |

Total : 108 heures de rédaction et environ 16 heures de révision.

### Liens entre les lots

1. **Lot A et tous les lots.** La vue logique (3.4) fixe les noms des éléments et des flux. Christian la diffuse le lundi 23 novembre, avant les brouillons.
2. **Lots A et D.** La vue d'exécution et de déploiement (3.5, Sidiki) s'appuie sur l'orchestrateur (4.8, Christian). Les deux auteurs se coordonnent directement.
3. **Lots C et D.** Ibrahima (SS-6) et Sidiki (endurance) utilisent le même vérificateur du journal et les mêmes chiffres.
4. **Lot G.** La vue des modes de marche (3.6) et SS-5 (4.6) décrivent les mêmes états, avec le même diagramme.
5. **Lots E et F.** Les résultats de la section 5.2 (Raouf) alimentent le bilan exigence par exigence (5.6, Rayane), qui est le livrable L06.
6. **Lot F et les auteurs des calculs.** Ibrahima (pas de temps, temps de cycle, fréquence des sceaux) et Raouf (intervalles de confiance) envoient leurs calculs à Rayane, qui les regroupe par thème à la section 5.1.
7. **Lots A, E et H.** Les risques (7.1, Raouf) et le budget (7.2, Christian) se calculent ensemble, avec les heures compilées par Wilson : la contingence est répartie selon les risques.
8. **Lot F et tous les lots.** Les références sont envoyées à Rayane, numérotées [n].

### Suivi

| Lot | Auteur | Statut | Lien de la demande de fusion |
|:-:|---|---|---|
| A | Christian | À faire | |
| B | Abdramane | À faire | |
| C | Ibrahima | À faire | |
| D | Sidiki | À faire | |
| E | Raouf | À faire | |
| F | Rayane | À faire | |
| G | Jérémie | À faire | |
| H | Wilson | À faire | |

Statuts possibles : À faire, Brouillon déposé, En révision, Approuvé.

---

## 5. Risques

| Risque | Effet | Mesure |
|---|---|---|
| C1 échoue à l'essai du 18 novembre | Environ 30 h de plus sur SS-3 ; J3 peut glisser | Raouf et Christian construisent la référence recalée ; Abdramane et Wilson reprennent des tâches simples de Raouf ; on retire d'abord l'historique de l'interface (lot L8) |
| L'interface Dash n'est pas prête au J3 | Démonstration incomplète ; essai d'utilisabilité retardé | La version texte de SS-5 sert à la démonstration ; l'essai d'utilisabilité reste au sprint 2 |
| Examens de fin de session en décembre | Moins de disponibilité pendant le sprint 3 | Les brouillons du rapport 13 sont faits au sprint 2 ; chacun signale ses dates d'examen d'ici le 18 novembre |
| Deux rapports à remettre le même jour | Surcharge de la dernière semaine | Rapport 13 rédigé en premier ; le rapport final le reprend au lieu de le réécrire |
| Plafond de 135 h par membre | Un membre ne peut plus contribuer | Suivi hebdomadaire des heures ; réallocation selon la section 3 |
| Recrutement de cinq participants externes pour EX-Q-03 | Essai incomplet | Jérémie, Ibrahima et Abdramane recrutent dès le sprint 1 |
| Six membres actifs chargés à près de 90 % | Peu de marge individuelle | Les imprévus vont d'abord à Abdramane et Wilson sous forme de tâches simples ; suivi des heures chaque semaine |
| Transfert de SS-6 à Ibrahima | Perte de connaissance du prototype | Wilson remet son module documenté au sprint 1 et répond aux questions d'Ibrahima |

---

## 6. Définition de « terminé »

Pour un élément de code ou d'essai :

- [ ] La demande de fusion est approuvée par le réviseur, qui a coché la liste de vérification en 6 points.
- [ ] Les tests automatiques passent, et un test couvre le nouveau comportement.
- [ ] Le résultat d'essai est chiffré, avec son critère et son verdict.

Pour une section du rapport 13 :

- [ ] Elle suit les rubriques communes de la section 2.
- [ ] Ses diagrammes sont écrits en PlantUML, avec le rendu à côté du `.puml`.
- [ ] Elle ne renvoie ni au dépôt ni à un fichier.
- [ ] Le réviseur l'a approuvée.

---

## 7. Dates clés

| Date | Événement |
|---|---|
| Lundi 16 novembre | Début du sprint 1 ; validation de ce plan au laboratoire de la semaine |
| Mardi 17 novembre | Fin de l'itération I2 |
| Mercredi 18 novembre | Essai de cohérence, verdict sur C1 (J2-b) |
| Vendredi 20 novembre | J3 : démonstration et gel des fonctionnalités ; revue et rétrospective du sprint 1 |
| Lundi 23 novembre | Diffusion de la vue logique (lot A) |
| Mercredi 25 novembre | Point de mi-sprint |
| Lundi 30 novembre | Relevés de l'essai d'endurance remis à Sidiki ; valeurs des spécifications techniques remises à Raouf |
| Mercredi 2 décembre | Brouillons des sections 1 à 4 du rapport 13 |
| Jeudi 3 décembre | Résultats de tous les essais remis à Rayane pour le bilan L06 |
| Vendredi 4 décembre | J4 : campagne d'essais terminée ; révision des sections 1 à 4 terminée ; données de calcul remises à Rayane ; revue et rétrospective du sprint 2 |
| Lundi 7 décembre | Heures au 4 décembre remises à Christian ; répartition du rapport final envoyée à l'équipe |
| Mercredi 9 décembre | Brouillons de la section 5 |
| Vendredi 11 décembre | Brouillons des sections 6 à 9 |
| Lundi 14 décembre | Révision des sections 5 à 9 terminée |
| Mercredi 16 décembre | Conclusion, résumé et références ; répétition de la présentation |
| Vendredi 18 décembre | J5 : présentation orale ; rétrospective du sprint 3 |
| Lundi 21 décembre | Versions complètes des deux rapports |
| Jeudi 24 décembre | Dépôt du rapport 13 et du rapport final |

---

## 8. Règles de rédaction

Les règles du rapport 12 s'appliquent sans changement : un fichier par lot, une branche par auteur, « réalisé » seulement pour ce qui a été exécuté, aucun renvoi au dépôt, références envoyées à Rayane, schémas en PlantUML, et français normal sans tirets longs employés comme parenthèses.

Deux règles s'ajoutent :

1. **Une figure ou un tableau a toujours une légende numérotée**, placée sous la figure et au-dessus du tableau. C'est la correction qui a pris le plus de temps à la fin du rapport 12.
2. **Chaque résultat et chaque décision sont expliqués** dans un texte argumentatif, comme la grille le demande pour presque tous les critères.

---

## 9. Points à trancher

- [x] **Rapport 13 et rapport final.** Ce sont deux documents distincts, tous deux à remettre le 24 décembre.
- [ ] **Parties prenantes du RACI.** Identifier l'auxiliaire et le technicien à consulter pour la revue de conception (section 6.1).
- [ ] **Dates d'examen.** Chaque membre signale les siennes d'ici le 18 novembre, pour ajuster le sprint 3.
- [ ] **Feuilles de temps.** Les mettre à jour au 15 novembre, pour recalculer les heures disponibles de la section 3.
- [ ] **Participants de l'essai d'utilisabilité.** Trouver cinq personnes qui n'ont pas développé l'interface.
- [ ] **Revue de conception.** Demander à M. Otis si la démonstration du J3 peut servir de revue de conception, en plus de l'avis des autres parties prenantes.
