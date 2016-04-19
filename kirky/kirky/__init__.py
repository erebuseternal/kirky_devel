from fractions import Fraction
from pyx import canvas
from .draw import DrawBlock
from time import clock
from .issue import Issue
from sympy import Matrix
from block_creation import createBaseBlock, createInteriorBlock

class Kirchhoff:
    def __init__(self, B, conditions, multiples):
        self.block = createBaseBlock(conditions, B)
        self.web = self.block.vertex_pool.web
        self.interior = createInteriorBlock(conditions, multiples, self.block)
        self.dimension = self.block.dimension
        # each entry will take the last number of zero locks
        self.independents = []
        # stuff to do with solutions
        self.solution = None
        self.incidence_matrix = None
        self.linear_system = None
        
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
    
    """
    We know that vertex cuts reduce to edges and that all of our conditions 
    are based on vertex cuts. Therefore we can reduce the set of variables we 
    need to consider down to just edge weights. 
    
    The following method then goes ahead and generates a matrix that contains
    all of these conditions in such a form that this matrix M multiplied by 
    a column containing the edge weights should equal zero. 
    
    How do we generate each of these rows of this matrix then? We follow the 
    following algorithm:
        * loop through every each of the symbolic nodes attached to our Kirchhoff object
            * for each node check to see if it is locked (in which case we know it 
                is locked to zero). If it is locked and is a vertex type node 
                (i.e. a node representing an element of a vertex cut) then find 
                the parent group containing an edge and grab all of 
    """
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
        self.linear_system = matrix 
    
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
    
    def SolveLinearSystem(self):
        # here we make a call to generate the linear system the we try to solve 
        # for its nullspace. We set whatever solution we find to self.solution. For Sympy
        # if there is no solution what we return will be an empty list. So 
        # you can check for that
        print('-->looking for nullspace')
        start = clock()
        solution = self.linear_system.nullspace()
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
            self.GenerateLinearSystem()
            self.SolveLinearSystem()
            if not self.solution:
                self.Grow(current)
                if current == 0:
                    current = 1
                else:
                    current = 0
            else:
                break
        self.LockSolution()
        self.incidence_matrix = self.GetIncidenceMatrix()
        if file:
            self.Draw(file)
        end = clock()
        print('total time elapsed: %s seconds' % (end - start))