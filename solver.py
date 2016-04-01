from cvxopt import matrix
from l1 import l1
from kirky import *
# conditions is the B.T scaled so that there are no fractions, multiples is the multiples of dependent vectors 
# based on the scaling for conditions
def solve(conditions, multiples, num=None):
	base = createBaseBlock(conditions)
	# next we create our interior
	interior = createInteriorBlock(conditions, multiples, base)
	# now we try our solution tuple
	solution_tuple = trysolution(conditions, base)
	if solution_tuple[0]:
		return solution_tuple[1]
	count = 1
	while True:
		if num:
			if count > num:
				return
		for i in range(0, len(base.size)):
			size = base.size[i]
			# we first shift the block itself
			base.shiftAndAdd(size, i)
			# now we shift the interior
			shifts = []
			# we create our shifts
			for j in range(1, size + 1):
				shifts.append(interior.shift(j, i))
			# then the shifts are ingested
			for shift in shifts:
				interior.ingest(shift)
			# and now we try for a solution
			solution_tuple = trysolution(conditions, base)
			if solution_tuple[0]:
				return solution_tuple[1]
			count += 1
				
		
		
def trysolution(conditions, block):
	b_c = createBlockConditions(conditions, block)
	# now we check to see if it not over determines
	if b_c.size[0] <= b_c.size[1]:
		# we try for a solution
		b = matrix(0, (b_c.size[0],1))
		x = l1(b_c, b)
		for element in x:
			if element > 1:
				return True, x
	return False, None

def convertWeights(weights, block):
	row = 0
	elements = []
	I = []
	J = []
	for vertex in block.vertices:
		for edge_tuple in vertex:
			edge = edge_tuple[0]
			head = edge_tuple[1]
			vector_id = edge.vector_id
			id = edge.id
			element = weights[id]
			if head:
				element *= -1
			elements.append(element)
			I.append(row)
			J.append(vector_id)
		row += 1
	m = matrix(elements,I,J)
	return m
			
			
	