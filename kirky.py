from copy import copy
from fractions import Fraction
from edge import Block
from vertex import VertexPool

# the following function will take a conditions
# matrix. It will then go ahead and create a base block

# conditions should be the B part of [IB] transposed and should be cvxopt matrix
def createBaseBlock(conditions, B):
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
    # now before we can start building the block, we need our vertex pool
    vertex_pool = VertexPool(B)
    # now that we have our sides and our vertex_pool we can go ahead and create our block
    block = Block(vertex_pool)
    block.num_vectors = block.dimension + B.size[1]
    # we add a single vertex which is the origin, and we will build from here
    vertex = vertex_pool.GetVertex([Fraction(0,1)] * vertex_pool.dimension)
    # we start by making the 1 sided hyper cube we will use
    for i in range(0, conditions.size[1]):
        # first we create our new vector we will be
        # adding on
        vector = [Fraction(0,1)] * conditions.size[1]
        vector[i] = Fraction(1,1)
        # now we grab the blocks vertices
        vertices = copy(block.Vertices())
        # now we shift the block by one in the ith dimension
        block.AddShift(1,i)
        # for each of the old vertices we add an edge going out from
        # them of our new type
        for vertex in vertices:
            head = []
            for j in range(0, conditions.size[1]):
                head.append(vertex.position[j] + vector[j])
            tail = copy(vertex.position)
            # now we create the edge that will go between these two positions
            edge = block.CreateEdge(head, tail,i)
            # and we attempt to add it
            block.AddEdge(edge)
    # now we shift and add on the various sides
    for i in range(0, conditions.size[1]):
        # note that we add on one less number of sides than in sides. That's
        # because by the above construction we already have one of those sides
        for j in range(1, sides[i]):
            block.AddShift(1, i)
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
    interior = Block(baseblock.vertex_pool)
    interior.num_vectors = baseblock.num_vectors
    for i in range(0, conditions.size[0]):
        for vertex in baseblock.Vertices():
            # first we add
            desired_position = []
            for j in range(0, len(vertex.position)):
                desired_position.append(vertex.position[j] + conditions[i,j])
            # now we want to see if there is a vertex at this position
            has_vertex = baseblock.vertex_pool.HasVertex(desired_position)
            if has_vertex:
                edge = interior.CreateEdge(desired_position, copy(vertex.position), i + conditions.size[1], multiples[i])
                # I now add the edge and note it will add over the same vertex pool as the base block
                interior.AddEdge(edge)
            # then we subtract
            desired_position = []
            for j in range(0, len(vertex.position)):
                desired_position.append(vertex.position[j] - conditions[i,j])
            # now we want to see if there is a vertex at this position
            has_vertex = baseblock.vertex_pool.HasVertex(desired_position)
            if has_vertex:
                edge = interior.CreateEdge(copy(vertex.position), desired_position, i + conditions.size[1], multiples[i])
                interior.AddEdge(edge)
    return interior