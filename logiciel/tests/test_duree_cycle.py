"""G5 : la durée de calcul de chaque cycle est journalisée, pour mesurer EX-Q-01.

Le cycle k porte la durée du cycle k-1, journal et cache compris : celle du cycle k n'est
connue qu'après son écriture au journal. Le premier cycle n'en porte donc pas.
"""
import json
import sqlite3
import statistics
from pathlib import Path

from jumeau.orchestrateur import Orchestrateur
from jumeau.scenario import charger

SCENARIOS = Path(__file__).resolve().parent.parent / "scenarios"


def test_la_duree_de_chaque_cycle_est_journalisee(tmp_path):
    Orchestrateur(charger(SCENARIOS / "nominal.json"), tmp_path / "e", silencieux=True).executer(700)
    cx = sqlite3.connect(tmp_path / "e" / "journal.sqlite")
    contenus = [json.loads(c) for (c,) in cx.execute("SELECT contenu FROM journal ORDER BY sequence")]
    cx.close()

    assert "duree_cycle_precedent_ms" not in contenus[0]
    durees = [c["duree_cycle_precedent_ms"] for c in contenus[1:]]
    assert len(durees) == 699 and all(d > 0 for d in durees)

    centile_99 = sorted(durees)[int(0.99 * len(durees)) - 1]
    print(f"\nCycles mesurés : {len(durees)} ; médiane {statistics.median(durees):.2f} ms ; "
          f"99e centile {centile_99:.2f} ms ; maximum {max(durees):.2f} ms ; "
          f"cycles d'au moins 100 ms : {sum(d >= 100 for d in durees)}")
    assert centile_99 < 1000, "EX-Q-01 : le cycle complet doit tenir dans T = 1 s"
