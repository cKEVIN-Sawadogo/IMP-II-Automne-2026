# SS-6, concept A : spécifications techniques

**Fonction (tableau 1-4 du plan de projet).** Journaliser, horodater et protéger l'intégrité de la chaîne, de l'acquisition à l'affichage.
**Concept.** A, journal d'événements · **Lot.** L5
**Auteur.** Christian Kévin Sawadogo · **Réviseur.** à désigner · **Version.** v0.1, 21 octobre 2026

Ce document est l'étape 3 de l'analyse des concepts pour le seul concept A de SS-6. Il prolonge `SS6-ConceptA_Journal-d-evenements.md`. Les colonnes des concepts B et C sont conservées vides pour que la grille se fusionne telle quelle dans la grille d'équipe, leurs responsables restant à les remplir.

---

## 1. Grille des spécifications techniques

| Fonction | Fonctionnalité | Concept A | Concept B | Concept C |
|---|---|---|---|---|
| **Journaliser, horodater et protéger l'intégrité de la chaîne, de l'acquisition à l'affichage** | Types d'événements | 9 types, énumération close. Un type absent de la liste ne peut pas être écrit. | à compléter | à compléter |
| | Champs obligatoires par entrée | 7 : numéro de séquence, horodatage daté, horloge monotone, type, sous-système émetteur, charge utile, empreinte chaînée. | à compléter | à compléter |
| | Taille d'une entrée | ≤ 512 octets, charge utile comprise. | à compléter | à compléter |
| | Écritures par cycle en fonctionnement normal | 1, l'événement d'acquisition, plus 1 par événement exceptionnel survenu dans le cycle. | à compléter | à compléter |
| | Part du temps de cycle consommée par l'écriture (EX-Q-01) | ≤ 5 % de T, mesurée au pire cas et non en moyenne. | à compléter | à compléter |
| | Contenu de l'événement d'acquisition (EX-F-10) | Numéro de cycle, code de qualité par variable, empreinte des 3 valeurs. Les valeurs elles-mêmes ne sont pas écrites. | à compléter | à compléter |
| | Fonction d'empreinte | SHA-256 pour l'empreinte des valeurs, HMAC-SHA-256 pour le chaînage des entrées. | à compléter | à compléter |
| | Nombre d'écrivains concurrents | Exactement 1, pour que l'ordre d'écriture soit l'ordre des numéros de séquence sans arbitrage. | à compléter | à compléter |
| | Numéro de séquence | Entier strictement croissant, sans réutilisation ni remise à zéro en cours de session. | à compléter | à compléter |
| | Précision d'horodatage | Déclarée dans l'entrée d'ouverture de session. Aucune décimale au-delà de la précision déclarée. | à compléter | à compléter |
| | Période de scellement | Toutes les 1000 entrées ou toutes les 5 minutes, au premier des deux atteint. | à compléter | à compléter |
| | Conservation du condensé de scellement | Hors du fichier qu'il protège. | à compléter | à compléter |
| | Rotation | Par session, et par fichier au-delà de 10 Mo. | à compléter | à compléter |
| | Preuve d'absence d'entrée manquante (EX-Q-02) | Continuité stricte des numéros de séquence sur toute la campagne. L'absence constatée d'erreur ne vaut pas preuve. | à compléter | à compléter |
| | Durée de l'essai d'endurance (EX-Q-02) | D minutes sans interruption ni perte d'entrée. | à compléter | à compléter |
| | Vérificateur indépendant | Programme distinct de l'application, sans dépendance hors bibliothèque standard, exécutable sur un poste neutre. | à compléter | à compléter |
| | Entrées de la procédure de vérification | 3 : le fichier de journal, l'attestation de scellement, la clé remise séparément. | à compléter | à compléter |
| | Contrôles exécutés par le vérificateur | 4 : recalcul de la chaîne, comparaison au condensé scellé, continuité des numéros de séquence, monotonie de l'horloge. | à compléter | à compléter |
| | Détenteur de la clé de chaînage | Le producteur du journal. L'intégrité est prouvée contre un tiers, pas contre le producteur. | à compléter | à compléter |
| | Journalisation d'une donnée rejetée (EX-Q-04) | Entrée de rejet portant la variable et le motif. La non-propagation est exécutée par le maillon appelant. | à compléter | à compléter |

