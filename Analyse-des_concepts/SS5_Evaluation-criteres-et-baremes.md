# SS-5 : définition de l'évaluation des concepts

**Fonction (tableau 1-4 du plan de projet).** Présenter l'état, la confiance et les contributions à l'opérateur, sans commander l'installation.
**Lot.** L8 · **Auteur.** Christian Kévin Sawadogo · **Réviseur.** à désigner · **Version.** v0.1, 21 octobre 2026

Étape 4 de l'analyse des concepts. Les critères et les barèmes ci-dessous s'appliquent aux **trois** concepts de la fonction, pas seulement au concept C : c'est cette identité de barème qui rend la matrice de décision de l'étape 5 recevable. La colonne de spécification reprend les cibles fixées à l'étape 3 dans `SS5-ConceptC_Specifications-techniques.md`.

Deux conventions, reprises du gabarit du cours. Un barème à **0 %** signifie que le concept remplit la fonction au plus mauvais niveau acceptable. Un barème à **rejet** signifie que le concept est éliminé, quel que soit son pointage ailleurs. Les pondérations sont des propositions à ratifier au jalon J2.

---

## Grille d'évaluation

| Critères | Pondération | Barèmes | Spéc. min. | Spéc. max. |
|---|:-:|---|:-:|:-:|
| **Sûreté de l'interprétation** | **35** | | | |
| Traitement de l'état « incertain » | 15 | état « incertain » natif, au même rang que les autres états -> 100 % | N = 3 cycles | |
| | | obtenu par une règle ajoutée et vérifiable par essai -> 75 % | | |
| | | rendu par une simple absence d'alarme -> 0 % | | |
| | | aucun état « incertain » possible -> rejet | | |
| Adéquation entre ce que le concept conclut et ce qu'il justifie | 12 | tout élément affiché que l'opérateur pourrait prendre pour une conclusion est accompagné de son fondement, accessible en 1 geste, y compris les éléments écartés lorsque le concept en écarte -> 100 % | | 1 geste |
| | | toute conclusion affichée est accompagnée de son fondement en 1 geste, mais les éléments écartés ne sont pas montrés -> 75 % | | |
| | | le fondement existe mais demande plus de 1 geste -> 50 % | | |
| | | le fondement n'est consultable que dans le code ou la documentation -> 0 % | | |
| | | une conclusion est affichée sans aucun fondement consultable -> rejet | | |
| Résistance à l'erreur d'interprétation | 8 | jamais une seule conclusion affichée, ex aequo non départagés -> 100 % | 2 hypothèses | 5 hypothèses |
| | | plusieurs conclusions affichées mais ex aequo départagés -> 75 % | | |
| | | une seule conclusion affichée, ordre non fondé sur la gravité -> 50 % | | |
| | | une seule conclusion affichée, ordre fondé sur la gravité -> 0 % | | |
| **Conformité au périmètre** | **25** | | | |
| Nature de la preuve d'absence de commande | 15 | preuve par architecture, vérifiée automatiquement à chaque intégration -> 100 % | | 0 dépendance d'écriture |
| | | preuve par architecture, vérifiée manuellement -> 75 % | | |
| | | preuve par configuration, à redémontrer à chaque mise à jour -> 25 % | | |
| | | aucune preuve opposable -> rejet | | |
| Confirmation du passage en mode dégradé | 10 | dialogue non préconfirmé restituant état, confiance et contributions, journalisé -> 100 % | | |
| | | dialogue non préconfirmé et journalisé, sans restitution du contenu -> 50 % | | |
| | | confirmation par simple clic de fermeture -> 0 % | | |
| | | bascule sans confirmation -> rejet | | |
| **Performance d'usage** | **20** | | | |
| Identification de l'état par un opérateur non impliqué | 12 | moins de 5 s dans 9 essais sur 10 -> 100 % | 8 essais sur 10 | S = 10 s |
| | | moins de 10 s dans 8 essais sur 10 -> 75 % | | |
| | | moins de 20 s dans 8 essais sur 10 -> 25 % | | |
| | | au-delà de 20 s, ou moins de 8 essais sur 10 -> rejet | | |
| Latence d'affichage | 8 | moins de 0,5 T -> 100 % | | T |
| | | moins de T -> 75 % | | |
| | | moins de 2 T -> 25 % | | |
| | | au-delà de 2 T -> rejet | | |
| **Charge de conception et vérifiabilité** | **20** | | | |
| Effort de réalisation | 10 | 60 h-personnes ou moins -> 100 % | | 150 h-personnes |
| | | de 60 à 90 h-personnes -> 75 % | | |
| | | de 90 à 120 h-personnes -> 50 % | | |
| | | de 120 à 150 h-personnes -> 25 % | | |
| | | au-delà de 150 h-personnes -> rejet | | |
| Vérifiabilité des exigences par essai | 10 | les 6 exigences de la fonction vérifiables par un essai automatisable -> 100 % | 6 exigences | |
| | | les 6 vérifiables, dont certaines par inspection seulement -> 75 % | | |
| | | au moins une exigence vérifiable seulement par jugement -> 25 % | | |
| | | au moins une exigence non vérifiable -> rejet | | |

