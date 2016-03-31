from cvxopt import matrix, spmatrix, sparse
from copy import copy, deepcopy
from fractions import Fraction

# a vertex is just a position and a collection of edges where
# we keep track of whether the edge is coming in or heading out.

class Vertex:

    def __init__(self, position):
        self.position = position
        self.edges = []

    def addEdge(self, edge, head):
        # we just add the boolean and the edge to the edges as a tuple
        self.edges.append((head,edge))

    def __str__(self):
        return '%s' % self.position

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self.position == other.position:
            return True
        else:
            return False

"""
a kirckhoff edge is essentially a head position, a tail position and
the 'name' or id of the edge based on the original matrix these
edges or vectors come from
For the sake of this program I am adding an additional piece.
To simplify the creation of edges based off of uncompleted cycles
of independent "basis" edges as one gets in my algorithm in the case
where you don't just have one edge to many 'basis edges' but many such
edges, I am going to have an edge have an additional parameter which is
exactly how many edges it is really made of (these are placed in serial
and connected by null vertices in reality, but to simplify the blocks,
the null vertices are not noted).

One should note that this simplification is okay because if our 'actual'
graph contains no such duplications in serial, we can scale everything
to get those duplications in serial
"""

class Edge:

    def __init__(self, head, tail, vector_id, num_edges=1):
        # the vector id is the index of the column that this vector was named
        # for
        self.vector_id = vector_id
        # this is the number of edges needed to complete the cycle this vector
        # is based off of (if any, remember 'basis edges' are selected by
        # the creator of the kirkhoff graph)
        self.num_edges = num_edges
        # these two methods check to make sure our head and tail are vectors
        # and then add them on
        self.head_position = head
        self.tail_position = tail
        # we create vertices by default: this is for the block stuff that will
        # come later
        self.addVertex(Vertex(self.head_position),True)
        self.addVertex(Vertex(self.tail_position),False)

        # finally we add a position so that this can be indexed by position
        self.position = head
        # this will be used later to identify edges in a block condition matrix
        self.block_id = None

    # let's you handle the whole operation right here
    def addVertex(self, vertex, head):
        if head:
            self.head_vertex = vertex
        else:
            self.tail_vertex = vertex
        vertex.addEdge(self, head)

    def __str__(self):
        return '%s%s%s' % (self.vector_id, self.head_position, self.tail_position)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self.head_position != other.head_position:
            return False
        if self.tail_position != other.tail_position:
            return False
        if self.vector_id != other.vector_id:
            return False
        return True

"""
The following class indexes objects by their position. It takes as
parameters an integer range which essentially allows you to tell
it what range on any dimension is to be considered the same value
in the indexing. It takes a start_index (base 1) which will allow
you to determine where in the position vectors the indexing should
start. And then a depth which tells you how many indexes
you should go in creating the index.

The index is created by adding elements.
And you can grab elements by position vector.
"""

class Index:

    def __init__(self, range, start_index, depth):
        self.range = range
        self.face = {}  # this is going to be our first map
        self.depth = depth  # this is used to determine how many elements
        # we should grab from each position vector in our indexing
        # these grabs will be made in order
        self.start_index = start_index  # this lets us know where to start
        # indexing in each position vector

    # this creates the key for a specific entry given the range we want
    # each key to span
    def getRange(self, entry):
        difference = entry % self.range
        start = entry - difference
        return '%s->%s' % (start, start + self.range)

    # note that we are indexing by the position property of an element
    # which is a vector
    def addElement(self, element):
        # first we get the position vector
        position = element.position
        # we get the
        current_map = self.face
        count = 1
        for i in range(self.start_index, self.start_index + self.depth):
            r = self.getRange(position[i])
            # if we have reached the end we need to grab the appropriate
            # list
            if count == self.depth:
                if not r in current_map:
                    current_map[r] = []
                current_list = current_map[r]
            # otherwise we just grab the next map as we delve deeper into the
            # index
            else:
                if not r in current_map:
                    current_map[r] = {}
                current_map = current_map[r]
            count += 1
        # now we look to see if it is in the list already
        for thing in current_list:
            if thing == element:
                return
        # if it isn't we add it to that list
        else:
            current_list.append(element)

    def getElement(self, position):
        current_map = self.face
        count = 1
        for i in range(self.start_index, self.start_index + self.depth):
            r = self.getRange(position[i])
            # if we have reached the end we need to grab the appropriate
            # list
            if count == self.depth:
                if not r in current_map:
                    return None
                current_list = current_map[r]
            # otherwise we just grab the next map as we delve deeper into the
            # index
            else:
                if not r in current_map:
                    return None
                current_map = current_map[r]
            count += 1
        # now we try to find the element with this position vector
        for element in current_list:
            if position == element.position:
                return element
        # if we didn't find anything we return None
        return None

