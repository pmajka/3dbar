#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# vim: set foldmethod=indent

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
The module provides classes necessary to convert atlas to CAF dataset.

G{importgraph}
"""

import os, sys
import cStringIO
import subprocess
import xml.dom.minidom as dom
from string import strip,  split

from PIL import Image,ImageChops
import atlas_indexer

from base import performTracing, barPath, barTransfMatrixMetadataElement,\
                        barBregmaMetadataElement, cleanPotraceOutput,\
                        barTracedSlide, barTracedSlideRenderer,\
                        barPretracedSlideRenderer, _printRed


class barGenericParser(object):
    """
    @type _requiredInternalData: C{list}
    @cvar _requiredInternalData: Required instance attributtes. Without
                                 prividing them parsing cannot be invoked.
                                 Meaning of each attribute is explained below.
    
    @type outputDirectory: C{string}
    @ivar outputDirectory: Final CAF dataset directory. Directory in which
                           traced files ans CAF index file is stored. Used
                           mostly by 
                           L{_getOutputFilename<barGenericParser._getOutputFilename>}
                           and for saving index CAF index file:
                           L{writeXMLtoFile<base.barObject.writeXMLtoFile>}
    
    @type  filenameTemplates: C{dict}
    @ivar  filenameTemplates: Dictionary holding templates of output filenames
    used by parser and indexing module. Keys are type of slides (ie. C{contour}
    or C{traced}) while values are strings with templates. Usually simple parser
    requires only C{traced} file template: C{dict(traced='%d_traced_v%d.svg')}.
    
    @type slideRange: C{list}
    @ivar slideRange: List of integers containing consecutive slide numbers. it
    is assumed that list contains consecutive slide numbers. List does not have
    to start from zero.
    
    @type renderingProperties: C{dict}
    @ivar renderingProperties: Set of rendering properties for generating bitmap
                               representations of SVG slides. Although there are
                               default C{renderingProperties} defined (see
                               L{here<base.CONF_DEFAULT_RENDERING_PROPS>}),
                               this parser requires providing its own renderinf
                               properes. Each element of the dictinary is
                               explained
                               L{here<base.CONF_DEFAULT_RENDERING_PROPS>}.
    
    @type tracingProperties: C{dict}
    @ivar tracingProperties: Dictionary holding preferences regarding tracing
    wiht PoTrace. All entries are decribed here: 
    L{CONF_POTRACE_ACCURACY_PARAMETER<base.CONF_POTRACE_ACCURACY_PARAMETER>},
    L{CONF_POTRACE_SVG_RESOLUTION_STRING<base.CONF_POTRACE_SVG_RESOLUTION_STRING>},
    L{CONF_POTRACE_WIDTH_STRING<base.CONF_POTRACE_WIDTH_STRING>},
    L{CONF_POTRACE_HEIGHT_STRING<base.CONF_POTRACE_HEIGHT_STRING>}.
    
    @change: pią, 21 sty 2011, 11:40:31 CET, Creating index without parsing all
    nlides again: L{<reindex>} method introduced.
    """
    _requiredInternalData = ['outputDirectory', 'filenameTemplates',\
                            'slideRange','tracingProperties',\
                            'renderingProperties']
    
    def __init__(self,  **kwargs):
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)
        
        self.indexer = atlas_indexer.barIndexer()
    
    def parse(self, slideNumber):
        """
        @type  slideNumber: C{int}
        @param slideNumber: Number of slide to parse
        
        @rtype: L{barTracedSlideRenderer<barTracedSlideRenderer>}
        @return: Traced slide with given C{slideNumber}.
        
        Performs all operation related to creating CAF slide from souce data.
        Should be customized in each parser.
        
        @note: Parsing cannot be performed until all attributes enumerated in
        L{_requiredInternalData<_requiredInternalData>} will be provided.
        """
        print >>sys.stderr, "Parser: parsing slide %d" % (slideNumber,)
        return self._validateInternalData()
    
    def parseAll(self):
        """
        Performs tracing of all slides enumerated in
        L{self.slideRange<self.slideRange>}. Should be customized in each
        parser. Has the same effect as
        L{parseRange<parseRange>}C{(slideRange[0],slideRange[-1])}.

        @rtype: C{None}
        @return: C{None}
        """
        return map(self.parse, self.slideRange)
    
    def parseRange(self, firstSlide, lastSlide):
        """
        @type  firstSlide: integer
        @param firstSlide: number of the first slide to process
        
        @type  lastSlide: integer
        @param lastSlide: number of the last slide to process
        
        @rtype: C{None}
        @return: C{None}
        
        @todo: Implement checking if provided range is withing the limits.
        
        Parses slides starting from C{firstSlide} up to C{lastSlide}.
        """
        #TODO: Implement checking if range is within the limits.
        return map(self.parse, range(firstSlide, lastSlide+1))
    
    def writeIndex(self, rescanSlides = False):
        """
        @type  rescanSlides: C{bool}
        @param rescanSlides: Determines if all slides will be reindexed before
        creating index file
        
        @rtype: C{None}
        @return: C{None}
        
        Creates and writex index file on disk. Whole index is regenerated when
        C{rescanSlides} is C{True}. This option is useful when consecutive
        slides were not indexed during tracing procedure. 
        
        @todo: Check if all required data is set.
        """
        #TODO: Check if all required data is set
        self.indexer.writeXMLtoFile(self._getIndexFilename()) 
    
    def reindex(self):
        """
        @rtype: C{None}
        @return: C{None}
        
        Reindexes all slides in L{self.slideRange<self.slideRange>}. This
        option is useful when consecutive slides were not indexed during tracing
        procedure.
        """
        for slideNumber in self.slideRange:
            tracedSlide = barTracedSlideRenderer.fromXML(\
                    self._getOutputFilename(slideNumber), self.renderingProperties)
            self.indexer.indexSingleSlide(tracedSlide, slideNumber)
    
    def __setInternalData(self, name, value):
        self.__setattr__(name, value)
    
    def __getInternalData(self, name):
        self.__getattribute__(name)
    
    def getProperty(self, name):
        """
        @type  name: string
        @param name: name of the arribute

        @rtype: C{None}
        @return: C{None}

        Returns value of the given attribute.
        """
        return self.__getInternalData(name)
    
    def setProperty(self, name, value):
        """
        @type  name: string
        @param name: name of the arribute

        @type  value: various
        @param value: value of the attribute. Usually value of the attribute is
                      dictionary but it may be also list, etc.

        @rtype: C{None}
        @return: C{None}

        Sets internal property of the parser.
        """
        self.__setInternalData(name, value)

    def _validateInternalData(self):
        """
        Performs internal parsing properties validation. Parsing properties are
        properties provided by the user required for proper parsing procedure.
        Required parameters are listed in 
        L{_requiredInternalData<self._requiredInternalData>}. If not all
        parameters are provided L{parse<self.parse>} cannot be invoked.
        
        @rtype: C{None}
        @return: C{None}
        """

        # Iterate over list of required attributes and checks if they are
        # defined. If an attribute is not defined, raise an exception.
        for dataElement in self._requiredInternalData:
            if self.__getattribute__(dataElement) is None:
                raise ValueError(\
                        "Required parsing property not provided:%s.",\
                        (dataElement,))

    def _getOutputFilename(self, slideNumber, version = 0):
        """
        @type  slideNumber: integer
        @param slideNumber: Number of page to parse
        
        @type  version: integer
        @param version: slide version 0 by default.
       
        @rtype: C{str}
        @return: Path for given traced slide number with given version.
        
        Generates filename for traced file with given version. Function requires
        C{filenameTempates} to be provided.
        """
        return os.path.join(self.outputDirectory,\
                     self.filenameTemplates['traced'] %(slideNumber, version))
    
    def _getIndexFilename(self):
        """
        @rtype: C{str}
        @return: Provides CAF index file path.
        """
        return os.path.join(self.outputDirectory, "index.xml")
    
    def RGBToHTMLColor(self, rgb_tuple):
        """ convert an (R, G, B) tuple to #RRGGBB """
        hexcolor = '#%02x%02x%02x' % rgb_tuple
        # that's it! '%02x' means zero-padded, 2-digit hex values
        return hexcolor

    def _performTracing(self, binaryImage):
        """
        @type  binaryImage: PIL image
        @param binaryImage: Flooded image for tracing.
        
        Preforms tracing procedure. Alias for L{performTracing<performTracing>}.
        
        @rtype: C{str}
        @return: Raw tracing output string.
        """
        return performTracing(binaryImage, self.tracingProperties['PoTraceConf'])