**Total : 100**

---

## Justification des pondérations

| Groupe | Poids | Pourquoi ce poids |
|---|:-:|---|
| Sûreté de l'interprétation | 35 | C'est la raison d'être de la fonction. Un affichage qui laisse croire que tout va bien quand on ne sait pas est le seul défaut que le projet s'est engagé à ne pas commettre, et c'est aussi l'esprit commun des normes retenues à la section 6 du plan. |
| Conformité au périmètre | 25 | L'exclusion de toute commande est une exigence de périmètre, donc une condition d'acceptation du mandat et non une qualité parmi d'autres. Le poids est élevé mais le critère n'est pas éliminatoire en soi, puisque les trois concepts peuvent la respecter par des moyens de preuve de force inégale. |
| Performance d'usage | 20 | La fonction n'a de valeur que si un opérateur lit juste et vite. Le poids reste sous celui de la sûreté parce qu'un affichage lent mais honnête est préférable à un affichage rapide mais trompeur. |
| Charge de conception et vérifiabilité | 20 | Il reste quatre semaines de développement après le jalon J2. Un concept non livrable ou non vérifiable dans ce délai ne rend aucun service, quelles que soient ses qualités. |

---

## Ce que ce barème dit déjà du concept C

Le barème n'a pas été écrit pour favoriser le concept dont j'ai la charge, et deux lignes le montrent.

Sur l'**adéquation entre ce que le concept conclut et ce qu'il justifie**, les trois concepts peuvent atteindre 100 %, mais chacun par un travail différent. Le concept A y parvient en n'affichant aucune conclusion qu'il ne puisse justifier, ses variables et leurs écarts étant déjà à l'écran. Le concept C doit en faire bien davantage, puisqu'il est le seul à produire une conclusion de haut niveau : il lui faut afficher les hypothèses écartées avec leur motif pour atteindre le même niveau. Le critère est donc le plus exigeant pour le concept C, et c'est volontaire.

Une version antérieure de cette ligne donnait 100 % à « hypothèses écartées et motifs affichés », ce que seul le concept C pouvait offrir, et plafonnait le concept A à 75 % pour une raison qui n'est pas un défaut, puisqu'il n'a aucune conclusion à tracer. Le critère a été reformulé pour mesurer l'adéquation plutôt que la quantité de justification.

Sur la **résistance à l'erreur d'interprétation**, le concept C part avec le handicap le plus lourd des trois, l'ancrage sur la première hypothèse, et il ne peut atteindre 100 % qu'au prix des quatre dispositions décrites dans sa définition. Le concept A, qui n'affiche aucune conclusion, y est bon sans effort.

Autrement dit, ce barème n'avantage le concept C sur aucun critère, et il le pénalise sur le risque qu'il est seul à créer. C'est la condition pour que la comparaison tienne devant l'équipe.

---

## Point à trancher avant de figer la grille

La valeur de T apparaît deux fois dans les barèmes de latence et n'appartient à aucun des deux lots concernés. Tant qu'elle n'est pas arrêtée, la ligne « latence d'affichage » est notée en multiples d'une valeur inconnue et ne départage rien. C'est le premier point à régler en réunion.
