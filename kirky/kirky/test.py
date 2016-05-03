from linear_clean import RowPositive
from pyx import canvas
from sympy import Matrix

C = Matrix([[-1,2],[-3,-4]])
r = RowPositive(C)
all_good = r.CheckAndGenerate()
count = 0
"""
for splitter in r.splitters:
    c = canvas.canvas()
    splitter.Draw(c)
    c.writePDFfile('drawing%s' % (count))
    count += 1
"""
print(all_good)
if all_good:
    print(r.GetV())