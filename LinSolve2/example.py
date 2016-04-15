from kirky import Kirchhoff
from sympy import Matrix

"""
First of all your matrix must be of the form [IB] and B^T cannot have two 
rows which are the same.

So to use the Kirchhoff object you need to have B from [IB]. Then you 
need to have [B^TI] scaled (using multiplications 
on rows) so that every element is an integer. Then you'll want the block portion
of that (just B^T if no scaling was required). Whatever numbers you 
used to scale each row you will want in a list. The first row's scaling 
should be the first entry, the second rows scaling should be the second entry,
etc. If no scaling was needed for a particular row, place a one at that position.
Finally, you will need the minimum number of vectors that can be on any vertex
for that vertex to be non-zero. Enter each of these components into the 
Kirchhoff object constructor in that order. 

Then you just call the Find method with a file to print to (which is optional)
and the object will run an algorithm to find your solution

Note that you can only draw the Kirchhoff graph if the number of dependent
vectors are two (i.e. the I in [IB] is two by two), otherwise you are dealing 
with a space of dimension 3 and greater and I haven't implemented how to draw 
that quite yet.
"""

m = Matrix([[2,1],[1,2]])
b = m.T

k = Kirchhoff(m, [1,1], 3)
k.Find('kirchhoff')
print(k.incidence_matrix)