from random import shuffle
from math import factorial
from proto import ProtoBot

def end(hand, opphand):
	seq = 1
	scorea = 5
	mxseqa = 0
	a = hand[0]
	for i in range(1, 20):
		b = hand[i]
		if b == a + 1: seq += 1
		elif b > a: seq = 1
		else: break
		if seq > mxseqa: mxseqa = seq
		scorea += 5
		a = b
	if scorea == 100 and mxseqa >= 5: return 1
	seq = 1
	scoreb = 5
	mxseqb = 0
	a = opphand[0]
	for i in range(1, 20):
		b = opphand[i]
		if b == a + 1: seq += 1
		elif b > a: seq = 1
		else: break
		if seq > mxseqb: mxseqb = seq
		scoreb += 5
		a = b
	if scoreb == 100 and mxseqb >= 5: return -1
	return 0
	
def score(hand, opphand):
	seq = 1
	scorea = 5
	mxseqa = 0
	a = hand[0]
	for i in range(1, 20):
		b = hand[i]
		if b == a + 1: seq += 1
		elif b > a: seq = 1
		else: break
		if seq > mxseqa: mxseqa = seq
		scorea += 5
		a = b
	seq = 1
	scoreb = 5
	mxseqb = 0
	a = opphand[0]
	for i in range(1, 20):
		b = opphand[i]
		if b == a + 1: seq += 1
		elif b > a: seq = 1
		else: break
		if seq > mxseqb: mxseqb = seq
		scoreb += 5
		a = b
	if (scorea == 100) and (scoreb == 100):
		if mxseqa >= 5: return 50
		if mxseqb >= 5: return -50
		if mxseqa >= 2:
			if mxseqb >= 2: return 10*(mxseqa-mxseqb)
			return 10*mxseqa
		if mxseqb >= 2: return -10*mxseqb
		return 0
	if scorea == 100:
		if mxseqa >= 5: return 150-scoreb
		if mxseqa >= 2: return 100 + 10*mxseqa - scoreb
		return 100 - scoreb
	if scoreb == 100:
		if mxseqb >= 5: return scorea - 150
		if mxseqb >= 2: return scorea - 100  + 10*mxseqb
		return scorea - 100
	return scorea - scoreb

def search(depth, turn, pile, hand, opphand, discard, alpha, beta):
	if depth == 0: return score(hand, opphand)
	b = end(hand, opphand)
	if b != 0: return score(hand, opphand)
	for i in range(20):
		temp = search(depth - 1, not turn, pile, opphand, hand[:i] + [discard] + hand[i+1:], hand[i], alpha, beta)
		if turn:
			if temp > alpha: alpha = temp
			if beta <= alpha: return alpha
		else:
			if temp < beta: beta = temp
			if beta <= alpha: return alpha
	for i in range(20):
		temp = search(depth - 1, not turn, pile[:-1], opphand, hand[:i] + [pile[-1]] + hand[i+1:], hand[i], alpha, beta)
		if turn:
			if temp > alpha: alpha = temp
			if beta <= alpha: return beta
		else:
			if temp < beta: beta = temp
			if beta <= alpha: return beta
	if turn: return alpha
	return beta

def dfs(depth, turn, pile_size, hand, opphand_givens, discard, removed, n):
	#Apologies for the ugly code on this and dfs_deck.
	scores = [0 for i in range(40)]
	excludeopp = [i[0] for i in opphand_givens]
	exclude = hand + excludeopp + removed
	cs = [i for i in range(80) if i not in exclude]
	for i in range(n):
		shuffle(cs)
		pile = cs[:pile_size]
		opphand = cs[pile_size+1:]
		for c in opphand_givens:
			opphand = opphand[:c[1]] + [c[0]] + opphand[c[1]+1:]
		mx = -200
		move = 0
		for i in range(20):
			a = search(depth - 1, False, pile, opphand, hand[:i] + [discard] + hand[i+1:], hand[i], -200, 200)
			scores[i] += a
		for i in range(20):
			a = search(depth - 1, not turn, pile[:-1], opphand, hand[:i] + [pile[-1]] + hand[i+1:], hand[i], -200, 200)
			scores[i+20] += a
	print(scores)
	return scores.index(max(scores))
	
def dfs_deck(depth, turn, pile_size, hand, opphand_givens, discard, removed, n, card):
	scores = [0 for i in range(20)]
	excludeopp = [i[0] for i in opphand_givens]
	exclude = hand + excludeopp + removed
	cs = [i for i in range(80) if i not in exclude]
	for i in range(n):
		shuffle(cs)
		pile = cs[:pile_size]
		opphand = cs[pile_size+1:]
		for c in opphand_givens:
			opphand = opphand[:c[1]] + [c[0]] + opphand[c[1]+1:]
		mx = -200
		move = 0
		for i in range(20):
			a = search(depth - 1, False, pile, opphand, hand[:i] + [card] + hand[i+1:], hand[i], -200, 200)
			scores[i] += a
	print(scores)
	return scores.index(max(scores))
	
class botdfs(ProtoBot):
	def __init__(self, depth, n):
		ProtoBot.__init__(self)
		self.depth = depth
		self.n = n
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
			self.opphand_givens += [(self.discard, other_player_moves["idx"])]
		self.discard = discard
		i = self.choose_move()
		if i < 20:
			return self.request_discard(i)
		return self.request_deck()
	def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
		self.pile_size -= 1
		self.removed += [self.discard]
		return self.choose_deckmove(card)
	def choose_move(self):
		return dfs(self.depth, self.turn, self.pile_size, self.hand, self.opphand_givens, self.discard, self.removed, self.n)
	def choose_deckmove(self, card):
		return dfs_deck(self.depth, self.turn, self.pile_size, self.hand, self.opphand_givens, self.discard, self.removed, self.n, card)
		
def combos(x, y):
	if x <= 0 or y <= 0: return 0
	if y > x: return 0
	return factorial(x)/(factorial(y)*factorial(x-y))

def s(x, y):
	return combos(80-x,19-y)*combos(x-1, y)/3535316142212174320

def heuristic(card, hand):
	scores = [s(card, i) - s(hand[i], i) for i in range(20)]
	if max(scores) < 0: return -1
	return scores.index(max(scores))

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
			self.opphand_givens += [(self.discard, other_player_moves["idx"])]
		self.discard = discard
		i = self.choose_move()
		if i < 20:
			return self.request_discard(i)
		return self.request_deck()
	def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
		self.pilesize -= 1
		self.removed += [discard]
		return self.choose_deckmove(card)
	def choose_move(self):
		return heuristic(self.discard, self.hand)
	def choose_deckmove(self, card):
		return heuristic(card, self.hand)
