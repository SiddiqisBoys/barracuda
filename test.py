class ProtoBot:
    def __init__(self):
        self.is_enabled=True
    def enable(self):
        self.is_enabled=True
    def disable(self):
        self.is_enabled=False
    def ping(self,s):
        if self.is_enabled:
            return "pong"
        else:
            return "The bot is currently offline"
    def start_game(self, game_id, player_id, initial_discard, other_player_id):
        pass
    def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
        return self.request_discard(0)
    def request_deck(self):
        return {"move": "request_deck"}
    def request_discard(self, index):
        return {"move": "request_discard", "idx":index}

    def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
        return 0

    def move_result(self,game_id, move, reason=""):
        pass
    def game_result(self,game_id, your_score, other_score, reason):
        pass

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
        self.opponent_hand.add(card)
        self.total_gone.update(self.opponent_hand)

    def opponent_hand_remove(self, card):
        """Have a card removed from the list of cards in the opponent's hand
        """
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

    def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
        self.hand=rack
        if len(other_player_moves) == 0:
            pass
        elif other_player_moves[-1]["move"] == "take_deck":
            self.card_is_drawn()
        elif other_player_moves[-1]["move"] == "take_discard":
            self.opponent_hand_add(self.discard, other_player_moves[-1]["idx"])

        self.discard = discard
        return self.request_discard(0)

    def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
        self.card_is_drawn()
        return 0

from math import factorial

def binomial(x, y):
    if y == 0: return 1
    if x <= 0 or y < 0: return 0
    if y > x: return 0
    return factorial(x)/(factorial(y)*factorial(x-y))

class HeuristicBot(DataKeeper):
    def __init__(self,weights=[1,1]):
        DataKeeper.__init__(self)

    def heuristic_combined(self, card, hand, requesting_from_discard):
        scores = [0 for i in range(15)]
        for i in range(15):
            a = hand[i]
            pro = []
            for j in range(5):
                v = []
                for k in range(5):
                    if hand[i+k] == hand[i+j] + k - j: v += [i + k]
                pro += [v]
            lenpro = [len(v) for v in pro]
            pro = pro[lenpro[::-1].index(max(lenpro))]
            
            for j in range(max(0, max(pro) - 4), min(15, min(pro) + 5)):
                scores[i] += self.score_1(hand[j], j)
            scores[i] *= 80 ** len(pro)
        a = 14 - scores[::-1].index(max(scores))
        protected = []
        for j in range(5):
            v = []
            for k in range(5):
                if hand[a+k] == hand[a+j] + k - j: v += [a + k]
            protected += [v]
        lenpro = [len(v) for v in protected]
        protected = protected[lenpro[::-1].index(max(lenpro))]
        
        racko = hand[a]
        
        scan_for = []
        for j in range(max(0, max(protected) - 4), min(15, min(protected) + 5)):
            if j not in protected: scan_for += [racko + j - a]
        
        if card in scan_for: return card + a - racko
        
        scores = [self.score_0(card, i) - self.score_0(hand[i], i) for i in range(20) if i not in protected]
        if requesting_from_discard and max(scores) < 0: return -1
        return [i for i in range(20) if i not in protected][scores.index(max(scores))]

    def score_0(self,val, pos):
        live_before=self.live_cards_between(-1,val)
        live_after=self.live_cards_between(val,80+1)
        #live_before = val - 1
        #live_after = 80 - val
        if live_before + live_after < 19: return 0
        return binomial(live_before,pos)*binomial(live_after,19-pos)/binomial(live_before+live_after,19)

    def score_1(self, val, pos):
        return binomial(75-val,14-pos)*binomial(val-1, pos)/6635869816740560

    def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
        DataKeeper.get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves)
        i = self.heuristic_combined(self.discard, self.hand, requesting_from_discard=True)
        if i == -1: return self.request_deck()
        return self.request_discard(i)
    
    def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
        DataKeeper.get_deck_exchange(self,game_id, remaining_microseconds, rack, card)
        return self.heuristic_combined(card, self.hand, requesting_from_discard=False)


