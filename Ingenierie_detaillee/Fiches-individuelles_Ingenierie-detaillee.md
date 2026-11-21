# Fiches individuelles : ingénierie détaillée

Une fiche par membre, à publier telle quelle sur Discord (chaque fiche tient dans un message de moins de 2 000 caractères). Le détail complet est dans `Plan-de-travail_Architecture-et-conception.md`.

---

## Message commun (à épingler)

**Ingénierie détaillée : règles communes**
**Un seul rapport : le rapport 13, qui tient lieu de rapport final, remis le jeudi 24 décembre.**
Dates clés : J3 démonstration et gel du code **ven 20 nov** ; J4 essais terminés **ven 4 déc** ; J5 présentation orale **jeu 10 déc**.

**Code**
• Une branche par personne, une demande de fusion par changement, tests au vert.
• Le réviseur coche la liste en 6 points, puis Christian fusionne.
• Après le 20 nov, on corrige et on vérifie seulement : aucune fonction nouvelle.

**Rédaction du rapport 13**
• Tu écris directement dans tes sections du document partagé (lien épinglé), en suivant la consigne grise, puis tu effaces la consigne.
• Chaque résultat donne : le critère, le résultat chiffré, le verdict, et une explication. La grille note le raisonnement, pas seulement les chiffres.
• Chaque figure et chaque tableau a une légende numérotée.
• Diagrammes en PlantUML, avec l'image rendue.
• Aucun renvoi au dépôt GitHub : le professeur ne le consulte pas.
• Tes références vont à Rayane, numérotées [n].

**Révision** : tu coches la liste, tu laisses tes commentaires dans le document, l'auteur corrige dans les 48 h.
**Feuille de temps** : à jour chaque dimanche soir.
**Bloqué plus de 24 h** : tu écris ici tout de suite.

---

## Raouf : SS-3, condition C1, risques (environ 45 h)

**Semaine du 16 nov (avant le J3)**
• **Lun 16** : SS-3 final fusionné dans main (modèle réduit, calage de 600 cycles), dès que Sidiki a fusionné SS-2.
• **Mer 18** : essai de cohérence. 20 essais sains (graines 2001 à 2020), 600 cycles de calage puis 6 600 d'évaluation. Biais de T, P et Q avec intervalle de confiance à 95 %. Critère : |b| ≤ 0,1σ, intervalle compris. Verdict écrit envoyé à Christian et Rayane **le 18 au soir**.
• Si C1 échoue : on construit la référence recalée avec Christian dès le 19.
• **Ven 20** : 5 minutes à la démonstration du J3 sur SS-3 et le verdict C1.

**Du 21 nov au 4 déc**
• Avec Rayane : confirmer C1 sur la version gelée (20 à 30 essais). Résultats à Rayane **jeu 3 déc**.
• Spécifications techniques : chacun t'envoie ses paramètres **lun 30 nov**.
• À Rayane **ven 4 déc** : ton calcul d'intervalle de confiance (formule et un calcul fait à la main).

