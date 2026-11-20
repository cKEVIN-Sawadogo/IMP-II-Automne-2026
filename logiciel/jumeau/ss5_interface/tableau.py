"""Interface web de SS-5 (Plotly Dash).

Trois pages :
  Conduite   vue permanente (état codé par la forme, la couleur et le libellé,
             confiance, heure d'entrée dans l'état), bandeau des trois
             variables, vue de détail en un geste, demande de confirmation,
             historique des transitions ;
  Analyse    sorties de chaque sous-système, cycle par cycle : grandeurs
             vraies et mesures (SS-1, SS-2), valeurs attendues et résidus
             (SS-3), sommes cumulées (SS-4), état et confiance (SS-4, SS-5) ;
  Journal    intégrité de la chaîne SHA-256 (SS-6) et événements de l'essai.

L'interface lit les enregistrements de la session. Elle ne renvoie au jumeau
que la réponse de l'opérateur, par PresentationEtat.repondre().

Exécution, depuis le dossier logiciel :
    python lancer.py --interface
    python lancer.py scenarios/derive_lente.json --temps-reel
"""
from __future__ import annotations

import base64
import logging
import math
import threading
import time
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from plotly.subplots import make_subplots

from jumeau.contrat import PLAGES, UNITES, Variable
from jumeau.ss3_reference import N_CALAGE
from jumeau.ss4_decision import SEUIL_H, SEUIL_INSTANT
from jumeau.ss5_interface import LIBELLES, NOMS
from jumeau.ss5_interface.session import (ARRETE, EN_COURS, ERREUR, PAUSE, PRET, TERMINE, VITESSES,
                                          Session, scenarios_disponibles)

DOSSIER = Path(__file__).resolve().parent

# ----- Codage des états -------------------------------------------------------
# Chaque état a sa forme, son motif de remplissage et son libellé : les quatre
# restent distincts en noir et blanc. La couleur ne fait que doubler.

COULEURS = {"normal": "#3b6e4d", "derive": "#6b4c9a", "anomalie": "#b3261e", "incertain": "#3a5f8f"}
ORDRE_ETATS = ("normal", "derive", "anomalie", "incertain")
DESCRIPTIONS = {
    "normal": "Écarts entre mesure et attendu dans les limites",
    "derive": "Écart persistant détecté par la somme cumulée",
    "anomalie": "Écart brusque au-delà du seuil instantané",
    "incertain": "Données insuffisantes pour conclure",
}
FORMES = {"normal": "cercle", "derive": "triangle", "anomalie": "octogone", "incertain": "carré pointillé"}

INTITULES_VARIABLES = {"T": "Température sortie V1", "P": "Pression absolue", "Q": "Débit massique"}
FORMATS = {"T": (2, 3), "P": (4, 5), "Q": (4, 5)}  # décimales : valeur, écart
COULEURS_VARIABLES = {"T": "#8a3b12", "P": "#1f4e79", "Q": "#3d6b2f"}

MODULES = {
    "ss1": ("SS-1", "Simulateur de la boucle", "Modèle 0D à cinq volumes"),
    "ss2": ("SS-2", "Acquisition des mesures", "Bruit, biais, défauts injectés"),
    "ss3": ("SS-3", "Référence", "Valeurs attendues et résidus"),
    "ss4": ("SS-4", "Décision séquentielle", "Somme cumulée, seuil instantané"),
    "ss5": ("SS-5", "Présentation par état", "Affichage opérateur"),
    "ss6": ("SS-6", "Journal de données", "SQLite, chaînage SHA-256"),
}

NOMS_DEFAUTS = {"derive": "dérive", "saut": "saut", "perte_communication": "perte de communication",
                "hors_plage": "hors plage"}

LIBELLES_STATUT = {PRET: "EN ATTENTE", EN_COURS: "EN COURS", PAUSE: "EN PAUSE", TERMINE: "TERMINÉ",
                   ARRETE: "ARRÊTÉ", ERREUR: "ERREUR"}


