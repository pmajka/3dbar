#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2011 Piotr Majka, Lukasz Walejko, Jakub M. Kowalski   #
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
from PIL import Image, ImageChops
import nifti

from bar.base import getDictionaryFromFile
from bar import parsers as bar
from data import *

class AtlasParser(bar.barBitmapParser):
    """
    @type  rawSlidesDirectory: string
    @param rawSlidesDirectory: Directory with raw SVG files (raw conversion from ie. PDF)
        
    Required to implement:
    _getSourceImage(self, slideNumber)
    _createMask(self, image, colorValue)
    _getZCoord(self, slideNumber)
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
        
        # Define source dataset location and initialize parser by loading
        # source dataset
        sourceFilename = 'atlas.nii'
        self._loadVolume(sourceFilename)
        
        # Some properties cannot be predefined, adding them now:
        self.setProperty('outputDirectory', outputDirectory)
        
        # structure name -> structure colour mapping
        fullnameMappingFile = os.path.join(self.inputDirectory,'fullnames.txt')
        structureColours = getDictionaryFromFile(fullnameMappingFile, 0, 2)
        self.setProperty('structureColours', structureColours)
        self.indexer.colorMapping = structureColours
        
        self._defineSlideRange(antPostAxis=3)
        self._pathNumber = 0
        
        # Set indexer properties        
        self.indexer.updateProperties(indexerProperties)
    
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
                                                 generateLabels = False,
                                                 useIndexer = False)
        return tracedSlide
    
    def parseAll(self):
        bar.barBitmapParser.parseAll(self)
        self.reindex()
    
    def reindex(self): 
        bar.barBitmapParser.reindex(self)
        
        #Load hierarchy from parents.txt
        hierarhySourceFilename = os.path.join(self.inputDirectory, 'parents.txt')
        self.indexer.setParentsFromFile(hierarhySourceFilename)
        
        # set structure name -> structure colour mapping
        fullnameMappingFile = os.path.join(self.inputDirectory,'fullnames.txt')
        structureColours = getDictionaryFromFile(fullnameMappingFile, 0, 2)
        self.setProperty('structureColours', structureColours)
        self.indexer.colorMapping=structureColours
        
        # Load and use fullname mapping
        fullnameMappingFile = os.path.join(self.inputDirectory,'fullnames.txt')
        self.indexer.setNameMappingFromFile(fullnameMappingFile, 0 , 1)
        
        self.writeIndex()
    
    def _getSourceImage(self, slideNumber):
        volumeSlide = self._volume[self.slideRange[slideNumber] ,:,:]
        volumeSlide[ volumeSlide[:,:]==0 ] = 255
        
        image = Image.fromarray(volumeSlide).convert("RGB")
        return image
    
    def _createMask(self, image, colorValue):
        r,g,b = colorValue
        R, G, B = 0, 1, 2 # Meaningfull channel names
        
        source = image.split()
        mask = (source[R].point(lambda i: i == r and 255),\
                source[G].point(lambda i: i == g and 255),\
                source[B].point(lambda i: i == b and 255))
        
        # Resize image it order to get better tracing effects:
        # Use nearest neiborhood to get saw-like shape as this dataset has
        # number of single voxels which we don't want to lose.
        resizeTuple = self.renderingProperties['imageSize']
        image = ImageChops.multiply(ImageChops.multiply(mask[1], mask[0]),mask[2])
        image = ImageChops.invert(image).resize(resizeTuple, Image.NEAREST)
        return image
    
    def _getSpatialCoordinate(self, voxelIndexTuple):
        if self._volumeSrc.header['sform_code']: spFunct = self._volumeSrc.vx2s
        if self._volumeSrc.header['qform_code']: spFunct = self._volumeSrc.vx2q
        try:
            return spFunct(voxelIndexTuple)
        except:
            raise NotImplementedError, "unable to fetch zVoxelIndex via any known method"
    
    def _getZCoord(self, slideNumber):
        zVoxelIndex = self.slideRange[slideNumber]
        return self._getSpatialCoordinate((0, 0, zVoxelIndex))[2]
   
    def _getSpatialTransfMatrix(self, slideNumber):
        # The spatial transformation matrix does not depend on slideNumber in
        # this dataset
        return coordinateTuple
    
    def _getNewPathID(self, structName = None):
        self._pathNumber+=1
        return "structure%d_label%d_%s" % (self._pathNumber, self._pathNumber, structName)


if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  = 'atlases/aba/src/'
        outputDirectory = 'atlases/aba/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