**Rapport 13 (lot E)**
• **Mer 2 déc** : 3.1 Validation de la solution préliminaire (erreurs relevées, correctifs, avis au client) ; 4.4 SS-3 (7 rubriques, diagramme de classes, diagramme d'états) ; 4.9 Spécifications techniques (tableau : paramètre, valeur, unité, origine).
• **Ven 11 déc** : 5.2 Essai de cohérence et C1 (protocole, critère, résultat, verdict, méthode statistique expliquée).
• **Lun 14 déc** : 7.1 Révision finale des risques (matrices avant et après mitigation), en lien avec Christian pour le budget.

**Ta révision** : le lot de Sidiki (3.5, 4.3, 5.5, 6.1), terminée le **4 déc** puis le **17 déc**.

---

## Rayane : SS-4, campagne statistique, bilan des exigences (environ 55 h)

**Semaine du 16 nov (avant le J3)**
• **Mar 17** : test de la convention S ≥ h (résidu constant de 1,5σ : déclenchement au cycle 9) et gestion des données invalides (aucune mise à jour sur un résidu absent, état incertain après N = 3 cycles).
• **Jeu 19** : choix entre h = 9 et h = 10 sur la chaîne intégrée, après le verdict C1 de Raouf : 20 essais nominaux de 120 min pour chaque valeur, fausses alarmes et délai de dérive. Décision écrite et code fusionné **le 19 au soir**.

**Du 21 nov au 4 déc**
• Campagne sur la version gelée, avec Raouf : 20 à 30 essais sains (fausses alarmes par essai), dérive lente de 0,01σ par cycle (délai moyen et 95e centile), saut franc.
• Bilan exigence par exigence (livrable L06) : tableau exigence, élément, essai, résultat, verdict. Tu reçois les résultats de Sidiki, Jérémie et Raouf **jeu 3 déc**. Bilan terminé **ven 4 déc** (J4).

**Rapport 13 (lot F)**
• **Mer 2 déc** : 4.5 SS-4 (7 rubriques, diagramme d'états avec la règle de priorité).
• **Ven 11 déc** : 5.1 Calculs de dimensionnement (tu reçois ceux d'Ibrahima et de Raouf le 4 déc ; pour chaque calcul : formule, données, résultat, vérification à la main) ; 5.3 Performances de détection ; 5.6 Bilan exigence par exigence.
• **Ven 18 déc** : 11 Références (liste numérotée [n], numéros du rapport 12 gardés si possible).

**Ta révision** : le lot de Raouf (3.1, 4.4, 4.9, 5.2, 7.1), terminée le **4 déc** puis le **17 déc**.

---

## Ibrahima : SS-1, intégration de SS-6, introduction, présentation (environ 53 h)

**Semaine du 16 nov (avant le J3)**
• **Lun 16** : tu reçois le module SS-6 de Wilson.
• **Mar 17** : format de l'événement de confirmation convenu avec Jérémie.
• **Mer 18** : SS-1, essai d'interface sur 100 cycles (aucune valeur manquante, unités du contrat) et preuve que les défauts de SS-2 ne changent pas SS-1 (mêmes trajectoires avec et sans défaut). Fusionné.
• **Jeu 19** : SS-6 intégré au squelette : écrivain, scelleur et vérificateur, noms de champs du tableau 2-1 (pression en MPa), scelleur seul à lire la clé privée, réception de la confirmation. Tests ajoutés : journal intact, ligne modifiée détectée, arrêt brutal détecté. Fusionné.

**Du 21 nov au 4 déc**
• Aide à l'essai d'utilisabilité de Jérémie (déroulement, chronométrage, notes).
• **Mer 2 déc** : annexe des comparaisons expérimentales de SS-1, avec leurs sources.
• À Rayane **ven 4 déc** : calcul du pas de temps (5 cycles minimum par constante de temps), budget du temps de cycle, fréquence des sceaux (60 cycles, 121 sceaux).

**Rapport 13 (lot C)**
• **Mer 2 déc** : 1 Introduction en cinq parties (contexte et objectif, portée, méthodologie, importance et impact, structure) ; 4.2 SS-1 ; 4.7 SS-6 (à partir de la section de Wilson du rapport 12).

**Présentation orale** : tu prépares le support ; à partir du contenu de Christian, support complet **lun 7 déc**, répétition **mar 8 déc**, présentation **jeu 10 déc**.

**Ta révision** : le lot d'Abdramane (2, 6.3), terminée le **4 déc** puis le **17 déc**.

---

## Sidiki : SS-2, démonstration du J3, essais fonctionnels, revue de conception (environ 42 h)

**Semaine du 16 nov (avant le J3)**
• **Lun 16 au soir** : SS-2 final fusionné. Raouf en dépend pour l'essai de cohérence.
• **Jeu 19** : déroulé de la démonstration du J3 (10 min : nominal, dérive lente, perte de communication, confirmation, vérification du journal) et répétition avec Christian.
• **Ven 20** : démonstration, puis compte rendu (présents, commentaires, décisions). Il sert à la section 6.1.

**Du 21 nov au 4 déc**
• Essais sur la version gelée : EX-F-02 (même graine, même journal), EX-F-05 (variable désignée = variable en défaut), EX-F-06 (incertain en N cycles au plus après une perte ou une valeur hors plage), EX-F-09 (confirmation au journal), EX-F-10 (chaque changement d'état au journal), EX-Q-04 (donnée malformée rejetée et non propagée). Résultats à Rayane **jeu 3 déc**.
• Tu reçois les relevés d'endurance de Wilson **lun 30 nov** : nombre d'entrées, temps de cycle au 99e centile, verdict du vérificateur.
• Revue de conception : recueillir l'avis du professeur, de l'auxiliaire et du technicien du RACI, avec un compte rendu pour chacun.

**Rapport 13 (lot D)**
• **Mer 2 déc** : 3.5 Vue d'exécution et de déploiement (6 rubriques, diagramme de séquence d'un cycle, chemins anormaux, processus et fichiers) ; 4.3 SS-2.
• **Ven 11 déc** : 5.5 Endurance et temps de cycle.
• **Lun 14 déc** : 6.1 Revue de conception (avis de chaque partie prenante, changements apportés).

**Ta révision** : le lot d'Ibrahima (1, 4.2, 4.7), terminée le **4 déc**.

---

## Jérémie : SS-5 et interface Plotly Dash, utilisabilité, Gantt (environ 51 h)

**Semaine du 16 nov (avant le J3)**
• Interface Dash, mise à jour chaque seconde :
  - vue permanente : état (forme, couleur, libellé), confiance, heure d'entrée dans l'état ;
  - bandeau des trois variables : mesure, écart à l'attendu, heure de la dernière acquisition valide ;
  - vue de détail en un geste : une tuile par variable, variables désignées par SS-4 mises en évidence ;
  - historique des transitions (première fonction retirée si le temps manque) ;
  - les quatre états restent distincts en noir et blanc.
• Demande de confirmation en D2 : non préremplie, rappelle l'état, la confiance et les variables ; la réponse part au journal avec un instantané de l'écran. Format convenu avec Ibrahima **mar 17**.
• **Jeu 19 midi** : fusionné. Sinon, la démonstration se fait avec la version texte.
• Recruter cinq participants qui n'ont pas développé l'interface, avec Ibrahima et Abdramane, d'ici le **ven 20**.

**Du 21 nov au 4 déc**
• **Lun 23** : protocole d'utilisabilité écrit (20 présentations, cinq participants).
• Séances avant le **mer 2 déc**. Critère : au moins 18 réussites en moins de 10 s, et aucun état anomalie ou incertain lu comme normal. Résultats à Rayane **jeu 3 déc**.

**Rapport 13 (lot G)**
• **Mer 2 déc** : 3.6 Vue des modes de marche (états du GEMMA reliés aux états du logiciel) ; 4.6 SS-5 (7 rubriques, une capture par vue).
• **Ven 11 déc** : 5.4 Utilisabilité.
• **Lun 14 déc** : 8 Gantt révisé (J3 et J4 atteints ou non, chemin critique).

**Ta révision** : le lot de Rayane (4.5, 5.1, 5.3, 5.6, 11), terminée le **4 déc** puis le **17 déc**.

---

## Abdramane : parties prenantes, développement durable, appui (environ 19 h)

• **D'ici le ven 20 nov** : trouver au moins deux des cinq participants de l'essai d'utilisabilité (personnes qui n'ont pas développé l'interface).
• **Entre le 23 nov et le 2 déc** : accueillir les participants et chronométrer pendant les séances de Jérémie.

**Rapport 13 (lot B)**
• **Mer 2 déc** : section 2, Parties prenantes. Un tableau de trois colonnes : partie prenante (client Hydro-Québec, opérateur, vérificateur, Commission canadienne de sûreté nucléaire, équipe, conseiller), ses préoccupations (sûreté, fiabilité du diagnostic, traçabilité, temps de réponse, entretien), la vue de la section 3 qui y répond.
• **Lun 14 déc** : section 6.3, Développement durable, une page à une page et demie. Trois parties : environnement, économie, société. Puis le contexte social, politique et socio-économique. Puis les solutions de rechange envisagées (par exemple, une boucle physique ou un service infonuagique) et pourquoi on ne les a pas retenues.

**Ta révision** : le lot de Jérémie (3.6, 4.6, 5.4, 8), terminée le **4 déc** puis le **17 déc**.
**Rapport 13** : mise en forme du **21 au 23 déc** (légendes numérotées, table des matières, abréviations).

---

## Wilson : remise de SS-6, essai d'endurance, heures (environ 19 h)

• **Lun 16 nov** : remettre ton module SS-6 à Ibrahima, sur une branche, avec une courte note (comment le lancer, rôle de chaque fichier). Renommer les champs selon le tableau 2-1 (T, P en MPa, Q, état). Répondre à ses questions pendant la semaine.
• **Entre le 23 et le 27 nov** : lancer l'essai d'endurance de 120 minutes en temps réel sur la version gelée, avec la commande que Sidiki te donne. Relever : le nombre d'entrées de cycle, le fichier des temps de cycle, le verdict du vérificateur.
• **Lun 30 nov** : envoyer les fichiers et tes relevés à Sidiki.
• **Lun 7 déc** : compiler les heures de chaque membre au 4 décembre, à partir des feuilles de temps (un tableau : membre, heures cumulées), et l'envoyer à Christian.

**Ta révision** : le lot de Christian (3.2, 3.3, 3.4, 4.1, 4.8, puis 6.2, 7.2 et 9), terminée le **4 déc** puis le **17 déc**.
**Rapport 13** : relecture de la langue **lun 21 et mar 22 déc**.

---

## Christian : intégration, architecture, gestion (environ 52 h)

**Semaine du 16 nov**
• **Lun 16 et mar 17** : trancher avec Sidiki, Jérémie et Ibrahima le partage d'état entre Dash et l'orchestrateur, la séparation du scelleur, Docker ou des versions figées. Partager le document du rapport 13 et épingler le lien.
• Revue et fusion des demandes de fusion ; figure 2-1 en PlantUML.
• **Ven 20** : démonstration du J3 avec Sidiki.

**Du 21 nov au 4 déc**
• **Lun 23** : diffuser la vue logique (3.4), qui fixe les noms.
• Suivi du tableau des lots, point de mi-sprint **mer 25 nov**.

**Rapport 13 (lot A)**
• **Mer 2 déc** : 3.2, 3.3, 3.4, 4.1, 4.8.
• **Ven 4 déc** : contenu de la présentation remis à Ibrahima.
• **Lun 14 déc** : 6.2 Avancement et post-mortem, 7.2 Budget (heures de Wilson), 9 Performance financière.
• **Ven 18 déc** : 10 Conclusion et recommandation d'ingénierie (L08), résumé exécutif.
• **Du 21 au 24 déc** : intégration, cohérence entre les deux rapports, export, dépôt.

**Ta révision** : le petit lot de Wilson (heures au 4 décembre).