def _svg_etat(etat: str, taille: int = 88) -> str:
    c = COULEURS.get(etat, "#555")
    if etat == "normal":
        corps = f'<circle cx="50" cy="50" r="38" fill="none" stroke="{c}" stroke-width="9"/>'
    elif etat == "derive":
        corps = (f'<defs><pattern id="h" width="9" height="9" patternUnits="userSpaceOnUse" '
                 f'patternTransform="rotate(45)"><rect width="4" height="9" fill="{c}"/></pattern></defs>'
                 f'<polygon points="50,8 94,88 6,88" fill="url(#h)" stroke="{c}" stroke-width="7" '
                 f'stroke-linejoin="round"/>')
    elif etat == "anomalie":
        corps = (f'<polygon points="32,6 68,6 94,32 94,68 68,94 32,94 6,68 6,32" fill="{c}"/>'
                 f'<rect x="44" y="22" width="12" height="36" fill="#fff"/>'
                 f'<rect x="44" y="66" width="12" height="12" fill="#fff"/>')
    else:
        corps = (f'<rect x="9" y="9" width="82" height="82" fill="none" stroke="{c}" stroke-width="7" '
                 f'stroke-dasharray="14 9"/>'
                 f'<text x="50" y="67" text-anchor="middle" font-family="Arial" font-weight="700" '
                 f'font-size="48" fill="{c}">?</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{taille}" height="{taille}" '
           f'viewBox="0 0 100 100">{corps}</svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


SYMBOLES_SVG = {e: _svg_etat(e) for e in ORDRE_ETATS}
SYMBOLES_SVG_PETITS = {e: _svg_etat(e, 22) for e in ORDRE_ETATS}

# ----- Mise en forme ----------------------------------------------------------


# Heure de l'Est du Canada (Québec). Le journal reste horodaté en UTC ;
# seul l'affichage est converti. Sans base de fuseaux, l'heure du poste.
try:
    FUSEAU = ZoneInfo("America/Toronto")
except ZoneInfoNotFoundError:
    FUSEAU = None


def _locale(dt: datetime) -> datetime:
    return dt.astimezone(FUSEAU) if FUSEAU else dt.astimezone()


def _sigle(dt: datetime | None = None) -> str:
    """HNE (heure normale de l'Est) ou HAE (heure avancée de l'Est)."""
    dt = _locale(dt or datetime.now(timezone.utc))
    if FUSEAU is None:
        return "heure locale"
    return "HAE" if dt.dst() else "HNE"


def _heure(iso: str | None) -> str:
    if not iso:
        return "n.d."
    try:
        return _locale(datetime.fromisoformat(iso.replace("Z", "+00:00"))).strftime("%H:%M:%S")
    except ValueError:
        return iso


def _duree(secondes: float) -> str:
    secondes = int(max(0, secondes))
    return f"{secondes // 3600:02d}:{secondes % 3600 // 60:02d}:{secondes % 60:02d}"


def _nombre(x: float | None, decimales: int, signe: bool = False) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n.d."
    return f"{x:{'+' if signe else ''}.{decimales}f}"


def _entier(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def _noms_variables(codes) -> str:
    return ", ".join(NOMS[Variable(c)] for c in codes) if codes else "aucune"


def _decrire_evenement(ev: dict) -> tuple[str, str]:
    """(catégorie, texte) d'un événement du journal."""
    t = ev.get("type")
    var = ev.get("variable")
    nom_var = NOMS[Variable(var)] if var in ("T", "P", "Q") else ("toutes les variables" if var == "toutes" else var)
    if t == "consignes":
        return "Consignes", (f"Vitesse de pompe {ev.get('vitesse_pompe')}, "
                             f"puissance de chauffe {ev.get('puissance_W'):g} W")
    if t == "defaut_injecte" or (t in ("derive", "saut", "perte_communication", "hors_plage") and "debut_s" in ev):
        genre = ev.get("type") if t != "defaut_injecte" else ev.get("genre", "défaut")
        details = {
            "derive": f"dérive de {ev.get('pente_sigma_par_cycle')} σ par cycle",
            "saut": f"saut de {ev.get('amplitude_sigma')} σ",
            "perte_communication": f"perte de communication pendant {ev.get('duree_s')} s",
            "hors_plage": f"valeur hors étendue pendant {ev.get('duree_s')} s",
        }.get(genre, genre)
        return "Défaut injecté", f"{details.capitalize()} sur {nom_var}"
    if t == "defaut_refuse":
        return "Scénario", f"Défaut n° {ev.get('index_defaut')} refusé ({ev.get('motif')})"
    if t == "mesure_rejetee":
        return "Mesure", f"Mesure de {nom_var} rejetée : {str(ev.get('motif', '')).replace('_', ' ')}"
    if t == "calage_termine":
        return "Référence", f"Calage terminé sur {ev.get('cycles')} cycles, référence prête"
    if t == "reference_hors_domaine":
        return "Référence", "Consignes hors du domaine de la référence"
    if t == "changement_etat":
        de = LIBELLES_TXT.get(ev.get("de"), "Démarrage")
        return "État", f"{de} → {LIBELLES_TXT.get(ev['vers'])} (variables : {_noms_variables(ev.get('variables'))})"
    if t == "demande_confirmation":
        return "Opérateur", (f"Demande de confirmation : état {LIBELLES_TXT.get(ev.get('etat'))}, "
                             f"confiance {ev.get('confiance', 0):.0%}")
    if t == "demande_confirmation_retiree":
        return "Opérateur", f"Demande retirée ({str(ev.get('motif', '')).replace('_', ' ')})"
    if t == "reponse_operateur":
        verbe = "confirmé" if ev.get("reponse") == "confirme" else "refusé"
        return "Opérateur", f"Fonctionnement dégradé {verbe} par l'opérateur"
    if t == "etat_critique":
        return "Opérateur", f"Sévérité critique, aucune demande ({_noms_variables(ev.get('variables'))})"
    if t == "defaut_composant":
        return "Composant", f"Défaut de {ev.get('module')} : {ev.get('message')}"
    return "Autre", ", ".join(f"{c} = {v}" for c, v in ev.items() if c not in ("cycle", "horodatage_utc"))


LIBELLES_TXT = {e.value: LIBELLES[e] for e in LIBELLES}

# ----- Graphiques -------------------------------------------------------------

POLICE = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
CONFIG_GRAPHE = {"displaylogo": False, "responsive": True,
                 "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d", "toggleSpikelines"]}


def _mise_en_page(fig: go.Figure, hauteur: int, revision) -> go.Figure:
    fig.update_layout(
        template="none", height=hauteur, uirevision=revision,
        margin=dict(l=70, r=20, t=46, b=40),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font=dict(family=POLICE, size=12, color="#2a3036"),
        legend=dict(orientation="h", x=1, xanchor="right", y=1.0, yanchor="bottom", font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified", hoverlabel=dict(font_family=POLICE, bgcolor="#ffffff"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e6e8ea", linecolor="#9aa2a9", ticks="outside",
                     tickcolor="#9aa2a9", zeroline=False, showline=True, mirror=False)
    fig.update_yaxes(showgrid=True, gridcolor="#e6e8ea", linecolor="#9aa2a9", ticks="outside",
                     tickcolor="#9aa2a9", zeroline=False, showline=True)
    return fig


def _axe_temps(fig: go.Figure, inst: dict) -> None:
    """Axe du temps sur toute la durée prévue : on voit l'essai avancer."""
    fin = max(inst.get("cycles_prevus") or 0, (inst["k"][-1] + 1) if inst["k"] else 1)
    fig.update_xaxes(range=[0, fin])


def _pas(n: int, maximum: int = 2500) -> int:
    return max(1, math.ceil(n / maximum))


def _reperes(fig: go.Figure, inst: dict, lignes) -> None:
    """Fin du calage et débuts de défaut, sur toutes les lignes de la figure."""
    k_calage = next((e["cycle"] for e in inst["evenements"] if e.get("type") == "calage_termine"), None)
    for ligne in lignes:
        if k_calage is not None:
            fig.add_vrect(x0=0, x1=k_calage, fillcolor="#8f979e", opacity=0.08, line_width=0,
                          row=ligne, col=1)
    if k_calage is not None:
        fig.add_vline(x=k_calage, line=dict(color="#6c757d", width=1, dash="dot"), row="all", col=1)
        fig.add_annotation(x=k_calage, y=0.995, yref="paper", text=" Fin du calage", showarrow=False,
                           xanchor="left", yanchor="top", bgcolor="rgba(255,255,255,0.85)",
                           font=dict(size=10, color="#5a636b"))
    for d in (inst.get("scenario") or {}).get("defauts", []):
        x = d.get("debut_s")
        if x is None or x > (inst["k"][-1] if inst["k"] else 0):
            continue
        fig.add_vline(x=x, line=dict(color="#b3261e", width=1.2, dash="dash"), row="all", col=1)
        fig.add_annotation(x=x, y=0.995, yref="paper", showarrow=False, xanchor="left", yanchor="top",
                           bgcolor="rgba(255,255,255,0.85)",
                           text=f" Défaut injecté ({NOMS_DEFAUTS[d['type']]}, {d['variable']})",
                           font=dict(size=10, color="#b3261e"))


def figure_grandeurs(inst: dict) -> go.Figure:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=[f"{INTITULES_VARIABLES[v]} ({UNITES[Variable(v)]})" for v in "TPQ"])
    p = _pas(inst["n"])
    k = inst["k"][::p]
    for i, v in enumerate("TPQ", start=1):
        legende = i == 1
        fig.add_trace(go.Scatter(x=k, y=inst["vraie"][v][::p], name="Grandeur vraie (SS-1, banc d'essai)",
                                 line=dict(color="#9aa2a9", width=1.2), legendgroup="vraie",
                                 showlegend=legende), row=i, col=1)
        fig.add_trace(go.Scatter(x=k, y=inst["mesure"][v][::p], name="Mesure (SS-2)",
                                 line=dict(color=COULEURS_VARIABLES[v], width=1), legendgroup="mesure",
                                 showlegend=legende, connectgaps=False), row=i, col=1)
        fig.add_trace(go.Scatter(x=k, y=inst["attendu"][v][::p], name="Valeur attendue (SS-3)",
                                 line=dict(color="#1b1f23", width=1.6, dash="dash"), legendgroup="attendu",
                                 showlegend=legende), row=i, col=1)
        # Mesures non valides : repérées sous la courbe, jamais codées par zéro.
        rejet = [(kk, s) for kk, s in zip(inst["k"], inst["statut_mesure"][v]) if s != "valide"]
        if rejet:
            valeurs = [x for x in inst["mesure"][v] if x is not None]
            y0 = min(valeurs) if valeurs else 0
            fig.add_trace(go.Scatter(x=[r[0] for r in rejet], y=[y0] * len(rejet), mode="markers",
                                     name="Mesure non valide", legendgroup="rejet", showlegend=True,
                                     marker=dict(symbol="x-thin", size=7, line=dict(width=1.5, color="#b3261e")),
                                     text=[r[1].replace("_", " ") for r in rejet],
                                     hovertemplate="%{text}<extra></extra>"), row=i, col=1)
    _reperes(fig, inst, (1, 2, 3))
    fig.update_xaxes(title_text="Temps simulé (s)", row=3, col=1)
    _axe_temps(fig, inst)
    for a in fig.layout.annotations[:3]:
        a.update(x=0, xanchor="left", font=dict(size=12, color="#2a3036"))
    return _mise_en_page(fig, 640, inst["numero"])


def figure_residus(inst: dict) -> go.Figure:
    fig = make_subplots(rows=1, cols=1)
    p = _pas(inst["n"])
    for v in "TPQ":
        fig.add_trace(go.Scatter(x=inst["k"][::p], y=inst["residu"][v][::p], name=f"Résidu {v}",
                                 line=dict(color=COULEURS_VARIABLES[v], width=1)))
    for s in (SEUIL_INSTANT, -SEUIL_INSTANT):
        fig.add_hline(y=s, line=dict(color="#b3261e", width=1, dash="dash"))
    fig.add_annotation(x=1, xref="paper", y=SEUIL_INSTANT, text=f"Seuil instantané ± {SEUIL_INSTANT:g} σ",
                       showarrow=False, xanchor="right", yanchor="bottom", font=dict(size=10, color="#b3261e"))
    _reperes(fig, inst, (1,))
    fig.update_yaxes(title_text="Résidu normalisé (σ)")
    fig.update_xaxes(title_text="Temps simulé (s)")
    _axe_temps(fig, inst)
    return _mise_en_page(fig, 320, inst["numero"])


def figure_sommes(inst: dict) -> go.Figure:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                        subplot_titles=[f"{INTITULES_VARIABLES[v]}" for v in "TPQ"])
    p = _pas(inst["n"])
    for i, v in enumerate("TPQ", start=1):
        fig.add_trace(go.Scatter(x=inst["k"][::p], y=inst["somme_haut"][v][::p], name="S⁺ (écart positif)",
                                 line=dict(color="#1b1f23", width=1.3), legendgroup="haut",
                                 showlegend=i == 1), row=i, col=1)
        fig.add_trace(go.Scatter(x=inst["k"][::p], y=inst["somme_bas"][v][::p], name="S⁻ (écart négatif)",
                                 line=dict(color="#7d868e", width=1.3, dash="dot"), legendgroup="bas",
                                 showlegend=i == 1), row=i, col=1)
        # Après l'alarme, la somme continue de croître : l'axe est borné pour que
        # le franchissement du seuil reste lisible.
        fig.update_yaxes(range=[-0.5, 2.5 * SEUIL_H], row=i, col=1)
        fig.add_hline(y=SEUIL_H, line=dict(color="#1b1f23", width=1.2, dash="dash"), row=i, col=1)
    fig.add_annotation(x=1, xref="paper", y=SEUIL_H, yref="y", text=f"Seuil h = {SEUIL_H:g}", showarrow=False,
                       xanchor="right", yanchor="bottom", font=dict(size=10, color="#1b1f23"))
    _reperes(fig, inst, (1, 2, 3))
    fig.update_xaxes(title_text="Temps simulé (s)", row=3, col=1)
    _axe_temps(fig, inst)
    for a in fig.layout.annotations[:3]:
        a.update(x=0, xanchor="left", font=dict(size=12, color="#2a3036"))
    return _mise_en_page(fig, 520, inst["numero"])


