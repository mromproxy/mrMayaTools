"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 2.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Root

Description: In Development
    Installs the toolkit for easy use
    Drag and Drop into viewport to install a shelf and menu. Refer to documentation for more information


"""
import os
import sys
import re
import json

from Utility.settingManager import SettingsManager

try:
    from importlib import reload
except:
    print("//Running Maya 2022 or Earlier")


fileLocation= os.path.dirname(__file__)
if fileLocation not in sys.path:
    sys.path.append(fileLocation)



def onMayaDroppedPythonFile(arg):
    #Add current directory to sys.path
    fileLocation= os.path.dirname(__file__)
    if fileLocation not in sys.path:
        sys.path.append(fileLocation)
        
    #run reloadShelf to create
    import Ui.shelfSetup as shelfSetup
    reload(shelfSetup)
    shelfSetup.run()




# def createShelf():
#     if external:
#         return
#     if mc.shelfLayout('Auto_Rigging',ex=1):
#         mc.deleteUI('Auto_Rigging')
#     else:
#         mc.shelfLayout('Auto_Rigging',p='ShelfLayout')


if __name__ == "__main__":
    #__loadSettings()

    # with open(jsonPath,"r") as f:
    #     readFile = json.load(f)
    # print(readFile, type(readFile))
    #print(modulePath)

