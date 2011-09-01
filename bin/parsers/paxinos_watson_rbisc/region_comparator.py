#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2011 Piotr Majka, Jakub M. Kowalski                   #
#                                                                             #
#    3d Brain Atlas Reconstructor is free software: you can redistribute      #
#    it and/or modify it under the terms of the GNU General Public License    #
#    as published by the Free Software Foundation, either version 3 of        #
#    the License, or (at your option) any later version.                      #
#                                                                             #
#    3d Brain Atlas Reconstructor is distributed in the hope that it          #
#    will be useful, but WITHOUT ANY WARRANTY; without even the implied       #
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.         #
#    See the GNU General Public License for more details.                     #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along  with  3d  Brain  Atlas  Reconstructor.   If  not,  see            #
#    http://www.gnu.org/licenses/.                                            #
#                                                                             #
###############################################################################

import xml.dom.minidom as dom
import sys
import string

"""
@change: śro, 23 lut 2011, 11:17:11 CET
This file is a temporary solution and will be replaced in further versions of
the software
"""

class RegionComparator:
    """
    Class for post processing of traced files. At this moment, class has
    following capabilities:

        1. Find regions which are defined by the same path (the same path means
        that the definition of the path <d> attribute is the same for those
        paths). In other words find regions with the same <d> tags.
    
        2. Find corresponding labels for those regions.
    
        3. Remove all but one path.
            - Leave only one label (the first one) defining given region
            - Mark other labels as "spot labels" and make them red
    
    As an input for this class traced file should be provided. Traced file may
    have all kinds of labels (normal, spot label, comment label).
    Effect it that there should be no overlapping areas in output file, no new
    unlabelled areas and some new spotlabels
    """
    
    def __init__(self):
        """
        Constructor for RegionComparator. Constructor sets some initial settings
        allowing class for immediate file processing
        
        @return: Nothing, it is class constructor
        """
        self.svgdom=None
        self.listOfChanges=None
        self.documentStatus=None
    
    def processOneSlide(self, svgdom):
        """
        @type  svgdom: DOM object
        @param svgdom: Complete SVG document
        
        @return: Nothing, SVG drawing is modified in-place
        
        Proesses given SVG drawing:
            1. Clears current RegionComparator cache
            2. Determines list of identical paths and generates list of chagned
               for clearing the document.
            3. Meanwhile dumps changes that were applied
        """

        # Clearing cache is very, very important as without clearing cache we
        # can easily mess up whole svg drawing
        self.clearCache()
        self.svgdom=svgdom
        self.extractPathDefinitions()

        # At this step one can see what changes will be applied
        # print >>sys.stderr, self.listOfChanges
        self.applyChanges()

    def clearCache(self):
        """
        Prepares class instance for processing another slide by setting
        parameters to their default values (removig current document reference,
        clearing list of corrections and setting document status to unprocessed)

        @return: Nothing
        """
        self.svgdom=None
        self.listOfChanges=None
        self.documentStatus=None

    def extractPathDefinitions(self):
        """
        Creates a list of changes that are to be made in order to eliminate
        duplicating path elements.

        List of changes is created in following way:

            1. Extract path definition (d tag) and ID from each path element
            2. Sort path definitions as they are simply strings.
            3. For each path definition find paths elements with the same d tag.
            4. Now the hardest step to describe:

        Then, for each different path definition algorithm searches for paths
        with identical definitions then collects those paths and splits them
        into two groups. The first group contains only one path element (the
        last path element from the list) and this path element will be
        preserved. All but the last paths are stored in the other group and are
        to be deleted.

        Function returns dictionary with two elements:
        C{preserve} contains IDs of path elements that would not be deleted
        while C{remove} contains IDs of path elements that should be removed.
        This function do not perform any changes with labels or paths - those
        operation are performed by another function.

        @return: Nothing. Only sets internal field listOfChanges
        """

        # Check if cache is clear as without clear chache we cannot proceed
        if self.documentStatus!=None or\
                self.listOfChanges!=None:
            print >>sys.stderr, "Error: Cache is not clear."
            return

        # Get all path elements in SVG file
        allPathsElements=self.svgdom.getElementsByTagName('path')

        # Extract all information about paths in SVG file:
        # and store them in pathData list
        pathData=\
                map( self.extractPathData, allPathsElements)

        # Sort extracted path definitions by extracted <d> element
        pathData.sort(key=lambda path: path[1])

        # Initialize dictionary that is going to be returned
        toChange={'preserve':[],'remove':[]}

        # Now the hardest thing: determining which elements will be considered
        # as an actual paths and labels and which of them will be removed or
        # replaced. The approach is following: for each extracted path
        # definition find all other paths with the same definition. Store ID's
        # of those paths in temporary array.
        # Then for all id's of paths with the same definition take the last one
        # and move the id to list of paths that will be preserved. All other
        # paths are denoted as paths to remove. If there is only path with given
        # definition if would be preserved while list of paths to remove would
        # be empty
        
        for pathDef in pathData:
            # pathDef[1] is the path definition
            tempresult = ([x[0] for x in pathData if x[1]==pathDef[1]], pathDef[1])
            elementToBePreserved=tempresult[0].pop()
            elementsToBeRemoved=tempresult[0]

            toChange['preserve'].append(elementToBePreserved)
            toChange['remove'].append(elementsToBeRemoved)
        
        # Make flat list of unique id's to remove and to preserve
        toChange['preserve']=list(set(flatten(toChange['preserve'])))
        toChange['remove']  =list(set(flatten(toChange['remove'])))
        
        # Update class listOfChanges field and then update document status
        self.listOfChanges=toChange
        self.documentStatus="ChangesExtracted"
        
    def extractPathData(self, pathElement):
        """
        Extracts provided path's definition (C{d} tag) and it's ID element value

        @type  pathElement: DOM object
        @param pathElement: Path SVG element to extract data from.

        @return: (tuple) Tuple containing id of povided path and it's definition
        (id, definition)
        """
        
        # Extract elements which are interesting 
        returnTuple=(\
                pathElement.getAttribute('id'),\
                pathElement.getAttribute('d'))
        
        return returnTuple
    
    def applyChanges(self):
        """
        @return: Nothing only internal svgdom is modified but no value is
        returned.

        Applies changes from list of changes created by
        L<extractPathDefinitions{extractPathDefinitions}>
        Also process labels corresponding to removed or changed paths.

        Changes are applied using following approach (this approach is actually
        very stupid because it is much better to use getElementById but this
        method is not working.
            1. Iterate over all path elements (again !!:( )
            2. Check if id of this path is in C{remove} list. Delete if it is.
            Store id of removed path, extract ID of corresponding text label and
            then store this id of text label. If ID is in C{preserve} list - do
            nothing.
            4. Then iterate over all text labels (well, I know extremely
            Ineffective). 

        """
        # Check if list of changes is defined by veryfying documentStatus and
        # validity of list of changes
        if self.documentStatus!="ChangesExtracted" or\
                self.listOfChanges==None:
            print >>sys.stderr, "Error: There is no valid list of changes"
            print >>sys.stderr, "       No changes applied."
            return
        
        # Initialize list of textElementsIDs that will be changed
        labelsToChangeID=[]
        
        # Create alias for list of changes:
        changes=self.listOfChanges
        
        # Iterate again over all path elements (again), remove paths that are
        # denoted as path to remove and store IDs of text labels associated with
        # them
        for path in self.svgdom.getElementsByTagName('path'):
            if path.getAttribute('id') in changes['remove']:
                print >>sys.stderr, "Removing id %s" % path.getAttribute('id')
                path.parentNode.removeChild(path)
        
                # Extract ID of text label corresponding to removed path
                # We blindly assume that this ID may be correctly extracted
                # by splitting pathID by "_" and taking the middle element.
                # Finally store labelID in array
                textLabelIdElem=path.getAttribute('id').split('_')[1]
                labelsToChangeID.append(textLabelIdElem)
        
        # Iterate over all text labels and if label set type of given label to
        # spotlabel then set color of this label to red in order to highlight
        # this label in final drawing
        for textLabel in self.svgdom.getElementsByTagName('text'):
            if textLabel.getAttribute('id') in labelsToChangeID:
                print >>sys.stderr, "Updating label %s" % textLabel.getAttribute('id')
                self.setTextLabelType(textLabel, "spotlabel")
    
    def setTextLabelType(self, textLabel, labelType):
        """
        @type  textLabel: DOM object
        @param textLabel: Text SVG element to be modified.
        @type  labelType: string
        @param labelType: Type of given label

        @return: Nothing. C{textLabel} object is modified by reference

        Changes type of the label C{textLabel} to type C{labelType}.
        Tries to prevent from assigning ambigous types (there should be only one
        special char denoting label type).

        C{spotlabel} are supposed to have "." as first char while
        C{normallabels} are denoted by giving them "," as first character of the
        label.
        """

        # Well... next statements are self-explaining...
        if labelType=="spotlabel" and\
                textLabel.firstChild.nodeValue[0]!=".":
            textLabel.firstChild.nodeValue=\
                    "."+textLabel.firstChild.nodeValue
            textLabel.setAttribute('fill',"#ff0000")

            # Remove style attribute because it is messing up.
            if textLabel.hasAttribute('style'):
                tempDict={}
                for elemSt in textLabel.getAttribute('style').split(';'):
                    elemSp = elemSt.split(':')
                    tempDict[str(elemSp[0])]=elemSp[1]
                tempDict['fill']="#ff0000"
                textLabel.setAttribute('style',";".join([":".join(i) for i in tempDict.iteritems()]))
                
        if labelType=="normalLabel" and\
                textLabel.firstChild.nodeValue[0] in [",","."]:
            textLabel.firstChild.nodeValue=\
                    textLabel.firstChild.nodeValue[1:]
    
def flatten(x):
    """
    flatten(sequence) -> list
    
    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    
    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]

    @type  x: iterable sequence
    @param x: sequence to flat

    @return: (list). Flattened list. Read description for firther information.
    """
    
    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

if __name__=='__main__':
    # Create RegionComparator class instance
    rg = RegionComparator()
    
    InputFilename  = sys.argv[1]
    OutputFilename = sys.argv[2]
    
    rg.processOneSlide(dom.parse(InputFilename))
    rg.svgdom.writexml(\
            open(OutputFilename,'w'),\
            indent="", addindent="", newl="")
