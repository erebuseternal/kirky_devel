from .vertex import VertexPool
from .edge import Block, EdgePool
from fractions import Fraction
from copy import copy

"""
This function takes the conditions generated from scaling B^T so that it has all
integer entries and B itself and generates the corresponding baseblock for them.

It does so by first finding the max element in each column of the conditions.
This determines the width of the block along each dimension. For example, the max
element in the first column determines the width of the block in the first dimension.

Then we create an edge pool, a vertex pool, and with these a block. We then create
a vertex a the origin. 

Next we create a unit cube of dimension equal to the number of rows of B by performing 
the following iteration dimension times starting with that vertex at the origin:
    create a copy the block so far one unit away from its 
    current position in the direction of the current dimension.
    join every vertex in the copied block with its corresponding vertex in the
    'old' using an edge of length one in the direction of the dimension. this 
    edge corresponds to the vector numbered by the current dimension.
    Increment the dimension and repeat.
    
With that done we have created our basic cube. Now in order to finish our block
we just shift and add along each dimension by one a number of times equal to the 
max found in the corresponding column.

Then we are done and return the block!  
"""
def createBaseBlock(conditions, B):
    # we need to get the max element of each column, this will
    # be the length of one dimension or side of our block
    sides = []
    for i in range(0, conditions.shape[1]):
        column = conditions[:,i]
        max_elem = 0
        for element in column:
            if abs(element) > max_elem:
                max_elem = abs(element)
        sides.append(max_elem)
    # now before we can start building the block, we need our vertex pool
    vertex_pool = VertexPool(B)
    edge_pool = EdgePool()
    # now that we have our sides and our vertex_pool we can go ahead and create our block
    block = Block(vertex_pool, edge_pool)
    block.num_vectors = block.dimension + B.shape[1]
    # we add a single vertex which is the origin, and we will build from here
    vertex = vertex_pool.GetVertex([Fraction(0,1)] * vertex_pool.dimension)
    # we start by making the 1 sided hyper cube we will use
    for i in range(0, conditions.shape[1]):
        # first we create our new vector we will be
        # adding onto each vertex's position
        vector = [Fraction(0,1)] * conditions.shape[1]
        vector[i] = Fraction(1,1)
        # now we grab the blocks vertices so we can run through only the 'old'
        # ones after we've added the new
        vertices = copy(block.Vertices())
        # now we shift the block by one in the ith dimension
        block.AddShift(1,i)
        # for each of the old vertices we add an edge going out from
        # them of our new type
        for vertex in vertices:
            # we create the new head position
            head = []
            for j in range(0, conditions.shape[1]):
                head.append(vertex.position[j] + vector[j])
            tail = copy(vertex.position)
            # now we create the edge that will go between these two positions
            edge = block.CreateEdge(head, tail,i)
            # and we attempt to add it
            block.AddEdge(edge)
    # now we shift and add on the various sides
    for i in range(0, conditions.shape[1]):
        # note that we add on one less number of sides than in sides. That's
        # because by the above construction we already have one of those sides
        for j in range(1, sides[i]):
            block.AddShift(1, i)
    # now we have our basic block
    return block

"""
The interior block will contain all of the dependent vectors - the ones corresponding 
to the columns of B. Now we know that for each such vector the corresponding 
multiple of them (gotten from the scaling of B^T to get the conditions matrix)
is equal to the dot product of the corresponding row of conditions and the column
vector of independent vectors. But each of the independent vectors is just 1 
along a specific dimension. Therefore the dot product between the two is computable
and extremely easy to compute. 

So all we do to create the interior is run through the dependent vectors and for
each do the following:
    run through all of the vertices in the baseblock
        for each vertex add the vector obtained in above manner to its position
        and check to see if there is a vertex at this new position. If there is
        add the edge between them.
        do the same but subtract instead of add.
        
And that's it, we return the resulting block.

NOTE: the vertex and edge pools of the interior and exterior are the same.
"""
def createInteriorBlock(conditions, multiples, baseblock):
    interior = Block(baseblock.vertex_pool, baseblock.edge_pool)
    interior.num_vectors = baseblock.num_vectors
    for i in range(0, conditions.shape[0]):
        for vertex in baseblock.Vertices():
            # first we add
            desired_position = []
            for j in range(0, len(vertex.position)):
                desired_position.append(vertex.position[j] + conditions[i,j])
            # now we want to see if there is a vertex at this position
            has_vertex = baseblock.vertex_pool.HasVertex(desired_position)
            if has_vertex:
                edge = interior.CreateEdge(desired_position, copy(vertex.position), i + conditions.shape[1], multiples[i])
                # I now add the edge and note it will add over the same vertex pool as the base block
                interior.AddEdge(edge)
            # then we subtract
            desired_position = []
            for j in range(0, len(vertex.position)):
                desired_position.append(vertex.position[j] - conditions[i,j])
            # now we want to see if there is a vertex at this position
            has_vertex = baseblock.vertex_pool.HasVertex(desired_position)
            if has_vertex:
                edge = interior.CreateEdge(copy(vertex.position), desired_position, i + conditions.shape[1], multiples[i])
                interior.AddEdge(edge)
    return interior