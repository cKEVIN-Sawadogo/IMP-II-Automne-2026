# Titre
SS-6 : intégration du journal signé et du vérificateur

# Description à compléter après les essais
Intégration du prototype de Wilson au contrat du squelette collectif :
- journal SQLite compatible avec le cache et l'orchestrateur ;
- scelleur séparé et sceaux Ed25519 ;
- rapport de vérification dans lancer.py ;
- tests d'altération, suppression, arrêt brutal, cache et commande de vérification ;
- dépendance cryptography fixée à 50.0.2.

Validation sur ma branche : [commande, nombre de tests, durée, environnement].
Essai intégré : [scénario, cycles, nombre de sceaux, verdict].
Limites : permissions de la clé privée à préciser ; endurance réelle à confirmer.
L'alerte nominale à 5362 s est un point SS-3/SS-4 distinct.

Ferme #NUMERO_DE_L_ISSUE_SS6

Remplacer le numéro avant publication. Faire cocher la liste de revue en six points
de l'équipe, puis laisser Christian fusionner.
