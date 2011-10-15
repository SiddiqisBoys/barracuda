#Nikita: all you care about are kill_card(card) and 
#gone() and present_between(lower, upper).

#kill_card(card) mark it deaded

#gone() return set of all dead cards

#present_between(lower, upper) returns set of dead cards between
#lower and upper inclusive.

class DeadCards:
    def __init__(self):
        self.gone_deck = set()
        self.opp_hand = set()
        self.total_gone = set()
        pass
  
    #use op_hand_add(card) to add a card to an opponent's hand
    #as known by watching them take the top discard
    def op_hand_add(self, card):
        self.opp_hand.add(card)
        self.total_gone.update(self.opp_hand)

    #kill a card by having it disappear in the discard
    #calling function must know that this happened, this is just
    #the kill order
    def discard_kill_card(self, card):
        self.gone_deck.add(card)
        self.total_gone.update(self.gone_deck)
    
    #general destruction of the card.  Use if you don't care how
    #cards are being removed from the deck
    def kill_card(self, card):
        self.total_gone.add(card)

    #have a card removed from the list of cards in the opponent's
    #hand
    def op_hand_return(self, card):
        self.opp_hand.discard(card)
        self.total_gone.discard(card)
        
    #reset, as after a shuffle
    def reset(self):
        self.gone_deck = set()
        self.total_gone = set()

    #return all removed cards
    def gone(self):
        return self.total_gone
    
    #return all cards that are dead and have values between
    #lower and upper inclusive
    def present_between(self, lower, upper):
        self.range_gone = set()
        if lower != upper:
            while(lower <= upper):
                if lower in self.total_gone:
                    self.range_gone.add(lower)    
                lower += 1
        return self.range_gone
        
