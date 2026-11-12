"""Interface commune des sous-systèmes.

L'orchestrateur ne connaît que cette interface. Chaque membre peut donc
remplacer l'intérieur de son module sans rien changer chez les autres, tant
qu'il respecte les clés d'entrée et de sortie décrites dans son module.
"""
from __future__ import annotations


class SousSysteme:
    """Classe de base d'un sous-système.

    Cycle de vie, piloté par l'orchestrateur :
      1. demarrer(contexte) une fois, avant le premier cycle ;
      2. etape(k, entrees) une fois par cycle, dans l'ordre SS-1 à SS-6 ;
      3. arreter() une fois, après le dernier cycle.

    Une sortie peut contenir la clé « evenements » : une liste de dict que
    l'orchestrateur transmet à SS-6 pour le journal (flux E).
    """

    nom = "SS-?"

    def demarrer(self, contexte: dict) -> None:
        """Reçoit la graine, le scénario et le dossier de sortie."""

    def etape(self, k: int, entrees: dict) -> dict:
        raise NotImplementedError

    def arreter(self) -> None:
        """Libère les ressources (fichiers, connexions)."""
