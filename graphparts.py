# Note we will add id's to edges later using an edge -> vertex map
# note we need to make the vertices and edges hashable
# position vectors should be BaseOneLists

from matrix import *

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

    def __init__(self, vector_id, head, tail, num_edges=0):
        self.vector_id = vector_id
        self.addHead(head)
        self.addTail(tail)
        self.head_vertex = None
        self.tail_vertex = None
        self.num_edges = num_edges

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

    def addVertex(self, vertex):
        # first we get the vertex's position vector
        position = vertex.position
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
        if vertex in current_list:
            return
        else:
            current_list.append(vertex)

    def getVertex(self, position):
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
        for vertex in current_list:
            if position == vertex.position:
                return vertex
        return None
