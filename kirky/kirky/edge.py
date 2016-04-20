from .issue import Issue
from copy import copy

class Edge:

    def __init__(self, head, tail, vector_id, multiples=1):
        # the vector id is the index of the column that this vector was named
        # for
        self.vector_id = vector_id
        # this is the number of edges needed to complete the cycle this vector
        # is based off of (if any, remember 'basis edges' are selected by
        # the creator of the kirkhoff graph)
        self.num_edges = multiples
        # these hold the head and tail positions of the edge
        self.head_position = head
        self.tail_position = tail
        # the first entry is the one at the tail, the second is the one at the
        # head
        self.vertices = [None, None]
        # finally we add a position so that this can be indexed by position
        self.position = head
        # this will hold the weight node, which will get assigned by the block
        self.weight = None

    """
    this tries to add a vertex. If the edge is not redundant this function will 
    return True letting us know the vertex was added to the edge and visa versa
    if it was redundant, we will return false therefore indicating the edge is 
    unnecessary note that if it is redundant at the tail vertex it will be 
    redundant at the other 
    """
    def AddVertices(self, tail_vertex, head_vertex):
        if tail_vertex.position != self.tail_position or head_vertex.position != self.head_position:
            raise Issue('one or both vertices do not touch edge')
        self.vertices[0] = tail_vertex
        self.vertices[1] = head_vertex
        if tail_vertex.AddEdge(self):
            head_vertex.AddEdge(self)
            return True # this lets us know the edge was accepted
        return False # let's us know the edge was rejected

    def __str__(self):
        return 'id:%shead:%stail:%s' % (self.vector_id, self.head_position, self.tail_position)

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
the following class handles creating, adding, and tracking edges 
over a vertex pool. This allows us to keep collective state 
about the edge weights
"""
class EdgePool:
    
    def __init__(self):
        self.edge_weights = []
        self.current_id = 0
        
    # these two methods allow us to keep track of the edge weight nodes
    def AddEdgeWeight(self, weight):
        self.edge_weights.append(weight)
        weight.weight_id = self.current_id
        self.current_id += 1
    
    def RemoveEdgeWeight(self):
        self.edge_weights.pop(-1)
        self.current_id -= 1

class Block:

    def __init__(self, vertex_pool, edge_pool):
        self.vertex_pool = vertex_pool
        self.edge_pool = edge_pool
        self.edges = []
        self.dimension = self.vertex_pool.dimension
        self.num_vectors = 0

    """
    This method will attempt to add an edge. It will succeed if the edge it 
    is adding is not redundant.
    If the action succeeds then we will append this edge to self.edges
    If it does not succeed we do not just pass on but also remove the node
    that represented the edge weight both from edge_weights and from the 
    vertex pool's web
    """
    def AddEdge(self, edge):
        # note these functions will create the vertices if they do not 
        # yet exist. This is important for shift and add
        tail_vertex = self.vertex_pool.GetVertex(edge.tail_position)
        head_vertex = self.vertex_pool.GetVertex(edge.head_position)
        if edge.AddVertices(tail_vertex, head_vertex):
            # if the edge was accepted we add it to the block's list of edges
            self.edges.append(edge)
        else:
            self.edge_pool.RemoveEdgeWeight()
            self.vertex_pool.web.RemoveNode()
    
    """
    We use this to create an edge because this handles not only calling the 
    constructor for the edge, but creating a node for the edge weight and 
    registering it with edge_weights. 
    """
    def CreateEdge(self, tail_position, head_position, vector_id, num_edges=1):
        edge = Edge(tail_position, head_position, vector_id, num_edges)
        edge.weight = self.vertex_pool.web.CreateNode()
        edge.weight.kind = 'edge'
        self.edge_pool.AddEdgeWeight(edge.weight)
        return edge
        
    def Size(self):
        return self.vertex_pool.size
        
    def Vertices(self):
        return self.vertex_pool.vertices
    
    """
    This creates a copy of each edge in the block shifted by the input amount 
    in the direction of the input dimension and attempts to add each 
    into the block (creating vertices where needed through the implementation of 
    AddEdge). Thus this essentially creates a copy of the block and adds the block
    and this copy together without ever duplicating an edge (because AddEdge 
    will not add an edge if doing so we cause a duplicate)  
    """
    def AddShift(self, amount, dimension):
        if dimension > self.dimension:
            raise Issue('this dimension is outside of the dimensions of this block')
        num = len(self.edges)
        for i in range(0,num):
            edge = self.edges[i]
            new_head = copy(edge.head_position)
            new_head[dimension] += amount
            new_tail = copy(edge.tail_position)
            new_tail[dimension] += amount
            new_edge = self.CreateEdge(new_head,new_tail, edge.vector_id, edge.num_edges)
            self.AddEdge(new_edge)