from kirky import createBaseBlock, createInteriorBlock, createBlockConditions
from cvxopt import matrix

def blockformation(elements, size):
    conditions = matrix(elements,size)
    block = createBaseBlock(conditions)
    print('conditions matrix: %s' % conditions)
    print('number of vertices %s' % len(block.vertices))
    for vertex in block.vertices:
        print(vertex)

def test_blockformation(): 
    print('expecting 9 vertices')
    blockformation([2,1,1,2],(2,2))
    print('expecting 6 vertices')
    blockformation([2,1,1,1], (2,2))
    print('expecting 8 vertices')
    blockformation([1,1,1,1,1,1], (2,3))
    print('expecting 12 vertices')
    blockformation([2,1,1,1,1,1], (2,3))
    
def interiorblockformation(elements, size, multiples):
    conditions = matrix(elements,size)
    print('conditions matrix: %s' % conditions)
    print('multiples: %s' % multiples)
    block = createBaseBlock(conditions)
    print('number of vertices in block %s' % len(block.vertices))
    interior = createInteriorBlock(conditions, multiples, block)
    print('number of vertices in the interior %s' % len(interior.vertices))
    print('printing edges now')
    for edge in interior.edges:
        print(edge)
        
def test_interiorblockformation():
    interiorblockformation([1,1,1,1],(2,2), [1,1])
    interiorblockformation([1,1,1,-1],(2,2), [1,1])
    interiorblockformation([1,1,1,2],(2,2), [1,1])
    
def blockconditions(elements, size, multiples):
    conditions = matrix(elements,size)
    print('conditions matrix: %s' % conditions)
    block = createBaseBlock(conditions)
    interior = createInteriorBlock(conditions, multiples, block)
    bc = createBlockConditions(conditions, multiples, block, interior)
    for vertex in block.vertices:
        string = ''
        for edge_tuple in vertex.edges:
            edge = edge_tuple[1]
            head = edge_tuple[0]
            vector_id = edge.vector_id
            id = edge.id
            if head:
                string += '(vid:%s,cid:%s,-)' % (vector_id, id)
            else:
                string += '(vid:%s,cid:%s,+)' % (vector_id, id)
        print('vertex %s has cut %s' % (vertex,string))
    print(bc)
    

# test block formation
#test_blockformation()
# test interior block formation
#test_interiorblockformation()
# block conditions tests
#blockconditions([1,1,1,1], (2,2), [1,1])
#blockconditions([1,1,1,1], (2,2), [2,1])
