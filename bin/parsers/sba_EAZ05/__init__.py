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
import os, json

import bar.sbaconverter as bar
from bar.sbaconverter import cleanStructName
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
        pass
    
    def parseAll(self):
        bar.barSBAParser.parseAll(self)
        self.reindex()
    
    def reindex(self):
        # bar.barSBAParser.reindex(self)
        # self.indexer.createFlatHierarchy()
        self.indexer.colorMapping = dict((cleanStructName(v),k) for k, v in self._sbaImportData['rgb2acr'].iteritems())
        self.indexer.fullNameMapping = self._sbaImportData['acr2full'] 
        
        # And the just store the results into the txt files so they can be
        # further preocessed by the volumetric parser.
        
        # Ditry hack stripping all keys and values. It is required as provided
        self.indexer.fullNameMapping = dict(
            (cleanStructName(k),v )\
            for k, v in self.indexer.fullNameMapping.iteritems())
        
        # Define mappings for all the files that will be used in other processings
        fullNameMappingPath = os.path.join(self.inputDirectory, CONF_FULLNAME_MAPPING_FILE)
        colorMappingPath = os.path.join(self.inputDirectory, CONF_COLOR_MAPPING_FILE)
        volIdxToAbbrevPath = os.path.join(self.inputDirectory, CONF_VOLUME_LABEL_MAPPING_FILE)
        volIdxToAbbrevSrcPath = os.path.join(self.inputDirectory, CONF_VOLUME_LABEL_MAPPING_SOURCE)
        
        # Load additional mappings from json files
        volumeToAbbrevMapping = json.load(open(volIdxToAbbrevSrcPath))
        colorToStructureMapping = dict(map(lambda (k,v): \
                (str(k), cleanStructName(v)), enumerate(volumeToAbbrevMapping)))
        
        # And then store them into files
        self._writeDictionaryToFile(self.indexer.colorMapping, colorMappingPath)
        self._writeDictionaryToFile(self.indexer.fullNameMapping, fullNameMappingPath)
        self._writeDictionaryToFile(colorToStructureMapping, volIdxToAbbrevPath)
        
    def _writeDictionaryToFile(self, dictionaryToStore, outputFilename):
        # Iterate over dictionary's values and then store
        outputString = ""
        
        for (k,v) in sorted(dictionaryToStore.iteritems()):
            outputString += "\t".join([ str(k), str(v) ]) + "\n"
        
        # Store the string into the file.
        open(outputFilename, 'w').write(outputString)
        pass
    

if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  = 'atlases/' + CONF_PARSER_NAME + '/src/'
        outputDirectory = 'atlases/' + CONF_PARSER_NAME + '/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
