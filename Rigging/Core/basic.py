"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2020
Version: 1.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Core

Description: Functions for generating the most primitive control structures.
    Some structures, such as bash chains and stickyTips are being revisited and currently exist as hotfixes to previous
    rigging needs.

"""

import maya.cmds as mc
from Utility.stringTools import *
import Utility.vectorMath as vec
from Rigging.Utility.general import organizeElement,createUtility,getDescendent,getParent,getRigSpace,addDriver
from Rigging.Controls.core import makeCntl,enableInverseBlend

##########################################################
##########################################################
#                         Utility                        #
##########################################################
##########################################################


def duplicateChain(jnts, typ='typ',addID='',conflictID=''):
    """Duplicates an existing joint chain and ensures no name conflicts.
        Currently expects all joints of the chain to be given.
        In Dev: support for root+chain length inputs

    Args:
        jnts (list | str): joints to be duplicated
        typ (str, optional): intended typ tag for the new joints. Defaults to 'typ'.
        addID (str, optional): additional IDs to be added to the new chain. Defaults to ''.
        conflictID (str, optional): Desire str to be used for conflictingIDs. Will use numbers if give ''. Defaults to ''.

    Returns:
        list: list of new joints
    """
    # TODO inspect conflictID handling
    if isinstance(jnts,(str)):
        jnts = [jnts]

    output_jnts = []
    
    conflictAbove=0
    conflictCount=0
    if not conflictID:
        conflictID = conflictCount
    
    newJnts=[]
    previousNewJnt= ''
    for jnt in jnts:
        # Name handling
        newName= replaceSegment(jnt,'typ',typ)
        if addID:
            newName= appendID(newName,addID)
        if conflictAbove:
            newName = appendID(newName,conflictID) 
        if mc.objExists(newName):
            newNameWithId=newName
            while mc.objExists(newNameWithId):
                if isinstance(conflictID,int):
                    conflictID += 1
                    newNameWithId= appendID(newName,str(conflictID))
                else:
                    conflictCount += 1
                    conflictID = ''.join((conflictID,str(conflictCount)))
                    newNameWithId= appendID(newName,conflictID)
            # enable the reuse of the previously solved conflictID
            conflictAbove=1
            newName= newNameWithId
        mc.duplicate(jnt,n=newName,po=1)
        
        if previousNewJnt:
            mc.parent(newName,previousNewJnt)
        else:
            mc.parent(newName,a=1,w=1)
        previousNewJnt=newName
        newJnts.append(newName)

    organizeElement(newJnts[0])
    return newJnts


##########################################################
##########################################################
#                          Core                          #
##########################################################
##########################################################


def assembleFK(jnts,cntlSize=1.0,rotation=(0,0,90), typ='nested', rotationAxis='z',
                shape='circle',upAxis='y',forwardAxis='x', parentDriver='',preset=''):
    """creates an fk system for the given joints.
    'nested' type creates a classic FK chain with each control parented to the one above
    'base' type creates an FK system where each control is driven by an attr on a single control -- used for systems like hands
    Still being refactored

    Args:
        jnts (list | str): joints to be driven by the FK system
        cntlSize (float, optional): uniform scale of control handle. Defaults to 1.0.
        rotation (tuple, optional): control rotation. Defaults to (0,0,90), such that the control lies on yx
        typ (str, optional): type of FK system, excepts either 'nested' or 'base'. Defaults to 'nested'.
        rotationAxis (str, optional): which axis is controlled when using a 'base' type. Defaults to 'z'.
        upAxis (str, optional): Currently Defunct. Defaults to 'y'.
        forwardAxis (str, optional): Currently Defunct. Defaults to 'x'.
        shape (str, optional): Shape of control shape. Defaults to 'circle'.
        parentDriver (str, optional): Defunct. Defaults to ''.
        preset (str, optional): Defunct. Defaults to ''.

    Returns:
        _type_: _description_
    """
    #create new influence chain and attach it to the given chain
        
    proxy_jnts = duplicateChain(jnts, 'fk')
    for jnt, proxy_jnt in zip(jnts,proxy_jnts):
        addDriver(proxy_jnt,jnt,'parent')
    
    if typ == 'nested':
    #Stack controls
        cntls = makeCntl(jnts, typ='fk',size=cntlSize, rotation=rotation, shape=shape)
        for i in range(1,len(cntls)):
            #gets cntl grp above it and then gets the cntl
            cntl_handle = getDescendent(cntls[i-1],2)
            mc.parent(cntls[i],cntl_handle, a=1)
        
        #connects cntls to new joint chain
        for cntl,jnt in zip(cntls,proxy_jnts):
            cntl = getDescendent(cntl,2)
            #because && and || don't seem to like me
            addDriver(cntl,jnt,'parent')
        parent = getParent(jnts[0],1)
        addDriver(parent,cntls[0],'parent')
        organizeElement(cntls[0])

        #if parentDriver:
            #pass #addDriver(parentDriver,getParent(cntls[0],2),'parent')
        return cntls[0]


    #move rotation to a pma so you can stack
    elif typ == 'base':
        base_cntl_grp = makeCntl(jnts[0],typ='fk', size=cntlSize, rotation=rotation,shape=shape)[0]
        base_cntl_offset = getDescendent(base_cntl_grp,1)
        base_cntl=getDescendent(base_cntl_grp,2)
        addDriver(base_cntl, proxy_jnts[0], 'parent')
        #make pMA node
        base_pma_node= replaceSegment(base_cntl_offset,-1,'pMA')
        base_pma_node= createUtility('plusMinusAverage',base_pma_node)
        
        ###############################
        # TODO
        # move incoming connect to offset and pc jnt to control
        #
        ##############################

        #add attrs and set up base connections of pMA-> jnt
        mc.select(base_cntl)
        mc.addAttr(ln='jnt0', at='float', dv=0,k=1)
        #base rotate to first input of pma 3D
        #mc.connectAttr('.'.join((base_cntl,'rotate')),'.'.join((base_pma_node,'input3D[0]')), f=1)
        #additional attr to specific pma 3D[1] axis
        mc.connectAttr('.'.join((base_cntl,'jnt0')),'.'.join((base_pma_node,'input3D[0]','i3'+rotationAxis)))
        #pma to proxy joint
        mc.connectAttr('.'.join((base_pma_node,'output3D')),'.'.join((base_cntl_offset,'rotate')))
        addDriver(getParent(jnts[0]),base_cntl_grp,'parent')
        
        #plug in translate to aid with following
        #mc.connectAttr('.'.join((base_cntl,'translate')),'.'.join((proxy_jnts[0],'translate')))
        rotationAttr = ''.join(('rotate',rotationAxis.upper()))

        #add an additional attr for each jnt lower
        for i in range(1,len(proxy_jnts)):
            attrName = ''.join(('jnt',str(i)))
            mc.addAttr(base_cntl,ln=attrName, at='float', dv=0,k=1)
            mc.connectAttr('.'.join((base_cntl,attrName)),
                    '.'.join((proxy_jnts[i],rotationAttr)), f=1)
        organizeElement(base_cntl_grp)

        #if parentDriver:
            #pass #addDriver(parentDriver,base_cntl_grp,'parent')

        return base_cntl
            

def makePV(jnts, ik, distance=1, size=1):
    """Makes a pole vector for the given 3 joint chain and attaches it to
    the give ik. distance is the offset from the middle joint

    Args:
        jnts (list): list of joints the PV is being created for
        ik (str): name of IK handle
        distance (int, optional): offset distance for control. Defaults to 1.
        size (int, optional): PV control shape scale. Defaults to 1.

    Returns:
        str: name of the PV's control_group
    """
    #get locations
    startJoint=mc.xform(jnts[0], q=1, t=1,ws=1)
    #mc.getAttr(jnts[0]+'.translate')[0]
    middle=mc.xform(jnts[1], q=1, t=1, ws=1)
    endEffector=mc.xform(jnts[2], q=1, t=1,ws=1)

    #get plane vectors
    norm = vec.normalize(vec.vector(middle,endEffector))
    bitangent = vec.bitangent(norm,vec.vector(middle,startJoint))
    bisector = vec.normalize(vec.add(norm,bitangent))

    #get target world position
    pvPosition = vec.add(middle,vec.mult(bitangent,(-1*distance)))
    #actually make the control and connect it
    cntl_grp = makeCntl(ik,typ='pv',size=size,position=pvPosition)[0]
    pv_cntl= getDescendent(cntl_grp,2)
    addDriver(pv_cntl,ik,'pv')
    organizeElement(cntl_grp)
    return cntl_grp



##########################################################
##########################################################
#                    Refactoring & Dev                   #
##########################################################
##########################################################


# TODO test
def assembleIK(jnts, solver='ikRPsolver', name='', typ='ik',shape='nail', 
                cntlSize=1, rotation=(0,0,90), offsetShapeDist=(0,0,0), pvSize=1, pvDist=1,
                forwardAxis='x', preset='', stickyTip=0, stickyShape='sphere',
                skipDuplicateChain=0,skipControl=0,attachAbove=1,addClav=0):
    """creates an IK set up for the given 3 joint chain. \n
    Currently only supports 3 joint chains, plans to expand further

    Args:
        jnts (list): joints to build IK contrtols for
        solver (str, optional): the type of IK solver. Options are 'ikRPsolver' or 'ikSCsolver'. Defaults to 'ikRPsolver'.
        name (str, optional): name replacement if desired, uses ending joint name if '' is given. Defaults to ''.
        typ (str, optional): typ tag to be applied to new nodes. Defaults to 'ik'.
        shape (str, optional): control shape. Defaults to 'nail'.
        cntlSize (int, optional): uniform scale for control. Defaults to 1.
        rotation (tuple, optional): control rotation. Defaults to (0,0,90), such that the control lies on xy plane.
        offsetShapeDist (tuple, optional): control offset distance. Defaults to (0,0,0).
        pvSize (int, optional): pole vector control scale. Defaults to 1.
        pvDist (int, optional): pole vector offset distance along bone normal. Defaults to 1.
        forwardAxis (str, optional): Defunct. Defaults to 'x'.
        preset (str, optional): presets for IK systems specific to certain character types. Defaults to ''.
        stickyTip (int, optional): toggle to add spport for end location locking. Defaults to 0.
        stickyShape (str, optional): control shape for the stickyTip. Defaults to 'sphere'.
        skipDuplicateChain (int, optional): Set to 1 if you want to apply the IK directly to the joint given. Defaults to 0.
        skipControl (int, optional): Skips IK control. feature used for IK systems used in feet. Defaults to 0.
        attachAbove (int, optional): Attach proxy chain to parent node of source chain. Defaults to 1.
        addClav (int, optional): Adds a single IK system to the joint above. Used in arm abstractions. Defaults to 0.
    
    Returns:
        list: list of new controls such that [IK_control, PV_control]
    """
    #need to orient cntl to end effector before binding
    #add addDriver(getParent(jnts[0]),proxy_jnts[0],'parent')
    
    
    cntls=[]
    # jnt order Top->elbow->endEffector->palm|[stickyTip]--if 3 jnt chain
    if skipDuplicateChain==1:
        proxy_jnts=jnts
    else:
        if addClav:
            jnts.insert(0,getParent(jnts[0]))
        proxy_jnts = duplicateChain(jnts, 'ik')
        for jnt, proxy_jnt in zip(jnts,proxy_jnts):
            addDriver(proxy_jnt,jnt,'parent')

    #built first so it doesn't break everything later
    # flips like crazy for some reason
    #I think it has something to do with the clavicle ik not being seperate from the arm ik chain...
    if addClav:
        #makes the clavicle ik
        clav_ik= assembleIK(proxy_jnts[0:2],solver='ikSCsolver',name='clav', typ='ik',skipDuplicateChain=1,skipControl=1,attachAbove=0)[0]
        #makes a cntl at the clavicles position
        clav_cntl_grp= makeCntl(proxy_jnts[0],typ='ik',shape='nail',name='clav',size=cntlSize,rotation=rotation,offsetShapeDist=offsetShapeDist)[0]
        clav_cntl= getDescendent(clav_cntl_grp,2)
        
        #connects ik to cntl, and proxy jnt to parent
        addDriver(clav_cntl,clav_ik,'parent')
        addDriver(getParent(jnts[0]),clav_cntl_grp,'parent')
        proxy_clav_jnt=proxy_jnts.pop(0)
        clav_jnt=jnts.pop(0)
        organizeElement(clav_ik)
        organizeElement(clav_cntl_grp)


    if 'animal' in preset:
        pass
    elif 'custom' in preset:
        pass

    #core minimal process
    else:
        startJoint= proxy_jnts[0]
        middleJoint = proxy_jnts[1]
        endEffector = proxy_jnts[-1]

    if not name:
        name= getSegment(endEffector,2)
        #update name from end Effector, maybe promote to a recursive call using dictionaries?
    ikName= replaceSegment(
            replaceSegment(endEffector,-2,typ)
            ,-1,'hndl')

    #make ik handle
    ik = mc.ikHandle(sj=proxy_jnts[0],ee=proxy_jnts[-1],sol=solver,n=ikName)[0]
    organizeElement(ik)
    cntls.append(ik)
    #add PV if needed
    if solver == 'ikRPsolver':
        pv_cntl = makePV(proxy_jnts,ik,distance=pvDist,size=pvSize)
        cntls.append(pv_cntl)

    #skips ik control--used for foot mstr
    if skipControl:
        if attachAbove:
            addDriver(getParent(jnts[0]),proxy_jnts[0],'parent')
        return cntls
    #end core minimal process


    #makes the control to drive the ik handle
    ik_cntl_grp = makeCntl(endEffector,typ='ik',name=name,size=cntlSize,
                            shape=shape,rotation=rotation,offsetShapeDist=offsetShapeDist)
    
    #enable orient ik to jnt
    # forgive me for garbage code
    #mc.parent(ik_cntl_grp[0],endEffector)
    #mc.makeIdentity(ik_cntl_grp[0],t=1)

    organizeElement(ik_cntl_grp[0])
    ik_cntl = getDescendent(ik_cntl_grp,2)
    cntls[0]=ik_cntl
    
    #connects control to approriate type
    if solver == 'ikSCsolver':
        addDriver(ik_cntl,ik,'parent')
    elif solver == 'ikRPsolver':
        addDriver(ik_cntl,ik,'point')
        addDriver(ik_cntl,endEffector,'orient')

    #if stickyTip is enabled, make an ik system for last to second to last
    #currently not implemented
    if stickyTip:
        addStickyTip(jnts,ik_cntl,stickyShape)
        #make handle and control
        #connect weight of parent constraint to this
        #pass   disable sticky_cntl's follow parent follow of ik_cntl
    else:
        addDriver(ik_cntl,proxy_jnts[-1],'orient')

    #Riddled with problems
    if addClav:
        #clav_cntl =assembleSingleBash([getParent(jnts[0]),jnts[0]],name='clav',cntlSize=cntlSize)
        #cntls.append(clav_cntl)
        """
        clav_ikName= replaceSegment(
            replaceSegment(proxy_clav,-2,'ik')
            ,-1,'hndl')

        clav_ik = mc.ikHandle(sj=proxy_clav,ee=proxy_jnts[0],sol='ikSCsolver',n=clav_ikName)[0]
        clav_cntl_grp= makeCntl(proxy_clav,typ='ik',name='clav',size=cntlSize,shape=shape,rotation=rotation,offsetShapeDist=offsetShapeDist)[0]
        clav_cntl= getDescendent(clav_cntl_grp,2)
        addDriver(clav_cntl,clav_ik,'parent')
        jnts.insert(0,getParent(jnts[0]))
        proxy_jnts.insert(0,proxy_clav)
        cntls.append(clav_cntl)
        """

    #maybe attach control instead of joint?
    #attach cntl to joint above and enable space switching.
    if attachAbove:
        if addClav:
            addDriver(getParent(clav_jnt),proxy_clav_jnt,'parent')
        else:
            addDriver(getParent(jnts[0]),proxy_jnts[0],'parent')
        if addClav:
            pass
            #addDriver(getParent(jnts[0]),clav_cntl_grp,'parent')

    return (ik_cntl,pv_cntl,ik)


# TODO bug splat on last cntl -- previous comments did not clarify issue. RIP
def assembleBashChain(jnts,shape='circle',rotation=(0,0,0),cntlSize=1.0,
                        finalCntlShape='rombus',finalCntlSize=1.0,finalCntlOffset=(0,0,0)):
    """Experimental \n
    makes a chain of single IKs \n
    This is a work around to meet deadlines and deliverables. Produces a makeshift FKIK hybrid spine


    Args:
        jnts (list): joints to be controlled by the Bash Chain
        shape (str, optional): control shape for each joint. Defaults to 'circle'.
        rotation (tuple, optional): rotation to orient controls. Defaults to (0,0,0).
        cntlSize (float, optional): uniform scale modifier for control shapes. Defaults to 1.0.
        finalCntlShape (str, optional): unique shape for final control in chain. Defaults to 'rombus'.
        finalCntlSize (float, optional): uniform scale modifier for final constrol shape. Defaults to 1.0.
        finalCntlOffset (tuple, optional): position offset for final control shape. Defaults to (0,0,0).

    Returns:
        list: list of new controls
    """

    #duplicate the chain before hand
    proxy_jnts = duplicateChain(jnts, 'bash')
    for jnt, proxy_jnt in zip(jnts,proxy_jnts):
        addDriver(proxy_jnt,jnt,'parent')

    rig_space=getRigSpace(getSegment(jnts[0],0))
    cntls=[]
    hip_cntl_grp= makeCntl(proxy_jnts[0],typ='ik',size=cntlSize,shape=shape,rotation=rotation)[0]
    organizeElement(hip_cntl_grp)
    hip_cntl=getDescendent(hip_cntl_grp,2)
    addDriver(hip_cntl,proxy_jnts[0],'parent')
    cntls.append(hip_cntl)
    #need to add support for end difference
    for i in range(len(proxy_jnts)-1):
        if i == len(proxy_jnts)-2:
            cntls.append(assembleIK([proxy_jnts[i],proxy_jnts[i+1]],solver='ikSCsolver',cntlSize=finalCntlSize,shape=finalCntlShape,rotation=rotation,offsetShapeDist=finalCntlOffset,skipDuplicateChain=1,attachAbove=0)[0])
        else:
            cntls.append(assembleIK([proxy_jnts[i],proxy_jnts[i+1]],solver='ikSCsolver',cntlSize=cntlSize,shape=shape,rotation=rotation,skipDuplicateChain=1,attachAbove=0)[0])

        #after the first, start adding follow controls
        if len(cntls)>2:
            cntl_offset = getParent(cntls[i],1)
            constraint = addDriver(cntls[i-1],cntl_offset,'parent')
            addDriver(rig_space,cntl_offset,'parent')
            enableInverseBlend(cntls[i],constraint,'follow')
    
    #endCntl stuff
    endCntl_offset = getParent(cntls[-1],1)
    end_constraint = addDriver(cntls[-2],endCntl_offset,'parent')
    addDriver(rig_space,endCntl_offset,'parent')
    enableInverseBlend(cntls[-1],end_constraint,'follow')
    #need to add support for special end control   
    #single chain IK with cntls on base that drives 
    return cntls


def addStickyTip(jnts, root_cntl,  shape='sphere'):
    """Experimental \n
        creates single chain IK handle and it's control with follow spaces. \n
        designed to refactor the creation of a position maintaining end effector out of the assembleIK Funtion

    Args:
        jnts (list): list of 3 joints
        root_cntl (str, optional): control shape to contain the sticky toggle attr. Defaults to ''.
        shape (str, optional): Sticky Tip Control Shape. Defaults to 'sphere'.
    
    Returns:
        str: name of new control handle
    """
    sticky_ik_handle = mc.ikHandle(sj=jnts[-2],ee=jnts[-1],sol='ikSCSolver')
    sticky_cntl = getDescendent(makeCntl(jnts[2], shape=shape),2)

    addDriver(sticky_cntl,sticky_ik_handle)

    #adds 'stickyTip' attr to root_cntl if needed
    if not mc.addAttr(root_cntl, q=1, ex='stickyTip'):
        mc.addAttr(root_cntl, ln='sitchyTip', at='float',max=1,min=0,dv=0)

    return sticky_cntl


def assembleSingleBash(jnts, shape='nail', name='', rotation=(0,0,90), 
                        cntlSize=1.0,position=(0,0,0),offsetShapeDist=(0,0,0)):
    """Experimental \n
    Bash chains are just lazy stacked iks--it also serves as a bootstrapped work around for adding a second layer of ik 
    because I need to revisit the execute order.
    Maybe rework the system when ui gets started.

    Args:
        jnts (list | str): joints to add controls to
        shape (str, optional): control shape. Defaults to 'nail'.
        name (str, optional): name of new joint chain. Defaults to ''.
        rotation (tuple, optional): rotation offset for control. Defaults to (0,0,90).
        cntlSize (float, optional): uniform control scale modifier. Defaults to 1.0.
        position (tuple, optional): positional offset of control from joint. Defaults to (0,0,0).
        offsetShapeDist (tuple, optional): Offset of shape from pivot. Defaults to (0,0,0).

    Returns:
        str: name of new control
    """

    proxy_jnts = duplicateChain(jnts, 'bash')
    for jnt, proxy_jnt in zip(jnts,proxy_jnts):
        addDriver(proxy_jnt,jnt,'parent')

    ik= assembleIK(proxy_jnts,solver='ikSCsolver',name=name, typ='bash',skipControl=1)[0]
    
    ik_cntl_grp= makeCntl(proxy_jnts[0],typ='bash',shape=shape,name=name,size=cntlSize,rotation=rotation,position=position,offsetShapeDist=offsetShapeDist)[0]
    ik_cntl= getDescendent(ik_cntl_grp,2)
    addDriver(ik_cntl,ik,'parent')
    addDriver(getParent(jnts[0]),proxy_jnts[0],'parent')
    return ik_cntl