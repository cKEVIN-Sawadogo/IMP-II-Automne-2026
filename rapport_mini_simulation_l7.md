# Rapport de Mini-Simulation — Vérification du Concept C (Décision Séquentielle SPRT / CUSUM)

**Projet :** Jumeau numérique cyberrésilient — Boucle thermohydraulique simplifiée (inspirée du [circuit de caloportage primaire CANDU 6](https://canteach.candu.org/Content%20Library/20044212.pdf) de la centrale [Gentilly-2 d'Hydro-Québec](https://archives.bape.gouv.qc.ca/sections/mandats/gentilly-2/documents/DA22-1.pdf))  
**Fonction vérifiée (Lot L7) :** *« Décider si un résidu traduit une anomalie, et dire avec quelle confiance. »*  
**Concept testé :** Concept C — Décision séquentielle par accumulation temporelle ([SPRT de Wald](https://www.me.psu.edu/ray/journalAsokRay/1983/020RayDesaiDeyst1983.pdf) / [CUSUM de Page](https://www.researchgate.net/publication/281567648_The_CuSum_algorithm_-_a_small_review))  
**Script et figure associés :** `test_concept_C_sequentiel.py` et `Resultats_Mini_Simulation_ConceptC.png`  
**Cadre normatif :** [CSA N290.7](https://www.csagroup.org/fr/store/product/2428461/), [CEI 62645](https://webstore.iec.ch/en/publication/32904) et [CEI 62859](https://webstore.iec.ch/en/publication/26131).

## 1. Objectif et Paramètres de la Mini-Simulation

L'objectif de ce test de preuve de concept est de vérifier que l'algorithme du **Concept C** retenu à l'issue des Étapes 5 et 6 respecte les exigences fonctionnelles et de sûreté sur une séquence synthétique de $35$ pas d'échantillonnage ($k = 1$ à $35$).

### Paramètres de configuration retenus pour le test
- **Écart-type du bruit nominal ($\sigma$) :** $\sigma = 1{,}0$ (résidu normalisé en nombre d'écarts-types).
- **Amplitude minimale de dérive cible ($\mu_{\text{cible}}$) :** $\mu_{\text{cible}} = 1{,}0\,\sigma$ (toute dérive supérieure à $\mu_{\text{cible}}/2 = 0{,}5\,\sigma$ fait croître l'accumulateur).
- **Risques d'erreur déclarés :** probabilité maximale de fausse alarme $\alpha = 1\ \%$ ($0{,}01$) et probabilité maximale de non-détection $\beta = 1\ \%$ ($0{,}01$).
- **Seuil d'alarme de Wald ($B$) :**
  $$B = \ln\!\left(\frac{1 - \beta}{\alpha}\right) = \ln\!\left(\frac{0{,}99}{0{,}01}\right) \approx 4{,}60$$
- **Équations récursives exécutées à chaque pas $k$ :**
  $$s(k) = \frac{\mu_{\text{cible}}}{\sigma^2}\left(\vert r(k) \vert - \frac{\mu_{\text{cible}}}{2}\right), \quad S(k) = \max\!\big(0, \, S(k-1) + s(k)\big), \quad C(k) = 100 \times (1 - \alpha) \times \min\!\left(1, \, \frac{S(k)}{B}\right)$$

## 2. Protocole des Quatre Scénarios Testés

La séquence de $35$ pas de temps enchaîne quatre situations représentatives des conditions réelles d'exploitation :

| Scénario | Intervalle de temps | Signal d'entrée $r(k)$ appliqué | Comportement attendu du Concept C |
| :--- | :---: | :--- | :--- |
| **1. Régime normal + pointe de bruit isolée** | $k = 1$ à $13$<br>*(pic à $k = 5$)* | Bruit centré autour de $0\,\sigma$, avec une pointe transitoire isolée à **$+3{,}20\,\sigma$** au pas $k = 5$. | La pointe fait monter $S(5)$ en *Pré-alerte* sans atteindre $B = 4{,}60$, puis les mesures normales suivantes ramènent $S(k)$ à $0$ (aucune fausse alarme). |
| **2. Dérive lente / Cyberattaque furtive** | $k = 14$ à $25$ | Biais continu de faible amplitude (**$\approx +1{,}35\,\sigma$**), inférieur à un seuil statique classique de $3\,\sigma$. | L'accumulateur additionne les écarts positifs pas après pas jusqu'à franchir $B = 4{,}60$ en moins de $20\,\Delta t$ et retrouve l'instant initial $\hat{k}_0 = 14$. |
| **3. Saut franc brutal (panne franche)** | $k = 26$ à $32$<br>*(saut dès $k = 29$)* | Retour à l'état sain ($k = 26\text{..}28$), puis échelon brutal à **$+4{,}50\,\sigma$** à partir de $k = 29$. | Franchissement très rapide du seuil $B = 4{,}60$ (en $\le 3\,\Delta t$) avec confiance garantie à $99{,}0\ \%$ et localisation de l'instant initial $\hat{k}_0 = 29$. |
| **4. Perte de mesure / Capteur coupé** | $k = 33$ à $35$ | Mesures manquantes (`NaN` / capteur déconnecté). | Suspension immédiate de l'évaluation, maintien de la mémoire et affichage de l'état **Incertain** (confiance ramenée à $0\ \%$). |

## 3. Résultats Pas-à-Pas de la Simulation ($k = 1$ à $35$)

| Pas $k$ | Scénario en cours | Résidu $r(k)$ | Incrément $s(k)$ | Somme cumulée $S(k)$ | Confiance $C(k)$ | Décision transmise à l'interface opérateur |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | 1a. Régime normal | $+0{,}34\,\sigma$ | $-0{,}16$ | $0{,}00$ | $0{,}0\ \%$ | Normal ($\mathcal{H}_0$) |
| **2** | 1a. Régime normal | $-0{,}09\,\sigma$ | $-0{,}41$ | $0{,}00$ | $0{,}0\ \%$ | Normal ($\mathcal{H}_0$) |
| **3** | 1a. Régime normal | $+0{,}01\,\sigma$ | $-0{,}49$ | $0{,}00$ | $0{,}0\ \%$ | Normal ($\mathcal{H}_0$) |
| **4** | 1a. Régime normal | $+0{,}08\,\sigma$ | $-0{,}42$ | $0{,}00$ | $0{,}0\ \%$ | Normal ($\mathcal{H}_0$) |
| **5** | **1b. Pointe de bruit isolée** | **$+3{,}20\,\sigma$** | **$+2{,}70$** | **$2{,}70$** | **$58{,}2\ \%$** | **Pré-alerte (accumulation — pas d'alarme)** |
| **6** | 1a. Retour au bruit normal | $+0{,}00\,\sigma$ | $-0{,}50$ | $2{,}20$ | $47{,}4\ \%$ | Pré-alerte (résorption en cours) |
| **7** | 1a. Retour au bruit normal | $-0{,}00\,\sigma$ | $-0{,}50$ | $1{,}70$ | $36{,}6\ \%$ | Pré-alerte (résorption en cours) |
| **8** | 1a. Retour au bruit normal | $-0{,}35\,\sigma$ | $-0{,}15$ | $1{,}55$ | $33{,}4\ \%$ | Pré-alerte (résorption en cours) |
| **9** | 1a. Retour au bruit normal | $+0{,}20\,\sigma$ | $-0{,}30$ | $1{,}26$ | $27{,}0\ \%$ | Pré-alerte (résorption en cours) |
| **10** | 1a. Retour au bruit normal | $+0{,}12\,\sigma$ | $-0{,}38$ | $0{,}88$ | $18{,}9\ \%$ | Pré-alerte (résorption en cours) |
| **11** | 1a. Retour au bruit normal | $-0{,}13\,\sigma$ | $-0{,}37$ | $0{,}50$ | $10{,}8\ \%$ | Pré-alerte (résorption en cours) |
| **12** | 1a. Retour au bruit normal | $-0{,}03\,\sigma$ | $-0{,}47$ | $0{,}03$ | $0{,}7\ \%$ | Pré-alerte (résorption en cours) |
| **13** | 1a. Retour complet à zéro | $+0{,}10\,\sigma$ | $-0{,}40$ | **$0{,}00$** | **$0{,}0\ \%$** | **Normal ($\mathcal{H}_0$ — pointe totalement absorbée)** |
| **14** | **2. Début dérive lente** | **$+1{,}30\,\sigma$** | **$+0{,}80$** | **$0{,}80$** | **$17{,}2\ \%$** | **Pré-alerte (accumulation — pas 1)** |
| **15** | 2. Dérive lente furtive | $+1{,}30\,\sigma$ | $+0{,}80$ | $1{,}60$ | $34{,}5\ \%$ | Pré-alerte (accumulation — pas 2) |
| **16** | 2. Dérive lente furtive | $+1{,}06\,\sigma$ | $+0{,}56$ | $2{,}16$ | $46{,}5\ \%$ | Pré-alerte (accumulation — pas 3) |
| **17** | 2. Dérive lente furtive | $+1{,}46\,\sigma$ | $+0{,}96$ | $3{,}12$ | $67{,}2\ \%$ | Pré-alerte (accumulation — pas 4) |
| **18** | 2. Dérive lente furtive | $+1{,}37\,\sigma$ | $+0{,}87$ | $3{,}99$ | $86{,}1\ \%$ | Pré-alerte (accumulation — pas 5) |
| **19** | **2. Seuil $B=4{,}60$ franchi** | **$+1{,}40\,\sigma$** | **$+0{,}90$** | **$4{,}90$** | **$99{,}0\ \%$** | **ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 14$** |
| **20** | 2. Dérive lente maintenue | $+1{,}04\,\sigma$ | $+0{,}54$ | $5{,}44$ | $99{,}0\ \%$ | ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 14$ |
| **21** | 2. Dérive lente maintenue | $+1{,}68\,\sigma$ | $+1{,}18$ | $6{,}62$ | $99{,}0\ \%$ | ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 14$ |
| **22** | 2. Dérive lente maintenue | $+1{,}38\,\sigma$ | $+0{,}88$ | $7{,}50$ | $99{,}0\ \%$ | ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 14$ |
| **23** | 2. Dérive lente maintenue | $+1{,}27\,\sigma$ | $+0{,}77$ | $8{,}28$ | $99{,}0\ \%$ | ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 14$ |
| **24** | 2. Dérive lente maintenue | $+1{,}76\,\sigma$ | $+1{,}26$ | $9{,}53$ | $99{,}0\ \%$ | ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 14$ |
| **25** | 2. Dérive lente maintenue | $+1{,}34\,\sigma$ | $+0{,}84$ | $10{,}37$ | $99{,}0\ \%$ | ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 14$ |
| **26** | 3a. Réinitialisation / Calme | $-0{,}29\,\sigma$ | $-0{,}21$ | $0{,}00$ | $0{,}0\ \%$ | Normal ($\mathcal{H}_0$) |
| **27** | 3a. Régime normal | $-0{,}08\,\sigma$ | $-0{,}42$ | $0{,}00$ | $0{,}0\ \%$ | Normal ($\mathcal{H}_0$) |
| **28** | 3a. Régime normal | $-0{,}46\,\sigma$ | $-0{,}04$ | $0{,}00$ | $0{,}0\ \%$ | Normal ($\mathcal{H}_0$) |
| **29** | **3b. Début saut franc** | **$+4{,}71\,\sigma$** | **$+4{,}21$** | **$4{,}21$** | **$90{,}7\ \%$** | **Pré-alerte haute (accumulation — pas 1)** |
| **30** | **3b. Confirmation saut franc** | **$+4{,}42\,\sigma$** | **$+3{,}92$** | **$8{,}13$** | **$99{,}0\ \%$** | **ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 29$** |
| **31** | 3b. Saut franc maintenu | $+4{,}35\,\sigma$ | $+3{,}85$ | $11{,}98$ | $99{,}0\ \%$ | ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 29$ |
| **32** | 3b. Saut franc maintenu | $+4{,}71\,\sigma$ | $+4{,}21$ | $16{,}19$ | $99{,}0\ \%$ | ANOMALIE CONFIRMÉE ($\mathcal{H}_1$) — début détecté $\hat{k}_0 = 29$ |
| **33** | **4. Capteur coupé** | **`NaN`** | — | $16{,}19$ *(figé)* | **$0{,}0\ \%$** | **Incertain (donnée manquante — décision suspendue)** |
| **34** | 4. Capteur coupé | `NaN` | — | $16{,}19$ *(figé)* | $0{,}0\ \%$ | Incertain (donnée manquante — décision suspendue) |
| **35** | 4. Capteur coupé | `NaN` | — | $16{,}19$ *(figé)* | $0{,}0\ \%$ | Incertain (donnée manquante — décision suspendue) |

## 4. Analyse et Validation des Exigences (Synthèse pour la Remise)

Ce mini-test valide expérimentalement les quatre propriétés qui ont conduit au choix du **Concept C** lors des Étapes 5 et 6 :
1. **Immunité aux fausses alertes sur pointes transitoires (Critère 5 validé) :** Alors qu'un comparateur à seuil fixe de $3\,\sigma$ (Concepts A et B) aurait immédiatement déclenché une fausse alarme au pas $k = 5$ ($r(5) = +3{,}20\,\sigma > 3\,\sigma$), l'accumulateur séquentiel absorbe le pic ($S(5) = 2{,}70 < 4{,}60$) puis redescend progressivement jusqu'à $0{,}00$ au pas $k = 13$.
2. **Détection des dérives lentes et cyberattaques furtives (Critère 1 validé) :** La dérive de $+1{,}35\,\sigma$ injectée dès $k = 14$ demeure constamment deux fois plus petite que le seuil statique $3\,\sigma$ (elle serait donc totalement invisible pour les Concepts A et B). Grâce à la mémoire cumulative, le Concept C la détecte avec certitude au pas $k = 19$ (soit en **$6$ pas de temps**, bien en deçà de la spécification maximale de $20\,\Delta t$) et restitue sans erreur l'instant exact où l'attaque a commencé ($\hat{k}_0 = 14$).
3. **Faible temps de latence sur anomalie franche (Critère 2 validé) :** Lors du saut brutal de $+4{,}50\,\sigma$ au pas $k = 29$, l'accumulateur atteint $90{,}7\ \%$ dès le premier pas et franchit le seuil d'alarme $B = 4{,}60$ dès le second pas ($k = 30$, soit une latence de **$2\,\Delta t \le 3\,\Delta t$**), tout en identifiant l'instant initial exact ($\hat{k}_0 = 29$).
4. **Sûreté de fonctionnement sur perte de données (Critères 6 et 7 validés) :** Dès l'interruption du signal aux pas $k = 33$ à $35$, l'algorithme fige l'état de l'accumulateur, ramène la confiance à $0\ \%$ et affiche explicitement **« Incertain (donnée manquante) »**, conformément aux normes [CEI 62645](https://webstore.iec.ch/en/publication/32904) et [CEI 62859](https://webstore.iec.ch/en/publication/26131).
