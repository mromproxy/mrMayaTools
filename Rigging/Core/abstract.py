"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2020
Version: 1.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Core

Description: In Development / Testing
    Functions for generating common anatomically defined control structures.
    Most functions still require testing

"""

from maya import cmds as mc

from Utility.stringTools import *
import Utility.vectorMath as vec
from Rigging.Utility.general import organizeElement,getDescendent,getParent,addDriver
from Rigging.Controls.core import makeCntl,makeMasterCntl,enableInverseBlend,syncVis

from Rigging.Core.basic import assembleFK,assembleIK,duplicateChain
from Rigging.Core.geo import getFootPivots,makePivots,stackPivots


#needs testing
def assembleFootIK(ankle_jnt,verts='',geo='',ankle_ik='',
                    cntlShape='circle',name='foot',
                    cntlSize=1.0,rotation=(0,0,0),
                    forwardAxis='x',upAxis='y',
                    rotationAxis='z',pvSize=1.0):
    """Builds a foot IK system.

    Args:
        ankle_jnt (str): ankle joint to serve as the root of the IK system. Defaults to ''.
        verts (list, optional): list of vertices to use for evaluation foot pivots. Defaults to ''.
        geo (str, optional): geometry used to evaluate foot pivots. Defaults to ''.
        ankle_ik (str, optional): ik handle for ankle, one will be generated if not given. Defaults to ''.
        cntlShape (str, optional): shape for foot control. Defaults to 'circle'.
        name (str, optional): name of control. Defaults to 'foot'.
        cntlSize (float, optional): uniform scale modifier for control shape. Defaults to 1.0.
        rotation (tuple, optional): rotation modifier for control shape. Defaults to (0,0,0).
        forwardAxis (str, optional): forward Axis of foot. Defaults to 'x'.
        upAxis (str, optional): up axis of foot. Defaults to 'y'.
        rotationAxis (str, optional): primary rotation axis for ankle. Defaults to 'z'.
        pvSize (float, optional): uniform scale modifier for pole vector control. Defaults to 1.0.

    Returns:
        str: name of foot control
    """
    #pivots will be automated and sorted later, just need a quick in for now
    
    #this might need it's own chain to accomidate fk-ik switch
    
    #make pivots
    pivot_dict = getFootPivots(ankle_jnt=ankle_jnt,verts=verts,geo=geo)
    pivots = makePivots(pivot_dict, ankle_jnt,name=name)
    stackPivots(pivots)
    organizeElement(pivots[-1])
    #makes leg ik if need be
    if not ankle_ik:
        #gets joints
        knee_jnt= getParent(ankle_jnt,1)
        hip_jnt= getParent(ankle_jnt,2)
        leg_jnts=[hip_jnt,knee_jnt,ankle_jnt]
        #get's a distance for the pv since I don't wanna keep guessing numbers
        legLength=vec.mag(vec.vector(mc.xform(hip_jnt,q=1,t=1,ws=1),mc.xform(ankle_jnt,q=1,t=1,ws=1)))*2 #arbitraty scaling just cayse full leg seemed like a lot
        # makes the ik
            # should not be used with animal preset--pass ik in directly
        #need to revisit pvDist
        ik_return = assembleIK(leg_jnts,solver='ikRPsolver',name='leg',skipControl=1,pvDist=legLength/2,attachAbove=1,pvSize=pvSize)
        ik_handle = ik_return[-1]
        pv_cntl= ik_return[1]
    else:
        ik_handle=ankle_ik
    
    #make foot IKs
        #assumes no individual toes need to revisit digit support for this--aka refactor hand and mix into foot stack (toeUp pivot drives offset of digit base/ik?)
    #makes ball and toe ik jnts, and parents them to the existing 
    ball_jnt=getDescendent(ankle_jnt,1)
    toe_jnt=getDescendent(ankle_jnt,2)
    foot_jnts=[ball_jnt,toe_jnt]
    footIK_jnts = duplicateChain(foot_jnts, 'ik')
    for foot_jnt, footIK_jnt in zip(foot_jnts,footIK_jnts):
        addDriver(footIK_jnt,foot_jnt,'parent')
    #stitch together the name for the ankleIK_jnt and pop it in the front
    footIK_jnts.insert(0,replaceSegment(footIK_jnts[0],2,getSegment(ankle_jnt,2)))
    #organize chains
    mc.parent(footIK_jnts[1],footIK_jnts[0])

    #sc ball to toe, sc ankle to ball
    toe_ik=assembleIK([footIK_jnts[-2],footIK_jnts[-1]],solver='ikSCsolver',skipDuplicateChain=1,skipControl=1,attachAbove=0)
    ball_ik=assembleIK([footIK_jnts[0],footIK_jnts[1]],solver='ikSCsolver',skipDuplicateChain=1,skipControl=1,attachAbove=0)
    #places IKs--use parent constraint instead of parenting
    addDriver(pivots[0],toe_ik,'parent')
    addDriver(pivots[1],ankle_ik,'parent')
    addDriver(pivots[2],ball_ik,'parent')
    mc.parent(ankle_ik,pivots[1])
    mc.parent(ball_ik,pivots[2])

    #direction shouldn't matter since pivot are world oriented

    #make driven attr list
    rotate_roll= ''.join(('rotate',forwardAxis.upper()))
    rotate_pitch= ''.join(('rotate',rotationAxis.upper()))
    rotate_yaw= ''.join(('rotate',upAxis.upper()))

    rotate_roll= ''.join(('rotate','Z'))
    rotate_pitch= ''.join(('rotate','X'))
    rotate_yaw= ''.join(('rotate','Y'))

    #merge inside outside roll in future
    attr_list=[
        'toeWiggle',
        'toePivotUp',
        'toePivotTwist',
        'ballPivotUp',
        'ballPivotTwist',
        'HeelPivotUp',
        'HeelPivotTwist',
        'insideRoll',
        'outsideRoll',
        'ankleRoll',
        'anklePitch',
        'ankleYaw'
        ] 
    
    #driver targts need update
    driven_list=[
        '.'.join((pivots[0],rotate_pitch)), #toeWiggle
        '.'.join((pivots[2],rotate_pitch)), #toePivotPitch
        '.'.join((pivots[2],rotate_yaw)), #toePivotYaw
        '.'.join((pivots[1],rotate_pitch)), #ballPitch
        '.'.join((pivots[1],rotate_yaw)), #ballYaw
        '.'.join((pivots[3],rotate_pitch)), #heelPitch  
        '.'.join((pivots[3],rotate_yaw)), #heelPitch
        '.'.join((pivots[4],rotate_roll)), #insideRoll
        '.'.join((pivots[5],rotate_roll)), #outsideRoll
        '.'.join((pivots[6],rotate_roll)), #ankleX
        '.'.join((pivots[6],rotate_pitch)), #ankleY
        '.'.join((pivots[6],rotate_yaw)) #ankleZ
    ]

    foot_cntl_grp = makeCntl(pivots[-2],typ='mstr',shape=cntlShape,name=name,size=cntlSize,rotation=rotation)[0]
    foot_cntl = getDescendent(foot_cntl_grp,2)
    foot_offset = getDescendent(foot_cntl_grp,1)
    addDriver(foot_cntl,pivots[-2])
    #add and connect attrs to mstr cntl
    presel = mc.ls(selection=1)
    mc.select(foot_cntl)
    for attr,driven in zip(attr_list,driven_list):
        mc.addAttr(ln=attr,k=1,at='float')
        mc.connectAttr('.'.join((foot_cntl,attr)),driven,f=1)
    organizeElement(foot_cntl_grp)
    ## NOTE
    # This needs re-assessing how following works.
    # Ik weight always on, fkik switch only turns down fk weight
    # and turns up inverse IK matrix weight?
    """
    if mc.objExists(ankle_fk_jnt):
        rig_space = getRigSpace(getSegment(ankle_jnt,0))
        ankle_fk_jnt=replaceSegment(footIK_jnts[0],-2,'fk')
        constraint = addDriver(ankle_fk_jnt,pivots[-1],'parent')
        addDriver(rigSpace,pivots[-1],'parent')
        enableInverseBlend(foot_cntl,constraint,'fkik',0,1)
        #also need to pair bind's constrain to same attr
    #parent constraint cntl offset to ankle bind for leg follow?
    return foot_cntl
    """
    return foot_cntl    


#ready but needs stress test and clav + end pairing tests
def assembleBasicLimb(jnts,mstrCntl='',clav=0,
                    fk=1,fkCntlSize=1.0,fkRotation=(0,0,0),fkTyp='nested',
                    fkRotationAxis='z',fkUpAxis='y',fkForwardAxis='x',fkShape='circle',fkPreset='',
                    ik=1,ikSolver='ikRPsolver', ikName='limb', ikShape='nail', 
                    ikCntlSize=1, ikRotation=(0,0,90),pvSize=1, pvDist=1, 
                    ikPreset='', ikForwardAxis='x',stickyTip=False, 
                    stickyShape='sphere',
                    mstrCntlShape='cone',mstrName='arm',mstrCntlSize=1.0,
                    mstrRotation=(0,0,180),mstrOffset=(1.2,0,0)):
    """A wrapper function for the generation of a limb's control system \n
    This will be moved to the Control System class once that is implemented

    Args:
        jnts (list): joints to build controls for
        mstrCntl (str, optional): Master Control if it already esists. Defaults to ''.
        clav (int, optional): toggle to add support for a clavicle-like joint above the chain. Defaults to 0.
        fk (int, optional): If an fk chain should be made. Defaults to 1.
        fkCntlSize (float, optional): uniform scale of the fk contorls. Defaults to 1.0.
        fkRotation (tuple, optional): rotational offset for fk controls. Defaults to (0,0,0).
        fkTyp (str, optional): type of fk structure to make. Options are 'nested' and 'base' Defaults to 'nested'.
        fkRotationAxis (str, optional): the primary rotational axis. Used for 'base' fk structures. Defaults to 'z'.
        fkUpAxis (str, optional): Defunct, left for compatability. Defaults to 'y'.
        fkForwardAxis (str, optional): Defunct, left for compatability. Defaults to 'x'.
        fkShape (str, optional): control shape for fk controls. Defaults to 'circle'.
        fkPreset (str, optional): Defunct, left for compatability. Defaults to ''.
        ik (int, optional): toggle to add an ik structure. Defaults to 1.
        ikSolver (str, optional): type of IK solver. Options are 'ikRPsolver' and ikSCsolver'. Defaults to 'ikRPsolver'.
        ikName (str, optional): basename for ik system. Defaults to 'limb'.
        ikShape (str, optional): ik control shape. Defaults to 'nail'.
        ikCntlSize (int, optional): uniform scale modifier for ik control. Defaults to 1.
        ikRotation (tuple, optional): rotational offset of ik control. Defaults to (0,0,90).
        pvSize (int, optional): uniform scale modifier for pv control. Defaults to 1.
        pvDist (int, optional): offset distance of pv control. Defaults to 1.
        ikPreset (str, optional): Defunct, left for compatability. Defaults to ''.
        ikForwardAxis (str, optional): Defunct, left for compatability. Defaults to 'x'.
        stickyTip (bool, optional): option to add stickyTip to ik system. Defaults to False.
        stickyShape (str, optional): control shape for stickyTip. Defaults to 'sphere'.
        mstrCntlShape (str, optional): control shape of master control. Defaults to 'cone'.
        mstrName (str, optional): name of master control. Defaults to 'arm'.
        mstrCntlSize (float, optional): uniform scale modifier for master control shape. Defaults to 1.0.
        mstrRotation (tuple, optional): rotational offset for master control. Defaults to (0,0,180).
        mstrOffset (tuple, optional): positional offset for master control. Defaults to (1.2,0,0).
        

    Returns:
        _type_: _description_
    """
    controls = []
    if fk==1:
        fk_cntls = assembleFK(jnts,fkCntlSize,fkRotation,fkTyp,fkRotationAxis,fkUpAxis,fkForwardAxis,fkShape,fkPreset)
    if ik==1:
        ik_cntls = assembleIK(jnts=jnts,solver=ikSolver,shape=ikShape,cntlSize=ikCntlSize,rotation=ikRotation,pvSize=pvSize,pvDist=pvDist,preset=ikPreset,forwardAxis=ikForwardAxis,stickyTip=stickyTip,stickyShape=stickyShape,name=ikName,addClav=clav,attachAbove=1)
    
    if fk and ik:
        if not mstrCntl:
            mstr_cntl = makeMasterCntl(jnts[-1],cntlSize=mstrCntlSize,rotation=mstrRotation,cntlShape=mstrCntlShape,name=mstrName,offset=mstrOffset)
        else:
            mstr_cntl= mstrCntl
        mc.select(mstr_cntl)
        mc.addAttr(ln='fkik', at='float',max=1,min=0,dv=0,k=1)
        for jnt in jnts:
            #assumes there is only a single constraint
            constraints = list(set(mc.listConnections(jnt,type='constraint')))
            for check in constraints:
                if 'bind' in check:
                    constraint=check
            enableInverseBlend(mstr_cntl,constraint,'fkik',0,1)
        syncVis(mstr_cntl,'fkik',ik_cntls,fk_cntls)
        return mstr_cntl
    else: 
        return fk+ik


#ready, kind of touchy tho
def assembleHand(root,
    mstrCntl='',
    name='hand',
    mstrShape='cone',
    mstrOffset=(.85,.85,0),
    mstrRotation=(0,0,0),
    mstrCntlSize=1,
    fk=1, 
    fkShape='circle',
    fingerAxis='z',
    upAxis='y',
    fingerType='base',
    fkRotation=(0,0,90),
    fkCntlSize=1,
    ik=0, 
    ikCntlSize=1, 
    ikRotation=(0,0,90),
    ikShape='nail',
    ikStickyTip=0):
    """Experimental \n
    Creates a hand control system.

    Args:
        root (str): name of the joint containing all fingers
        mstrCntl (str, optional): Master Control to drive the fingers, will create one if not provided. Defaults to ''.
        name (str, optional): name of master control. Defaults to 'hand'.
        mstrShape (str, optional): control shape for master control. Defaults to 'cone'.
        mstrOffset (float, optional): positional offset of master control shape. Defaults to (.85,.85,0).
        mstrRotation (tuple, optional): rotational offset of master control. Defaults to (0,0,0).
        mstrCntlSize (int, optional): uniform scale modifer for master control. Defaults to 1.
        fk (int, optional): toggle to add fk controls to fingers. Defaults to 1.
        fkShape (str, optional): fk control shape. Defaults to 'circle'.
        fingerAxis (str, optional): primary roation axis for each digit. Defaults to 'z'.
        upAxis (str, optional): Defunct, left for compatibility. Defaults to 'y'.
        fingerType (str, optional): type of control system for each fk finger. Defaults to 'base'.
        fkRotation (tuple, optional): rotational offset for each fk finger control. Defaults to (0,0,90).
        fkCntlSize (int, optional): uniform scale modifier for fk controls. Defaults to 1.
        ik (int, optional): toggle to add ik system to each finger. Defaults to 0.
        ikCntlSize (int, optional): uniform scale modifier for ik control. Defaults to 1.
        ikRotation (tuple, optional): rotational offset for ik control. Defaults to (0,0,90).
        ikShape (str, optional): ik control shape. Defaults to 'nail'.
        ikStickyTip (int, optional): toggle to add stickyTips to ik systems. Defaults to 0.

    Returns:
        str: name of base control
    """

    #thumb needs some tlc
    #currently doesn't support metacarpals
    #need to check if hand_cntl already exists
    if not mstrCntl:
        mstrCntl = makeMasterCntl(root,mstrCntlSize,mstrShape,
            mstrRotation,name,mstrOffset)

    finger_roots = mc.listRelatives(root,c=1)
    fkParentDriver = replaceSegment(root,-2,'fk')
    if mc.objExists(fkParentDriver):
        fkParentDriver
    for finger in finger_roots:
        count = len(mc.listRelatives(finger,ad=1))
        jnts=[finger]
        for i in range(count-1):
            jnts.append(getDescendent(jnts[i],1))

        if fk==1:
            if not mc.objExists(fkParentDriver):
                fkParentDriver = duplicateChain(root,typ='fk',addID='fkik')[0]
                addDriver(root,fkParentDriver,'parent')
            fk_cntl= assembleFK(jnts,rotationAxis=fingerAxis,rotation=fkRotation,shape=fkShape,cntlSize=fkCntlSize,typ='base',parentDriver=fkParentDriver)
            addDriver(root,getParent(fk_cntl,2),'parent',mo=1)

        if ik==1:
            #sc iks need to affect the rotate of the end jnt in not sticky,
            #if stick needs to effect cntl grp of sticky?
            ik_cntl= assembleIK(jnts,solver='ikSCsolver',cntlSize=ikCntlSize,rotation=ikRotation,shape=ikShape)
            addDriver(root,getParent(ik_cntl,2),'parent')

        #need to get constraints
        if fk and ik:
            mc.select(fk_cntl)
            mc.addAttr(ln='fkik', at='float',max=1,min=0,dv=0,k=1)
            for jnt in jnts:
                #assumes there is only a single constraint
                constraint = list(set(mc.listConnections(jnt,type='constraint')))[0]
                enableInverseBlend(fk_cntl,constraint,'fkik',0,1)
            #needs to be IK to fk only    
            syncVis(fk_cntl,'fkik',ik_cntl)
            #get constraints on jnts
            #enable inverseBlend on each, driven by fkik attr on base
            #enable syncVis between cntls and fkik attr
    return mstrCntl