def figure_chronologie(inst: dict, hauteur: int = 230, confiance: bool = True) -> go.Figure:
    lignes = 2 if confiance else 1
    fig = make_subplots(rows=lignes, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                        row_heights=[0.55, 0.45] if confiance else [1.0])
    k_fin = inst["k"][-1] + 1 if inst["k"] else 1
    segments = []
    for i, tr in enumerate(inst["transitions"]):
        fin = inst["transitions"][i + 1]["k"] if i + 1 < len(inst["transitions"]) else k_fin
        segments.append((tr["k"], fin, tr["vers"]))
    motifs = {"normal": "", "derive": "/", "anomalie": "", "incertain": "."}
    for e in ORDRE_ETATS:
        segs = [s for s in segments if s[2] == e]
        fig.add_trace(go.Bar(
            x=[s[1] - s[0] for s in segs] or [0], base=[s[0] for s in segs] or [0], y=["État"] * max(1, len(segs)),
            orientation="h", name=LIBELLES_TXT[e], showlegend=bool(segs),
            marker=dict(color=COULEURS[e] if e != "normal" else "#dfe7e1", line=dict(color=COULEURS[e], width=1),
                        pattern=dict(shape=motifs[e], fillmode="overlay", fgcolor="#ffffff",
                                     size=8, solidity=0.3)),
            hovertemplate=f"{LIBELLES_TXT[e]}<br>début %{{base}} s, durée %{{x}} s<extra></extra>",
        ), row=1, col=1)
    fig.update_layout(barmode="overlay", bargap=0.25)
    if confiance:
        p = _pas(inst["n"])
        fig.add_trace(go.Scatter(x=inst["k"][::p], y=[c * 100 for c in inst["confiance"][::p]],
                                 name="Confiance (%)", line=dict(color="#1b1f23", width=1.2),
                                 showlegend=False), row=2, col=1)
        fig.update_yaxes(range=[-5, 105], title_text="Confiance (%)", row=2, col=1)
    fig.update_xaxes(range=[0, max(k_fin, inst.get("cycles_prevus") or 0)])
    fig.update_xaxes(title_text="Temps simulé (s)", row=lignes, col=1)
    fig.update_yaxes(showgrid=False, row=1, col=1)
    fig = _mise_en_page(fig, hauteur, inst["numero"])
    fig.update_layout(hovermode="closest", margin=dict(l=70, r=20, t=30, b=38))
    return fig


