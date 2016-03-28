"""
this is where I implement LRU to solve our linear system that we
arrive at after creating a block. We simply have a fractional
matrix object and we need to solve Ax = 0
"""

from fraction import Fraction

def LU(matrix):
    n = matrix.size[0]
    for k in range(1, n):
        for i in range(k + 1, n + 1):
            matrix.set(matrix.get(i, k) / matrix.get(k,k), i, k)
            for j in range(k + 1, n + 1):
                matrix.setValue(matrix.get(i,j) - matrix.get(i,k) * matrix.get(k,j), i, j)
    # now we separate the two
    L = matrix(n,n)
    U = matrix(n,n)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i < j:
                U.set(matrix.get(i,j), i,j)
            elif i > j:
                L.set(matrix.get(i,j), i,j)
            else:
                L.set(Fraction(1,1), i,i)
                U.set(matrix.get(i,i), i,i)
    return (L, U)

def SolveLower(L,b):
    n = L.size[0]
    y = createZeroBOL(L.size[1])
    for i in range(0, n):
        row = L.get(n - i,None)
        sum = 0
        for j in range(1, i):
            sum += y[j] * row[j]
        y[i] = 1 / L.get(i,i) * (b[i] - sum)
    return y

def SolveUpper(U,b):
    n = U.size[0]
    y = createZeroBOL(L.size[1])
    for i in range(1, n + 1):
        row = U.get(i,None)
        sum = 0
        for j in range(1, i):
            sum += y[j] * row[j]
        y[i] = 1 / U.get(i,i) * (b[i] - sum)
    return y

def Solve(A,b):
    L, U = LU(A)
    y = SolveLower(L, b)
    y = SolveUpper(U, y)
    return y

"""
Problem: this only works if we have an nxn matrix... what does this mean
for our matrices which are likely to be much larger in the number of columns?

We need to be able to solve nxm where n < m. We cannot necessarily delete
columns because that would corrupt our matrix... or would it? That would be like
setting an entire edge to zero. Our constraints remain the same though.
The thing is that deletion of columns can immediately spell doom for our other
columns. This is essentially because our matrix is incredibly sparse.
This sparseness is what indicates our connections between various edges as
really being the same vector
"""
