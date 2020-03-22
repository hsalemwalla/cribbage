#!/usr/bin/python3
from cribbage import Player, Team, Game
import copy
from flask import Flask, Response
from flask_cors import CORS
import flask

app = Flask(__name__)
CORS(app)

players = []
teams = {'team1': Team(),
         'team2': Team()}

game = Game()


# *****************************************************************************
# Starting Game
# *****************************************************************************
@app.route('/addPlayer/<team>/<name>')
def add_player(team, name):
    print("ADDING {} to {}".format(name, team))
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
    print("STARTING GAME")
    global game
    global teams

    if len(players) == 4:
        game.start_game(teams)


def waiting_for_players():
    print('WAITING FOR PLAYERS')
    try:
        global game
        # The first time this is called, we need to respond correctly
        curr_num_players = len(players)
        setup_data = {'num_players': curr_num_players,
                      'ready': 'False',
                      'player_names': [{'name': p.name, 'team': p.team} for p in game.players]}
        if curr_num_players == 4:
            setup_data['ready'] = 'True'
        print("line 57: yielding player data")
        yield "data: {}\n\n".format(flask.json.dumps(setup_data))

        if curr_num_players < 4:
            # As this continues to be looping, we need to update our responses with changes
            while len(players) < 4:
                # Update to the right number of players
                if len(players) != curr_num_players:
                    print("line 65:updating number of players")
                    curr_num_players = len(players)
                    setup_data['num_players'] = curr_num_players
                    setup_data['player_names'] = [{'name': p.name, 'team': p.team} for p in game.players]
                    yield "data: {}\n\n".format(flask.json.dumps(setup_data))

            if curr_num_players == 4:
                print('line 72: starting game')
                start_game()
                setup_data["ready"] = 'True'
                setup_data['player_names'] = [{'name': p.name, 'team': p.team} for p in game.players]
                print('line 76: updating number of players')
                yield "data: {}\n\n".format(flask.json.dumps(setup_data))
    except GeneratorExit:
        print("client closed stream")
        return "data: client closed connection\n\n"


@app.route('/gameReady')
def game_ready():
    print('GAME READY')
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


@app.route('/addToCrib/<player_name>/<card>')
def add_to_crib(player_name, card):
    card_symbol, card_suit = card.split(' ')
    global game
    game.add_to_crib(player_name, card_suit, card_symbol)

    return "OK"


@app.route('/pointing')
def pointing():
    print("Client called pointing")

    def checking_for_pointed_cards():
        global game

        game_data = {'new_count': game.count,
                     'player_turn': game.turn.name,
                     'card_flipped': game.card_flipped}
        yield "data: {}\n\n".format(flask.json.dumps(game_data))

        cur_count = copy.deepcopy(game.count)
        while game.phase == 'pointing':
            if game.count != cur_count:
                game_data = {'new_count': game.count,
                             'player_turn': game.turn.name,
                             'card_flipped': game.card_flipped}
                cur_count = copy.deepcopy(game.count)
                yield "data: {}\n\n".format(flask.json.dumps(game_data))

        return 'data: Pointing Phase Done\n\n'

    return Response(checking_for_pointed_cards(),
                    mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

