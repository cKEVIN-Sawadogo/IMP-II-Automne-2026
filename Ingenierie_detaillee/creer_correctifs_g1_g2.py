# -*- coding: utf-8 -*-
"""Crée les issues des correctifs G1 et G2 du registre de Gel-J3.md, assignées à Jérémie.

Les deux correctifs touchent seulement SS-5 (l'interface Dash). Ils ne changent pas la campagne
statistique ni l'étiquette gel-j3.1, mais ils doivent être fusionnés avant l'essai
d'utilisabilité EX-Q-03 (#106).

Utilisation, depuis la racine du dépôt :
    python Ingenierie_detaillee/creer_correctifs_g1_g2.py --essai        # affiche, sans rien créer
    python Ingenierie_detaillee/creer_correctifs_g1_g2.py                # crée les deux issues
    python Ingenierie_detaillee/creer_correctifs_g1_g2.py --projet 1     # et les ajoute au tableau numéro 1

Il faut l'outil gh, connecté avec le compte cKEVIN-Sawadogo. Pour --projet, le jeton doit avoir
la permission « project » : gh auth refresh -s project. Le script peut être relancé sans
risque : il ne recrée pas une issue qui existe déjà (même titre).
"""
import argparse
import json
import subprocess
import sys

DEPOT = "cKEVIN-Sawadogo/IMP-II-Automne-2026"
JEREMIE, IBRAHIMA = "Mrpropre12", "IbrahimaDiallo19"
ESSAI_UTILISABILITE = 106
ETIQUETTES = {"ingénierie détaillée": "5319e7", "logiciel": "1d76db", "correctif": "d93f0b"}

REGLES = (
    "### Règles des correctifs après le gel (`Ingenierie_detaillee/Gel-J3.md`, section 4)\n"
    "- Une seule branche pour G1 et G2, par exemple `correctifs-ss5`, partie de `main` à jour.\n"
    "- Une demande de fusion dont le titre commence par « Correctif : » et dont la description contient "
    "`Ferme #G1` et `Ferme #G2` (avec les vrais numéros de ces issues).\n"
    "- Chaque défaut a un test qui échoue avant le correctif et passe après.\n"
    "- `python -m pytest -q` dans `logiciel` : tout au vert. Sous Windows, le résultat attendu "
    "est « passed » partout, avec un seul test sauté.\n"
    "- Dans le registre de `Gel-J3.md` (section 5), remplir la colonne « Demande » de G1 et G2 avec le numéro "
    "de la demande de fusion. La colonne « Étiquette » reste « sans objet » : un correctif limité à SS-5 "
    "ne crée pas de nouvelle étiquette.\n"
    "- Revue par Ibrahima (liste en 6 points), puis Christian fusionne."
)


def corps(contexte, constat, a_faire, tests, fini, echeance):
    s = f"{contexte}\n\n### Ce qui ne va pas aujourd'hui\n" + "\n".join(f"- {c}" for c in constat)
    s += "\n\n### À faire\n" + "\n".join(f"- [ ] {t}" for t in a_faire)
    s += "\n\n### Tests à ajouter\n" + "\n".join(f"- [ ] {t}" for t in tests)
    s += "\n\n### Terminé quand\n" + "\n".join(f"- {f}" for f in fini)
    s += f"\n\n**Échéance : {echeance}.** Les séances de l'essai d'utilisabilité (#{ESSAI_UTILISABILITE}) " \
         "commencent après la fusion et se terminent le mercredi 2 décembre."
    return s + "\n\n" + REGLES


