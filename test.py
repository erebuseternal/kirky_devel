
from kirky import *
from time import clock
from random import randint
from functions import *
"""
v1 = Vector(3)
for i in range(1,4):
    v1[i] = i
v2 = Vector(3)
e = Edge(v1,v2,1)
print(e.head_vertex.edges)
print(e.tail_vertex.edges)
"""
"""
vertices = []
index = Index(2, 1, 5)
sum = 0
for i in range(1, 200000):
    vector = Vector()
    for j in range(0, 5):
        vector.append(randint(0,10))
    vertex = Vertex(vector)
    vertices.append(vertex)
new_list = []
start = clock()
for vertex in vertices:
    new_list.append(vertex)
end = clock()
print(end - start)
start = clock()
for vertex in vertices:
    index.addElement(vertex)
end = clock()
print(end-start)
element = vertices[10000]
start = clock()
for vertex in vertices:
    if element == vertex:
        break
end = clock()
print(end - start)
start = clock()
index.getElement(element.position)
end = clock()
print(end - start)
"""
"""
edges = []
for i in range(0, 20000):
    v1 = Vector()
    v2 = Vector()
    for j in range(0, 5):
        v1.append(randint(0,5))
        v2.append(randint(0,5))
    e = Edge(v1,v2,randint(1,5))
    edges.append(e)
b = Block(5,5)
for edge in edges:
    b.addEdge(edge)
print(len(b.edges))
print(len(b.vertices))
b.shiftAndAdd(10,2)
print(len(b.edges))
print(len(b.vertices))
"""
"""
for edge in edges:
    print(edge)
    print(b.edge_indexes[edge.vector_id].getElement(edge.position))
for i in range(0,10):
    b.addEdge(edge)
"""
"""
edges = []
for i in range(0, 20000):
    v1 = Vector()
    v2 = Vector()
    for j in range(0, 5):
        v1.append(randint(0,5))
        v2.append(randint(0,5))
    e = Edge(v1,v2,randint(1,5))
    edges.append(e)
b = Block(5,5)
for edge in edges:
    b.addEdge(edge)
b.ingest(b)
"""
"""
M = Matrix(4,3)
M[1][1] = 1
M[1][2] = 2
M[2][1] = 3
M[2][2] = 4
M[3][1] = 5
M[3][2] = 6
M[4][1] = 1
M[4][2] = 1
M[4][3] = 1
M[1][3] = 1
M[2][3] = 1
M[3][3] = 1
print(M)
b = createBaseBlock(M)
print(len(b.edges))
"""
