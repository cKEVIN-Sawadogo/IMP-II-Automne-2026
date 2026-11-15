# Plan de travail : description des composants (ingénierie préliminaire)

**Projet.** Jumeau numérique de surveillance d'une boucle thermohydraulique (6GEN135 IMP2, UQAC)
**Gabarit.** `12-Description-des-composants.doc` du carnet de développement de logiciels. Il remplace le gabarit 08 « Rapport d'ingénierie préliminaire » du carnet classique.
**Fichier de travail.** `IMP-II-Automne-2026/12-Description-des-composants.docx`, gabarit déjà adapté : page titre, définitions, structure ci-dessous et consigne de chaque lot en gris italique.
**Auteur.** Christian Kévin Sawadogo, chargé de projet · **Version.** v0.2, 4 novembre 2026

Le rapport est découpé en huit lots équilibrés, un par membre, et chaque lot est révisé par un autre membre. Les brouillons sont attendus le mardi 10 novembre et le dépôt est fixé au dimanche 15 novembre.

La répartition ci-dessous est une proposition. Elle se valide au laboratoire du jeudi 5 novembre.

---

## 1. Ce que le rapport doit contenir

Le gabarit 12 demande une introduction, la description des composants logiciels, la revue de conception réalisée et les mises à jour de gestion. Il ne demande pas explicitement de démontrer la validité de la solution. Le gabarit 08 du carnet classique le demande, avec deux sous-sections :

1. Les calculs et les tests (08, section 1.1).
2. Les plans, programmes, simulations ou prototypages **réalisés** (08, section 1.2).

Le professeur a précisé que le contenu attendu reste celui du carnet classique. Ces deux éléments vont donc dans la description de chaque composant (section 2 ci-dessous).

Le rapport 12 reste au niveau des composants : ce que fait chacun et comment ils se relient. Les vues structurelles et comportementales détaillées (classes, séquences, états internes) appartiennent au rapport 13 « Architecture et conception du logiciel ». On ne les écrit pas maintenant.

Le professeur corrige seulement le rapport. Aucun renvoi au dépôt GitHub ni à un fichier : chaque résultat, figure ou extrait de code utile se trouve dans le rapport ou ses annexes.

---

## 2. Structure retenue

0. Résumé exécutif, non numéroté, rédigé en dernier.
1. Introduction : 1.1 Objectif, 1.2 Portée (système adjacent d'aide à la décision, interactions avec le scénario d'essai et l'opérateur, aucune sortie vers l'installation selon EX-F-08, ce qui est hors portée).
2. Description des composants logiciels :
    - 2.0 Structure globale et relations entre les composants (diagramme de composants, contrat de données, orchestrateur à pas fixe).
    - 2.1 SS-1, modèle 0D de la boucle.
    - 2.2 SS-2, acquisition et qualification des mesures (erreur additive, dérive, perte de communication, contrôle de plage).
    - 2.3 SS-3, référence en boucle ouverte (modèle 0D réduit).
    - 2.4 SS-4, décision séquentielle (somme cumulée et seuil instantané).
    - 2.5 SS-5, présentation par état.
    - 2.6 SS-6, journal de données et scellement signé.
3. Revue de conception réalisée avec le client, les intervenants ou des experts.
4. Mise à jour de l'estimation des coûts et des bénéfices (avec l'analyse des feuilles de temps).
5. Mise à jour de l'échéancier : 5.1 Échéancier, 5.2 Courbe en S et indices de performance.
6. Commentaires sur l'avancement du projet.
7. Références.
8. Annexes : résultats d'essai détaillés et extraits de code utiles.

### Gabarit commun des sections 2.1 à 2.6

Les six composants sont décrits avec les mêmes rubriques, dans le même ordre :