def figure_tendance(inst: dict, v: str, designee: bool) -> go.Figure:
    """Écart entre mesure et attendu sur les derniers cycles, pour une tuile de détail."""
    ecarts = [(k, m - a) for k, m, a in zip(inst["k"], inst["mesure"][v], inst["attendu"][v])
              if m is not None and a is not None]
    fig = go.Figure(go.Scatter(x=[e[0] for e in ecarts], y=[e[1] for e in ecarts], mode="lines",
                               line=dict(color="#1b1f23" if designee else "#5f6870", width=1.2),
                               hovertemplate="t = %{x} s<br>écart %{y:.4g}<extra></extra>"))
    fig.add_hline(y=0, line=dict(color="#9aa2a9", width=1))
    fig.update_layout(template="none", height=110, margin=dict(l=46, r=8, t=6, b=22),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=POLICE, size=10, color="#4a535b"), showlegend=False,
                      uirevision=inst["numero"])
    fig.update_xaxes(showgrid=False, ticks="outside", tickcolor="#9aa2a9", nticks=4)
    fig.update_yaxes(showgrid=True, gridcolor="#e6e8ea", nticks=3, tickformat=".2g")
    return fig


# ----- Mise en page -----------------------------------------------------------


def _panneau(titre: str, *enfants, id_=None, classe: str = "", outils=None) -> html.Section:
    tete = [html.H2(titre)]
    if outils is not None:
        tete.append(html.Div(outils, className="outils"))
    attrs = {"id": id_} if id_ else {}
    return html.Section([html.Header(tete, className="panneau-tete"), *enfants],
                        className=f"panneau {classe}".strip(), **attrs)


def _page_conduite() -> html.Div:
    bandeau = html.Div(
        [html.Div(id=f"bandeau-{v}", className="cellule-variable", n_clicks=0) for v in "TPQ"]
        + [html.Button("Vue de détail", id="bouton-detail", className="bouton-detail", n_clicks=0)],
        className="bandeau", id="bandeau")
    tuiles = html.Div([
        html.Div([html.Div(id=f"tuile-{v}-texte"),
                  dcc.Graph(id=f"tuile-{v}-graphe", config={"displayModeBar": False},
                            className="tuile-graphe", style={"height": "110px"})],
                 id=f"tuile-{v}", className="tuile") for v in "TPQ"], className="tuiles")
    return html.Div([
        html.Div([
            _panneau("Vue permanente", html.Div(id="vue-permanente"), classe="panneau-etat"),
            _panneau("Demande de confirmation", html.Div(id="confirmation-texte"),
                     html.Div([html.Button("Confirmer", id="bouton-confirmer", className="bouton bouton-principal",
                                           n_clicks=0, disabled=True),
                               html.Button("Refuser", id="bouton-refuser", className="bouton", n_clicks=0,
                                           disabled=True)], className="confirmation-boutons"),
                     html.Div(id="confirmation-message", className="message"),
                     classe="panneau-confirmation"),
        ], className="rangee rangee-haut"),
        _panneau("Variables surveillées", bandeau, classe="panneau-bandeau"),
        html.Div(_panneau("Vue de détail", tuiles,
                          outils=html.Span("Variables désignées par SS-4 encadrées", className="aide")),
                 id="zone-detail", className="zone-detail ferme"),
        html.Div([
            _panneau("Chronologie des états",
                     dcc.Graph(id="graphe-chronologie", config=CONFIG_GRAPHE | {"displayModeBar": False},
                               style={"height": "200px"}),
                     classe="panneau-large"),
            _panneau("Historique des transitions", html.Div(id="historique", className="table-defilante"),
                     classe="panneau-historique"),
        ], className="rangee rangee-bas"),
    ], id="page-conduite", className="page")


def _bloc_chaine() -> html.Div:
    """Chaîne SS-1 à SS-6, visible quel que soit l'onglet."""
    chaine = html.Div([html.Div(id=f"module-{c}", className="module") for c in MODULES],
                      className="chaine", id="chaine-modules")
    return html.Div(_panneau("Chaîne de traitement, cycle courant", chaine, classe="panneau-chaine"),
                    className="zone-chaine")


def _page_analyse() -> html.Div:
    return html.Div([
        _panneau("SS-1 et SS-2 : grandeurs vraies, mesures et valeurs attendues",
                 dcc.Graph(id="graphe-grandeurs", config=CONFIG_GRAPHE, style={"height": "640px"})),
        html.Div([
            _panneau("SS-3 : résidus normalisés", dcc.Graph(id="graphe-residus", config=CONFIG_GRAPHE, style={"height": "320px"}),
                     classe="panneau-moitie"),
            _panneau("SS-4 et SS-5 : état présenté et confiance",
                     dcc.Graph(id="graphe-etats", config=CONFIG_GRAPHE, style={"height": "320px"}), classe="panneau-moitie"),
        ], className="rangee"),
        _panneau("SS-4 : sommes cumulées bilatérales", dcc.Graph(id="graphe-sommes", config=CONFIG_GRAPHE, style={"height": "520px"})),
    ], id="page-analyse", className="page cachee")


def _page_journal() -> html.Div:
    return html.Div([
        html.Div([
            _panneau("Intégrité du journal (SS-6)", html.Div(id="journal-integrite"),
                     html.Button("Vérifier la chaîne SHA-256", id="bouton-verifier", className="bouton",
                                 n_clicks=0),
                     html.Div(id="journal-verification", className="message"), classe="panneau-integrite"),
            _panneau("Synthèse de l'essai", html.Div(id="journal-synthese"), classe="panneau-synthese"),
        ], className="rangee"),
        _panneau("Événements de l'essai", html.Div(id="journal-evenements", className="table-defilante haute"),
                 outils=dcc.Dropdown(id="filtre-evenements", multi=True, placeholder="Toutes les catégories",
                                     options=[{"label": c, "value": c} for c in
                                              ("État", "Opérateur", "Défaut injecté", "Mesure", "Référence",
                                               "Consignes", "Composant", "Scénario", "Autre")],
                                     className="filtre")),
    ], id="page-journal", className="page cachee")


def _barre_essai(scenarios: list[dict], scenario_initial: str | None, vitesse_initiale: str) -> html.Div:
    options = [{"label": f"{s['nom']}  ({s['fichier']}, {_entier(s['cycles'])} cycles)", "value": s["chemin"]}
               for s in scenarios]
    valeur = scenario_initial or (options[0]["value"] if options else None)
    return html.Div([
        html.Div([html.Label("Scénario", htmlFor="choix-scenario"),
                  dcc.Dropdown(id="choix-scenario", options=options, value=valeur, clearable=False,
                               searchable=False, className="choix-scenario")], className="champ champ-large"),
        html.Div([html.Label("Cadence"),
                  dcc.RadioItems(id="choix-vitesse", value=vitesse_initiale, inline=True,
                                 className="segments", inputClassName="segment-entree",
                                 labelClassName="segment",
                                 options=[{"label": "Temps réel", "value": "1"}, {"label": "× 10", "value": "10"},
                                          {"label": "× 60", "value": "60"}, {"label": "Max", "value": "max"}])],
                 className="champ"),
        html.Div([html.Label("Mode"),
                  dcc.Checklist(id="choix-tolerant", options=[{"label": "Tolérant aux pannes", "value": "oui"}],
                                value=[], className="case", inputClassName="case-entree")], className="champ"),
        html.Div([html.Button("Lancer l'essai", id="bouton-lancer", className="bouton bouton-principal", n_clicks=0),
                  html.Button("Pause", id="bouton-pause", className="bouton", n_clicks=0, disabled=True),
                  html.Button("Arrêter", id="bouton-arreter", className="bouton", n_clicks=0, disabled=True)],
                 className="commandes"),
        html.Div(id="description-scenario", className="description-scenario"),
    ], className="barre-essai")


