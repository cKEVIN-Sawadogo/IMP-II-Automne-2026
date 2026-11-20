# Figures du rapport 13 en PlantUML

Les sources `.puml` font foi. Les fichiers `.png` (pour Word) et `.svg` en sont tirés ; on ne les retouche jamais à la main.

| Source | Figure | Section du rapport 13 |
|---|---|---|
| `figure-2-1_composants.puml` | Composants du prototype et flux F1 à F9 et E (F7 à F9 en orange) | 3.4, vue logique (reprend la figure 2-1 du rapport 12) |
| `contrat-de-donnees.puml` | Contrat de données : types communs et contenu de chaque flux | 3.4 et 3.6 (traduit `logiciel/jumeau/contrat.py`) |
| `vue-execution.puml` | Processus, cache, file des confirmations, scelleur et journal | 3.5, vue d'exécution et de déploiement |

## Régénérer les images

Java suffit. Télécharger `plantuml.jar` sur plantuml.com, puis, depuis ce dossier :

```
java -jar plantuml.jar -charset UTF-8 -tsvg *.puml
java -jar plantuml.jar -charset UTF-8 -tpng -Sdpi=180 *.puml
```

L'extension PlantUML de VS Code affiche aussi l'aperçu en direct (Alt+D).

## Règle

Tout changement d'un flux ou d'un champ du contrat se fait d'abord dans `contrat.py` ou l'orchestrateur, avec ses tests, puis ici, dans la même demande de fusion. Le nom d'un flux ne change pas une fois diffusé : F7 reste F7.
