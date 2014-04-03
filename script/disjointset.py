class DisjointNode:
	def __init__(self,node,rank):
		self.parent = self
		self.rank = rank
		self.node = node

	def __eq__ (self,other):
		return self.node == other.node

def make_set(x):
	return DisjointNode(x,0)

def find(x):
	if x.parent != x:
		x.parent = find(x.parent)
	return x.parent

def union(x,y):
	xRoot = find(x)
	yRoot = find(y)

	# X and Y are not already in same set, merge them.
	if xRoot.rank < yRoot.rank:
		xRoot.parent = yRoot
	elif xRoot.rank > yRoot.rank:
		yRoot.parent = xRoot
	else:
		yRoot.parent = xRoot
		xRoot.rank += 1

