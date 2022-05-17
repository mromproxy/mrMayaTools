"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 2.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Utility

Description: Library of vector math functions.

"""
from math import sqrt

def vector(a,b):
    return (b[0]-a[0],b[1]-a[1],b[2]-a[2])    

def mag(a):
    return sqrt(a[0]**2 + a[1]**2 + a[2]**2)

def mult(a,b):
    if not isinstance(b,tuple):
        return (a[0]*b,a[1]*b,a[2]*b)
    else:
        return (a[0]*b[0],a[1]*b[1],a[2]*b[2])

def add(a,b):
    return (a[0]+b[0],a[1]+b[1],a[2]+b[2])

def scale(a,b):
    return mult(a,b)

def offset(a,b):
    return add(a,b)

def normalize(a):
    m = mag(a)
    return (a[0]/m, a[1]/m, a[2]/m)
    
def dot(a,b):
    return (a[0]*b[0] + a[1]*b[1] + a[2]*b[2])
    
def cross(a,b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])
    
def upVector(a,b):
    return normalize(cross(a,b))

def bitangent(a,b):
    a = normalize(a)
    b = normalize(b)
    return normalize(cross(normalize(cross(a,b)),a))

def invert(a):
    return scale(a,-1);

def bisector(a,b,c):
    #returns vector D, such that it bysects angle ABC
    pass

##########################################################
##########################################################
#                        Incomplete                      #
##########################################################
##########################################################
"""
def reflect(a,b):
    pass


    """
#Used for anim constraints
def getAxis(axis):
    axis = [0.0,0.0,0.0]
    #currently only supports linear
    axis = axis.lower()
    if 'x' in axis:
        if '-' in axis:
            return (-1.0,0.0,0.0)
        else:
            return (1.0,0.0,0.0)
    if 'y' in axis:
        if '-' in axis:
            return (0.0,-1.0,0.0)
        else:
            return (0.0,1.0,0.0)
    if 'z' in axis:
        if '-' in axis:
            return (0.0,0.0,-1.0)
        else:
            return (0.0,0.0,1.0)
    ##############
    axis = axis.lower()
    if 'x' in axis:
        if '-' in axis:
            x= -1
        else:
            x= 1
    if 'y' in axis:
        if '-' in axis:
            y= -1
        else:
            y= 1
    if 'z' in axis:
        if '-' in axis:
            z= -1
        else:
            z= 1