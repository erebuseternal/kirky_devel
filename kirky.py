from matrix import *
from copy import deepcopy

# a vertex is just a position and a collection of edges where
# we keep track of whether the edge is coming in or heading out.

class Vertex:

    def __init__(self, position):
        # position is a vector
        if not isinstance(position, Vector):
            raise Issue('position vector is not a Vector')
        self.position = position
        self.edges = Vector()

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
        self.addHead(head)
        self.addTail(tail)
        # we create vertices by default: this is for the block stuff that will
        # come later
        self.addVertex(Vertex(self.head_position),True)
        self.addVertex(Vertex(self.tail_position),False)

        # finally we add a position so that this can be indexed by position
        self.position = head
        # this will be used later to identify edges in a block condition matrix
        self.block_id = None

    def addHead(self, position):
        if not isinstance(position, Vector):
            raise Issue('position vector is not a Vector')
        self.head_position = position

    def addTail(self, position):
        if not isinstance(position, Vector):
            raise Issue('position vector is not a Vector')
        self.tail_position = position

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

    def __init__(self, dimensions, num_edges, r=2):
        self.edges = []
        self.vertices = []
        self.vertex_index = Index(r,1,dimensions)
        self.edge_indexes = Vector()
        for i in range(1, num_edges + 1):
            self.edge_indexes.append(Index(r,1,dimensions))
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
            edge = index_edge
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
            new_edge = Edge(edge.head_position, edge.tail_position, edge.vector_id, edge.num_edges)
            new_edge.head_position[dimension] += amount
            new_edge.tail_position[dimension] += amount
            self.addEdge(new_edge)

    def ingest(self, block):
        for edge in block.edges:
            self.addEdge(edge)
