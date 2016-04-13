from issue import Issue

"""
NOTE!!! because Nodes do not update lock information when say a parent is added
(which would need to be the case if the parent was locked) you must create before
you do any locking. Or better put, you can only create and add onto a web of 
nodes if ALL of the nodes are unlocked.
"""

class Node:
    
    def __init__(self, web, id):
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
        
        self.web = web
        self.id = id
        
    def CreateParentGroup(self, *parent_tuples):
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
    
    # this will be called by lock to see if there are any parent groups 
    # with one unlocked parent. In which case that parent needs to get locked    
    def checkForGroupLocks(self):
        # this is here because if the child is not locked, the even if only one 
        # of its parents are not locked, it isn't locked so the group isn't either
        if not self.lock:
            return
        for key in self.parent_groups:
            if len(self.parent_groups[key]) - 1 == self.parent_group_locks[key]:
                # we now create the value we will need to lock this to
                value = 0
                for parent_tuple in self.parent_groups[key]:
                    if parent_tuple[0].lock:
                        value += parent_tuple[1] * parent_tuple[0].value 
                    else:
                        unlocked_parent = parent_tuple[0]
                        multiplier = parent_tuple[1]
                # this way the sum of the parents times their multipliers 
                # equals the value of this child
                value = (self.value - value) / multiplier
                # and now we go for the lock
                # note that we let the lock know to ignore this one particular
                # child
                unlocked_parent.Lock(value, self.id)
    
    # this updates the lock counts on the children and triggers a lock where 
    # necessary (avoiding a lock trigger on id_to_ignore)        
    def updateLocksOnChildren(self, id_to_ignore):
        for key in self.children:
            for child in self.children[key]:
                child.parent_group_locks[key] += 1
                # then we need to see if a lock is triggered on the children
                if child.parent_group_locks[key] == len(child.parent_groups[key]):
                    # this is to make sure that the parent isn't spurned to lock by a child 
                    # and then causes a double lock on a child
                    if id_to_ignore != child.id or child.id == None:
                        child.parentLock(key)
    
    def Lock(self, value, id_to_ignore=None):
        # if this is not already locked, we lock it
        if not self.lock:
            self.value = value
            self.lock = True
            self.web.addLock(self, value)
            # next we need to update the lock counts for its children
            self.updateLocksOnChildren(id_to_ignore)
            # now we need to see if this also locks any parents
            # this will happen if all but one of a parent group's members 
            # are already locked
            self.checkForGroupLocks()
            # now we look to see if any of its children are already locked
            # because this may mean that having itself locked means that there 
            # is a group of parents on the child with only one parent left over now
            for key in self.children:
                for child in self.children[key]:
                    child.checkForGroupLocks()
        # otherwise we have to check two things
        else:
            # first if the values are the same this double lock is legal
            if self.value == value:
                return
            # but if they aren't something is wrong in our web so the web
            # needs to be told
            else:
                print(self.value)
                print(self)
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
        
    def Lock(self, node, value):
        if node.lock:
            raise Issue('cannot lock an already locked node from web command!')
        new_lock_data = (node, [])
        self.locks.append(new_lock_data)
        # and now we initiate the lock
        node.Lock(value)
        
    def addLock(self, node, value):
        # we add a new node into the current_lock data
        self.locks[-1][1].append(node)
        
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
    
    def HandleDoubleLock(self, node, value):
        self.errors.append((node, value))
        
    def Unlock(self):
        # this will rollback everything
        while len(self.locks) > 0:
            self.RollBack()

                
    
        