---

## 2. Valeurs proposées pour les paramètres encore ouverts

Le registre laisse D ouvert, et T est commun à plusieurs sous-systèmes. Les valeurs ci-dessous sont des **propositions à ratifier au jalon J2**, chacune avec sa justification.

| Paramètre | Exigence | Valeur proposée | Justification |
|---|---|---|---|
| D | EX-Q-02 | 60 minutes | À une écriture par seconde, une heure produit de l'ordre de 3600 entrées, assez pour franchir plusieurs rotations et plusieurs scellements, donc pour éprouver les mécanismes qui ne se déclenchent que périodiquement. Un essai plus court ne les atteindrait jamais. |
| Taille d'entrée | propre au concept | 512 octets | Les 7 champs obligatoires tiennent largement dans cette borne, dont une empreinte de 64 caractères hexadécimaux, et la borne garantit un coût d'écriture prévisible par cycle. |
| Période de scellement | propre au concept | 1000 entrées ou 5 minutes | Un scellement trop rare laisse une fenêtre longue sans preuve intermédiaire, un scellement trop fréquent alourdit le journal d'entrées de service. Le double critère couvre la marche normale et les périodes creuses. |
| Part du temps de cycle | EX-Q-01 | 5 % de T | Le journal est une fonction de support qui ne doit pas peser sur la chaîne qu'elle observe. Au-delà de cette part, l'instrumentation changerait ce qu'elle mesure. |
| Rotation | propre au concept | 10 Mo | À 512 octets par entrée, cela représente environ 20 000 entrées par fichier, soit un fichier qu'un vérificateur peut traiter d'un seul tenant. |

La valeur de T n'est pas proposée ici : elle appartient aux sous-systèmes qui portent le cycle d'acquisition et de comparaison, et le lot L5 s'y conforme.

---

## 3. Restrictions à respecter

- Aucune entrée d'un type absent de l'énumération close ne peut être écrite.
- Le condensé de scellement n'est jamais conservé dans le fichier qu'il protège.
- Aucun affichage d'horodatage ne comporte plus de décimales que la précision déclarée à l'ouverture de session.
- Le numéro de séquence n'est jamais réutilisé ni remis à zéro en cours de session.
- Il n'y a jamais plus d'un écrivain.
- L'objet remis à l'audit est le journal lui-même, jamais une version reformatée ou filtrée.

---

## 4. Moyens de vérification

| Spécification | Essai |
|---|---|
| Complétude des entrées (EX-Q-02) | Campagne de D minutes, puis comparaison du nombre de cycles exécutés au nombre d'entrées d'acquisition, et contrôle de la continuité des numéros de séquence. |
| Intégrité | Altération volontaire d'une entrée au milieu du journal, puis exécution du vérificateur, qui doit localiser l'entrée en cause. |
| Résistance à la coupure | Coupure provoquée pendant une écriture, puis vérification que seule la dernière ligne est invalide et que le reste de la chaîne tient. |
| Coût par cycle | Mesure du temps d'écriture sur 100 cycles consécutifs, valeur maximale rapportée à T. |
| Journalisation d'un rejet (EX-Q-04) | Injection d'une donnée malformée, puis présence de l'entrée de rejet et absence de propagation au modèle. |
| Indépendance du vérificateur | Exécution sur un poste où l'application n'est pas installée, à partir des 3 seules entrées prévues. |

---

## 5. Point à trancher avant de figer ces valeurs

La capacité de retrouver les valeurs qui ont produit une décision repose sur la régénération de la trajectoire à partir de l'identifiant de scénario, donc sur la tenue d'EX-F-02 par SS-1. **Tant que la reproductibilité n'est pas démontrée, la ligne de l'empreinte des valeurs ne garantit que la détection d'une altération, pas la capacité de rejeu.** Si l'équipe retient pour SS-1 un concept dont la reproductibilité n'est qu'à tolérance et non exacte, l'empreinte des valeurs devient inutilisable comme preuve de rejeu et il faudra soit enregistrer les valeurs, ce qui revient au concept B, soit accepter de ne pouvoir que reconstituer.
