# -*- coding: utf-8 -*-
"""Ferme les issues du sprint 1 dont le travail est terminé et rouvre #88, fermée par erreur.

Chaque issue fermée reçoit un commentaire qui cite la preuve (demande de fusion, commit ou
document) et ses cases à cocher sont cochées, pour que la progression du tableau soit juste.

Utilisation, depuis la racine du dépôt :
    python Ingenierie_detaillee/fermer_issues_terminees.py                          # affiche, sans rien modifier
    python Ingenierie_detaillee/fermer_issues_terminees.py --appliquer              # applique
    python Ingenierie_detaillee/fermer_issues_terminees.py --appliquer --demo-faite # si la démonstration du J3 a eu lieu

Sans --demo-faite, #72 (démonstration du J3) et #78 (SS-3, dont la dernière case est la
présentation à la démonstration) restent telles quelles. Avec --demo-faite, #78 est fermée et
#72 a ses trois premières cases cochées, mais reste ouverte jusqu'au compte rendu.

Il faut l'outil gh, connecté avec le compte cKEVIN-Sawadogo. Le script peut être relancé sans
risque : une issue déjà fermée n'est pas touchée.
"""
import argparse
import json
import re
import subprocess
import sys

DEPOT = "cKEVIN-Sawadogo/IMP-II-Automne-2026"
R = f"repos/{DEPOT}"

A_FERMER = {
    70: "Terminé : les quatre décisions sont prises et consignées le 19 novembre (commentaire ci-dessus et "
        "`Ingenierie_detaillee/Decisions-architecture.md`). Elles sont en place dans `main` depuis les demandes "
        "#119 et #120. L'issue avait été rouverte par erreur le 19 novembre.",
    71: "Terminé : le gabarit 13 est en ligne (OneDrive), la figure 2-1 et le contrat de données sont en "
        "PlantUML dans `Ingenierie_detaillee/figures/`, et les demandes du sprint 1 (#118 à #125) sont toutes "
        "fusionnées depuis le 20 novembre, tests au vert. La version gelée est l'étiquette `gel-j3`, remplacée "
        "par `gel-j3.1` le 24 novembre (#126).",
    89: "Terminé : les tests de contrat et d'indépendance de SS-1 sont fusionnés dans `main` le 20 novembre "
        "par la demande #122 (`logiciel/tests/test_ss1_boucle.py`). Merci Ibrahima.",
    103: "Terminé : l'interface Plotly Dash est fusionnée dans `main` le 20 novembre par la demande #124, "
         "toutes les cases sont cochées. Les écarts restants sont suivis à part : G1 (#127) et G2 (#128).",
    104: "Terminé : la demande de confirmation en D2 est fusionnée dans `main` le 20 novembre par la demande "
         "#124, toutes les cases sont cochées. La transmission de la réponse par la file des confirmations "
         "est le correctif G1 (#127).",
    113: "Terminé : le module SS-6 (écrivain, scelleur séparé et vérificateur) est fusionné dans `main` le "
         "20 novembre par la demande #123, et Ibrahima a fermé #90. Merci Wilson.",
}

SI_DEMO = {
    78: "Terminé : SS-3 final est dans `main`, la campagne préliminaire C1 (graines 2001 à 2020) passe pour "
        "T, P et Q (commentaire du 19 novembre), et SS-3 a été présenté à la démonstration du J3. La "
        "confirmation de C1 sur la version gelée se poursuit dans #79.",
}

A_ROUVRIR = {
    88: "Rouverte : cette révision est due le jeudi 17 décembre, après la rédaction des sections 5.2 et 7.1 "
        "par Raouf (#81, lundi 14 décembre). Elle avait été fermée par erreur le 18 novembre.",
}


def gh(*args, donnees=None):
    p = subprocess.run(["gh", *args], input=json.dumps(donnees) if donnees is not None else None,
                       capture_output=True, text=True, encoding="utf-8")
    if p.returncode:
        sys.exit(f"Échec de gh {' '.join(args[:4])} : {p.stderr.strip()}")
    return json.loads(p.stdout) if p.stdout.strip().startswith(("{", "[")) else p.stdout


def cocher(corps, seulement=None):
    """Coche les cases ; seulement=n coche les n premières."""
    vu = [0]

    def f(m):
        vu[0] += 1
        return "- [x]" if seulement is None or vu[0] <= seulement else m.group(0)
    return re.sub(r"- \[ \]", f, corps)


def commenter(n, texte, appliquer):
    if appliquer:
        gh("api", "-X", "POST", f"{R}/issues/{n}/comments", "--input", "-", donnees={"body": texte})


def fermer(n, commentaire, appliquer):
    issue = gh("api", f"{R}/issues/{n}")
    if issue["state"] == "closed":
        print(f"#{n} déjà fermée : {issue['title']}")
        return
    corps = issue["body"] or ""
    restantes = corps.count("- [ ]")
    print(f"#{n} {'fermée' if appliquer else 'à fermer'} ({restantes} case(s) à cocher) : {issue['title']}")
    if appliquer:
        commenter(n, commentaire, True)
        champs = {"state": "closed", "state_reason": "completed"}
        if restantes:
            champs["body"] = cocher(corps)
        gh("api", "-X", "PATCH", f"{R}/issues/{n}", "--input", "-", donnees=champs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--appliquer", action="store_true", help="applique les changements")
    ap.add_argument("--demo-faite", action="store_true", help="la démonstration du J3 a eu lieu le 20 novembre")
    a = ap.parse_args()

    for n, texte in A_FERMER.items():
        fermer(n, texte, a.appliquer)

    if a.demo_faite:
        for n, texte in SI_DEMO.items():
            fermer(n, texte, a.appliquer)
        issue = gh("api", f"{R}/issues/72")
        if issue["state"] == "open" and issue["body"].count("- [ ]") == 4:
            print(f"#72 {'mise à jour' if a.appliquer else 'à mettre à jour'} : trois cases cochées, "
                  "reste ouverte jusqu'au compte rendu")
            if a.appliquer:
                gh("api", "-X", "PATCH", f"{R}/issues/72", "--input", "-",
                   donnees={"body": cocher(issue["body"], seulement=3)})
                commenter(72, "La démonstration du J3 a eu lieu le vendredi 20 novembre et la version est gelée "
                              "(`gel-j3`, puis `gel-j3.1`). Il reste le compte rendu : présents, commentaires "
                              "reçus et décisions prises. Il va à Sidiki pour la section 6.1 (#101).", True)
    else:
        print("#72 et #78 laissées telles quelles (ajouter --demo-faite si la démonstration du J3 a eu lieu).")

    for n, texte in A_ROUVRIR.items():
        issue = gh("api", f"{R}/issues/{n}")
        if issue["state"] == "open":
            print(f"#{n} déjà ouverte : {issue['title']}")
            continue
        print(f"#{n} {'rouverte' if a.appliquer else 'à rouvrir'} : {issue['title']}")
        if a.appliquer:
            # Les dates de cette révision n'avaient pas suivi le report du 21 novembre.
            corps = (issue["body"] or "").replace("révision terminée le lundi 14 décembre",
                                                  "révision terminée le jeudi 17 décembre")
            corps = corps.replace("**Échéance : lundi 14 décembre.**", "**Échéance : jeudi 17 décembre.**")
            gh("api", "-X", "PATCH", f"{R}/issues/{n}", "--input", "-", donnees={"state": "open", "body": corps})
            commenter(n, texte, True)

    if not a.appliquer:
        print("\nRien n'a été modifié. Relancer avec --appliquer pour appliquer.")


if __name__ == "__main__":
    main()
