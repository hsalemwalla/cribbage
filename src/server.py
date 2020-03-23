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
    global game

    if game.phase == 'counting':
        # Just move to the next turn if its the current player
        if game.turn.name == player_name:
            game.next_turn(player_name)

    if game.phase != 'pointing':
        return "OK"

    # We should check if this is the last card to be 
    # played for the pointing phase
    if game.get_total_num_cards_played() == 16:
        game.pointing_phase_done()
        return "OK"

    if card == "Pass":
        print(player_name + " attempting to pass")
        game.pass_turn(player_name)
    else: 
        print(player_name + " attempting to play: " + card)
        card_symbol, card_suit = card.split(' ')
        game.play_card(player_name, card_suit, card_symbol)

    return "OK"


@app.route('/getCardsForPlayer/<name>')
def get_cards_for_player(name):
    return game.get_player_hand(name)


@app.route('/addToCrib/<player_name>/<card>')
def add_to_crib(player_name, card):
    if card != 'Pass':
        card_symbol, card_suit = card.split(' ')
        global game
        game.add_to_crib(player_name, card_suit, card_symbol)
        print([str(c) for c in game.dealer.crib])

    return "OK"


@app.route('/pointing')
def pointing():
    print("Client called pointing")

    def checking_for_pointed_cards():
        global game

        try:
            # Waiting for all players
            if len(game.dealer.crib) < 4:
                game_data = {'new_count': game.count,
                             'dealer': "",
                             'phase': game.phase,
                             'player_turn': "",
                             'round_play': game.round_play,
                             'next_round_avail': False,
                             'scores': game.scores,
                             'card_flipped': "Waiting for other players"}
                yield "data: {}\n\n".format(flask.json.dumps(game_data))

                while len(game.dealer.crib) < 4:
                    pass

            # Inital ready game state
            game_data = {'new_count': game.count,
                         'dealer': game.dealer.name,
                         'phase': game.phase,
                         'player_turn': game.turn.name,
                         'round_play': game.round_play,
                         'next_round_avail': all(game.who_passed.values()) or game.count == 31,
                         'scores': game.scores,
                         'card_flipped': str(game.card_flipped)}
            yield "data: {}\n\n".format(flask.json.dumps(game_data))

            # Main pointing phase loop
            curr_trigger = copy.deepcopy(game.trigger_next_turn)
            while game.phase == 'pointing':
                if game.trigger_next_turn != curr_trigger:
                    game_data = {'new_count': game.count,
                                 'dealer': game.dealer.name,
                                 'phase': game.phase,
                                 'player_turn': game.turn.name,
                                 'round_play': game.round_play,
                                 'next_round_avail': all(game.who_passed.values()) or game.count == 31,
                                 'scores': game.scores,
                                 'card_flipped': str(game.card_flipped)}
                    curr_trigger = copy.deepcopy(game.trigger_next_turn)
                    yield "data: {}\n\n".format(flask.json.dumps(game_data))

            game_data = {'new_count': game.count,
                         'dealer': game.dealer.name,
                         'phase': game.phase,
                         'player_turn': game.turn.name,
                         'round_play': game.round_play,
                         'next_round_avail': False,
                         'scores': game.scores,
                         'card_flipped': str(game.card_flipped)}
            yield "data: {}\n\n".format(flask.json.dumps(game_data))
        except GeneratorExit:
            print("Client closed pointing phase")
            return "data: pointing done, client closed\n\n"

        return 'data: Pointing Phase Done\n\n'

    return Response(checking_for_pointed_cards(),
                    mimetype="text/event-stream")


@app.route('/counting')
def counting():
    print("Client called counting")

    def counting_phase():
        global game

        try:
            # Initial ready game state
            game_data = {'dealer': game.dealer.name,
                         'phase': game.phase,
                         'all_cards': game.get_all_cards(),
                         'player_turn': game.turn.name,
                         'all_done_counting': all(game.who_passed.values()),
                         'reset': False,
                         'scores': game.scores,
                         'card_flipped': str(game.card_flipped)}
            yield "data: {}\n\n".format(flask.json.dumps(game_data))

            # Main pointing phase loop
            curr_trigger = copy.deepcopy(game.trigger_next_turn)
            while game.phase == 'counting':
                if game.trigger_next_turn != curr_trigger:
                    game_data = {'dealer': game.dealer.name,
                                 'phase': game.phase,
                                 'player_turn': game.turn.name,
                                 'all_done_counting': all(game.who_passed.values()),
                                 'reset': False,
                                 'all_cards': game.get_all_cards(),
                                 'scores': game.scores,
                                 'card_flipped': str(game.card_flipped)}
                    curr_trigger = copy.deepcopy(game.trigger_next_turn)
                    yield "data: {}\n\n".format(flask.json.dumps(game_data))

            game_data = {'dealer': "",
                         'phase': game.phase,
                         'player_turn': "",
                         'all_cards': game.get_all_cards(),
                         'all_done_counting': all(game.who_passed.values()),
                         'reset': True,
                         'scores': game.scores,
                         'card_flipped': ""}
            yield "data: {}\n\n".format(flask.json.dumps(game_data))
        except GeneratorExit:
            print("Client closed counting phase")
            return "data: counting done, client closed\n\n"

        return 'data: Pointing Phase Done\n\n'

    return Response(counting_phase(), mimetype="text/event-stream")


@app.route('/nextRound')
def next_round():
    global game
    game.next_round()
    return "OK"


@app.route('/newHand')
def new_hand():
    global game
    game.ready_for_new_hand_counter += 1
    if game.ready_for_new_hand_counter == 4:
        game.new_hand()
    return "OK"


@app.route('/score/<team>/<score>')
def update_score(team, score):
    global game
    game.scores[team] = score
    game.trigger_next_turn += 1
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
