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
        sourceFilename = 'canon_labels_r.nii'
        volumetricFile = os.path.join(inputDirectory,sourceFilename)
        self._volumeSrc = nifti.NiftiImage(volumetricFile)
        self._volume = self._volumeSrc.data[0]
        
        #Some properties cannot be predefined, adding them now:
        self.setProperty('outputDirectory', outputDirectory)
        
        # set structure name -> structure colour mapping
        fullnameMappingFile = os.path.join(self.inputDirectory,'fullnames.txt')
        structureColours = getDictionaryFromFile(fullnameMappingFile, 0, 2)
        self.setProperty('structureColours', structureColours)
        self.indexer.colorMapping=structureColours
        
        self.slideRange = map(lambda x: 1023 - x, range(0,1024))
        self._pathNumber = 0
        
        # Set indexer properties        
        self.indexer.updateProperties(indexerProperties)
        
    def parse(self, slideNumber):
        tracedSlide = bar.barBitmapParser.parse(self, slideNumber,\
                                                 generateLabels = True,
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
        volumeSlide = self._volume[:, self.slideRange[slideNumber], :]
        volumeSlide[ volumeSlide[:,:]==0 ] = 255
        
        image = Image.fromarray(volumeSlide, 'L').convert("RGB")
        image = image.transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
        return image
    
    def _createMask(self, image, colorValue):
        r,g,b = colorValue
        R, G, B = 0, 1, 2
        
        source = image.split()
        # select regions where red is less than 100
        mask = (source[R].point(lambda i: i == r and 255),\
        source[G].point(lambda i: i == g and 255),\
        source[B].point(lambda i: i == b and 255))
        
        # Resize image it order to get better tracing effects:
        # resizing is performed using high quality anialiasing filter
        # get size:
        resizeTuple = self.renderingProperties['imageSize']
        image = ImageChops.multiply(ImageChops.multiply(mask[1], mask[0]),mask[2])
        image = ImageChops.invert(image).resize(resizeTuple, Image.ANTIALIAS)
        #image = ImageChops.invert(image).resize(resizeTuple, Image.NEAREST)
        return image
    
    def _getZCoord(self, slideNumber):
        zVoxelIndex = self.slideRange[slideNumber]
        if self._volumeSrc.header['sform_code']:
            return self._volumeSrc.vx2s((0, zVoxelIndex, 0))[1]

        if self._volumeSrc.header['qform_code']:
            return self._volumeSrc.vx2q((0, zVoxelIndex, 0))[1]

        raise NotImplementedError, "unable to fetch zVoxelIndex via any known method"
    
    def _getSpatialTransfMatrix(self, slideNumber):
        return spatialTransformationMatrix
    
    def _getNewPathID(self, structName = None):
        #TODO: Assert no spaces in structure name and not null structName
        self._pathNumber+=1
        return "structure%d_label%d_%s" % (self._pathNumber, self._pathNumber, structName)


if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  = 'atlases/whs_0.5/src/'
        outputDirectory = 'atlases/whs_0.5/caf/'

    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
