def end(hand, opphand):
	seq = 1
	wina = False
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
	winb = False
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
	wina = False
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
	winb = False
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
