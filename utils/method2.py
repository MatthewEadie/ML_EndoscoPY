from numpy import vstack, take, einsum, hstack
import numpy as np
from scipy.interpolate import griddata
import scipy.spatial.qhull as qhull



def LinearInterpolation_OLD(xGrid, yGrid, meanvalues, xCentroids, yCentroids):
  

    #GET CENTROIDS
    # coords = vstack((xCentroids, yCentroids)).T

    #GET MEAN INTENCITIES 
    gridzLin = griddata((yGrid, xGrid), meanvalues, (yCentroids, xCentroids), method='linear')

    return gridzLin


def NearestInterpolation_OLD(xGrid, yGrid, meanvalues, xCentroids, yCentroids):
  
    #GET MEAN INTENCITIES 
    np_im_input_griddata_interpolate = griddata((yGrid, xGrid), meanvalues, (yCentroids, xCentroids))

    return np_im_input_griddata_interpolate


def CubicInterpolation_OLD(xGrid, yGrid, meanvalues, xCentroids, yCentroids):
  

    #GET CENTROIDS
    coords = vstack((xCentroids, yCentroids)).T

    #GET MEAN INTENCITIES 
    gridzLin = griddata((yGrid, xGrid), meanvalues, (yCentroids, xCentroids), method='cubic')

    return gridzLin










def interp_weights(xy, uv,d=2):
    """
    To speed up scipy griddata we can pre-calculate triangulation
    and barycentric weights and this allows for faster calls in 
    python. All rutines below are vectorised matrix manipulations.
    The routine was obtained from stackoverflow:
    https://tinyurl.com/2p87hd9s
    """

    # Delaunay triangulation
    tri = qhull.Delaunay(xy)

    # Find all triangles, in our 2D case simplex is a triangle
    simplex = tri.find_simplex(uv)

    # Take all rows from tri.siplices, this gets the vertices of triangles
    vertices = take(tri.simplices, simplex, axis=0)

    # Calculate barycentric weights for each pixel in image.
    # Need to understand this better!
    temp = take(tri.transform, simplex, axis=0)
    delta = uv - temp[:, d]
    # bary = einsum('njk,nk->nj', temp[:, :d, :], delta)
    bary = einsum('abc,ac->ab', temp[:, :d, :], delta)

    # Return the result, use this routine once and then call interpolate()
    # below.
    return vertices, hstack((bary, 1 - bary.sum(axis=1, keepdims=True)))



def interpolate(values, vtx, wts):
    """
    Fast interpolation using pre-calculated weights.
    The routine was obtained from stackoverflow:
    https://tinyurl.com/2p87hd9s
    """
    # return einsum('nj,nj->n', take(values, vtx), wts)
    return einsum('ab,ab->a', take(values, vtx), wts)