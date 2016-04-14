from kirky import Kirchhoff
from cvxopt import matrix
from time import clock

def findKirchhoff(B,m,multiples,min_num,file):
    start = clock()
    k = Kirchhoff(B,m,multiples,min_num)
    current = 0
    while True:
        k.LockZeroes()
        solution = k.SolveEdgeOnly()
        if not solution:
            k.Unlock()
            k.Grow(current)
            if current == 0:
                current = 1
            else:
                current = 0
        else:
            break
    k.Unlock()
    k.LockSolutionEdgeOnly(solution)
    k.Draw(file)
    end = clock()
    print('total time elapsed: %s seconds' % (end - start))
    
    

m = matrix([-3,5,1,2,-3,1], (2,3))
print(m)
findKirchhoff(m, m.T, [1,1,1], 4, 'kirchhoff13')