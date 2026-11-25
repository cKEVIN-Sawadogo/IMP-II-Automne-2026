# -*- coding: utf-8 -*-
"""Met les issues GitHub à jour après la décision du 21 novembre :
un seul rapport (le rapport 13, remis le 24 décembre) et la présentation orale le jeudi 10 décembre.

Utilisation, depuis la racine du dépôt :
    python Ingenierie_detaillee/maj_issues.py              # affiche ce qui changerait, sans rien modifier
    python Ingenierie_detaillee/maj_issues.py --appliquer  # applique les changements

Il faut l'outil gh, connecté avec un compte qui peut modifier les issues du dépôt.
"""
import json
import subprocess
import sys

DEPOT = "cKEVIN-Sawadogo/IMP-II-Automne-2026"
APPLIQUER = "--appliquer" in sys.argv

# numéro : (nouveau titre ou None, [(ancien texte, nouveau texte), ...])
CHANGEMENTS = {
    75: (None, [
        ("- [ ] 10 Conclusion : objectifs, résultats, itérations, contraintes légales, budgétaires, socio-économiques, environnementales et technologiques, recommandations, limites, ouverture.",
         "- [ ] 10 Conclusion : objectifs, résultats, itérations, contraintes légales, budgétaires, socio-économiques, environnementales et technologiques, limites, ouverture, et la recommandation d’ingénierie (livrable L08), qui était prévue au rapport final."),
        ("- Sections 6.2, 7.2 et 9 le 11 décembre ; conclusion et résumé le 16 décembre.",
         "- Sections 6.2, 7.2 et 9 le lundi 14 décembre ; conclusion, recommandation et résumé le vendredi 18 décembre."),
        ("**Échéance : mercredi 16 décembre.**", "**Échéance : vendredi 18 décembre.**"),
    ]),
    76: ("[Dépôt] Intégration, cohérence et dépôt du rapport 13", [
        ("- [ ] Lundi 21 : les deux rapports sont complets.", "- [ ] Lundi 21 : le rapport 13 est complet."),
        ("- [ ] Mardi 22 : mêmes chiffres et mêmes verdicts dans les deux rapports.",
         "- [ ] Mardi 22 : mêmes chiffres et mêmes verdicts dans toutes les sections, et avec le support de la présentation du 10 décembre."),
        ("- Les deux rapports sont déposés.", "- Le rapport 13, qui tient lieu de rapport final, est déposé."),
    ]),
    81: (None, [
        ("- 5.2 le 9 décembre ; 7.1 le 11 décembre ; révision de Rayane terminée le 14.",
         "- 5.2 le vendredi 11 décembre ; 7.1 le lundi 14 décembre ; révision de Rayane terminée le jeudi 17."),
        ("**Échéance : vendredi 11 décembre.**", "**Échéance : lundi 14 décembre.**"),
    ]),
    82: (None, [
        ("- [ ] 5.5 et 6.1 : révision terminée le lundi 14 décembre.", "- [ ] 5.5 et 6.1 : révision terminée le jeudi 17 décembre."),
        ("**Échéance : lundi 14 décembre.**", "**Échéance : jeudi 17 décembre.**"),
    ]),
    87: (None, [
        ("- 5.1, 5.3 et 5.6 le 9 décembre ; références le 16 décembre.",
         "- 5.1, 5.3 et 5.6 le vendredi 11 décembre ; références le vendredi 18 décembre."),
        ("**Échéance : mercredi 16 décembre.**", "**Échéance : vendredi 18 décembre.**"),
    ]),
    94: ("[S3] Présentation orale du J5 (jeudi 10 décembre)", [
        ("Présentation de fin de projet.", "Présentation de fin de projet, avancée au jeudi 10 décembre. Christian fournit le contenu ; le rapport 13 est remis ensuite, le 24 décembre."),
        ("- [ ] Préparer le support à partir du rapport 13 et des résultats.",
         "- [ ] Lundi 7 décembre : support complet, à partir du contenu de Christian et des résultats de la campagne (J4, 4 décembre)."),
        ("- [ ] Répétition le mercredi 16 décembre.", "- [ ] Répétition le mardi 8 décembre, avec toute l’équipe."),
        ("- [ ] Présentation le vendredi 18 décembre.",
         "- [ ] Présentation le jeudi 10 décembre ; noter les questions et les commentaires reçus pour la section 6.1."),
        ("- Le support est prêt pour la répétition du 16.", "- La présentation a eu lieu et ses commentaires sont remis à Sidiki pour la section 6.1."),
        ("**Échéance : mercredi 16 décembre.**", "**Échéance : jeudi 10 décembre.**"),
    ]),
    95: (None, [
        ("- [ ] Section 6.3 : révision terminée le lundi 14 décembre.", "- [ ] Section 6.3 : révision terminée le jeudi 17 décembre."),
        ("**Échéance : lundi 14 décembre.**", "**Échéance : jeudi 17 décembre.**"),
    ]),
    101: (None, [
        ("- [ ] 6.1 Revue de conception : avis de chaque partie prenante, décisions, changements apportés.",
         "- [ ] 6.1 Revue de conception : avis de chaque partie prenante, y compris les questions et les commentaires reçus à la présentation du 10 décembre ; décisions ; changements apportés."),
        ("- 5.5 le 9 décembre ; 6.1 le 11 décembre ; révision de Raouf terminée le 14.",
         "- 5.5 le vendredi 11 décembre ; 6.1 le lundi 14 décembre ; révision de Raouf terminée le jeudi 17."),
        ("**Échéance : vendredi 11 décembre.**", "**Échéance : lundi 14 décembre.**"),
    ]),
    108: (None, [
        ("- [ ] 8 Gantt révisé (`Diagram de Gant.gan`) : jalons J3 et J4 atteints ou non, dates révisées, chemin critique, réserve utilisée.",
         "- [ ] 8 Gantt révisé (`Diagram de Gant.gan`) : jalons J3 et J4 atteints ou non, J5 avancé au 10 décembre, fusion du rapport final et du rapport 13, dates révisées, chemin critique, réserve utilisée."),
        ("- 5.4 le 9 décembre ; Gantt le 11 décembre ; révision d’Abdramane terminée le 14.",
         "- 5.4 le vendredi 11 décembre ; Gantt le lundi 14 décembre ; révision d’Abdramane terminée le jeudi 17."),
        ("**Échéance : vendredi 11 décembre.**", "**Échéance : lundi 14 décembre.**"),
    ]),
    109: (None, [
        ("- [ ] 5.1, 5.3, 5.6 et 11 : révision terminée le lundi 14 décembre.", "- [ ] 5.1, 5.3, 5.6 et 11 : révision terminée le jeudi 17 décembre."),
        ("**Échéance : lundi 14 décembre.**", "**Échéance : jeudi 17 décembre.**"),
    ]),
    110: (None, [
        ("- [ ] Section 6.3 (vendredi 11 décembre)", "- [ ] Section 6.3 (lundi 14 décembre)"),
        ("**Échéance : vendredi 11 décembre.**", "**Échéance : lundi 14 décembre.**"),
    ]),
    111: (None, [
        ("- [ ] 5.4 et 8 : révision terminée le lundi 14 décembre.", "- [ ] 5.4 et 8 : révision terminée le jeudi 17 décembre."),
        ("**Échéance : lundi 14 décembre.**", "**Échéance : jeudi 17 décembre.**"),
    ]),
    112: ("[Dépôt] Mise en forme du rapport 13", []),
    116: (None, [
        ("- [ ] 6.2, 7.2 et 9 : révision terminée le lundi 14 décembre.",
         "- [ ] 6.2, 7.2 et 9 : révision terminée le jeudi 17 décembre ; conclusion et résumé relus le lundi 21 décembre."),
        ("**Échéance : lundi 14 décembre.**", "**Échéance : jeudi 17 décembre.**"),
    ]),
    117: ("[Dépôt] Relecture de la langue du rapport 13", []),
}

