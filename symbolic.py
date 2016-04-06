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
            
    def AddParent(self, key, parent_tuple):
        self.parent_groups[key].append(parent_tuple)
            
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
                value = value / multiplier
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
                    if id_to_ignore != child.id:
                        child.parentLock(key)
    
    def Lock(self, value, id_to_ignore=None):
        # if this is not already locked, we lock it
        if not self.lock:
            self.value = value
            self.lock = True
            self.web.AddLock(self, value)
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
                self.web.HandleDoubleLock(self, value)
            
    def Unlock(self):
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
                
    
        