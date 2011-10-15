from proto import ProtoBot

class DataKeeper(ProtoBot):
    def __init__(self):
        ProtoBot.__init__(self)
        self.hand=[]

        self.discard = -1

        self.deck_size = 39
        self.gone_deck = set()
        self.opponent_hand = set()
        self.total_gone = set()

    def opponent_hand_add(self, card):
        """Add a card to the opponent's hand as know by watching them take the top discard"""
        self.opponent_hand.add(card)
        self.total_gone.update(self.opponent_hand)

    def discard_bury_card(self, card):
        """Kill a card by having it disappear in the discard
        Calling function must know that this happened, this is just the kill order
        """
        self.gone_deck.add(card)
        self.total_gone.update(self.gone_deck)


    def kill_card(self, card):
        """General destruction of the card.  Use if you don't know how cards are being removed from the deck
        """
        self.total_gone.add(card)


    def op_hand_remove(self, card):
        """Have a card removed from the list of cards in the opponent's hand
        """
        self.opponent_hand.discard(card)
        self.total_gone.discard(card)

    def reshuffle_deck(self):
        """reset, as after a shuffle"""
        self.pile_size = 39
        self.gone_deck = set()
        self.total_gone = set()

    def present_between(self, lower, upper):
        """return all cards that are dead and have values between lower and upper inclusive"""
        self.range_gone = set()
        if lower != upper:
            while(lower <= upper):
                if lower in self.total_gone:
                    self.range_gone.add(lower)    
                lower += 1
        return self.range_gone
