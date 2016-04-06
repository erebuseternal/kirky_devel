from symbolic import Web

"""
Each vertex has a vertex cut. If there are n vectors 
in your block, then the vertex cut has n spots each of 
which will end up being some number.

From the conditions we actually know exactly how these things 
need to be related, and thanks to symbolic nodes this becomes 
super easy! 

All we have to do is literally set some of the numbers in each cut 
in terms of the others.

Because of the form of the conditions we are going to be inputting this 
becomes significantly easy: that form is [IB]. (mxn)

From this form the first m entries are left alone. But, the ith entry (i>m)
is equal to the sum of each of the first m entries each multiplied 
by the corresponding element in the ith column.

ith entry = sum([IB][j,i]*jth entry) j goes from 1 to m

we can represent this very simply with our symbolic nodes,
and vertex creation and all of this other jazz described can easily be handled
by a vertex pool
"""

class Vertex:

    def __init__(self, position):
        self.position = position
        self.cut = []

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

# this is just a container really but it also handles the creation of new 
# vertices
class VertexPool:

    # condition block should be a cvxopt matrix it is the B portion of [IB]
    def __init__(self, condition_block, r=2):
        self.condition_block = condition_block
        # the dimension of our space is equal to the number of rows
        # in our condition_block
        self.dimension = self.condition_block.size[0]
        
        # we prepare ourself for the vertices
        self.vertices = []
        self.index = Index(r,0,self.dimensions)
        
        # we prepare the web of symbolic nodes that we are 
        # going to be generating
        self.web = Web()
        
    def createCut(self):
        # here is where we create a new cut for a vertex
        # first we create a bunch of brand new symbolic nodes 
        # to act as our independent first m entries in this cut
        cut = []
        for i in range(0, self.dimension):
            cut.append(self.web.CreateNode())
            
        # now we create the rest of the entries (which of course are conditioned
        # on the first m
        for i in range(0, self.condition_block.size[1]):
            node = self.web.CreateNode()
            # now we add in our conditions
            # we create the new parent group for these conditions
            group_key = node.CreateParentGroup()
            # now we go ahead and add the parents and their multiples
            for j in range(0, self.dimension):
                multiplier = self.condition_block[i,j]
                parent = cut[j]
                node.AddParent(group_key, (parent, multiplier))
        # and our cut has been created!
        return cut
    
    def addVertex(self, vertex):
        # first we look to see if there is a vertex at this position 
        # already in the index
        index_vertex = self.index.getElement(vertex.position)
        # and we only add this vertex if it isn't already there
        if not index_vertex:
            self.index.addElement(vertex)
            return vertex
        # otherwise we will return the indexed vertex
        else:
            return index_vertex
    
    def CreateVertex(self, position):
        vertex = Vertex(position)
        cut = self.createCut()
        # now we are going to handle adding a vertex
        # note this makes sure we return the actual indexed vertex 
        # which is especially important if there is already one there
        # uniqueness is thus maintained at the level of creating vertices
        # it is impossible to create a vertex at the same position twice
        vertex = self.addVertex(vertex)
        return vertex