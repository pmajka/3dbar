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

import sys
import os
from PIL import Image, ImageChops, ImageOps
import nifti
import numpy as np

from bar.base import getDictionaryFromFile
from bar import parsers as bar
from data import *

class AtlasParser(bar.barBitmapParser):
    """
    @type  rawSlidesDirectory: string
    @param rawSlidesDirectory: Directory with raw SVG files (raw conversion from ie. PDF)
    
    This is quite complex example
    
    Required to implement:
    _getSourceImage(self, slideNumber)
    _createMask(self, image, colorValue)
    _getZCoord(self, slideNumber)
    _getUniqeColours(self, sourceImage)
    _getSpatialTransfMatrix(self, slideNumber)
    _getNewPathID(self, structName = None)
    """
    _requiredInternalData=bar.barBitmapParser._requiredInternalData +\
            ['_volume','_pathNumber']
    
    def __init__(self, inputDirectory, outputDirectory, **kwargs):
        # Extend passed properties and invoke uperclass constuctor
        kwargs.update(atlasparserProperties)
        bar.barBitmapParser.__init__(self, **kwargs)
        
        self.inputDirectory = inputDirectory
        self.outputDirectory= outputDirectory
        
        # Some properties cannot be predefined, adding them now:
        self.setProperty('outputDirectory', outputDirectory)
        
        # --------------------------------------
        # Load mappings and other settings:
        
        # Generate voxel_index -> structure_name mapping
        imageToStructure = self.__getLabelIndexToNameMapping()
        self.setProperty('imageToStructure', imageToStructure)
        
        # Structure name -> structure colour mapping
        structureColours = self.__getColorMapping()
        self.setProperty('structureColours', structureColours)
        self.indexer.colorMapping = structureColours
        
        # Define hierarchy root
        self.indexer.hierarchyRootElementName = hierarchyRootElementName
        
        # Set indexer properties        
        self.indexer.updateProperties(indexerProps)
        
        #----------------------------------------
        # Deal with the volume

        # Define source dataset location and initialize parser by loading
        # source dataset
        self._loadVolume(SOURCE_VOLUME_FILENAME)
        
        self._defineSlideRange(antPostAxis=2)
        self._pathNumber = 0
        
    def __getFullnameMapping(self):
        filename = os.path.join(self.inputDirectory, CONF_FULLNAME_MAPPING_FILE)
        mapping =  getDictionaryFromFile(filename)
        return mapping
    
    def __getColorMapping(self):
        # Structure name -> structure colour mapping
        # The mapping has to be assigned to the parser as well as to the indexer separately
        # This procedure should be simplified in the future.
        filename = os.path.join(self.inputDirectory, CONF_COLOR_MAPPING_FILE)
        mapping = getDictionaryFromFile(filename)
        return mapping
    
    def __getLabelIndexToNameMapping(self):
        # Load pixelValue to structureName mapping:
        # This mapping is required to assign structure's name to the given label's index
        filename = os.path.join(self.inputDirectory, CONF_VOLUME_LABEL_MAPPING_FILE)
        mapping  = getDictionaryFromFile(filename)
        mapping  = dict(map(lambda (k,v): (int(k),v), mapping.iteritems()))
        return mapping
    
    def _loadVolume(self, sourceFilename):
        volumetricFile = os.path.join(self.inputDirectory, sourceFilename)
        
        self._volumeSrc = nifti.NiftiImage(volumetricFile)
        self._volume  = self._volumeSrc.data
        self._volumeHeader = self._volumeSrc.header 
    
    def _defineSlideRange(self, antPostAxis):
        """
        Defines number of sections along anterior-posterior axis.
        
        @type  antPostAxis: C{int}
        @prarm antPostAxis: Dimension representing ant-pos direction.
        """
        antPostDim = self._volumeHeader['dim'][antPostAxis]
        self._voxelSize = self._volumeHeader['pixdim'][antPostAxis]
        self.slideRange = map(lambda x: (antPostDim - 1) - x, range(0, antPostDim))
    
    def parse(self, slideNumber):
        tracedSlide = bar.barBitmapParser.parse(self, slideNumber,\
                                                 generateLabels = True,
                                                 useIndexer = False,
                                                 writeSlide = False)
        
        # Make the label's font smaller so they do not cover each other
        map(lambda x: \
                x._attributes.update({'font-size':'8px'}),\
                tracedSlide.labels)
        tracedSlide.writeXMLtoFile(self._getOutputFilename(slideNumber))
        
        return tracedSlide
    
    def parseAll(self):
        bar.barBitmapParser.parseAll(self)
        self.reindex()
    
    def reindex(self): 
        bar.barBitmapParser.reindex(self)
        
        self.indexer.createFlatHierarchy()
        
        # set structure name -> structure colour mapping
        self.indexer.colorMapping = self.__getColorMapping()
        
        # Load and use fullname mapping
        self.indexer.fullNameMapping = self.__getFullnameMapping()
        self.writeIndex()
    
    def _getSourceImage(self, slideNumber):
        volumeSlide = self._volume[:,self.slideRange[slideNumber],:]
        
        image = volumeSlide
        return image
    
    def _getUniqeColours(self, sourceImage):
        # This is an unusual implementation as we extract unique values
        # from numpy array instead of (typically) PIL image.
        return np.unique(sourceImage).tolist()
    
    def _createMask(self, image, colorValue):
        # Create mask of provided image 
        # (this method operates on numpy arrays) while typical _createMask
        # method operates on PIL image. But that's still fine.
        imgtemp=np.copy(image)
        imgtemp[image==colorValue]=255
        imgtemp[image!=colorValue]=0
        
        # Convert numpy array into PIL image.
        image = Image.fromarray(imgtemp.astype(np.uint8)).convert("L")
        resizeTuple = self.renderingProperties['imageSize']
        image = ImageOps.flip(image)
        image = ImageChops.invert(image).resize(resizeTuple, Image.NEAREST)
        return image
    
    def _getZCoord(self, slideNumber):
        zVoxelIndex = self.slideRange[slideNumber] 
        return self._volumeSrc.vx2s((0, zVoxelIndex, 0))[1]
    
    def _getSpatialTransfMatrix(self, slideNumber):
        # The spatial transformation matrix does not depend on slideNumber in
        # this dataset
        return origTransformationMatrix
    
    def _getNewPathID(self, structName = None):
        self._pathNumber+=1
        return "structure%d_label%d_%s" % (self._pathNumber, self._pathNumber, structName)


if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  = 'atlases/' + CONF_PARSER_NAME + '/src/'
        outputDirectory = 'atlases/' + CONF_PARSER_NAME + '/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