class Block:

    def __init__(self, dimensions, num_vectors, r=2):
        self.edges = []
		self.size = [0] * dimensions 	# used with shift
        self.vertices = []
        self.vertex_index = Index(r,0,dimensions)
        self.edge_indexes = []
        for i in range(0, num_vectors):
            self.edge_indexes.append(Index(r,0,dimensions))
        # used for checking
        self.dimensions = dimensions

    # we add by edges
    # this will make sure we never replicate edges or vertices
    def addEdge(self, edge):
        head_vertex = edge.head_vertex
        tail_vertex = edge.tail_vertex
        vector_id = edge.vector_id
        index_edge = self.edge_indexes[vector_id].getElement(edge.position)
        if not index_edge:
            self.edges.append(edge)
            edge.id = len(self.edges)
            self.edge_indexes[vector_id].addElement(edge)
        else:
            return
        # we now check to see if the vertices are in our index already
        # and if so we reset the appropriate vertex on the edge
        index_vertex = self.vertex_index.getElement(head_vertex.position)
        if not index_vertex:
            self.vertices.append(head_vertex)
            self.vertex_index.addElement(head_vertex)
        else:
            edge.addVertex(index_vertex, True)
        index_vertex = self.vertex_index.getElement(tail_vertex.position)
        if not index_vertex:
            self.vertices.append(tail_vertex)
            self.vertex_index.addElement(tail_vertex)
        else:
            edge.addVertex(index_vertex, False)


    def shiftAndAdd(self, amount, dimension):
        if dimension > self.dimensions:
            raise Issue('this dimension is outside of the dimensions of this block')
        num = len(self.edges)
        for i in range(0,num):
            edge = self.edges[i]
            new_edge_head = deepcopy(edge.head_position)
            new_edge_head[dimension] += amount
            new_edge_tail = deepcopy(edge.tail_position)
            new_edge_tail[dimension] += amount
            new_edge = Edge(new_edge_head,new_edge_tail, edge.vector_id, edge.num_edges)
            self.addEdge(new_edge)
		self.size[dimension] += amount

		
			
# the following function will take a conditions
# matrix. It will then go ahead and create a base block


def createBaseBlock(conditions):
    # we need to get the max element of each column, this will
    # be the length of one dimension or side of our block
    sides = []
    for i in range(0, conditions.size[1]):
        column = conditions[:,i]
        max_elem = 0
        for element in column:
            if abs(element) > max_elem:
                max_elem = abs(element)
        sides.append(max_elem)
    # now that we have our sides we can go ahead and create our block
    block = Block(conditions.size[1], conditions.size[0] + conditions.size[1])
    # we add a single vertex which is the origin, we will build from here
    vertex = Vertex([Fraction(0,1)] * conditions.size[1])
    block.vertex_index.addElement(vertex)
    block.vertices.append(vertex)
    # we start by making the hyper cube we will use
    for i in range(0, conditions.size[1]):
        # first we create our new vector we will be
        # adding on
        vector = [Fraction(0,1)] * conditions.size[1]
        vector[i] = Fraction(1,1)
        # now we grab the blocks vertices
        vertices = copy(block.vertices)
        # now we shift the block by one in the ith dimension
        block.shiftAndAdd(1,i)
        # for each of the old vertices we add an edge going out from
        # them of our new type
        for vertex in vertices:
			head = []
			for j in range(0, conditions.size[1]):
				head.append(vertex.position[j] + vector[j])
            tail = vertex.position
            edge = Edge(head, tail,i)
            block.addEdge(edge)
    # now we shift and add on the various sides
    for i in range(0, conditions.size[1]):
        # note that we add on one less number of sides than in sides. That's
        # because by the above construction we already have one of those sides
        for j in range(1, sides[i]):
            block.shiftAndAdd(1, i)
    # now we have our basic block
    return block

