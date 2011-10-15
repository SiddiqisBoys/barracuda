from math import factorial
from datakeeper import DataKeeper

def binomial(x, y):
    if y == 0: return 1
    if x <= 0 or y < 0: return 0
    if y > x: return 0
    return factorial(x)/(factorial(y)*factorial(x-y))

class HeuristicBot(DataKeeper):
    def __init__(self,weights=[1,1]):
        DataKeeper.__init__(self)

    def heuristic_combined(self, card, hand, requesting_from_discard):
        if self.turn_number<=15:
            # Do not build a racko until later on in the game
            scores = [self.score_0(card, i) - self.score_0(hand[i], i) for i in range(20)]
            if requesting_from_discard and max(scores) < 0: return -1
            return scores.index(max(scores))


        ##Look at every set of five points, indexed by the first point

        # Assign a score
        scores = [0 for i in range(15)]
        for i in range(15):
            # Find the largest subsequence who are correct in order
            # The protected includes only the elements that are in order
            # Pro is a 5xn matrix - for each j, which k are in order
            # with j
            pro = []

            # Compare elements pairwise
            for j in range(5):
                v = []
                for k in range(5):
                    # Append points that are part of the order to v
                    if hand[i+k] == hand[i+j] + k - j: v += [i + k]
                #Append v to pro
                pro += [v]

            # Pick the one with the maximum length
            lenpro = [len(v) for v in pro]
            pro = pro[4-lenpro[::-1].index(max(lenpro))]

            # Score the racko (based on the number of rackos containing the protected points)
            for j in range(max(0, max(pro) - 4), min(15, min(pro) + 5)):
                scores[i] += self.score_1(hand[j], j)
            # For the elements we don't have, divide by the prob.
            # of getting both
            # Extra factor to shift the distribution to the right
            scores[i] *= 80 ** len(pro) * (i+1)**2
        #end for

        # Take the largest score, from the back first
        a = 14 - scores[::-1].index(max(scores))

        # Initialize the protected list - similar to "pro" above
        # Protected list contains only elements that are part of the
        # racko
        protected = []
        for j in range(5):
            v = []
            for k in range(5):
                if hand[a+k] == hand[a+j] + k - j: v += [a + k]
            protected += [v]
        lenpro = [len(v) for v in protected]
        protected = protected[lenpro[::-1].index(max(lenpro))]

        # Domain of swap index-values
        swap_domain = []

        # If already have a racko
        if len(protected)==5:
            pass
        else:
            # The domain of index-values that can form part of our racko
            racko_domain = range(max(0, max(protected) - 4), min(20, min(protected) + 5))

            # The element at the start of the racko sequence
            racko_start = hand[a]

            # The element at the end of the racko sequence
            racko_end = protected[-1]

            # List of cards to look for to place into the racko
            scan_for = []

            internal_swap = []
            left_swap = []
            for j in racko_domain:
                if j not in protected:
                    scan_for += [racko_start + j - a]
                    if j>racko_start:
                        if j>racko_end:
                            left_swap += [j]
                        else:
                            internal_swap += [j]
            swap_domain=left_swap+internal_swap

            # If card is in scan_for, it return the index you want
            # to put it in
            if card in scan_for: return card + a - racko_start

        # Give a score to every non-protected card
        scores = [self.score_0(card, i) - self.score_0(hand[i], i) for i in range(20) if i not in protected]
        # If scores are negative, draw from the deck
        if requesting_from_discard and max(scores) < 0:
            # Try the deck
            return -1
        elif not requesting_from_discard and max(scores) < 0:
            # Need to put it somewhere... try the swap
            if swap_domain!=[]:
                return swap_domain[-1]

        # Otherwise pick the highest of the scores
        return [i for i in range(20) if i not in protected][scores.index(max(scores))]

    def score_0(self,val, pos):
        #live_before=self.live_cards_between(-1,val)
        #live_after=self.live_cards_between(val,80+1)
        live_before = val - 1
        live_after = 80 - val
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
        return self.deck_exchange(self.heuristic_combined(card, self.hand, requesting_from_discard=False))



class HeuristicBotOld(DataKeeper):
    """Test bot"""
    def __init__(self):
        DataKeeper.__init__(self)

    def score_0(self,val, pos):
        #live_before=self.live_cards_between(-1,val)
        #live_after=self.live_cards_between(val,80+1)
        live_before = val - 1
        live_after = 80 - val
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
        return self.deck_exchange(self.heuristic_0(card, self.hand, requesting_from_discard=False))
