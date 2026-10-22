# SS-5 : définition de l'évaluation des concepts

**Fonction.** Présenter l'état, la confiance et les contributions à l'opérateur, sans commander l'installation.
**Lot.** L8 · **Auteur.** Christian Kévin Sawadogo · **Réviseur.** à désigner · **Version.** v0.3, 21 octobre 2026

Étape 4 de l'analyse des concepts. Les critères et les barèmes s'appliquent aux trois concepts de la fonction, et non au seul concept dont j'ai la charge : un concept noté avec son propre barème obtient toujours une bonne note.

Un barème à rejet élimine le concept quel que soit son pointage ailleurs. Les pondérations sont à ratifier avant que le moindre concept soit noté.

---

## Grille d'évaluation

| Critères | Pondération | Barèmes | Spécification |
|---|:-:|---|:-:|
| Traitement de l'état « incertain » | **30** | état « incertain » affiché comme un état à part entière -> 100 % | bascule après 3 cycles |
| | | affiché seulement comme une absence d'alarme -> 50 % | |
| | | aucun état « incertain » possible -> rejet | |
| Justification de ce qui est affiché | **25** | chaque conclusion affichée est accompagnée de son fondement, en un geste -> 100 % | 1 geste |
| | | le fondement existe mais demande plusieurs gestes -> 50 % | |
| | | une conclusion est affichée sans fondement consultable -> rejet | |
| Preuve qu'aucune commande n'est émise | **25** | aucune bibliothèque capable d'écrire vers un équipement n'est liée au module -> 100 % | 0 dépendance d'écriture |
| | | l'écriture existe mais est désactivée par configuration -> 50 % | |
| | | aucune preuve opposable -> rejet | |
| Effort de réalisation | **20** | 60 h-personnes ou moins -> 100 % | 100 h-personnes |
| | | de 60 à 100 h-personnes -> 50 % | |
| | | au-delà de 100 h-personnes -> rejet | |
| **Total** | **100** | | |

---

## Critères écartés et raison

Une version antérieure comptait neuf critères. Elle a été réduite à quatre, parce qu'un critère que l'équipe ne peut pas mesurer dans le temps imparti, ou qui donne la même note aux trois concepts, n'aide pas à décider.

| Critère écarté | Pourquoi |
|---|---|
| Temps d'identification de l'état par un opérateur | L'exigence EX-Q-03 reste à vérifier, mais par un essai qui passe ou qui échoue, pas par un barème à quatre niveaux. Un essai d'utilisabilité chiffré demanderait plus de participants que l'équipe n'en a. |
| Latence d'affichage | Elle se note en multiples du temps de cycle, qui n'est pas encore fixé. Tant qu'il ne l'est pas, le critère ne départage rien. |
| Vérifiabilité des exigences par essai | Recouvre les trois premiers critères, qui portent déjà chacun leur moyen de vérification. |
| Résistance à l'erreur d'interprétation | Fondue dans la justification de ce qui est affiché : un concept qui montre le fondement de sa conclusion réduit déjà le risque d'ancrage. |

---

## Ce que ce barème dit du concept dont j'ai la charge

Le concept C reste le plus exigé par le deuxième critère, puisqu'il est le seul à produire une conclusion de haut niveau, donc le seul à avoir quelque chose de lourd à justifier. Les concepts A et B y parviennent plus facilement. Le barème n'avantage le concept C sur aucune ligne.