G1 = dict(
    title="[S2] Correctif G1 : la réponse de l'opérateur passe par la file des confirmations",
    body=corps(
        "Registre de `Gel-J3.md`, écart G1. La décision d'architecture du 19 novembre (décision 1, point 4) dit que "
        "l'interface ne touche jamais SS-5 directement : elle dépose la réponse de l'opérateur dans "
        "`orchestrateur.confirmations`, et l'orchestrateur la prend au début du cycle suivant. L'orchestrateur sait "
        "déjà le faire (`Orchestrateur._transmettre_reponse`, événements `confirmation_operateur` et "
        "`confirmation_sans_effet`) ; il ne manque que le branchement côté interface. Exigence EX-F-09.",
        ["`Session.repondre()` (`logiciel/jumeau/ss5_interface/session.py`) appelle `self._ss5.repondre(reponse)` "
         "directement, depuis le fil de Dash, pendant que l'orchestrateur exécute SS-5 dans son propre fil.",
         "La réception n'est donc jamais journalisée : aucun événement `confirmation_operateur` dans le journal "
         "d'un essai lancé depuis l'interface, et le vérificateur affiche `confirmations=0`.",
         "Une réponse à une demande déjà retirée (changement d'état entre-temps) n'est pas détectée comme périmée.",
         "Deuxième défaut, trouvé en préparant cette issue : dans une session de l'interface, l'orchestrateur reçoit "
         "les modules enveloppés (`_Enveloppe`, `session.py` ligne 58). L'enveloppe n'expose pas `demande` ni "
         "`repondre` du module SS-5. Résultat : `getattr(self.modules[\"ss5\"], \"demande\", None)` vaut toujours "
         "`None`, le cache publie toujours `demande_en_cours: null`, et une réponse déposée dans la file serait "
         "journalisée « sans effet » avec le motif `aucune_demande_en_cours`."],
        ["Dans `_Enveloppe`, transmettre au module enveloppé tout ce que l'enveloppe ne définit pas : "
         "`def __getattr__(self, nom): return getattr(self.module, nom)`. L'orchestrateur voit alors la vraie "
         "demande de SS-5 et peut lui transmettre la réponse.",
         "Dans `Session.lancer()`, garder l'orchestrateur créé (par exemple `self._orch = orch`), et le remettre à "
         "`None` dans `_remettre_a_zero()`.",
         "Réécrire `Session.repondre(reponse)` : refuser une réponse autre que « confirme » ou « refuse » ; lire le "
         "numéro de cycle de la demande en cours (`getattr(self._ss5, \"demande\", None)`, puis son champ `\"k\"`, en lecture seule) ; refuser s'il n'y a "
         "pas de demande ; puis appeler `self._orch.confirmations.deposer({\"k_demande\": k, \"decision\": reponse})`.",
         "Ne plus appeler `self._ss5.repondre()` nulle part dans `session.py` ni dans `tableau.py`.",
         "Message affiché après le clic : « Réponse transmise ; elle sera journalisée au cycle suivant. »",
         "Mettre à jour la docstring en tête de `tableau.py` (ligne 14), qui dit encore que la réponse passe par "
         "`PresentationEtat.repondre()`."],
        ["Dans `tests/test_ss5_tableau.py` : lancer `derive_lente.json` avec `Session`, attendre la demande de "
         "confirmation, appeler `session.repondre(\"confirme\")`, laisser finir l'essai, puis vérifier que le journal "
         "contient, dans une même entrée, `confirmation_operateur` suivi de `reponse_operateur`, et que "
         "`verifier(journal).confirmations == 1`.",
         "Une réponse dont `k_demande` ne correspond plus à la demande en cours donne `confirmation_sans_effet` "
         "avec le motif `demande_perimee` (on peut déposer directement dans `session._orch.confirmations`).",
         "Un test qui lit `session.py` et `tableau.py` et vérifie qu'aucun ne contient `_ss5.repondre(` "
         "(même principe que les tests d'architecture de `test_ss5_interface.py`).",
         "Pour répondre pendant un essai lancé à la vitesse maximale : attendre que `getattr(session._ss5, \"demande\", None)` "
         "ne soit plus `None`, appeler `session.mettre_en_pause()`, répondre, puis `session.reprendre()`. Avec "
         "`derive_lente.json`, la demande arrive au cycle 1 270 et la réponse est journalisée un ou deux cycles plus tard (1 272 sur notre essai). Le test cherche l'entrée qui contient `confirmation_operateur`, sans fixer son numéro.",
         "Le test existant `test_la_reponse_sans_essai_en_cours_est_refusee` passe toujours."],
        ["Un essai lancé avec `python lancer.py scenarios/derive_lente.json --interface`, avec un clic sur "
         "« Confirmer », puis `python lancer.py --verifier <dossier>`, affiche `confirmations=1` et le verdict INTÈGRE.",
         "Les tests passent dans `main`, et le registre de `Gel-J3.md` est à jour."],
        "jeudi 26 novembre pour la demande de fusion, vendredi 27 novembre pour la fusion"),
)

