"""Rappels automatiques sur Discord pour l'ingénierie détaillée.

Lancé chaque matin par GitHub Actions (.github/workflows/rappels.yml). Le script lit les
issues ouvertes qui portent l'étiquette « ingénierie détaillée », trouve leur échéance dans
la ligne « **Échéance : ...** » de leur description, puis publie sur Discord, pour chaque
membre, les tâches en retard, celles du jour et celles des deux prochains jours.
Le lundi, il publie toute la semaine.

Variables d'environnement :
    GITHUB_TOKEN       jeton fourni par GitHub Actions (lecture des issues)
    GITHUB_REPOSITORY  « propriétaire/dépôt », fourni par GitHub Actions
    DISCORD_WEBHOOK    adresse du webhook du salon Discord (secret du dépôt)
    DISCORD_IDS        facultatif : JSON {"compte GitHub": "identifiant Discord"} pour mentionner chacun
    DATE_DU_JOUR       facultatif : AAAA-MM-JJ, pour tester une autre date
    ESSAI              facultatif : si « 1 », affiche le message sans l'envoyer
"""
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request

PRENOMS = {
    'cKEVIN-Sawadogo': 'Christian', 'RaoufK17': 'Raouf', 'Ryan540gh': 'Rayane',
    'IbrahimaDiallo19': 'Ibrahima', 'boubayans77-rgb': 'Sidiki', 'Mrpropre12': 'Jérémie',
    'abdouldrame09': 'Abdramane', 'thoroumwilson-op': 'Wilson',
}
MOIS = {'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7,
        'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12}
JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
ETIQUETTE = 'ingénierie détaillée'
ANNEE = 2026


def echeance(corps):
    """Date de la ligne « **Échéance : mercredi 2 décembre (brouillon).** », ou None."""
    m = re.search(r'\*\*Échéance : [^*]*?(\d{1,2}) (' + '|'.join(MOIS) + r')', corps or '')
    return dt.date(ANNEE, MOIS[m.group(2)], int(m.group(1))) if m else None


def avancement(corps):
    faites = len(re.findall(r'^- \[x\]', corps or '', re.M | re.I))
    total = faites + len(re.findall(r'^- \[ \]', corps or '', re.M))
    return f'{faites}/{total}' if total else ''


def issues_ouvertes(depot, jeton):
    resultats, page = [], 1
    while True:
        url = (f'https://api.github.com/repos/{depot}/issues?state=open&per_page=100&page={page}'
               f'&labels={urllib.parse.quote(ETIQUETTE)}')
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {jeton}',
                                                   'Accept': 'application/vnd.github+json'})
        with urllib.request.urlopen(req) as r:
            lot = json.load(r)
        resultats += [i for i in lot if 'pull_request' not in i]
        if len(lot) < 100:
            return resultats
        page += 1


def jour(d):
    mois = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'][d.month - 1]
    return f'{JOURS[d.weekday()]} {d.day} {mois}'


def composer(issues, aujourdhui, ids):
    lundi = aujourdhui.weekday() == 0
    horizon = aujourdhui + dt.timedelta(days=6 if lundi else 2)
    par_membre = {}
    for i in issues:
        d = echeance(i.get('body'))
        if d is None or d > horizon:
            continue
        for a in i.get('assignees') or [{'login': '?'}]:
            par_membre.setdefault(a['login'], []).append((d, i))
    if not par_membre:
        return []

    titre = (f"**Rappels de la semaine du {jour(aujourdhui)}**" if lundi
             else f"**Rappels du {jour(aujourdhui)}**")
    blocs = [titre + "\nCoche les cases de ton issue au fur et à mesure. Bloqué depuis plus de 24 h : écris-le ici."]
    for login in sorted(par_membre, key=lambda l: PRENOMS.get(l, l)):
        nom = f"<@{ids[login]}>" if login in ids else f"**{PRENOMS.get(login, login)}**"
        lignes = [nom]
        for d, i in sorted(par_membre[login], key=lambda x: x[0]):
            if d < aujourdhui:
                quand = f"🔴 en retard depuis {jour(d)}"
            elif d == aujourdhui:
                quand = "🟠 aujourd'hui"
            else:
                quand = f"🔵 {jour(d)}"
            av = avancement(i.get('body'))
            lignes.append(f"• {quand} : {i['title']} ({av} fait) <{i['html_url']}>" if av
                          else f"• {quand} : {i['title']} <{i['html_url']}>")
        blocs.append('\n'.join(lignes))
    return decouper(blocs)


def decouper(blocs, limite=1900):
    """Discord refuse les messages de plus de 2 000 caractères."""
    messages, courant = [], ''
    for b in blocs:
        if courant and len(courant) + len(b) + 2 > limite:
            messages.append(courant)
            courant = ''
        courant = f"{courant}\n\n{b}" if courant else b
    if courant:
        messages.append(courant)
    return messages


def envoyer(webhook, texte):
    req = urllib.request.Request(webhook, data=json.dumps({'content': texte}).encode(),
                                 headers={'Content-Type': 'application/json', 'User-Agent': 'rappels-imp2'})
    urllib.request.urlopen(req).read()


def main():
    aujourdhui = (dt.date.fromisoformat(os.environ['DATE_DU_JOUR']) if os.environ.get('DATE_DU_JOUR')
                  else (dt.datetime.utcnow() - dt.timedelta(hours=5)).date())
    ids = json.loads(os.environ.get('DISCORD_IDS') or '{}')
    issues = issues_ouvertes(os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_TOKEN'])
    messages = composer(issues, aujourdhui, ids)
    if not messages:
        print('Rien à rappeler aujourd’hui.')
    for m in messages:
        print(m, '\n' + '-' * 40)
        if os.environ.get('ESSAI') != '1':
            envoyer(os.environ['DISCORD_WEBHOOK'], m)


if __name__ == '__main__':
    main()
