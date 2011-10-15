from proto import ProtoBot

class DataKeeper(ProtoBot):
    def __init__(self):
        ProtoBot.__init__(self)
        self.player_id=0
        self.hand=[]

        self.discard = -1

        self.deck_size = 39
        self.gone_deck = set()
        self.opponent_hand = set()
        self.total_gone = set()

        self.indexed_opp_hand=[0 for x in range(20)]
        self.turn_number=0

    def reshuffle_deck(self):
        """reset, as after a shuffle"""
        self.pile_size = 39
        self.gone_deck = set()
        self.total_gone = set()

    def card_is_drawn(self):
        """A card is drawn from the deck, which means the top discard is buried
        """
        self.deck_size-=1
        if self.deck_size==0:
            self.reshuffle_deck()
        self.gone_deck.add(self.discard)
        self.total_gone.update(self.gone_deck)

    def opponent_hand_add(self, card, index):
        """Add a card to the opponent's hand as know by watching them take the top discard"""
        self.indexed_opp_hand[index]=card
        self.opponent_hand.add(card)
        self.total_gone.update(self.opponent_hand)

    def opponent_hand_remove(self, card, index):
        """Have a card removed from the list of cards in the opponent's hand
        """
        self.indexed_opp_hand[index]=0
        self.opponent_hand.discard(card)
        self.total_gone.discard(card)

    def dead_cards_between(self, lower, upper):
        """return all cards that are dead and have values between lower and upper inclusive"""
        self.range_gone = set()
        lower+=1
        if lower != upper:
            while(lower <= upper):
                if lower in self.total_gone:
                    self.range_gone.add(lower)
                lower += 1
        return self.range_gone

    def live_cards_between(self, lower, upper):
        """return the number of cards that are live and have values between lower and upper exclusive"""
        return (upper-lower-1)-len(self.dead_cards_between(lower,upper))



    def start_game(self,game_id,player_id,initial_discard,other_player_id):
        self.player_id=player_id
        self.discard=initial_discard
        self.reshuffle_deck()
        self.indexed_opp_hand=[0 for x in range(20)]
        self.turn_number=1

    def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
        self.hand=rack
        if len(other_player_moves) != 0:
            self.turn_number+=1

        if len(other_player_moves) == 0:
            pass
        elif other_player_moves[-1]["move"] == "take_deck":
            self.card_is_drawn()
            self.opponent_hand_remove(discard, other_player_moves[-1]["idx"])
        elif other_player_moves[-1]["move"] == "take_discard":
            self.opponent_hand_remove(discard, other_player_moves[-1]["idx"])
            self.opponent_hand_add(self.discard, other_player_moves[-1]["idx"])

        self.debug_print(30,"Turn %d: %s" % (self.turn_number, self.indexed_opp_hand))
        self.debug_print(30,"Turn %d: %s" % (self.turn_number, self.opponent_hand))

        self.discard = discard

    def request_discard(self, index):
        self.discard=self.hand[index]
        return ProtoBot.request_discard(self,index)

    def request_deck(self):
        self.card_is_drawn()
        return ProtoBot.request_deck(self)

    def deck_exchange(self,index):
        self.discard=self.hand[index]
        return index

    def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
        return self.deck_exchange(0)

    def game_result(self, game_id, your_score, other_score, reason):
        ProtoBot.game_result(self, game_id, your_score, other_score, reason)
        print(self.indexed_opp_hand)
