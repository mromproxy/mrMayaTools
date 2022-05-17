"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 0.1

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Rigging.Core

Description: In Development
    Primary Class for maintaining a Rig

"""

import maya.cmds as mc

class Rig(object):
    def __int__(self):
        super(Rig,self).__init__()
        #Abstracts
        self.Name = '' #Serves as the BaseName Space
        self.Classification = '' #What is it-- Biped, Quad, possibly more
        self.Joints = ''
        self.Meshes = ''
        self.ExportSets = {'Animation':'','Rig':''}
        self.Structures = {}
        self.Spaces = ''
        self.FilePath = '' #location of json

        self.Nodes = []