def createInteriorBlock(conditions, multiples, baseblock):
    """
    For each condition, we need to loop through the vertices
    in the baseblock and add and subtract to its position, the
    position of the other side of our vector. If either exists we
    create and add the appropriate vector.

    Note none of the multiples can be negative
    """
    interior = Block(conditions.size[1], conditions.size[1] + conditions.size[0])
    for i in range(0, conditions.size[0]):
        for vertex in baseblock.vertices:
            # first we add
			desire_position = []
			for j in range(0, len(vertex.position)):
				desired_position.append(vertex.position[j] + conditions[i,j])
            desired_vertex = baseblock.vertex_index.getElement(Vertex(desired_position))
            if desired_vertex:
                edge = Edge(desired_position, copy(vertex.position), i + conditions.size[1], multiples[i])
                # I make sure they are paired to the vertices in the baseblock so
                # I do not have to join later
                edge.addVertex(vertex, False)
                edge.addVertex(desired_vertex, True)
                interior.addEdge(edge)
            # then we subtract
            desire_position = []
			for j in range(0, len(vertex.position)):
				desired_position.append(vertex.position[j] - conditions[i,j])
            desired_vertex = baseblock.vertex_index.getElement(Vertex(desired_position))
            if desired_vertex:
                edge = Edge(copy(vertex.position), desired_position, i + conditions.size[1], multiples[i])
                # I make sure they are paired to the vertices in the baseblock so
                # I do not have to join later
                edge.addVertex(vertex, True)
                edge.addVertex(desired_vertex, False)
                interior.addEdge(edge)
    return interior

"""
Just need to add the code to generate a matrix to solve from the
original matrix and a block

The first things we must be able to do is generate the cut for a vertex

What we care about in the cut is the id of each edge, the vector id, and
then whether the edge is heading in or out (id, vector_id, head)

Then we will take our conditions, join it with the negative identity
and for each vector id, bring out the column and place it at the id
position multiplied by negative one if head is True in a matrix that
has as many columns as our block has edges and as many rows as our
conditions
"""

def identityMatrix(size):
	elements = []
	for i in range(0, size):
		for j in range(0, size):
			if i == j:
				elements.append(1)
			else:
				elements.append(0)
	id = matrix(elements, (size, size))
	return id

def createBlockConditionRows(vertex, num_edges_in_block, conditions):
	# first we add the negative of the identity to the right of the conditions matrix
    identity = identityMatrix(conditions.size[0])
    complete_conditions = matrix([[conditions],[-1 * identity]])
	# this will be used to create our block condition rows
	elements = []
	I = []
	J = []
    # now we go ahead and get our columns
    for edge_tuple in vertex.edges:
		# extract the edge and whether this is entering or exiting from the tuple
        edge = edge_tuple[0]
        head = edge_tuple[1]
		# we get the id, to know which column we are grabbing from our matrix
        vector_id = edge.vector_id
		# we get the id, so that we know what column we will be creating in the conditions
        id = edge.id
        # now we have all the info we need
		# we now need to loop through the elements in our complete conditions having to do with this vector
        for i in range(0, complete_conditions.size[0])
			element = complete_conditions[i,vector_id]
			# we make sure we caputer the orientation
			if head:
				element = -1 * element
			# now we set this element and its position
			elements.append(element)
			I.append(i)
			# this is the column in the block conditions
			J.append(id)
    # now we can create our sparse matrix
	# we specify size because we are not going to get the most extreme J we can get every single time
	blockconditionrows = spmatrix(elements, I, J, (complete_conditions.size[0], num_edges_in_block))
    return blockconditionrows

# note that we only need to call this on the base block, because it contains all the vertices the interior has
# therefore when we take a cut of the base blocks vertices, we get the edges in the interior as well. base and 
# interior reference the same vertices
def createBlockConditions(conditions, block):
	num_edges_in_block = len(block.edges)
    count = 1
	matrix_blocks = []
    for vertex in block.vertices:
        rows = createBlockConditionRows(vertex, num_edges_in_block, conditions)
		matrix_blocks.append(rows)
	# and now we join the blocks
	blockconditions = sparse(matrix_blocks)
    return rows

# must be of form [IB]
# this returns B.T
def createConditions(input_matrix):
	n = input_matrix.size[1]
	m = input_matrix.size[0]
	slices = []
	# we grab the columns of B
	for i in range(m, n):
		slices.append([input_matrix[:,i]])
	# we join the columns
	new_matrix = matrix(slices)
	return new_matrix.trans()
	
				
	