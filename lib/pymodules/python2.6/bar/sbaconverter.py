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

"""
The module provides class necessary to translate data from ScalableBrainAtlas to CAF dataset.

G{importgraph}
"""

import json
import urllib2
import numpy as np
import os, sys
import xml.dom.minidom as dom
from string import *

from base import barPath, barTracedSlideRenderer, barTracedSlide,barBregmaMetadataElement, barTransfMatrixMetadataElement
from parsers import barExternalParser
STRUCTURE_NAME_TEMPLATE = "structure%d_label%d_%s"

#TODO: move to base.py
def cleanStructName(structName):
    """
    Provided acronyms are usually fine but sometimes they are not
    compatibile with 3dBar naming convention. Here we process them so they
    can pass 3dBAR name validataion.
    
    @type  structName: C{str}
    @param structName: initial sturcture name, potentially invalid
    
    @rtype: C{str}
    @return: structure name transformed in the way that passes 3dBAR name validation
    """
    # transform name into its valid form by replacing '(',')', '$', '/',
    # "'", '+', ' ' characters with their names and stripping hypens
    # from beginning and end of the string
    replaceMap = [('(', 'OpParen'),
                  (')', 'ClParen'),
                  ('$', 'Dollar'),
                  ('/', 'Slash'),
                  ('\\', 'Backslash'),
                  ('+', 'Plus'),
                  (' ', '-'),
                  ('\'', 'Prime')]
    
    return reduce(lambda x, (y, z): x.replace(y, z),
                  replaceMap,
                  structName).strip('- ')


