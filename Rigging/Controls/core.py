"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 2.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Rigging.Controls

Description: Primary functions for creating controls

"""

import re
import maya.cmds as mc

from Rigging.Controls.library import ControlLibrary
from Rigging.Utility.general import organizeElement
from Rigging.Utility.general import getDescendent,getParent
from Rigging.Utility.general import getRigSpace
from Rigging.Utility.general import hideAttrs
from Rigging.Utility.general import createUtility
from Rigging.Utility.general import addDriver


from Utility.stringTools import getSegment,replaceSegment,appendID
import Utility.vectorMath as vec

##########################################################
##########################################################
#                         Utility                        #
##########################################################
##########################################################

def getDefaultShape(typ):
    """Returns default curveShape ID for the given control typ

    Args:
        typ (str) : control abbreviation or short name

    Returns:
        str : control shape name
    """
    if  re.search("(?i)ik",typ) :
        return 'nail'
    elif re.search( "(?i)fk",typ ) :
        return 'circle'
    elif re.search( "(?i)pv",typ ) :
        return 'rombus'
    elif re.search( "(?i)face",typ ) :
        return 'sphere'
    elif re.search( "(?i)footprint",typ ) :
        return 'footprint'
    elif re.search( "(?i)hand",typ ) :
        return 'cone'
    else:
        return 'jack'
    

def addOffsetAbove(cntl,index=1, tag=''):
    """adds an offset at the given index (above the node given)
    tag is added as an ID to cntl name (typ and clas set to offset_grp)

    Args:
        cntl (str): name of control node to begin navigating from.
        index (int, optional): how many steps above or below the given node. a negative value will add directly under the cntl_grp. Defaults to 1.
        tag (str, optional): ID to be added to the new offset group. Defaults to ''.

    Returns:
        str: name of the new offset group
    """
    #get the element currently at the index
    if index > 0:
        index=max(index-1,0)
        if 'cntl_grp' in cntl:
            raise ValueError("You can't add an offset group above the base cntl group") 
        target = getParent(cntl, index)
    
    elif index < 0:
        current_grp = cntl
        while(not '_cntl_grp' in current_grp):
            current_grp = getParent(current_grp,1)
        target = getDescendent(current_grp,abs(index))
    elif index ==0:
         target=cntl

    #make name and ensure it's unique
    offset_name = replaceSegment(replaceSegment(cntl,-1,'grp'),-2,'offset')
    target_offset_name = appendID(offset_name,tag)
    count=1
    while(mc.objExists(target_offset_name)):
        target_offset_name=appendID(offset_name,''.join((tag,str(count))))
        count+=1
    offset_name=target_offset_name
    #make grp and reorder the list
    new_offset = mc.group(em=1,name=offset_name)
    parent = getParent(target,1)
    mc.parent(new_offset,parent)
    mc.makeIdentity(new_offset, apply=False)
    mc.parent(target,new_offset)
    #mc.select(cntl)

    return new_offset


def enableInverseBlend(cntl,constraint,attrName='switch',inverseWeightIdx=1,directWeightIdx=0):
    """connects the weights of the given constraint to be related to the given attr.
        standard is fk active at 0, ik active at 1
        InverseBlend only supports 2 influences,
        use space tools for 3+    

    Args:
        cntl (str): name of control to add inverseBlend feature
        constraint (str): name of contraint to be driven by the attr. Expects 2 influences
        attrName (str, optional): name of blend attr. Defaults to 'switch'.
        inverseWeightIdx (int, optional): Influence that will be active at 0. Defaults to 1.
        directWeightIdx (int, optional): Influence that will be active at 1. Defaults to 0.

    Returns:
        bool: True on success
    """
    #only support 2 influences use space tools for 3+
    
    #init node name
    invert_node_name = '_'.join((cntl,attrName,'reverse','util'))
    
    #create invert node if needed
    if not mc.objExists(invert_node_name):
        invertNode= createUtility('reverse', invert_node_name)
    else:
        invertNode = invert_node_name
        
    #add attr if needed
    if not mc.listAttr(cntl,st=attrName):
        mc.addAttr(cntl,ln=attrName,w=1,at='float',dv=1,hxv=1,hnv=1,max=1.0,min=0.0,k=1) 

    #does the connection
    constraintWeights = mc.parentConstraint(constraint, q=1, wal=1)
    driver= ''.join((cntl,'.',attrName))
    driven=''.join((constraint,'.',constraintWeights[directWeightIdx]))
    inverseIn = '.'.join((invertNode,'ix'))
    if not mc.isConnected(driver,inverseIn,iuc=1):
        mc.connectAttr(driver, inverseIn,f=1)
    inverseDriven=''.join((constraint,'.',constraintWeights[inverseWeightIdx]))
    
    mc.connectAttr(driver,driven,f=1)
    mc.connectAttr('.'.join((invertNode,'ox')), inverseDriven,f=1)
    return True


def syncVis(base_cntl,attrName,max_cntls=None,min_cntls=None, max=1.0,min=0.0):
    """ turns visibility of given nodes on and off based on max and min values given
    Visiblity is only off at the given value. All values inbetween will not disable visiblity for given nodes
    Args:
        base_cntl (str): control to add attr to
        attrName (str): Name of attr driving visiblity
        max_cntls (list | str, optional): cntls to be visible when attr Value is not min. Defaults to None.
        min_cntls (list | str, optional): cntls to be visible when attr Value is not max. Defaults to None.
        max (float, optional): off value for min_cntls. Defaults to 1.0.
        min (float, optional): off value for max_cntls. Defaults to 0.0.
    """
    if not mc.listAttr(base_cntl,st=attrName):
        mc.addAttr(base_cntl,ln=attrName,w=1,at='float',dv=1,hxv=1,hnv=1,max=max,min=min,k=1)
    if max_cntls:
        if isinstance(max_cntls,(str)):
            max_cntls = [max_cntls]
        condition_max_node = '_'.join((base_cntl,attrName,'visConditionMax','util'))
        #make condition node
        if not mc.objExists(condition_max_node):
            condition_max_node = createUtility('condition',condition_max_node)
        mc.setAttr('.'.join((condition_max_node,'ctr')),0)
        mc.setAttr('.'.join((condition_max_node,'cfr')),1)
        mc.setAttr('.'.join((condition_max_node,'st')),min)
        mc.connectAttr('.'.join((base_cntl,attrName)),'.'.join((condition_max_node,'ft')),f=1)
        for cntl in max_cntls:
            mc.connectAttr('.'.join((condition_max_node,'ocr')),'.'.join((cntl,'visibility')),f=1)

    if min_cntls:
        if isinstance(min_cntls,(str)):
            min_cntls = [min_cntls]
        condition_min_node = '_'.join((cntl,attrName,'visConditionMin','util'))
        if not mc.objExists(condition_min_node):
            condition_min_node = createUtility('condition',condition_min_node)
        mc.setAttr('.'.join((condition_min_node,'ctr')),0)
        mc.setAttr('.'.join((condition_min_node,'cfr')),1)
        mc.setAttr('.'.join((condition_min_node,'st')),max)
        mc.connectAttr('.'.join((base_cntl,attrName)),'.'.join((condition_min_node,'ft')),f=1)
        for cntl in min_cntls:
            if cntl:
                mc.connectAttr('.'.join((condition_min_node,'ocr')),'.'.join((cntl,'visibility')),f=1)


##########################################################
##########################################################
#                    Control Creation                    #
##########################################################
##########################################################

#Need to check direction
def makeCntl(jnts,
            typ='',
            shape='',
            name='',
            size=1.0,
            rotation=(0,0,0),
            position='',
            shapeOffset=(0,0,0)):
    """Creates a control for the given nodes. Control Shapes lay on the x,-z plane and point towards towards the origin, when applicable
        Controls consist of a shape with 2 parent groups-- one for alignment and one for incoming connections.
    Args
        jnts (str | list): joint or list of joints to create controls for
        typ (str, optional): New typ to assign to control. Defaults to typ specified in joint name.
        shape (str, optional): shape of control (curve or nurbs object). Defaults to template if not given.
        name (str, optional): New name. Defaults to joint Name.
        size (float | list | tuple, optional): scale of control. Defaults to 1.0.
        rotation (tuple, optional): Rotation of Control. Defaults to (0,0,0).
        position (list | tuple, optional): World Space Location to place control. Defaults to joint location if not given.
        shapeOffset (list | tuple, optional): Offset Distance from pivot. Defaults to (0,0,0).

    Returns:
        list : Name of highest control groups created
    """
    #if one joint, converts to a list
    if isinstance(jnts,(str)):
        jnts = [jnts]
    if isinstance(size,int):
        float(size)

    cntls = []
    for jnt in jnts:
        node_name= jnt
        if not typ:
            typ = getSegment(jnt,1)
        else:
            node_name = replaceSegment(node_name,1,typ)

        if name:
            node_name = replaceSegment(node_name,2,name)
    

        #grab default shape if none provided
        if not shape:
            shape = getDefaultShape(typ)

        #make cntl
        node_name = replaceSegment(node_name,-1,'cntl')
        cntl = ControlLibrary().createControlShape(shape, node_name,shapeOffset,rotation,size)
        mc.xform(cntl,t=shapeOffset,ws=1)
        mc.makeIdentity(cntl,apply=True)

        #make offset grp
        node_name = appendID(node_name,typ)
        offset_grp = replaceSegment(appendID(node_name, 'offset'),-1,'grp')
        mc.parent(cntl,mc.group(em=1,n=offset_grp))

        #make base cntl grp
        cntl_grp = replaceSegment(replaceSegment(offset_grp, -2, 'cntl'),-1,'grp')
        mc.parent(offset_grp,mc.group(em=1,n=cntl_grp))
        
        #if position not specified, match to joint
        if not position:
            mc.parent(cntl_grp,jnt)
            mc.makeIdentity(cntl_grp, apply=False)
            mc.parent(cntl_grp, a=1,w=1)
        else:
            mc.xform(cntl_grp,t=position,ws=1)

        cntls.append(cntl_grp)
    return cntls


def makeMasterCntl(root,
                cntlSize=1.0,
                cntlShape='cone', 
                rotation=(0,0,0),  
                name='', 
                offset = (1.2,0,0) ):
    """Creates a root control. Used for systems with FK-IK Blends or those requiring a master hub like Hands and Feet.

    Args:
        root (str): Base Joint for the Control to follow
        cntlSize (float, optional): Size multiplier for shape. Defaults to 1.0.
        cntlShape (str, optional): name of the desired shape. Defaults to 'cone'.
        rotation (tuple, optional): rotation to be applied to the control shape. Defaults to (0,0,0).
        name (str, optional): Basename of the Control Shape. Defaults to ''.
        offset ((float,float,float), optional): Relative position offset from given root. Defaults to (1.2,0,0).

    Returns:
        str: name of the new control handle
    """
    #house keeping
    if isinstance(offsetDist,int):
        offsetDist = float(offsetDist)
    if isinstance(offsetDist,float):
        offsetDist= (offsetDist,offsetDist,offsetDist)
    char = getSegment(root,0)
    #position
    root_pos = mc.xform(root,q=1,t=1,ws=1)
    cntl_pos = vec.add(root_pos,offset)
    #make control
    mstr_cntl_grp = makeCntl(root,typ='mstr',shape=cntlShape,name=name,size=cntlSize,rotation=rotation,position=cntl_pos)[0]
    organizeElement(mstr_cntl_grp)
    #aim at jnt
    mstr_cntl = getDescendent(mstr_cntl_grp,2)
    aim_constraint = addDriver(root,mstr_cntl,'aim',aimAxis='x+',upAxis='y+',mo=0)
    
    #add follow attr
    mc.addAttr(mstr_cntl,ln='follow',w=1,at='float',dv=1,hxv=1,hnv=1,max=1.0,min=0.0,k=1)

    #connect follow spaces
    mstr_cntl_offset= getDescendent(mstr_cntl_grp,1)
    rig_space = getRigSpace(char)
    follow_constraint = addDriver(root,mstr_cntl_offset,'parent')
    #issue-Requires testing
    addDriver(rig_space,mstr_cntl_offset,'parent',w=0)
    enableInverseBlend(mstr_cntl,follow_constraint,'follow')

    #hide things you don't need to see
    hideAttrs(mstr_cntl_offset,(0,0,1))
    hideAttrs(mstr_cntl,(1,0,1))
    return mstr_cntl

