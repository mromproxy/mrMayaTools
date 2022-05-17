"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 2.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Ui

Description: In Development
    Initializes Shelf for new installs, updates shelf if it exists

"""
import re
import os
import sys
try:
    import maya.cmds as mc
except:
    externalMode = 1    
try:
    from Utility.settingManager import SettingsManager
    settingsManager = SettingsManager()
    if settingsManager['modulePath'] not in sys.path:
        sys.path.append(settingsManager['modulePath'])
except:
    if os.path.dirname(os.path.dirname(__file__)) not in sys.path:
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class ButtonData(object):
    """
    This is where our button Data is stored. Below is a template Dict 
    {"iconText":"Example",
    "iconPath:"fileNew.png",
    "tooltip":"example Button",
    "script":"Path or File Name"}
    """
    def __init__(self,iconText,iconPath,tooltip,scriptName='',scriptPath=''):
        super(ButtonData,self).__init__()
        self.Data = {}
        self.iconText = iconText
        self.icon = iconPath
        self.tooltip=tooltip
        if scriptName:
            #need to search module for file name
            raise ValueError('ScriptName support is current being reworked, please provide a path instead')
            self.script = os.path.normpath( os.path.join(fileLocation,scriptName+'.py') )
        elif scriptPath:
            if re.search("^./",scriptPath):
                self.script = os.path.normpath( os.path.join(settingsManager.settings['modulePath'],scriptPath ) )
            else:
                self.script = os.path.normpath( scriptPath )
        else:
            self.script= '' 
        if not re.search('(?i)separator',iconText):
            self.__createCommand()



    def __createCommand(self,scriptPath):
        """Creates the sciprt to run the python file on button press

        Args:
            scriptPath (str): file path to be run on press
        """
        moduleLocation= os.path.normpath(settingsManager.settings['modulePath'])
        scriptLocation = os.path.normpath(os.path.basename(scriptPath)) #we need to derive the difference from moduleLocation and scriptPath
        scriptName = os.path.basename(scriptPath).split(".")[0]

        if moduleLocation in scriptLocation:
            importModulePath = '.'.join(scriptLocation.replace(moduleLocation+os.path.sep,'').split(os.path.sep),scriptName)
        else:
            moduleLocation = scriptLocation
            importModulePath = scriptName

        commandStart = 'import sys\nimport maya.cmds as mc\n\nif "{0}" not in sys.path:\nsys.path.append("{0}")\n'.format(moduleLocation)
        commandImport = 'import {0} as {1}\nreload({1}\n'.format(importModulePath,scriptName)
        commandRun = '{0}.run()'.format(scriptName)
        
        self.command = commandStart+commandImport+commandRun  
  

def run():
    pass

if __name__ == "__main__":
    fileLocation= os.path.normpath(os.path.dirname(__file__))
    sampleFileLocation = os.path.join(fileLocation, 'dag','rr')
    dirs = fileLocation.split(os.path.sep)
    sDirs = sampleFileLocation.split(os.path.sep)
    if fileLocation in sampleFileLocation:
        #print(sampleFileLocation.split(fileLocation))
        a = sampleFileLocation.replace(fileLocation+os.path.sep,'')
        print(a)
        print(os.path.normpath(a))
        print(a.split(os.path.sep))

#    if "RiggingTools" in dirs:
        #fileLocation = os.path.normpath( "\\".join(dirs[:dirs.index("RiggingTools")+1]) )
    else:
        pass