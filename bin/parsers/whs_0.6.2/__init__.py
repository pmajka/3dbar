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
from PIL import Image, ImageChops
import nifti

from bar.mbatParser import barMBATParser 
from data import *

class AtlasParser(barMBATParser):
    """
    Required to implement:
    _getSourceImage(self, slideNumber)
    _createMask(self, image, colorValue)
    _getZCoord(self, slideNumber)
    _getSpatialTransfMatrix(self, slideNumber)
    _getNewPathID(self, structName = None)
    """
    _requiredInternalData=barMBATParser._requiredInternalData +\
            ['_volume','_pathNumber']
    
    def __init__(self, inputAtlasFile, outputDirectory, **kwargs):
        # Extend passed properties and invoke uper class constuctor
        kwargs.update(atlasparserProperties)
        barMBATParser.__init__(self, inputAtlasFile, outputDirectory, **kwargs)
        
        # Fix parrents for empty groups as in mbat atlases have multiple
        # hierarchy root elements.
        self.indexer.hierarchyRootElementName = 'CNS'
        for (k,v) in self.parents.iteritems():
            if v == "": self.parents[k] =\
                    self.indexer.hierarchyRootElementName
        
        # Define hierarchy, fullNameMapping, and color mapping
        self.indexer.hierarchy       = self.parents
        self.indexer.fullNameMapping = self.fullNameMapping
        self.indexer.colorMapping    = self.structureColours
        
        # Set indexer properties, but get indexer reference matrix in advance.
        indexerProperties['RefCords'] = ",".join(map(str,self._getIndexerRefMatrix()))
        self.indexer.updateProperties(indexerProperties)
    
    def _getSpatialCoordinate(self, voxelIndexTuple):
        if self._volumeSrc.header['sform_code']: spFunct = self._volumeSrc.vx2s
        if self._volumeSrc.header['qform_code']: spFunct = self._volumeSrc.vx2q
        try:
            return spFunct(voxelIndexTuple)
        except:
            raise NotImplementedError, "unable to fetch zVoxelIndex via any known method"
    
    def _getZCoord(self, slideNumber):
        zVoxelIndex = self.slideRange[slideNumber]
        return self._getSpatialCoordinate((0, zVoxelIndex, 0))[1]
    
    def _getSpatialTransfMatrix(self, slideNumber):
        cc = self._getSpatialCoordinate((0, 0, 511))
        return (self._voxelSize, cc[0], -self._voxelSize, cc[2])
    
    def _defineSlideRange(self, antPostAxis = 2):
        antPostDim = self._volumeHeader['dim'][antPostAxis]
        self._voxelSize = self._volumeHeader['pixdim'][antPostAxis]
        
        # Reverse direction of the slides along A-P axis just to have
        # anterior on first slides and posteror on the latter.
        self.slideRange = map(lambda x: (antPostDim - 1) - x, range(0, antPostDim))
    
    def parse(self, slideNumber):
        tracedSlide = barMBATParser.parse(self, slideNumber,\
                                                 generateLabels = True,
                                                 useIndexer = False,
                                                 writeSlide = False)
        
        # Natalia wants labels to have smaller font size as (in her opinion)
        # they are hard to decipher. 
        map(lambda x: \
                x._attributes.update({'font-size':'10px'}),\
                tracedSlide.labels)
        tracedSlide.writeXMLtoFile(self._getOutputFilename(slideNumber))
        
        return tracedSlide
    
    def reindex(self): 
        barMBATParser.reindex(self)
        self.indexer.fullNameMapping = self.fullNameMapping
        self.indexer.colorMapping    = self.structureColours
        self.writeIndex()
    

if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  =\
        'atlases/whs_0.6.2/src/MBAT_WHS_atlas_v0.6.2/start_atlas/WHS_0.6.2.atlas'
        outputDirectory = 'atlases/whs_0.6.2/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