def creer_application(session: Session, *, scenario_initial: str | None = None,
                      vitesse_initiale: str = "1") -> Dash:
    app = Dash(__name__, title="Surveillance de la boucle, jumeau numérique", update_title=None,
               assets_folder=str(DOSSIER / "assets"))
    scenarios = scenarios_disponibles()
    descriptions = {s["chemin"]: s["description"] for s in scenarios}
    if scenario_initial:
        scenario_initial = str(Path(scenario_initial).resolve())
        if scenario_initial not in descriptions:
            scenarios.append({"chemin": scenario_initial, "fichier": Path(scenario_initial).name,
                              "nom": Path(scenario_initial).stem, "description": "", "cycles": 0})

    def disposition():
        return html.Div([
        dcc.Interval(id="horloge", interval=1000),
        # Version de ce que chaque zone affiche, gardée dans le navigateur : une
        # zone n'est redessinée que si sa version change ou si on l'ouvre.
        dcc.Store(id="version-conduite"), dcc.Store(id="version-analyse"), dcc.Store(id="version-journal"),
        html.Header([
            html.Div([html.Div("Boucle thermohydraulique", className="site"),
                      html.H1("Surveillance par jumeau numérique")], className="titre"),
            html.Div(id="entete-essai", className="entete-essai"),
            html.Div([html.Div(id="entete-temps", className="entete-temps"),
                      html.Button("Noir et blanc", id="bouton-nb", className="bouton bouton-discret", n_clicks=0)],
                     className="entete-droite"),
        ], className="entete"),
        _barre_essai(scenarios, scenario_initial, vitesse_initiale),
        html.Div(id="message-essai", className="message-essai"),
        _bloc_chaine(),
        dcc.Tabs(id="onglets", value="conduite", className="onglets", parent_className="onglets-parent",
                 children=[dcc.Tab(label=l, value=v, className="onglet", selected_className="onglet-actif")
                           for v, l in (("conduite", "Conduite"), ("analyse", "Analyse des sous-systèmes"),
                                        ("journal", "Journal"))]),
        html.Main([_page_conduite(), _page_analyse(), _page_journal()]),
        html.Footer("SS-5, présentation par état. Affichage seul, aucune commande vers l'installation (EX-F-08).",
                    className="pied"),
    ], id="racine", className="hmi")

    app.layout = disposition
    _callbacks(app, session, descriptions)
    return app


# ----- Comportement -----------------------------------------------------------