1. **Rôle et exigences couvertes.** Ce que fait le composant et la liste des exigences (EX-F, EX-Q) qu'il porte.
2. **Entrées, sorties et interfaces.** Ce qu'il reçoit, ce qu'il produit, à qui, à quelle cadence, selon le contrat de données (tableau 7-2 du rapport de concept).
3. **Modèle, algorithme et paramètres.** Les équations ou la logique retenues et les valeurs de départ du tableau 8-6, avec leur origine.
4. **Écarts par rapport au concept retenu.** Ce qui a changé depuis le rapport de concept, et pourquoi.
5. **Calculs et tests réalisés.** Pour chaque test : ce qui a été mesuré, le critère, le résultat obtenu et le verdict.
6. **Programme ou prototype réalisé.** Ce qui fonctionne aujourd'hui, avec une figure ou une capture.
7. **Limites et travaux restants avant J3.** Ce qui n'est pas encore démontré.

Une section de composant tient en deux à trois pages, figures comprises.

---

## 3. Le cas de SS-3 et de la condition C1

Le dépôt du 15 novembre tombe avant l'essai de cohérence et le jalon J2-b du 18 novembre. Le rapport ne peut donc pas affirmer que la condition C1 est respectée. Position proposée :

1. **SS-1, SS-2 et SS-6.** Ils sont construits pendant l'itération I1, qui se termine le 8 novembre. Leurs tests sont présentés comme réalisés : bilans de masse et d'énergie fermés à 0,1 % près, étude du pas de temps, injection des défauts, intégrité du journal.
2. **SS-4.** La somme cumulée se teste sans SS-3, sur des résidus synthétiques gaussiens dont on connaît le biais. Ce test confirme ou corrige par la mesure les tableaux 8-4 et 8-5 du rapport de concept. Il est présenté comme réalisé.
3. **SS-5.** L'affichage des quatre états se teste avec des états produits à la main. L'essai d'utilisabilité à 20 présentations reste prévu pour J4.
4. **SS-3.** Le composant est décrit en entier, avec son protocole de calage et les critères du tableau 8-7. Si une première mesure du biais résiduel existe le 13 novembre, elle est présentée comme préliminaire, avec sa taille d'échantillon. Le verdict sur C1 et la règle de bascule vers la référence recalée sont annoncés pour le 18 novembre.
5. **Section 6.** Elle déclare clairement que la validité de l'architecture dépend encore de C1 et donne la date où elle sera établie.

Cette position est honnête et défendable. L'autre voie, devancer l'essai de cohérence avant le 13 novembre, demanderait de terminer SS-3 en avance alors que le modèle de référence est le lot en retard sur le chemin critique.

---

## 4. Répartition des tâches

### Principes

1. **Chaque composant revient à celui qui l'a analysé.** L'auteur des sections 2.1 à 2.6 est le membre qui a mené l'analyse de ce sous-système à l'étape des concepts.
2. **Les autres sections suivent le travail déjà fait.** Chaque section générale va au membre qui a écrit la section correspondante du plan de projet ou du rapport de concept.
3. **La charge tient compte du développement.** SS-1, SS-2 et SS-6 sont terminés à la fin d'I1, le 8 novembre : leurs auteurs prennent une section générale en plus. SS-3, SS-4 et SS-5 sont développés en I2, en même temps que le rapport : leurs auteurs ont moins de rédaction. Raouf a la charge la plus légère, parce que SS-3 est sur le chemin critique.
4. **Le réviseur est le voisin dans la chaîne.** Il est le premier concerné par les interfaces du lot qu'il révise. Chaque membre révise un seul lot, et personne ne révise le sien.

### Tableau des lots

Les heures sont des estimations de rédaction. Elles excluent le développement, mais comprennent la mise en forme des résultats d'essai et des figures. Chaque membre ajoute environ 2 heures pour la révision de son lot.

