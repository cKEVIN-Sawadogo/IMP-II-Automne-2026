# Plan de travail : rapport d'ingénierie de concept

**Projet.** Jumeau numérique de surveillance d'une boucle thermohydraulique (6GEN135 IMP2, UQAC)
**Gabarit.** `11-Spécifications-des-exigences.docx`, adapté pour l'étape de concept
**Auteur.** Christian Kévin Sawadogo, chargé de projet · **Version.** v0.1, 28 octobre 2026

Le rapport est découpé en huit lots, un par membre, et chaque lot est révisé par un autre membre. Les brouillons sont attendus le 1er novembre et le dépôt est visé le 6 novembre. Cette date reste à confirmer avec le professeur.

La répartition ci-dessous est une proposition. Elle se valide à l'atelier de ce soir.

---

## 1. Répartition des sections

| Lot | Sections du gabarit 11 | Source à utiliser | Auteur | Réviseur |
|:-:|---|---|---|---|
| A | 8.1 Présentation des solutions potentielles et justification du choix | `concept_analyse/Choix-final_Analyse-des-concepts.md`, matrices de l'étape 5, schéma du choix final | Christian | Raouf |
| B | 1 Introduction (objectif, portée, hypothèses) et 4 Exigences (4.1 à 4.5) | Plan de projet (sections 1 et 3), registre des exigences, corrections du choix final | Ibrahima | Abdramane |
| C | 2 Cas d'utilisation (diagramme et fiches) et 3 Acteurs | Plan de projet, GEMMA, parties prenantes | Sidiki | Ibrahima |
| D | 5 Contraintes de conception et 6 Composants externes | Section 5 Normes (v0.3), contraintes du cours, rapport NRC | Abdramane | Rayane |
| E | 8.2 Calculs et tests préliminaires | Choix final (C1, CUSUM), rapport « Paramètres manquants selon la NRC », grilles SS-3 | Raouf | Christian |
| F | 8.3 Plans, programmes, simulations ou prototypages à réaliser et 10.2 Mise à jour de l'échéancier | Échéancier préliminaire, plan de mise en œuvre, lots L4 à L9 | Jérémie | Wilson |
| G | 9 Revue de conception prévue, 10.1 Mise à jour des coûts et des bénéfices, 10.3 Commentaires sur l'avancement | Estimation des coûts du plan, feuilles de temps compilées, comptes rendus de rencontre | Wilson | Jérémie |
| H | 7 Interfaces (7.1 entre sous-systèmes, GUI, matérielles, communication) et 11 Références | Spécifications techniques de l'étape 3 (SS-1 à SS-6), concepts SS-5 B et SS-6 B | Rayane | Sidiki |

Christian assemble aussi la section 12 (Annexes) et intègre les huit lots dans le gabarit. Chaque membre révise un seul lot, et personne ne révise le sien.

### Suivi

| Lot | Auteur | Statut | Lien de la demande de fusion |
|:-:|---|---|---|
| A | Christian | À faire | |
| B | Ibrahima | À faire | |
| C | Sidiki | À faire | |
| D | Abdramane | À faire | |
| E | Raouf | À faire | |
| F | Jérémie | À faire | |
| G | Wilson | À faire | |
| H | Rayane | À faire | |

Statuts possibles : À faire, Brouillon déposé, En révision, Approuvé.

---

## 2. Calendrier

1. **Mercredi 28 octobre, atelier.** Valider la répartition et trancher les points de la section 4.
2. **Dimanche 1er novembre.** Chaque auteur dépose son brouillon par une demande de fusion.
3. **Mardi 3 novembre.** Révisions terminées : le réviseur coche la liste de vérification en 6 points dans la demande de fusion, et l'auteur corrige.
4. **Mercredi 4 novembre, atelier.** Christian intègre les lots dans le gabarit 11. L'équipe fait une relecture d'ensemble et l'essai de cohérence entre les sections 4, 7 et 8.
5. **Vendredi 6 novembre.** Version finale, export PDF et dépôt.

Le développement (phase P3) a commencé le 26 octobre et le gel des fonctionnalités tombe le 20 novembre (J3). Le rapport ne doit donc pas déborder sur la semaine du 9 novembre.

---

## 3. Règles de rédaction

- **Un fichier par lot.** Chaque auteur rédige en Markdown dans `rapport_concept/`, nommé d'après son lot (exemple : `rapport_concept/Lot-E_8-2_Calculs-et-tests.md`). Christian fait la conversion vers le gabarit Word à l'intégration.
- **Une branche par auteur.** La demande de fusion n'est fusionnée qu'après l'approbation du réviseur.
- **Les chiffres viennent des documents de référence.** Toute valeur provient du choix final ou du rapport NRC. Une valeur que l'équipe a choisie est présentée comme un choix de l'équipe, jamais comme une valeur de la NRC.
- **Citations NRC.** Les numéros de page sont vérifiés dans le PDF avant d'être cités.
- **Références.** Elles sont numérotées [n] et envoyées à Rayane, qui tient la section 11. Aucune référence ne va directement dans le gabarit.
- **Schémas.** Ils sont écrits en PlantUML, avec le SVG rendu à côté du `.puml`.
- **Texte du gabarit.** Les consignes en gris italique sont supprimées au fur et à mesure qu'une section est remplie.
- **Style.** On écrit en français normal, sans tirets longs employés comme parenthèses ou entre deux phrases.
- **Fichiers du professeur.** On ne les renomme pas.

---

## 4. Points à trancher avant d'écrire

- [ ] **Date de remise.** Confirmer le 6 novembre avec le professeur.
- [ ] **Période T.** Désigner le lot qui en est responsable et fixer la valeur (1 s proposée, compatible avec la NRC). Aujourd'hui, SS-5 suppose 1 s et SS-6 suppose 100 ms.
- [ ] **Nom du concept retenu pour SS-4.** Choisir une seule lettre pour la décision séquentielle : B dans la grille de l'équipe, C dans le document du lot L7.
- [ ] **EX-Q-03.** L'exigence nomme 3 états alors que SS-5 en affiche 4. Il faut corriger l'exigence ou l'affichage.
- [ ] **Scénarios EX-F-02.** Attribuer la dérive lente, la perte de communication et la valeur hors plage à SS-2. Aucune fonction ne les porte aujourd'hui.
- [ ] **Valeurs révisées.** Ratifier les quatre changements tirés du rapport NRC :
    - X/Y passe à 18 sur 20, sans aucune confusion critique ;
    - h vaut 9 ;
    - la condition C1 est durcie, avec un biais résiduel d'au plus 0,1σ ;
    - les tolérances de fidélité deviennent absolues : 2 à 3 °C, 0,1 à 0,2 MPa et 2 à 3 % pour le débit.
- [ ] **Grilles SS-5 et SS-6 de Christian.** Confirmer leur retrait, puisque l'étape 5 a utilisé la grille de l'équipe.
- [ ] **Page titre.** Ajouter Abdramane Drame et corriger l'orthographe d'Ibrahima Diallo.
