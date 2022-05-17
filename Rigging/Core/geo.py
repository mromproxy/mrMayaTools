"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2020
Version: 1.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Core

Description: Functions for laying out nodes with relation to geometry
    Currently debug format for foot pivots
    

"""

from maya import cmds as mc
from Utility.stringTools import *
import Utility.vectorMath as vec
from Rigging.Utility.general import getDescendent


##########################################################
##########################################################
#                     Foot Analysis                      #
##########################################################
##########################################################

def getFootPivots(ankle_jnt,verts='',obj=''):
    """calculates the location of where each foot pivot should be placed

    Args:
        ankle_jnt (str): name of ankle joint. Defaults to ''.
        verts (list, optional): list of vertices to check. Defaults to ''.
        obj (str, optional): name of geometry node. Defaults to ''.

    Returns:
        dict: dictionary of pivot names and their positions
    """
    if not verts and not obj:
        raise ValueError('either vertices or geometry node needs to be provided')
    #initialize
    pivots= [
        'toeUp', #0
        'ball', #1
        'toeTip', #2
        'heel', #3
        'inside', #4
        'outside', #5
        'ankle', #6
        'center', #7
        'offset' #8
        ]

    pivot_pos= []
    ball_jnt= getDescendent(ankle_jnt,1)
    toe_jnt= getDescendent(ankle_jnt,2)

    #if give a limited list, use that, and make a center from 
    if isinstance(verts,list):
        cluster = mc.cluster(verts)
        center= mc.xform(cluster[1],q=1,rp=1,ws=1)
        mc.delete(cluster)
        #mc.select(selected)
    #if given whole obj make a list of all the verts
    #need to add support for telling different sides
    elif obj:
        center = mc.xform(ankle_jnt,q=1,t=1,ws=1)
        vert_count = mc.polyEvaluate(obj,v=1)
        verts=[]
        for i in range(vert_count):
            verts.append('{}.vtx[{}]'.format(obj,i))
    #init pivot positions to center
    for x in range(len(pivots)):
        pivot_pos.append(center)
    
    #set ankle and offset
    pivot_pos[6] = mc.xform(ankle_jnt,q=1,t=1,ws=1)
    pivot_pos[-1] = mc.xform(ankle_jnt,q=1,t=1,ws=1)
    #set ball and toeUp
    pivot_pos[0] = mc.xform(ball_jnt,q=1,t=1,ws=1)
    pivot_pos[1] = mc.xform(ball_jnt,q=1,t=1,ws=1)
    #set toeTip
    pivot_pos[2] = mc.xform(toe_jnt,q=1,t=1,ws=1)

    #scrub points to find extremes
    for vert in verts:
        vert_pos = mc.xform(vert,q=1,t=1,ws=1)
        #toe_tip
        if vert_pos[2]>pivot_pos[2][2]:
            if vert_pos[1]<pivot_pos[2][1]:
                pivot_pos[2] = vert_pos
        #heel
        if vert_pos[2]<pivot_pos[3][2]:
            if vert_pos[1]<pivot_pos[3][1]:
                pivot_pos[3] = vert_pos
        #inside
        if abs(vert_pos[0]) < abs(pivot_pos[4][0]):
            if vert_pos[1]<pivot_pos[4][1]:
                pivot_pos[4]=vert_pos
        #outside
        if abs(vert_pos[0]) > abs(pivot_pos[5][0]):
            if vert_pos[1]<pivot_pos[5][1]:
                pivot_pos[5]=vert_pos
        #lowestPoint
        if vert_pos[1] <= pivot_pos[-2][1]:
            pivot_pos[-2][1]=vert_pos[1]

    #re-calculate center
    #x=average of inside an doutside
    center_x= (pivot_pos[4][0]+pivot_pos[5][0])/2
    #y=center y because I jerry-rigged lowest point into here
    center_y = pivot_pos[7][1]
    #z=average toe to heel
    center_z= (pivot_pos[2][2]+pivot_pos[3][2])/2
    #set the center to the new values
    pivot_pos[-2]=(center_x,center_y,center_z)
    pivot_pos[4][1]= center_y
    pivot_pos[5][1]= center_y

    pivotData={}
    for pivot, pos in zip(pivots,pivot_pos):
        pivotData[pivot]=pos
    return pivotData
    

#Ready for testing
def makePivots(pivot_data,ankle_jnt,name=''):
    #init name from given jnt
    if name:
      base_name= replaceSegment(ankle_jnt,2,name)
    else:
        base_name= ankle_jnt
    base_name= replaceSegment(replaceSegment(base_name,-1,'pivot'),-2,'stacked')

    pivots=[]

    for id,position in pivot_data:
        pivot_name = appendID(base_name,id)
        pivot= mc.group(em=1,name=pivot_name)
        mc.xform(pivot,t=position,ws=1)
        pivots.append(pivot)
    return pivots


def stackPivots(pivots,setID='footIK'):
    """
    just does footIK pivots at the moment
    """
    for i in range(1,len(pivots)):
        if i ==1:
            mc.parent(pivots[i-1],pivots[i+1])
        else:
            mc.parent(pivots[i-1],pivots[i])
    return pivots