class barSBAParser(barExternalParser):
    """
    Generic class for translating data from ScalableBrainAtlas to CAF dataset.
    This class should be subclassed for each template available on SBA
    website and customized according to template-specific features.
    """
    _requiredInternalData = barExternalParser._requiredInternalData +\
            [ 'renderingProperties', 'templateName', 'tracingProperties',
              'slideTemplate', 'inputDirectory', 'jsonFilelist', 'templateUrl']
    
    def __init__(self, **kwargs):
        barExternalParser.__init__(self, **kwargs)
        
        # All JSON files are loaded into this dictionary
        self._sbaImportData      = {}
        
        # Initialize structure indexer
        self.slideStructureIndexer = 0
    
    def parse(self, slideNumber,\
                    generateLabels = True,\
                    useIndexer = True,\
                    writeSlide = True):
        """
        @param slideNumber: int
        @type  slideNumber: Number of slide which will be parsed
        
        Creates svg document from JSON file for given slide number.
        Slide is created using following workflow:
        
            - Get template of empty slide
            - Get list of structures in given slide
            - Extract definitions of paths corresponding to structures,
              add them into slide
            - Extract metadata and put in into SVG slide
            - Generate positions of labels corresponding to created paths and
              append therm
        """
        barExternalParser.parse(self, slideNumber)
        tracedSlide = barTracedSlideRenderer(\
             slideTemplate = self.slideTemplate,\
             rendererConfiguration = self.renderingProperties,\
             tracingConfiguration  = self.tracingProperties)
        
        # Define string version of current slide number 
        # I do it because loaded json files are converted to dictionaries
        # and integer keys are converted to string keys ( 1 goes to '1')
        # so all keys are strings
        CurrentSlideNumber = str(slideNumber)
        
        # Extract structures that are defined in slide >CurrentSlideNumber<
        # There are two ways of indexing structures: by dictionary (keys are
        # slidenumbers) or in list.
        # Code belows tries to load data in both ways
        try:
            CurrentSlideStructures = self._sbaImportData['brainslices'][CurrentSlideNumber]
        except TypeError:
            CurrentSlideStructures = self._sbaImportData['brainslices'][int(CurrentSlideNumber)]
        
        # CurrentSlideStructures is dictionary that maps color in hexagonal
        # format to number of polygon corresponding to given structure
        # eg. {'fafafa':[0]}
        # so key id color-encoded name of the structure and list is list of
        # path indexes stored in self.sbaImportData['svgpaths'] list
        
        # Dump information about structures in given slide
        print >>sys.stderr, "Converting slide number:\t%d" % slideNumber
        if __debug__:
            print >>sys.stderr, "\tThere are %d structures defined." % len(CurrentSlideStructures)
            print >>sys.stderr, "\tInitializing structure index."
        
        # Now we iterate over all structures in given slide
        for structure in CurrentSlideStructures.keys():
            # TODO come up with idea how to do it better
            # Now two thing are passed structureID, and list of path indexes
            
            # Create path definition
            map(tracedSlide.addPath,
                  self._parseSingleStructure(structure, CurrentSlideStructures[structure]))
        
        # Extract stereoraxic transformation matrix and put it into SVG slide
        offsets=[\
                self._sbaImportData['xyscaling'][str(CurrentSlideNumber)][0:2],
                self._sbaImportData['xyscaling'][str(CurrentSlideNumber)][2:]]
        
        spatialData = self._saveTransformationAsMetadata(offsets,\
                      self._sbaImportData['bregma'][slideNumber])
        tracedSlide.updateMetadata(spatialData)
        corrArray = np.array([[0.1,0,0],[0,0.1,0],[0,0,0]])
        
        tracedSlide.affineTransform(corrArray)
       
        # Perform additional actions if requested
        if generateLabels:
            tracedSlide.generateLabels()
        if writeSlide: tracedSlide.writeXMLtoFile(self._getOutputFilename(slideNumber))
        if useIndexer: self.indexer.indexSingleSlide(tracedSlide, slideNumber)
        return tracedSlide 
    
    def _parseSingleStructure(self, structureIDbyFill, structurePathList):
        """
        @type  structureIDbyFill: string
        @param structureIDbyFill: color-encoded structure ID which will be
                                  processed
        
        @type  structurePathList: list
        @param structurePathList: list of path corresponding to given structure
                                  on given slide
        
        @return: None
        
        Function extracts all paths from given slide having filled with
        'structureIDbyFill' color. At the end of processing, path is appended to
        the slide.
        
        @todo: # TODO: Arrange code in each function to make it more reusable
        """
        # Define and store fill color and name of the structure
        currentStructureData = {}
        currentStructureData['fillcolor'] = structureIDbyFill
        currentStructureData['name'] = self._getStructureName(structureIDbyFill)
        
        # Process all polygons describing given structure in a loop.
        # (there may by more than one polygon describing given structure per
        # slide)
        retPaths = []
        for pathNumber in structurePathList:
            # Increase structure iterator value: to make ID's uniqe
            self.slideStructureIndexer+=1
            # Gater all requires path properties and create path object
            newPathDefinition = self._sbaImportData['svgpaths'][pathNumber]
            newPathColor      = currentStructureData['fillcolor']
            newPathID         = self._getPathID(currentStructureData['name'])
            try:
                pathToAppend = barPath(newPathID,\
                        newPathDefinition, newPathColor, clearPathDef = True)
                retPaths.append(pathToAppend)
            except ValueError:
                pass
        
        # Dumping diagnostic information        
        if __debug__:
            print >>sys.stderr, "\t\tExtracting structure %s" % currentStructureData['name']
            print >>sys.stderr, "\t\tFill color of current structure %s" % currentStructureData['fillcolor']
            print >>sys.stderr, "\t\tNumber of polygons creating this structure %d" % len(structurePathList)
            print >>sys.stderr, "\t\t\t!FULLDUMP!Full structure dump: %s" % structurePathList
            print >>sys.stderr, "\t\tStarting processing paths."
        
        return retPaths
        
    def _getPathID(self, structName):
        """
        @return: (string) ID of path with given name. Uniqness if ID is
        guaranteed by internal index.
        """
        # TODO define pathID template and define in in configuration file
        n = self.slideStructureIndexer
        return STRUCTURE_NAME_TEMPLATE %  (n, n, structName)
    
    def _getStructureName(self, structureIDbyFill):
        """
        @type  structureIDbyFill: string
        @param structureIDbyFill: color-encoded structure name to be decoded
        
        @return: (string) name of the structure corresponding to gocen fill
        color.
        
        Function translates fill color to structure name (structure
        abbreviation to be precise). Fill and name are in 1:1 relation (each
        fill color is uniqe).
        """
        # Provided acronyms are usually fine but sometimes they are not
        # compatibile with 3dBar naming convention. Here we process them so they
        # can pass 3dBAR name validataion.
        structName =  self._sbaImportData['rgb2acr'][structureIDbyFill].strip()
        cleanName = self._cleanStructName(structName)
        
        if __debug__:
            print >>sys.stderr, "\t\tCleaning structure name '%s' -> '%s'" % (structName, cleanName)
        return cleanName
   
    def _cleanStructName(self, structName):
        """
        An alias to C{L{cleanStructName}(structName)}.
        """
        return cleanStructName(structName)
    
    def _saveTransformationAsMetadata(self, transformation, bregma):
        """
        @type  transformation: 4 elements array
        @param transformation: array holding transformation coefficients in
                               following orader: [b,a,d,c]. x'=a*x+b, y'=c*y+d
        
        @type  bregma: string
        @param bregma: bregma coordinate
        
        Puts stereotactic coordinates matrix as SVG metadata
        
        Clues given by Rembrand Bakker:
        x'=xy[0]+xy[1]*x
        y'=xy[0]+xy[1]*y
        """
        # We assume that template is properly defined and empty template
        # has precisely one 'metadata' element.
        
        # Appending transformation matrix and bregma coordinate
        TransformationMatrix =\
                (1*transformation[0][1], transformation[0][0],
                1*transformation[1][1], transformation[1][0])
        spatialMatrix = barTransfMatrixMetadataElement(TransformationMatrix)        
        
        BregmaMetadataElement = barBregmaMetadataElement(bregma)
        
        return (spatialMatrix, BregmaMetadataElement)
    
    def _loadjsonfiles(self):
        """
        @return: None
        
        Downloads data from ScalableBrainAtas website (precise location of the
        data is located in configuration files) and stores it in internal
        dictionary. Function assumes that all data is available and there is no
        connection issues.
        """

        # Read list of files for downloading from config dict and load location
        # template. jsonfileslist has following structure: 'dict_element_key':
        # filename_to_download. All files are downloaded from
        # urlLocationTemplate.
        jsonfileslist = self.jsonFilelist
        urlLocationTemplate = self.templateUrl
        
        # Try to load each file:
        for jsonfile in jsonfileslist.items():
            
            # Extract filename and dictionary key name.
            filename = jsonfile[1]
            dictElemName = jsonfile[0]
            print >>sys.stderr, "Downloading %s ..." % (urlLocationTemplate % filename)
            
            # Well, we assume that all files are available
            urlRequest  = urllib2.Request(urlLocationTemplate % filename)
            urlResponse = urllib2.urlopen(urlRequest).read()
            self._sbaImportData[dictElemName] =  json.loads(urlResponse)
            
            savefilename = os.path.join(self.inputDirectory, filename)
            # Store the file on disk for further review
            open(savefilename, 'w').write(str(urlResponse))
        
        # now we need to calculate some constants basing on config.json file
        self._putscalings(self._calculatescaling())
    
    def _calculatescaling(self):
        """
        function calculates coefficients of transformation matrix basing on
        config.json file provided by scalablebrainatlas template.
        
        folowing fomulas are used to calculate mentioned coefficients:
        
        x' = sx/w*x +b
        y' =-sy/h*y +d
        
        b = xl - l/w    *sx
        d = yl + (1+t/h)*sy
        
        sx - span in x plane in real coordinates;
        sy - span along y axis in real coordinates;
        l - point xl on x axis in svg coordinates
        t - point yl on y axis in svg coordinates
        
        @return: (tuple of 4 floats) coefficients of transformation from svg
                 drawing to real (?? stereotactic) coordinates.
        """
        
        # extract important values from config.json file
        fr   = map(float, self._sbaImportData['config']['sliceCoordFrame'])
        xlim = map(float, self._sbaImportData['config']['sliceXLim']      )
        ylim = map(float, self._sbaImportData['config']['sliceYLim']      )
        
        # calculate coefficients
        (sx, sy) = ( abs(xlim[0] - xlim[1]), abs(ylim[0] - ylim[1]) )
        (w, h)   = ( fr[2], fr[3] )
        (l, t)   = ( fr[0], fr[1] )
        
        (xl, yl) = ( xlim[0], ylim[0] )
        
        a, b     = ( 10 * sx/w, xl -l/w*sx    )
        c, d     = ( 10 * -sy/h, yl +(1+t/h)*sy)

        return (a,b,c,d)
    
    def _putscalings(self, (a,b,c,d)):
        """
        @type  coefs: tuple of four floats 
        @param coefs: coefficients of transformation from svg to real
                      coordinates
        @return: none
        
        fills constants predefined in config.py files. initial values in this
        file may not be defined correctly of may be outdated. after downloading
        json files some constants needs to be recalculated. those constants are
        xyscaling and alignerreferencecoords.
        """
        
        # create xyscalings for all slides:
        self._sbaImportData['xyscaling'] = {}
        for i in self.slideRange:
            self._sbaImportData['xyscaling'][str(i)] = [b,a,d,c]
        
        # Override values from indexerProps
        self.indexer.updateProperties(\
                {'RefCords': ','.join(map(str,[b,d,a,c]))})
