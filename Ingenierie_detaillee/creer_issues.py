"""Crée les tâches de l'ingénierie détaillée dans GitHub : jalons, étiquettes, issues assignées,
et les ajoute au tableau GitHub Projects.

Prérequis (une seule fois, dans PowerShell) :
    winget install GitHub.cli
    gh auth login
    gh auth refresh -s project        # nécessaire pour ajouter les issues au tableau

Utilisation, depuis le dossier Ingenierie_detaillee :
    py creer_issues.py --essai                # affiche ce qui serait créé, sans rien créer
    gh project list --owner cKEVIN-Sawadogo   # pour connaître le numéro du tableau
    py creer_issues.py --projet 1             # crée tout et l'ajoute au tableau numéro 1

Le script peut être relancé sans risque : il ne recrée pas une issue qui existe déjà (même titre).
"""
import argparse, json, subprocess, sys

C, RA, RY, IB, SI, JE, AB, WI = ('cKEVIN-Sawadogo', 'RaoufK17', 'Ryan540gh', 'IbrahimaDiallo19',
                                  'boubayans77-rgb', 'Mrpropre12', 'abdouldrame09', 'thoroumwilson-op')
S1, S2, S3, DEP = 'Sprint 1 : prototype intégré et gel (J3)', 'Sprint 2 : campagne d’essais (J4)', 'Sprint 3 : rapports et présentation (J5)', 'Dépôt du 24 décembre'

PLAN = 'Plan de travail : `Ingenierie_detaillee/Plan-de-travail_Architecture-et-conception.md`. Gabarit : `Ingenierie_detaillee/13-Architecture-et-conception-du-logiciel.docx`.'
CODE = ('**Règles du code** : une branche, une demande de fusion qui ferme cette issue (`Ferme #n` dans la description), '
        'tests au vert (`python -m pytest` dans `logiciel`). Le réviseur coche la liste en 6 points, puis Christian fusionne.')
REDAC = ('**Règles de rédaction** : écrire directement dans tes sections du document partagé du rapport 13, en suivant la consigne grise, puis l’effacer. '
         'Chaque résultat : critère, résultat chiffré, verdict et explication. Chaque figure et tableau : une légende numérotée. '
         'Diagrammes en PlantUML avec l’image rendue. Aucun renvoi au dépôt GitHub. Références envoyées à Rayane, numérotées [n].')

def corps(contexte, taches, fini, liens=None, regles=None, echeance=None):
    s = f'{contexte}\n\n### À faire\n' + '\n'.join(f'- [ ] {t}' for t in taches)
    s += '\n\n### Terminé quand\n' + '\n'.join(f'- {f}' for f in fini)
    if liens: s += '\n\n### Tu reçois et tu remets\n' + '\n'.join(f'- {l}' for l in liens)
    if echeance: s += f'\n\n**Échéance : {echeance}.**'
    if regles: s += '\n\n' + regles
    s += '\n\n' + PLAN
    return s

I = []
def add(titre, assignes, jalon, etiquettes, body): I.append(dict(title=titre, assignees=assignes, milestone=jalon, labels=['ingénierie détaillée'] + etiquettes, body=body))

# ---------------- Christian ----------------
add('[S1] Trancher les décisions d’architecture avant de coder', [C, SI, JE, IB], S1, ['logiciel'], corps(
    'Trois choix conditionnent le code de SS-5 et de SS-6. Ils doivent être pris avant que Jérémie et Ibrahima commencent, et ils seront justifiés à la section 3.2 du rapport 13.',
    ['Partage d’état entre Plotly Dash et l’orchestrateur : deux fils d’exécution avec un état partagé protégé, ou une interface qui relit le journal.',
     'Scelleur de SS-6 dans un programme séparé, seul à lire la clé privée : oui ou non pour le J3.',
     'Reproductibilité : versions exactes dans `requirements.txt` (au minimum), Docker en option.',
     'Consigner chaque décision dans un commentaire de cette issue : options, critère, choix, raison.'],
    ['Les trois décisions sont écrites ici et connues de Jérémie, Ibrahima et Sidiki.'], echeance='mardi 17 novembre'))
add('[S1] Intégration, figure 2-1 et document partagé du rapport 13', [C], S1, ['logiciel'], corps(
    'Coordination technique du sprint 1.',
    ['Mettre le gabarit 13 en ligne et épingler le lien sur Discord.',
     'Figure 2-1 et contrat de données en PlantUML, à jour des flux F7 à F9.',
     'Réviser et fusionner les demandes de fusion du sprint 1 au fil de l’eau.',
     'Jeudi 19 : tout est dans `main`, tous les tests au vert.'],
    ['`main` contient SS-2, SS-3, SS-4, SS-5 Dash, SS-6 intégré, et les tests passent.'], echeance='jeudi 19 novembre'))
