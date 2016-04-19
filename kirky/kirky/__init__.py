from copy import copy
from fractions import Fraction
from .edge import Block, EdgePool
from .vertex import VertexPool
from pyx import canvas
from .draw import DrawBlock
from time import clock
from .issue import Issue
from sympy import Matrix

# the following function will take a conditions
# matrix. It will then go ahead and create a base block

# conditions should be the B part of [IB] transposed and should be sympy matrix
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
        # adding on
        vector = [Fraction(0,1)] * conditions.shape[1]
        vector[i] = Fraction(1,1)
        # now we grab the blocks vertices
        vertices = copy(block.Vertices())
        # now we shift the block by one in the ith dimension
        block.AddShift(1,i)
        # for each of the old vertices we add an edge going out from
        # them of our new type
        for vertex in vertices:
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

def createInteriorBlock(conditions, multiples, baseblock):
    """
    For each condition, we need to loop through the vertices
    in the baseblock and add and subtract to its position, the
    position of the other side of our vector. If either exists we
    create and add the appropriate vector.

    Note none of the multiples can be negative
    """
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

class Kirchhoff:
    def __init__(self, B, conditions, multiples, min_vectors):
        self.block = createBaseBlock(conditions, B)
        self.web = self.block.vertex_pool.web
        self.interior = createInteriorBlock(conditions, multiples, self.block)
        self.min_vectors = min_vectors
        self.dimension = self.block.dimension
        # each entry will take the last number of zero locks
        self.independents = []
        # stuff to do with solutions
        self.solution = None
        self.incidence_matrix = None
        
    # this function will cause a replication along a specific dimension 
    # such as to duplicate along that direction
    def Grow(self, dimension):
        # this simply shift and adds the block in the dimension specified by its 
        # current size by an amount which is the size of the block in that dimension
        # currently.
        # it then shift and adds the interior in that dimension an amount one 
        # the original block size mentioned above number of times
        print('-->growing along dimension %s' % dimension)
        start = clock()
        self.Unlock()
        # first we grab how far we are going to have to shift
        amount = int(self.block.Size()[dimension])
        # now we shift the block by that amount
        self.block.AddShift(amount, dimension)
        # now we do the incremental shift and add for the interior
        for i in range(0, amount):
            self.interior.AddShift(1, dimension)
        # and that's it!
        end = clock()
        print('-->grew along dimension %s in %s seconds' % (dimension, (end-start)))
        
    def Unlock(self):
        self.web.Unlock()
    
    """
    when generating our linear system we consider the relations on the 
    cut itself and any edges underneath each portion of each vertex cut.
    Note that we do not consider whether there are no edges underneath 
    an entry in a vertex cut. What this means is that our linear system
    could solve in such a way that the portion of the cut with no incident
    edges could be non-zero. Obviously, this should be impossible, so 
    here we are going to lock such entries in vertex cuts to zero. By
    doing so we ensure that they cannot be non-zero in the solution of 
    our system as this lock will be incorporated into the system we are 
    going to solve. 
    
    This needs to be called each time before we attempt to generate the linear
    system corresponding to a block.
    
    It needs to be undone by Unlock() each time we grow our block
    """   
    def LockZeroes(self):
        print('-->locking zeroes')
        start = clock()
        for vertex in self.block.Vertices():
            for i in range(0, len(vertex.edges)):
                # we check to see if there is no edge of this type entering or 
                # exiting and attempt a lock if that is true
                if not vertex.edges[i][0] and not vertex.edges[i][1]:
                    if not vertex.cut[i].lock:
                        self.web.Lock(vertex.cut[i], Fraction(0,1))
                    else:
                        pass
        end = clock()
        print('-->zeroes locked in %s seconds' % (end - start))
    
    """
    Once we have obtained a non-trivial null space for a specific block-size
    we are going to want to lock the values we have found into the block so
    that we can obtain our Kirchhoff Graph.
    
    The thing is that we may have more than one null space vector in our null
    space. Therefore we have to make a selection - this is the meaning of the 
    nullspace_vector_index. Whatever number you supply there will be the vector
    chose (and it's all in base 0 of course). It defaults to 0, but if, for 
    example you choose to enter 1 you will get the second vector if it exists.
    If it doesn't exist get prepared for an error.
    
    Once a vector has been chosen, this method just runs through the edge weights
    locking each one to its solution in the vector. And remember, because 
    we based the order of the solution off of the order of the edge weights
    in the edge pool this is pretty easy.
    """
    def LockSolution(self, nullspace_vector_index=0):
        print('-->locking solution')
        start = clock()
        nullspace_vector = self.solution[nullspace_vector_index]
        for i in range(0, len(self.block.edge_pool.edge_weights)):
            node = self.block.edge_pool.edge_weights[i]
            value = nullspace_vector[i,0]
            if not node.lock:
                self.web.Lock(node,value)
        end = clock()
        print('-->solution locked in %s seconds' % (end - start))

    def GenerateLinearSystem(self):
        print('-->generating linear system')
        start = clock()
        """
		We know for a fact that our nodes split into two different kinds:
			edges and vertex cut entries
		we also know that except for cuts with absolutely no entries that each cut 
		is 'determined' by the edges that enter into it. Therefore we need only solve
		for the edges as they contain all of the information about our final solution.
		In order to get only edges in our final solution we will do the following.
		When looping through our nodes like in the normal generate linear system function
		whenever we encounter a cut-node we 'replace' it with the edges that comprise this.
		That is, instead of placing its multiple where its id should go, we instead 
		for each of its corresponding edges, we enter the edges multiplier times the 
		multiplier of the node at the id of the edge (the weight id). Then for parent 
		groups that are comprised of edges, unless the node is locked (in which case 
		it is locked to zero and we place each edge weight's multipler at its id) we 
		skip (this reduces the number of contraints). And that is how we generate the 
		linear system only concerning edges.
		"""
        # first we need to generate the matrix that will hold our system
        # to do this we need the number of rows and the length of each row
        num_rows = self.FindNumRows()
        num_edges = len(self.block.edge_pool.edge_weights) # this is the length of each row
        matrix = Matrix(num_rows, num_edges, [0]*(num_rows * num_edges))
        # now that we have generated the matrix we need to add in the non-zero
        # parts of each row. We will do this by looping through the vertices 
        # and for every lock to zero or parent group updating a new row. We will
        # keep track of the row we are on with the following counter
        row = 0
        for node in self.web.nodes:
            edge_parents = self.getEdgeParents(node)
            if node.lock and node.kind == 'vertex':
                if edge_parents[1] or edge_parents[0]:
                    for edge_tuple in edge_parents:
                        if edge_tuple:
                            weight = edge_tuple[0]
                            multiplier = edge_tuple[1]
                            matrix[row, weight.weight_id] += multiplier
                    row += 1
            for key in node.parent_groups:
                # now we check to make sure this isn't a edge_weight parent group
                # because if it is we have already dealt with it
                if node.parent_groups[key][0][0].kind == 'edge':
                        continue
                # now we deal with a parent group with parents of the 'vertex' kind 
                for parent_tuple in node.parent_groups[key]:
                    # now for each of these we need to replace them by their 
                    # edge parents
                    parent = parent_tuple[0]
                    parent_multiplier = parent_tuple[1]
                    # now we get the edges to replace it
                    parent_edge_parents = self.getEdgeParents(parent)
                    # we now enter the edge weight info into our matrix
                    for edge_tuple in parent_edge_parents:
                        if edge_tuple:
                            weight = edge_tuple[0]
                            multiplier = edge_tuple[1]
                            matrix[row, weight.weight_id] += multiplier * parent_multiplier
                    # finally we add in this node's parents with a minus 1 affixed to 
                    # each of their multipliers
                    for edge_tuple in edge_parents:
                        if edge_tuple:
                            weight = edge_tuple[0]
                            multiplier = edge_tuple[1]
                            matrix[row, weight.weight_id] += multiplier * -1
                # we increment because now we are done with that row
                row += 1
        end = clock()
        print('-->generated linear system of size (%s, %s) in %s seconds' % (matrix.shape[0], matrix.shape[1], (end-start)))
        return matrix  
    
    def getEdgeParents(self, node):
        # this gets the edge_weights that form the parent group of a node 
        # returns a two list, with edge or None in each entry
        parents = [None, None]
        index = 0
        for key in node.parent_groups:
            # we check to see if this key represents an edge parent group
            if not node.parent_groups[key][0][0].kind == 'edge':
                continue
            # okay we now know that this is the parent group with edges
            for parent_tuple in node.parent_groups[key]:
                edge_weight = parent_tuple[0]
                multiplier = parent_tuple[1]
                if index > 1:
                    break
                parents[index] = (edge_weight, multiplier)
                index += 1
            break
        return parents
    
    def FindNumRows(self):
        count = 0
        for node in self.web.nodes:
            edge_parents = self.getEdgeParents(node)
            if node.lock:
                if edge_parents[1] or edge_parents[0]:
                    count += 1
            # we skip things that are strictly edges
            for key in node.parent_groups:
                # now we check to make sure this isn't a edge_weight parent group
                if node.parent_groups[key][0][0].kind == 'edge':
                        continue
                count += 1
        return count
    
    def Solve(self):
        # here we make a call to generate the linear system the we try to solve 
        # for its nullspace. We set whatever solution we find to self.solution. For Sympy
        # if there is no solution what we return will be an empty list. So 
        # you can check for that
        M = self.GenerateLinearSystem()
        print('-->looking for nullspace')
        start = clock()
        solution = M.nullspace()
        end = clock()
        print('-->nullspace found in %s seconds' % (end - start))
        self.solution = solution
                
    def Draw(self, file):
        # this simply creates a canvas, draws the interior and exterior and 
        # then exports it as a PDF
        c = canvas.canvas()
        DrawBlock(self.block, c)
        DrawBlock(self.interior, c)
        c.writePDFfile(file)
        
    def GetIncidenceMatrix(self):
        print('-->getting incidence matrix')
        start = clock()
        # this should only be called after a solution has been locked
        # we are just going to run through the vertices
        # and generate the incidence matrix. Note you can find their positions
        # by grabbing the corresponding vertex simply by accessing it from 
        # self.block.Vertices() at the 
        # same index of the row you are looking at in the incidence matrix
        # first we generate the matrix we will be using
        num_cols = self.block.num_vectors
        num_rows = len(self.block.Vertices())
        M = Matrix(num_rows, num_cols, [0] * (num_rows * num_cols))
        row = 0
        for vertex in self.block.Vertices():
            vector_id = 0
            for node in vertex.cut:
                M[row, vector_id] = node.value
                vector_id += 1
            row += 1
        end = clock()
        print('-->got incidence matrix in %s seconds' % (end - start))
        return M
                
        
    def Find(self, file=None):
        # this runs the algorithm to find the kirchhoff graph for the entered 
        # matrix
        start = clock()
        current = 0
        while True:
            self.LockZeroes()
            self.Solve()
            if not self.solution:
                self.Unlock()
                self.Grow(current)
                if current == 0:
                    current = 1
                else:
                    current = 0
            else:
                break
        self.Unlock()
        self.LockSolution()
        self.incidence_matrix = self.GetIncidenceMatrix()
        if file:
            self.Draw(file)
        end = clock()
        print('total time elapsed: %s seconds' % (end - start))