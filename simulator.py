import random
from copy import copy
import racko_scoring

from proto import ProtoBot
from racko import botdfs
from heuristic import HeuristicBot

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
        while racko_scoring.end(self.p0_hand,self.p1_hand)==0 and turn<75:
            m0=self.p0.get_move(1,self.p0_hand,self.discard,1000,[])
            if m0["move"]=="request_discard":
                i=m0["idx"]
                tmp=self.p0_hand[i]
                self.p0_hand[i]=self.discard
                self.discard=tmp
            elif m0["move"]=="request_deck":
                d=self.deal()
                i=self.p0.get_deck_exchange(1,1000,self.p0_hand,d)
                self.buried.append(self.discard)
                self.discard=self.p0_hand[i]
                self.p0_hand[i]=d
            else:
                print ("Invalid move", m0)
                assert False
            self.p0.move_result(1,"next_player_move")

            if racko_scoring.end(self.p0_hand,self.p1_hand)!=0:
                break

            m1=self.p1.get_move(1,self.p1_hand,self.discard,1000,[])
            if m1["move"]=="request_discard":
                i=m1["idx"]
                tmp=self.p1_hand[i]
                self.p1_hand[i]=self.discard
                self.discard=tmp
            elif m1["move"]=="request_deck":
                d=self.deal()
                i=self.p1.get_deck_exchange(1,1000,self.p1_hand,d)
                self.buried.append(self.discard)
                self.discard=self.p1_hand[i]
                self.p1_hand[i]=d
            else:
                print ("Invalid move", m0)
                assert False
            self.p1.move_result(1,"next_player_move")

            turn+=1

        if racko_scoring.end(self.p0_hand,self.p1_hand)!=0:
            print("Player one, hands are:")
            print(self.p0_hand)
            print(self.p1_hand)

        sc=racko_scoring.score(self.p0_hand,self.p1_hand)
        self.p0.game_result(1,sc,0,"Game over")
        self.p1.game_result(1,0,-sc,"Game over")
        print("GAME OVER")


s=Simulator(HeuristicBot([1,0]),HeuristicBot([1,1]))
s.run_game()
