"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 2.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Rigging.Utility

Description: Being Refactored
    Generic utility functions for:
        Node Orginization & Management
        Rig Traversal
        Abstract for Space Access

"""

import re
import maya.cmds as mc

from Utility.stringTools import getSegment,replaceSegment,appendID
import Utility.vectorMath as vec

#ready | list based inputs do not work, but it does correctly wrap into a list?
def organizeElement(nodes,typ='',clas='',rigType='character'):
    """Sorts Rig nodes inside of the character rig group

    Args:
        nodes (str | list): Nodes that require sorting
        typ (str, optional): _description_. Defaults to ''.
        clas (str, optional): _description_. Defaults to ''.
        rigType (str, optional): _description_. Defaults to 'character'.
    """
    if isinstance(nodes,(str)):
        nodes = [nodes]
        
    for node in nodes:
        offset=0
        char = getSegment(node,0)
        character_grp = '_'.join([char,rigType,'rig'])
        if not mc.objExists(character_grp):
            mc.group(em=1,name=character_grp)

        #if given a group, use typ and last id for name
        if getSegment(node,-1) == 'grp':
            offset = -1
        if not typ:
            typ = getSegment(node,(-2+offset))
        if not clas:
            clas = getSegment(node,(-1+offset))
        
        typ_grp= '_'.join([char,typ,clas,'grp'])
        class_grp= '_'.join([char, clas,'grp'])
        rig_root= '_'.join([char,'rig','grp'])
        
        #cntls live outside of the rig for ease of access
        if clas== 'cntl':
            rig_root= character_grp

        #just a special case to deal with constraints
        #maybe add a typ group for different types of constraints
        if 'constraint' in node.lower():
            class_grp = '_'.join((char,'constraint','grp'))
            typ_grp = '_'.join((char, getSegment(node,(-3)),'constraint','grp'))
            if not mc.objExists(class_grp):
                if not mc.objExists(rig_root):
                    mc.parent(mc.group(em=1,n=rig_root),character_grp)
                    mc.setAttr('.'.join((rig_root,'visibility')),0)
                mc.parent(mc.group(em=1,n=class_grp),rig_root)
            if not mc.objExists(typ_grp):
                mc.parent(mc.group(em=1,n=typ_grp),class_grp)
            mc.parent(node,w=1)
            mc.parent(node,typ_grp)
            return

        #series of checks and sorting
        if not mc.objExists(typ_grp):
            mc.parent(node,mc.group(em=1,n=typ_grp))
        else:
            if getParent(node,1) != None:
                mc.parent(node,w=1)
            mc.parent(node,typ_grp)
            return

        if not mc.objExists(class_grp):
            mc.parent(typ_grp,mc.group(em=1,n=class_grp))
        else:
            mc.parent(typ_grp,class_grp)
            return

        if not mc.objExists(rig_root):
            mc.parent(class_grp,mc.group(em=1,n=rig_root))
            mc.setAttr('.'.join((rig_root,'visibility')),0)
            mc.parent(rig_root,character_grp)
        else:
            mc.parent(class_grp,rig_root)
    return


def deleteRig(char):
    """
    deletes everything in the char_rig_grp and all utility nodes.
    Unsure why I had to step though and checking existence-- test edge cases
    """
    nodes=[]
    rig_grp= '_'.join([char,'rig','grp'])
    cntl_grp= '_'.join([char,'cntl','grp'])
    utility_grp = '_'.join((char,'utility','grp'))
    if mc.objExists(utility_grp):
        if  mc.listAttr(utility_grp,st='utilityList'):
            utility_list = mc.getAttr('.'.join((utility_grp,'utilityList')),asString=1)
            nodes = utility_list.split(',')
    if mc.objExists(cntl_grp):
        nodes.append(cntl_grp)
    if mc.objExists(rig_grp):
        nodes.append(rig_grp)

    for node in nodes:
        if mc.objExists(node):
            mc.delete(node)


def createUtility(nodeType,name):
    """
    creates a utility node and appends it to a list for easy clean up later
    name needs to be established in full before call
    returns node name
    """
    #don't do anything if it already exists--maybe change later?
    if mc.objExists(name):
        return name
    #make the new node and names
    else:
        mc.createNode(nodeType,n=name)
        char = getSegment(name,0)
        utility_grp = '_'.join((char,'utility','grp'))
        utility_list_attr = '.'.join((utility_grp,'utilityList'))
    
    #adds a utility tracking attr if need be
    if not mc.objExists(utility_grp):
        rig_root_grp = '_'.join((char,'rig','grp'))
        mc.group(em=1,n=utility_grp)
        presel = mc.ls(selection=1)
        mc.select(utility_grp)
        mc.addAttr(ln='utilityList',dt='string')
        mc.parent(utility_grp,rig_root_grp)
        mc.select(presel)
    
    #adds a tracking variable if need be
    if not mc.listAttr(utility_grp,st='utilityList'):
        mc.addAttr(ln='utilityList',at='string',dv=utility_grp,s=1)
    
    #append new node to list, or 
    current_list = mc.getAttr(utility_list_attr,asString=1)
    if not current_list:
        mc.setAttr(utility_list_attr, name, type='string')
    else:
        mc.setAttr(utility_list_attr,','.join((current_list,name)), type='string')
    return name


def getDescendent(node,steps=1):
    child = node
    for i in range(steps):
        child = mc.listRelatives(child,c=1)
        if child != None:
            child=child[0]
    return child


def getParent(node,steps=1):
    parent = node
    for i in range(steps):
        parent = mc.listRelatives(parent,p=1)
        if parent != None:
            parent = parent[0]
    return parent


def getSpace(targets):
    """
    Returns a list of spaces for the given targets, \n
    creates them if they do not already exist
    """
    if isinstance(targets,str):
        targets = [targets]

    spaces= []
    for target in targets:
        space_name = replaceSegment(target,-1, 'space')
        if mc.objExists(space_name):
            spaces.append(space_name)
        else:
            #get names
            char = getSegment(target,0)
            space = mc.group(em=1,n=space_name)
            space_grp = '_'.join((char,'space','grp'))
            rig_grp = '_'.join((char,'rig','grp'))
            
            if not mc.objExists(space_grp):
                space_grp = mc.group(em=1,n=space_grp)
                mc.parent(space_grp,rig_grp)

            mc.parent(space, space_grp)
            addDriver(target,space,'parent',mo=0)
            spaces.append(space)

    return spaces


def getSpaceList(char):
    space_grp = '_'.join((char,'space','grp'))
    return mc.listRelatives(space_grp,ad=1)


#lazy way to get rig space (acts as world)    
def getRigSpace(char):
    """
    returns what is essentially a sudo-world space grp
    """
    rig_space = '_'.join((char,'rig','space'))
    
    if mc.objExists(rig_space):
        return rig_space
    else:
        mc.group(em=1,n=rig_space)
        space_grp = '_'.join((char,'space','grp'))
        rig_grp = '_'.join((char,'rig','grp'))
        
        if not mc.objExists(space_grp):
            space_grp = mc.group(em=1,n=space_grp)
            mc.parent(space_grp,rig_grp)
        mc.parent(rig_space, space_grp)
        addDriver(rig_grp,rig_space,'parent',mo=0)
        return rig_space


def getRootGrp(node):
    clas = ''
    while(clas != 'rig'):
        node = getParent(node,1)
        if node == None:
            return False
        else:
            clas = getSegment(node,-1)
    return node


def hideAttrs(node,pattern):
    """
    hides translate, rotate, or scale based on the pattern tuple \n
    1 is on, 0 is off
    """
    for attr,value in zip(('.translate','.rotate','.scale'),pattern):
        for comp in ('X','Y','Z'):
            target= ''.join((node,attr,comp))
            mc.setAttr(target, k=value)


# TODO debug
def addDriver(driver,driven,typ='parent',skipRotation='none',
    skipTranslate='none',mo=1, aimAxis='x+',upAxis='y+',w=1):
    """connects two node via constraint, 
    adds as an additional influence if that type of constraint already exists \n
    returns constraint 

    Args:
        driver (str): influencing node
        driven (str): influenced node
        typ (str, optional): constraint type. Defaults to 'parent'.
        skipRotation (str, optional): rotation channels to be skipped. Valid values are "x","y","z", "none" Defaults to 'none'.
        skipTranslate (str, optional): translation channels to be skipped. Valid values are "x","y","z", "none" Defaults to 'none'.. Defaults to 'none'.
        mo (int, optional): whether to maintain offset or not. Defaults to 1.
        aimAxis (str, optional): forward axis for aim constraints. Defaults to 'x+'.
        upAxis (str, optional): up axis for aim constraints. Defaults to 'y+'.
        w (int, optional): default weight for new constraint influence. Defaults to 1.

    Returns:
        str: name of constraint
    """
    constraints = []
    typ = typ.lower()
    #switch for type of constraint
    #need buffer to accomidate None returns
    #constraints = list(set(mc.listConnections(driven,type='constraint')))
    if typ == 'parent':
        constraint = mc.parentConstraint( driver, driven,sr=skipRotation, w=w, mo=mo)[0]
    elif typ == 'orient':
        constraint = mc.orientConstraint( driver, driven,skip=skipRotation, w=w, mo=mo)[0]
    elif typ == 'pv':
        constraint = mc.poleVectorConstraint(driver, driven, w=w)[0]
    elif typ == 'point':
        constraint = mc.pointConstraint(driver, driven, skip=skipTranslate, w=w, mo=mo)[0]
    elif typ == 'aim':
        if isinstance(aimAxis, str):
            aimAxis= vec.getAxis(aimAxis)
        if isinstance(upAxis,str):
            upAxis= vec.getAxis(upAxis)
        constraint = mc.aimConstraint(driver, driven, skip=skipRotation, aim=aimAxis, upVector=upAxis, w=w, mo=mo)[0]
    else: 
        pass
    organizeElement(constraint)
    #constraints.append(constraint)

    #just add it and if it's parent isn'the constrains folder, move it to constrains folder

    return constraint