add('[S1] Démonstration du J3 et gel des fonctionnalités', [SI, C], S1, ['logiciel'], corps(
    'La démonstration du 20 novembre marque le jalon J3. Après elle, on ne développe plus de fonction nouvelle : on corrige et on vérifie seulement.',
    ['Déroulé de 10 minutes : scénario nominal, dérive lente, perte de communication, demande de confirmation, vérification du journal avec `python lancer.py --verifier`.',
     'Répétition jeudi 19 sur la version de `main`.',
     'Démonstration vendredi 20.',
     'Compte rendu : présents, commentaires reçus, décisions prises. Il alimente la section 6.1.'],
    ['La démonstration a eu lieu et le compte rendu est déposé.'], echeance='vendredi 20 novembre'))
add('[R13] Lot A, partie 1 : sections 3.2, 3.3, 3.4, 4.1 et 4.8', [C], S2, ['rapport 13'], corps(
    'Architecture d’ensemble et orchestrateur. La vue logique (3.4) fixe les noms des éléments et des flux pour tous les autres lots.',
    ['Lundi 23 : diffuser la vue logique (3.4) à l’équipe.',
     '3.2 Démarche de conception : pour chaque choix (Python ou OpenModelica, Dash ou Grafana, SQLite ou JSON Lines, T = 1 s, calage de 600 cycles, h = 9 ou 10), les options, le critère, le résultat et la décision.',
     '3.3 Vue d’ensemble : les trois vues et les préoccupations auxquelles elles répondent.',
     '3.4 Vue logique : six rubriques, figure 2-1 mise à jour.',
     '4.1 Vue d’ensemble de la conception détaillée et 4.8 Orchestrateur et informations communes.'],
    ['Les cinq sections sont rédigées et Wilson a terminé sa révision le 4 décembre.'], regles=REDAC, echeance='mercredi 2 décembre (brouillon)'))
add('[S3] Répartition du rapport final', [C], S3, ['rapport final'], corps(
    'Le rapport final et le rapport 13 sont deux documents distincts, tous deux remis le 24 décembre.',
    ['Confirmer avec M. Otis le contenu attendu du rapport final et de la recommandation d’ingénierie (L08).',
     'Répartir les sections du rapport final, en reprenant le rapport 13 au lieu de le réécrire.',
     'Publier la répartition sur Discord et créer une issue par part.'],
    ['Chaque membre connaît sa part du rapport final.'], echeance='lundi 7 décembre'))
add('[R13] Lot A, partie 2 : sections 6.2, 7.2, 9, 10 et résumé', [C], S3, ['rapport 13'], corps(
    'Gestion de projet, budget et synthèse.',
    ['6.2 Avancement : travaux, retards, imprévus, changements du RACI, retour sur les sprints, bilan Kanban et Lean, mise à jour du plan, post-mortem.',
     '7.2 Révision finale du budget, fondée sur les risques de la section 7.1 (Raouf) et les heures compilées par Wilson.',
     '9 Performance financière : courbe en S finale, IPC, IPD et IPAA comparés au rapport de concept et au rapport 12.',
     '10 Conclusion : objectifs, résultats, itérations, contraintes légales, budgétaires, socio-économiques, environnementales et technologiques, recommandations, limites, ouverture.',
     'Résumé exécutif d’environ 250 mots, en dernier.'],
    ['Sections 6.2, 7.2 et 9 le 11 décembre ; conclusion et résumé le 16 décembre.'], regles=REDAC, echeance='mercredi 16 décembre'))
add('[Dépôt] Intégration, cohérence et dépôt des deux rapports', [C], DEP, ['rapport 13', 'rapport final'], corps(
    'Dernière semaine.',
    ['Lundi 21 : les deux rapports sont complets.',
     'Mardi 22 : mêmes chiffres et mêmes verdicts dans les deux rapports.',
     'Mercredi 23 : mise en forme, table des matières (F9), export PDF.',
     'Jeudi 24 : dépôt.'],
    ['Les deux rapports sont déposés.'], echeance='jeudi 24 décembre'))
add('[Révision] Lot H : heures au 4 décembre (Wilson)', [C], S3, ['révision'], corps(
    'Vérifier le tableau des heures compilé par Wilson avant de l’utiliser aux sections 7.2 et 9.',
    ['Comparer le total de l’équipe à la feuille de temps.', 'Signaler les écarts à Wilson.'],
    ['Le tableau est vérifié.'], echeance='mardi 8 décembre'))

# ---------------- Raouf ----------------
add('[S1] SS-3 final et essai de cohérence de la condition C1', [RA], S1, ['logiciel', 'essai'], corps(
    'Chemin critique du projet : le verdict sur C1 décide si l’architecture tient (jalon J2-b).',
    ['Lundi 16 : SS-3 final fusionné dans `main` (`logiciel/jumeau/ss3_reference`), dès que SS-2 de Sidiki est fusionné.',
     'Comparer les configurations des deux campagnes nominales internes (19 essais sur 20 avec une alarme, contre 13 sur 20) : versions, graines, paramètres de SS-4.',
     'Mercredi 18 : essai de cohérence avec `validation/ss3_reference/campagne_c1.py`, 20 essais sains (graines 2001 à 2020), 600 cycles de calage puis 6 600 d’évaluation.',
     'Calculer le biais normalisé de T, P et Q avec l’intervalle de confiance à 95 % (moyenne ± 1,96 s/√20).',
     'Écrire le verdict dans un commentaire de cette issue et l’envoyer à Christian et Rayane le 18 au soir.',
     'Vendredi 20 : 5 minutes sur SS-3 et le verdict à la démonstration du J3.'],
    ['Critère de C1 : |b| ≤ 0,1σ et intervalle de confiance compris dans ±0,1σ, pour T, P et Q.',
     'Si C1 échoue : on construit la référence recalée avec Christian dès le 19, et cette issue reste ouverte.'],
    ['Tu as besoin de SS-2 final (Sidiki, lundi 16).', 'Tu remets le verdict à Rayane, qui choisit le seuil h le 19.'],
    regles=CODE, echeance='mercredi 18 novembre'))
