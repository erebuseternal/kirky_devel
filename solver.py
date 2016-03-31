from cvxopt import matrix
from l1 import l1
# conditions is the B.T scaled so that there are no fractions, multiples is the multiples of dependent vectors 
# based on the scaling for conditions
def solve(conditions, multiples):
	base = createBaseBlock(conditions)
	# next we create our interior
	interior = createInteriorBlock(conditions, multiples, base)
	tuple = trysolution(conditions, base)
		if tuple[0]:
			return tuple[1]
	while True:
		if started:
			for i in range(0, len(base.size)):
				size = base.size[i]
				# we first shift the block itself
				base.shiftAndAdd(size, i)
				# now we shift the interior
				for j in range(0, size):
					"""
					I NEED A VERTEX POOL SO I CAN KEEP THESE THINGS SEPARATE...
					"""
				
		
		
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
	