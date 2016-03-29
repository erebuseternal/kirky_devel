
"""
We start with our first class, the matrix. Now I am going to do a couple
things here to make things easier for me, and for whoever is likely
to use this code.

The first thing I am going to do, is make this base 1. Yep cs people
out there, base 1. This is for the mathematicians, so please don't have
me, I figure its easier for you to adapt than them.

Then I am going to allow you to access this matrix by columns or
rows.

Finally, you will have to define the matrix dimensions from the start
and then you can input lists for the rows or columns.
"""

from fractions import Fraction
from copy import deepcopy

class Issue(Exception):
    def __init__(self, problem):
        self.problem = problem

    def __str__(self):
        return 'ERROR: the problem was: %s' % self.problem

class Vector:

    # a base one list can be initialized with a
    # size, if given it will make itself 'size' long
    # and fill with zeros
    def __init__(self, size=0):
        # create the list
        self.list = []
        # make it the appropriate size
        for i in range(0, size):
            self.list.append(Fraction(0,1))
        self.current_index = 1    # this is used for iterations
        # useful for iterations using an index
        # allows us to easily iterate over a base 1 vector
        # whereas python has its iteration helpers built around
        # base zero
        self.indices = range(1, len(self) + 1)

    # iteration handling ----------------------------------
    def __iter__(self):
        return self

    def next(self):
        # if we have are trying to access at an index beyond
        # the length we need to stop
        if self.current_index > len(self):
            # this allows us to iterate again
            self.current_index = 1
            raise StopIteration
        # otherwise we grab the element at self.current_index
        else:
            element = self[self.current_index]
            # we get ready for the next call of next()
            self.current_index += 1
            return element
    # -----------------------------------------------------

    # basic math operations -------------------------------
    def __sub__(self, other):
        if len(self) != len(other):
            raise Issue('vectors are of different lengths')
        new_vector = Vector()
        for i in self.indices:
            new_vector.append(self[i] - other[i])
        return new_vector

    def __add__(self, other):
        if len(self) != len(other):
            raise Issue('vectors are of different lengths')
        new_vector = Vector()
        for i in self.indices:
            new_vector.append(self[i] + other[i])
        return new_vector

    # with rmul, the other is found before self, which is
    # how scalar multiplication works
    def __rmul__(self, other):
        new_vector = Vector()
        for i in self.indices:
            new_vector.append(other * self[i])
        return new_vector
    # ------------------------------------------------------

    # in place math operations -----------------------------
    # these operations will not return a new vector but rather
    # modify the current one
    def addOn(self, other):
        if len(self) != len(other):
            raise Issue('vectors are of different lengths')
        for i in self.indices:
            self[i] = self[i] + other[i]

    def subtractFrom(self, other):
        if len(self) != len(other):
            raise Issue('vectors are of different lengths')
        for i in self.indices:
            self[i] = self[i] - other[i]

    def scale(self, other):
        for i in self.indices:
            self[i] = other * self[i]

    # ------------------------------------------------------

    # List like operations ---------------------------------
    def __len__(self):
        return len(self.list)

    def append(self, element):
        self.list.append(element)
        # we also have to update indicies
        self.indices = range(1, len(self) + 1)

    def prepend(self, element):
        self.list.insert(0, element)
        self.indices = range(1, len(self) + 1)

    # these following two methods allow our vector to be base
    # one rather than base zero
    def __setitem__(self, key, value):
        # this is to create the appropriate behavior for matrices
        if not key and key != 0:
            if len(value) != len(self):
                raise Issue('length of row and number of columns differ')
            for i in self.indices:
                self[i] = value[i]
            return
        if type(key) == int and key > 0:
            try:
                self.list[key - 1] = value
            except:
                raise Issue('key was out of bounds')
        else:
            raise Issue('key was not a positive integer')

    def __getitem__(self, key):
        # this is convenience for matrices later. If we try
        # self[None] we just get self
        if not key and key != 0:
            return self
        if type(key) == int and key > 0:
            try:
                return self.list[key - 1]
            except:
                raise Issue('key was out of bounds')
        else:
            raise Issue('key was not a positive integer')

    # -----------------------------------------------------

    # if two vectors have the same entries, the equals operation
    # evaluates to True
    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in self.indices:
            if self[i] != other[i]:
                return False
        return True

    # means that the string is <value1, value2, value3, ...>
    def __str__(self):
        string = '<'
        for i in self.indices:
            string += '%s, ' % self[i]
        if len(string) > 3:
            string = string[:-2] + '>'
        else:
            string = string + '>'
        return string

    def __repr__(self):
        return str(self)

    # hashes based on the string representation
    def __hash__(self):
        return hash(str(self))