add('[S2] Confirmation de C1 sur la version gelée', [RA], S2, ['essai'], corps(
    'Le verdict du 18 novembre porte sur la version d’avant le gel. Il faut le confirmer sur la version démontrée au J3.',
    ['Refaire la campagne C1 sur la version gelée, 20 à 30 essais sains, avec Rayane.', 'Conserver graines, versions et commandes pour qu’on puisse refaire l’essai.'],
    ['Le tableau des biais avec intervalles de confiance est remis à Rayane.'],
    ['Tu remets tes résultats à Rayane le jeudi 3 décembre (bilan L06).', 'Tu remets ton calcul d’intervalle de confiance (formule et un calcul fait à la main) à Rayane le vendredi 4 décembre (section 5.1).'],
    echeance='jeudi 3 décembre'))
add('[R13] Lot E, partie 1 : sections 3.1, 4.4 et 4.9', [RA], S2, ['rapport 13'], corps(
    'Validation de la solution préliminaire, conception détaillée de SS-3 et spécifications techniques.',
    ['3.1 Validation de la solution retenue à l’étape préliminaire : erreurs ou manques relevés (flux F7 à F9, convention S ≥ h, fenêtre de calage, résultat de C1), correctifs, avis au client.',
     '4.4 SS-3 : sept rubriques, diagramme de classes (modèle réduit, calage, résidus) et diagramme d’états (calage, boucle ouverte, bascule vers la référence recalée).',
     '4.9 Spécifications techniques : un tableau de tous les paramètres de tous les composants (paramètre, valeur, unité, origine). Chaque auteur t’envoie ses paramètres le lundi 30 novembre.'],
    ['Les trois sections sont rédigées et Rayane a terminé sa révision le 4 décembre.'], regles=REDAC, echeance='mercredi 2 décembre'))
add('[R13] Lot E, partie 2 : sections 5.2 et 7.1', [RA], S3, ['rapport 13'], corps(
    'Résultats de C1 et révision finale des risques.',
    ['5.2 Essai de cohérence et condition C1 : objectif, protocole, critère, résultats, verdict, méthode statistique expliquée et justifiée.',
     '7.1 Révision finale des risques : matrices obligatoires (probabilité et gravité avant et après mitigation), risques fermés, nouveaux risques, mesures appliquées. Partir du registre du plan de projet et de `Analyse_Risque_IMP2.xls`, et coordonner avec Christian (budget 7.2).'],
    ['5.2 le 9 décembre ; 7.1 le 11 décembre ; révision de Rayane terminée le 14.'], regles=REDAC, echeance='vendredi 11 décembre'))
add('[Révision] Lot D de Sidiki : sections 3.5, 4.3, 5.5 et 6.1', [RA], S3, ['révision'], corps(
    'Relire le lot de Sidiki avec la liste de vérification en 6 points.',
    ['3.5 et 4.3 : révision terminée le vendredi 4 décembre.', '5.5 et 6.1 : révision terminée le lundi 14 décembre.', 'Laisser les commentaires dans le document partagé.'],
    ['Sidiki a reçu tes commentaires aux deux dates.'], echeance='lundi 14 décembre'))

# ---------------- Rayane ----------------
add('[S1] SS-4 : convention S ≥ h, données invalides et choix du seuil h', [RY], S1, ['logiciel', 'essai'], corps(
    'Finaliser la décision de SS-4 avant le gel.',
    ['Mardi 17 : test unitaire de la convention S ≥ h dans `logiciel/tests/` (résidu constant de 1,5σ : déclenchement au cycle 9).',
     'Mardi 17 : données invalides (`logiciel/jumeau/ss4_decision`) : aucune mise à jour sur un résidu absent, état incertain après N = 3 cycles.',
     'Jeudi 19, après le verdict C1 de Raouf : 20 essais nominaux de 120 min avec h = 9, puis avec h = 10 (`python lancer.py scenarios/nominal.json --silencieux`, graines différentes). Compter les fausses alarmes et mesurer le délai de la dérive lente.',
     'Écrire la décision (h retenu, chiffres) dans un commentaire de cette issue.'],
    ['Les tests passent, le seuil retenu est fusionné et justifié.'], ['Tu as besoin du verdict C1 de Raouf (mercredi 18).'], regles=CODE, echeance='jeudi 19 novembre'))
