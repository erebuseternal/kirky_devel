from cvxopt import matrix
import numpy as np
from numpy.linalg import svd

# this uses svd to get our null space
def nullspace(M, atol=1e-13, rtol=0):
    rows = []
    for i in range(0, M.size[0]):
        row = []
        for j in range(0, M.size[1]):
            row.append(M[i,j])
        rows.append(row)
    A = np.array(rows)
    # my modification
    # first we convert to numpy array
    #A = np.array(M)
    # Now their bit: http://scipy-cookbook.readthedocs.org/items/RankNullspace.html
    """Compute an approximate basis for the nullspace of A.

    The algorithm used by this function is based on the singular value
    decomposition of `A`.

    Parameters
    ----------
    A : ndarray
        A should be at most 2-D.  A 1-D array with length k will be treated
        as a 2-D with shape (1, k)
    atol : float
        The absolute tolerance for a zero singular value.  Singular values
        smaller than `atol` are considered to be zero.
    rtol : float
        The relative tolerance.  Singular values less than rtol*smax are
        considered to be zero, where smax is the largest singular value.

    If both `atol` and `rtol` are positive, the combined tolerance is the
    maximum of the two; that is::
        tol = max(atol, rtol * smax)
    Singular values smaller than `tol` are considered to be zero.

    Return value
    ------------
    ns : ndarray
        If `A` is an array with shape (m, k), then `ns` will be an array
        with shape (k, n), where n is the estimated dimension of the
        nullspace of `A`.  The columns of `ns` are a basis for the
        nullspace; each element in numpy.dot(A, ns) will be approximately
        zero.
    """

    A = np.atleast_2d(A)
    u, s, vh = svd(A)
    tol = max(atol, rtol * s[0])
    nnz = (s >= tol).sum()
    ns = vh[nnz:].conj().T
    # now my bit again, I am going to convert back to a matrix
    NS = matrix(ns)
    return NS