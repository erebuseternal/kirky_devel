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
        self.interior = createInteriorBlock(conditions, multiples, self.block)
        self.web = self.block.vertex_pool.web
        self.dimension = self.block.dimension
        self.solution = None
        self.incidence_matrix = None
        self.linear_system = None
        
    """
    This method allows us to grow our block along a certain dimension. It does
    so by shift-adding the base block by the width of the block in that dimension
    and then shift-adding the interior by one as many times as the original base
    block was wide in that dimension
    """
    def Grow(self, dimension):
        print('-->growing along dimension %s' % dimension)
        start = clock()
        self.Unlock()
        # first we grab how far we are going to have to shift
        amount = int(self.block.Size()[dimension])
        # now we shift-add the baseblock by that amount
        self.block.AddShift(amount, dimension)
        # now we do the incremental shift and add for the interior
        for i in range(0, amount):
            self.interior.AddShift(1, dimension)
        # and that's it!
        end = clock()
        print('-->grew along dimension %s in %s seconds' % (dimension, (end-start)))
    
    """
    This allow you to unlock this object from its solution if you want to try 
    another solution
    """  
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
    need to consider down to just edge weights. Each edge weight gets an unique
    index. The same index its weight has in the edge_pool's edge_weights. This 
    index is the column in which it appears in the matrix of our linear system
    
    The following method then goes ahead and generates a matrix that contains
    all of these conditions in such a form that this matrix M multiplied by 
    a column containing the edge weights should equal zero. 
    
    How do we generate each of these rows of this matrix then? We follow the 
    following algorithm:
        * loop through every each of the symbolic nodes attached to our Kirchhoff 
            object
        * for each such node we grab its edge parents using getEdgeParents
        * for each such node we loop through its parent groups (note that the 
            only nodes with parents are vertex cut nodes)
        * for each parent group that isn't an edge parent group we create a new 
            row
        * for each parent group, if it is not the edge parent group we take 
            each parent and get its edge parents (note that every parent in a 
            parent group which isn't the edge parent group does not have any 
            edge nodes in it). We then get the multiplier of the edge weight 
            (obtained from the edge parent group for the node) multipled by
            the current node's multiplier in the parent group we are considering
            and add it to the column position in that row corresponding to the 
            edge weight in consideration.
        * Then, for each edge weight in the child's parent group, we add the 
            multipler to the column corresponding to that edge weight multiplied 
            by negative one. (we multiply by negative, because the parent group 
            values input above, when multipled by the edge weight solution must 
            add up to the sum to the child, so by subtracting the child, our 
            row, multiplied by the edge weights should equal zero)
            
    Once this is done it sets self.linear_system to the found matrix
    """
    def GenerateLinearSystem(self):
        print('-->generating linear system')
        start = clock()
        # first we need to generate the matrix that will hold our system
        # to do this we need the number of rows and the length of each row
        num_rows = self.FindNumRows()
        # the number of columns is just the number of edge weights we will be 
        # solving for
        num_edges = len(self.block.edge_pool.edge_weights) # this is the length of each row
        matrix = Matrix(num_rows, num_edges, [0]*(num_rows * num_edges))
        # now we can go ahead and fill in the non-zero bits in this matrix.
        # to keep track of the row we are currently on we keep the following counter
        row = 0
        for node in self.web.nodes:
            edge_parents = self.getEdgeParents(node)
            for key in node.parent_groups:
                # first we check to make sure this isn't the edge parent group
                if node.parent_groups[key][0][0].kind == 'edge':
                        continue
                # now we go about replacing all of the parents with their edge
                # edge weight parents
                for parent_tuple in node.parent_groups[key]:
                    parent = parent_tuple[0]
                    parent_multiplier = parent_tuple[1]
                    # now we get the edges to replace it
                    parent_edge_parents = self.getEdgeParents(parent)
                    # we now enter the edge weight info into our matrix
                    for edge_tuple in parent_edge_parents:
                        if edge_tuple:
                            weight = edge_tuple[0]
                            multiplier = edge_tuple[1]
                            # we add this into the right column position in this row
                            matrix[row, weight.weight_id] += multiplier * parent_multiplier
                    # finally we add in this node's parents with a minus 1 affixed to 
                    # each of their multipliers
                    for edge_tuple in edge_parents:
                        if edge_tuple:
                            weight = edge_tuple[0]
                            multiplier = edge_tuple[1]
                            # we add this into the right column position in this row
                            matrix[row, weight.weight_id] += multiplier * -1
                # we increment because now we are done with that row
                row += 1
        end = clock()
        print('-->generated linear system of size (%s, %s) in %s seconds' % (matrix.shape[0], matrix.shape[1], (end-start)))
        self.linear_system = matrix 
    
    """
    This returns a list of length two. The first entry is for the first edge
    weight found, and the second entry is for the second edge weight found. 
    If in either case the edge weight doesn't exist the entry in the 
    list there just defaults to None. If it does exist the entry is a tuple
    with the edge weight being the first entry and its multiplier in the parent
    group in which it was found being the second entry
    
    We find these two by looping through the node's parent groups and grabbing 
    the parents from the one whose first node is of the type edge. If no such 
    parent groups are found we just return [None,None]
    """
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
                # the parent group will contain the edge weight node and the 
                # multipler in that order so we just set the entry at the 
                # current index to exactly that
                parents[index] = parent_tuple
                index += 1
            break
        return parents
    
    """
    This runs through the nodes attached to our object finds the number of
    none-edge parent groups. This corresponds to the number of rows that will 
    be in our linear system.
    """
    def FindNumRows(self):
        count = 0
        for node in self.web.nodes:
            # we skip things that are strictly edges
            for key in node.parent_groups:
                # now we check to make sure this isn't a edge_weight parent group
                if node.parent_groups[key][0][0].kind == 'edge':
                        continue
                count += 1
        return count
    
    """
    This is where we plug in our nullspace finder. It simply looks for the 
    nullspace of self.linear_system and sets self.solution to what it finds
    """
    def SolveLinearSystem(self):
        print('-->looking for nullspace')
        start = clock()
        solution = self.linear_system.nullspace()
        end = clock()
        print('-->nullspace found in %s seconds' % (end - start))
        self.solution = solution
    
    """
    This is where we plug in the drawing functionality from draw
    """
    def Draw(self, file):
        # this simply creates a canvas, draws the interior and exterior and 
        # then exports it as a PDF
        c = canvas.canvas()
        DrawBlock(self.block, c)
        DrawBlock(self.interior, c)
        c.writePDFfile(file)
    
    """
    THIS SHOULD ONLY BE CALLED AFTER A SOLUTION HAS BEEN LOCKED
    
    It creates a matrix with as many columns as vectors. It runs through the 
    vertices and for each one adds its cut as a row. 
    
    Note that the index of the row you are looking at corresponds to the 
    vertex at the same index in self.block.Vertices()
    
    Once it is done it sets the matrix it found to self.incidence_matrix
    
    NOTE THAT MANY VERTICES ARE LIKELY TO BE ZERO BECAUSE THEY ARE NOT 
    PART OF THE SOLUTION. YET BECAUSE WE ARE GETTING THE CUTS OF ALL 
    VERTICES THEY WILL STILL SHOW UP IN THE INCIDENCE MATRIX
    """
    def GetIncidenceMatrix(self):
        print('-->getting incidence matrix')
        start = clock()
        # first we generate the matrix we will be using
        num_cols = self.block.num_vectors
        num_rows = len(self.block.Vertices())
        M = Matrix(num_rows, num_cols, [0] * (num_rows * num_cols))
        # we keep track of the row we are on with the following counter
        row = 0
        # we run the vertices setting their cut to the current row
        for vertex in self.block.Vertices():
            vector_id = 0
            for node in vertex.cut:
                # we check to make sure the node is locked
                if node.lock:
                    M[row, vector_id] = node.value
                else:
                    # if it isn't then we just set the current element to zero
                    # because this node is obviously not part of our solution
                    M[row, vector_id] = 0
                vector_id += 1
            # we are done with the row, so we increment our counter
            row += 1
        end = clock()
        print('-->got incidence matrix in %s seconds' % (end - start))
        self.incidence_matrix = M
                
    """
    This is the algorithm that puts all of the above together to find the 
    Kirchhoff Graph corresponding to the inputs entered into the constructor.
    
    It is pretty straight forwards as it just 
    """  
    def Find(self, file=None):
        start = clock()
        # this counter holds the next direction to grow along
        current = 0
        while True:
            self.GenerateLinearSystem()
            self.SolveLinearSystem()
            if not self.solution:
                self.Grow(current)
                # we check to see if we still have another dimension 
                # to grow in before we need to go back to dimension 0
                if current < self.dimension - 1:
                    current += 1
                else:
                    current = 0
            else:
                break
        self.LockSolution()
        self.GetIncidenceMatrix()
        if file:
            self.Draw(file)
        end = clock()
        print('total time elapsed: %s seconds' % (end - start))