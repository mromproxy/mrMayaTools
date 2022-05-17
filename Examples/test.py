"""
A quick test 
"""
import os
import sys
import maya.cmds as cmds

modulePath = r''
if modulePath not in sys.path:
    sys.path.append(modulePath)
    
from Rigging.Utility.general import deleteRig
import Rigging.Core.abstract as rigAbs

deleteRig('RBT')
jnts = ['RBT_bind_clavicle_L_jnt', 'RBT_bind_shoulder_L_jnt', 'RBT_bind_elbow_L_jnt']
rigAbs.assembleBasicLimb(jnts,fkCntlSize=10,
                        ikCntlSize=10,pvDist=10, pvSize=5,
                        mstrOffset=(0,0,30),mstrCntlSize=2,mstrCntlShape='sphere')