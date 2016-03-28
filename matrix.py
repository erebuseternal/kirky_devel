
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

class BaseOneList:

    def __init__(self, array=[]):
        self.list = array
        self.current = 1

    def __iter__(self):
        return self

    def next(self):
        if self.length() < self.current:
            self.current = 1
            raise StopIteration
        else:
            element = self[self.current]
            self.current += 1
            return element

    def append(self, element):
        self.list.append(element)

    def length(self):
        return len(self.list)

    def __setitem__(self, key):
        if type(key) == int and key > 0:
            try:
                self.list[key - 1] =
            except:
                raise Issue('key was out of bounds')
        else:
            raise Issue('key was not an integer')

    def __getitem__(self, key, value):
        if type(key) == int and key > 0:
            try:
                return self.list[key - 1] = value
            except:
                raise Issue('key was out of bounds')
        else:
            raise Issue('key was not an integer')

    def __eq__(self, other):
        if self.length() != other.length():
            return False
        for i in range(1, self.length + 1):
            if self[i] != other[i]:
                return False
        return True

    def __str__(self):
        return str(self.list)

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
