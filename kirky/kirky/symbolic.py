from .issue import Issue

"""
The basic idea of a node is the following. Each node can have a series of parent
groups, and each parent can have a series of children (if a child has a parent
that parent MUST have it as a child). Any node can then be locked. This happens
in only one of two ways, either you lock it manually, or if all of a child's
parents in one group get locked then it will get locked. How? well, each parent
group is composed of tuples. Each tuple has for its first entry a node, and for 
its second a multiplier (which should be a number). When all the parents are 
locked they trigger the last child to lock to the sum of each of them multiplied
by their multiplier. So if a child has two parents, one with a multiplier of 1
and on with a multiplier of -1 then if the parents lock to the same value 
the child will lock to zero.

And that's essentially all there is to nodes
"""

class Node:
    
    def __init__(self, web, id):
        self.kind = None
        # children will be held under the key they assign to this parent
        # this is so that when the parents let the children know they have 
        # locked, the children can quickly assign the lock to the appropriate
        # group
        self.children = {}
        # parents will be held in groups each element within a group will 
        # be a tuple with the parent node as the first element and a multiplier
        # as the second
        self.parent_groups = {}
        # these will let us know how many parents have 
        # locked in a group
        self.parent_group_locks = {}
        # this just holds the next key we will use for a parent group
        self.next_key = 0
        
        self.value = None
        
        self.lock = False
        
        # this is the web the node is attached to
        self.web = web
        self.id = id
        # this holds the weight id's for edges
        self.weight_id = 0
        
    def CreateParentGroup(self, *parent_tuples):
        # parent groups are how we show that several nodes should when combined 
        # in a particular way equal this node
        # we create the new parent group
        key = self.next_key
        self.parent_groups[key] = []
        self.parent_group_locks[key] = 0
        self.next_key += 1
        # and then add in the parents
        for parent_tuple in parent_tuples:
            self.parent_groups.append(parent_tuple)
            # and this allows the parent to add the child 
            # under the appropriate group number
            parent_tuple[0].addChild(key, self)
        return key
            
    def AddParent(self, key, parent_tuple):
        self.parent_groups[key].append(parent_tuple)
        parent_tuple[0].addChild(key, self)
            
    def addChild(self, key, child):
        if not key in self.children:
            self.children[key] = []
        self.children[key].append(child)
    
    # this is what gets called when all parents have locked and now a child
    # should as well
    def parentLock(self, key):
        # first we generate the value that this child will attempt to lock 
        # to, because we need for both conditional statements to follow
        value = 0
        for parent_tuple in self.parent_groups[key]:
            value += parent_tuple[1] * parent_tuple[0].value
        # now that we have our value we see if this node is already locked 
        # we can attempt a lock
        self.Lock(value)
    
    # this updates the lock counts on the children and triggers a lock where 
    # necessary (avoiding a lock trigger on id_to_ignore)        
    def updateLocksOnChildren(self):
        for key in self.children:
            for child in self.children[key]:
                child.parent_group_locks[key] += 1
                # then we need to see if a lock is triggered on the children
                if child.parent_group_locks[key] == len(child.parent_groups[key]):
                    child.parentLock(key)
    
    # this is how you manually lock a node            
    def Lock(self, value):
        # first we check to make sure that this isn't already locked
        if not self.lock:
            self.value = value
            self.lock = True
            # we let the web node a lock has happened
            self.web.addLock(self, value)
            # we update lock information on child nodes
            self.updateLocksOnChildren()
        else:
            # if it is already locked we check to see that the value we are 
            # trying to lock to is the node's own value
            if self.value == value:
                return 
            else:
                # if it isn't we send invoke a method on the web
                self.web.HandleDoubleLock(self, value)
            
    def Unlock(self):
        if self.lock:
            # this is overly simple because most of the unlocking procedure 
            # will be handled by the web this node is in
            self.lock = False
            self.value = 0
            # and now we need to decrement the lock counts on this node's children
            # note that the actual unlocking of these children will be handled by 
            # the web
            for key in self.children:
                for child in self.children[key]:
                    child.parent_group_locks[key] -= 1
        
"""
This class hold collective state about nodes and captures lock state 
in such a way that we can rollback anything that we do in a consistent manner
"""
class Web:
    
    def __init__(self):
        self.next_id = 0 
        # this is a list containing the locks that were specifically 
        # commanded. What is actually contained in each entry
        # is a tuple, the first entry is the node that was locked by 
        # command, the second entry is the list of locks that occured
        # after that lock took place
        # this data will allow us to roll back to the last actuated lock
        self.locks = []
        # this is a list that holds all of the nodes that got a double 
        # lock condition on them
        self.errors = []
        # I don't keep track of the nodes in a list, because this would 
        # mean that every node I create would be kept, whereas many of them
        # for example when I am creating edges will simply be lost as they 
        # are found to be unneeded
        self.nodes = [] # this should be cleaned up
        
    # this just creates a new node, assigned to this web, with the appropriate
    # new id
    def CreateNode(self):
        node = Node(self, self.next_id)
        self.next_id += 1
        self.nodes.append(node)
        return node
    
    def RemoveNode(self):
        self.nodes.pop(-1)
        self.next_id -= 1
    
    # this is how we should call a lock on a node. Calling it in this way 
    # allows the web to keep enough state so that it can rollback in the 
    # future
    def Lock(self, node, value):
        if node.lock:
            raise Issue('cannot lock an already locked node from web command!')
        # we create a new entry for this lock and the locks that happen as a 
        # result
        new_lock_data = (node, [])
        self.locks.append(new_lock_data)
        # and now we initiate the lock
        node.Lock(value)
        
    def addLock(self, node, value):
        # we add a new node into the current_lock data
        self.locks[-1][1].append(node)
    
    # this allows you to go back to the state of your nodes before the most 
    # recent lock (this can be called repeatedly if you have made many locks    
    def RollBack(self):
        # first we empty errors NOTE THAT YOU SHOULD NOT KEEP GOING IF 
        # ERRORS EXIST!!!!
        self.errors = []
        # we just have to unlock all the nodes in our last lock data set
        for node in self.locks[-1][1]:
            node.Unlock()
        self.locks[-1][0].Unlock()
        # and now we remove that lock data set
        last_data = self.locks.pop(-1)
        # we return the last actuated node for convenience
        return last_data[0]
    
    # this allows us to track when we have tried to lock one node in many 
    # ways, usually an indication of an error
    def HandleDoubleLock(self, node, value):
        self.errors.append((node, value))
    
    # this rolls back all locks made so far
    def Unlock(self):
        # this will rollback everything
        while len(self.locks) > 0:
            self.RollBack()

                
    
        