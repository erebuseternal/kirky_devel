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

    def __init__(self, vector_id, head, tail):
        self.vector_id = vector_id
        self.addHead(head)
        self.addTail(tail)
        self.head_vertex = None
        self.tail_vertex = None

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