A_FERMER = {
    74: "Sans objet : le professeur a confirmé le 21 novembre que le rapport d’ingénierie détaillée tient lieu de rapport final. "
        "Il n’y a plus qu’un rapport, le rapport 13, remis le 24 décembre. La recommandation d’ingénierie (L08) va à la section 10 (#75).",
}

JALON_3 = {"title": "Sprint 3 : présentation (J5, 10 décembre) et sections 5 à 10", "due_on": "2026-12-18T00:00:00Z"}


def gh(*args, entree=None):
    r = subprocess.run(["gh", *args], input=entree, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit(f"Échec de gh {' '.join(args[:3])} : {r.stderr.strip()}")
    return r.stdout


def main():
    erreurs = 0
    for numero, (titre, remplacements) in CHANGEMENTS.items():
        issue = json.loads(gh("api", f"repos/{DEPOT}/issues/{numero}"))
        corps = issue["body"] or ""
        for ancien, nouveau in remplacements:
            if ancien not in corps:
                if nouveau in corps:
                    continue  # déjà appliqué
                print(f"#{numero} : texte introuvable, à vérifier à la main : {ancien[:70]}…")
                erreurs += 1
                continue
            corps = corps.replace(ancien, nouveau)
        champs = {}
        if corps != (issue["body"] or ""):
            champs["body"] = corps
        if titre and titre != issue["title"]:
            champs["title"] = titre
        if not champs:
            print(f"#{numero} : déjà à jour")
            continue
        print(f"#{numero} : {', '.join(champs)} {'modifié' if APPLIQUER else 'à modifier'}" + (f" → « {titre} »" if "title" in champs else ""))
        if APPLIQUER:
            gh("api", "-X", "PATCH", f"repos/{DEPOT}/issues/{numero}", "--input", "-", entree=json.dumps(champs))

    for numero, commentaire in A_FERMER.items():
        issue = json.loads(gh("api", f"repos/{DEPOT}/issues/{numero}"))
        if issue["state"] == "closed":
            print(f"#{numero} : déjà fermée")
            continue
        print(f"#{numero} : {'fermée' if APPLIQUER else 'à fermer'} avec un commentaire")
        if APPLIQUER:
            gh("api", "-X", "POST", f"repos/{DEPOT}/issues/{numero}/comments", "--input", "-", entree=json.dumps({"body": commentaire}))
            gh("api", "-X", "PATCH", f"repos/{DEPOT}/issues/{numero}", "--input", "-",
               entree=json.dumps({"state": "closed", "state_reason": "not_planned"}))

    jalons = json.loads(gh("api", f"repos/{DEPOT}/milestones?state=all"))
    jalon = next((j for j in jalons if j["title"].startswith("Sprint 3")), None)
    if jalon and jalon["title"] != JALON_3["title"]:
        print(f"Jalon « {jalon['title']} » {'renommé' if APPLIQUER else 'à renommer'} → « {JALON_3['title']} »")
        if APPLIQUER:
            gh("api", "-X", "PATCH", f"repos/{DEPOT}/milestones/{jalon['number']}", "--input", "-", entree=json.dumps(JALON_3))

    if not APPLIQUER:
        print("\nRien n’a été modifié. Relancer avec --appliquer pour appliquer.")
    if erreurs:
        print(f"{erreurs} texte(s) introuvable(s) : les issues concernées ont peut-être été modifiées à la main.")


if __name__ == "__main__":
    main()
