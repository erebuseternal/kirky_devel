from monitor import Kirchhoff2
from cvxopt import matrix
from time import clock

def findKirchhoff(B,m,multiples,min_num,file):
    k = Kirchhoff2(B,m,multiples,min_num)
    current = 0
    while True:
        print('locking zeroes')
        k.LockZeroes()
        try:
            print('attempting a solution')
            start = clock()
            solution = k.Solve()
            end = clock()
            print('solution found in %s seconds' % (end - start))
            break
        except:
            k.Unlock()
            k.Grow(current)
            if current == 0:
                current = 1
            else:
                current = 0
    print('locking solution')
    start = clock()
    k.LockSolution(solution)
    end = clock()
    print('solution locked in %s seconds' % (end - start))
    k.Draw(file)
    

m = matrix([2,1,1,-1,3,-1], (2,3))
print(m)
findKirchhoff(m, m.T, [1,1,1], 3, 'kirchhoff4')