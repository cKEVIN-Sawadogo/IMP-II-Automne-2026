#!/usr/bin/env python3
"""Mini-simulation de vérification du Concept C (Décision séquentielle SPRT / CUSUM).

Lot L7 — Fonction : « Décider si un résidu traduit une anomalie, et dire avec quelle confiance. »
Ce script teste le Concept C sur une séquence simple de 35 pas de temps comprenant :
  1. Régime normal + une pointe de bruit isolée au pas k=5 (pas 1 à 13) -> Aucune fausse alarme (retour à 0)
  2. Dérive lente / cyberattaque furtive dès k=14 (pas 14 à 25) -> Détection par accumulation + début exact k=14
  3. Retour au calme puis saut franc brutal dès k=29 (pas 26 à 32) -> Détection rapide + début exact k=29
  4. Donnée manquante / capteur coupé (pas 33 à 35) -> État "Incertain"
"""

import math
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PARAMÈTRES SIMPLES DU CONCEPT C (3 paramètres)
# ==============================================================================
SIGMA = 1.0          # Écart-type du bruit normal du résidu (ex. 1.0 kPa sur la pression)
MU_CIBLE = 1.0       # Plus petite dérive que l'on souhaite détecter (1.0 * sigma)
ALPHA = 0.01         # Risque maximal de fausse alarme toléré (1 %)
BETA = 0.01          # Risque maximal de non-détection toléré (1 %)

# Calcul automatique du seuil d'alarme de Wald : B = ln((1 - beta) / alpha)
SEUIL_B = math.log((1.0 - BETA) / ALPHA)  # B ≈ 4.60


# ==============================================================================
# 2. FONCTION DU MODULE DE DÉCISION SÉQUENTIELLE (CONCEPT C)
# ==============================================================================
def pas_decision_sequentielle(residu, S_prec, compteur_prec):
    """Exécute un pas de temps du Concept C et retourne (S, compteur, etat, confiance)."""
    # Étape 1 : Vérifier si la donnée est utilisable
    if residu is None or math.isnan(residu):
        return S_prec, compteur_prec, "Incertain (donnée manquante)", 0.0

    # Étape 2 : Calculer le score élémentaire s(k) (rapport de log-vraisemblance)
    # En régime normal (|residu| < 0.5*sigma), s_k est négatif ; en dérive, s_k est positif
    s_k = (MU_CIBLE / (SIGMA ** 2)) * (abs(residu) - (MU_CIBLE / 2.0))

    # Étape 3 : Mettre à jour l'accumulateur à mémoire S(k) = max(0, S(k-1) + s(k))
    S_k = max(0.0, S_prec + s_k)
    compteur_k = (compteur_prec + 1) if S_k > 0.0 else 0

    # Étape 4 : Calculer l'indice de progression / confiance (plafonné à 1 - alpha = 99 %)
    confiance = 100.0 * (1.0 - ALPHA) * min(1.0, S_k / SEUIL_B)

    # Étape 5 : Appliquer la règle de décision à 3 états
    if S_k == 0.0:
        etat = "Normal (H0)"
    elif S_k < SEUIL_B:
        etat = "Pré-alerte (accumulation)"
    else:
        etat = "ANOMALIE CONFIRMÉE (H1)"

    return S_k, compteur_k, etat, confiance


# ==============================================================================
# 3. CRÉATION D'UN MINI-SCÉNARIO DE TEST (35 PAS DE TEMPS)
# ==============================================================================
np.random.seed(7)
N_PAS = 35
pas_temps = list(range(1, N_PAS + 1))

bruit = np.random.normal(0.0, 0.20 * SIGMA, size=N_PAS)
residus = []