class HeuristicBotOld(DataKeeper):
    def __init__(self):
        DataKeeper.__init__(self)

    def score_0(self,val, pos):
        live_before=self.live_cards_between(-1,val)
        live_after=self.live_cards_between(val,80+1)
        #live_before = val - 1
        #live_after = 80 - val
        if live_before + live_after < 19: return 0
        return binomial(live_before,pos)*binomial(live_after,19-pos)/binomial(live_before+live_after,19)

    def heuristic_0(self, card, hand, requesting_from_discard):
        scores = [self.score_0(card, i) - self.score_0(hand[i], i) for i in range(20)]
        #print(card, hand, scores, scores.index(max(scores)))
        if requesting_from_discard and max(scores) < 0: return -1
        return scores.index(max(scores))

    def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
        DataKeeper.get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves)
        i = self.heuristic_0(self.discard, self.hand, requesting_from_discard=True)
        if i == -1: return self.request_deck()
        return self.request_discard(i)
    
    def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
        DataKeeper.get_deck_exchange(self,game_id, remaining_microseconds, rack, card)
        return self.heuristic_0(card, self.hand, requesting_from_discard=False)

import random
#from copy import copy
import racko_scoring

#from racko import botdfs

class Simulator:
    def __init__(self,p0,p1):
        self.p0=p0
        self.p1=p1

    def deal(self):
        if len(self.deck) == 0:
            print("RESHUFFLING DECK")
            self.deck=self.buried
            self.buried=[]

        return self.deck.pop()

    def run_game(self):
        deal=list(range(81)[1:])
        random.shuffle(deal)
        self.p0_hand=deal[0:20]
        self.p1_hand=deal[20:40]
        self.discard=deal[40]
        self.buried=[]
        self.deck=deal[41:]

        self.p0.start_game(1,0,self.discard,1)
        self.p1.start_game(1,1,self.discard,0)

        turn = 0
        last_move=None
        last_idx=0
        while racko_scoring.end(self.p0_hand,self.p1_hand)==0 and turn<75:
            m0=self.p0.get_move(1,self.p0_hand,self.discard,1000,
                                [{"move":last_move, "idx":last_idx}]
                                if last_move else [])
            if m0["move"]=="request_discard":
                i=m0["idx"]
                tmp=self.p0_hand[i]
                self.p0_hand[i]=self.discard
                self.discard=tmp
                last_move="take_discard"
                last_move_idx=i
            elif m0["move"]=="request_deck":
                d=self.deal()
                i=self.p0.get_deck_exchange(1,1000,self.p0_hand,d)
                self.buried.append(self.discard)
                self.discard=self.p0_hand[i]
                self.p0_hand[i]=d
                last_move="take_deck"
                last_move_idx=i
            else:
                print ("Invalid move", m0)
                assert False
            self.p0.move_result(1,"next_player_move")

            if racko_scoring.end(self.p0_hand,self.p1_hand)==0 and turn<75:
                pass
            else:
                turn+=1

            m1=self.p1.get_move(1,self.p1_hand,self.discard,1000,
                                [{"move":last_move, "idx":last_idx}]
                                if last_move else [])
            if m1["move"]=="request_discard":
                i=m1["idx"]
                tmp=self.p1_hand[i]
                self.p1_hand[i]=self.discard
                self.discard=tmp
                last_move="take_discard"
                last_move_idx=i
            elif m1["move"]=="request_deck":
                d=self.deal()
                i=self.p1.get_deck_exchange(1,1000,self.p1_hand,d)
                self.buried.append(self.discard)
                self.discard=self.p1_hand[i]
                self.p1_hand[i]=d
                last_move="take_deck"
                last_move_idx=i
            else:
                print ("Invalid move", m0)
                assert False
            self.p1.move_result(1,"next_player_move")
            print(self.p0_hand, self.p1_hand)

            turn+=1

        return racko_scoring.score(self.p0_hand,self.p1_hand)
        self.p0.game_result(1,sc,0,"Game over")
        self.p1.game_result(1,0,-sc,"Game over")


s=Simulator(HeuristicBotOld(),HeuristicBot())
score = sum(s.run_game() for i in range(1)) / 1
print(score)
