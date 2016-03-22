"""
Our first function will take a 2d array of fractions
and return a numpy array of fractions in reduced row
echelon form. (Row matrix)

We will do the following:
    We will have a for loop for the size of the matrix
    We will select the i'th row and ignore it
    Then we will use the i'th row to delete
    the j'th element in each row (for rows that aren't
    the i'th). Then we will just skip the last row
    Finally, we will scale the matrix so each beginning
    entry is one.
"""



# if this cannot make a reduced echelon form it will throw an error
def reduceMatrix(matrix):
    for i in range(0, len(matrix)):
        # the range goes to len(matrix) - 2 so that we ignore the last row
        deletion_row = matrix[i]
        # first we have to check that this row does not have a zero for
        # its ith value
        if deletion_row[i] == 0:
            # first we check to see if there is a row below
            # it with a nonzero entry here
            good_row = None
            for j in range(i + 1, len(matrix)):
                if matrix[j][i] != 0:
                    # if we found a good row we switch the rows
                    good_row = matrix[j]
                    matrix[j] = deletion_row
                    matrix[i] = good_row
                    deletion_row = matrix[i]
                    break
            # otherwise we throw an error cause we have a problem
            raise Error
        # first we scale this row's ith value to be one. It will need to be
        # in the end anyways and this will simplyfy things
        coefficient = deletion_row[i]
        for j in range(i, len(deletion_row)):
            deletion_row[j] = deletion_row[j] / coefficient
        for j in range(0, len(matrix)):
            if j == i:
                continue
            current_row = matrix[j]
            # now we multiply the deletion_row with
            # the inverse of ith value in the deletion row times
            # the ith value in the current row but the deletion's value is one
            coefficient = current_row[i]
            # we subtract the deletion_row with the multiplication from
            # the current row
            for k in range(0, len(deletion_row)):
                current_row[k] = current_row[k] - coefficient * deletion_row[k]

class Vector:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

# this will make a matrix go from column to row or vice versa
# essentially the transpose
def flipMatrix(matrix):
    flipped_matrix = []
    for i in range(0, len(matrix[0])):
        flipped_matrix.append([0] * len(matrix))
    for i in range(0, len(matrix[0])):
        for j in range(0, len(matrix)):
            flipped_matrix[i][j] = matrix[j][i]
    return flipped_matrix

def getConditions(matrix):
    # first we turn it to reduced echelon form
    reduceMatrix(matrix)
    # then we change to column matrix
    matrix = flipMatrix(matrix)
    # now we grab the columns that do not have a single one in them
    conditions_matrix = matrix[len(matrix[0]):]
    return conditions_matrix
