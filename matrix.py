
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

from fraction import Fraction

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
        self.indicies = range(1, len(self) + 1)

    # iteration handling ----------------------------------
    def __iter__(self):
        return self

    def next(self):
        # if we have are trying to access at an index beyond
        # the length we need to stop
        if self.current > len(self):
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
        for i in self.indicies:
            new_vector.append(self[i] - other[i])
        return new_vector

    def __add__(self, other):
        if len(self) != len(other):
            raise Issue('vectors are of different lengths')
        new_vector = Vector()
        for i in self.indicies:
            new_vector.append(self[i] + other[i])
        return new_vector

    # with rmul, the other is found before self, which is
    # how scalar multiplication works
    def __rmul__(self, other):
        new_vector = Vector()
        for i in self.indicies:
            new_vector.append(other * self[i])
        return new_vector
    # ------------------------------------------------------

    # in place math operations -----------------------------
    # these operations will not return a new vector but rather
    # modify the current one
    def addOn(self, other):
        if len(self) != len(other):
            raise Issue('vectors are of different lengths')
        for i in self.indicies:
            self[i] = self[i] + other[i]

    def subtractFrom(self, other):
        if len(self) != len(other):
            raise Issue('vectors are of different lengths')
        for i in self.indicies:
            self[i] = self[i] - other[i]

    def scale(self, other):
        for i in self.indicies:
            self[i] = other * self[i]

    # ------------------------------------------------------

    # List like operations ---------------------------------
    def __len__(self):
        return len(self.list)

    def append(self, element):
        self.list.append(element)
        # we also have to update indicies
        self.indicies = range(1, len(self) + 1)

    # these following two methods allow our vector to be base
    # one rather than base zero
    def __setitem__(self, key, value):
        if type(key) == int and key > 0:
            try:
                self.list[key - 1] = value
            except:
                raise Issue('key was out of bounds')
        else:
            raise Issue('key was not a positive integer')

    def __getitem__(self, key):
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
        for i in range(1, self.length + 1):
            if self[i] != other[i]:
                return False
        return True

    # means that the string is <value1, value2, value3, ...>
    def __str__(self):
        string = '<'
        for i in self.indicies:
            string += '%s, ' % self[i]
        string = string[:-2] + '>'
        return string

    # hashes based on the string representation
    def __hash__(self):
        return hash(str(self))

def createZeroBOL(self, size):
    BOL = BaseOneList()
    for i in range(0, size):
        BOL.append(Fraction(0, 1))
    return BOL

class Matrix:

    def __init__(self, num_rows, num_cols):
        # the matrix will be n by m
        self.size = (num_rows, num_cols)
        # rows and columns need to be BaseOneLists
        # and filled with them as well
        self.columns = BaseOneList()
        self.rows = BaseOneList()
        # now we fill with zeroes
        for i in range(0, num_cols):
            self.columns.append(createZeroBOL(num_rows))
        for i in range(0, num_rows):
            self.rows.append(createZeroBOL(num_cols))

    def get(self, row_key, column_key):
        if not row:
            if type(column_key) == int and column_key > 0:
                try:
                    return self.columns[column_key]
                except:
                    raise Issue('column key was out of bounds')
            else:
                raise Issue('column key was not an integer')
        else:
            if type(row_key) == int and row > 0:
                try:
                     row = self.rows[row_key]
                except:
                    raise Issue('row key was out of bounds')
            else:
                raise Issue('row key was not an integer')
            if not column:
                return row
            else:
                return row[column_key]

    def setValue(self, value, row_key, column_key):
        if not type(row_key) == int:
            raise Issue('row key was not an integer')
        if not type(column_key) == int:
            raise Issue('column key was not an integer')
        if row_key > self.size[0] or row_key < 1:
            raise Issue('row key was out of bounds')
        if column_key > self.size[1] or column_key < 1:
            raise Issue('column key was out of bounds')
        # have to set things for both the rows and the columns
        self.columns[column_key][row_key] = value
        self.rows[row_key][column_key] = value

    def setRow(self, row, row_key):
        if not isinstance(row, BaseOneList):
            raise Issue('row was not a child of BaseOneList')
        if not type(row_key) == int:
            raise Issue('row key was not an integer')
        if row_key > self.size[0] or row_key < 1:
            raise Issue('row key was out of bounds')
        if not len(row) == self.size[1]:
            raise Issue('row was of the wrong length')
        # now we set the row
        self.rows[row_key] = row
        for i in range(0, self.size[1]):
            self.setValue(row[i + 1], row_key, i + 1)

    def setColumn(self, column, column_key):
        if not isinstance(column, BaseOneList):
            raise Issue('column was not a child of BaseOneList')
        if not type(column_key) == int:
            raise Issue('column key was not an integer')
        if column_key > self.size[1] or column_key < 1:
            raise Issue('column key was out of bounds')
        if not len(column) == self.size[0]:
            raise Issue('column was of the wrong length')
        # now we set the row
        self.columns[column_key] = column
        for i in range(0, self.size[0]):
            self.setValue(column[i + 1], column_key, i + 1)

    def getTranspose(self):
        transpose = Matrix(self.size[1], self.size[0])
        transpose.columns = self.rows
        transpose.rows = self.columns
        return transpose


def joinRows(matrix1, matrix2):
    if matrix1.size[1] != matrix2.size[1]:
        raise Issue('your two matrices have different number of columns!')
    matrix = Matrix(matrix1.size[0] + matrix2.size[0], matrix1.size[1])
    matrix.rows = matrix1.rows
    for i in range(0, matrix2.size[0]):
        matrix.rows.append(matrix2.rows[i + 1])
    return matrix

def joinColumns(matrix1, matrix2):
    if matrix1.size[0] != matrix2.size[0]:
        raise Issue('your two matrices have different number of rows!')
    matrix = Matrix(matrix1.size[0], matrix1.size[1]+matrix2.size[1])
    matrix.columns = matrix1.columns
    for i in range(0, matrix2.size[1]):
        matrix.columns.append(matrix2.columns[i + 1])
    return matrix

def negateMatrix(matrix):
    for i in range(1, matrix.size[0] + 1):
        for j in range(1, matrix.size[1] + 1):
            matrix.setValue(-1 * matrix.get(i, j), i, j)
    return matrix

def identityMatrix(size):
    matrix = Matrix(size, size):
    for i in range(1, size + 1):
        matrix.setValue(Fraction(1, 1), i, i)
    return matrix
