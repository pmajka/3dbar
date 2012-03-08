#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2012 Piotr Majka, Jakub M. Kowalski                   #
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

import sys
import os
import json
import urllib2

import bar.sbaconverter as bar
from data import *

class AtlasParser(bar.barSBAParser):
    """
    Subclass of L{sbaImporter<sbaImporter>} suited for parsing data from PHT00
    template.
    
    This class extends sbaImporter class by implementing custom
    L{_dev_loadjsonfiles<_dev_loadjsonfiles>} function and reimplementing
    constructor.
    """
    def __init__(self, inputDirectory, outputDirectory):
        """
        @type  rawSlidesDirectory: string
        @param rawSlidesDirectory: location of input/resulting directory
                                   (currently, input and output directory
                                   are the same directories)
        
        @type  propertiesDictionary: dictionary
        @param propertiesDictionary: dictionary of settings loaded from
                                     config.py file
        
        @type  debugMode: boolean
        @param debugMode: determines, if debug (verbose) mode will be active
        """
        props = {}
        props['filenameTemplates'] = filenameTempates
        props['slideRange'] = slideRange
        props['renderingProperties'] = renderingProperties
        props['tracingProperties'] = tracerSettings
        props['inputDirectory'] = inputDirectory
        props['outputDirectory'] = outputDirectory
        props['slideTemplate'] = tracedSlideTemplate
        props['templateName']  = templateName
        props['jsonFilelist']  = jsonFilelist
        props['templateUrl']   = templateUrl
        
        bar.barSBAParser.__init__(self, **props)
        
        self.indexer.updateProperties(indexerProps)
        
        # Download and import data from SBA website
        self._loadjsonfiles()

    def parse(self, slideNumber):
        tracedSlide = bar.barSBAParser.parse(self, slideNumber,\
                generateLabels = True,\
                useIndexer     = False,\
                writeSlide     = False)
        
        # We need to shift whole image, see data.py for details
        stm = shiftedTransformationMatrix
        tracedSlide.alignToRefMatrix((stm[2], stm[0], stm[3], stm[1]))
        tracedSlide.writeXMLtoFile(self._getOutputFilename(slideNumber))
        
        return tracedSlide
    
    def parseAll(self):
        bar.barSBAParser.parseAll(self)
        self.reindex()
    
    def reindex(self):
        bar.barSBAParser.reindex(self)
        self.indexer.createFlatHierarchy()
        self.indexer.colorMapping = dict((v,k) for k, v in self._sbaImportData['rgb2acr'].iteritems())
        self.indexer.fullNameMapping = dict((v,v) for k, v in self._sbaImportData['rgb2acr'].iteritems())
        self.writeIndex()
    

if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory = 'atlases/sba_LPBA40_on_SRI24/src/'
        outputDirectory= 'atlases/sba_LPBA40_on_SRI24/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