G2 = dict(
    title="[S2] Correctif G2 : mode opérateur sans grandeurs vraies pour l'essai EX-Q-03",
    body=corps(
        "Registre de `Gel-J3.md`, écart G2. Les grandeurs vraies de SS-1 n'existent que dans le banc d'essai : un "
        "opérateur réel ne les voit jamais. Pendant l'essai d'utilisabilité, un participant doit lire l'état "
        "seulement à partir de ce que l'opérateur verrait. Sinon il peut lire la réponse au lieu de la déduire, et "
        "le résultat d'EX-Q-03 ne vaut rien. Le mode actuel reste le mode par défaut pour la démonstration et la "
        "présentation du 10 décembre.",
        ["La page « Analyse des sous-systèmes » trace la « Grandeur vraie (SS-1, banc d'essai) » "
         "(`tableau.py`, vers la ligne 273).",
         "Le résumé de la chaîne, visible sur tous les onglets, affiche « T vraie », « P vraie » et « Q vraie » "
         "(`tableau.py`, vers la ligne 897).",
         "La barre d'essai montre le nom et la description du scénario (`choix-scenario`, `description-scenario`) : "
         "un participant qui lit « dérive lente » connaît la réponse.",
         "`Session` enregistre les grandeurs vraies à chaque cycle (`self.vraie`, `session.py` lignes 122, 146 et 192)."],
        ["Ajouter l'option `--mode operateur` à `lancer.py` (valeurs `developpement`, par défaut, et `operateur`), "
         "transmise à `servir()` puis à `creer_application(session, mode=...)` et à `Session(mode=...)`.",
         "En mode opérateur, `Session` n'enregistre aucune grandeur vraie : l'enveloppe de SS-1 ne copie plus "
         "`grandeurs_vraies`. Rien ne peut donc fuiter vers l'écran, même par erreur.",
         "En mode opérateur, l'interface n'a que l'onglet « Conduite » : pas d'onglet « Analyse », pas d'onglet "
         "« Journal », pas de bloc « Chaîne de traitement ».",
         "En mode opérateur, la barre d'essai ne montre ni la liste des scénarios ni leur description. L'animateur "
         "lance la présentation en ligne de commande : "
         "`python lancer.py scenarios/<scénario>.json --interface --mode operateur`. Il garde « Lancer », « Pause » "
         "et « Arrêter ».",
         "Attention aux rappels Dash : un rappel dont la sortie n'existe plus dans la page fait une erreur. Ne pas "
         "enregistrer ces rappels en mode opérateur (ou passer `suppress_callback_exceptions=True`).",
         "Ajouter au README de `logiciel` la commande de l'essai d'utilisabilité.",
         "Faire une capture de la vue opérateur pour les sections 4.6 et 5.4 du rapport 13."],
        ["Mode opérateur : après un essai court (`cycles=700`), `session.instantane(complet=True)[\"vraie\"]` ne "
         "contient aucune valeur.",
         "Mode opérateur : la mise en page de l'application, convertie en texte (`str(app.layout)` ou "
         "`json.dumps(app.layout.to_plotly_json(), default=str)`), ne contient ni « vraie », ni « Analyse », ni "
         "« choix-scenario », ni « description-scenario ».",
         "Mode développement : les tests existants de `test_ss5_tableau.py` passent sans changement (les grandeurs "
         "vraies sont toujours enregistrées et l'onglet « Analyse » existe).",
         "`python lancer.py --help` mentionne `--mode`."],
        ["`python lancer.py scenarios/derive_lente.json --interface --mode operateur` ouvre une page où l'on ne voit "
         "que la conduite, sans grandeurs vraies ni nom de scénario, et la dérive s'affiche au bon moment.",
         "Le protocole de l'essai d'utilisabilité (#106) utilise cette commande.",
         "Les tests passent dans `main`, et le registre de `Gel-J3.md` est à jour."],
        "jeudi 26 novembre pour la demande de fusion, vendredi 27 novembre pour la fusion"),
)

