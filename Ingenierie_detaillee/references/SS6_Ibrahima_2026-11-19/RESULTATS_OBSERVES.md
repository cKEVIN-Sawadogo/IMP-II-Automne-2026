# Résultats observés avant remise

## Sur le PC d'Ibrahima
Windows, Python 3.13.15, pytest 9.2.0.
Suite avec les cinq cas SS-1 copiés depuis la branche dédiée :
103 tests réussis en 86,62 s, aucun ignoré.

Essai E9 isolé : 7 200 cycles ; médiane 2,39 ms ; maximum 23,69 ms ;
aucun cycle à au moins 100 ms.
Un essai précédent avait atteint 123,68 ms : dépassement réel à conserver dans
l'analyse des performances, cause non établie. Le seuil n'a pas été relevé.

Scénario derive_lente, graine 2026 : 2 400 entrées, 41 sceaux, deux transitions,
sceau final oui, verdict INTÈGRE après fermeture et vérification séparée.
Transitions : incertain à 0 s, normal à 599 s, derive sur T à 1 267 s.

Les cinq scénarios nominal, derive_lente, hors_plage, perte_communication et saut_franc
ont produit des journaux intègres, avec sceau final.
Le nominal a signalé derive sur T à 5 362 s : point distinct transmis à Christian.

## Portée
Tests automatisés et scénarios exécutés en temps accéléré.
Aucun résultat d'endurance en temps réel n'est annoncé ici.
Ces observations ne prouvent pas la conformité globale du jumeau ni sa validité physique.