class barVectorParser(barGenericParser):
    """
    Class for creating CAF datasets from contour slides and created index.
    Following minimal data and code has to be provided:
    
        1. Provide: rendering L{renderingProperties<self.renderingProperties>},
        L{potraceProperties<base.CONF_DEFAULT_POTRACE_PROPERTIES>},
        L{tracerSettings<base.BAR_TRACER_DEFAULT_SETTINGS>},
        C{filenameTempates},
        C{indexerProps},
        L{slideRange<self.slideRange>},
        C{colorMapping}.
        
        2. Subclass of L{barVectorParser<barVectorParser>} with overriden
        L{__init__<self.__init__>}, L{parseAll<self.parseAll>} methods.
        
    Most useful information is provided in exemplary parsers.
    
    @type inputDirectory: C{str}
    @ivar inputDirectory: Path to directory with contour slides. Number of
    contour slides has to be the same as lenght of the slideRange property.
    
    @type structureColours: C{dict}
    @ivar structureColours: Dictionary holding structure abbreviations (keys)
                            and translating them into path colous in CAF traced
                            file (values).
    
    @note: C{filenameTemplates} attribute has to have C{pretraced} slide name
    template
    """
    _requiredInternalData = barGenericParser._requiredInternalData +\
            ['structureColours', 'inputDirectory']
    
    def __init__(self, **kwargs):
        barGenericParser.__init__(self, **kwargs)
        #for k, v in kwargs.iteritems():
        #    self.__setattr__(k, v)
        """
        @todo: Provide list of required elements
        @todo: Implement custom structure list.
        """
        pass
    
    def parseAll(self):
        return map(lambda x: self.parse(x), self.slideRange)
    
    def parse(self, slideNumber,\
                    useIndexer = True,\
                    writeSlide = True,\
                    writeContourBack = True):
        
        barGenericParser.parse(self, slideNumber)
        
        # Create traced slide
        contourSlide = barPretracedSlideRenderer.fromXML(\
                        self._getInputFilename(slideNumber))
        contourSlide._tracingConf = self.tracingProperties
        contourSlide._rendererConf= self.renderingProperties
        contourSlide.slideNumber = slideNumber
        tracedSlide = contourSlide.trace(self.structureColours)
        
        if writeSlide: tracedSlide.writeXMLtoFile(self._getOutputFilename(slideNumber))
        if useIndexer: self.indexer.indexSingleSlide(tracedSlide, slideNumber)
        if writeContourBack:
            contourSlide.writeXMLtoFile(self._getInputFilename(slideNumber))
        
        # And return the slide
        return tracedSlide
    
    def _getInputFilename(self, slideNumber, version = 0):
        """
        @type  slideNumber: C{int}
        @param slideNumber: number of contour slide for which path will be
        generated.
        
        @rtype: C{str}
        @return: Path to contour slide with given number
        """
        return os.path.join(self.inputDirectory,\
                     self.filenameTemplates['pretraced'] %(slideNumber, version))


