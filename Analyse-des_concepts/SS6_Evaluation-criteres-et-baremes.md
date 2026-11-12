# SS-6 : définition de l'évaluation des concepts

**Fonction.** Journaliser, horodater et protéger l'intégrité de la chaîne, de l'acquisition à l'affichage.
**Lot.** L5 · **Auteur.** Christian Kévin Sawadogo · **Réviseur.** à désigner · **Version.** v0.3, 21 octobre 2026

Étape 4 de l'analyse des concepts. Les critères et les barèmes s'appliquent aux trois concepts de la fonction, et non au seul concept dont j'ai la charge : un concept noté avec son propre barème obtient toujours une bonne note.

Un barème à rejet élimine le concept quel que soit son pointage ailleurs. Les pondérations sont à ratifier avant que le moindre concept soit noté.

---

## Grille d'évaluation

| Critères | Pondération | Barèmes | Spécification |
|---|:-:|---|:-:|
| Preuve d'intégrité | **30** | toute altération est détectée et localisée à l'entrée près -> 100 % | SHA-256 |
| | | altération détectée sans localisation -> 50 % | |
| | | aucun mécanisme opposable à un tiers -> rejet | |
| Preuve qu'aucune entrée ne manque | **25** | le nombre d'entrées est comparable au nombre de cycles exécutés -> 100 % | essai de 60 min |
| | | continuité des numéros de séquence seulement -> 50 % | |
| | | aucune preuve autre que l'absence d'erreur constatée -> rejet | |
| Possibilité de refaire le diagnostic | **25** | les valeurs sont enregistrées, recalcul direct -> 100 % |  |
| | | les valeurs sont régénérables et vérifiables par empreinte -> 50 % | |
| | | reconstitution de la suite des décisions seulement -> 25 % | |
| Effort de réalisation | **20** | 40 h-personnes ou moins -> 100 % | 80 h-personnes |
| | | de 40 à 80 h-personnes -> 50 % | |
| | | au-delà de 80 h-personnes -> rejet | |
| **Total** | **100** | | |

---

## Critères écartés et raison

Une version antérieure comptait neuf critères. Elle a été réduite à quatre, parce qu'un critère que l'équipe ne peut pas mesurer dans le temps imparti, ou qui donne la même note aux trois concepts, n'aide pas à décider.

| Critère écarté | Pourquoi |
|---|---|
| Indépendance du vérificateur | Fondue dans la preuve d'intégrité : une altération ne peut pas être localisée sans un vérificateur qui rejoue le contrôle, donc le premier critère la contient déjà. |
| Part du temps de cycle et volume produit | À l'échelle du prototype, aucun des trois concepts ne pèse sur le temps de cycle. Un critère qui donne la même note aux trois ne sert à rien. |
| Portée de la rétention | Le prototype ne vit que le temps des essais, donc la durée de conservation ne départage pas les concepts. |
| Séparation des rôles | Devient une obligation documentaire : la limite de la clé détenue par celui qui écrit est à inscrire au rapport, et non à noter. |

---

## Ce que ce barème dit du concept dont j'ai la charge

Le concept A plafonne à 50 % sur le troisième critère, parce que ses valeurs sont régénérables mais non enregistrées. Le concept B est le seul à pouvoir atteindre 100 %. Cette note bascule à 25 % si SS-1 ne tient pas une reproductibilité exacte, donc elle dépend d'une décision prise dans un autre lot.
