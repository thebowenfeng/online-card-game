class Card():
    def __init__(self, play):
        self.play = play.split()
        self.deck = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "sJoker", "bJoker"]

    def __gt__(self, other):
        if self.deck.index(self.play[0]) > self.deck.index(other.play[0]):
            return True
        else:
            return False