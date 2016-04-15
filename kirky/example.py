from kirky import Kirchhoff
from sympy import Matrix

"""
All matrices used by kirky are sympy matrices

First of all the matrix you are generating a Kirchhoff Graph for using this 
software must be of the form [IB] and B^T cannot have two 
rows which are the same.

So to use the Kirchhoff object you need to have 
 * B from [IB]. 
 * Then you need to have [B^TI] scaled (using multiplications 
on rows) so that every element is an integer. What you'll actually be inputting 
to the Kirchhoff Object is the the block portion
of that (just B^T if no scaling was required). 
 * Whatever numbers you used to scale each row you will want in a list. 
 The first row's scaling should be the first entry, the second rows scaling 
 should be the second entry, etc. If no scaling was needed for a particular row, 
 place a one at that position.
 * Finally, you will need the minimum number of vectors that can be on any vertex
for that vertex to be non-zero. 
--> Enter each of these components into the Kirchhoff object constructor in that order. 

Then, to get find the Kirchhoff graph corresponding to [IB] 
you just call the Find method with a file to draw to (which is optional)
and the object will run an algorithm to find your solution

Note that you can only draw the Kirchhoff graph if the number of dependent
vectors are two (i.e. the I in [IB] is two by two), otherwise you are dealing 
with a space of dimension 3 and greater and I haven't implemented how to draw 
that quite yet.
"""

m = Matrix([[2,1],[1,2]])

k = Kirchhoff(m, m.T, [1,1], 3)
k.Find('kirchhoff')
print(k.incidence_matrix)