# this acts like a vector, but is accessing the rows of a matrix
# directly which allows for some nice functionality
class ColumnSlice:

    def __init__(self, rows, index_to_slice):
        self.rows = rows
        self.index_to_slice = index_to_slice
        self.current_index = 1
        self.indices = range(1, len(self.rows) + 1)

    # iterations ---------------------------------------------
    def __iter__(self):
        return self

    def next(self):
        # if we have are trying to access at an index beyond
        # the length we need to stop
        if self.current_index > len(self):
            # this allows us to iterate again
            self.current_index = 1
            raise StopIteration
        # otherwise we grab the element at self.current_index
        else:
            element = self[self.current_index]
            # we get ready for the next call of next()
            self.current_index += 1
            return element
    # -------------------------------------------------------

    # list like methods -------------------------------------
    def __len__(self):
        return len(self.rows)

    def __getitem__(self, key):
        if type(key) == int and key > 0:
            try:
                return self.rows[key][self.index_to_slice]
            except:
                raise Issue('key was out of bounds')
        else:
            raise Issue('key was not a positive integer')

    def __setitem__(self, key, value):
        if type(key) == int and key > 0:
            try:
                self.rows[key][index_to_slice] = value
            except:
                raise Issue('key was out of bounds')
        else:
            raise Issue('key was not a positive integer')
    # -------------------------------------------------------

    # if two vectors have the same entries, the equals operation
    # evaluates to True
    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in self.indices:
            if self[i] != other[i]:
                return False
        return True

    # means that the string is <value1, value2, value3, ...>
    def __str__(self):
        string = '<'
        for i in self.indices:
            string += '%s, ' % self[i]
        string = string[:-2] + '>'
        return string

    def __repr__(self):
        return str(self)

    # hashes based on the string representation
    def __hash__(self):
        return hash(str(self))

    # this creates a vector copy of this column slice
    def createVector(self):
        vector = Vector()
        for element in self:
            vector.append(deepcopy(element))
        return vector

# this is completely to allow for nice syntax on Matrices
# it handles the cases of Matrix[None][i] and the getting
# and setting that results. For getting it returns a column
# slice, which acts pretty much like the vector (without
# the math methods) but whose elements are embedded in the
# rows. Therefore doing anything to them, affects the matrix
# the rows came from.
# for setting it loops through the rows setting the ith entry
# of each to the approriate element from a column vector you
# are trying to set.
class RowWrapper:

    def __init__(self, rows):
        self.rows = rows

    # when we have a matrix and we call M[None][1]
    # M[None] returns a row wrapper and therefore
    # this with a key of one would be called with
    # M[None][1]. We need it to return a column
    # slice which is like a vector except that its
    # holding the rows, so that any modification to the
    # column also affects the rows
    def __getitem__(self, key):
        if key > len(self.rows[1]) or key < 1:
            raise Issue('index is out of bounds')
        return ColumnSlice(self.rows, key)

    # this would arise with a call like M[None][i] = vector
    # so we need to loop through the rows and set their
    # ith element to the corresponding element in the vector
    # where the vector should be like a column
    def __setitem__(self, key, value):
        if len(value) != len(self.rows):
            raise Issue('length of column and number of rows differ')
        if key > len(self.rows[1]) or key < 1:
            raise Issue('index is out of bounds')
        # we loop through the rows and the value at the same time
        for i in self.rows.indices:
            self.rows[i][key] = value[i]
        # and we are all done!

