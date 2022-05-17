"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 2.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Utility

Description: Settings Management class. In Development, currently not implemented

"""

import os
import json
#import sys
#import re


class SettingsManager(object):
    """
    Class for managing and maintaining tool settings
    """
    def __init__(self):
        super(SettingsManager,self).__init__()
        self.settings = self.__loadSettings()

    def __loadSettings(self,default=0):
        """Loads settings if they exist, generates default if not.

        Args:
            default (int, optional): force settings to default if default>0. Defaults to 0.

        Returns:
            dict: dictionary of setting values
        """
        jsonPath = os.path.join(os.path.dirname(__file__),'settings.json') 

        if not os.path.isfile(jsonPath) or default:
            if default:
                print("Restoring Settings To Default")
            else:
                print("No Settings found, Generating Default Settings")
            settings={}
            settings['modulePath'] = os.path.dirname(os.path.dirname(__file__))
            self.__writeSettings(settings)

        else:
            print('Reading Settings')
            with open(jsonPath,"r") as f:
                settings = json.load(f)
        return settings


    def __writeSettings(self,settings):
        if 'modulePath' in settings.keys():
            jsonPath = os.path.join(settings['modulePath'],'settings.json')     
        else:
            jsonPath = os.path.join(os.path.dirname(os.path.dirname(__file__)),'settings.json') 
        with open(jsonPath,"w") as f:
            json.dump(settings,f,indent=4)


if __name__ == '__main__':
    pass