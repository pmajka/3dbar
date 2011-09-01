#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from PIL import Image, ImageChops
import datetime

from bar.base import getDictionaryFromFile
from bar import parsers as bar
from data import *

class AtlasParser(bar.barBitmapParser):
    _requiredInternalData=bar.barBitmapParser._requiredInternalData +\
            ['_pathNumber']
    
    def __init__(self, inputDirectory, outputDirectory, **kwargs):
        bar.barBitmapParser.__init__(self, **kwargs)
        
        self.inputDirectory = inputDirectory
        self.outputDirectory= outputDirectory
        
        # Set slide background colour
        self.setProperty('backgroundColor', (0, 0, 0))
        
        # Set parser's output directory
        self.setProperty('outputDirectory', outputDirectory)
        
        # set source bitmap colour -> structure name
        imagToStructFn = os.path.join(self.inputDirectory,'imagecol2structname.txt')
        imageToStructure = getDictionaryFromFile(imagToStructFn)
        imageToStructure = dict( ('#'+k.lower(), v) for k, v in
                imageToStructure.iteritems())
        self.setProperty('imageToStructure', imageToStructure)
        
        # set structure name -> structure colour mapping
        fullnameMappingFile = os.path.join(self.inputDirectory,'fnm.txt')
        structureColours = getDictionaryFromFile(fullnameMappingFile, 0, 2)
        self.setProperty('structureColours', structureColours)
        self.indexer.colorMapping=structureColours
        
        self.slideRange = range(1,101)
        self._pathNumber = 0
        
        self.setProperty('filenameTemplates', dict(traced='%d_traced_v%d.svg'))
        self.setProperty('renderingProperties', renderingProperties)
        self.setProperty('tracingProperties', tracerSettings)
        self.setProperty('slideTemplate', tracedSlideTemplate)
        
        self.indexer.properties = ('ReferenceWidth', 1000)
        self.indexer.properties = ('ReferenceHeight', 800)
        self.indexer.properties = ('FilenameTemplate',\
                              self.filenameTemplates['traced'])
        self.indexer.properties = ('RefCords', ','.join(map(str,alignerCoordinateTuple)))
        self.indexer.properties = ('CAFSlideOrientation', 'coronal')
        self.indexer.properties = ('CAFSlideUnits', 'mm')
        self.indexer.properties = ('CAFName', '')
        self.indexer.properties = ('CAFComment', '')
        self.indexer.properties = ('CAFCreator', '')
        self.indexer.properties = ('CAFCreatorEmail', 'pmajka@nencki.gov.pl')
        self.indexer.properties = ('CAFCompilationTime', datetime.datetime.utcnow().strftime("%F %T"))
        
    def parse(self, slideNumber):
        tracedSlide = bar.barBitmapParser.parse(self, slideNumber,\
                                                 generateLabels = True,
                                                 useIndexer = False)
        return tracedSlide
    
    def parseAll(self):
        bar.barBitmapParser.parseAll(self)
        
    def reindex(self): 
        bar.barBitmapParser.reindex(self)
        
        #Load hierarchy from parents.txt
        hierarhySourceFilename = os.path.join(self.inputDirectory, 'ahp.txt')
        self.indexer.setParentsFromFile(hierarhySourceFilename)
        
        # set structure name -> structure colour mapping
        fullnameMappingFile = os.path.join(self.inputDirectory,'fnm.txt')
        structureColours = getDictionaryFromFile(fullnameMappingFile, 0, 2)
        self.setProperty('structureColours', structureColours)
        self.indexer.colorMapping=structureColours

        # Load and use fullname mapping
        fullnameMappingFile = os.path.join(self.inputDirectory,'fnm.txt')
        self.indexer.setNameMappingFromFile(fullnameMappingFile, 0 , 1)
        
        #self.indexer.writeXMLtoFile(self._getIndexFilename())\
        self.writeIndex()
    
    def _getSourceImage(self, slideNumber):
        filename = 'V3_slice%02d.png'% (101 - slideNumber)
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
        return conf_bragma[slideNumber+27] 
    
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
        inputDirectory  =  'atlases/anreas_hess_mouse/src/'
        outputDirectory =  'atlases/anreas_hess_mouse/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
