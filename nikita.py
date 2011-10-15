from math import factorial
from cards import DataKeeper

def binomial(x, y):
    if y == 0: return 1
    if x <= 0 or y < 0: return 0
    if y > x: return 0
    return factorial(x)/(factorial(y)*factorial(x-y))

class DeadCardsBot(DataKeeper):
    def calc_score(self,val, pos):
        live_before=self.live_cards_between(0,val)
        live_after=self.live_cards_between(val,80+1)
        return binomial(live_before,pos)*binomial(live_after,19-pos)/binomial(live_before+live_after,19)

    def heuristic(self, card, hand, requesting_from_discard):
        scores = [self.calc_score(card, i) - self.calc_score(hand[i], i) for i in range(20)]
        if requesting_from_discard and max(scores) < 0: return -1
        return scores.index(max(scores))

    def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
        DataKeeper.get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves)
        i = self.heuristic(self.discard, self.hand, requesting_from_discard=True)
        if i == -1: return self.request_deck()
        return self.request_discard(i)
    def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
        DataKeeper.get_deck_exchange(self,game_id, remaining_microseconds, rack, card)
        return self.heuristic(card, self.hand, requesting_from_discard=False)
