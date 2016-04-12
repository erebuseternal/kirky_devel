from kirky import createBaseBlock, createInteriorBlock
from fractions import Fraction
from issue import Issue
from draw import DrawBlock
from pyx import canvas

class Kirchhoff:
    
    def __init__(self, B, conditions, multiples, min_vectors):
        self.block = createBaseBlock(conditions, B)
        self.web = self.block.vertex_pool.web
        self.interior = createInteriorBlock(conditions, multiples, self.block)
        self.min_vectors = min_vectors
        self.dimension = self.block.dimension
        # each entry will take the last number of zero locks
        self.zero_locks = []
        self.independents = []
    
    # this function will cause a replication along a specific dimension 
    # such as to duplicate along that direction
    def Grow(self, dimension):
        self.Unlock()
        # first we grab how far we are going to have to shift
        amount = int(self.block.Size()[dimension])
        # now we shift the block by that amount
        self.block.AddShift(amount, dimension)
        # now we do the incremental shift and add for the interior
        for i in range(0, amount):
            self.interior.AddShift(1, dimension)
        # and that's it!
        
    def Unlock(self):
        self.block.vertex_pool.web.Unlock()
        self.zero_locks = []
        
    def LockZeroes(self):
        # first we go through and lock down any vertices that have less 
        # than min_vectors adjacent we also check to make sure 
        # that the number of locks that are zero in value is less that min_vector
        # or equal to the length of the cut if not, we lock everything to zero
        
        # first, anyplace where both the edge coming in and the edge going out 
        # are not there we need to set things to zero
        self.zero_locks.append(0)
        for vertex in self.block.Vertices():
            for i in range(0, len(vertex.edges)):
                if not vertex.edges[i][0] and not vertex.edges[i][1]:
                    if vertex.cut[i].lock and vertex.cut[i].value == 0:
                        continue
                    elif vertex.cut[i].lock:
                        # we trigger a double lock otherwise
                        self.web.HandleDoubleLock(vertex.cut[i],0)
                    self.web.Lock(vertex.cut[i], Fraction(0,1))
                    self.zero_locks[-1] += 1
        for vertex in self.block.Vertices():
            count = 0
            for entry in vertex.edges:
                if entry[0] or entry[1]:
                    count += 1
            # now we make sure count is not less than min_vectors
            if count < self.min_vectors:
                self.lockZero(vertex)
                self.zero_locks[-1] += 1
            else:
                # this is where we check to make sure the number of zero 
                # locks in the cut is not too high
                count = 0
                for node in vertex.cut:
                    if node.lock and node.value == 0:
                        count += 1
                if self.block.num_vectors - count < self.min_vectors and count != len(vertex.cut):
                    self.lockZero(vertex)
                    self.zero_locks[-1] += 1
        if self.zero_locks[-1] == 0:
            self.zero_locks.pop(-1)
        # now we check to see if any errors arose
        if self.web.errors:
            return False    #let the user know this size doesn't work
        else:
            return True     # let the user know this size works for zero locks       
                
    def lockZero(self, vertex):
        for i in range(0, self.dimension):
            # don't want to double lock if we don't have to 
            if vertex.cut[i].lock and vertex.cut[i].value == 0:
                continue
            elif vertex.cut[i].lock:
                # we trigger a double lock otherwise
                self.web.HandleDoubleLock(vertex.cut[i],0)
            self.web.Lock(vertex.cut[i], Fraction(0,1))
        
            
    def GetCut(self, vertex):
        string = '<'
        for node in vertex.cut:
            if node.lock:
                string += '%s,' % node.value
            else:
                string += 'None,'
        string = string[:-1] + '>'
        return string
    
    def GetNumLockedVertices(self):
        count = 0
        for vertex in self.block.Vertices():
            locked = True
            for node in vertex.cut:
                if not node.lock:
                    locked = False
            if locked:
                count += 1
        return count        
    
    def TryLockIndependents(self, independents, vertex):
        if len(independents) != self.dimension:
            raise Issue('discrepency between # of values you input and # of dimensions')
        # now we scale this to the first independent we find in our cut
        scaling = 1
        had_to_scale = False
        for i in range(0, self.dimension):
            if vertex.cut[i].lock:
                if vertex.cut[i].value != 0 and independents[i] == 0:
                    raise Issue('non zero value in cut and zero value in independents')
                scaling = vertex.cut[i].value / independents[i]
                if scaling != 1:
                    had_to_scale = True
                break
        # here we are going to try to avoid zero or negative vectors
        for i in range(0, self.dimension):
            independents[i] *= scaling
        for i in range(0, self.dimension):
            if vertex.cut[i].lock:
                if vertex.cut[i].value != independents[i]:
                    raise Issue('could not scale independents to match all locks in vector')
        # now we can lock
        for i in range(0, self.dimension):
            if vertex.cut[i].lock and vertex.cut[i].value == independents[i]:
                pass
            elif vertex.cut[i].lock:
                self.web.HandleDoubleLock(vertex.cut[i], independents[i])
            else:
                self.web.Lock(vertex.cut[i], independents[i])
        self.independents.append(True)
        # now we lock zeros
        self.LockZeroes()
        if self.web.errors:
            # first we want to check if the error has to do with a scaling problem
            # in this cut because of course we haven't scaled to the dependents
            # therefore we will grab the first lock in the dependents. If it is 
            # not the problem we rollback, if it is we look to see if we had to scale
            # if we did we roll back. If we didn't we rollback and try again
            self.RollbackZeroes()
            self.RollbackIndependents()
            if not had_to_scale:
                # we get our first locked dependent node
                node = None
                index = 0
                for i in range(self.dimension, len(vertex.cut)):
                    index = i
                    node = vertex.cut[i]
                    if node.lock:
                        break
                if node:
                    # we create a new vertex to see if this node is a problem
                    cut = self.block.vertex_pool.createCut()
                    for i in range(0, self.dimension):
                        cut[i].Lock(independents[i])
                    # now we can see if it is the problem
                    if node.value != cut[index].value:
                        # so it is the problem and so we scale
                        scaling = node.value / cut[index].value
                        for i in range(0, self.dimension):
                            independents[i] *= scaling
                        return self.TryLockIndependents(independents, vertex)
            return False
        else:
            return True
        
    def RollbackZeroes(self):
        print('rolling back zeros')
        for i in range(0, self.zero_locks[-1]):
            self.web.RollBack()
        self.zero_locks.pop(-1)
        
    def RollbackIndependents(self):
        print('rolling back independents')
        # this rolls back the last independents lock 
        for i in range(0, self.dimension):
            self.web.RollBack()
        self.independents.pop(-1)
                
    def Rollback(self):
        if len(self.zero_locks) > 0:
            self.RollbackZeroes()
            if len(self.independents) > 0:
                self.RollbackIndependents()
            return True
        return False
    
    def GetVertex(self, position):
        return self.block.vertex_pool.GetVertex(position)
    
    def Draw(self, file):
        c = canvas.canvas()
        DrawBlock(self.block, c)
        DrawBlock(self.interior, c)
        c.writePDFfile(file)
            
        
        
                
        
                
                