add('[S2] Campagne statistique sur la version gelée', [RY, RA], S2, ['essai'], corps(
    'Mesurer les performances de détection sur la chaîne complète, et non plus sur des résidus synthétiques.',
    ['20 à 30 essais sains : fausses alarmes par essai et distribution.',
     'Dérive lente de 0,01σ par cycle : délai moyen et 95e centile sur au moins 20 essais.',
     'Saut franc de 6σ : délai de détection.',
     'Conserver graines, versions et commandes.'],
    ['Critères : au plus une fausse alarme par essai normal ; délai moyen ≤ 90 cycles et 95e centile ≤ 120 cycles pour la dérive lente.'],
    echeance='jeudi 3 décembre'))
add('[S2] Bilan exigence par exigence (livrable L06)', [RY], S2, ['essai', 'rapport 13'], corps(
    'Le bilan marque le jalon J4. Il complète la matrice de traçabilité du rapport 12 (tableau 2-3).',
    ['Un tableau : exigence (EX-F-01 à EX-F-10, EX-Q-01 à EX-Q-05), élément, essai, résultat, verdict.',
     'Recevoir les résultats le jeudi 3 décembre : Sidiki (essais EX-F et endurance), Jérémie (utilisabilité), Raouf (C1).'],
    ['Chaque exigence a un verdict, ou une raison écrite si elle n’a pas pu être vérifiée.'], echeance='vendredi 4 décembre'))
add('[R13] Lot F, partie 1 : section 4.5 SS-4', [RY], S2, ['rapport 13'], corps(
    'Conception détaillée de SS-4.',
    ['Sept rubriques.', 'Diagramme de classes : sommes cumulées, seuil instantané, calcul de la confiance.', 'Diagramme d’états normal, dérive, anomalie, incertain, avec la règle de priorité retenue.'],
    ['La section est rédigée et Jérémie a terminé sa révision le 4 décembre.'], regles=REDAC, echeance='mercredi 2 décembre'))
add('[R13] Lot F, partie 2 : sections 5.1, 5.3, 5.6 et 11', [RY], S3, ['rapport 13'], corps(
    'Calculs, performances, bilan et références.',
    ['5.1 Calculs de dimensionnement, regroupés par thème : pas de temps et temps de cycle (Ibrahima), seuils h et k, ARL0 et ARL1 (toi), intervalles de confiance (Raouf). Pour chaque calcul : formule, données, résultat, vérification faite à la main.',
     '5.3 Performances de détection, comparées au rapport de concept et au rapport 12.',
     '5.6 Bilan exigence par exigence (à partir du L06).',
     '11 Références : liste numérotée [n], numéros du rapport 12 gardés si possible.'],
    ['5.1, 5.3 et 5.6 le 9 décembre ; références le 16 décembre.'], ['Tu reçois les calculs d’Ibrahima et de Raouf le vendredi 4 décembre.'], regles=REDAC, echeance='mercredi 16 décembre'))
add('[Révision] Lot E de Raouf : sections 3.1, 4.4, 4.9, 5.2 et 7.1', [RY], S3, ['révision'], corps(
    'Relire le lot de Raouf avec la liste de vérification en 6 points.',
    ['3.1, 4.4 et 4.9 : révision terminée le vendredi 4 décembre.', '5.2 et 7.1 : révision terminée le lundi 14 décembre.'],
    ['Raouf a reçu tes commentaires aux deux dates.'], echeance='lundi 14 décembre'))

# ---------------- Ibrahima ----------------
add('[S1] SS-1 : essai d’interface et indépendance vis-à-vis de SS-2', [IB], S1, ['logiciel', 'essai'], corps(
    'Les deux vérifications de SS-1 restées ouvertes au rapport 12.',
    ['Test sur 100 cycles : aucune valeur manquante, unités du contrat de données (°C, MPa, kg/s).',
     'Test d’indépendance : les trajectoires de SS-1 sont identiques avec et sans défauts injectés par SS-2.',
     'Ajouter les tests dans `logiciel/tests/test_ss1_boucle.py`.'],
    ['Les deux tests passent dans `main`.'], regles=CODE, echeance='mercredi 18 novembre'))
add('[S1] SS-6 : intégrer le scelleur et le vérificateur au squelette', [IB], S1, ['logiciel'], corps(
    'Tu reprends SS-6 à partir du prototype de Wilson, qui te le remet lundi 16.',
    ['Intégrer l’écrivain, le scelleur et le vérificateur dans `logiciel/jumeau/ss6_journal`.',
     'Noms de champs du tableau 2-1 (pression en MPa, et non en kPa).',
     'Scelleur : seul à lire la clé privée, selon la décision d’architecture du 17 novembre.',
     'Recevoir l’événement de confirmation de SS-5 (format convenu avec Jérémie le mardi 17).',
     'Tests : journal intact, ligne modifiée détectée, ligne effacée détectée, arrêt brutal détecté (sceau final absent).'],
    ['Un essai complet produit `journal.sqlite` et `sceaux.sqlite`, et `python lancer.py --verifier` rend le verdict INTÈGRE.'],
    ['Tu reçois le module de Wilson le lundi 16.'], regles=CODE, echeance='jeudi 19 novembre'))