ISSUES = [G1, G2]


def gh(*args, donnees=None):
    p = subprocess.run(["gh", *args], input=json.dumps(donnees) if donnees is not None else None,
                       capture_output=True, text=True, encoding="utf-8")
    if p.returncode:
        sys.exit(f"Échec de gh {' '.join(args[:3])} : {p.stderr.strip()}")
    return json.loads(p.stdout) if p.stdout.strip().startswith(("{", "[")) else p.stdout


def titres_existants(R):
    titres, page = {}, 1
    while True:
        lot = gh("api", f"{R}/issues?state=all&per_page=100&page={page}")
        if not lot:
            return titres
        titres.update({i["title"]: i["number"] for i in lot if "pull_request" not in i})
        page += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--essai", action="store_true", help="affiche les issues sans rien créer")
    ap.add_argument("--projet", type=int, help="numéro du tableau GitHub Projects")
    a = ap.parse_args()
    if a.essai:
        for it in ISSUES:
            print("=" * 100 + f"\n{it['title']}\nAssignée à : {JEREMIE}\n\n{it['body']}\n")
        print("Rien n'a été créé. Relancer sans --essai pour créer les issues.")
        return

    R = f"repos/{DEPOT}"
    jalons = gh("api", f"{R}/milestones?state=all&per_page=100")
    jalon = next((j["number"] for j in jalons if j["title"].startswith("Sprint 2")), None)
    if jalon is None:
        sys.exit("Jalon « Sprint 2 » introuvable.")
    presentes = {e["name"] for e in gh("api", f"{R}/labels?per_page=100")}
    for nom, couleur in ETIQUETTES.items():
        if nom not in presentes:
            gh("api", "-X", "POST", f"{R}/labels", "--input", "-", donnees={"name": nom, "color": couleur})

    existantes = titres_existants(R)
    numeros = []
    for it in ISSUES:
        if it["title"] in existantes:
            n = existantes[it["title"]]
            print(f"déjà là : #{n} {it['title']}")
        else:
            r = gh("api", "-X", "POST", f"{R}/issues", "--input", "-", donnees={
                "title": it["title"], "body": it["body"], "assignees": [JEREMIE],
                "labels": list(ETIQUETTES), "milestone": jalon})
            n = r["number"]
            print(f"#{n} {it['title']}")
        numeros.append(n)
        if a.projet:
            # Sans effet si l'issue est déjà dans le tableau : le script peut être relancé.
            gh("project", "item-add", str(a.projet), "--owner", DEPOT.split("/")[0],
               "--url", f"https://github.com/{DEPOT}/issues/{n}")
            print(f"   ajoutée au tableau {a.projet}")

    g1, g2 = numeros
    # Les numéros réels remplacent « #G1 » et « #G2 » dans les règles de chaque issue.
    for n in numeros:
        issue = gh("api", f"{R}/issues/{n}")
        corps_maj = issue["body"].replace("`Ferme #G1`", f"`Ferme #{g1}`").replace("`Ferme #G2`", f"`Ferme #{g2}`")
        if corps_maj != issue["body"]:
            gh("api", "-X", "PATCH", f"{R}/issues/{n}", "--input", "-", donnees={"body": corps_maj})

    marque = f"Bloquée par #{g1} et #{g2}"
    commentaires = gh("api", f"{R}/issues/{ESSAI_UTILISABILITE}/comments?per_page=100")
    if not any(marque in c["body"] for c in commentaires):
        gh("api", "-X", "POST", f"{R}/issues/{ESSAI_UTILISABILITE}/comments", "--input", "-", donnees={"body":
           f"{marque} (correctifs G1 et G2 de `Gel-J3.md`). Les séances se font après leur fusion, avec "
           f"`python lancer.py scenarios/<scénario>.json --interface --mode operateur`. @{IBRAHIMA}, tu fais la "
           f"revue des deux correctifs."})
        print(f"Commentaire ajouté à #{ESSAI_UTILISABILITE}.")


if __name__ == "__main__":
    main()
