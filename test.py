from random import shuffle, randint
from card import Card

index_deck = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "sJoker", "bJoker"]
full_deck = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "sJoker", "bJoker", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
shuffle(full_deck)
wild_cards = full_deck[:3]
p1_deck = sorted(full_deck[3:20] , key=lambda x: index_deck.index(x))
p2_deck = sorted(full_deck[20:37] , key=lambda x: index_deck.index(x))
p3_deck = sorted(full_deck[37:54] , key=lambda x: index_deck.index(x))

print(wild_cards)
print(p1_deck)
print(p2_deck)
print(p3_deck)

print(randint(1, 3))
