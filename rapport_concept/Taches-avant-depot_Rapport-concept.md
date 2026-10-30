# Tâches avant le dépôt du rapport d'ingénierie de concept

**Document visé.** `Rapport-ingenierie-de-concept_v0.2.docx`
**Responsable.** Christian Kévin Sawadogo, chargé de projet
**Version.** 28 octobre 2026

Les tâches sont classées dans l'ordre où elles doivent être faites. Une tâche cochée n'est terminée que si la section du rapport concernée a été mise à jour.

---

## 1. Avant tout

- [ ] **Confirmer la date de dépôt avec le professeur.** Le rapport propose le 6 novembre. Il faut ensuite remplir « [ DATE DE DÉPÔT ] » sur la page titre et mettre à jour le tableau 10-3.
- [ ] **Faire compiler les feuilles de temps d'octobre.** La dernière compilation date du 1er octobre. Il faut les heures de chaque membre jusqu'au 28 octobre.
- [ ] **Faire corriger la feuille d'Aboubacar.** Sa feuille détaillée totalise 27,4 h alors que le bilan indique 33,65 h (section 10.1).

## 2. Décisions à faire ratifier par l'équipe (atelier)

Tant qu'elles ne sont pas ratifiées, le rapport doit continuer de les présenter comme des propositions.

- [ ] **EX-F-02.** Les trois scénarios défaillants sont attribués à SS-2 (tableau 4-1).
- [ ] **Paramètres des exigences.** N = 3 cycles, T = 1 s, D = 120 min (tableaux 4-2 à 4-4).
- [ ] **EX-Q-03.** Quatre états affichés, S = 10 s, 18 réussites sur 20, aucune confusion critique (tableau 4-3).
- [ ] **Condition C1 durcie.** Résidu centré, biais résiduel d'au plus 0,1σ (section 5).
- [ ] **Réglage de SS-4.** Somme cumulée avec δ = 1σ, h = 9 et un seuil instantané à 5σ (section 8.2). La décision revient au lot L7.
- [ ] **Tolérances de fidélité.** Valeurs absolues : 2 à 3 °C, 0,1 à 0,2 MPa, 2 à 3 % du débit (section 8.2). La décision revient au lot L4.
- [ ] **Phase P3.** Passer à deux itérations au lieu de trois (section 10.2).
- [ ] **Conseiller comme relecteur externe** aux revues de jalon (section 9).

Après la ratification, il faut remplacer « Proposé, à ratifier » par « Ratifié le … » dans le tableau 10-4 et retirer le paragraphe d'avertissement de la section 4.

## 3. Informations à obtenir des lots

| Lot | Information à demander | Section du rapport |
|---|---|---|
| L4 | Plus petite constante de temps attendue pour SS-1, pour confirmer T = 1 s | 4.3 |
| L4, L6 | Unités du contrat de données (°C, MPa, kg/s) | 7.1, tableau 7-2 |
| L5 | Intervalle de scellement du journal | 7.4 |
| L5 | Bibliothèque de signature retenue | 6, tableau 6-1 |
| L4, L6, L7, L8 | Estimation de l'effort en heures pour SS-1, SS-3, SS-4 et SS-5 | 10.1 et tableau 5-1 |
| L7 | Alignement des lettres des concepts de SS-4 | 8.1 et tableau 10-5 |

## 4. Données de gestion à compléter (section 10)

- [ ] **Tableau 10-1.** Le remplacer par les heures compilées au 28 octobre.
- [ ] **Coût réel au jalon J2.** Le calculer (heures × 50 $) et le comparer aux 23 000 $ prévus. Si l'écart dépasse 10 %, il faut l'écrire et appliquer l'arbitrage prévu pour le risque RP2.
- [ ] **Indice d'avancement.** Revoir le 0,50 si le professeur accepte de compter une partie du jalon J2.
- [ ] **Classe d'estimation.** Si les estimations en heures arrivent à temps, faire le reclassement en classe 4 ; sinon laisser la phrase actuelle.

## 5. Vérifications de contenu

- [ ] **Relecture croisée.** Chaque lot relit la section qui le concerne, sans jamais relire son propre travail, avec la liste de vérification en 6 points.
- [ ] **Citations de la NRC.** Ouvrir les PDF des références [4], [5], [11], [12], [13] et [15] et vérifier que chaque phrase qui les cite dit bien ce que dit le rapport source.
- [ ] **Notes de l'étape 5.** Les recontrôler dans les matrices de l'équipe (tableau 8-1), en particulier les notes de SS-5, que j'ai recalculées.
- [ ] **Annexes.** Vérifier que chaque fichier du tableau 12-1 existe sous ce nom dans le dépôt, puis le joindre au dépôt du rapport.
- [ ] **Référence [1].** Indiquer la version exacte du plan de projet déposé.

## 6. Mise en forme et dépôt

- [ ] **Page titre.** Remplir le nom du représentant du client, ou écrire « sans objet, client fictif ».
- [ ] **Figure 8-1.** Vérifier qu'elle est lisible une fois imprimée ; sinon, l'agrandir ou la mettre en annexe en pleine page.
- [ ] **Historique des révisions.** Ajouter une ligne pour la version déposée.
- [ ] **Table des matières.** La mettre à jour dans Word : tout sélectionner, puis F9.
- [ ] **PDF.** Exporter le PDF final et vérifier la pagination.
- [ ] **Dépôt GitHub.** Faire le commit et le push sur la branche `analyse-concepts-christian`, puis ouvrir la demande de fusion.
- [ ] **Remise.** Déposer le rapport selon les consignes du cours.

---

## Hors rapport, à ne pas oublier

- [ ] Plan de projet : ajouter Abdramane Drame sur la page titre et corriger « Ibrahim » en « Ibrahima ». Cette correction est consignée au tableau 10-4 ; le plan déjà évalué n'est pas modifié avant l'accord du professeur.
- [ ] Faire appliquer les corrections du tableau 10-5 aux livrables des lots, en commençant par les deux corrections bloquantes (SS-2 et SS-4).
