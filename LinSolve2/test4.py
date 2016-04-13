from kirky import Kirchhoff
from cvxopt import matrix
from time import clock

def findKirchhoff(B,m,multiples,min_num,file):
    k = Kirchhoff(B,m,multiples,min_num)
    current = 0
    while True:
        k.LockZeroes()
        solution = k.Solve()
        if not solution:
            k.Unlock()
            k.Grow(current)
            if current == 0:
                current = 1
            else:
                current = 0
        else:
            break
    k.LockSolution(solution)
    k.Draw(file)
    

m = matrix([3,-5,1,2,-3,-3], (2,3))
print(m)
findKirchhoff(m, m.T, [1,1,1], 3, 'kirchhoff10')