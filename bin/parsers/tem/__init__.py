#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from PIL import Image, ImageChops

from bar.base import getDictionaryFromFile
from bar.parsers import barBitmapParser
from data import *

class AtlasParser(barBitmapParser):
    _requiredInternalData = barBitmapParser._requiredInternalData +\
            ['_pathNumber']
    
    def __init__(self, inputDirectory, outputDirectory, **kwargs):
        # Extend passed properties and invoke uperclass constuctor
        kwargs.update(atlasparserProperties)
        barBitmapParser.__init__(self, **kwargs)
        
        self.inputDirectory = inputDirectory
        self.outputDirectory= outputDirectory
        
        # Set parser's output directory
        self.setProperty('outputDirectory', outputDirectory)
        
        self.setProperty('imageToStructure', self.__getImageToStructureMapping())
        self.setProperty('structureColours', self.__getColorMapping())
        
        self.slideRange = SLIDE_RANGE
        self._pathNumber = 0 # Internal paths counter
    
    def __getColorMapping(self):
        # set structure name -> structure colour mapping
        # We need to set this mapping here because parser needs to know what
        # colors have to be assigned to paths
        colorMappingFile = os.path.join(self.inputDirectory, COLOR_MAPPING_FN)
        structureColours = getDictionaryFromFile(colorMappingFile, 0, 2)
        return structureColours
    
    def __getImageToStructureMapping(self):
        # set source bitmap colour -> structure name
        imagToStructFn =\
                os.path.join(self.inputDirectory, IMAGE_TO_STRUCTURE_FN)
        imageToStructure = getDictionaryFromFile(imagToStructFn)
        imageToStructure = dict( ('#'+k.lower(), v) for k, v in
                imageToStructure.iteritems())
        return imageToStructure
    
    def __getFullNameMapping(self):
        fullnameMappingFile =\
                os.path.join(self.inputDirectory, FULLNAME_MAPPING_FN)
        return getDictionaryFromFile(fullnameMappingFile, 0 , 1)
        
    def parse(self, slideNumber):
        tracedSlide = barBitmapParser.parse(self, slideNumber,\
                                                 generateLabels = True,
                                                 useIndexer = False)
        return tracedSlide
    
    def parseAll(self):
        barBitmapParser.parseAll(self)
        self.reindex()
     
    def reindex(self): 
        barBitmapParser.reindex(self)
        
        # Set indexer properties        
        self.indexer.updateProperties(indexerProperties)
        
        # Hierarchy should be set as first, then other mappings
        self.indexer.createFlatHierarchy()
        
        # set structure name -> structure colour mapping
        self.indexer.colorMapping = self.__getColorMapping()
        
        # Load and use fullname mapping
        self.indexer.fullNameMapping = self.__getFullNameMapping()
         
        self.writeIndex()
    
    def _getSourceImage(self, slideNumber):
        filename = INPUT_FILENAME_TEMPLATE % slideNumber
        image = Image.open(os.path.join(self.inputDirectory,filename))
        image = image.transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
        return image
    
    def _createMask(self, image, colorValue):
        r,g,b = colorValue
        R, G, B = 0, 1, 2
        
        source = image.split()
        mask = (source[R].point(lambda i: i == r and 255),\
        source[G].point(lambda i: i == g and 255),\
        source[B].point(lambda i: i == b and 255))
        
        # Resize image it order to get better tracing effects:
        # resizing is performed using high quality anialiasing filter
        # get size:
        resizeTuple = self.renderingProperties['imageSize']
        image = ImageChops.multiply(ImageChops.multiply(mask[1], mask[0]),mask[2])
        image = ImageChops.invert(image).resize(resizeTuple, Image.ANTIALIAS)
        return image
    
    def _getZCoord(self, slideNumber):
        return -float(slideNumber)*40.+1160
    
    def _getSpatialTransfMatrix(self, slideNumber):
        return spatialTransformationMatrix
    
    def _getNewPathID(self, structName = None):
        #TODO: Assert no spaces in structure name and not null structName
        self._pathNumber+=1
        print self._pathNumber
        return "structure%d_label%d_%s" % (self._pathNumber, self._pathNumber, structName)

if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  =  'atlases/tem/src/'
        outputDirectory =  'atlases/tem/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
