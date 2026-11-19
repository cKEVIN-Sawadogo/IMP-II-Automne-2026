# Rappels automatiques sur Discord

Chaque matin vers 7 h 30, GitHub Actions publie dans le salon Discord de l'équipe, pour chaque membre :

- 🔴 les tâches en retard ;
- 🟠 les tâches du jour ;
- 🔵 les tâches des deux prochains jours (le lundi : toute la semaine).

Chaque ligne donne le titre de l'issue, son avancement (cases cochées sur le total) et son lien. Les tâches viennent des issues ouvertes qui portent l'étiquette « ingénierie détaillée » ; l'échéance est lue dans la ligne « **Échéance : ...** » de leur description. Une issue fermée disparaît des rappels.

## Mise en place (une seule fois)

1. **Créer le webhook Discord.** Dans le salon choisi : Modifier le salon, Intégrations, Webhooks, Nouveau webhook, puis Copier l'URL du webhook.
2. **Donner l'adresse à GitHub.** Dans le dépôt : Settings, Secrets and variables, Actions, New repository secret. Nom : `DISCORD_WEBHOOK`. Valeur : l'URL copiée.
3. **Facultatif : mentionner chaque membre.** Dans Discord, activer le mode développeur (Paramètres, Avancés), puis clic droit sur chaque membre, Copier l'identifiant. Créer le secret `DISCORD_IDS` avec, par exemple :

   ```json
   {"cKEVIN-Sawadogo": "111", "RaoufK17": "222", "Ryan540gh": "333", "IbrahimaDiallo19": "444",
    "boubayans77-rgb": "555", "Mrpropre12": "666", "abdouldrame09": "777", "thoroumwilson-op": "888"}
   ```

   Sans ce secret, les rappels affichent les prénoms sans notifier personne.
4. **Tester.** Onglet Actions, Rappels Discord, Run workflow. Cocher « Afficher le message sans l'envoyer » pour un premier essai ; le message apparaît dans le journal de l'exécution.

## Prérequis

Les issues doivent exister : lancer d'abord `Ingenierie_detaillee/creer_issues.py`.

## Arrêter les rappels

Onglet Actions, Rappels Discord, bouton « ... », Disable workflow. Ou les arrêter après le dépôt du 24 décembre en supprimant `.github/workflows/rappels.yml`.