add('[S2] Annexe des comparaisons expérimentales de SS-1', [IB], S2, ['rapport 13'], corps(
    'Le rapport 12 mentionnait des comparaisons à des données expérimentales publiées, sans les montrer. Elles vont en annexe du rapport 13.',
    ['Pour chaque comparaison : la source complète, les données, la figure, l’écart et son interprétation.', 'Envoyer les références à Rayane.'],
    ['L’annexe est rédigée avec ses sources.'], regles=REDAC, echeance='mercredi 2 décembre'))
add('[S2] Données de calcul pour la section 5.1', [IB], S2, ['rapport 13'], corps(
    'Rayane regroupe les calculs par thème à la section 5.1.',
    ['Pas de temps : au moins 5 cycles par plus petite constante de temps (19,95 s, soit près de 20 cycles).',
     'Budget du temps de cycle : part de T utilisée par chaque composant.',
     'Fréquence des sceaux : un sceau tous les 60 cycles, soit 121 sceaux pour 7 200 cycles, et au plus 60 lignes sans sceau après un arrêt brutal.',
     'Pour chaque calcul : formule, données, résultat, vérification faite à la main.'],
    ['Rayane a reçu les trois calculs.'], echeance='vendredi 4 décembre'))
add('[R13] Lot C : sections 1, 4.2 et 4.7', [IB], S2, ['rapport 13'], corps(
    'Introduction, SS-1 et SS-6.',
    ['1 Introduction en cinq parties : 1.1 contexte et objectif, 1.2 portée, 1.3 méthodologie, 1.4 importance et impact, 1.5 structure du rapport.',
     '4.2 SS-1 : sept rubriques, diagramme des cinq volumes, calcul d’un pas.',
     '4.7 SS-6 : sept rubriques, à partir de la section de Wilson du rapport 12 ; diagramme de séquence de l’écriture d’un cycle et de la pose d’un sceau ; essais E1 à E9 refaits dans la chaîne complète.'],
    ['Les trois sections sont rédigées et Sidiki a terminé sa révision le 4 décembre.'], regles=REDAC, echeance='mercredi 2 décembre'))
add('[S3] Présentation orale du J5', [IB], S3, ['rapport final'], corps(
    'Présentation de fin de projet.',
    ['Préparer le support à partir du rapport 13 et des résultats.', 'Répétition le mercredi 16 décembre.', 'Présentation le vendredi 18 décembre.'],
    ['Le support est prêt pour la répétition du 16.'], echeance='mercredi 16 décembre'))
add('[Révision] Lot B d’Abdramane : sections 2 et 6.3', [IB], S3, ['révision'], corps(
    'Relire le lot d’Abdramane avec la liste de vérification en 6 points.',
    ['Section 2 : révision terminée le vendredi 4 décembre.', 'Section 6.3 : révision terminée le lundi 14 décembre.'],
    ['Abdramane a reçu tes commentaires aux deux dates.'], echeance='lundi 14 décembre'))

# ---------------- Sidiki ----------------
add('[S1] SS-2 final fusionné', [SI], S1, ['logiciel'], corps(
    'Raouf a besoin de la version finale de SS-2 pour l’essai de cohérence du 18 novembre.',
    ['Fusionner la version finale de `logiciel/jumeau/ss2_mesures` et ses tests.', 'Prévenir Raouf sur Discord dès la fusion.'],
    ['SS-2 final est dans `main` et les tests passent.'], regles=CODE, echeance='lundi 16 novembre au soir'))
add('[S2] Essais fonctionnels sur la version gelée', [SI], S2, ['essai'], corps(
    'Vérifier les exigences fonctionnelles sur la chaîne complète.',
    ['EX-F-02 : un même scénario avec la même graine produit le même journal.',
     'EX-F-05 : la variable désignée par SS-4 est celle où le défaut a été injecté.',
     'EX-F-06 : état incertain en N = 3 cycles au plus après une perte de communication ou une valeur hors plage.',
     'EX-F-09 : la confirmation de l’opérateur est au journal.',
     'EX-F-10 : chaque changement d’état est au journal.',
     'EX-Q-04 : une donnée malformée est rejetée, journalisée et non propagée.'],
    ['Chaque essai a son critère, son résultat et son verdict.'], ['Tu remets tes résultats à Rayane le jeudi 3 décembre.'], echeance='jeudi 3 décembre'))
add('[S2] Analyse de l’essai d’endurance et du temps de cycle', [SI], S2, ['essai'], corps(
    'Wilson lance l’essai de 120 minutes en temps réel et te remet ses relevés.',
    ['Donner à Wilson la commande à lancer : `python lancer.py scenarios/nominal.json --temps-reel`.',
     'Compter les entrées de cycle (EX-Q-02 : au moins 7 200 pour 7 200 cycles).',
     'Calculer le temps de cycle au 99e centile (EX-Q-01).',
     'Vérifier le journal avec `python lancer.py --verifier`.'],
    ['Les trois résultats ont leur verdict.'], ['Tu reçois les relevés de Wilson le lundi 30 novembre.', 'Tu remets les résultats à Rayane le jeudi 3 décembre.'], echeance='jeudi 3 décembre'))
