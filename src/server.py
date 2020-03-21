from cribbage import Player, Team, Game
import json
from flask import Flask

app = Flask(__name__)

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


@app.route('/getCardsForPlayer/<team>/<name>')
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


def start_game():
    global game
    global teams

    if len(players) == 4:
        game = Game(teams)
        game.deal()


@app.route('/gameReady')
def game_ready():
    global game
    return game is not None
