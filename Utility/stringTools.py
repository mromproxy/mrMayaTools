"""
copyright Matthew Rom 2022
______________________________
Created: 2020
Updated: 5/10/2022
Version: 2.0

@author: Matthew Rom
@email: matthewrom.td@gmail.com

Module: Utility

Description: Collection of name management functions.
    This autorig relies on tags and name segments to identify and traverse the rig.
    The expected and generated patterns are as follows: ['char','typ','name','side','IDs','class']
        such that IDs can be any amount of additional tags. 
    Currently all processes use "_" for delimination, 
        but support for namespaces is being added for an updated pattern of: Char:Typ:Name_Side_[IDs]_class
    Please refer to Documentation/NamingConventions.md for examples of names, IDs, solutions to side assignments, etc

"""

import re
import maya.cmds as mc



##########################################################
##########################################################
#                        Internal                        #
##########################################################
##########################################################

def __nameToSegments(name):
    """
    Seperates string into segments deliminated by "_" or ":"
    Note: While parsing supports namespaces, this is still being implemented
        and currently namespaces are converted 

    Args:
        name (str): string to split

    Returns:
        list : name segments
    """
    if ':' not in name:
        return name.split('_')
    else:
        segments = name.split(':')
        for segment in segments:
            if re.search('_',segment):
                currentIndex = segments.index(segments)
                toParse = segments.pop(currentIndex)
                additionalSegments = toParse.split('_')
                segments = segments[0:currentIndex] + additionalSegments + segments[currentIndex:]
    return segments


def __segmentsToName(segments,namespace=0):
    """Wrapper placed in anticipation of namespace support

    Args:
        segments list: preorded list

    Returns:
        _type_: _description_
    """
    if namespace:
        return ':'.join(segments[:2]) + ':' + '_'.join(segments[2:])
    else:
        return '_'.join(segments)


def __getSegmentByID(name , ID ):
    """Return segment for given ID

    Args:
        name (str): string to search
        ID (str): ID to be returned

    Returns:
        str: string segment
    """
    segmentIndices = ['char','typ','name','side','IDs','class']
    segments = __nameToSegments(name)
    if re.search('(?i)id',ID):
        return segments[4:-1]
    elif re.search('(?i)class',ID):
        return segments[-1]
    else:
        return segments[ segmentIndices.index(ID)]
    

def __getSegmentByIndex( name , index):
    return __nameToSegments(name)[index]


##########################################################
##########################################################
#                    Name Management                     #
##########################################################
##########################################################


def getSegment( name , index ):
    """Returns the segment at the give index / ID.
        Expected Indices: [0:'char',1:'typ',2:'name',3:'side',4+:'IDs',-1:'class']
    Args:
        name (str): name to parse
        index (str | int): Id or index to return
    """
    if isinstance(index, str):
        return __getSegmentByID( name , index )
    if isinstance(index, int):
        return __getSegmentByIndex( name , index)


def replaceSegment(name, index, replacement='NA'):
    """Replace a segment of a name. 
        Expected Indices: [0:'char',1:'typ',2:'name',3:'side',4+:'IDs',-1:'class']

    Args:
        name (str): name to be editted
        index ( str or int, optional): ID or index of segment you wish you change.
        replacement (str, optional): new segment text. Defaults to 'NA'.

    Returns:
        str: updated name
    """
    segments = __nameToSegments(name)
    segmentIndices = ['char','typ','name','side','IDs','class']
    if isinstance(index, str):
        index = segmentIndices.index(index)
    segments[index] = replacement
    return __segmentsToName(segments)


def appendID(name,id=''):
    """
    adds an id to the end of the id list
    """
    segments = __nameToSegments(name)
    segments.insert(-2,id)
    return __segmentsToName(segments)


    
