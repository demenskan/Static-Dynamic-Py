from flask import *
from methods import *
import os
from dotenv import load_dotenv

app = Flask(__name__)
generator=Generator()

@app.route("/")
def urlRoot():
    return generator.getPage("index.json", {})
@app.route("/_health")
def urlHealth():
    return "OKidoki"
@app.route("/match")
def urlMatch():
    season = request.args.get('season')
    tournament = request.args.get('tournament')
    game = request.args.get('game')
    return generator.getPage("game.json", {
            "SEASON" : season,
            "TOURNAMENT" : tournament,
            "GAME" : game
        })

@app.route("/standings")
def urlStandings():
    season = request.args.get('season')
    tournament = request.args.get('tournament')
    if (request.args.get('matchweek') is None):
        matchweek = "latest"  # luego vemos lo de las diferentes fechas
    else:
        matchweek=request.args.get('matchweek')
    return generator.getPage("standings.json", {
            "SEASON" : season,
            "TOURNAMENT" : tournament,
            "MATCHWEEK" : matchweek
        })

@app.route("/tournaments")
def urlTournaments():
    season = request.args.get('season')
    tournament = request.args.get('tournament')
    return generator.getPage("tournaments.json", {
            "SEASON" : season,
            "TOURNAMENT" : tournament
        })
@app.route("/tournament-documents-list")
def urlTournamentDocumentsList():
    season = request.args.get('season')
    tournament = request.args.get('tournament')
    return generator.getPage("documents-list.json", {
            "SEASON" : season,
            "TOURNAMENT" : tournament
        })
@app.route("/tournament-document")
def urlTournamentDocument():
    season = request.args.get('season')
    tournament = request.args.get('tournament')
    id=request.args.get('id')
    return generator.getPage("tournaments-document-viewer.json", {
            "SEASON" : season,
            "TOURNAMENT" : tournament,
            "ID" : id
        })
@app.route("/tournament-schedule")
def urlSchedule():
    season = request.args.get('season')
    tournament = request.args.get('tournament')
    if (request.args.get('matchweek') is None):
        matchweek = "latest"  # luego vemos lo de las diferentes fechas
    else:
        matchweek=request.args.get('matchweek')
    return generator.getPage("schedule.json", {
            "SEASON" : season,
            "TOURNAMENT" : tournament,
            "MATCHWEEK" : matchweek
        })
@app.route("/tournament-club-schedule")
def urlClubSchedule():
    season = request.args.get('season')
    tournament = request.args.get('tournament')
    if (request.args.get('club') is None):
        club = "default"  # luego vemos lo de las diferentes fechas
    else:
        club=request.args.get('club')
    return generator.getPage("club-schedule.json", {
            "SEASON" : season,
            "TOURNAMENT" : tournament,
            "CLUB" : club
        })
@app.route("/tournament-scoring")
def urlScoring():
    season = request.args.get('season')
    tournament = request.args.get('tournament')
    if (request.args.get('club') is None):
        club = "general"
    else:
        club=request.args.get('club')
    return generator.getPage("scoring.json", {
            "SEASON" : season,
            "TOURNAMENT" : tournament,
            "CLUB" : club
        })
# e.g. http://127.0.0.1:8000/login
@app.route("/login", methods=['POST'])
def urlLogin():
    try:
        username = request.form['username']
        password = request.form['password']
    except:
        abort(401)
    token = login.generateToken(username, password)
    if token:
        r = {"data": token}
        return jsonify(r)
    abort(401)
# e.g. http://127.0.0.1:8000/cidr-to-mask?value=8
@app.route("/cidr-to-mask")
def urlCidrToMask():
    try:
        auth = request.headers.get('Authorization')
    except:
        abort(401)
    if not protected.accessData(auth):
        abort(401)
    val = request.args.get('value')
    r = {"function": "cidrToMask","input": val,"output": convert.cidrToMask(val), }
    return jsonify(r)
# # e.g. http://127.0.0.1:8000/mask-to-cidr?value=255.0.0.0
@app.route("/mask-to-cidr")
def urlMaskToCidr():
    try:
        auth = request.headers.get('Authorization')
    except:
        abort(401)
    if not protected.accessData(auth):
        abort(401)
    val = request.args.get('value')
    r = { "function": "maskToCidr","input": val,"output": convert.maskToCidr(val),}
    return jsonify(r)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

