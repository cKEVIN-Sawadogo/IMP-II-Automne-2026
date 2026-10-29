# SS-5, concept C : spécifications techniques

**Fonction (tableau 1-4 du plan de projet).** Présenter l'état, la confiance et les contributions à l'opérateur, sans commander l'installation.
**Concept.** C, présentation par hypothèse de défaillance · **Lot.** L8
**Auteur.** Christian Kévin Sawadogo · **Réviseur.** à désigner · **Version.** v0.1, 21 octobre 2026

Ce document est l'étape 3 de l'analyse des concepts pour le seul concept C de SS-5. Il prolonge `SS5-ConceptC_Presentation-par-hypothese-de-defaillance.md`. Les colonnes des concepts A et B sont conservées vides pour que la grille se fusionne telle quelle dans la grille d'équipe, leurs responsables restant à les remplir.

---

## 1. Grille des spécifications techniques

| Fonction | Fonctionnalité | Concept A | Concept B | Concept C |
|---|---|---|---|---|
| **Présenter l'état, la confiance et les contributions à l'opérateur, sans commander l'installation** | Nombre d'hypothèses présentées simultanément | à compléter | à compléter | Au moins 2, au plus 5. Jamais une seule, même si une seule atteint le degré de correspondance. |
| | Seuil d'affichage d'une hypothèse | à compléter | à compléter | Degré de correspondance ≥ 0,50, soit la moitié des symptômes attendus par la signature. |
| | Rang de l'hypothèse « indéterminé » | à compléter | à compléter | Rang libre, rang 1 inclus. Aucune règle ne la relègue en fin de liste. |
| | Ordre de présentation | à compléter | à compléter | Décroissant par degré de correspondance. L'ordre par gravité est interdit. Les ex aequo partagent un rang. |
| | Hypothèses écartées affichées | à compléter | à compléter | 100 %, chacune avec le motif de son rejet. |
| | Gestes pour atteindre le détail d'une hypothèse | à compléter | à compléter | 1 geste, depuis la zone 1 vers les zones 2 et 3. |
| | Contenu permanent à l'écran (EX-F-04) | à compléter | à compléter | 3 variables, leur écart au modèle, l'horodatage de la dernière acquisition valide. Visible sans aucun geste. |
| | Bascule en état « incertain » (EX-F-06) | à compléter | à compléter | Après N = 3 cycles consécutifs avec au moins une variable indisponible ou hors plage. |
| | Comportement en état « incertain » | à compléter | à compléter | « Indéterminé » passe au rang 1 et aucune cause n'est présentée comme probable. Aucun état normal n'est affiché. |
| | Format du niveau de confiance (EX-F-07) | à compléter | à compléter | Fréquentiel à dénominateur constant, « x sur 10 ». Barre d'erreur, pourcentage seul et animation sont interdits. |
| | Verbes d'action dans les libellés d'hypothèse | à compléter | à compléter | 0. Énoncés de constat seulement, par exemple « écart compatible avec une dérive du capteur de débit ». |
| | Dépendances capables d'écrire vers un équipement (EX-F-08) | à compléter | à compléter | 0, vérifié par inventaire automatique du graphe d'importation à chaque intégration. |
| | Confirmation du mode dégradé (EX-F-09) | à compléter | à compléter | Dialogue modale non préconfirmée, action positive distincte d'une fermeture, restituant état, confiance et hypothèses présentées. |
| | Latence d'affichage (EX-Q-01) | à compléter | à compléter | ≤ T secondes après réception de la sortie de SS-4, rafraîchissement à chaque cycle. |
| | Identification de l'état par un opérateur non impliqué (EX-Q-03) | à compléter | à compléter | ≤ S secondes, dans au moins X essais sur Y. |
| | Taille de la base de connaissance | à compléter | à compléter | 8 causes candidates, 7 symptômes observables, dont l'entrée « indéterminé ». |

---

## 2. Valeurs proposées pour les paramètres encore ouverts

