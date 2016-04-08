from draw import DrawEdge
from edge import Edge
from symbolic import Node
from fractions import Fraction
from pyx import canvas

"""
e1 = Edge([1,1],[0,0],0)
e2 = Edge([0,0],[1,0],1)
e3 = Edge([-1,-0.5],[0,0],2)
e4 = Edge([1,1], [-1,-0.5],3)
e5 = Edge([2,2],[1,1],0)
e1.weight = Node(None, None)
e2.weight = Node(None, None)
e3.weight = Node(None, None)
e4.weight = Node(None, None)
e5.weight = Node(None, None)
e1.weight.lock = True
e2.weight.lock = True
e3.weight.lock = True
e5.weight.lock = True
e1.weight.value = Fraction(2,3)
e2.weight.value = Fraction(11,12)
e3.weight.value = Fraction(1,2)
e5.weight.value = Fraction(0,1)

c = canvas.canvas()
DrawEdge(e1, c)
DrawEdge(e2, c)
DrawEdge(e3, c)
DrawEdge(e4, c)
DrawEdge(e5, c)
c.writePDFfile("arrow")
"""