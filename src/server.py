from cribbage import Player, Team, Game
from flask import Flask
from flask import Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

players = []
teams = {'team1': Team(),
        'team2': Team()}
game = None

# team1 = Team([players[0], players[1]])
# team2 = Team([players[2], players[3]])
# game = Game([team1, team2])
# game.deal()


@app.route('/getCardsForPlayer/<player>')
def get_cards_for_player(player):
    return game.get_player_hand(player)


@app.route('/addPlayer/<team>/<name>')
def add_player(team, name):
    # Add player to player list
    player = Player(name)
    global players
    players.append(player)

    # Find team
    # Add player to team
    global teams
    teams[team].add_player(player)

    start_game()
    return ""


def start_game():
    global game
    global teams

    if len(players) == 4:
        game = Game(list(teams.values()))
        game.deal()

def waiting_for_players():
    currNumPlayers = len(players)
    yield "data: %s\n\n" % currNumPlayers
    while len(players) < 4:
        # If the number of players changes, yield it
        if len(players) != currNumPlayers:
            currNumPlayers = len(players)
            yield "data: %s\n\n" % currNumPlayers
    yield "data: %s\n\n" % "Game is ready"


@app.route('/gameReady')
def game_ready():
    global game
    # return str(game is not None)
    return Response(waiting_for_players(),
                          mimetype="text/event-stream")
