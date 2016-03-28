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
"""