class barBitmapParser(barGenericParser):
    """
    Generic bitmap parser for processing color encoded bitmaps and volumetric
    datasets. This generic class requires implementing several functions in
    order to make it fully functional parser:
    
        1. Generating source bitmap of the slide:
           L{_getSourceImage<_getSourceImage>}
        2. Creating black and white image mask:
           L{_createMask<_createMask>}
        3. Getting 'z' coordinate for given slide:
           L{_getZCoord<_getZCoord>}
        4. Getting spatial transformation martix for given slide:
           L{_getSpatialTransfMatrix<_getSpatialTransfMatrix>}
        5. Generating consecutive paths IDs:
           L{_getNewPathID<_getNewPathID>}
    
    @type imageToStructure: C{dict}
    @ivar imageToStructure: Dictionary holding image colour (key) to structure
                            abbrevation (value) translation. Used for decoding
                            source image colours to th structures names.
    
    @type structureColours: C{dict}
    @ivar structureColours: Dictionary holding structure abbreviations (keys)
                            and translating them into path colous in CAF traced
                            file (values).
    
    """
    _requiredInternalData=barGenericParser._requiredInternalData +\
            [ 'imageToStructure', 'structureColours',
              'backgroundColor']

    def __init__(self, **kwargs):
        barGenericParser.__init__(self, **kwargs)
    
    def parse(self, slideNumber,\
                    generateLabels = True,\
                    useIndexer = True,\
                    writeSlide = True):
        
        barGenericParser.parse(self, slideNumber)
        
        # Create traced slide
        tracedSlide = self._getSlide(slideNumber)
        
        # Perform additional actions if requested
        if generateLabels: tracedSlide.generateLabels()
        if writeSlide: tracedSlide.writeXMLtoFile(self._getOutputFilename(slideNumber))
        if useIndexer: self.indexer.indexSingleSlide(tracedSlide, slideNumber)
        
        # And return the slide
        return tracedSlide
    
    def _getSlide(self, slideNumber):
        """
        @type  slideNumber: C{int}
        @param slideNumber: Number of slide to extract

        @rtype: L{barTracedSlideRenderer<barTracedSlideRenderer>}
        @return: Traced slide with given number.
        """
        
        # Get PIL bitmap image containing slide with given slideNumber
        # It is assumed that image is provided in RGB mode.
        sourceImage = self._getSourceImage(slideNumber)
        
        # Extract list of uniqe colours from source slide image
        # list of tuples in rgbformat
        uniqeColours= self._getUniqeColours(sourceImage)
        
        # Create traced slide:
        # Use customized slide tempate if provided
        try: 
            self.slideTemplate
            customSlideTemplate = self.slideTemplate
        except: 
            customSlideTemplate = None
        retSlide = barTracedSlideRenderer(\
                    slideTemplate = customSlideTemplate,\
                    rendererConfiguration = self.renderingProperties,\
                    tracingConfiguration   = self.tracingProperties)
        retSlide.slideNumber = slideNumber
        
        # Remove background color from the set of colours in the bitmap
        uniqeColours.remove(self.backgroundColor)
        
        # Iterate over all uniqe colours and create set of paths basing on
        # every uniqe colour:
        for imageColour in uniqeColours:
            map(retSlide.addPath, self._processStructure(sourceImage, imageColour))
        
        # Append metadata to newly created slide:
        spatialLocation = [\
        barTransfMatrixMetadataElement(self._getSpatialTransfMatrix(slideNumber)),
        barBregmaMetadataElement(self._getZCoord(slideNumber))]
        
        retSlide.updateMetadata(spatialLocation)
        
        return retSlide

    def _processStructure(self, sourceImage, imageColour):
        """
        @type  sourceImage: PIL image 
        @param sourceImage: raw image from file or volumetric dataset

        @type  imageColour: C{(int,int,int)}
        @param imageColour: colour tuple in r,g,b format. All pixels with that
        colour will be extracted and consideres as pixels representing given
        stucture.

        @rtype: C{SVG XML DOM object}
        @return: DOM object holding SVG document created by tracing masked
                 image generated by L{_parseTracerOutput<_parseTracerOutput>}.
        """
        # Note that image colour is provied in form of (r,g,b) tuple
        # and all bar* object use colour in form of html colour denotation:
        # #%x%x%x. Conversion if performed by RGBToHTMLColor.
        
        # Get binary mask and put it for tracing
        imageForTracing = self._createMask(sourceImage, imageColour)
        tracedImage = self._performTracing(imageForTracing)
        
        # Generate html colour denotation:
        htmlColour = self.RGBToHTMLColor(imageColour)
        
        # Append all paths
        return self._parseTracerOutput(tracedImage, htmlColour)

    def _getUniqeColours(self, sourceImage):
        """
        @type  sourceImage: PIL image
        @param sourceImage: Image in RGB

        @todo: Check if image is in RGB mode

        @rtype: C{[(int,int,int), ... ]}
        @return: List of uniqe colours that were found in given image.
        """
        #TODO: Check if image is in RGB mode
        diffColors = sourceImage.getcolors()
        diffColors = map(lambda x: x[1], diffColors)
        return diffColors

    def _getSourceImage(self, slideNumber):
        """
        @type  slideNumber: C{int}
        @param slideNumber: number of slide to process.

        @rtype: C{PIL image}
        @return: raw bitmap with slide C{slideNumber}

        @note: this is Virtual method and should be custimized in subclasess.

        Generated raw bitmap slide for further processing.
        """
        raise NotImplementedError, "Virtual method executed."

    def _createMask(self, image, colorValue):
        """
        @type  image: PIL image
        @param image: Image basing on which mask will be created. 

        @type  colorValue: C{str}
        @param colorValue: Colour in '#%x%x%x' format

        @rtype: C{PIL image}
        @return: Black and white image with structure mask.

        @note: this is Virtual method and should be custimized in subclasess.

        Creates black & white mask of given slide using provided colour. All
        pixels with given colour are changed to black while all other pixels are
        turned into white. Note that image mode is not binary but still indexed
        (holds 256 colours not 2).
        """
        raise NotImplementedError, "Virtual method executed."

    def _getZCoord(self, slideNumber):
        """
        @type  slideNumber: C{int}
        @param slideNumber: number of slide to process.

        @rtype: C{float}
        @return: Colonal ('z') coordinate of given slide.

        @note: this is Virtual method and should be custimized in subclasess.
        """
        raise NotImplementedError, "Virtual method executed."

    def _getSpatialTransfMatrix(self, slideNumber):
        """
        @type  slideNumber: C{int}
        @param slideNumber: number of slide to process.

        @rtype: C{(float a, float b, float c, float d)}
        @return: Creates set of parameters allowing to translate any image
        coordinate into spatial coordinate using the formula: x'=ax+b, y'=cy+d.

        @note: this is Virtual method and should be custimized in subclasess.
        """
        raise NotImplementedError, "Virtual method executed."

    def _getNewPathID(self, structName):
        """
        @type  structName: C{string}
        @param structName: Name of the structure that will be represented by
        given path.

        @rtype: C{str}
        @return: path id

        @note: this is Virtual method and should be custimized in subclasess.

        Builds id of new path representing provided structure using internal
        path indexing.
        """
        raise NotImplementedError, "Virtual method executed."

    def _parseTracerOutput(self, tracerOutput, pathColour):
        """
        Change PoTrace SVG output in the way which will be usefull later:
            1. Creates DOM structure from PoTrace SVG output
            2. Creates single path segments instead of long bezier paths
            3. Converts path coordinates to absolute
            4. Reduces transformation rules (using my own L{svgfix<svgfix>} module :)
        
        @type  pathColour: C{str}
        @param pathColour: Colour in '#%x%x%x' format
        
        @type  tracerOutput: string
        @param tracerOutput: PoTrace SVG output string
        
        @return: SVG XML DOM stucture generated from PoTrace SVG output string.
        """
        svgdom = cleanPotraceOutput(tracerOutput)
        
        structName = self.imageToStructure[pathColour]
        structFill = self.structureColours[structName]
        
        # Extract barPath objects from svg paths
        newPathList = map(lambda x:\
                self._getPath(x, structName, structFill),\
                svgdom.getElementsByTagName('path'))
        return newPathList

    def _getPath(self, pathElem, structName, structFill):
        """
        @type  pathElem: DOM object
        @param pathElem: SVG path element to process

        @type  structName: str
        @param structName: Name of the structure

        @type  structFill: C{str}
        @param structFill: Colour in '#%x%x%x' format

        @rtype: L{barPath<barPath>}
        @return: Path object representing given structure.

        Creates L{barPath<barPath>} element representing given stucture.
        """

        #Assign dummy id and fill color to avoid parPath constructor errors
        pathElem.setAttribute('id','structure_0_dummy')
        pathElem.setAttribute('fill','#000000')

        # Create new path element
        newPath = barPath.fromXML(pathElem, clearPathDef = True)
        newPath.id = self._getNewPathID(structName)
        newPath.color = structFill

        return newPath


class barExternalParser(barGenericParser):
    def __init__(self, **kwargs):
        barGenericParser.__init__(self, **kwargs)
    
    def parse(self, slideNumber, useIndexer = True):
        barGenericParser.parse(self, slideNumber)


if __name__=='__main__':
    pass
