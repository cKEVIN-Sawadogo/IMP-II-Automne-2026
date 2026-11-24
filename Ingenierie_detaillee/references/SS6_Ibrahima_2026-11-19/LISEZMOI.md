# Intégration de SS-6 préparée par Ibrahima (19 novembre 2026)

Ibrahima a préparé, à partir du prototype de Wilson, une intégration complète de SS-6 au squelette collectif : écrivain, scelleur, vérificateur, `lancer.py` et 17 tests. Pendant ce temps, l'intégration de Wilson était fusionnée dans `main` (#123), puis gelée avec l'étiquette `gel-j3`. Les deux versions ont été faites en parallèle.

Ce dossier garde son travail tel qu'il a été remis :

1. `SS6_pour_Wilson.zip` : le paquet complet, code et tests compris.
2. `INTEGRATION.md`, `DEMANDE_DE_FUSION.md`, `RESULTATS_OBSERVES.md` et `EMPREINTES.json` : ses notes, sorties du paquet pour être lisibles sur GitHub.

Le code n'est pas copié dans `logiciel/`. Il remplacerait des fichiers gelés et ne suit pas les mêmes noms que `main` (par exemple `EMPREINTE_DEPART` au lieu de `EMPREINTE_INITIALE`), ce qui casserait l'orchestrateur et la campagne en cours.

## Ce qui a été repris dans `main` (correctifs de `gel-j3.1`)

Ses améliorations ont été reportées une à une sur le code gelé, chacune avec un test (voir `Ingenierie_detaillee/Gel-J3.md`, section 5) :

1. **G3.** L'essai d'arrêt brutal tourne maintenant sous Windows aussi : le processus de l'essai est lancé à part, puis tué, et le vérificateur ne doit trouver que des entrées en attente de sceau.
2. **G5.** La durée de chaque cycle est écrite dans le journal (`duree_cycle_precedent_ms`), ce qui permet de vérifier EX-Q-01 et l'essai E9 à partir du journal.
3. **G6.** Le vérificateur distingue un journal en cours d'écriture, dont les dernières entrées attendent leur sceau, d'un journal altéré. L'interface n'affiche plus « Journal altéré » pendant un essai.
4. **G7.** L'écrivain refuse un numéro de cycle en double ou en recul, et le vérificateur compare la colonne `k` de la base au contenu signé.
5. L'écrivain passe en `PRAGMA synchronous=FULL`.

Les cinq scénarios de référence donnent les mêmes contenus signés, les mêmes états, le même nombre d'entrées et le même nombre de sceaux qu'avec `gel-j3`.

## Ce qui reste ouvert

1. Les permissions du fichier de la clé privée sous Windows, que ses notes signalent comme une limite. À traiter dans les limites du rapport 13 (section 10) si rien n'est fait d'ici là.
2. L'essai d'endurance de 120 minutes en temps réel (#114).
3. Sa fausse alarme à 5 362 s dans le scénario nominal est la même que celle de la section 2 de `Gel-J3.md` (cycle 5 363, à une seconde près selon la façon de compter le temps) : elle relève de la campagne de SS-3 et SS-4, pas de SS-6.
