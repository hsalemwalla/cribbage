from cribbage import Player, Team, Game
import copy
from flask import Flask, jsonify, Response
from flask_cors import CORS
import time
import flask

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


# *****************************************************************************
# Starting Game
# *****************************************************************************


@app.route('/addPlayer/<team>/<name>')
def add_player(team, name):
    # Add player to player list
    player = Player(name, team)
    global players
    players.append(player)

    # Find team
    # Add player to team
    global teams
    teams[team].add_player(player)

    return "OK"


def start_game():
    global game
    global teams

    if len(players) == 4:
        game = Game(list(teams.values()))
        game.deal()


def waiting_for_players():
    try: 
        curr_num_players = len(players)
        setup_data = {'num_players': curr_num_players}


        # The first time this is called, we need to respond correctly
        if curr_num_players == 4:
            setup_data['ready'] = 'True'
            global game
            setup_data['player_names'] = [{'name': p.name, 'team': p.team} for p in game.players]
        else:
            setup_data['ready'] = 'False'
        yield "data: {}\n\n".format(flask.json.dumps(setup_data))

        if curr_num_players < 4:
            # As this continues to be looping, we need to update our responses with changes
            while len(players) < 4:
                # Update to the right number of players
                if len(players) != curr_num_players:
                    curr_num_players = len(players)
                    setup_data['num_players'] = curr_num_players
                    yield "data: {}\n\n".format(flask.json.dumps(setup_data))

            if curr_num_players == 4:
                start_game()
                setup_data["ready"] = 'True'
                setup_data['player_names'] = [{'name': p.name, 'team': p.team} for p in game.players]
                yield "data: {}\n\n".format(flask.json.dumps(setup_data))
    except:
        return "data: client closed connection\n\n"


@app.route('/gameReady')
def game_ready():
    return Response(waiting_for_players(),
                    mimetype="text/event-stream")


# *****************************************************************************
# Game Play
# *****************************************************************************
@app.route('/playCard/<player_name>/<card>')
def play_card(player_name, card):
    card_symbol, card_suit = card.split(' ')
    global game
    game.play_card(player_name, card_suit, card_symbol)

    return "OK"


@app.route('/getCardsForPlayer/<name>')
def get_cards_for_player(name):
    return game.get_player_hand(name)

@app.route('/pointing')
def pointing():
    def checking_for_pointed_cards():
        global game
        cur_count = copy.deepcopy(game.count)
        while game.phase == 'pointing':
            if game.count != cur_count:
                game_data = {'new_count': game.count}
                cur_count = copy.deepcopy(game.count)
                print(flask.json.dumps(setup_data))
                yield "data: {}\n\n".format(flask.json.dumps(game_data))

        return 'data: Pointing Phase Done\n\n'

    return Response(checking_for_pointed_cards(),
                    mimetype="text/event-stream")
