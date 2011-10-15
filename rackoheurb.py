from proto import ProtoBot
from math import factorial
from random import shuffle

def combos(x, y):
	if x <= 0 or y <= 0: return 0
	if y > x: return 0
	return factorial(x)/(factorial(y)*factorial(x-y))

def s(x, y):
    return combos(80-x,19-y)*combos(x-1, y)/3535316142212174320

def heuristica(card, hand, switch=True):
	scores = [s(card, i) - s(hand[i], i) for i in range(20)]
	if switch and max(scores) < 0: return (-1, 1)
	return (scores.index(max(scores)), max(scores))

class bot_heur(ProtoBot):
	def start_game(self, game_id, player_id, initial_discard, other_player_id):
		if player_id == 1: self.turn = True
		else: self.turn = False
		self.discard = initial_discard
		self.pile_size = 39
		self.opphand_givens = []
		self.removed = []
	def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
		self.hand = rack
		if len(other_player_moves) == 0:
			pass
		elif other_player_moves[-1]["move"] == "take_deck":
			self.pile_size -= 1
			self.removed += [discard]
		elif other_player_moves[-1]["move"] == "take_discard":
			self.opphand_givens += [(self.discard, other_player_moves[-1]["idx"])]
		self.discard = discard
		i = self.choose_move()
		if i == -1: return self.request_deck()
		return self.request_discard(i)
	def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
		self.pile_size -= 1
		self.removed += [discard]
		return self.choose_deckmove(card)
	def choose_move(self):
		return heuristica(self.discard, self.hand)[0]
	def choose_deckmove(self, card):
		return heuristica(card, self.hand, False)[0]

def sb(x, y):
    return combos(75-x,14-y)*combos(x-1, y)/6635869816740560

def heuristicb(card, hand, switch=True):
	scores = [0 for i in range(20)]
	for i in range(20):
		a = card
		for j in range(max(0, i - 4), i + 1):
			count = 0
			for k in range(j, min(20, j + 5)):
				if hand[k] == a + (k - i): count += 1
			scores[i] += sb(a + (j - i), j) * 2 ** count
	return (scores.index(max(scores)), max(scores))

def heuristicc(card, hand, alpha, beta, switch=True):
	ha = heuristica(card, hand)
	hb = heuristicb(card, hand)
	if alpha*ha[1] > beta*hb[1]: return ha[0]
	return hb[0]
