from kirky import Kirchhoff
from sympy import Matrix

m = Matrix([[2,1],[1,2]])
k = Kirchhoff(m, m.T, [1,1], 3)
k.Find('kirchhoff14')
print(k.incidence_matrix)