def _callbacks(app: Dash, session: Session, descriptions: dict) -> None:
    @app.callback(Output("description-scenario", "children"), Input("choix-scenario", "value"))
    def _description(chemin):
        return descriptions.get(chemin, "")

    @app.callback(Output("message-essai", "children"),
                  Input("bouton-lancer", "n_clicks"), Input("bouton-pause", "n_clicks"),
                  Input("bouton-arreter", "n_clicks"), Input("choix-vitesse", "value"),
                  State("choix-scenario", "value"), State("choix-tolerant", "value"),
                  prevent_initial_call=True)
    def _commandes(_l, _p, _a, vitesse, chemin, tolerant):
        declencheurs = {p.split(".")[0] for p in ctx.triggered_prop_ids}
        # Si la cadence et le lancement arrivent ensemble, le lancement l'emporte
        # (il applique la cadence choisie).
        declencheur = "bouton-lancer" if "bouton-lancer" in declencheurs else ctx.triggered_id
        if declencheur == "choix-vitesse":
            session.regler_vitesse(VITESSES[vitesse])
            return ""
        if declencheur == "bouton-lancer":
            if not chemin:
                return "Choisir un scénario."
            try:
                session.lancer(chemin, vitesse=VITESSES[vitesse], tolerant=bool(tolerant))
            except (ValueError, OSError) as erreur:
                return f"Scénario refusé : {erreur}"
            return ""
        if declencheur == "bouton-pause":
            if session.statut == PAUSE:
                session.reprendre()
            else:
                session.mettre_en_pause()
            return ""
        if declencheur == "bouton-arreter":
            session.arreter()
            return "Arrêt demandé : le cycle en cours est journalisé, puis l'essai s'arrête."
        return no_update

    @app.callback(Output("racine", "className"), Input("bouton-nb", "n_clicks"))
    def _noir_et_blanc(n):
        return "hmi nb" if n and n % 2 else "hmi"

    @app.callback(Output("bouton-nb", "children"), Input("bouton-nb", "n_clicks"))
    def _libelle_nb(n):
        return "Couleur" if n and n % 2 else "Noir et blanc"

    @app.callback(Output("page-conduite", "className"), Output("page-analyse", "className"),
                  Output("page-journal", "className"), Input("onglets", "value"))
    def _pages(onglet):
        return tuple("page" if onglet == p else "page cachee" for p in ("conduite", "analyse", "journal"))

    @app.callback(Output("zone-detail", "className"), Output("bouton-detail", "children"),
                  Input("bouton-detail", "n_clicks"), Input("bandeau-T", "n_clicks"),
                  Input("bandeau-P", "n_clicks"), Input("bandeau-Q", "n_clicks"),
                  State("zone-detail", "className"), prevent_initial_call=True)
    def _detail(_b, _t, _p, _q, classe):
        ouvert = "ferme" in (classe or "")
        return ("zone-detail" if ouvert else "zone-detail ferme",
                "Masquer le détail" if ouvert else "Vue de détail")

    # --- En-tête et barre d'essai ---

    @app.callback(Output("entete-essai", "children"), Output("entete-temps", "children"),
                  Output("bouton-pause", "children"), Output("bouton-pause", "disabled"),
                  Output("bouton-arreter", "disabled"), Input("horloge", "n_intervals"))
    def _entete(_n):
        st = session.statut
        sc = session.scenario
        n = len(session.k)
        k = session.k[-1] if n else 0
        prevus = session.cycles_prevus or 0
        if sc:
            cadence = "max" if session.vitesse is None else f"× {session.vitesse:g}"
            essai = [
                html.Span(LIBELLES_STATUT[st], className=f"pastille statut-{st}"),
                html.Div([html.Div(sc["nom"], className="essai-nom"),
                          html.Div(f"Graine {sc['graine']}, version {sc.get('version', 'n.d.')}, cadence {cadence}",
                                   className="essai-meta")]),
                html.Div([html.Div(className="progression-barre",
                                   style={"width": f"{min(100, 100 * n / prevus) if prevus else 0:.1f}%"})],
                         className="progression", title=f"{_entier(n)} / {_entier(prevus)} cycles"),
            ]
            if session.erreur:
                essai.append(html.Span(session.erreur, className="erreur"))
        else:
            essai = [html.Span(LIBELLES_STATUT[PRET], className="pastille statut-pret"),
                     html.Div("Aucun essai lancé", className="essai-nom")]
        maintenant = _locale(datetime.now(timezone.utc))
        temps = [
            html.Div([html.Span("Temps simulé", className="etiquette"),
                      html.Span(f"t = {_entier(k)} s", className="chiffre")]),
            html.Div([html.Span("Cycle", className="etiquette"),
                      html.Span(f"{_entier(n)} / {_entier(prevus)}", className="chiffre")]),
            html.Div([html.Span(f"Heure ({_sigle()})", className="etiquette"),
                      html.Span(maintenant.strftime("%H:%M:%S"), className="chiffre")]),
        ]
        actif = session.actif
        return essai, temps, ("Reprendre" if st == PAUSE else "Pause"), not actif, not actif

    # --- Versions ---
    # Une seule fonction rapide, appelée chaque seconde, décide ce qui a changé.
    # Les zones se redessinent sur changement de version ou d'onglet, jamais
    # sur l'horloge directement : un rendu lourd n'est donc jamais remplacé par
    # une réponse vide arrivée après lui.

    @app.callback(Output("version-conduite", "data"), Output("version-analyse", "data"),
                  Output("version-journal", "data"), Input("horloge", "n_intervals"),
                  State("version-conduite", "data"), State("version-analyse", "data"),
                  State("version-journal", "data"))
    def _versions(_n, v_conduite, v_analyse, v_journal):
        numero, n, statut = session.numero, len(session.k), session.statut
        conduite = [numero, n, statut, bool((session.ss5 or {}).get("demande"))]
        # Graphes d'analyse : au plus toutes les 2 s pendant l'essai, pour rester fluide.
        analyse = [numero, statut, int(time.time() // 2) if statut == EN_COURS else n]
        journal = [numero, statut, len(session.evenements), n // 10]
        return tuple(nouvelle if nouvelle != ancienne else no_update
                     for nouvelle, ancienne in ((conduite, v_conduite), (analyse, v_analyse),
                                                (journal, v_journal)))

    # --- Chaîne de traitement, toujours visible ---

    @app.callback(*[Output(f"module-{c}", "children") for c in MODULES],
                  *[Output(f"module-{c}", "className") for c in MODULES],
                  Input("version-conduite", "data"))
    def _chaine(_v):
        modules, classes = _rendre_modules(session.instantane(complet=False, fenetre=1))
        return [*modules, *classes]

    # --- Page de conduite ---

    sorties_conduite = (
        [Output("vue-permanente", "children"), Output("confirmation-texte", "children"),
         Output("bouton-confirmer", "disabled"), Output("bouton-refuser", "disabled"),
         Output("historique", "children"), Output("graphe-chronologie", "figure")]
        + [Output(f"bandeau-{v}", "children") for v in "TPQ"]
        + [Output(f"bandeau-{v}", "className") for v in "TPQ"]
        + [Output(f"tuile-{v}-texte", "children") for v in "TPQ"]
        + [Output(f"tuile-{v}", "className") for v in "TPQ"]
        + [Output(f"tuile-{v}-graphe", "figure") for v in "TPQ"]
    )

    @app.callback(*sorties_conduite, Input("version-conduite", "data"), Input("onglets", "value"),
                  Input("zone-detail", "className"))
    def _conduite(_v, onglet, classe_detail):
        if onglet != "conduite":
            return [no_update] * len(sorties_conduite)
        inst = session.instantane(complet=False, fenetre=300)
        chrono = session.instantane(complet=True) if inst["n"] else inst
        return _rendre_conduite(inst, chrono, detail_ouvert="ferme" not in (classe_detail or ""))

    @app.callback(Output("confirmation-message", "children"),
                  Input("bouton-confirmer", "n_clicks"), Input("bouton-refuser", "n_clicks"),
                  prevent_initial_call=True)
    def _reponse(_c, _r):
        reponse = "confirme" if ctx.triggered_id == "bouton-confirmer" else "refuse"
        return session.repondre(reponse)

    # --- Page d'analyse ---

    @app.callback(Output("graphe-grandeurs", "figure"), Output("graphe-residus", "figure"),
                  Output("graphe-sommes", "figure"), Output("graphe-etats", "figure"),
                  Input("version-analyse", "data"), Input("onglets", "value"))
    def _analyse(_v, onglet):
        if onglet != "analyse":
            return [no_update] * 4
        inst = session.instantane(complet=True)
        return [figure_grandeurs(inst), figure_residus(inst), figure_sommes(inst),
                figure_chronologie(inst, hauteur=320)]

    # --- Page du journal ---

    @app.callback(Output("journal-integrite", "children"), Output("journal-synthese", "children"),
                  Output("journal-evenements", "children"),
                  Input("version-journal", "data"), Input("onglets", "value"), Input("filtre-evenements", "value"))
    def _journal(_v, onglet, filtre):
        if onglet != "journal":
            return no_update, no_update, no_update
        return _rendre_journal(session.instantane(complet=False, fenetre=1), filtre)

    @app.callback(Output("journal-verification", "children"), Input("bouton-verifier", "n_clicks"),
                  prevent_initial_call=True)
    def _verifier(_n):
        try:
            resultat = session.verifier_journal()
        except Exception as erreur:  # base en cours d'écriture
            return html.Span(f"Vérification impossible pour l'instant : {erreur}", className="ko")
        if resultat is None:
            return "Aucun journal à vérifier."
        integre, fautive, n = resultat
        heure = f"{_locale(datetime.now(timezone.utc)):%H:%M:%S} {_sigle()}"
        if integre:
            return html.Span(f"Chaîne intègre : {_entier(n)} entrées recalculées, aucune rupture ({heure}).",
                             className="ok")
        return html.Span(f"Journal altéré : chaîne rompue à l'entrée {fautive} sur {_entier(n)} ({heure}).",
                         className="ko")


# ----- Rendu des pages --------------------------------------------------------


def _rendre_conduite(inst: dict, chrono: dict, detail_ouvert: bool) -> list:
    n = inst["n"]
    ss5 = inst["ss5"]
    if not n:
        vide = html.Div("Lancer un essai pour afficher l'état de la boucle.", className="vide")
        bandeau = [[html.Div(v, className="code"), html.Div(INTITULES_VARIABLES[v], className="nom"),
                    html.Div("n.d.", className="valeur")] for v in "TPQ"]
        return ([vide, html.Div("Aucune demande.", className="vide"), True, True,
                 html.Div("Aucune transition.", className="vide"), figure_chronologie(inst, confiance=False)]
                + bandeau + ["cellule-variable"] * 3 + [""] * 3 + ["tuile"] * 3
                + [figure_tendance(inst, v, False) for v in "TPQ"])

    etat = inst["etat"][-1]
    confiance = inst["confiance"][-1]
    contrib = inst["contributrices"][-1]
    k = inst["k"][-1]
    trans = inst["transitions"]
    entree = trans[-1] if trans else {"k": 0, "horodatage_utc": inst["horodatage"][0]}
    description = DESCRIPTIONS[etat]
    if etat == "incertain" and not inst["pret"][-1]:
        description = f"Calage de la référence en cours ({min(k + 1, N_CALAGE)} / {N_CALAGE} cycles)"

    vue = html.Div([
        html.Div(html.Img(src=SYMBOLES_SVG[etat], alt=f"{LIBELLES_TXT[etat]} ({FORMES[etat]})"),
                 className="symbole"),
        html.Div([
            html.Div(LIBELLES_TXT[etat], className="libelle-etat"),
            html.Div(description, className="description-etat"),
            html.Div([html.Div(className="jauge-remplie", style={"width": f"{confiance * 100:.0f}%"})],
                     className="jauge", title="Confiance"),
        ], className="etat-centre"),
        html.Dl([
            html.Dt("Confiance"), html.Dd(f"{confiance:.0%}", className="chiffre"),
            html.Dt("Entrée dans l'état"),
            html.Dd([html.Span(f"{_heure(entree['horodatage_utc'])} {_sigle()}", className="chiffre"),
                     html.Span(f"  t = {_entier(entree['k'])} s", className="secondaire")]),
            html.Dt("Durée dans l'état"), html.Dd(_duree(k - entree["k"] + 1), className="chiffre"),
            html.Dt("Variables en cause"), html.Dd(_noms_variables(contrib)),
        ], className="etat-details"),
    ], className=f"vue-permanente etat-{etat}")

    # Demande de confirmation (CU5)
    demande = ss5.get("demande")
    if demande:
        conf = html.Div([
            html.Div("Passage en fonctionnement dégradé ?", className="question"),
            html.Dl([html.Dt("État"), html.Dd(LIBELLES_TXT.get(demande["etat"])),
                     html.Dt("Confiance"), html.Dd(f"{demande['confiance']:.0%}"),
                     html.Dt("Variables"), html.Dd(_noms_variables(demande["variables"])),
                     html.Dt("Sévérité"), html.Dd("non critique"),
                     html.Dt("Demandée à"), html.Dd(f"t = {_entier(demande['k'])} s")], className="liste-courte"),
        ], className="demande active")
    else:
        dernieres = [e for e in inst["evenements"] if e.get("type") in
                     ("reponse_operateur", "etat_critique", "demande_confirmation_retiree")]
        conf = html.Div("Aucune demande en attente.", className="vide")

    # Historique des transitions
    lignes = []
    for i, tr in enumerate(reversed(trans)):
        lignes.append(html.Tr([
            html.Td(f"{_entier(tr['k'])} s", className="chiffre"),
            html.Td(_heure(tr["horodatage_utc"]), className="chiffre"),
            html.Td([html.Img(src=SYMBOLES_SVG_PETITS[tr["vers"]], alt=""),
                     html.Span(LIBELLES_TXT[tr["vers"]])], className="cellule-etat"),
            html.Td(LIBELLES_TXT.get(tr["de"], "Démarrage") if tr["de"] else "Démarrage"),
            html.Td(_noms_variables(tr["variables"])),
            html.Td(f"{tr['confiance']:.0%}", className="chiffre"),
        ], className="courant" if i == 0 else ""))
    historique = html.Table([html.Thead(html.Tr([html.Th(x) for x in
                                                 ("Temps", f"Heure ({_sigle()})", "Vers", "Depuis", "Variables", "Conf.")])),
                             html.Tbody(lignes)], className="table")

    # Bandeau des trois variables (EX-F-04)
    bandeau, classes_bandeau, tuiles, classes_tuiles, graphes = [], [], [], [], []
    for v in "TPQ":
        unite = UNITES[Variable(v)]
        dec, dec_e = FORMATS[v]
        statut = inst["statut_mesure"][v][-1]
        mesure = inst["mesure"][v][-1]
        attendu = inst["attendu"][v][-1]
        ecart = mesure - attendu if mesure is not None and attendu is not None else None
        designee = v in contrib
        derniere = ss5.get("derniere_valide", {}).get(v)
        etiquette = {"absent": "MESURE ABSENTE", "hors_plage": "HORS PLAGE"}.get(statut)
        bandeau.append([
            html.Div([html.Span(v, className="code"), html.Span(INTITULES_VARIABLES[v], className="nom"),
                      html.Span("DÉSIGNÉE", className="marque") if designee else None], className="tete"),
            html.Div([html.Span(_nombre(mesure, dec) if mesure is not None else "n.d.", className="valeur"),
                      html.Span(unite, className="unite")], className="ligne-valeur"),
            html.Div(etiquette, className="statut-mesure") if etiquette else
            html.Div([html.Span("Écart à l'attendu", className="etiquette"),
                      html.Span(f"{_nombre(ecart, dec_e, True)} {unite}" if ecart is not None else "référence en calage",
                                className="chiffre")], className="ligne"),
            html.Div([html.Span("Dernière acquisition valide", className="etiquette"),
                      html.Span(f"{_heure(derniere)} {_sigle()}", className="chiffre")], className="ligne"),
        ])
        classes_bandeau.append("cellule-variable" + (" designee" if designee else "")
                               + (" invalide" if etiquette else ""))

        residu = inst["residu"][v][-1]
        tuiles.append([
            html.Div([html.Span(v, className="code"), html.Span(INTITULES_VARIABLES[v], className="nom"),
                      html.Span("DÉSIGNÉE PAR SS-4", className="marque") if designee else None], className="tete"),
            html.Div(ss5.get("libelle", {}).get(v, ""), className="libelle-variable"),
            html.Dl([
                html.Dt("Mesure"), html.Dd(f"{_nombre(mesure, dec)} {unite}", className="chiffre"),
                html.Dt("Attendue"), html.Dd(f"{_nombre(attendu, dec)} {unite}", className="chiffre"),
                html.Dt("Écart"), html.Dd([f"{_nombre(ecart, dec_e, True)} {unite}",
                                           html.Span(f"  ({_nombre(residu, 2, True)} σ)", className="secondaire")
                                           if residu is not None else None], className="chiffre"),
                html.Dt("Tendance"), html.Dd(ss5.get("tendance", {}).get(v, "n.d.").replace("tendance de l'écart ", "")),
            ], className="liste-courte"),
            html.Div(f"Écart entre mesure et attendu, {min(n, 300)} derniers cycles", className="legende-graphe"),
        ])
        classes_tuiles.append("tuile" + (" designee" if designee else ""))
        graphes.append(figure_tendance(inst, v, designee) if detail_ouvert else no_update)

    actif = bool(demande) and inst["statut"] in (EN_COURS, PAUSE)
    return ([vue, conf, not actif, not actif, historique, figure_chronologie(chrono, confiance=False, hauteur=200)]
            + bandeau + classes_bandeau + tuiles + classes_tuiles + graphes)


def _residu_max(inst: dict) -> str:
    valeurs = [abs(inst["residu"][v][-1]) for v in "TPQ" if inst["residu"][v][-1] is not None]
    return f"{max(valeurs):.2f} σ" if valeurs else "en calage"


def _rendre_modules(inst: dict) -> tuple[list, list]:
    n = inst["n"]
    stats = inst["modules"]

    def dernier(liste):
        return liste[-1] if liste else None

    resumes = {}
    if n:
        vr = {v: dernier(inst["vraie"][v]) for v in "TPQ"}
        resumes["ss1"] = [("T vraie", f"{_nombre(vr['T'], 2)} °C"), ("P vraie", f"{_nombre(vr['P'], 4)} MPa"),
                          ("Q vraie", f"{_nombre(vr['Q'], 4)} kg/s")]
        valides = sum(inst["statut_mesure"][v][-1] == "valide" for v in "TPQ")
        actifs = [d for d in (inst["scenario"] or {}).get("defauts", [])
                  if d["debut_s"] <= inst["k"][-1] < d["debut_s"] + d.get("duree_s", float("inf"))]
        resumes["ss2"] = [("Mesures valides", f"{valides} / 3"),
                          ("Défaut actif", ", ".join(f"{NOMS_DEFAUTS[d['type']]} {d['variable']}"
                                                     for d in actifs) or "aucun")]
        pret = inst["pret"][-1]
        resumes["ss3"] = [("Référence", "prête" if pret else f"calage {min(n, N_CALAGE)} / {N_CALAGE}"),
                          ("Résidu max", _residu_max(inst))]
        smax = max((max(inst["somme_haut"][v][-1] or 0, inst["somme_bas"][v][-1] or 0) for v in "TPQ"), default=0)
        resumes["ss4"] = [("État", LIBELLES_TXT[inst["etat"][-1]]), ("S max / h", f"{smax:.2f} / {SEUIL_H:g}")]
        ss5 = inst["ss5"]
        resumes["ss5"] = [("Affiché", LIBELLES_TXT.get(ss5.get("etat_affiche"), "n.d.")),
                          ("Demande", "en attente" if ss5.get("demande") else "aucune")]
        emp = inst["journal"].get("empreinte") or ""
        resumes["ss6"] = [("Entrées", _entier((inst["journal"].get("sequence") or 0) + 1)),
                          ("Empreinte", emp[:12] if emp else "n.d.")]
    enfants, classes = [], []
    for i, (c, (code, nom, role)) in enumerate(MODULES.items()):
        st = stats[c]
        moyenne = st["duree_s"] / st["cycles"] * 1000 if st["cycles"] else None
        en_defaut = st["defauts"] > 0
        lignes = [html.Div([html.Span(e, className="etiquette"), html.Span(val, className="chiffre")],
                           className="ligne") for e, val in resumes.get(c, [])]
        enfants.append([
            html.Div([html.Span(code, className="code"),
                      html.Span("DÉFAUT" if en_defaut else ("EN SERVICE" if st["cycles"] else "ARRÊT"),
                                className="voyant")], className="tete"),
            html.Div(nom, className="nom"), html.Div(role, className="role"),
            html.Div(lignes, className="lignes"),
            html.Div(f"{_entier(st['cycles'])} cycles, {moyenne:.3f} ms par cycle" if moyenne is not None
                     else "Aucun cycle", className="pied-module"),
            html.Div(st["dernier_defaut"], className="statut-mesure") if en_defaut else None,
        ])
        classes.append("module" + (" en-defaut" if en_defaut else (" actif" if st["cycles"] else "")))
    return enfants, classes


def _rendre_journal(inst: dict, filtre) -> tuple:
    j = inst["journal"]
    sortie = inst["sortie"]
    if inst["n"]:
        integrite = html.Dl([
            html.Dt("Fichier"), html.Dd(str(Path(sortie) / "journal.sqlite") if sortie else "n.d.", className="chemin"),
            html.Dt("Entrées écrites"), html.Dd(_entier(j["sequence"] + 1), className="chiffre"),
            html.Dt("Dernière empreinte"), html.Dd(j["empreinte"], className="empreinte"),
            html.Dt("Chaînage"), html.Dd("SHA-256, chaque entrée contient l'empreinte de la précédente"),
        ], className="liste-courte")
    else:
        integrite = html.Div("Aucun journal pour l'instant.", className="vide")

    resume = inst.get("resume")
    if inst["scenario"]:
        duree = (inst["fin_reelle"] or time.time()) - (inst["debut_reel"] or time.time())
        synthese = html.Dl([
            html.Dt("Scénario"), html.Dd(inst["scenario"]["nom"]),
            html.Dt("Statut"), html.Dd(LIBELLES_STATUT[inst["statut"]]),
            html.Dt("Cycles journalisés"), html.Dd(f"{_entier(inst['n'])} / {_entier(inst['cycles_prevus'])}",
                                                   className="chiffre"),
            html.Dt("Durée réelle"), html.Dd(_duree(duree), className="chiffre"),
            html.Dt("Transitions"), html.Dd(" → ".join(LIBELLES_TXT[t["vers"]] for t in inst["transitions"]) or "aucune"),
            html.Dt("État final"), html.Dd(LIBELLES_TXT.get((resume or {}).get("etat_final")) or
                                           (LIBELLES_TXT[inst["etat"][-1]] + " (provisoire)" if inst["etat"] else "n.d.")),
            html.Dt("Dossier de sortie"), html.Dd(sortie or "n.d.", className="chemin"),
        ], className="liste-courte")
    else:
        synthese = html.Div("Aucun essai.", className="vide")

    lignes = []
    for ev in reversed(inst["evenements"]):
        categorie, texte = _decrire_evenement(ev)
        if filtre and categorie not in filtre:
            continue
        lignes.append(html.Tr([html.Td(f"{_entier(ev['cycle'])} s", className="chiffre"),
                               html.Td(_heure(ev.get("horodatage_utc")), className="chiffre"),
                               html.Td(html.Span(categorie, className=f"categorie cat-{_classe(categorie)}")),
                               html.Td(texte)]))
        if len(lignes) >= 300:
            break
    if not lignes:
        table = html.Div("Aucun événement.", className="vide")
    else:
        table = html.Table([html.Thead(html.Tr([html.Th(x) for x in ("Temps", f"Heure ({_sigle()})", "Catégorie", "Événement")])),
                            html.Tbody(lignes)], className="table")
    return integrite, synthese, table


def _classe(texte: str) -> str:
    return (texte.lower().replace("é", "e").replace("è", "e").replace(" ", "-"))


# ----- Démarrage --------------------------------------------------------------


def servir(scenario: str | None = None, *, cycles: int | None = None, sortie: str | None = None,
           vitesse: float | None = 1.0, tolerant: bool = False, silencieux: bool = True,
           port: int = 8050, ouvrir: bool = True, a_la_fin=None) -> int:
    """Démarre l'interface ; lance tout de suite le scénario s'il est donné."""
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    session = Session()
    session.a_la_fin = a_la_fin
    cle_vitesse = next((c for c, v in VITESSES.items() if v == vitesse), "1")
    app = creer_application(session, scenario_initial=scenario, vitesse_initiale=cle_vitesse)
    if scenario:
        session.lancer(scenario, vitesse=vitesse, cycles=cycles, tolerant=tolerant, silencieux=silencieux,
                       sortie=sortie)
    adresse = f"http://127.0.0.1:{port}/"
    print(f"Interface opérateur : {adresse}  (Ctrl+C pour quitter)", flush=True)
    if ouvrir:
        threading.Timer(1.2, lambda: webbrowser.open(adresse)).start()
    try:
        app.run(host="127.0.0.1", port=port, debug=False)
    except KeyboardInterrupt:
        pass
    finally:
        session.arreter(attendre=True)
    return 0


if __name__ == "__main__":
    servir()