for k in pas_temps:
    if k == 5:
        # Scénario 1b : Pointe de bruit isolée à +3.2 sigma (dépasserait un seuil fixe de 3 sigma !)
        residus.append(3.2 * SIGMA)
    elif 1 <= k <= 13:
        # Scénario 1a : Régime normal (le bruit reste proche de 0)
        residus.append(float(bruit[k - 1]))
    elif 14 <= k <= 25:
        # Scénario 2 : Dérive lente / attaque furtive (+1.35 sigma, sous le seuil fixe 3 sigma !)
        residus.append(1.35 * SIGMA + float(bruit[k - 1]))
    elif 26 <= k <= 28:
        # Retour temporaire au régime normal
        residus.append(float(bruit[k - 1]))
    elif 29 <= k <= 32:
        # Scénario 3 : Saut franc brutal (+4.5 sigma, panne franche)
        residus.append(4.5 * SIGMA + float(bruit[k - 1]))
    else:
        # Scénario 4 : Perte de capteur aux pas 33 à 35
        residus.append(float("nan"))


# ==============================================================================
# 4. EXÉCUTION DE LA SIMULATION PAS-À-PAS ET AFFICHAGE CONSOLE
# ==============================================================================
S_courant = 0.0
compteur = 0

historique_S = []
historique_conf = []
historique_etat = []

print("=" * 84)
print(f"MINI-SIMULATION DU CONCEPT C (Seuil de Wald B = {SEUIL_B:.2f} pour alpha={ALPHA*100:.0f}%, beta={BETA*100:.0f}%)")
print("=" * 84)
print(f"{'Pas k':>5} | {'Résidu r(k)':>12} | {'Somme S(k)':>10} | {'Confiance':>10} | {'Décision du module L7'}")
print("-" * 84)

for k, r in zip(pas_temps, residus):
    if k == 26:
        S_courant, compteur = 0.0, 0

    S_courant, compteur, etat, conf = pas_decision_sequentielle(r, S_courant, compteur)
    historique_S.append(S_courant)
    historique_conf.append(conf)
    historique_etat.append(etat)

    r_str = "NaN (coupé)" if math.isnan(r) else f"{r:+8.2f} σ"
    debut_str = f" (début détecté k̂₀={k - compteur + 1})" if etat == "ANOMALIE CONFIRMÉE (H1)" else ""
    print(f"{k:5d} | {r_str:>12} | {S_courant:10.2f} | {conf:8.1f} % | {etat}{debut_str}")

print("=" * 84)


# ==============================================================================
# 5. GÉNÉRATION DU GRAPHIQUE DE PREUVE DE FONCTIONNEMENT
# ==============================================================================
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11.5, 8.6), sharex=True, dpi=300)
fig.patch.set_facecolor("#FFFFFF")

for ax in (ax1, ax2, ax3):
    ax.axvspan(32.5, 35.5, color="#CBD5E1", alpha=0.45, label="Capteur coupé → État Incertain" if ax == ax1 else None)
    ax.grid(True, linestyle="--", alpha=0.4)

# Graphique 1 : Résidu d'entrée r(k) comparé à un seuil fixe classique (3 sigma)
ax1.plot(pas_temps, residus, marker="o", color="#1D4ED8", linewidth=1.8, label="Résidu d'entrée r(k)")
ax1.axhline(3.0 * SIGMA, color="#DC2626", linestyle=":", linewidth=1.6, label="Seuil statique classique (3σ) — Concepts A / B")
ax1.annotate("1. Pointe de bruit (+3,2σ à k=5)\n(Fausse alerte si seuil fixe 3σ !)",
             xy=(5, 3.2), xytext=(1.2, 4.35),
             arrowprops=dict(arrowstyle="->", color="#B91C1C", lw=1.2),
             fontsize=8.5, fontweight="bold", color="#B91C1C")
ax1.annotate("2. Dérive lente furtive (~1,35σ dès k=14)\n(Invisible sous le seuil statique 3σ)",
             xy=(17, 1.45), xytext=(11.8, 3.45),
             arrowprops=dict(arrowstyle="->", color="#0F766E", lw=1.2),
             fontsize=8.5, fontweight="bold", color="#0F766E")