Le registre des exigences laisse N, T, S, X et Y ouverts et impose qu'aucun seuil numérique ne soit posé arbitrairement. Les valeurs ci-dessous sont des **propositions à ratifier au jalon J2**, chacune avec sa justification. Elles ne sont pas des faits mesurés.

| Paramètre | Exigence | Valeur proposée | Justification |
|---|---|---|---|
| N | EX-F-06 | 3 cycles consécutifs | Un seul cycle ferait basculer l'affichage sur une perte isolée, ce qui rendrait l'état « incertain » trop fréquent pour être pris au sérieux. Trois cycles confirment la perte tout en restant sous quelques secondes à la cadence retenue. |
| T | EX-Q-01 | 1 seconde | Les grandeurs d'une boucle thermohydraulique évoluent sur des constantes de temps de l'ordre de la dizaine de secondes, donc une seconde laisse dix points par constante de temps, ce qui suffit à voir une dérive sans surcharger l'affichage. |
| S | EX-Q-03 | 10 secondes | Durée au-delà de laquelle la lecture cesse d'être un coup d'œil et devient une analyse, ce qui est contraire à l'objet d'une vue de synthèse. |
| X sur Y | EX-Q-03 | 8 essais sur 10 | Deux échecs tolérés sur dix laissent la place à une erreur de manipulation sans masquer un défaut de conception de l'affichage. |
| Degré minimal | propre au concept | 0,50 | En deçà de la moitié des symptômes attendus, la correspondance n'est plus discriminante et la liste se remplirait de causes faiblement soutenues. |

Chacune de ces valeurs doit être confrontée aux essais avant d'être figée. La valeur de T en particulier est commune à plusieurs sous-systèmes et ne peut pas être décidée par le seul lot L8.

---

## 3. Restrictions à respecter

Les points suivants ne sont pas des cibles mais des interdits, et chacun est vérifiable par un essai qui réussit ou qui échoue.

- Aucune commande n'est émise vers un équipement, et aucune bibliothèque capable d'en émettre n'est liée au module.
- Aucun libellé d'hypothèse ne contient de verbe d'action.
- Aucune hypothèse n'est affichée seule.
- Les hypothèses de même degré de correspondance ne sont jamais départagées.
- L'état « incertain » n'est jamais présenté comme une absence d'anomalie.
- Le niveau de confiance n'est jamais rendu par une barre d'erreur ni par un pourcentage isolé.

---

## 4. Moyens de vérification

| Spécification | Essai |
|---|---|
| Nombre d'hypothèses, ordre, ex aequo | Jeux de symptômes construits pour produire 1, 2, 5 et 6 correspondances, puis inspection de la liste obtenue. |
| Bascule après N cycles | Essai de perte de capteur sur N moins 1 puis N cycles, vérification du basculement au bon cycle. |
| Absence de commande | Inventaire du graphe d'importation en intégration continue, échec du test si une dépendance d'écriture apparaît. |
| Hypothèses écartées et motifs | Liste de contrôle d'affichage, une ligne par hypothèse de la table. |
| Latence | Mesure sur 100 cycles consécutifs, valeur maximale relevée et non la moyenne. |
| EX-Q-03 | Essai d'utilisabilité avec un membre de l'équipe n'ayant pas développé l'interface, chronométrage externe. |

---

## 5. Point à trancher avant de figer ces valeurs

La dépendance signalée dans la définition du concept vaut aussi pour ses spécifications. Les symptômes S4 et S5, soit le bilan d'énergie et la loi de perte de charge, n'existent que si le concept B de SS-2 ou le concept C de SS-3 est retenu. Sans eux, la table passe de 7 à 5 symptômes et le degré de correspondance de 0,50 n'a plus le même sens, puisqu'il se calcule sur moins de symptômes. **Les valeurs de cette grille supposent donc qu'au moins une relation physique invariante soit disponible en amont.** Si l'équipe retient un autre couple de concepts, la ligne du seuil d'affichage et la taille de la base de connaissance sont à recalculer.
