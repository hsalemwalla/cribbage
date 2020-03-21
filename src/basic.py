from cribbage import Player, Team, Game
import json

players = [Player(n) for n in ['Jillian', 'Hussein', 'Farhat', 'Mustafa']]

team1 = Team([players[0], players[1]])
team2 = Team([players[2], players[3]])

game = Game([team1, team2])

game.deal()
# print(game.card_flipped)
# for p in players:
#     print(p.name)
#     for c in p.hand:
#         print('\t', c)

j_hand = game.get_player_hand('Jillian')

print(j_hand)