| Lot | Tâches | Travail déjà fait sur lequel le lot s'appuie | Auteur | Heures | Réviseur |
|:-:|---|---|---|:-:|---|
| A | Résumé exécutif ; 5.2 Courbe en S et indices de performance ; 6 Commentaires sur l'avancement ; intégration des lots dans le gabarit 12 et export PDF | Sections 8 et 10 du plan de projet, section 10.3.2 et intégration du rapport de concept | Christian | 11 | Wilson |
| B | 2.0 Structure globale et relations (diagramme de composants, contrat de données, composants externes) ; matrice de traçabilité exigences et composants ; contrôle de cohérence d'ensemble du 14 novembre | Section 5 Normes, lot D du rapport de concept (contraintes de conception, composants externes) | Abdramane | 12 | Christian |
| C | 1 Introduction (objectif, portée, hors portée) ; 2.1 SS-1 | Lot B du rapport de concept (introduction et exigences), analyse des concepts de SS-1 | Ibrahima | 11 | Sidiki |
| D | 2.2 SS-2 ; 3 Revue de conception réalisée (support de présentation, compte rendu, décisions) | Lot C du rapport de concept (cas d'utilisation et acteurs), analyse des concepts de SS-2 (livrables 27 et 36) | Sidiki | 12 | Raouf |
| E | 2.3 SS-3, avec la position de la section 3 sur la condition C1 | Lot E du rapport de concept (calculs et tests préliminaires), analyse des concepts de SS-3 | Raouf | 10 | Rayane |
| F | 2.4 SS-4, avec le test de la somme cumulée sur résidus synthétiques ; 7 Références | Lot H du rapport de concept (interfaces et références), évaluation de l'étape 5 du lot L7 | Rayane | 11 | Jérémie |
| G | 2.5 SS-5 ; 5.1 Échéancier mis à jour (jalons, itérations, chemin critique) | Lot F du rapport de concept (échéancier), diagramme de Gantt du plan, analyse des concepts de SS-5 | Jérémie | 11 | Abdramane |
| H | 2.6 SS-6 ; 4 Mise à jour des coûts et des bénéfices (feuilles de temps au 8 novembre, ressources, budget, bordereau) | Lot G du rapport de concept (coûts et bénéfices), estimation préliminaire des coûts du plan, analyse quantitative de SS-6 | Wilson | 13 | Ibrahima |

Total estimé : 91 heures de rédaction et environ 16 heures de révision. L'écart entre les membres va de 10 à 13 heures.

### Liens entre les lots

Certaines sections se nourrissent l'une de l'autre. Les auteurs concernés se coordonnent directement :

1. **Lots A, G et H.** La courbe en S (A) utilise les coûts engagés (H) et les dates révisées (G). Wilson et Jérémie remettent leurs chiffres à Christian au plus tard le 10 novembre.
2. **Lot B et lots C à H.** Le diagramme de composants et le contrat de données (B) fixent les noms des données, les unités et la cadence T. Abdramane les diffuse le 9 novembre, avant la rédaction des sections de composants.
3. **Lots D et A.** Le compte rendu de la revue du 11 novembre (D) alimente les commentaires sur l'avancement (A).
4. **Lot F et tous les lots.** Les références sont envoyées à Rayane, numérotées [n]. Aucune référence ne va directement dans le gabarit.

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

## 5. Calendrier

1. **Jeudi 5 novembre, laboratoire.** Valider la répartition, la position sur SS-3 (section 3) et trancher les points de la section 7. Christian demande à M. Otis une revue de conception pour l'atelier du 11 novembre.
2. **Vendredi 6 novembre.** Dépôt du rapport de concept. Aucun travail sur le rapport 12 ne doit le retarder.
3. **Dimanche 8 novembre, fin de l'itération I1.** Démonstration interne de SS-1, SS-2 et SS-6, consignée dans un compte rendu. Compilation des feuilles de temps : c'est la date d'état des sections 4 et 5.
4. **Lundi 9 novembre.** Abdramane diffuse le diagramme de composants et le contrat de données (noms, unités, cadence T).
5. **Mardi 10 novembre.** Chaque auteur dépose son brouillon par une demande de fusion.
6. **Mercredi 11 novembre, atelier.** Revue de conception avec M. Otis, qui tient lieu de relecteur externe. Sidiki prépare le support et rédige le compte rendu. On lui présente l'architecture, les interfaces et les résultats d'I1. Ses commentaires et les décisions prises alimentent la section 3.
7. **Jeudi 12 novembre.** Révisions terminées : le réviseur coche la liste de vérification en 6 points dans la demande de fusion, et l'auteur corrige.
8. **Vendredi 13 novembre.** Date limite des résultats d'essai admis dans le rapport, dont une éventuelle première mesure de C1. Christian intègre les lots dans le gabarit.
9. **Samedi 14 novembre.** Relecture d'ensemble par l'équipe. Abdramane mène le contrôle de cohérence entre la section 2.0 et les sections 2.1 à 2.6 (mêmes noms de données, mêmes unités, même cadence T).
10. **Dimanche 15 novembre.** Version finale, export PDF et dépôt.

L'itération I2 (SS-3, SS-4, SS-5) court en même temps, du 9 au 20 novembre. Le rapport ne doit pas retarder le modèle de référence, attendu au plus tard le 18 novembre.

---

## 6. Règles de rédaction

- **Un fichier par lot.** Chaque auteur rédige en Markdown dans `rapport_composants/`, nommé d'après son lot (exemple : `rapport_composants/Lot-E_2-3_SS-3.md`). Christian fait la conversion vers le gabarit Word à l'intégration.
- **Une branche par auteur.** La demande de fusion n'est fusionnée qu'après l'approbation du réviseur.
- **Réalisé ou prévu.** Un test n'est présenté comme réalisé que s'il a été exécuté, avec son résultat chiffré. Tout le reste est présenté comme prévu, avec sa date.
- **Les chiffres viennent des documents de référence ou des essais.** Une valeur que l'équipe a choisie est présentée comme un choix de l'équipe, jamais comme une valeur de la NRC.
- **Citations NRC.** Les numéros de page sont vérifiés dans le PDF avant d'être cités.
- **Références.** Elles sont numérotées [n] et envoyées à Rayane. Aucune référence ne va directement dans le gabarit.
- **Schémas.** Ils sont écrits en PlantUML, avec le SVG rendu à côté du `.puml`.
- **Aucun renvoi au dépôt.** Le professeur ne consulte pas GitHub. Ce qui doit être lu se trouve dans le rapport ou en annexe.
- **Texte du gabarit.** Les consignes en gris italique sont supprimées au fur et à mesure qu'une section est remplie.
- **Style.** On écrit en français normal, sans tirets longs employés comme parenthèses ou entre deux phrases.
- **Fichiers du professeur.** On ne les renomme pas.

---

## 7. Points à trancher avant d'écrire

- [ ] **Répartition.** Confirmer que chaque auteur des sections 2.1 à 2.6 est bien le développeur du sous-système pendant la phase P3. Sinon, l'auteur devient le développeur.
- [ ] **Position sur SS-3.** Adopter la position de la section 3, ou décider de devancer l'essai de cohérence.
- [ ] **Revue avec M. Otis.** Obtenir son accord pour le 11 novembre. À défaut, la section 3 ne peut s'appuyer que sur la démonstration interne du 8 novembre.
- [ ] **Effort restant.** Estimer l'effort de SS-1, SS-3, SS-4 et SS-5 avant la fin d'I1, comme l'annonce le rapport de concept. Ces valeurs vont à la section 4.
- [ ] **Paiement de J2.** Indiquer si le client a accepté de scinder le paiement en J2-a et J2-b, et si J2-a est acquis. La valeur acquise de la courbe en S en dépend.
- [ ] **Réduction de contenu.** Confirmer les éléments retirés des rangs 7 et 8 de la priorisation des besoins (au moins 76 heures), pour que la portée de la section 1.2 en tienne compte.
