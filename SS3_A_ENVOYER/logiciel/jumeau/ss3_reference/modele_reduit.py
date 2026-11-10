from __future__ import annotations

import math

# Modèle 0D réduit de SS-3.
# Il est volontairement plus simple que le modèle SS-1 à cinq volumes.
# Il utilise uniquement les consignes du scénario.

FROID = 20.0

# Paramètres réduits provisoires.
# Ils seront ajustés avec les mesures saines de SS-2 pendant le calage.
GAIN_T = 0.0123923445      # °C/W au point nominal
TAU_T = 120.0              # constante de temps thermique réduite, s


def debit_attendu(vitesse_pompe: float) -> float:
    """Débit massique attendu en kg/s."""
    return 0.1 * float(vitesse_pompe)


def pression_attendue(vitesse_pompe: float) -> float:
    """Pression absolue attendue en MPa."""
    v = float(vitesse_pompe)
    return 0.1 + 0.008 * v * v


def temperature_equilibre(
    vitesse_pompe: float,
    puissance_W: float,
) -> float:
    """Température d'équilibre simplifiée en °C."""
    v = max(float(vitesse_pompe), 1e-6)
    p = float(puissance_W)

    return FROID + GAIN_T * p / v


def avancer_temperature(
    temperature: float,
    vitesse_pompe: float,
    puissance_W: float,
    dt: float,
) -> float:
    """Avance le modèle thermique réduit d'un cycle."""
    cible = temperature_equilibre(vitesse_pompe, puissance_W)

    return temperature + dt * (cible - temperature) / TAU_T