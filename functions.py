# the following function will take a conditions
# matrix. It will then go ahead and create a base block
from matrix import *
from graphparts import *

def createBaseBlock(conditions):
    # we need to get the max element of each column, this will
    # be the length of one dimension or side of our block
    sides = BaseOneList()
    for i in range(1, conditions.size[1]):
        column = conditions.get(None, i)
        max_elem = 0
        for element in column:
            if abs(element) > max_elem:
                max_elem = abs(element)
        sides.append(max_elem)
    # now that we have our sides we can go ahead and create our block
    block = Block(conditions.size[1])
    # we start by making the hyper cube we will use
    for i in range(1, conditions.size[1]):
        head = createZeroBol()
        head[i] = Fraction(1,1)
        edge = Edge(i, head, createZeroBOL()[])
        block.addEdge(edge)
    # now we shift and add on the various sides
    for i in range(1, conditions.size[1]):
        for j in range(0, sides[i]):
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
    interior = Block(conditions.size[1])
    for i in range(1, conditions.size[0] + 1):
        for vertex in baseblock.vertices:
            # first we add
            desired_position = vertex.position + conditions.get(i,None)
            desired_vertex = baseblock.vertex_index.getElement(Vertex(desired_position))
            if desired_vertex:
                edge = Edge(i, desired_position, vertex.position, multiples[i])
                edge.addVertex(vertex, False)
                edge.addVertex(desired_vertex, True)
                interior.addEdge(edge)
            # then we subtract
            desired_position = vertex.position - conditions.get(i,None)
            desired_vertex = baseblock.vertex_index.getElement(Vertex(desired_position))
            if desired_vertex:
                edge = Edge(i, vertex.position, desired_position, multiples[i])
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

def createConditionRows(vertex, num_edges, condition_matrix):
    identity = identityMatrix(conditions.size[0])
    matrix = joinColumns(conditions, negateMatrix(identity))
    # this gives us our real conditions
    conditionRows = Matrix(conditions.size[0], num_edges)
    # now we go ahead and get our columns
    for edge_tuple in vertex.edges:
        edge = edge_tuple[0]
        head = edge_tuple[1]
        vector_id = edge.vector_id
        id = edge.id
        # now we have all the info we need
        column = deepcopy(condition_matrix.get(vector_id, None))
        if head:
            for i in range(1, column.length() + 1):
                column[i] = -1 * column[i]
        # now we set the column based on the id
        # note all other columns will be zeroes
        conditionsRows.setColumn(column, id)
    return conditionsRows

def createBlockConditions(block, conditions):
    identity = identityMatrix(conditions.size[0])
    condition_matrix = joinColumns(conditions, negateMatrix(identity))
    num_edges = block.edges.length()
    count = 1
    rows = None
    for vertex in block.vertices:
        old_rows = rows
        rows = createConditionRows(vertex, num_edges, condition_matrix)
        if count > 1:
            rows = joinRows(old_rows, rows)
        count += 1
    return rows
