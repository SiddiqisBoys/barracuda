from math import factorial
from cards import DataKeeper

def binomial(x, y):
    if y == 0: return 1
    if x <= 0 or y < 0: return 0
    if y > x: return 0
    return factorial(x)/(factorial(y)*factorial(x-y))

class HeuristicBot(DataKeeper):
    def __init__(self,weights=[1,1]):
        DataKeeper.__init__(self)
        self.weights=weights

    def heuristic_combined(self, card, hand, requesting_from_discard):
        h0 = self.heuristic_0(card, hand, requesting_from_discard)
        h1 = self.heuristic_1(card, hand, requesting_from_discard)

        if self.weights[0]*h0[1] > self.weights[1]*h1[1]:
            return h0[0]
        else:
            return h1[0]

    def score_0(self,val, pos):
        live_before=self.live_cards_between(0,val)
        live_after=self.live_cards_between(val,80+1)
        return binomial(live_before,pos)*binomial(live_after,19-pos)/binomial(live_before+live_after,19)

    def heuristic_0(self, card, hand, requesting_from_discard):
        scores = [self.score_0(card, i) - self.score_0(hand[i], i) for i in range(20)]
        if requesting_from_discard and max(scores) < 0: return (-1, 1)
        return (scores.index(max(scores)), max(scores))

    def score_1(self, val, pos):
        return binomial(75-val,14-pos)*binomial(val-1, pos)/6635869816740560

    def heuristic_1(self, card, hand, requesting_from_discard):
        scores = [0 for i in range(20)]
        for i in range(20):
            a = card
            for j in range(max(0, i - 4), i + 1):
                count = 0
                for k in range(j, min(20, j + 5)):
                    if hand[k] == a + (k - i): count += 1
                scores[i] += self.score_1(a + (j - i), j) * 2 ** count
        return (scores.index(max(scores)), max(scores))


    def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
        DataKeeper.get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves)
        i = self.heuristic_combined(self.discard, self.hand, requesting_from_discard=True)
        if i == -1: return self.request_deck()
        return self.request_discard(i)
    def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
        DataKeeper.get_deck_exchange(self,game_id, remaining_microseconds, rack, card)
        return self.heuristic_combined(card, self.hand, requesting_from_discard=False)
