import random
import copy
import json


class Game:
    def __init__(self):
        self.teams = []
        self.players = []
        self.turn = None
        self.dealer = None

        self.deck = Deck()
        self.card_flipped = None

        self.phase = 'setup'
        self.count = 0

        self.who_passed = {}
        self.round_play = []

        self.trigger_next_turn = 0

    def start_game(self, teams):
        self.teams = teams
        self.players = [teams['team1'].players[0], teams['team2'].players[0],
                        teams['team1'].players[1], teams['team2'].players[1]]
        self.who_passed = {p.name: False for p in self.players}
        self.dealer = self.players[0]
        self.turn = self.players[1]

        self.phase = 'pointing'
        self.count = 0

        self.deal()

    def deal(self):
        self.deck.shuffle_deck()
        dealing_deck = copy.deepcopy(self.deck.deck)
        for p in self.players:
            p.hand = [dealing_deck.pop() for _ in range(5)]

        self.card_flipped = dealing_deck.pop()

    def get_player_hand(self, player_name):
        player_hands = {p.name: p.hand for p in self.players}
        hand = player_hands[player_name]
        hand_json = json.dumps([str(c) for c in hand])
        return hand_json

    def pass_turn(self, player_name):
        name2player_map = {p.name: p for p in self.players}
        player = name2player_map[player_name]

        def verify_pass():
            # Verify players turn
            is_player_turn = self.turn.name == player_name
            cards_not_played = [c for c in player.hand if c not in player.pointed]
            # Check that all the not played cards are illegal
            for c in cards_not_played:
                if (c.value + self.count) <= 31:
                    return False
            return True
        legal_pass = verify_pass()
        if legal_pass:
            # Move turn to next player
            all_player_names = [p.name for p in self.players]
            next_player_index = (all_player_names.index(player_name) + 1) % 4
            self.turn = self.players[next_player_index]
            self.who_passed[player_name] = True
            self.trigger_next_turn += 1

    def play_card(self, player_name, card_suit, card_symbol):
        name2player_map = {p.name: p for p in self.players}
        player = name2player_map[player_name]

        # Verify the Card
        def verify_card():
            for c in player.hand:
                # Verify players turn
                is_player_turn = self.turn.name == player_name
                # Verify card in hand
                card_in_hand = (c.suit == card_suit) & (c.symbol == card_symbol)
                # Verify card not in pointed
                card_not_pointed = c not in player.pointed
                # Verify card count <= 31
                under_31 = (c.value + self.count) <= 31

                if is_player_turn & card_in_hand & card_not_pointed & under_31:
                    return c

        card = verify_card()
        if card is None:
            return "NOT A GOOD CARD"

        # Move the card into the player's pointed list
        player = name2player_map[player_name]
        player.pointed.append(card)

        # Add card to the count
        self.count += card.value

        # Add play to the round play
        self.round_play.append({'player': player_name,
                                'card': str(card)})

        # Move turn to next player
        all_player_names = [p.name for p in self.players]
        next_player_index = (all_player_names.index(player_name) + 1) % 4
        self.turn = self.players[next_player_index]
        self.trigger_next_turn += 1

    def add_to_crib(self, player_name, card_suit, card_symbol):
        name2player_map = {p.name: p for p in self.players}
        player = name2player_map[player_name]

        # Verify the Card
        def verify_card():
            for c in player.hand:
                # Verify card in hand
                card_in_hand = (c.suit == card_suit) & (c.symbol == card_symbol)

                if card_in_hand:
                    return c

        card = verify_card()
        if card is None:
            return "NOT A GOOD CARD"

        # Add card to dealer's crib
        self.dealer.crib.append(card)

        # Remove from player's hand
        player.hand.remove(card)

    def next_round(self):
        # Set count to 0
        self.count = 0

        # Reset who has passed
        self.who_passed = {}

        # Update whose turn it is
        last_to_play = self.round_play[-1]['player']

        all_player_names = [p.name for p in self.players]
        next_player_index = (all_player_names.index(last_to_play) + 1) % 4
        self.turn = self.players[next_player_index]

        # Reset round_play
        self.round_play = []
        self.trigger_next_turn += 1


class Team:
    def __init__(self):
        self.players = []
        self.points = 0

    def __str__(self):
        player_names = [p.name for p in self.players]
        return ', '.join(player_names)

    def add_player(self, player):
        self.players.append(player)


class Player:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.hand = []
        self.pointed = []
        self.crib = []


class Deck:
    def __init__(self):
        symbols = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = ['spades', 'hearts', 'clubs', 'diamonds']

        self.deck = [Card(suit, symb) for symb in symbols for suit in suits]

        self.shuffle_deck()

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.deck):
            card = self.deck[self.n]
            self.n += 1
            return card
        else:
            raise StopIteration

    def shuffle_deck(self):
        random.shuffle(self.deck)


class Card:
    def __init__(self, suit, symbol):
        self.suit = suit
        self.symbol = symbol

        symbol_value_map = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                            '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                            'J': 10, 'Q': 10, 'K': 10}
        self.value = symbol_value_map[symbol]

    def __str__(self):
        return '{} {}'.format(self.symbol, self.suit)


# def player_cards():
#     """
#     Given a player's name, return a json object with the cards currently in the players hand.
#     :return:
#     """
#
#     for game.team