add('[S2] Revue de conception : avis des parties prenantes du RACI', [SI], S2, ['rapport 13'], corps(
    'La grille demande une revue exhaustive, avec l’avis de toutes les parties prenantes du RACI.',
    ['Identifier dans le RACI le professeur, l’auxiliaire et le technicien.',
     'Leur présenter la conception (démonstration du J3 ou rencontre) et recueillir leur avis.',
     'Un compte rendu par rencontre : présents, commentaires, décisions.',
     'Liste des changements apportés à la conception à la suite de la revue.'],
    ['Chaque partie prenante a donné son avis, consigné par écrit.'], echeance='vendredi 4 décembre'))
add('[R13] Lot D, partie 1 : sections 3.5 et 4.3', [SI], S2, ['rapport 13'], corps(
    'Vue d’exécution et de déploiement, conception détaillée de SS-2.',
    ['3.5 : six rubriques ; diagramme de séquence d’un cycle (ordre d’appel, données, horodatage) ; chemins anormaux (mesure absente ou hors plage, perte de communication, erreur interne) ; déploiement (processus, fichiers `journal.sqlite` et `sceaux.sqlite`, clé privée, environnement reproductible). Coordonner avec Christian (4.8).',
     '4.3 SS-2 : sept rubriques ; diagramme d’activité de la qualification d’une mesure et de l’injection d’un défaut.'],
    ['Les deux sections sont rédigées et Raouf a terminé sa révision le 4 décembre.'], regles=REDAC, echeance='mercredi 2 décembre'))
add('[R13] Lot D, partie 2 : sections 5.5 et 6.1', [SI], S3, ['rapport 13'], corps(
    'Résultats d’endurance et revue de conception.',
    ['5.5 Endurance et temps de cycle : protocole, critère, résultat, verdict.',
     '6.1 Revue de conception : avis de chaque partie prenante, décisions, changements apportés.'],
    ['5.5 le 9 décembre ; 6.1 le 11 décembre ; révision de Raouf terminée le 14.'], regles=REDAC, echeance='vendredi 11 décembre'))
add('[Révision] Lot C d’Ibrahima : sections 1, 4.2 et 4.7', [SI], S2, ['révision'], corps(
    'Relire le lot d’Ibrahima avec la liste de vérification en 6 points.',
    ['Introduction, SS-1 et SS-6 : révision terminée le vendredi 4 décembre.'],
    ['Ibrahima a reçu tes commentaires.'], echeance='vendredi 4 décembre'))

# ---------------- Jérémie ----------------
add('[S1] SS-5 : interface Plotly Dash', [JE], S1, ['logiciel'], corps(
    'Remplacer la version texte de SS-5 par l’interface du concept B, mise à jour chaque seconde. Respecter la décision d’architecture du 17 novembre sur le partage d’état.',
    ['Ajouter `dash` (version exacte) à `logiciel/requirements.txt`.',
     'Vue permanente : état codé par la forme, la couleur et le libellé ; confiance ; heure d’entrée dans l’état.',
     'Bandeau des trois variables : mesure, écart à l’attendu, heure de la dernière acquisition valide.',
     'Vue de détail en un geste : une tuile par variable (mesure, attendue, écart, tendance), variables désignées par SS-4 mises en évidence.',
     'Historique des transitions (première fonction retirée si le temps manque).',
     'Les quatre états restent distincts en noir et blanc.',
     'Garder la version texte pour les essais en mode accéléré.'],
    ['L’interface s’affiche dans le navigateur pendant `python lancer.py scenarios/derive_lente.json --temps-reel` et montre la dérive au bon moment.',
     'Si ce n’est pas prêt jeudi 19 à midi, la démonstration du J3 se fait avec la version texte.'],
    regles=CODE, echeance='jeudi 19 novembre à midi'))
add('[S1] SS-5 : demande de confirmation en D2', [JE], S1, ['logiciel'], corps(
    'Exigence EX-F-09 : la confirmation de l’opérateur est demandée et journalisée.',
    ['Mardi 17 : convenir avec Ibrahima du format de l’événement envoyé au journal.',
     'Quand l’état est dérive ou anomalie non critique : demande non préremplie qui rappelle l’état, la confiance et les variables.',
     'La réponse (confirme ou refuse) part au journal avec un instantané de l’écran ; aucune commande n’est émise.',
     'Test automatique : la réponse est bien au journal.'],
    ['Le test passe dans `main`.'], regles=CODE, echeance='jeudi 19 novembre'))
add('[S1] Recruter les cinq participants de l’essai d’utilisabilité', [JE, IB, AB], S1, ['essai'], corps(
    'L’essai EX-Q-03 demande cinq personnes qui n’ont pas développé l’interface.',
    ['Trouver cinq participants (Abdramane en trouve au moins deux).', 'Fixer avec eux des créneaux entre le 23 novembre et le 2 décembre.'],
    ['Cinq participants et leurs créneaux sont notés dans cette issue.'], echeance='vendredi 20 novembre'))
