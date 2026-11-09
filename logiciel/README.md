# Prototype : jumeau numérique de surveillance

Ce dossier contient le logiciel du projet IMP2 (6GEN135). C'est un squelette qui tourne de bout en bout : les six sous-systèmes existent, se parlent selon le contrat de données et écrivent un journal intègre. Plusieurs modules sont encore des versions provisoires, que leurs responsables remplacent un à un sans toucher au reste.

## Lancer le prototype (Windows, PowerShell)

Depuis le dossier `logiciel` :

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Un scénario, avec l'affichage de l'opérateur dans la console
.\.venv\Scripts\python.exe lancer.py scenarios\derive_lente.json

# Le même, au rythme réel d'un cycle par seconde (Ctrl+C pour arrêter)
.\.venv\Scripts\python.exe lancer.py scenarios\derive_lente.json --temps-reel

# Vérifier l'intégrité d'un journal produit
.\.venv\Scripts\python.exe lancer.py --verifier sorties\<dossier>\journal.sqlite

# Tous les tests
.\.venv\Scripts\python.exe -m pytest
```

Chaque essai écrit dans `sorties\<scénario>_<date>\` :

- `journal.sqlite` : le journal de SS-6, une entrée par cycle, chaînée par SHA-256.
- `verite.csv` : les grandeurs vraies de SS-1, réservées au banc d'essai pour la validation.
- `resume.json` : les changements d'état et l'état final.

## Scénarios disponibles

| Fichier | Ce qui est injecté | Ce qui est attendu |
|---|---|---|
| `nominal.json` | Rien, pendant 7 200 cycles (durée D) | État normal après le calage ; fausses alarmes comptées |
| `derive_lente.json` | Dérive de 0,01 σ par cycle sur T à partir de 1 200 s | État « dérive » sur la température |
| `perte_communication.json` | Coupure de P pendant 60 s à partir de 1 200 s | État « incertain » au troisième cycle, puis retour à la normale |
| `hors_plage.json` | Valeur de Q hors étendue pendant 10 s | Valeur rejetée, journalisée, non propagée (EX-Q-04) |
| `saut_franc.json` | Saut de 6 σ sur Q à partir de 1 200 s | État « anomalie » |

Pendant les 600 premiers cycles, l'état est « incertain » : SS-3 se cale sur les mesures et ne peut pas encore conclure.

## Structure

```
logiciel/
  jumeau/
    contrat.py          Contrat de données (tableau 7-2) : Mesure, Statut, Etat, T_CYCLE
    interface.py        Classe SousSysteme : demarrer, etape, arreter
    orchestrateur.py    Boucle à pas fixe et acheminement des données
    scenario.py         Lecture et contrôle d'un scénario
    ss1_boucle/         Ibrahima    modèle 0D à cinq volumes (repris de son dossier de validation)
    ss2_mesures/        Sidiki      bruit, biais et défauts d'EX-F-02
    ss3_reference/      Raouf       PROVISOIRE : moyenne de calage au lieu du modèle 0D réduit
    ss4_decision/       Rayane      somme cumulée, seuil instantané, état incertain
    ss5_interface/      Jérémie     PROVISOIRE : affichage texte au lieu de Plotly Dash
    ss6_journal/        Wilson      SQLite, chaînage SHA-256 ; scellement signé à faire
  scenarios/            Un fichier JSON par scénario
  tests/                Test de bout en bout et règles d'architecture
  lancer.py             Point d'entrée
```

## Qui reçoit quoi

L'orchestrateur appelle chaque module une fois par cycle avec `etape(k, entrees)` et lui transmet seulement les clés ci-dessous. La docstring en tête de chaque module détaille ses clés d'entrée et de sortie.

| Module | Reçoit | Renvoie |
|---|---|---|
| SS-1 | `consignes` | `grandeurs_vraies` |
| SS-2 | `grandeurs_vraies`, `horodatage_utc` | `mesures` |
| SS-3 | `mesures`, `consignes` | `residus`, `pret`, `attendus` |
| SS-4 | `residus`, `pret` | `etat`, `confiance`, `contributrices`, `sommes` |
| SS-5 | `etat`, `confiance`, `contributrices`, `mesures`, `attendus` | `affichage` |
| SS-6 | `contenu` du cycle, préparé par l'orchestrateur | `sequence`, `empreinte` |

Tout module peut ajouter une clé `evenements` (liste de dict) : l'orchestrateur la verse au journal. Les grandeurs vraies ne vont jamais à SS-3 ni à SS-4 ; un test le vérifie.

## Règles d'intégration

1. **On ne modifie que son dossier.** `contrat.py`, `interface.py` et `orchestrateur.py` ne changent qu'avec l'accord du chargé de projet, parce qu'ils touchent tout le monde.
2. **On garde les mêmes clés d'entrée et de sortie.** L'intérieur du module est libre. Si une clé doit changer, on en parle d'abord.
3. **Une branche par personne, une demande de fusion par changement.** GitHub Actions lance les tests à chaque demande ; une demande dont les tests échouent n'est pas fusionnée.
4. **On ajoute ses propres tests** dans `tests/test_<module>.py`. Ils servent aussi de preuves pour la section « Calculs et tests réalisés » du rapport.
5. **Le réviseur coche la liste de vérification en 6 points**, puis le chargé de projet fusionne.

## Choix techniques retenus pour le squelette

Ces choix tranchent les variantes que le rapport de concept laissait ouvertes. Ils sont à faire valider par l'équipe et à consigner comme changements par rapport au plan de projet.

1. **Tout en Python, y compris SS-1 et SS-3.** SS-1 existait déjà en Python, et l'orchestrateur unique est en Python. OpenModelica peut servir à vérifier SS-1 hors ligne, pas à tourner dans la boucle.
2. **SQLite pour le journal.** Un seul fichier, sans serveur.
3. **T = 1 s.**
4. **SS-5 en mode texte pour l'instant.** Plotly Dash viendra ensuite, dans le même processus.

## Premiers constats d'essai

Ces chiffres viennent du squelette, sur 20 graines différentes. Ils sont à reprendre avec les versions finales des modules.

- **Délai de détection de la dérive lente :** environ 75 cycles en médiane, pour 78 prévus par la simulation de la section 8.2 du rapport de concept.
- **Fausses alarmes sur l'essai nominal de 120 minutes :** 13 essais sur 20 en ont produit une. Le rapport prévoyait environ 0,8 fausse alarme par essai avec h = 9. Le repli h = 10 est à examiner (SS-4).
- **Calage de la référence :** avec 120 cycles de calage, le biais résiduel atteignait 0,12 σ, au-dessus de la borne de C1. Le calage est passé à 600 cycles. La démonstration de C1 reste à faire avec le vrai modèle de SS-3.

## Points à confirmer en équipe

- **Flux des consignes vers SS-3.** Une référence en boucle ouverte doit connaître les commandes. Ce flux n'apparaît pas au tableau 7-1 du rapport de concept.
- **Priorité entre une alarme confirmée et l'état incertain** (SS-4).
- **Nombre d'entrées au journal.** Le squelette écrit une entrée par cycle, avec les événements à l'intérieur, pour respecter EX-Q-02. Le tableau 4-5 parlait d'une entrée de plus par événement.
