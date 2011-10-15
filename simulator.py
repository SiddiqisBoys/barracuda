from proto import ProtoBot
import random
from copy import copy
import racko_scoring
from racko import botdfs, bot_heur

class Simulator:
    def __init__(self,p0,p1):
        self.p0=p0
        self.p1=p1

    def run_game(self):
        deal=list(range(81)[1:])
        random.shuffle(deal)
        self.p0_hand=deal[0:20]
        self.p1_hand=deal[21:40]
        self.discard=deal[40]
        self.hand=deal[41:]

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
            else:
                d=deck.pop()
                i=self.p0.get_deck_exchange(1,1000,self.p0_hand,d)
                tmp=self.p0_hand[i]
                self.p0_hand[i]=self.discard
                self.discard=tmp
            self.p0.move_result(1,"next_player_move")

            if racko_scoring.end(self.p0_hand,self.p1_hand)!=0:
                break

            m1=self.p1.get_move(1,self.p1_hand,self.discard,1000,[])
            if m1["move"]=="request_discard":
                i=m1["idx"]
                tmp=self.p1_hand[i]
                self.p1_hand[i]=self.discard
                self.discard=tmp
            else:
                d=deck.pop()
                i=self.p1.get_deck_exchange(1,1000,self.p1_hand,d)
                tmp=self.p1_hand[i]
                self.p1_hand[i]=self.discard
                self.discard=tmp
            self.p1.move_result(1,"next_player_move")

            turn+=1

        sc=racko_scoring.score(self.p0_hand,self.p1_hand)
        self.p0.game_result(1,sc[0],sc[1],"Game over")
        self.p1.game_result(1,sc[1],sc[0],"Game over")
        print("GAME OVER")


s=Simulator(bot_heur(),botdfs(3,1))
s.run_game()
