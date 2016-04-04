from cvxopt import matrix
from kirky import *
from kirky_linsolve import nullspace

def trysolution(conditions, multiples, block, interior):
	b_c = createBlockConditions(conditions, multiples, block, interior))
	# now we check to see if it not over determines
	if b_c.size[0] <= b_c.size[1]:
		# now we try get the null space
		ns = nullspace(b_c)
		# we check to make sure we actually got something
		if ns.size[0] == 0 or ns.size[1] == 0:
			# if we didn't we return false and none
			return False, None
		else:
			# we return the first column
			return True, ns[:,0]
	return False, None

# conditions is the B.T scaled so that there are no fractions, multiples is the multiples of dependent vectors 
# based on the scaling for conditions
# this function returns the weightings for the edges by in a column vector 
# where the row index refers to the id of the edge in our block and interior
# it also returns the base and interior blocks
def solve(conditions, multiples, num=None):
	base = createBaseBlock(conditions)
	# next we create our interior
	interior = createInteriorBlock(conditions, multiples, base)
	# now we try our solution tuple
	solution_tuple = trysolution(conditions, multiples, base, interior)
	if solution_tuple[0]:
		return solution_tuple[1], base, interior
	count = 1
	while True:
		if num:
			if count > num:
				return None, None, None
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
			solution_tuple = trysolution(conditions, multiples, base, interior)
			if solution_tuple[0]:
				return solution_tuple[1], base, interior
			count += 1

# this converts our weights and vectors cuts to an incidence matrix
def getIncidenceMatrix(weights, block):
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


			
			
	