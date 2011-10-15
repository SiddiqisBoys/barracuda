#The cards in the deck:

class DeadCards:
    def __init__(self):
        self.gone_deck = set()
        self.opp_hand = set()
        self.total_gone = set()
        pass
    
    def op_hand_add(self, card):
        self.opp_hand.add(card)
        self.total_gone.update(self.opp_hand)

    def discard_kill_card(self, card):
        self.gone_deck.add(card)
        self.total_gone.update(self.gone_deck)
    
    def kill_card(self, card):
        self.total_gone.add(card)

    def op_hand_return(self, card):
        self.opp_hand.discard(card)
        self.total_gone.discard(card)

    def gone(self):
        return self.total_gone
        
    def present_between(self, lower, upper):
        self.range_gone = set()
        if lower != upper:
            while(lower <= upper):
                if lower in self.total_gone:
                    self.range_gone.add(lower)    
                lower += 1
        return self.range_gone
        