add('[S2] Essai d’utilisabilité EX-Q-03', [JE, IB, AB], S2, ['essai'], corps(
    'Vérifier que l’opérateur lit correctement l’état de la boucle.',
    ['Lundi 23 : protocole écrit (20 présentations, cinq participants, tâche demandée, chronométrage).',
     'Séances avant le mercredi 2 décembre. Abdramane accueille les participants et chronomètre ; Ibrahima prend les notes.',
     'Compiler les résultats : réussites, temps, erreurs de lecture.'],
    ['Critère : au moins 18 réussites sur 20 en moins de 10 s, et aucun état anomalie ou incertain lu comme normal.'],
    ['Tu remets les résultats à Rayane le jeudi 3 décembre.'], echeance='jeudi 3 décembre'))
add('[R13] Lot G, partie 1 : sections 3.6 et 4.6', [JE], S2, ['rapport 13'], corps(
    'Vue des modes de marche et conception détaillée de SS-5.',
    ['3.6 : six rubriques ; relier les états retenus du GEMMA (A1, A2, A5, A6, F1, F2, F4, F6, D1, D2, D3) aux états du logiciel et à la confirmation en D2 ; un diagramme d’états.',
     '4.6 SS-5 : sept rubriques ; composants de l’interface ; mise à jour à chaque cycle et confirmation ; une capture de chaque vue. Même diagramme d’états qu’en 3.6.'],
    ['Les deux sections sont rédigées et Abdramane a terminé sa révision le 4 décembre.'], regles=REDAC, echeance='mercredi 2 décembre'))
add('[R13] Lot G, partie 2 : sections 5.4 et 8', [JE], S3, ['rapport 13'], corps(
    'Résultats d’utilisabilité et échéancier.',
    ['5.4 Utilisabilité : protocole, critère, résultats, verdict.', '8 Gantt révisé (`Diagram de Gant.gan`) : jalons J3 et J4 atteints ou non, dates révisées, chemin critique, réserve utilisée.'],
    ['5.4 le 9 décembre ; Gantt le 11 décembre ; révision d’Abdramane terminée le 14.'], regles=REDAC, echeance='vendredi 11 décembre'))
add('[Révision] Lot F de Rayane : sections 4.5, 5.1, 5.3, 5.6 et 11', [JE], S3, ['révision'], corps(
    'Relire le lot de Rayane avec la liste de vérification en 6 points.',
    ['4.5 : révision terminée le vendredi 4 décembre.', '5.1, 5.3, 5.6 et 11 : révision terminée le lundi 14 décembre.'],
    ['Rayane a reçu tes commentaires aux deux dates.'], echeance='lundi 14 décembre'))

# ---------------- Abdramane ----------------
add('[R13] Lot B : sections 2 et 6.3', [AB], S3, ['rapport 13'], corps(
    'Parties prenantes et développement durable.',
    ['Section 2 (mercredi 2 décembre) : un tableau de trois colonnes. Partie prenante : client Hydro-Québec, opérateur, vérificateur, Commission canadienne de sûreté nucléaire, équipe de développement, conseiller du projet. Préoccupations : sûreté, fiabilité du diagnostic, traçabilité, temps de réponse, facilité d’entretien. Vue de la section 3 qui y répond.',
     'Section 6.3 (vendredi 11 décembre), une page à une page et demie : environnement, économie, société ; contexte social, politique et socio-économique ; solutions de rechange envisagées (par exemple une boucle physique ou un service infonuagique) et pourquoi elles n’ont pas été retenues.'],
    ['Les deux sections sont rédigées et Ibrahima a terminé sa révision.'], regles=REDAC, echeance='vendredi 11 décembre'))
add('[Révision] Lot G de Jérémie : sections 3.6, 4.6, 5.4 et 8', [AB], S3, ['révision'], corps(
    'Relire le lot de Jérémie avec la liste de vérification en 6 points.',
    ['3.6 et 4.6 : révision terminée le vendredi 4 décembre.', '5.4 et 8 : révision terminée le lundi 14 décembre.'],
    ['Jérémie a reçu tes commentaires aux deux dates.'], echeance='lundi 14 décembre'))
add('[Dépôt] Mise en forme du rapport final', [AB], DEP, ['rapport final'], corps(
    'Dernière passe sur la forme.',
    ['Chaque figure et chaque tableau a une légende numérotée.', 'Définitions et abréviations complètes et en ordre alphabétique.', 'Table des matières à jour (F9).'],
    ['La mise en forme est terminée.'], echeance='mercredi 23 décembre'))

# ---------------- Wilson ----------------
add('[S1] Remettre le module SS-6 à Ibrahima', [WI], S1, ['logiciel'], corps(
    'Ibrahima intègre ton prototype de journal scellé au squelette.',
    ['Pousser ton module (écrivain, scelleur, vérificateur, script d’essais) sur une branche.',
     'Renommer les champs selon le tableau 2-1 : T, P en MPa (diviser les kPa par 1 000), Q, état.',
     'Écrire une courte note : comment lancer chaque programme, rôle de chaque fichier.',
     'Répondre aux questions d’Ibrahima pendant la semaine.'],
    ['Ibrahima a ta branche et ta note.'], echeance='lundi 16 novembre'))