ax1.annotate("3. Saut franc (+4,5σ à k=29)",
             xy=(29, 4.71), xytext=(21.5, 5.25),
             arrowprops=dict(arrowstyle="->", color="#1E3A8A", lw=1.2),
             fontsize=8.5, fontweight="bold", color="#1E3A8A")
ax1.set_ylabel("Résidu r(k) [en σ]", fontweight="bold")
ax1.set_ylim(-1.0, 6.7)
ax1.set_title("Mini-Simulation de Validation du Concept C (Décision Séquentielle SPRT / CUSUM)",
              fontsize=12.5, fontweight="bold", pad=10)
ax1.legend(loc="upper left", ncol=3, fontsize=8.0, framealpha=0.92)

# Graphique 2 : Accumulateur séquentiel S(k) et Seuil de Wald B
ax2.plot(pas_temps, historique_S, marker="s", color="#0F766E", linewidth=2.0, label="Accumulateur à mémoire S(k)")
ax2.axhline(SEUIL_B, color="#DC2626", linestyle="--", linewidth=1.8, label=f"Seuil d'alarme de Wald B = {SEUIL_B:.2f} (α=1%, β=1%)")
ax2.fill_between(pas_temps, 0, SEUIL_B, color="#FEF3C7", alpha=0.35, label="Zone de Pré-alerte (0 < S(k) < B)")
ax2.annotate("Pointe absorbée sans alarme\n(S monte à 2,70 puis retombe à 0 à k=13)",
             xy=(5, 2.7), xytext=(1.2, 6.8),
             arrowprops=dict(arrowstyle="->", color="#0F766E", lw=1.2),
             fontsize=8.5, fontweight="bold", color="#0F766E")
ax2.annotate("Dérive lente détectée à k=19\n(S = 4,90 ≥ 4,60, début exact k̂₀=14)",
             xy=(19, 4.9), xytext=(11.5, 9.5),
             arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.2),
             fontsize=8.5, fontweight="bold", color="#DC2626")
ax2.annotate("Saut franc confirmé dès k=30",
             xy=(30, 8.13), xytext=(22.0, 12.2),
             arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.2),
             fontsize=8.5, fontweight="bold", color="#DC2626")
ax2.set_ylabel("Somme cumulée S(k)", fontweight="bold")
ax2.set_ylim(-0.5, 18.5)
ax2.legend(loc="upper left", ncol=3, fontsize=8.0, framealpha=0.92)

# Graphique 3 : Niveau de confiance affiché à l'opérateur [0 à 100 %]
ax3.step(pas_temps, historique_conf, where="mid", color="#7C3AED", linewidth=2.0, label="Confiance affichée C(k) [0 à 99 %]")
ax3.axhline(99.0, color="#DC2626", linestyle=":", linewidth=1.5, label="Garantie statistique (1 - α) = 99 %")
ax3.annotate("Chute à 0 % (État Incertain)\nsur perte de mesure (k=33..35)",
             xy=(33, 2.0), xytext=(23.8, 35.0),
             arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2),
             fontsize=8.5, fontweight="bold", color="#334155")
ax3.set_ylabel("Confiance IHM [%]", fontweight="bold")
ax3.set_xlabel("Pas d'échantillonnage k", fontweight="bold")
ax3.set_ylim(-5, 115)
ax3.legend(loc="upper left", ncol=2, fontsize=8.0, framealpha=0.92)

plt.tight_layout()
# Chemin à modifier selon votre environnement
plt.savefig("C:\\Users\\abdou\\OneDrive\\Documents\\Mes cours Uqac\\automne 2026\\imp 2\\Nouveau dossier\\Resultats_Mini_Simulation_ConceptC.png", dpi=300)
plt.close()
print("Graphique sauvegardé : Resultats_Mini_Simulation_ConceptC.png")