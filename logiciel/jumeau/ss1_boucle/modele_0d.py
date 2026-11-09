"""Équations du modèle 0D à cinq volumes.

Reprises de simuler_ss1_0d.py (Ibrahima Diallo, dossier de validation SS-1).
Seule la puissance de chauffe devient un paramètre au lieu d'une constante.
Les coefficients hydrauliques sont des propositions non validées
expérimentalement, comme l'indique son dossier.
"""
from __future__ import annotations

import numpy as np

M = np.array([6.0, 3.0, 5.0, 3.0, 3.0])  # masse de chaque volume (kg)
CP = 4180.0                               # capacité thermique de l'eau (J/(kg·K))
UA = 100.0                                # conductance de l'échangeur (W/K)
FROID = 20.0                              # température de la source froide (°C)


def matrices(vitesse_pompe: float, puissance_W: float):
    """Renvoie (A, b, débit en kg/s, pression absolue en MPa) pour dT/dt = A·T + b."""
    q = np.sqrt(10000 * vitesse_pompe**2 / (2e11 + 8e11))  # débit volumique (m³/s)
    debit = 1000 * q
    A = np.zeros((5, 5))
    b = np.zeros(5)
    for i in range(5):
        A[i, i] = -debit / M[i]
        A[i, (i - 1) % 5] = debit / M[i]
    A[2, 2] -= UA / (M[2] * CP)
    b[0] = puissance_W / (M[0] * CP)
    b[2] = UA * FROID / (M[2] * CP)
    pression = 0.1 + 8e11 * q * q / 1e6
    return A, b, debit, pression


def regime_etabli(vitesse_pompe: float, puissance_W: float) -> np.ndarray:
    """Températures des cinq volumes en régime établi."""
    A, b, _, _ = matrices(vitesse_pompe, puissance_W)
    return np.linalg.solve(A, -b)
