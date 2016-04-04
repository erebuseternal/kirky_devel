from cvxopt import matrix, spmatrix, sparse
from copy import copy, deepcopy
from fractions import Fraction
from block import *

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
    interior = Block(conditions.size[1], conditions.size[1] + conditions.size[0], baseblock.vertex_pool)
    for i in range(0, conditions.size[0]):
        for vertex in baseblock.vertices:
            # first we add
            desired_position = []
            for j in range(0, len(vertex.position)):
                desired_position.append(vertex.position[j] + conditions[i,j])
            desired_vertex = baseblock.vertex_index.getElement(desired_position)
            if desired_vertex:
                edge = Edge(desired_position, copy(vertex.position), i + conditions.size[1], multiples[i])
                # I make sure they are paired to the vertices in the baseblock so
                # I do not have to join later
                edge.addVertex(vertex, False)
                edge.addVertex(desired_vertex, True)
                interior.addEdge(edge)
            # then we subtract
            desired_position = []
            for j in range(0, len(vertex.position)):
                desired_position.append(vertex.position[j] - conditions[i,j])
            desired_vertex = baseblock.vertex_index.getElement(desired_position)
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
    iden = matrix(elements, (size, size))
    return iden

def createBlockConditionRows(vertex, num_edges_in_block, conditions, multiples):
    # first we add the negative of the identity to the right of the conditions matrix
    identity = identityMatrix(conditions.size[0])
    complete_conditions = matrix([[conditions],[-1 * identity]])
    # now we need to multiply by multiples in order to get the right matrix. Remember,
    # because of the modifications we made to our conditions matrix in order to have 
    # everything be integers our S_d is now not a 'row of ones' but has multipliers
    # so we run through each of the -1's we just added and multiply them by the 
    # corresponding multiple
    for i in range(conditions.size[1], complete_conditions.size[1]):
        complete_conditions[i - conditions.size[1], i] *= multiples[i - conditions.size[1]]
    # this will be used to create our block condition row
    elements = []
    I = []
    J = []
    # now we go ahead and get our columns
    for edge_tuple in vertex.edges:
        # extract the edge and whether this is entering or exiting from the tuple
        edge = edge_tuple[1]
        head = edge_tuple[0]
        # we get the id, to know which column we are grabbing from our matrix
        vector_id = edge.vector_id
        # we get the id, so that we know what column we will be creating in the conditions
        id = edge.id
        # now we have all the info we need
        # we now need to loop through the elements in our complete conditions having to do with this vector
        for i in range(0, complete_conditions.size[0]):
            element = complete_conditions[i,vector_id]
            # we make sure we capture the orientation
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
def createBlockConditions(conditions, multiples, block, interior):
    num_edges_in_block = len(block.edges) + len(interior.edges)
    matrix_blocks = []
    for vertex in block.vertices:
        rows = createBlockConditionRows(vertex, num_edges_in_block, conditions, multiples)
        matrix_blocks.append(rows)
    # and now we join the blocks
    blockconditions = sparse(matrix_blocks)
    return blockconditions

# THIS WILL NOT BE USED!!!!!!!
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