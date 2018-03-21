#!/usr/bin/python3
"""
rdp

Python implementation of the Ramer-Douglas-Peucker algorithm.
"""
import sys
import numpy as np
#from math import sqrt
#from functools import partial
from math import radians, cos, sin, asin, sqrt

if sys.version_info[0] >= 3:
    xrange = range

def pl_dist(point, start, end):
    """
    Calculates the distance from ``point`` to the line given
    by the points ``start`` and ``end``.

    :param point: a point
    :type point: numpy array
    :param start: a point of the line
    :type start: numpy array
    :param end: another point of the line
    :type end: numpy array
    """
    if np.all(np.equal(start, end)):
        return np.linalg.norm(point - start)

    return np.divide(
        np.abs(np.linalg.norm(np.cross(end - start, start - point))),
        np.linalg.norm(end - start))


def rdp_rec(M, epsilon, dist=pl_dist):
    """
    Simplifies a given array of points.

    Recursive version.

    :param M: an array
    :type M: numpy array
    :param epsilon: epsilon in the rdp algorithm
    :type epsilon: float
    :param dist: distance function
    :type dist: function with signature ``f(point, start, end)`` -- see :func:`rdp.pl_dist`
    """
    dmax = 0.0
    index = -1

    for i in xrange(1, M.shape[0]):
        d = dist(M[i], M[0], M[-1])

        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        r_1 = rdp_rec(M[:index + 1], epsilon, dist)
        r_2 = rdp_rec(M[index:], epsilon, dist)
        return np.vstack((r_1[:-1], r_2))
    else:
        return np.vstack((M[0], M[-1]))


def rdp(M, epsilon=0, dist=pl_dist):
    """
    Simplifies a given array of points using the Ramer-Douglas-Peucker
    algorithm.

    Example:

    >>> from rdp import rdp
    >>> rdp([[1, 1], [2, 2], [3, 3], [4, 4]])
    [[1, 1], [4, 4]]

    This is a convenience wrapper around :func:`rdp.rdp_rec`
    that detects if the input is a numpy array
    in order to adapt the output accordingly. This means that
    when it is called using a Python list as argument, a Python
    list is returned, and in case of an invocation using a numpy
    array, a NumPy array is returned.

    Example:

    >>> from rdp import rdp
    >>> import numpy as np
    >>> arr = np.array([1, 1, 2, 2, 3, 3, 4, 4]).reshape(4, 2)
    >>> arr
    array([[1, 1],
           [2, 2],
           [3, 3],
           [4, 4]])

    :param M: a series of points
    :type M: numpy array with shape (n,d) where n is the number of points and d their dimension
    :param epsilon: epsilon in the rdp algorithm
    :type epsilon: float
    :param dist: distance function
    :type dist: function with signature ``f(point, start, end)`` -- see :func:`rdp.pl_dist`
    """

    if "numpy" in str(type(M)):
        return rdp_rec(M, epsilon, dist)

    return rdp_rec(np.array(M), epsilon, dist).tolist()