add('[S2] Lancer l’essai d’endurance de 120 minutes', [WI], S2, ['essai'], corps(
    'Essai des exigences EX-Q-01 et EX-Q-02, en temps réel, sur la version gelée.',
    ['Entre le 23 et le 27 novembre, lancer `python lancer.py scenarios/nominal.json --temps-reel` depuis le dossier `logiciel` (la commande exacte est confirmée par Sidiki).',
     'Laisser tourner les 120 minutes sans fermer le programme.',
     'Relever le dossier de sortie, le nombre d’entrées de cycle et le verdict de `python lancer.py --verifier sorties/<dossier>/journal.sqlite`.'],
    ['Sidiki a reçu le dossier de sortie et tes relevés.'], ['Tu remets tout à Sidiki le lundi 30 novembre.'], echeance='lundi 30 novembre'))
add('[S3] Compiler les heures au 4 décembre', [WI], S3, ['rapport 13'], corps(
    'Christian en a besoin pour le budget (7.2) et la courbe en S (9).',
    ['À partir des feuilles de temps, un tableau : membre, heures cumulées au 4 décembre.', 'Total de l’équipe.'],
    ['Christian a reçu le tableau.'], echeance='lundi 7 décembre'))
add('[Révision] Lot A de Christian', [WI], S3, ['révision'], corps(
    'Relire le lot de Christian avec la liste de vérification en 6 points.',
    ['3.2, 3.3, 3.4, 4.1 et 4.8 : révision terminée le vendredi 4 décembre.', '6.2, 7.2 et 9 : révision terminée le lundi 14 décembre.'],
    ['Christian a reçu tes commentaires aux deux dates.'], echeance='lundi 14 décembre'))
add('[Dépôt] Relecture de la langue du rapport final', [WI], DEP, ['rapport final'], corps(
    'Dernière relecture.',
    ['Orthographe, accords, ponctuation.', 'Signaler les phrases peu claires à leur auteur.'],
    ['La relecture est terminée.'], echeance='mardi 22 décembre'))



DEPOT = 'cKEVIN-Sawadogo/IMP-II-Automne-2026'
DATES = {S1: '2026-11-20T23:59:00Z', S2: '2026-12-04T23:59:00Z', S3: '2026-12-18T23:59:00Z', DEP: '2026-12-24T23:59:00Z'}
DESC = {S1: 'Du 16 au 20 novembre. Le prototype intégré est démontré au J3 et ses fonctionnalités sont gelées.',
        S2: 'Du 21 novembre au 4 décembre. La campagne d’essais est terminée au J4 et les sections 1 à 4 du rapport 13 sont rédigées.',
        S3: 'Du 5 au 18 décembre. Les deux rapports sont complets et la présentation du J5 est prête.',
        DEP: 'Du 19 au 24 décembre. Intégration, relecture et dépôt du rapport 13 et du rapport final.'}
COULEURS = {'ingénierie détaillée': '5319e7', 'logiciel': '1d76db', 'essai': 'fbca04', 'rapport 13': '0e8a16',
            'rapport final': 'c5def5', 'révision': 'd4c5f9'}

def gh(*args, donnees=None):
    p = subprocess.run(['gh', *args], input=json.dumps(donnees) if donnees is not None else None,
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode:
        sys.exit(f'Erreur de gh {" ".join(args[:3])} : {p.stderr.strip()}')
    return json.loads(p.stdout) if p.stdout.strip().startswith(('{', '[')) else p.stdout

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--essai', action='store_true', help='affiche sans rien créer')
    ap.add_argument('--projet', type=int, help='numéro du tableau GitHub Projects')
    a = ap.parse_args()
    if a.essai:
        for it in I:
            print(f"{it['milestone'][:8]} | {', '.join(it['assignees']):45} | {it['title']}")
        print(f'{len(I)} issues.'); return
    R = f'repos/{DEPOT}'
    jalons = {m['title']: m['number'] for m in gh('api', f'{R}/milestones?state=all&per_page=100')}
    for t in DATES:
        if t not in jalons:
            jalons[t] = gh('api', '-X', 'POST', f'{R}/milestones', '--input', '-',
                           donnees={'title': t, 'due_on': DATES[t], 'description': DESC[t]})['number']
    etiquettes = {l['name'] for l in gh('api', f'{R}/labels?per_page=100')}
    for n, c in COULEURS.items():
        if n not in etiquettes:
            gh('api', '-X', 'POST', f'{R}/labels', '--input', '-', donnees={'name': n, 'color': c})
    existantes = {i['title'] for i in gh('api', f'{R}/issues?state=all&per_page=100&labels=ing%C3%A9nierie%20d%C3%A9taill%C3%A9e')}
    for it in I:
        if it['title'] in existantes:
            print('déjà là :', it['title']); continue
        r = gh('api', '-X', 'POST', f'{R}/issues', '--input', '-', donnees={
            'title': it['title'], 'body': it['body'], 'assignees': it['assignees'],
            'labels': it['labels'], 'milestone': jalons[it['milestone']]})
        print(f"#{r['number']} {it['title']}")
        if a.projet:
            gh('project', 'item-add', str(a.projet), '--owner', DEPOT.split('/')[0], '--url', r['html_url'])

if __name__ == '__main__':
    main()
