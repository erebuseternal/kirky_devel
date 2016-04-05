# Note we will add id's to edges later using an edge -> vertex map
# note we need to make the vertices and edges hashable
# position vectors should be BaseOneLists

from matrix import *

from copy import deepcopy

class Vertex:

    def __init__(self, position):
        # position is a vector
        if not isinstance(position, BaseOneList):
            raise Issue('position vector is not a BaseOneList')
        self.position = position
        self.edges = BaseOneList()

    def addEdge(self, edge, head):
        # we just add the boolean and the edge to the edges as a tuple
        self.edges.append((head,edge))

    def __hash__(self):
        return hash('%s' % self.position)

    def __eq__(self, other):
        if self.position == other.position:
            return True
        else:
            return False


class Edge:

    def __init__(self, vector_id, head, tail, num_edges=1):
        self.vector_id = vector_id
        self.addHead(head)
        self.addTail(tail)
        self.head_vertex = Vertex(self.head_position)
        self.tail_vertex = Vertex(self.tail_position)
        self.num_edges = num_edges
        self.position = self.head_position
        self.id = None

    def addHead(self, position):
        if not isinstance(position, BaseOneList):
            raise Issue('position vector is not a BaseOneList')
        self.head_position = position

    def addTail(self, position):
        if not isinstance(position, BaseOneList):
            raise Issue('position vector is not a BaseOneList')
        self.tail_position = position

    # let's you handle the whole operation right here
    def addVertex(self, vertex, head):
        if head:
            self.head_vertex = vertex
        else:
            self.tail_vertex = vertex
        vertex.addEdge(self, head)

    def __hash__(self):
        return hash('%s%s%s' % (self.vector_id, self.head_position, self.tail_position))

    def __eq__(self, other):
        if self.head_position != other.head_position:
            return False
        if self.tail_position != other.tail_position:
            return False
        if self.vector_id != other.vector_id:
            return False
        return True

"""
This class is intended to be used to index the vertices in a space.
We are going to assume that those points are just index one vectors
having integer entries.

We will set this as having a particular range. Then when a vector
comes in we can throw it against the first map to find all matches
for its first entry, the second map for its second and so on.

We will update the index only when we add a vertex
"""

# this object is used for creating the ranges of index
class Range:

    def __init__(self, start, range):
        self.start = start
        self.range = range

    def hash(self):
        return hash('%s->%s' % (self.start, self.start + self.range))

class Index:

    def __init__(self, range):
        self.range = range
        self.face = {}  # this is going to be our first map

    def getRange(self, entry):
        difference = entry % self.range
        start = entry - difference
        return Range(start, self.range)

    def addElement(self, element):
        # first we get the vertex's position vector
        position = element.position
        current_map = self.face
        count = 1
        for entry in position:
            r = self.getRange(entry)
            if count == position.length():
                if not r in current_map:
                    current_map[r] = []
                current_list = current_map[r]
            else:
                if not r in current_map:
                    current_map[r] = {}
                current_map = current_map[r]
            count += 1
        if element in current_list:
            return
        else:
            current_list.append(element)

    def getElement(self, position):
        for entry in position:
            r = self.getRange(entry)
            if count == position.length():
                if not r in current_map:
                    return None
                current_list = current_map[r]
            else:
                if not r in current_map:
                    return None
                current_map = current_map[r]
            count += 1
        for element in current_list:
            if position == element.position:
                return element
        return None

# this is a series of edges and vertices.
# it allows for the block to be easily be
# moved along any direction and return a new
# block
# it also allows for easy joining of two
# blocks

def Block:

    def __init__(self, dimensions, range=2):
        self.edges = []
        self.vertices = []
        self.vertex_index = Index(range)
        self.edge_indexes = BaseOneList()
        for i in range(1, dimensions + 1):
            self.edge_indexes.append(Index(range))
        # used for checking
        self.dimensions = dimensions

    # we add by edges
    # this will make sure we never replicate edges or vertices
    def addEdge(self, edge):
        head_vertex = edge.head_vertex
        tail_vertex = edge.tail_vertex
        vector_id = edge.vector_id
        index_edge = self.edge_indexes[vector_id].getElement(edge)
        if not index_edge:
            self.edges.append(edge)
            edge.id = self.edges.length()
            self.edge_indexes[vector_id].addElement(edge)
        else:
            edge = index_edge
        # we now check to see if the vertices are in our index already
        # and if so we reset the appropriate vertex on the edge
        index_vertex = self.vertex_index.getElement(head_vertex)
        if not index_vertex:
            self.vertices.append(head_vertex)
            self.vertex_index.addElement(head_vertex)
        else:
            edge.addVertex(index_vertex, True)
        index_vertex = self.vertex_index.getElement(tail_vertex)
        if not index_vertex:
            self.vertices.append(tail_vertex)
            self.vertex_index.addElement(tail_vertex)
        else:
            edge.addVertex(index_vertex, False)


    def shiftAndAdd(self, amount, dimension):
        if dimension > self.dimensions:
            raise Issue('this dimension is outside of the dimensions of this block')
        for edge in self.edges:
            new_edge = deepcopy(edge)
            new_edge.head_position[dimension] += amount
            new_edge.tail_position[dimension] += amount
            self.addEdge(new_edge)

    def ingest(self, block):
        for edge in block.edges:
            self.addEdge(edge)
