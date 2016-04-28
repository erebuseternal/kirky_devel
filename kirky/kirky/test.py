from linear import Slice, Lattice
from pyx import canvas, path
from math import pi, sqrt

slice = Slice(pi/4, pi/4)
lattice = Lattice()
lattice.FindPoint(slice,1)
c = canvas.canvas()
lattice.Draw(c)
max_sum = 0
for point in lattice.points:
    sum = point.position[0] ** 2 + point.position[1] ** 2
    if sum > max_sum:
        max_sum = sum
slice.Draw(c, sqrt(max_sum))
"""
lattice.GrowAbout([0,0])
lattice.GrowNext(slice)
c = canvas.canvas()
lattice.Draw(c)
slice.Draw(c, sqrt(2))
lattice.FindMarkedPoints(slice)
for point in lattice.marked:
    print(point.position)
print(slice.inclusion_bounds)
"""
c.writePDFfile('drawing')