class Matrix:

    def __init__(self, num_rows, num_cols):
        # the matrix will be n by m
        self.size = [num_rows, num_cols]
        # the containers for our rows will need to
        # be base one. Vectors will work well
        # the actual rows will be of course vectors
        self.rows = Vector()
        # now we create the rows initializing all of
        # their entries to zero (Fraction type)
        for i in range(0, num_rows):
            self.rows.append(Vector(num_cols))
        # to help with iterations
        self.row_indices = range(1, num_rows + 1)
        self.column_indices = range(1, num_cols + 1)
        self.rowwrapper = RowWrapper(self.rows)

    # in accessing matrices you should always give M[i][j] where
    # i or j can be None to indicate you want a column or row
    # respectively
    def __getitem__(self, key):
        if not key:
            # here we return a RowWrapper to handle acces by column
            return self.rowwrapper
        else:
            if key > len(self.rows) or key < 1:
                raise Issue('index is out of bounds')
            # we just return the row
            return self.rows[key]

    # we do not implement set item. This is because the matrix will
    # only ever see getitem because M[i][j] will return M[i], and then
    # only the object returned by M[i] will see set item on j

    def __str__(self):
        string = '('
        for row in self.rows:
            for element in row:
                string += '%s, ' % element
            string = string[:-1] + '\n'
        string = string[:-1] + ')'
        return string

    def __repr__(self):
        return str(self)

    # helper methods -------------------------------------------------
    def getTranspose(self):
        transpose = Matrix(self.size[1], self.size[0])
        # we are going to loop through each column
        for i in self.column_indices:
            transpose[i][None] = self[None][i].createVector()
        return transpose

    def prependColumns(self, other):
        if self.size[0] != other.size[0]:
            raise Issue('your two matrices have different number of rows!')
        for i in other.column_indices:
            for j in self.row_indices:
                # we actually run through the columns backwards
                self.rows[j].prepend(other[j][other.size[1] - i + 1])
        # now we just need to adjust the size and number of columns
        self.size[1] = self.size[1] + other.size[1]
        self.column_indices = range(1, self.size[1] + 1)

    def appendColumns(self, other):
        if self.size[0] != other.size[0]:
            raise Issue('your two matrices have different number of rows!')
        for i in other.column_indices:
            for j in self.row_indices:
                self.rows[j].append(other[j][i])
        # now we just need to adjust the size and number of columns
        self.size[1] = self.size[1] + other.size[1]
        self.column_indices = range(1, self.size[1] + 1)

    def prependRows(self, other):
        if self.size[1] != other.size[1]:
            raise Issue('your two matrices have different number of columns!')
        for i in other.row_indices:
            # we actually run through the rows backwards
            self.rows.prepend(deepcopy(other[other.size[0] - i + 1][None]))
        # now we just need to adjust the size and number of rows
        self.size[0] = self.size[0] + other.size[0]
        self.row_indices = range(1, self.size[0] + 1)

    def appendRows(self, other):
        if self.size[1] != other.size[1]:
            raise Issue('your two matrices have different number of columns!')
        for i in other.row_indices:
            self.rows.append(deepcopy(other[i][None]))
        # now we just need to adjust the size and number of rows
        self.size[0] = self.size[0] + other.size[0]
        self.row_indices = range(1, self.size[0] + 1)

    def negate(self):
        for i in self.row_indices:
            for j in self.column_indices:
                matrix[i][j] = -1 * matrix[i][j]



def identityMatrix(size):
    matrix = Matrix(size, size)
    for i in range(1, size + 1):
        matrix[i][i] = Fraction(1,1)
    return matrix
