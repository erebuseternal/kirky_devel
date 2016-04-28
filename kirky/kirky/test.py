from linear import Slice, Lattice
from pyx import canvas, path
from math import pi, sqrt

slice = Slice(pi/6, pi/7)
print('slice stuff %s %s' % (slice.upper[0], slice.lower[0]))
lattice = Lattice()
lattice.GrowAbout([0,0])
c = canvas.canvas()
lattice.Draw(c)
slice.Draw(c, sqrt(2))
c.writePDFfile('drawing')