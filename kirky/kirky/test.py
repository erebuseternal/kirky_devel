from linear_clean import Splitter, Angle
from pyx import canvas
from math import pi

a1 = Angle(pi - 0.05)
a2 = Angle(3.0*pi/2.0 + 1.35)
splitter = Splitter(a1,a2)
splitter.FindPoint()
c = canvas.canvas()
splitter.Draw(c)
c.writePDFfile('drawing')

