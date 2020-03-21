from cribbage import Player, Team, Game
import json
from flask import Flask

app = Flask(__name__)

players = [Player(n) for n in ['Jillian', 'Hussein', 'Farhat', 'Mustafa']]

team1 = Team([players[0], players[1]])
team2 = Team([players[2], players[3]])

game = Game([team1, team2])

game.deal()


@app.route('/getCardsForPlayer/<player>')
def get_cards_for_player(player):
    return game.get_player_hand(player)
