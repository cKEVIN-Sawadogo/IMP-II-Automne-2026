# SS-6 : définition de l'évaluation des concepts

**Fonction (tableau 1-4 du plan de projet).** Journaliser, horodater et protéger l'intégrité de la chaîne, de l'acquisition à l'affichage.
**Lot.** L5 · **Auteur.** Christian Kévin Sawadogo · **Réviseur.** à désigner · **Version.** v0.1, 21 octobre 2026

Étape 4 de l'analyse des concepts. Les critères et les barèmes s'appliquent aux **trois** concepts de la fonction. La colonne de spécification reprend les cibles fixées à l'étape 3 dans `SS6-ConceptA_Specifications-techniques.md`.

Un barème à **0 %** signifie le plus mauvais niveau acceptable, un barème à **rejet** élimine le concept quel que soit son pointage ailleurs. Les pondérations sont des propositions à ratifier au jalon J2.

---

## Grille d'évaluation

| Critères | Pondération | Barèmes | Spéc. min. | Spéc. max. |
|---|:-:|---|:-:|:-:|
| **Force de la preuve** | **35** | | | |
| Preuve d'intégrité | 15 | chaînage par entrée, toute altération localisée à l'entrée près -> 100 % | SHA-256 | |
| | | scellement par bloc, altération localisée au bloc près -> 75 % | | |
| | | condensé global du fichier, altération détectée sans localisation -> 25 % | | |
| | | aucun mécanisme opposable à un tiers -> rejet | | |
| Preuve qu'aucune entrée ne manque | 12 | continuité de séquence et égalité du compte d'entrées au compte de cycles -> 100 % | D = 60 min | |
| | | continuité de séquence seule -> 75 % | | |
| | | deux comptes à réconcilier en deux temps -> 50 % | | |
| | | absence constatée d'erreur présentée comme preuve -> rejet | | |
| Indépendance du vérificateur | 8 | exécutable sur un poste neutre, sans dépendance hors bibliothèque standard -> 100 % | | 3 entrées |
| | | exécutable sur un poste neutre, avec dépendances à installer -> 75 % | | |
| | | exige le moteur de stockage ou un outil d'analyse -> 25 % | | |
| | | exige l'application complète -> rejet | | |
| **Capacité de reconstitution** | **25** | | | |
| Possibilité de recalculer une décision | 15 | valeurs enregistrées, recalcul direct et inconditionnel -> 100 % | | |
| | | valeurs régénérables par scénario, empreinte vérifiable -> 75 % | | |
| | | recalcul limité à une fenêtre récente -> 50 % | | |
| | | reconstitution de la suite des décisions seulement -> 25 % | | |
| Portée de la rétention | 10 | rétention longue des événements et des données -> 100 % | | |
| | | rétention longue des événements, courte des données -> 75 % | | |
| | | rétention longue des événements seuls -> 50 % | | |
| | | rétention bornée par la seule taille du fichier -> 25 % | | |
| **Coût d'exécution** | **20** | | | |
| Part du temps de cycle consommée | 10 | 2 % de T ou moins -> 100 % | | 5 % de T |
| | | de 2 à 5 % de T -> 75 % | | |
| | | de 5 à 10 % de T -> 25 % | | |
| | | au-delà de 10 % de T -> rejet | | |
| Volume produit | 10 | 1 écriture par cycle au plus -> 100 % | | 512 octets par entrée |
| | | 3 écritures par cycle au plus -> 75 % | | |
| | | 1 écriture par variable et par cycle -> 50 % | | |
| | | au-delà -> 25 % | | |
| **Charge de conception et séparation des rôles** | **20** | | | |
| Effort de réalisation | 10 | 40 h-personnes ou moins -> 100 % | | 140 h-personnes |
| | | de 40 à 70 h-personnes -> 75 % | | |
| | | de 70 à 100 h-personnes -> 50 % | | |
| | | de 100 à 140 h-personnes -> 25 % | | |
| | | au-delà de 140 h-personnes -> rejet | | |
| Séparation des rôles | 10 | clé de scellement détenue par un rôle distinct de celui qui écrit -> 100 % | | |
| | | clé détenue par le producteur, limite documentée au rapport -> 50 % | | |
| | | clé détenue par le producteur, limite passée sous silence -> 0 % | | |
| | | aucune clé ni signature -> rejet | | |

**Total : 100**

---

## Justification des pondérations

| Groupe | Poids | Pourquoi ce poids |
|---|:-:|---|
| Force de la preuve | 35 | Un journal dont l'intégrité n'est pas démontrable ne sert ni à la vérification et validation, ni à un auditeur. C'est la seule chose que cette fonction apporte que personne d'autre n'apporte. |
| Capacité de reconstitution | 25 | C'est l'axe même qui sépare les trois concepts, donc celui qui porte le choix. Aucun niveau de rejet n'y figure, parce qu'aucune exigence du registre n'impose le recalcul : le poids reflète une valeur d'usage, pas une obligation. |
| Coût d'exécution | 20 | Le journal est une fonction de support. Au-delà d'une certaine part du temps de cycle, l'instrumentation modifie ce qu'elle observe, ce qui est un défaut de conception et non un simple inconfort. |
| Charge de conception et séparation des rôles | 20 | Même raison qu'ailleurs pour l'effort. La séparation des rôles y est jointe parce que c'est un des quatre principes de cybersécurité que l'équipe a inscrits comme exigences internes à la section 6 du plan. |

---

## Ce que ce barème dit déjà du concept A

Deux lignes placent le concept A en dessous du maximum, et c'est voulu.

Sur la **possibilité de recalculer une décision**, le concept A plafonne à 75 %, parce que les valeurs sont régénérables mais non enregistrées. Le concept B est le seul à pouvoir atteindre 100 %. Je n'ai pas construit de barème qui récompenserait l'empreinte des valeurs à l'égal d'un enregistrement réel, parce que la régénération reste conditionnelle à la reproductibilité de SS-1 alors que l'enregistrement ne l'est pas.

Sur la **séparation des rôles**, le concept A tel que défini plafonne à 50 %, puisque la clé est détenue par celui qui écrit. Le raffinement proposé dans sa définition, signer les entrées de scellement avec une clé tenue par un rôle distinct, est précisément ce qui ferait passer la ligne à 100 %. Le barème chiffre donc le coût de la limite que j'avais signalée, au lieu de la laisser à l'état de remarque.

En contrepartie, le concept A est le seul à pouvoir atteindre 100 % sur l'indépendance du vérificateur et sur la part du temps de cycle. Le barème ne départage pas les concepts sur une qualité globale, il les départage sur ce que chacun échange contre quoi.

---

## Point à trancher avant de figer la grille

Le critère de recalcul pèse 15 points et le concept A y perd 25 % de ce poids au profit du concept B. Ce verdict bascule si la reproductibilité exacte des scénarios n'est pas tenue par SS-1 : dans ce cas, la régénération ne vaut plus rien et le concept A tombe au niveau « reconstitution seulement », à 25 %. **La note de cette ligne dépend donc d'une décision prise dans un autre lot.** Elle ne doit pas être figée avant que le concept de SS-1 soit arrêté.
