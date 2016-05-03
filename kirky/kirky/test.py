from linear import Splitter, Angle
from pyx import canvas, path
from math import pi

a1 = Angle(0.0)
a2 = Angle(pi/2.0)
splitter = Splitter(a1,a2)
c = canvas.canvas()
splitter.Draw(c)

