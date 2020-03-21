import random
import copy
import json


class Game:
    def __init__(self, teams):
        self.teams = teams
        self.team1 = teams[0]
        self.team2 = teams[1]
        self.num_teams = len(teams)

        self.players = [teams[0].players[0], teams[1].players[0],
                        teams[0].players[1], teams[1].players[1]]

        self.deck = Deck()
        self.card_flipped = None
        self.deal()
        self.phase = 'pointing'
        self.count = 0

    def new_round(self):
        pass

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

    def play_card(self, player_name, card_suit, card_symbol):
        name2player_map = {p.name: p for p in self.players}
        player = name2player_map[player_name]

        # Verify the Card
        def verify_card():
            for c in player.hand:
                # Verify card in hand
                card_in_hand = (c.suit == card_suit) & (c.symbol == card_symbol)
                # Verify card not in pointed
                card_not_pointed = c not in player.pointed
                # Verify card count <= 31
                under_31 = (c.value + self.count) <= 31

                if card_in_hand & card_not_pointed & under_31:
                    return c
        card = verify_card()
        if card is None:
            return "NOT A GOOD CARD"

        # Move the card into the player's pointed list
        player = name2player_map[player_name]
        player.pointed.append(card)

        # Add card to the points
        self.count += card.value


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
    def __init__(self, name):
        self.name = name

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
