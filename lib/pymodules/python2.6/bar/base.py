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

"""
The module provides classes necessary to handle basic CAF slide manipulations.

G{importgraph}

@type CONF_DEFAULT_RENDERING_PROPS: {str : ... }
@var  CONF_DEFAULT_RENDERING_PROPS: default settings for rasterizing SVG slides
      used by L{barSlideRenderer<barSlideRenderer>};
      C{CONF_DEFAULT_RENDERING_PROPS['ReferenceWidth']} and
      C{CONF_DEFAULT_RENDERING_PROPS['ReferenceHeight']} are dimensions of the slide
      in 1:1 scale (in pixels) while C{CONF_DEFAULT_RENDERING_PROPS['imageSize']}
      is a tuple (w, h) holding size of the rasterized slide. Usually
      C{CONF_DEFAULT_RENDERING_PROPS['imageSize']} is few times larger than
      C{CONF_DEFAULT_RENDERING_PROPS['ReferenceHeight']} and
      C{CONF_DEFAULT_RENDERING_PROPS['ReferenceWidth']} allowing to more
      precise tracing and automatic label generation

@type CONF_POTRACE_ACCURACY_PARAMETER: str
@var  CONF_POTRACE_ACCURACY_PARAMETER: accurary of potrace tracing; consult
      potrace manual for details

@type CONF_POTRACE_HEIGHT_STRING: str
@var  CONF_POTRACE_HEIGHT_STRING: reference image height for potrace

@type CONF_POTRACE_WIDTH_STRING: str
@var  CONF_POTRACE_WIDTH_STRING: reference image width for potrace

@type CONF_POTRACE_SVG_RESOLUTION_STRING: str 
@var  CONF_POTRACE_SVG_RESOLUTION_STRING: reference resolution for potrace (eg.
      C{'300x300'}); provides resolution in dpi; final image will be scaled using
      this reference resolution so setting it porperly is very important;
      consult potrace manual for details 

@type BAR_TRACER_DEFAULT_SETTINGS: {str : ... } 
@var  BAR_TRACER_DEFAULT_SETTINGS: all settings used by L{barPretracedSlideRenderer}
                                   to perform conversion from contour slide to CAF slide; requires providing
                                   following elements:

@note: L{BAR_TRACER_DEFAULT_SETTINGS} requires providing following elements:
    1. C{DumpEachStepSVG}, C{DumpEachStepPNG}: (C{bool}) determines if every
    step of tracing process will be saved as PNG or SVG file (tracing
    results)
    2. C{DumpWrongSeed}: (C{bool}) determines if snapshot with incorectly placed
    labels will be saved as PNG files
    3. C{DumpVBrain}: (C{bool}) determines,if consecutive steps of generating
    whole brain outline will be stored
    4. C{DumpDirectory}: (C{str}) defines directory where all snapshots are stored
    5. C{DetectUnlabelled}: (C{bool}) defines if unlabelled areas are detected
    6. C{CacheLevel}: (C{int}) C{MaxGrowLevel}
    7. C{MinFiterTimesApplication}: (C{int}) defines intensity of Min filter
    used for generating consecutive images in cache
    8. C{GrowDefaultBoundaryColor}: (C{int}) boundary color
    9. C{RegionAlreadyTraced}: (C{int}) colour of areas denoted as traced
    10. C{PoTraceConf}: (C{str : ...}) traced properties, see
    L{CONF_DEFAULT_POTRACE_PROPERTIES} for details
    11. C{NewPathIdTemplate}: (C{str}) template of path id
    (eg. C{'structure%d_%s_%s'})
    12. C{BestFillAlgorithm}: (C{function}) reference for function for
    defining best gap filling level. This setting may be used to
    provide custom 'selectBestGapFillingLevel' function
"""

import os,  sys, re
from string import *

import xml.dom.minidom as dom
import xml.dom
import numpy as np
import cairo,  rsvg
from PIL import Image, ImageFilter, ImageChops, ImageOps, ImageDraw

import svgfix
from defaults import re_CoordinateMarker, re_CoronalCoord
from svgpathparse import parsePath,UnparsePath, extractBoundingBox,_mergeBoundingBox,\
                         modifyContour, parseStyle, formatStyle
import slides_aligner
from image_process import performTracing, getBestLabelLocation, massCentre,\
        floodFillScanlineStack, selectBestGapFillingLevel


BAR_XML_NAMESPACE = 'http://www.3dbar.org' 
BAR_XML_NAMESPACE_PREFIX    = 'bar:'
BAR_DEFAULT_GROWLEVEL      = 0
BAR_COORDINATE_MARKER_TEMPLATE = '(%f,%f)'
BAR_CORONAL_MARKER_TEMPLATE = 'Bregma:%f'
BAR_REGULAR_LABEL_PREFIX    = ''
BAR_COMMENT_LABEL_PREFIX    = ','
BAR_SPOT_LABEL_PREFIX       = '.'
BAR_LABEL_MAX_LENGTH        = 200
BAR_REGULAR_LABEL_COLOUR    = '#232323'
BAR_COMMENT_LABEL_COLOUR    = '#FF0000'
BAR_SPOT_LABEL_COLOUR       = '#FF0000'
BAR_BREGMA_METADATA_TAGNAME = 'coronalcoord'
BAR_TRAMAT_METADATA_TAGNAME = 'transformationmatrix'
BAR_DATA_LOCATION_ELEMENT   = 'defs'
BAR_XML_ENCODING            = 'utf-8'

CONF_DEFAULT_CONTOUR_WIDTH = '0.2'
CONF_DEFAULT_CONTOUR_COLOUR = '#ff3300'
CONF_DEFAULT_VBRAIN_LABEL_LOC= (10,10)

CONF_DEFAULT_PATH_ATTRIBUTES={
    'd':None,
    'fill':None,
    'id':None,
    'stroke':'none'}
CONF_DEFAULT_PATH_ATTRIBUTES_NS={'growlevel':0, 'type':None}

DEFAULT_TEXT_ELEMENTS_ATTRIBUTES={
    'fill':"#000000",
    'font-family':"Helvetica,sans-serif",
    'font-size':"18px",
    'id':None,
    'stroke':"none",
    'x':None,'y':None}
CONF_DEFAULT_TEXT_ATTRIBUTES_NS={'growlevel':0}

DEFAULT_MARKER_ATTRIBUTES={
    'fill':"#000000",
    'font-family':"Helvetica,sans-serif",
    'font-size':"18px",
    'id':None,
    'stroke':"none",
    'x':None,'y':None}
    
CONF_ALOWED_STRUCTURE_CHARACTERS = re.compile("^[a-z0-9A-Z-]*$", re.IGNORECASE)

#{ Default widht and height of the slide renderer class
CONF_DEFAULT_RENDER_WIDTH  = 1200 * 1
CONF_DEFAULT_RENDER_HEIGHT = 900  * 1

CONF_SLIDE_TEMPLATE ="""
<svg baseProfile="full" id="body"
height="%(width)s"
width="%(height)s"
viewBox="0 0 %(height)s %(width)s"
preserveAspectRatio="none"
version="1.1" 
xmlns="http://www.w3.org/2000/svg"
xmlns:ev="http://www.w3.org/2001/xml-events"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:bar="http://www.3dbar.org">
<title></title>
<desc></desc>

<defs></defs>
<g id='content'></g>

</svg>
"""

def getSlideTemplate(valuesDict):
    return CONF_SLIDE_TEMPLATE % valuesDict 

CONF_DEFAULT_SLIDE_TEMPLATE = getSlideTemplate(\
        {'height': CONF_DEFAULT_RENDER_WIDTH,
         'width' : CONF_DEFAULT_RENDER_HEIGHT})

CONF_DEFAULT_RENDERING_PROPS = {}
CONF_DEFAULT_RENDERING_PROPS['imageSize'] =\
        (CONF_DEFAULT_RENDER_WIDTH * 1, CONF_DEFAULT_RENDER_HEIGHT * 1)
CONF_DEFAULT_RENDERING_PROPS['ReferenceWidth'] = CONF_DEFAULT_RENDER_WIDTH
CONF_DEFAULT_RENDERING_PROPS['ReferenceHeight']=CONF_DEFAULT_RENDER_HEIGHT
#}

#{ Potrace tracing directives
CONF_POTRACE_ACCURACY_PARAMETER    = '0.001'
CONF_POTRACE_HEIGHT_STRING         =  str(CONF_DEFAULT_RENDER_HEIGHT) + 'pt'
CONF_POTRACE_WIDTH_STRING          =  str(CONF_DEFAULT_RENDER_WIDTH)  + 'pt'
CONF_POTRACE_SVG_RESOLUTION_STRING = '300x300'
CONF_DEFAULT_POTRACE_PROPERTIES    = {}
CONF_DEFAULT_POTRACE_PROPERTIES['potrace_accuracy_parameter'] = CONF_POTRACE_ACCURACY_PARAMETER
CONF_DEFAULT_POTRACE_PROPERTIES['potrace_svg_resolution_string']=CONF_POTRACE_SVG_RESOLUTION_STRING
CONF_DEFAULT_POTRACE_PROPERTIES['potrace_width_string']   =      CONF_POTRACE_WIDTH_STRING
CONF_DEFAULT_POTRACE_PROPERTIES['potrace_height_string']  =      CONF_POTRACE_HEIGHT_STRING
#}

#{ Tracing properties
# Debugging settings
BAR_TRACER_DEFAULT_SETTINGS={}
BAR_TRACER_DEFAULT_SETTINGS['DumpEachStepSVG']          = False 
BAR_TRACER_DEFAULT_SETTINGS['DumpEachStepPNG']          = False
BAR_TRACER_DEFAULT_SETTINGS['DumpWrongSeed']            = True 
BAR_TRACER_DEFAULT_SETTINGS['DumpVBrain']               = False 
BAR_TRACER_DEFAULT_SETTINGS['DumpDirectory']            = '.'
BAR_TRACER_DEFAULT_SETTINGS['DetectUnlabelled']         = True

# Basic configuration:
BAR_TRACER_DEFAULT_SETTINGS['CacheLevel']               = 5
BAR_TRACER_DEFAULT_SETTINGS['MinFiterTimesApplication'] = 3
BAR_TRACER_DEFAULT_SETTINGS['GrowDefaultBoundaryColor'] = 200
BAR_TRACER_DEFAULT_SETTINGS['RegionAlreadyTraced']      = 100
BAR_TRACER_DEFAULT_SETTINGS['UnlabelledTreshold']       = 500
BAR_TRACER_DEFAULT_SETTINGS['PoTraceConf'] = CONF_DEFAULT_POTRACE_PROPERTIES
BAR_TRACER_DEFAULT_SETTINGS['NewPathIdTemplate'] = 'structure%d_%s_%s'
#}

#GrowLevel - gap filling algorithm constants
#{ GrowLevel settings
CONF_GAPFILLING_MAXLEVEL = 5
#}

def getDictionaryFromFile(fileName, keyColumn=0, valueColumn=1):
    """
    @type fileName: str
    @param fileName: location of the file
    
    @type keyColumn: int
    @param keyColumn: column containing keys
    
    @type valueColumn: int
    @param valueColumn: column containing values
    
    @return: dictionary read from file
    @rtype: {str : str, ...}
    """
    returnDictionary = {}
    
    sourceFile = open(fileName)
    for sourceLine in sourceFile:
        if strip(sourceLine).startswith('#') or strip(sourceLine) == "":
            continue
        line = split(strip(split(sourceLine,"#")[0]),'\t')
        
        # Validate line 
        if max(keyColumn, valueColumn)+1 > len(line):
            _printRed("Wrong number of fields (%d). Expected %d. Skipping line..."\
                       % (len(line), 1 + max(keyColumn, valueColumn)))
            continue
            
        key = line[keyColumn]
        value = line[valueColumn]
        # Check, if there is only one child -> parent definition for
        # each child.
        if returnDictionary.has_key(key):
            _printRed("Entry %s defined more than once. Skipping..." % key)
            continue
        returnDictionary[key] = value
    sourceFile.close()
     
    return returnDictionary

class barObject(object):
    """
    Parental class for BAR elements.
    
    The general assumption is that every BAR element should have XML
    representation thus this class holds placeholdes for XML import / export
    methods but they are not always implemented in subclasses. Every element
    should also implement the __str__ method, but (again) some subclases do not
    have this function implemented.    
    
    This class have aslo some supplementary function as _getAttributesDict and
    getElementById which appears to be useful.
    
    @cvar _clsBoundingBox: bounding box representation class used by the class
                           objects
    @type _clsBoundingBox: class
    
    @cvar _clsPath: path representation class used by the class objects
    @type _clsPath: class
    
    @cvar _clsGenericStructure: structure (set of paths) representation class
                                used by the class objects
    @type _clsGenericStructure: class
    
    @cvar _clsStructureLabel: generic label representation class used by
                              the class objects
    @type _clsStructureLabel: class
    
    @cvar _clsRegularLabel: regular label representation used by the class
                            objects
    @type _clsRegularLabel: class
    
    @cvar _clsSpotLabel: spot label representation used by the class objects
    @type _clsSpotLabel:  class
    
    @cvar _clsCommentLabel: comment label representation used by the class
                            objects
    @type _clsCommentLabel: class
    
    @cvar _clsMetadataElement: meta data element representation class used by
                               the class objects
    @type _clsMetadataElement: class
    
    @cvar _clsBregmaMetadataElement: bregma meta data element representation
                                     class used by the class objects
    @type _clsBregmaMetadataElement: class
    
    @cvar _clsTransfMatrixMetadataElement: transformation matrix meta data
                                           element representation class used by
                                           the class objects
    """
    # to be owerwritten with descendent classes
    _clsBoundingBox = None
    _clsPath = None
    _clsGenericStructure = None
    _clsStructureLabel = None
    _clsRegularLabel = None
    _clsSpotLabel = None
    _clsCommentLabel = None
    _clsMetadataElement = None
    _clsBregmaMetadataElement = None
    _clsTransfMatrixMetadataElement = None
    
    def __str__(self):
        """
        An alias for C{self.L{getXMLelement}().toxml()}
        """
        return self.getXMLelement().toxml(encoding = BAR_XML_ENCODING)
    
    def getXMLelement(self):
        """
        A stub of method. Raise NotImplementedError.
        """
        raise NotImplementedError, "Virtual method executed."
    
    def writeXMLtoFile(self, outputFilename,
            indent="\t", addindent="\t", newl="\n",
            encoding=BAR_XML_ENCODING):
        """
        Write XML representation of the object to file.
        
        @type  outputFilename: str
        @param outputFilename: filename to save the file
        
        @type indent: str
        @param indent: indentation delimiter
        
        @type addindent: str
        @param addindent: additional indentation delimiter
        
        @type newl: str
        @param newl: newline delimiter
        
        @type encoding:
        @param encoding: output xml file encoding
        
        @return      : None
        """
        f=open(outputFilename,'w')
        self.getXMLelement().writexml(f, indent, addindent, newl, encoding)
        print >>sys.stderr, "Saved to: ", outputFilename
        f.close()
    
    @staticmethod
    def _getAttributesDict(xmlElement):
        """
        Extract attributes from L{xmlElement}.

        @type  xmlElement: xml.dom.minidom.Node
        @param xmlElement: svg from which all attributes will be extrated
        
        @return: attribute to value mapping
        @rtype: {str : str, ...}
        """
        return dict(xmlElement.attributes.items())
    
    #TODO: can be staticmethod
    def getElementById(self, domElement, tagName, id):
        """
        Stupid walkaround of faulty DOM getElementById.
        
        @attention: Do not use until there is not other way.
        
        @type domElement: xml.dom.minidom.Node
        @param domElement: XML element
        
        @type tagName: str
        @param tagName: requested XML element name
        
        @type id: str
        @param id: requested XML element id
        """
        for element in domElement.getElementsByTagName(tagName):
            if element.hasAttribute('id') and element.getAttribute('id') == id:
                return element


class barAtlasSlideElement(barObject):
    """
    General class describing all elements that are part of slide. E.g. markers,
    paths, labels and metadata. Provides XML export and virtual XML import
    method.
    
    @type _attributes: {str : ?, ...}
    @cvar _attributes: regular attribute (exported without namespace prefix)
                       name to value mapping
    
    @type _attributesNS: {str : ?, ...}
    @cvar _attributesNS: namespace attributes (exported with
                         L{BAR_XML_NAMESPACE_PREFIX} prefix) name to value
                         mapping
    @type _elementName: str
    @cvar _elementName: name of the represented XML element
    """
    
    _attributes = {}
    _attributesNS = {}
    _elementName = 'text'
    
    @classmethod
    def fromXML(cls, sourceXMLElement):
        """
        A stub of method. Raise NotImplementedError.

        @type  sourceXMLElement: DOM XML or string containing xml
        @param sourceXMLElement: XML representation of the element
        """
        raise NotImplementedError, "Virtual method executed."
    
    def getXMLelement(self, useBarNS = False):
        """
        Generate XML DOM representation of the object.

        @type  useBarNS: bool
        @param useBarNS: determines, if element uses 3dBAR XML namespace
        
        @rtype: xml.dom.minidom.Node
        @return: XML representation of the object
        """
        retDocument = dom.Document()
        if useBarNS:
            retElement  = retDocument.createElementNS(\
                    BAR_XML_NAMESPACE,
                    BAR_XML_NAMESPACE_PREFIX + self._elementName)
        else:
            retElement  = retDocument.createElement(self._elementName)

        # Put all attrubutes into text element
        for (attribName, attribValue) in self._attributes.items():
            if not attribValue == None:
                retElement.setAttribute(attribName, str(attribValue))
        
        # Additionally put attributes belonging to 3dBAR namespace
        for (attribName, attribValue) in self._attributesNS.items():
            if not attribValue == None:
                retElement.setAttributeNS(\
                        BAR_XML_NAMESPACE,
                        BAR_XML_NAMESPACE_PREFIX + attribName, 
                        str(attribValue))
        
        return retElement
    
    def _getTextNodeXMLelement(self, textNodeCaption):
        """
        Generate XML DOM representation of the object. Used when given XML
        element has textnode child (ie. labels).
        
        @type  textNodeCaption: str
        @param textNodeCaption: value of the textnode
        
        @return: XML representation of the object
        @rtype: dom.xml.Node
        """
        # Generate XML DOM element:
        retDocument= dom.Document()
        retElement = barAtlasSlideElement.getXMLelement(self)
        
        # Create text node carrying structure name 
        newTextNode = retDocument.createTextNode(textNodeCaption)
       
        # Put all the nodes in xml DOM structure
        retElement.appendChild(newTextNode)
        return retElement
    
    def affineTransform(self, M):
        """
        A stub of method. Raise NotImplementedError.

        @type  M: numpy 3x3 array
        @param M: transformation matrix
        """
        raise NotImplementedError, "Virtual method executed."
    
#-------------------------------------------------
# Labels
#-------------------------------------------------

class barStructureLabel(barAtlasSlideElement):
    """
    Parental class for all classes representing slide labels.
    
    @note: The class should not be used itself but rather its customized
           subclasses (L{barRegularLabel}, L{barSpotLabel}, L{barCommentLabel})
           as there are three basic types of labels.
     
    @cvar _color: color of label
    @type _color: str 
    
    @cvar _prefix: prefix that is added to the label when XML element
                   is generated
    @type _prefix: str
    """
    
    # Label types are distinguished by prefix and color thus generic label
    # has no particular color and prefix assigned.
    _color  = None
    _prefix = None
    _elementName = 'text'
    
    def __init__(self, labelLocation, labelCaption, labelID,
                       properties = None, growlevel = BAR_DEFAULT_GROWLEVEL):
        """
        @type  labelLocation: (int, int)
        @param labelLocation: point in which label is anchored
        
        @type  labelCaption: str
        @param labelCaption: text (name of the structure)
        
        @type  labelID: str
        @param labelID: uniqe ID assigned to this label
        
        @type  properties: {str : ?, ...}
        @param properties: custom XML attributes overriding default XML text
                           element settings
        """
        
        if properties:
            # if custom text element attributes are given use them:
            self._attributes = dict(properties)
        else:
            # Load default SVG properties from configuration file:
            self._attributes = dict(DEFAULT_TEXT_ELEMENTS_ATTRIBUTES)
        self._attributesNS = dict(CONF_DEFAULT_TEXT_ATTRIBUTES_NS)
        
        self.growlevel = growlevel
        
        # Public
        self.Location = labelLocation 
        self.Caption  = self._validateCaption(strip(labelCaption))
        self.ID = labelID
        
    @classmethod
    def fromXML(cls, svgTextElement):
        """
        Create label object from its XML representation. 

        @note: The method returns object of the proper class (according to
               the type of the given label representation).

        @type  svgTextElement: xml.dom.node
        @param svgTextElement: XML representation of the object

        @return: created label object
        @rtype: L{barStructureLabel}
        """
        # Check if given element is a 'text' element:
        if not svgTextElement.tagName == 'text': 
            raise TypeError, "Invalid SVG element provided"
        
        # Extract all attributes from given element:
        propertiesDict =\
        cls._getAttributesDict(svgTextElement)
        
        # Extract label's coordinates, caption and id which will be used in
        # label's constructor.
        x, y = map(lambda x: float(propertiesDict[x]), ['x','y'])
        
        # Now it's a bit tricky. Text elements may contain a number of nested
        # tspan tags. We will check if such tags exist and, it they are,
        # text will be extcracted from all of them and merged after all.
        #tspans = svgTextElement.getElementsByTagName('tspan')
        labelCaption = _recurseTextNodeExtract(svgTextElement)
        
        #labelCaption = strip(svgTextElement.firstChild.nodeValue)
        labelID = propertiesDict['id']
        
        # Extract growlevel attribute
        try:
            growlevel=\
                    int(propertiesDict[BAR_XML_NAMESPACE_PREFIX+'growlevel'])
        except:
            _printRed('Invalid or empty growlevel provided. Using growlevel=0.\
                    Don\'t worry, it may happen.')
            growlevel = 0
        
        # Try to extract label font size. If it is impossible default value of
        # font size will be used
        try:
            labelFontSize = propertiesDict['font-size']
        except:
            labelFontSize = None
        
        # Return label with proer type depending on label's prefix
        labelPrefix = labelCaption[0]
        
        # Create label
        if labelPrefix == BAR_COMMENT_LABEL_PREFIX:
            retLabel = cls._clsCommentLabel( (x, y), labelCaption[1:].replace(',',''), labelID)
        elif labelPrefix == BAR_SPOT_LABEL_PREFIX:
            retLabel = cls._clsSpotLabel( (x, y), labelCaption[1:].replace('.',''), labelID)
        else:
            retLabel = cls._clsRegularLabel( (x, y), labelCaption, labelID ) 

        # Customize label properties
        if labelFontSize: retLabel._attributes['font-size'] = labelFontSize
        else: pass
        retLabel.growlevel = growlevel 
        
        return retLabel
    
     
    
    @classmethod
    def castToCommentLabel(cls, sourceLabel):
        """
        An alias for C{L{castLabelType}(sourceLabel, barCommentLabel)}.
        """
        return cls.castLabelType(sourceLabel, cls._clsCommentLabel)
    
    @classmethod
    def castToSpotLabel(cls, sourceLabel):
        """
        An alias for C{L{castLabelType}(sourceLabel, barSpotLabel)}.
        """
        return cls.castLabelType(sourceLabel, cls._clsSpotLabel)
    
    @classmethod
    def castLabelType(cls, sourceLabel, targetLabelType):
        """
        Converts label type from one to another.
        
        @type  sourceLabel: L{barStructureLabel}
        @param sourceLabel: label to be converted
        
        @type  targetLabelType: class
        @param targetLabelType: class of the resulting label.
        
        @return: converted label
        @rtype: L{targetLabelType}
        """
        # Extract label properties ...
        (x,y) = sourceLabel.Location
        labelCaption = sourceLabel.Caption
        labelID = sourceLabel.ID
        properties = sourceLabel._attributes
        
        # and put them into new label
        retLabel = targetLabelType( (x, y), labelCaption, labelID, properties)
        return retLabel
    
    def getXMLelement(self):
        # Customize SVG element properties dictionary:
        (x,y) = self.Location
        self._attributes['id']   = str(self.ID)
        self._attributes['fill'] = str(self._color)
        self._attributesNS['growlevel'] = str(self.growlevel)
       
        return barAtlasSlideElement._getTextNodeXMLelement(\
                self, self._prefix + self.Caption)
    
    def _validateCaption(self, caption):
        """
        Validate given caption. Raise ValueError if invalid.
        
        @param caption: text to be validated
        @type caption: str
        
        @rtype: str
        @return: L{caption}
        """
        if len(caption) > BAR_LABEL_MAX_LENGTH:
            raise ValueError, \
            "Length of the caption: '%s' larger than allowed %d." % \
            (caption, BAR_LABEL_MAX_LENGTH)
        else: return caption
    
    #TODO: add assertion
    def __getLocation(self):
        """
        @return: location (x, y) of the label in SVG (slide) coordinates
        @rtype: (float, float)
        """
        return tuple(map(lambda x: float(self._attributes[x]), ['x','y']))
    
    def __setLocation(self, newLocation):
        """
        Assign the location of the label.

        @type  newLocation: (float, float)
        @param newLocation: new location (x, y) of the label
        """
        # Verify input data by mapping it into floats
        #TODO: refactoring
        (x, y) = tuple(map(float, newLocation))
        self._attributes['x'] = str(x)
        self._attributes['y'] = str(y)
    
    def __affineTransform(self, M):
        """
        Transform the location of the label.

        @param M: transformation matrix
        @type M: numpy 3x3 array
        """
        self.Location = tuple(svgfix.transformPoint(self.Location, M))
        
    def affineTransform(self, M):
        """
        An alias for C{self.L{__affineTransform}(M)}.
        """
        return self.__affineTransform(M)
    
    def __getCaption(self):
        """
        @return: the label caption
        @rtype: str
        """
        return self.__caption
    
    def __setCaption(self, newCaption):
        """
        Assign the label caption if is a valid structure name. Otherwise raise
        ValueError.

        @type newCaption: str
        @param newCaption: new caption value
        """
        self.__caption = self._validateCaption(newCaption)
    
    def __getID(self):
        """
        @return: the label identifier
        @rtype: str
        """
        return self._attributes['id']
    
    def __setID(self, newID):
        """
        Assign the label identifier.

        @type  newID: str
        @param newID: new label identifier
        """
        self._attributes['id'] = newID
    
    def __setGrowlevel(self, newGrowlevel):
        """
        Assign the label grow level.

        @param newGrowlevel: new grow level
        @type  newGrowlevel: convertable to int
        """
        self._growlevel = int(newGrowlevel)
    
    def __getGrowlevel(self):
        """
        @return: grow level of the label
        @rtype: int
        """
        return self._growlevel
    
    Location = property(__getLocation, __setLocation)
    """
    Location of the label.

    @type: (float, float)
    """

    Caption  = property(__getCaption,  __setCaption)
    """
    Caption of the label.

    @type: str
    """

    ID       = property(__getID, __setID)
    """
    Identifier of the label.

    @type: str
    """

    growlevel= property(__getGrowlevel, __setGrowlevel)
    """
    Grow level of the label.

    @type: int
    """


class barRegularLabel(barStructureLabel):
    """
    Regular label is used to indicate area corresponding to ordinary brain
    structure.
    
    Regular label has no prefix and the fill color is #232323. This value is
    hardcoded as it is constant across all templates. 
    """
    _prefix = BAR_REGULAR_LABEL_PREFIX
    _color  = BAR_REGULAR_LABEL_COLOUR
    
    def _validateCaption(self, caption):
        if not validateStructureName(caption):
            raise ValueError, "Incorrect label caption: '%s'." % caption
        else: return caption


class barSpotLabel(barStructureLabel):
    """
    Spot label is used to indicate point (spot). This kind of label is not
    traceable. The sense of spotlabel is: 'Point and small surroundings are
    described by this label'. There may be many spotlabels in enclosed area.
    
    Spot labels has a red color and '.' prefix. Dot character corresponds with
    spot behaviour of the label.
    """
    _prefix = BAR_SPOT_LABEL_PREFIX
    _color  = BAR_SPOT_LABEL_COLOUR


class barCommentLabel(barStructureLabel):
    """
    Comment labels are not related to brain structures. Their purpose is to
    convey additional information, comment or any other custom information.
    Consider comment labels as comments in programming languages.
    
    Comment labels are denoted by ',' (comma - comment) character as well as
    red font color.
    """
    _prefix = BAR_COMMENT_LABEL_PREFIX
    _color  = BAR_COMMENT_LABEL_COLOUR

#-------------------------------------------------
# Metadata elements
#-------------------------------------------------

class barMetadataElement(barAtlasSlideElement):
    """
    Basic class representing metadata objects.
    """
    _elementName = 'data'
    
    def __init__(self, name, value):
        """
        @type  name: str
        @param name: name of given metadata element
        
        @param value: content of metadata
        """
        self._value = value
        self._name  = name
   
    @classmethod
    def fromXML(cls, svgMetadataElement):
        """        
        Create metadata element from XML representation of 3dBAR metadata
        element. Determine which type of metadata is parsed and return proper
        subclass for L{barMetadataElement}.
        
        @type  svgMetadataElement: xml.dom.minidom.Node
        @param svgMetadataElement: XML representation of 3dBAR metadata element

        @return: created metadata element
        @rtype: L{barMetadataElement}
        """
        
        # Extract all attributes from given element:
        propertiesDict =\
          cls._clsStructureLabel._getAttributesDict(svgMetadataElement)
        metadataElType    = propertiesDict['name']
        metadataElContent = propertiesDict['content']
        
        if metadataElType == BAR_BREGMA_METADATA_TAGNAME:
            bregmaValue = float(metadataElContent)
            return cls._clsBregmaMetadataElement(bregmaValue)
        
        if metadataElType == BAR_TRAMAT_METADATA_TAGNAME:
            transfMat = map(float, metadataElContent.split(','))
            return cls._clsTransfMatrixMetadataElement(transfMat)
        
        # If none of above:
        return cls(metadataElType,metadataElContent)

    def _getContentString(self):
        """
        Generate string representation of content of metadata. Such
        representation may by used in XML element as is required because
        metadata content may be not only string but also list, dictionary, etc.
        
        Default string represenataion is str() but, in general, it is overided
        by subclases.
        
        @return: string representation of metadata content
        @rtype: str
        """
        return str(self._value)
    
    def _validateValue(self, NewValue):
        """
        Validates given value. Should be overriden and reimplemented in every
        subclass.

        @param NewValue: value to be validated
        """
        return True
    
    def _getValue(self):
        """
        @return: content of metadata element
        """
        return self._value
    
    def _setValue(self, NewValue):
        """
        Assign the content of the metadata element if valid.

        @param NewValue: new content of the metadata element
        """
        if self._validateValue(NewValue):
            self._value = NewValue
    
    def _getName(self):
        """
        @return: name of the metadata element
        @rtype: str
        """
        return self._name
    
    def getXMLelement(self):
        """
        An alias for C{L{barAtlasSlideElement.getXMLelement}(self, useBarNS = True)}.
        """
        self._attributes['name']    = self._name
        self._attributes['content'] = self._getContentString()
        
        return barAtlasSlideElement.getXMLelement(self, useBarNS = True) 
    
    def getMetadataTuple(self):
        """
        Generate tuple containing name and value of medatada object.
        
        @return: generated tuple
        @rtype (str, ?)
        """
        return (self._name, self._value)
    
    value = property(_getValue, _setValue)
    """
    Content of the metadata element.
    """

    name  = property(_getName)
    """
    Name of the metadata element.

    @type: str
    """
    

class barBregmaMetadataElement(barMetadataElement):
    """
    Class of objects representing bregma metadata elements.
    
    @note: Type of the element content is float.
    
    @note: Each slide may have only one BregmaMetadataElement - otherwise
           significant errors may ocurr.
    """
    def __init__(self, bregmaValue):
        """
        @type  bregmaValue: float
        @param bregmaValue: bregma coordinate of given slide
        """
        barMetadataElement.__init__(self, BAR_BREGMA_METADATA_TAGNAME, bregmaValue)


class barTransfMatrixMetadataElement(barMetadataElement):
    """
    Class of objects representing stereotectical coordinates transformation
    matrix.
    """
    def __init__(self, transformationMatrixTuple):
        """
        Transformation matrix coefficients (a, b, c, d)  that
        transforms image coordinate to stereotaxic (or other 'real') in
        following way: x'=a*x+b, y'=c*y+d.

        @type  transformationMatrixTuple: (float, float, float, float) or
                                          ((float, float), (float, float)
        @param transformationMatrixTuple: drawing to stereotaxic coordinate
                                          system transformation matrix
        """
        barMetadataElement.__init__(self,\
                BAR_TRAMAT_METADATA_TAGNAME, transformationMatrixTuple)
    
    def _getContentString(self):
        return ",".join(map(str, self._value))

#-------------------------------------------------
# Markers
#-------------------------------------------------

class barMarker(barAtlasSlideElement):
    """
    Class of objects representing markers.
    
    Markers are elements which allows to provide spatial coordinate system via
    graphical SVG element which can be easily done by various graphics
    software. Markers are recalculated into metadata elements by
    L{barPretracedSlide.parseMarkers<barPretracedSlide.parseMarkers>}. 
    """
    _elementName = 'text'
    
    def __init__(self, spatialLocation, svgLocation, properties = None):
        """
        @type  spatialLocation: (float, float)
        @param spatialLocation: location (x, y) of the marker in spatial
                                coordinate system
        @type  svgLocation: (float, float)
        @param svgLocation: location (x, y) of the markers in SVG coordinate
                            system
        
        @type  properties: {str : ?}
        @param properties: SVG attribute name to value mapping appended
                           to the XML representation of the marker
                           (please remember that, in fact, marker is a text
                           element)
        """
        if properties:
            # if custom text element attributes are given use them:
            self._attributes = dict(properties)
        else:
            # Load default SVG properties from configuration file:
            self._attributes = dict(DEFAULT_MARKER_ATTRIBUTES)
        
        if not hasattr(spatialLocation, '__iter__'):
            spatialLocation = (spatialLocation,)
        
        self._svgLocation     = svgLocation
        self._spatialLocation = spatialLocation
    
    @classmethod
    def fromXML(cls, svgTextElement):
        """
        Create marker from its XML representation.
        
        @type  svgTextElement: xml.dom.minidom.Node
        @param svgTextElement: source XML element
        
        @return: created object
        @rtype: L{barMarker}
        """
        
        # Check if given element is text element:
        if not svgTextElement.tagName == 'text': 
            raise TypeError, "Invalid SVG element provided"
        
        # Extract all attributes from given element:
        propertiesDict =\
          barCoordinateMarker._getAttributesDict(svgTextElement)
        
        # Extract label's coordinates, caption and id which will be used in
        # marker's constructor.
        x, y = map(lambda x: float(propertiesDict[x]), ['x','y'])
        
        # Parse text of text element looking for spatial coordinates
        # of the label
        labelCaption = _recurseTextNodeExtract(svgTextElement)
        
        try:
            spatialCoordinates = map(float, re_CoordinateMarker.search(labelCaption).groups())
            return barCoordinateMarker(spatialCoordinates, (x,y))
        except:
            pass
        
        try:
            spatialCoordinates = map(float, re_CoronalCoord.search(labelCaption).groups())
            return barCoronalMarker(spatialCoordinates, (x,y))
        except:
            pass
    
    def getXMLelement(self, textNodeCaption = ""):
        """
        Generate XML DOM representation of the object.
        
        @type  textNodeCaption: str
        @param textNodeCaption: caption of the marker
        
        @return: generated XML DOM representation
        @rtype: xml.dom.minidom.Node
        """
        # Put location (placement) of the marker
        # (expresed in SVG coordinate system)
        self._attributes['x'] = self._svgLocation[0]
        self._attributes['y'] = self._svgLocation[1]
#        self._attributes['id']= self._idAttrib
        return barAtlasSlideElement._getTextNodeXMLelement(\
                self, textNodeCaption)
    
    def _getSpatialLocation(self):
        """
        @return: location (x, y) of the marker in spatial coordinate system
        @rtype: (float, float)
        """
        return tuple(map(float, self._spatialLocation))
    
    def _setSpatialLocation(self, SpatialLocationTuple):
        """
        Assign the location of the marker in spatial coordinate system.

        @param SpatialLocationTuple: new location (x, y) of the marker
        @type SpatialLocationTuple: (float, float)
        """
        self._spatialLocation = SpatialLocationTuple
    
    def _getSVGLocation(self):
        """
        @return: location (x, y) of the marker in SVG coordinate system
        @rtype: (float, float)
        """
        return tuple(map(float, self._svgLocation))
    
    def _setSVGLocation(self, SVGLocationTuple):
        """
        Assign the location of the marker in SVG coordinate system.

        @param SVGLocationTuple: new location (x, y) of the marker
        @type SVGLocationTuple: (float, float)
        """
        self._svgLocation = SVGLocationTuple
    
    def __affineTransform(self, M):
        """
        Transform the location of the marker in SVG coordinate system.

        @param M: transformation matrix
        @type M: numpy 3x3 array
        """
        self.svgLocation = tuple(svgfix.transformPoint(self.svgLocation, M))
    
    def affineTransform(self, M):
        """
        An alias for C{self.L{__affineTransform}(M)}. 
        """
        return self.affineTransform(M)
    
    spatialLocation = property(_getSpatialLocation, _setSpatialLocation)
    """
    The location of the marker in spatial coordinate system.

    @type: (float, float)
    """

    svgLocation     = property(_getSVGLocation, _setSVGLocation)
    """
    The location of the marker in SVG coordinate system.

    @type: (float, float)
    """


class barCoordinateMarker(barMarker):
    """
    Class of objects representing marker of slide position in coronal plane.
    """
    def getXMLelement(self):
        newTextNodeCaption =\
            BAR_COORDINATE_MARKER_TEMPLATE % tuple(self._spatialLocation)
        return super(self.__class__, self).getXMLelement(newTextNodeCaption)

    
class barCoronalMarker(barMarker):
    """
    Class of objects representing marker of anterior-posterior slide position.
    """
    def getXMLelement(self):
        newTextNodeCaption =\
            BAR_CORONAL_MARKER_TEMPLATE % self._spatialLocation[0]
        return super(self.__class__, self).getXMLelement(newTextNodeCaption)

#-------------------------------------------------
# Paths and structures
#-------------------------------------------------

class barPath(barAtlasSlideElement):
    """
    Class of objects describing enclosed path denoting particular area in
    the slice.

    Note that 'path' does not mean 'structure' because structure may consist of
    many paths.
    """
    _elementName = 'path'
    
    def __init__(self, pathID, pathDefinition, fillColor, properties = None, clearPathDef = False):
        """
        @type  pathID: str
        @param pathID: identifier of the path element that will be stored as
                       path id in XML representation (valid path id)
        
        @type  pathDefinition: str
        @param pathDefinition: definition of the path (valid SVG path
                               definition)
        
        @type  fillColor: str
        @param fillColor: color string in hexadecimal format (might begin with
                          "#" char or not)

        @type properties: {str : ?}
        @param properties: SVG attribute name to value mapping appended
                           to the XML representation of the path

        @type clearPathDef: bool
        @param clearPathDef: indicates if the L{pathDefinition} has to be
                             converted to parser-compatible format
        """
        
        # We can load default path properties or replace default values by
        # substituted dictionary of properties
        if properties:
            # if custom text element attributes are given use them:
            self._attributes   = properties
        else:
            # Load default SVG properties from configuration file:
            self._attributes = dict(CONF_DEFAULT_PATH_ATTRIBUTES)
        self._attributesNS = dict(CONF_DEFAULT_PATH_ATTRIBUTES_NS)
        
        # Customize path properties: set ID, path definition and fill color
        self._setPathDefinition(pathDefinition, clearPathDef)
        self.color = fillColor
        self.id = pathID
    
    @classmethod
    def fromXML(cls, svgPathElement, clearPathDef = False):
        """
        Create path object from its XML representation.
        
        @type svgPathElement: xml.dom.node
        @param svgPathElement: XML representation of the object
        
        @return: created object
        @rtype: cls
        """
        # Extract id, definition and color from path
        pathDefinition = svgPathElement.getAttribute('d')
        pathID = svgPathElement.getAttribute('id')
        if clearPathDef:
            pathDefinition = cls.simplifyPathDef(pathDefinition)
        
        # If path element has defined fill color remove it and overwrite it with
        # inline style
        if svgPathElement.hasAttribute('fill'):
            fillColor = svgPathElement.getAttribute('fill')
        else:
            styleDict = parseStyle(svgPathElement.getAttribute('style'))
            fillColor = styleDict.get('fill',"#000000")
        
        # we treat growlevel as optional parameter
        try:
            growlevel = int(svgPathElement.getAttributeNS(\
                    BAR_XML_NAMESPACE, 'growlevel'))
        except:
            growlevel = 0
            if __debug__:
                _printRed('Invalid or empty growlevel provided. Using growlevel=0.\
                    Don\'t worry, it may happen.')
        
        retPath = cls(pathID, pathDefinition, fillColor, clearPathDef = clearPathDef)
        retPath.growlevel = int(growlevel)
        
        # Try to extract feature type and assign it to the path.
        # Skip it, if the feature type is undefined.
        try:
            strType = svgPathElement.getAttributeNS(\
                        BAR_XML_NAMESPACE, 'type')

            retPath.type = strType

        except:
            pass
        
        return retPath
    
    @staticmethod
    def simplifyPathDef(pathDefinition):
        """
        Change definition of path to absolute coordinates and eliminate all
        command shortcuts.
        
        @type  pathDefinition: str
        @param pathDefinition: path definition
        
        @return: simplified path
        @rtype: str
        """
        
        # Convert incompatible path format (relative coordinates, long curve segments)
        # to more legible format compatible with parser
        return  UnparsePath(parsePath(pathDefinition))
    
    def _getPathDefinition(self):
        """
        @return: SVG path definition
        @rtype: str
        """
        return self._attributes['d']
        
    def _setPathDefinition(self, newPathDefinition, clearPathDef = False):
        """
        Assign the path definition.
        
        @type  newPathDefinition: str
        @param newPathDefinition: new SVG path definition
        
        @type clearPathDef: bool
        @param clearPathDef: indicates if the L{newPathDefinition} has to be
                             validated and converted to parser-compatible
                             format; if true and L{newPathDefinition} is
                             invalid raise ValueError
        """
        if clearPathDef:
            if not self._validatePath(newPathDefinition):
                raise ValueError, "Invalid path definition provided"
            self._attributes['d'] = self.simplifyPathDef(newPathDefinition)
        else:
            self._attributes['d'] = newPathDefinition
        
    def _validatePath(self, pathDefinition):
        """
        Validate SVG path definition: Path definition has to contain at least
        three points and 'closepath'command in order to be considered as valid
        path.
        
        @type  pathDefinition: str
        @param pathDefinition: SVG path definition to be validated.
        
        @return: True, if path definition is correct, False otherwise 
        @rtype: bool
        """
        # Validate length:
        if len(parsePath(pathDefinition)) <= 3:
            return False
        
        # Search for 'closepath' command
        if pathDefinition.strip()[-1] not in ['Z', 'z']:
            return False
        return True
        
    def _getGrowlevel(self):
        """
        @return: gap filling level for the path
        @rtype: int
        """
        return self._attributesNS['growlevel']
    
    def _setGrowlevel(self, Growlevel = None):
        """
        Set gap filling level for the path.
        
        @type  Growlevel: int
        @param Growlevel: new level of gap filling that should be forced when
                          tracing is performed 
        """
        if not Growlevel:
            Growlevel = 0
        if int(Growlevel) >= -1 and int(Growlevel) <= CONF_GAPFILLING_MAXLEVEL:
            self._attributesNS['growlevel'] = Growlevel
        else:
            raise ValueError, "Given Growlevel is outside defined bounaries."
    
    def _validateID(self, id):
        """
        Validate identifier of the path.
        
        The basic rule of valid 3dBAR path id is that it is list of values
        separated with '_' (underscore) character. First value has to start exactly
        with 'structure' string, the second element is an actual uniqe id of the path while
        the last value is name of structure represented by particular path.
        
        Renember: NO SPACES are allowed!
        
        Example of proper 3dBAR path id is 'structureXX_genetared-from-label-6_Olf'
        while wrong definition could be 'str_Olf_from label 87'
        
        @type  id: str
        @param id: SVG path identifier to be validated
        
        @note: Method does not validate uniqness of given ID, only it's formal
               corectness.
        """
        valList = id.strip().split('_')
        
        if len(valList) < 3:
            debugOutput("Wrong path length %s" % id, error=True)
            return False
        if not valList[0].startswith('structure'):
            debugOutput("Invalid path id[0]: %s" % id, error=True)
            return False
        if not validateStructureName(valList[-1]):
            debugOutput("Invalid path id[-1]: %s" % id, error=True)
            return False
        if not validateStructureName(valList[-2]):
            debugOutput("Invalid path id[-2]: %s" % id, error=True)
            return False
        
        return True
    
    def _setID(self, newPathID):
        """
        Assign the identifier of the path.
        
        @type  newPathID: str
        @param newPathID: new value of SVG path identifier
        """
        if self._validateID(newPathID):
            self._attributes['id'] = newPathID.strip()
        else:
            raise ValueError, "Invalid path ID!"
    
    def _getID(self):
        """
        @return: SVG path identifier
        @rtype: str
        """
        return self._attributes['id']
    
    def _getPathType(self):
        """
        @return: value of 'L{type}' property
        @rtype: str
        """
        return self._attributesNS['type']
    
    def _setPathType(self, newPathType):
        """
        Assign the value of the 'L{type}' property.
        
        @type  newPathType: str
        @param newPathType: new value of the 'type' property
        """
        
        if newPathType == None:
            self._attributesNS['type'] = newPathType
        else:
            assert type(newPathType) is str or type(newPathType) is unicode, "String or 'None' value expected"
            assert validateStructureName(newPathType) == newPathType,\
                    "Invalid feature type name provided: %s" % newPathType
            self._attributesNS['type'] = newPathType
    
    def _getBbox(self):
        """
        Return value of the 'L{boundingBox}' property.

        @return: the bounding box description (x1, y1, x2, y2)
        @rtype: (int, int, int, int)
        """
        return extractBoundingBox(self._attributes['d'])
    
    def _setBbox(self, newBBox):
        """
        Raise ValueError
        """
        raise ValueError, "Bounding box is readonly property."
    
    def _getColor(self):
        """
        @return: fill colour of the path in hexadecimal represenatation
        @rtype: str
        """
        return self._attributes['fill']
    
    def _setColor(self, newColor):
        """
        Assign the fill colour of the path.

        @type  newColor: str
        @param newColor: new fill colour of the path in hexadecimal format (may
                         begin with "#" char or not)
        """
        if newColor[0] == "#": self._attributes['fill'] = newColor
        else: self._attributes['fill'] = "#" + newColor
    
    def _getCorrespondingStructureName(self):
        """
        @return: name of the structure corresponding to the path
        @rtype: str
        """
        return self._getID().split('_')[-1]
    
    def _getCorrespondingLabelID(self):
        """
        @return: identifier of the corresponding label
        @rtype: str
        """
        return self._getID().split('_')[-2]
    
    def _setCorrespondingLabelID(self, newID):
        """
        Raise ValueError.
        """
        raise ValueError, "Corresponding label ID is readonly property."
    
    def _rename(self, newStructName):
        """
        Change the structure corresponding to the path.

        @param newStructName: name of the new structure corresponding to
                              the path
        @type newStructName: str
        """
        newID     = self.id.split('_')
        newID[-1] = validateStructureName(newStructName)
        self._setID(join('_').join(newID))
    
    def __affineTransform(self, M):
        """
        Transform the location of the path in SVG coordinate system.
        
        @param M: transformation matrix
        @type M: numpy 3x3 array
        """
        self.pathDef = svgfix.fixPathDefinition(self.pathDef,  M)
        
    def affineTransform(self, M):
        """
        An alias for C{self.L{__affineTransform}(M)}.
        """
        return self.__affineTransform(M)
    
    def __setCrispEdges(self, boolValue):
        """
        Set the value of 'shape-rendering' attribute.
        
        @type boolValue: bool
        @param boolValue: True if 'shape-rendering' has to be 'crisp-edges',
                          False if it has to be 'geometric-precision'
        """
        assert type(boolValue) == type(True), "Boolean value expected"
        
        if boolValue:
            self._attributes['shape-rendering'] = 'crisp-edges'
        else:
            self._attributes['shape-rendering'] = 'geometric-precision'
    
    def __getCrispEdges(self):
        """
        @return: True when the value of 'shape-rendering' attribute is
        'crisp-edges', False otherwise.
        
        @rtype: bool 
        """
        if self._attributes.has_key('shape-rendering'):
            if self._attributes['shape-rendering'] == 'crisp-edges':
                return True
            elif self._attributes['shape-rendering'] == 'geometric-precision':
                return False
        else:
            return False
    
    id         = property(_getID, _setID)
    """
    The path identifier.
    
    @type: str
    """
    
    type   = property(_getPathType, _setPathType)
    """
    Attribute holding type of the feature delineated by given path. For example
    it can be like 'gray matter', 'white matter', 'single cell', 'ventricle', and
    other... This property would be extended when INCF DAI common metadata set
    will be well established.
    
    @type: string
    """
    
    growlevel  = property(_getGrowlevel, _setGrowlevel)
    """
    Gap filling level for the path.
    
    Baceuse barPath class is used in already traced files, gap filling
    level describes with which gap filling level tracing was performed.
    So in such case it has only informative purpose.
    
    By default Growlevel is set to 0 which means that no erosion filter was
    applied.
    
    @type: int
    """
    
    pathDef    = property(_getPathDefinition, _setPathDefinition)
    """
    The SVG path definition.
    
    @type: str
    """
    
    boundingBox= property(_getBbox, _setBbox)
    """
    The path bounding box description (x1, y1, x2, y2), where x1, y2 are
    coordinates of top-left corner of bounding box and x2, y2 are coordinates
    of bottom-right corner of bounding box.
    
    Please note that bounding box is only approximation of actual bounding box
    and may be slightly larger as it is based on extreme coordinated of control
    points creating given path. However, the difference is neglectable.
    
    Read-only property.
    
    @type: (int, int, int, int)
    """
    
    bbx        = boundingBox
    """
    An alias for L{boundingBox} property.
    """
    
    color      = property(_getColor, _setColor)
    """
    The fill colour of the path in hexadecimal represenatation.
    
    @type: str
    """
    
    structName = property(_getCorrespondingStructureName, _rename)
    """
    Name of the structure corresponding to the path.
    
    @type: str
    """
    
    relLabelID = property(_getCorrespondingLabelID, _setCorrespondingLabelID)
    """
    The identifier of the label corresponding to the path.
    
    Read-only property.
    
    @type: str
    """
    
    crispEdges = property(__getCrispEdges, __setCrispEdges)
    """
    Property related to the 'shape-rendering' SVG path attribute.
    
    See L{getter<__getCrispEdges>} and L{setter<__setCrispEdges>} for details.
    """


class barGenericStructure(barAtlasSlideElement):
    """
    Class of containers of L{paths<barPath>} related to one structure.
    
    @ivar _paths: paths related to the structure
    @type _paths: {str : L{barPath}}
    
    @ivar _name: name of the structure
    @type _name: str
    
    @ivar _color: colour of the structure in hexadecimal format (with or
                  without leading '#')
    @type _color: str
    """
    def __init__(self, name, color, pathList = None):
        """
        @param name: name of the structure
        @type name: str
        
        @param color: colour of the structure
        @type color: str
        
        @param pathList: paths to be included in the structure
        @type pathList: sequence([L{barPath}, ...])
        """
        self._paths = {}
        self._type = None
        self.name = name
        self._color = color
        
        if pathList:
            self._type = pathList[0].type
            for path in pathList:
                self.addPaths(path)
    
    def __setitem__(self, key, value):
        """
        Add path to the structure.
        
        @param key: path identifier (L{barPath.id})
        @type key: str
        
        @param value: path
        @type value: L{barPath}
        """
        self._paths[key] = value
        self._paths[key].color = self._color
    
    def __delitem__(self, key):
        """
        Remove path from the structure.
        
        @param key: path identifier
        @type key: str
        """
        del self[key]
        # Removes path with given key. If the path is the last path in the
        # structute, delete also the structure.
        if len(self) == 0: del self
    
    def __getitem__(self, key):
        """
        @param key: identifier of the requested path
        @type key: str
        
        @return: requested path
        @rtype: L{barPath}
        """
        return self._paths[key]
    
    def __str__(self):
        return "\n".join(map(str, self.values()))
    
    def __len__(self):
        """
        @return: number of paths in the structure
        @rtype: int
        """
        return len(self._paths)
    
    def updatePaths(self):
        """
        Update colour and name of contained paths.
        """
        # Update color and name? Why to update name and color?
        # perhaps it should be split into separate functions?
        map(lambda path:  path._setColor(self.color), self.paths)
        map(lambda path:  path._rename(self.name), self.paths)
        map(lambda path:  setattr(path, 'type', self.type), self.paths)
    
    def keys(self):
        """
        @return: contained paths identifiers
        @rtype: [str, ...]
        """
        return self._paths.keys()
    
    def items(self):
        """
        @return: (path identifier, path) pairs for contained paths
        @rtype: [(str, L{barPath}), ...]
        """
        return self._paths.items()
    
    def values(self):
        """
        @return: contained paths
        @rtype: [L{barPath}, ...]
        """
        return self._paths.values()
    
    def itervalues(self):
        """
        @return: iterator over contained paths
        @rtype: iterator([L{barPath}, ...])
        """
        return self._paths.itervalues()
    
    def iterkeys(self):
        """
        @return: iterator over contained paths identifiers
        @rtype: iterator([str, ...])
        """
        return self._paths.iterkeys()

    def iteritems(self):
        """
        @return: iterator over (path identifier, path) pairs for contained paths
        @rtype: iterator([(str, L{barPath}), ...])
        """
        return self._paths.iteritems()
    
    def _getPaths(self):
        """
        An alias for C{self.L{values}()}.
        """
        return self.values()
    
    def _getFeatureType(self):
        """
        Getter for the L{type} property
        
        @rtype: str or None
        @return: value of the L{type} property
        """
        return self._type
    
    def _setFeatureType(self, newFeatureType):
        """
        Setter for the L{type} property of the structure.
        
        @return: None
        """
        if newFeatureType == None:
            self._type = None
        else:
            assert type(newFeatureType) is str or type(newFeatureType) is unicode, "String or 'None' value expected"
            assert validateStructureName(newFeatureType) == newFeatureType,\
                    "Invalid feature type name provided: %s" % newFeatureType
            self._type = newFeatureType
        
        self.updatePaths()
    
    def _setStructureName(self, name):
        """
        Assign the name of the structure.
        
        @param name: new name of the structure
        @type name: str
        """
        self._name = validateStructureName(name)
        self.updatePaths()
    
    def _getStructureName(self):
        """
        @return: name of the structure
        @rtype: str
        """
        return self._name
    
    def _getStructureColor(self):
        """
        @return: colour of the structure in hexadecimal format (with or
                 without the leading '#')
        @rtype: str
        """
        return self._color
    
    def _setStructureColor(self, newColor):
        """
        Assign the colour of the structure.
        
        @param newColor: new colour of the structure in hexadecimal format
                         (with or without the leading '#')
        @type newColor: str
        """
        self._color = newColor
        self.updatePaths()
    
    def _getBbox(self):
        """
        @return: bounding box (min_x, min_y, max_x, max_y) of the whole
                 structure
        @rtype: (int, int, int, int)
        """
        # Alias for merginig bounding boxes.
        return _mergeBoundingBox( map(lambda path: path.bbx, self.paths))
    
    def _setBbox(self, newBBox):
        """
        Raise ValueError.
        """
        raise ValueError, "Bounding box is readonly property."
    
    def getXMLelement(self):
        """
        @return: iterator over XML DOM representations of contained paths.
        @rtype: iterator([xml.dom.minidom.Node, ...])
        """
        # Should return iterator
        for path in sorted(self.itervalues(), key=lambda x: x.id):
            yield path.getXMLelement()
    
    def addPaths(self, *args):
        """
        Add paths to the structure.
        
        @type args: [L{barPath}, ...]
        """
        for newPath in args:
            self.__setitem__(newPath.id, newPath)
        self.updatePaths()
            
    def __affineTransform(self, M):
        """
        Transform the location of all paths in SVG coordinate system.

        @param M: transformation matrix
        @type M: numpy 3x3 array
        """
        map(lambda x: x.affineTransform(M),  self.paths)
    
    def affineTransform(self, M):
        """
        An alias to C{self.L{__affineTransform}(M)}.
        """
        return self.__affineTransform(M)
    
    def __setCrispEdges(self, boolValue):
        """
        Set 'L{crispEdges<barPath.crispEdges>}' attribute for every path of
        the structure.
        """
        assert type(boolValue) == type(True), "Boolean value expected"
        map(lambda x: setattr(x, 'crispEdges', boolValue), self._paths.values())
    
    def __getCrispEdges(self):
        """
        @rtype: bool
        @return: C{True} if every contained path has L{crispEdges<barPath.crispEdges>}
                 attribute equal 'crispEdges', C{False} otherwise.
        """
        return all(map(lambda x: getattr(x, 'crispEdges'), self._paths.values()))
    
    name           = property(_getStructureName, _setStructureName)
    
    type           = property(_getFeatureType, _setFeatureType)
    """
    Attribute holding type of the feature delineated by given path. For example
    it can be like 'gray matter', 'white matter', 'single cell', 'ventricle', and
    other... This property would be extended when INCF DAI common metadata set
    will be well established.
    
    @type: string
    """
    
    color          = property(_getStructureColor, _setStructureColor)
    """
    Colour of the structure in hexadecimal format (with or without the leading
    '#').
    
    @type: str
    """
    
    bbx            = property(_getBbox, _setBbox)
    """
    Bounding box (min_x, min_y, max_x, max_y) of the whole structure.
    
    Read-only property.
    
    @type: (int, int, int, int)
    """
    
    paths          = property(_getPaths)
    """
    Contained paths.
    
    Read-only property.
    
    @type: [L{barPath}, ...]
    """
    
    crispEdges     = property(__getCrispEdges, __setCrispEdges)
    """
    The 'L{crispEdges<barPath.crispEdges>}' attribute of all contained paths.
    When read C{True} if the value of the attribute of every contained path
    is C{'crispEdges'}, C{False} otherwise.
    
    @type: bool
    """


class barBoundingBox(barObject):
    """
    Bounding box is a clever class that stores bounding box and implements
    simple operations that may be performed on bounding boxes such as
    extracting bounding box from SVG path definition, merging, printing etc.

    @ivar boundaries: bounding box coordinates (in following order: top, left,
                      bottom, right)
    @type boundaries: (int, int, int, int) or (float, float, float, float)
    """
    def __init__(self, initialBoundaries = None):
        """
        @type  initialBoundaries: (int, int, int, int) or
                                  (float, float, float, float)
        @param initialBoundaries: initial L{boundaries}.
        """
        if not initialBoundaries:
            self.boundaries = (None, None, None, None)
        else:
            self.boundaries = initialBoundaries
        pass
    
    @classmethod
    def fromPathDefinition(cls, svgPathDefinition):
        """
        Create bounding box based on SVG path definition.

        @type  svgPathDefinition: str
        @param svgPathDefinition: definition of the path in SVG manner
        
        @return: created bounding box
        @rtype: L{barBoundingBox}
        """
        return barBoundingBox(extractBoundingBox(svgPathDefinition))
    
    @classmethod
    def fromPathElement(self, svgPathElement):
        """
        Create bounding box based on SVG 'path' element.

        @type  svgPathElement: xml.dom.minidom.Node 
        @param svgPathElement: SVG path element
        
        @return: created bounding box
        @rtype: L{barBoundingBox}
        """
        barBoundingBox.fromPathDefinition(\
           svgPathElement.getAttribute('d'))
    
    def __merge(self, listOfBoundaries):
        """
        Merge given boundaries.

        @type  listOfBoundaries: [(int, int, int, int) or (float, float, float,
                                 float), ...]
        @param listOfBoundaries: boundaries to be merged
        
        @return: merged boundaries
        @rtype: (int, int, int, int) or (float, float, float, float)
        """
        return _mergeBoundingBox(listOfBoundaries)

    def extend(self, extIterable):
        """
        Modify bounding box boundaries by values in given iterable.

        @param extIterable: extension list
        @type  extIterable: sequence([int, int, int, int]) or sequence([float,
                            float, float, float])
        """
        b = np.array(self.boundaries)
        e = np.array(extIterable)
        self.boundaries = tuple(b+e)
    
    def __add__(self, obj):
        """
        Merge two bounding box objects into one.

        @return: merged bounding boxes
        @rtype: L{barBoundingBox}
        """
        merged = self.__merge((self.boundaries, obj.boundaries))
        return barBoundingBox(merged)
    
    def __iter__(self):
        return iter(self.boundaries)
   
    def __getitem__(self, index):
        return self.boundaries[index]
    
    def __mul__(self, number):
        """
        @type number: int or float
        @param number: boundaries multiplication factor

        @attention: boundaries of returned bounding box are rounded.

        @return: bounding box with boundaries multiplied by given factor
        @rtype: L{barBoundingBox}
        """
        multiplied = tuple(map(lambda x: round(x*number), self.boundaries))
        return barBoundingBox(multiplied)
    
    def __str__(self):
        return ",".join(map(str, self.boundaries))

    def __eq__(self, other):
        return other != None and self.boundaries == other.boundaries

    def __ne__(self, other):
        return not self == other

    
#-------------------------------------------------
# Slides
#-------------------------------------------------


class barVectorSlide(barObject):
    """
    An abstract class representing all types of vector slides - slides that
    are based on SVG drawings.
    
    @attention: This class is an abstract class and should never be instanced.

    @ivar slideTemplate: an empty SVG document which can be filled with labels,
                         structures and metadata
    @type slideTemplate: xml.dom.minidom.Document
    
    @ivar _labels: label ID to label representation mapping
    @type _labels: {str : L{barStructureLabel}, ...}
    
    @ivar _metadata: names of particular metadata to its representation mapping
    @type _metadata: {str : L{barMetadataElement}, ...}
    
    @ivar slideNumber: slide number
    @type slideNumber: int
    """
    def __init__(self, slideTemplate=CONF_DEFAULT_SLIDE_TEMPLATE, slideNumber=0):
        """
        @type slideTemplate: str
        @param slideTemplate: SVG slide template

        @type slideNumber: int
        @param slideNumber: slide number
        """
        self.slideTemplate    = slideTemplate
        
        self._labels           = {}
        self._metadata         = {}
        self.slideNumber = slideNumber
        self._setSlideTemplate(slideTemplate)
    
    def _getLabels(self):
        """
        @rtype: [L{barStructureLabel}, ...]
        @return: labels of the SVG slide
        """
        return self._labels.values()
    
    def _getMetadata(self):
        """
        @rtype: {str : L{barMetadataElement}, ...}
        @return: names of particular metadata to its representation mapping
        """
        return self._metadata
    
    def updateMetadata(self, metadataList):
        if hasattr(metadataList, '__iter__'):
            map(self._setMetadata, metadataList)
        else:
            self._setMetadata(metadataList)
    
    def _setMetadata(self, metadataElement):
        """
        Add metadata to the slide.
        
        @type  metadataElement: L{barMetadataElement}
        @param metadataElement: metadata element to be added to the slide
        """
        self._metadata[metadataElement.name] = metadataElement
    
    def addLabel(self, newLabel):
        """
        Add label to the slide.
        
        @type  newLabel: L{barStructureLabel}
        @param newLabel: label to be added to the slide
        """
        while self._labels.has_key(newLabel.ID):
            debugOutput(\
               "Label with ID %s already in the slide! Trying to fix.!\n"\
                % (newLabel.ID,), error=False)
            newLabel.ID += '_'
        
        self._labels[newLabel.ID] = newLabel
    
    #TODO: fix setter/getter type conflict
    def _getSlideTemplate(self):
        """
        @rtype: xml.dom.minidom.Document
        @return: SVG slide template
        """
        return self._slideTemplate
    
    def _setSlideTemplate(self, newSlideTemplate):
        """
        Assign new slide template.
        
        @type  newSlideTemplate: str
        @param newSlideTemplate: new slide template
        
        @todo: Add slide validation before replacing the template. See
               L{_validateSlideTemplate}.
        """
        if self._validateSlideTemplate(newSlideTemplate):
            self._slideTemplate = dom.parseString(newSlideTemplate)
    
    def _validateSlideTemplate(self, newSlideTemplate):
        """
        A stub of method.

        @todo: Implement template validation.
        """
        #TODO: Add template validation.
        return True
    
    def alignToRefMatrix(self, refTuple):
        """
        Transform slide in the way that current transformation matrix will be
        equal to L{refTuple}. 
        
        Workflow:
        
            1. Get initial transformation matrix from metadata.
            2. Calculate corrections basing on initial transformation matrix
               and reference matrix.
            3. Embed corrections as SVG transformation and put corrected
               transformation matrix as 3dBAR metedata.

        @note: Scaling can be either positive and negative. When scaling is
               positive it means that stereotaxic axis has the same direction
               as image axis. When scaling is negative stereotaxic and image
               axes are oriented in opposite directions. Be very careful
               in such case.
        
        @type  refTuple: (float, float, float, float)
        @param refTuple: reference transformation matrix (sxref, xref, syref,
                         yref) for aligning
        """
        
        currentTranfTuple = tuple(self._metadata[BAR_TRAMAT_METADATA_TAGNAME].value)
        (tranfMatrix, status) = slides_aligner.makeAlignment(refTuple, currentTranfTuple)
        
        # Status tells if given transformation should be applied:
        # yes, if it is non-identity transformation, no otherwise as we don't
        # want to waste time for multiplying all points by 1.
        if status:
            self.affineTransform(tranfMatrix)
            self._metadata[BAR_TRAMAT_METADATA_TAGNAME].value = refTuple
    
    def Show(self, binFile='eog', tempFilename="/tmp/barTemp.svg"):
        """
        Display the slide in external SVG browser.

        @type  binFile: str
        @param binFile: name of the executable file that will be used instead of
                        the detault SVG browser
        
        @type  tempFilename: str
        @param tempFilename: temporary file name used to store svg slide
        """
        self.writeXMLtoFile(tempFilename)
        os.system(binFile + " " + tempFilename) 
     
    def getLabelByName(self, labelCaption, labelType=None, oType='id'):
        """
        Find labels matching searching criteria (caption of the label and
        optionally its type).

        @type  labelCaption: str
        @param labelCaption: caption of the label
        
        @type  labelType: class
        @param labelType: the label class

        @type  oType: str
        @param oType: When set to 'id' IDs of selected labels are returned, if
                      'ref' references are returned
        
        @return: depends on L{oType}
        """
        if not labelType:  source = self.labels
        else: source = self.__getAllLabelsWithType(labelType)

        if oType == 'id':
            return [ label.ID
                   for label in source
                   if  label.Caption == labelCaption]
        if oType == 'ref':
            return [ label
                   for label in source
                   if  label.Caption == labelCaption]

    def retypeLabelByCaption(self, labelCaption, targetType):
        """
        Change class of representation of the requested label.

        @type targetType: class
        @param targetType: new class of the label representation

        @type labelCaption: str
        @param labelCaption: caption of labels which representation class
                             has to be changed
        """
        for labelID in self.getLabelByName(labelCaption):
            self._labels[labelID] = self._clsStructureLabel.castLabelType(
                                self._labels[labelID], targetType)
    
    def deleteLabelByCaption(self, labelCaption):
        """
        Remove from the slide every label of requested caption.

        @type labelCaption: str
        @param labelCaption: caption of labels to be daleted
        """
        for labelID in self.getLabelByName(labelCaption):
            del self._labels[labelID]
       
    def deleteLabelByID(self, labelID):
        """
        Remove from the slide label of requested ID.

        @type labelID: str
        @param labelID: identifier of the label to be deleted
        """
        del self._labels[labelID]
    
    def renameLabelByCaption(self, oldCaption, newCaption):
        """
        Change the caption of every label of requested caption.

        @param oldCaption: caption to be replaced
        @type oldCaption: str

        @param newCaption: new caption of labels of caption L{oldCaption}
        @type newCaption: str
        """
        for labelID in self.getLabelByName(oldCaption):
            self._labels[labelID].Caption = newCaption
    
    def __getAllLabelsWithType(self, labelType):
        """
        @param labelType: requested type of labels
        @type labelType: class

        @return: labels of requested type contained in the slide
        @rtype: [L{labelType}]
        """
        return [ label for label in self.labels if
                label.__class__.__name__ == labelType.__name__ ]
    
    def __affineTransform(self, M):
        """
        Transform the location of all paths in SVG coordinate system.

        @param M: transformation matrix
        @type M: numpy 3x3 array
        """
        map(lambda x: x.affineTransform(M),  self.labels)
    
    def affineTransform(self, M):
        """
        Transform the location of all paths in SVG coordinate system.

        @param M: transformation matrix
        @type M: numpy 3x3 array

        @return: self
        @rtype: L{barVectorSlide} 
        """
        self.__affineTransform(M)
        return self
    
    def __validateMetadata(self):
        """
        Check if all necessary metadata elements are provided. If not - raise
        KeyError.
        """
        try:
            temp = self._metadata[BAR_TRAMAT_METADATA_TAGNAME]
            temp = self._metadata[BAR_BREGMA_METADATA_TAGNAME]
        except KeyError:
            raise KeyError, "Metadata not provided. Cannot continue."
    
    def svg2srs(self, svgCoord, ndims = 2):
        """
        @type  svgCoord: (float, float)
        @param svgCoord: coordinates in svg coordinate system to be converted
                         into spatial coordinates.
        
        @type  ndims: int
        @param ndims: number of dimensions of returned value (determines if
                      output value will be 2 or 3 dimensional; when C{ndims == 3}
                      coronal coordinate is also included)
        
        @rtype: (float, float) or (float, float, float)
        @return: spatial coordinates corresponding to given svg coordinates
        
        @requires: All metadata has to be provided and correct.
        """
        # Check metadata availability
        self.__validateMetadata()
        
        # Check dimensionality
        assert ndims <= 3, "Invalid output dimensionality"
        
        (x, y) = svgCoord
        (a, b, c, d) = self._metadata[BAR_TRAMAT_METADATA_TAGNAME].value
        coronalC     = self._metadata[BAR_BREGMA_METADATA_TAGNAME].value
        
        # Calculate and return output
        if ndims == 2: return (a*x +b, c*y + d)
        if ndims == 3: return (a*x +b, c*y + d, coronalC)
    
    def srs2svg(self, spatialCoord):
        """
        @type  spatialCoord: (float, float)
        @param spatialCoord: spatial coorrdinate to be converted into SVG
                             coordinate
        
        @rtype:  (float, float)
        @return: SVG coordinates corresponding to provided spatial coordinates
        
        @requires: All metadata has to be provided and correct.
        """
        # Check metadata availability
        self.__validateMetadata()
        
        (a, b, c, d) = self._metadata[BAR_TRAMAT_METADATA_TAGNAME].value
        (xp, yp) = spatialCoord
        
        return ( (xp-b)/a, (yp-d)/c )
    
    def getCommentLabels(self):
        """
        An alias to C{self.L{__getAllLabelsWithType}(self.L{_clsCommentLabel})}.
        """
        return self.__getAllLabelsWithType(self._clsCommentLabel)
    
    def getRegularLabels(self):
        """
        An alias to C{self.L{__getAllLabelsWithType}(self.L{_clsRegularLabel})}.
        """
        return self.__getAllLabelsWithType(self._clsRegularLabel)
    
    def getSpotLabels(self):
        """
        An alias to C{self.L{__getAllLabelsWithType}(self.L{_clsSpotLabel})}.
        """
        return self.__getAllLabelsWithType(self._clsSpotLabel)
    
    def _generateLabelIndex(self):
        """
        @return: label identifier to label representation mapping
        @rtype: {str : L{barStructureLabel}} 
        """
        labelIndexByID = dict(map(lambda lab: (lab.ID, lab), self.labels))
        return labelIndexByID

    @classmethod
    def _fromXML_ParseXML(cls, svgDocument, fixDrawing):
        """
        Part of XML parsing subroutine responsible for parsing given SVG
        document into xml.dom.minidom object. This method may be overriden
        in subclasses if more features are required.
        
        @param svgDocument: SVG slide (DOM XML or filename or file handler)
        @type svgDocument: xml.dom.minidom.Document or str or file
        
        @param fixDrawing: indicates if path definitions has to be redefined
                           with absolute coordinates
        @type fixDrawing: bool
        
        @rtype: xml.dom.minidom.Document
        @return: xml.dom.minidom.Document
        """
        # Parse source SVG file if it is string, leave it otherwise
        if not svgDocument.__class__.__name__ == 'Document':
            svgdom = dom.parse(svgDocument)
        else:
            svgdom = svgDocument
        _removeWhitespacesXML(svgdom)
        
        # Redefine path definitions using absolute coordinates
        if fixDrawing:
            svgfix.fixSvgImage(svgdom, pagenumber=0, fixHeader=False)
        
        svgElement = svgdom.getElementsByTagName('svg')[0]
        # In case, when 3dBAR namespace is not defined, we declare it.
        svgElement.setAttribute('xmlns:bar', BAR_XML_NAMESPACE)
        
        return  svgdom     

    @classmethod
    def _fromXML_BeforeCleanUpHook(cls, slide, svgdom):
        """
        Customization hook allowing the developers implementing additional
        methods or features during parsing of XML document. This hook is
        executed after parsing whole slide, just before cleaning all unnecessary
        elements and extracting slide template.
        """
        pass
    
    @classmethod
    def _fromXML_AfterCleanUpHook(cls, slide, svgdom):
        """
        Customization hook allowing the developers implementing additional
        methods or features during parsing of XML document. This hook is
        executed just after removing all unnecessary elements and before
        assigning slide's template.
        """
        pass    

    @classmethod
    def _fromXML_LoadMetadata(cls, slide, svgdom):
        """
        Part of XML parsing subroutine responsible for extracting metadata
        from provided XML element corresponding to CAF slide.
        This method can be overriden in subclasses if more features are
        required.
        
        @type  slide: L{barVectorSlide}
        @param slide: Slide to which metadata extracted from C{svgdom} will be
                      assigned
        
        @param svgdom: SVG slide (DOM XML or filename or file handler)
        @type svgdom: xml.dom.minidom.Document or str or file
        
        @rtype: None
        @return: None
        """
        
        # Get metadata element and extract all metadata
        # then iterate over all metadata elements and extract values
        metadataDataset =\
                svgdom.getElementsByTagName(BAR_DATA_LOCATION_ELEMENT)[0]
        
        for metadataEntry in metadataDataset.childNodes:
            ### Debug it !!!
            try:
                metadata = cls._clsMetadataElement.fromXML(metadataEntry)
                slide._setMetadata(metadata)
            except:
                pass
        
        # Use extracted metadata elements to define tracing and rendering
        # properties:
        slide._tracingConf  = eval(slide._metadata['tracingConf'].value)
        slide._rendererConf = eval(slide._metadata['rendererConf'].value)
    
    @classmethod
    def _fromXML_Cleanup(cls, slide, svgdom):
        """
        Part of XML parsing subroutine responsible for preparing XML template
        for given slide. This method can be overriden in subclasses
        if more features are required.
        
        @type  slide: L{barVectorSlide}
        @param slide: Currently processed slide.
        
        @param svgdom: SVG slide (DOM XML or filename or file handler)
        @type svgdom: xml.dom.minidom.Document or str or file
        
        @rtype: None
        @return: None
        """
        # remove all paths, labels, etc. leaving slide template
        for element in ['text', 'path', 'bar:data', 'image']:
            for elementToDelete in svgdom.getElementsByTagName(element):
                elementToDelete.parentNode.removeChild(elementToDelete)
    
    slideTemplate=property(_getSlideTemplate, _setSlideTemplate)
    """
    SVG slide template.
    
    Property of non-consistent type.
    """
    
    labels      = property(_getLabels)
    """
    Labels of the slide.
    
    Read-only property.
    
    @type: [L{barStructureLabel}, ...]
    """
    
    labelIndex  = property(_generateLabelIndex)
    """
    Label identifier to label representation mapping.
    
    Read-only property.
    
    @type: {str : L{barStructureLabel}} 
    """
    
    metadata    = property(_getMetadata)
    """
    Slide metadata.
    
    Property of non-consistent type.
    """


class barSlideRenderer(barVectorSlide):
    """
    Class holding all operation related to rasterizing SVG slides. It allows
    rasteizing whole slide, particular structures (by their names), or paths
    with given ID or belonging to particular structures.
    
    Class has to be supplied with various parameters described better in class
    constructor. All rendered images are provided in form of PIL images.
    """
    
    def __init__(self, vectorSlide, rendererConfiguration, tracingConfiguration,
                 slideNumber=0):
        """
        Class requires providing following properties in order to work properly:
          - C{L{rendererConfiguration}['ReferenceWidth']}: (C{int}) width
            of SVG drawing
          - C{L{rendererConfiguration}['ReferenceHeight']}: (C{int}) height
            of SVG drawing
          - C{L{rendererConfiguration}['imageSize']} : (C{(int, int)}) size
            (width, height) of resulting bitmap image
        
        @param rendererConfiguration: renderer configuration (see module
                                      description for details)
        @type  rendererConfiguration: {str : ?, ...}
        
        @type tracingConfiguration: {str : ?, ...}
        @param tracingConfiguration: tracing configuration (see module
                                     description for details)
        
        @param slideNumber: slide number
        @type slideNumber: int
        """
        
        # Save rendering and tracing properties
        self._rendererConf = rendererConfiguration 
        self._tracingConf = tracingConfiguration
        
        # Copy slide's data from provided vector slide info this instnace
        # (and hope that actual data will be copied, not only references ;)
        
        self._metadata         = vectorSlide._metadata
        self._labels           = vectorSlide._labels
        self._slideTemplate    = vectorSlide._slideTemplate
        self.slideNumber       = vectorSlide.slideNumber
    
    def renderSlide(self, otype='pil'):
        """
        An alias for C{self.L{_renderSvgDrawing}(self.L{getXMLelement}(), otype=otype)}.
        """
        return self._renderSvgDrawing(self.getXMLelement(), otype=otype)
    
    def _toSVGCoordinates(self, ImageCoords):
        """
        Transform coordinates given in pixels (in image coordinate system) to
        coordinates in SVG drawing coordinate system (not spatial reference
        system).

        @type  ImageCoords: (int, int)
        @param ImageCoords: image coordinates to transform
        
        @return: coordinates transformed to SVG drawing coordinate system
        @rtype: (float, float)
        """
        
        # Just create few aliases
        imSize    = self._rendererConf['imageSize']
        refWidth  = self._rendererConf['ReferenceWidth' ]
        refHeight = self._rendererConf['ReferenceHeight']
        
        # The formula is extremely simple x/xref * svg_size
        # Where x is size of rendered image, xref - reference size, 
        # svg_size - svg coordinate value
        
        return (float( 1./(imSize[0] / refWidth )* ImageCoords[0] ),\
                float( 1./(imSize[1] / refHeight)* ImageCoords[1] ))
    
    def _toImageCoordinates(self, svgCoords):
        """
        Convert coordinates from SVG image to coordinates in raster image system.
        By default, SVG drawings are rendered with 90 dpi resolution.
        In this resolution one point in SVG drawing is equivalent to one pixel of
        raster image. When SVG is rendered in larger resolution (we do not
        consider smaller resolutions in this software), coordinates has to be
        rescaled. Returned values are rounded to integers.

        @type  svgCoords: (int, int)
        @param svgCoords: coordinates in SVG drawing coordinates system

        @return: image coordinates corresponding to provided SVG coordinates
        @rtype: (int, int)
        """
        
        # Just create few aliases
        imSize    = self._rendererConf['imageSize']
        refWidth  = self._rendererConf['ReferenceWidth' ]
        refHeight = self._rendererConf['ReferenceHeight']
        
        # The formula is extremely simple x/xref * svg_size
        # Where x is size of rendered image, xref - reference size, 
        # svg_size - svg coordinate value
        
        return (int(float( imSize[0] / refWidth * svgCoords[0] )),\
                int(float( imSize[1] / refHeight* svgCoords[1] )))
    
    def _renderSvgDrawing(self, svgdoc, renderingSize = None, boundingBox=None, otype='pil', grayscale=True):
        """
        Renders provided SVG image with varioous options and returns rendered
        image.
        
        Workflow:
            1. Render image and convert it to NumPy array
            2. Manipulate channels and colours, convert to indexed mode
            3. Create and return PIL image
        
        Availiable rendering protocols are:
            - C{'pil'} - returns PIL Image with rendered image,
            - C{'npy'} - returns NumPy array,
            - C{'rec'} - returns NumPy array rendered according to reconstruction
              module requirements
        
        @type  svgdoc: xml.dom.minidom.Document
        @param svgdoc: SVG document to render
        
        @type  renderingSize: (int, int)
        @param renderingSize: Dimensions (in pixels) of the rendered image,
                              before an optional cropping.
        
        @type  boundingBox: (int, int, int, int)
        @param boundingBox: cropping coordinates (left, top, right, bottom);
                            applies only to 'rec' protocol
        
        @type  otype: str
        @param otype: requested rendering protocol - one of C{'pil'}, C{'npy'},
                      C{'rec'}
        
        @type  grayscale: bool
        @param grayscale: determines if returned image would be in grayscale
                          or RGB mode; applies only to C{'pil'} L{protocol<otype>}
        

        
        @todo: Consider rewriting this method to staticmethod
        
        @rtype: PIL.Image.Image or numpy.ndarray
        @return: rendered SVG image
        """
        #TODO: Consider rewriting this method to staticmethod
        
        # Put XML to rsvg
        svg = rsvg.Handle(data = svgdoc.toxml())
        if renderingSize:
            width, height = tuple(map(int, renderingSize))
        else:
            width, height = tuple(map(int,self._rendererConf['imageSize']))
        
        # Allocate memory and create context
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(surface)
        
        # Define dimensions, rescale and render image
        wscale = float(width) / svg.props.width
        hscale = float(height) / svg.props.height
        cr.scale(wscale, hscale)
        svg.render_cairo(cr)
        
        # Save snapshot of rendered image for debug purposes
        #if __debug__: surface.write_to_png ('debugfilename.png')
        
        # Now we need generate PIL image from raw data extracted
        # from cairo surface. The workflow is following:
        # Dump raw image data to numpy, correct channels sequence 
        # And then convert NumPy array to PIL image object.
        
        # Dump image information to NumPy array
        # surface.get_data() returns RGBA array thus we have to
        # reshape this array manually
        a = np.frombuffer(surface.get_data(), np.uint8)
        a.shape = (height, width, 4) ###XXX TODO: width and height are reversed!
        
        # Swap channels (orig) [B,G,R,A] -> [R,G,B,A]
        b=a.copy()
        a[:,:,0]=b[:,:,2]
        a[:,:,2]=b[:,:,0]
        t=(255-a[:,:,3])
        
        # TODO: Optimize it
        a[:,:,0]+=t
        a[:,:,1]+=t
        a[:,:,2]+=t
        
        # Remove unnecessary arrays 
        del b
        del t
        
        # TODO: Perhaps desaturation should be done manually (using numpy)
        # Put final image into cache
        # Ok, we convert numpy array to image, then we convert it to indexed
        # colour and then every color that is not white is set to 200 and after
        # that we have indexed image with 255 colors in which only white and 200
        # are used
        
        # Returns color or grayscaled PIL image
        if otype == 'pil':
            if grayscale == True:
                image = Image.fromarray(a,'RGBA').convert("L")
            else:
                image = Image.fromarray(a,'RGBA').convert("RGB")
            return image
        
        # Returns grayscale npy array
        if otype == 'npy':
            a = 0.2989*a[:, :, 0] + 0.5870*a[:, :, 1] + 0.1140*a[:, :, 2]
            return a.astype(np.uint8)
        
        # Returns scaled and cropped np. array.
        if otype[0:3] == 'rec':
            # Convert bitmap to grayscale
            image = Image.fromarray(a.astype(np.uint8),'RGBA').convert("L")
            
            # Crop region of interest:
            image = image.crop(tuple(map(int,boundingBox)))
            
            # By default reverse image to make background black and foreground
            # white:
            image = ImageChops.invert(image)
            if otype[-1] == '1': image = image.transpose(Image.FLIP_TOP_BOTTOM)
            if otype[-2] == '1': image = image.transpose(Image.FLIP_LEFT_RIGHT)
            volumeSlice = np.array(image.getdata()).reshape(int(image.size[0]), int(image.size[1]), 1)
            return volumeSlice
    
    def values(self):
        """
        A stub of method. Raise NotImplementedError.
        """
        raise NotImplementedError

    def __getSlideSize(self):
        """
        Getter for the L{self.size} property.
        
        @rtype: (int, int)
        @return: tuple with (width, height) of the slide.
        """
        return tuple(map(lambda x:\
            int(self._rendererConf[x]),\
            ['ReferenceWidth','ReferenceHeight']))
    
    def __setSlideSize(self, newSize):
        """
        Setter for the L{self.size} property.
        
        @type  newSize: (int, int)
        @param newSize: Dimensions of the SVG drawing in pixels
        """
        assert map(type, newSize) == map(type, (1,1)),\
                "(int,int) Tuple of two integers required"
        x,y = newSize
        
        self._rendererConf['ReferenceWidth'] = x
        self._rendererConf['ReferenceHeight']= y
        
        self._tracingConf['PoTraceConf']['potrace_width_string'] = str(x) + 'pt'
        self._tracingConf['PoTraceConf']['potrace_height_string']= str(y) + 'pt'
        
        #TODO: This solution is so lame! There should be 'slideTemplate object
        # that could be edited as any other object without digging in xml!
        svg = self._slideTemplate.getElementsByTagName('svg')[0]
        svg.setAttribute('width',  str(x))
        svg.setAttribute('height', str(y))
        svg.setAttribute('viewBox', "0 0 %d %d" % (x,y))
    
    def __getBitmapSize(self):
        """
        Getter for the L{self.bitmapSize} property
        
        @rtype: (int, int)
        @return: Resolution of the rasterized slide in pixels
        """
        return self._rendererConf['imageSize']
    
    def __setBitmapSize(self, newBitmapSize):
        """
        Setter for the L{self.bitmapSize} property.
        
        @type  newBitmapSize: (int, int)
        @param newBitmapSize: resloution of the rasterized slide in pixels.
        
        @raise: ValueError
        """
        assert map(type, newBitmapSize) == map(type,(1,1)),\
                "(int,int) Tuple of two integers required"
        self._rendererConf['imageSize'] = newBitmapSize

    size = property(__getSlideSize, __setSlideSize)
    """
    Get / set the CAF slide dimensions in pixels. 
    
    @type: (int, int)
    """
    
    bitmapSize = property(__getBitmapSize, __setBitmapSize)
    """
    Get / set the size of the image that will be generated after invoking L{self.renderSlide}.
    @type: (int, int)
    """


class barPretracedSlide(barSlideRenderer):
    """
    Class of objects representing countur slides.
    """
    def __init__(self,\
            slideTemplate=CONF_DEFAULT_SLIDE_TEMPLATE,\
            rendererConfiguration=CONF_DEFAULT_RENDERING_PROPS,\
            tracingConfiguration=BAR_TRACER_DEFAULT_SETTINGS,\
            slideNumber=0):
        """
        @type  slideTemplate: str
        @param slideTemplate: SVG slide template
        
        @type rendererConfiguration: {str : ?, ...}
        @param rendererConfiguration: renderer configuration (see module
                                      description for details)
        
        @type tracingConfiguration: {str : ?, ...} 
        @param tracingConfiguration: tracing configuration (see module
                                     description for details)
        
        @type  slideNumber: int
        @param slideNumber: slide number
        """
        barSlideRenderer.__init__(self,\
                barVectorSlide(slideTemplate, slideNumber),\
                rendererConfiguration = rendererConfiguration,\
                tracingConfiguration  = tracingConfiguration,\
                slideNumber = slideNumber)
        
        self._svgPaths= []
        self.markers  = []
    
    def __setitem__(self, key, newLabel):
        """
        Add label to the slide.
        
        @param key: dummy parameter
        
        @param newLabel: label to be added to the slide
        @type newLabel: L{barStructureLabel} 
        """
        self._labels[newLabel.ID] = newLabel
    
    def __getitem__(self, key):
        """
        @param key: label identifier
        @type key: str
        
        @rtype: L{barStructureLabel}
        @return: label of requested identifier
        """
        return self._labels[key]
    
    def __delitem__(self, key):
        """
        Remove label of requested identifier from the slide,
        
        @param key: label identifier
        @type key: str
        """
        del self._labels[key]
    
    def values(self):
        """
        Returns list of all svg paths as DOM Objects.
        
        @rtype: [DOM Object, ... ]
        """
        return self._svgPaths
    
    @classmethod
    def fromXML(cls, svgDocument, fixDrawing=False):
        """
        Create object representing given SVG slide.
        
        @param svgDocument: SVG slide (DOM XML or filename or file handler)
        @type svgDocument: xml.dom.minidom.Document or str or file
        
        @rtype: cls
        @return: created object
        """
        
        # Initialize empty slide with dummy tracing and rendering configuration,
        # slide number empty
        slide = cls()
        svgdom = cls._fromXML_ParseXML(svgDocument, fixDrawing = fixDrawing)
        
        cls._fromXML_LoadMetadata(slide, svgdom)
        cls._fromXML_LoadPaths(slide, svgdom)
        cls._fromXML_LoadLabels(slide, svgdom)
        cls._fromXML_BeforeCleanUpHook(slide, svgdom)
        cls._fromXML_Cleanup(slide, svgdom)
        cls._fromXML_AfterCleanUpHook(slide, svgdom)
        
        slide._setSlideTemplate(svgdom.toxml())
        
        return slide  

    @classmethod    
    def _fromXML_LoadPaths(cls, slide, svgdom):
        """
        Part of XML parsing subroutine responsible for extracting SVG paths from
        provided XML element. This method should be overriden in subclasses if
        more features are required.
        
        @type  slide: L{barVectorSlide}
        @param slide: Slide to which paths extracted from C{svgdom} will be
                      assigned
        
        @param svgdom: SVG slide (DOM XML or filename or file handler)
        @type svgdom: xml.dom.minidom.Document or str or file
        
        @rtype: None
        @return: None
        """
        for pathElement in svgdom.getElementsByTagName('path'):
            slide._svgPaths.append(pathElement)
    
    @classmethod
    def _fromXML_LoadLabels(cls, slide, svgdom):
        """
        Part of XML parsing subroutine responsible for extracting labels and
        markers from provided XML element. This method can be overriden in
        subclasses if more features are required.
        
        @type  slide: L{barVectorSlide}
        @param slide: Slide to which labels extracted from C{svgdom} will be
                      assigned
        
        @param svgdom: SVG slide (DOM XML or filename or file handler)
        @type svgdom: xml.dom.minidom.Document or str or file
        
        @rtype: None
        @return: None
        """
        # Information about spatial coordinate system may be presented in
        # form of markers or as metadata elements. Markers elements has priority
        # over metadata elements. If found, markers are processed first.
        
        # Then extract all text elements and separate them between labels 
        # and markers. Labels are parsed at first as they are more probable
        for labelElement in svgdom.getElementsByTagName('text'):
            try:
                label = cls._clsStructureLabel.fromXML(labelElement)
                slide.addLabel(label)
            except:
                marker = barMarker.fromXML(labelElement)
                slide.markers.append(marker)
    
    def affineTransform(self, M):
        """
        Transform the location (in SVG coordinate system) of every label, marker
        and path in the slide.
        
        @param M: transformation matrix
        @type M: numpy 3x3 array
        
        @return: self
        @rtype: L{barPretracedSlide}
        """
        self.__affineTransform(M)
        return self
    
    def __affineTransform(self, M):
        """
        Transform the location (in SVG coordinate system) of every label, marker
        and path in the slide.
        
        @param M: transformation matrix
        @type M: numpy 3x3 array
        """
        barVectorSlide.affineTransform(self, M)
        map(lambda x: x.affineTransform(M),  self.markers)
        for pathElem in self._svgPaths:
            pathElem.setAttribute('d',\
                    svgfix.fixPathDefinition(pathElem.getAttribute('d'),  M))
   
    def parseMarkers(self):
        """
        Transform information contained in slide markers to slide medatata
        information. Remove markers from the slide.
        """
        
        m1 =[ m for m in self.markers if m.__class__ == barCoordinateMarker][0]
        m2 =[ m for m in self.markers if m.__class__ == barCoordinateMarker][1]
        bm =[ m for m in self.markers if m.__class__ == barCoronalMarker][0]
        self.updateMetadata(processMarkers(m1, m2, bm))
        self.markers = []
     
    def getXMLelement(self):
        """
        Generate XML DOM representation of the object.
        
        @return: generated XML DOM representation
        @rtype: xml.dom.minidom.Document
        
        @todo: Reimplement this in the nice way
        """
        
        # Save tracing and rendering properties as metadata entries:
        self._setMetadata(\
                self._clsMetadataElement('tracingConf', repr(self._tracingConf)))
        self._setMetadata(\
                self._clsMetadataElement('rendererConf', repr(self._rendererConf)))
        
        # Get slide template
        slide = self._getSlideTemplate().cloneNode(True)
        
        svgElement = slide.getElementsByTagName('svg')[0]
        metadataDataset =\
                slide.getElementsByTagName(BAR_DATA_LOCATION_ELEMENT)[0]
        
        for svgGroupDataset in slide.getElementsByTagName('g'):
            if svgGroupDataset.hasAttribute('xml:space'):
                svgGroupDataset.removeAttribute('xml:space')
        
        for metadataElement in self._metadata.values():
            metadataDataset.appendChild(metadataElement.getXMLelement())
        
        for pathElement in self._svgPaths:
            svgGroupDataset.appendChild(pathElement)
        
        for labelElement in self.labels:
            svgGroupDataset.appendChild(labelElement.getXMLelement())
        
        if all(self.markers):
            for markerElement in self.markers:
                svgGroupDataset.appendChild(markerElement.getXMLelement())
        
        # Redefine path definitions using absolute coordinates
        # svgfix.fixSvgImage(slide, pagenumber=self.slideNumber, fixHeader=True)
        return slide
    
    def modifyContours(self, newStrokeWidth = None, newStrokeColour = None):
        """
        Modify width and colour of the contours (paths).
        
        @type  newStrokeWidth: float
        @param newStrokeWidth: new width of contour
        
        @param newStrokeColour: new colour of the contour in hexadecimal
                                format with leading '#'
        @type  newStrokeColour: str
        """
        
        # Create modification dictionary basing on given parameters
        modifications={}
        if newStrokeWidth: modifications['newStrokeWidth'] = newStrokeWidth
        if newStrokeColour:modifications['newStrokeColour']= newStrokeColour
        
        # Iterate over all contours and apply modifications
        for pathElement in self._svgPaths:
            modifyContour(pathElement, modifications)
    
    svgDocument = property(getXMLelement)


class barTracedSlide(barSlideRenderer):
    """
    Class of objects representing CAF slides.
    """
    def __init__(self,\
            slideTemplate = CONF_DEFAULT_SLIDE_TEMPLATE,\
            rendererConfiguration = CONF_DEFAULT_RENDERING_PROPS,\
            tracingConfiguration  = BAR_TRACER_DEFAULT_SETTINGS,\
            slideNumber = 0):
        """
        @type  slideTemplate: str
        @param slideTemplate: SVG slide template
        
        @type rendererConfiguration: {str : ?, ...}
        @param rendererConfiguration: renderer configuration (see module
                                      description for details)
        
        @type tracingConfiguration: {str : ?, ...}
        @param tracingConfiguration: tracing configuration (see module
                                     description for details)
        
        @type  slideNumber: int
        @param slideNumber: slide number
        """
        
        barSlideRenderer.__init__(self,\
                barVectorSlide(slideTemplate, slideNumber),\
                rendererConfiguration = rendererConfiguration,\
                tracingConfiguration  = tracingConfiguration,\
                slideNumber = slideNumber)
                
        self._structures      = {}
   
    @classmethod
    def fromXML(cls, svgDocument, fixDrawing=False):
        """
        Create object representing given SVG slide.
        
        @param svgDocument: SVG slide (DOM XML or filename or file handler)
        @type svgDocument: xml.dom.minidom.Document or str or file
        
        @param fixDrawing: indicates if path definitions has to be redefined
                           with absolute coordinates
        @type fixDrawing: bool
        
        @rtype: cls
        @return: created object
        """
        
        # Initialize empty slide with dummy tracing and rendering configuration,
        # slide number empty
        slide = cls()
        svgdom = cls._fromXML_ParseXML(svgDocument, fixDrawing=fixDrawing)
        
        cls._fromXML_LoadMetadata(slide, svgdom)
        slide._fromXML_LoadStructures(slide, svgdom)
        slide._fromXML_LoadLabels(slide, svgdom)
        slide._fromXML_BeforeCleanUpHook(slide, svgdom)
        slide._fromXML_Cleanup(slide, svgdom)
        slide._fromXML_AfterCleanUpHook(slide, svgdom)
        
        slide._setSlideTemplate(svgdom.toxml())
        
        return slide  
    
    @classmethod    
    def _fromXML_LoadStructures(cls, slide, svgdom):
        """
        Part of XML parsing subroutine responsible for extracting 'structure'
        objects from provided XML element. This method may be overriden
        in subclasses if more features are required.
        
        @type  slide: L{barVectorSlide}
        @param slide: Slide to which structures extracted from C{svgdom} will be
                      assigned
        
        @param svgdom: SVG slide (DOM XML or filename or file handler)
        @type svgdom: xml.dom.minidom.Document or str or file
        
        @rtype: None
        @return: None
        """
        for pathElement in svgdom.getElementsByTagName('path'):
            newPath = cls._clsPath.fromXML(pathElement)
            
            # TODO: Replace with try: except: clause
            if slide.has_key(newPath.structName):
                slide.__getitem__(newPath.structName).addPaths(newPath)
            else:
                strName = newPath.structName
                strColor= newPath.color
                
                newStrc = cls._clsGenericStructure(strName, strColor, [newPath])
                slide.addStructures(newStrc)
    
    @classmethod
    def _fromXML_LoadLabels(cls, slide, svgdom):
        """
        Part of XML parsing subroutine responsible for extracting labels and
        markers from provided XML element. This method can be overriden in
        subclasses if more features are required.
        
        @type  slide: L{barVectorSlide}
        @param slide: Slide to which labels extracted from C{svgdom} will be
                      assigned
        
        @param svgdom: SVG slide (DOM XML or filename or file handler)
        @type svgdom: xml.dom.minidom.Document or str or file
        
        @rtype: None
        @return: None
        """
        for labelElement in svgdom.getElementsByTagName('text'):
            try:
                label = cls._clsStructureLabel.fromXML(labelElement)
                slide.addLabel(label)
            except ValueError:
                _printRed("Error while reading labels: %s\nSkipping." %\
                        (labelElement.toxml(),))
    
    def __setitem__(self, key, newStructure):
        """
        Add structure to the slide.

        @type key: str
        @param key: name of L{the structure<newStructure>}

        @type newStructure: L{barGenericStructure}
        @param newStructure: structure to be added to the slide
        """
        self._structures[key] = newStructure
    
    def __getitem__(self, key):
        """
        @type key: str
        @param key: name of the requested structures

        @return: requested structure
        @rtype: L{barGenericStructure}
        """
        return self._structures[key]
   
    def __delitem__(self, key):
        """
        Remove structure denoted by provided structure name. All paths
        corresponding to the given structure are removed. Every path with
        identifier corresponding to the given structure is also removed.
        
        @type  key: str
        @param key: name of the structure to be removed
        """
        for path in self._structures[key].paths:
            del self._labels[path.relLabelID]
        del self._structures[key]
    
    def keys(self):
        """
        @rtype: [str, ...]
        @return: names of structures in the slide
        """
        return self._structures.keys()
    
    def items(self):
        """
        @rtype: [(str, L{barGenericStructure}), ...]
        @return: (structure name, structure representation) pairs for every slide
                 structure
        """
        return self._structures.items()
    
    def values(self):
        """
        @rtype: [L{barGenericStructure}, ...]
        @return: slide structures
        """
        return self._structures.values()
    
    def __len__(self):
        """
        @rtype: int
        @return: number of structures in the slide
        """
        return len(self._structures)
    
    def __add__(self, op):
        """
        Add two slides.
        
        Preconditions:
            - The transformation matrix of both slides has to be identical,
            - Slides has to have equal 'z' axis location,
            - Slides has to have identical slide templates,
            - Slides has to have identical slide number
            - Slides has to have the same reference rendering and tracing
              properties.
        
        Definition of C{plus} operator:
            - New slide is created with the template and properties taken from
              operands,
            - Slide is filled with the structures from the first operand and
              then from the second operand
            - If operands contains labels, they are copied in the same order as
              structures.
        
        Resolving conflicts:
            - currently labels and paths with identical ids, prevent C{add}
              operation.

        @param op: second term of the addition (the first is the object itself)
        @type op: L{barTracedSlide}

        @return: sum of the slides
        @rtype: L{barTracedSlide}
        """
        
        # Compare the metadata
        # Define elements which values should be equal:
        #elToCompare = ['transformationmatrix', 'coronalcoord',\
        #        'rendererConf', 'tracingConf']
        elToCompare = ['transformationmatrix', \
                'rendererConf', 'tracingConf']
        
        for element in elToCompare:
            val1 = self.metadata[element].value
            val2 = op.metadata[element].value
            if not val1 == val2:
                raise ValueError,\
                        "Cannot add given slides. Metadata elements %s are not equal: %s, %s." % \
                            (element, val1, val2)
        
        if not self.slideTemplate.toxml() == op.slideTemplate.toxml():
            raise ValueError, "Cannot add given slides. Slide templates are not identical."
        
        if not self.slideNumber == op.slideNumber:
            raise ValueError, "Cannot add given slides. Slide numbers are not equal."
        
        commonPathsIds = set(self.pathIndex.keys()) & set(op.pathIndex.keys()) 
        if commonPathsIds:
            raise ValueError, "Cannot add given slides. Slide contains paths with the same IDs: " +\
                ", ".join(map(str, commonPathsIds)) 
        
        commonLabelsIds = set(self.labelIndex.keys()) & set(op.labelIndex.keys())
        if commonPathsIds:
            raise ValueError, "Cannot add given slides. Slide contains paths with the same IDs: " +\
                ", ".join(map(str, commonPathsIds)) 
        
        # Start the actual slides merging:
        slide = self.__class__()
        
        # Copy slide template:
        slide.slideTemplate = self.slideTemplate.toxml()
        
        # Merge metadata and update slide properties:
        slide._metadata={}
        slide.metadata.update(self.metadata)
        slide.metadata.update(op.metadata)
        slide._tracingConf  = eval(slide.metadata['tracingConf'].value)
        slide._rendererConf = eval(slide.metadata['rendererConf'].value)
        
        # Merge paths and labels:
        map(slide.addPath, self.paths + op.paths)
        map(slide.addLabel, self.labels + op.labels)
        
        return slide
    
    def has_key(self, key):
        """
        @param key: name of the structure
        @type key: str

        @return: C{True} if the requested structure is present in the slide;
                 C{False} otherwise
        @rtype: bool
        """
        if key in self._structures: return True
        else: return False
    
    def __addPath(self, newPath):
        """
        Add a path to the slide.
        
        If structure corresponding to the added path exists, path is added to
        the structure. Otherwise new structure holding added path is created.
        This is possible as the path element holds name of the structure which
        it belongs to.
        
        @note: Slide element does not contain L{barPath} elements directly.
               Paths are holded in structure elements so paths are added to
               the structures not to the slide directly.
        
        @type  newPath: L{barPath}
        @param newPath: path to be added to the slide
        """
        if self.has_key(newPath.structName):
            self.__getitem__(newPath.structName).addPaths(newPath)
        else:
            strName = newPath.structName
            strColor= newPath.color
            
            newStrc = self._clsGenericStructure(strName, strColor, [newPath])
            self.addStructures(newStrc)
    
    def addPath(self, newPathElement):
        """
        An alias of C{L{__addPath}(newPathElement)}
        """
        return self.__addPath(newPathElement)
    
    def __generatePathIndex(self):
        """
        @return: path identifier to path representation mapping for all paths
                 in the slide
        @rtype: {str : L{barPath}, ...}
        """
        pathIndexByID = {}
        for structureElement in self.structures:
            map(lambda pathEl: pathIndexByID.__setitem__(pathEl.id, pathEl), 
                          structureElement.paths)
        return pathIndexByID
    
    def _getPaths(self):
        """
        An alias for C{L{__generatePathIndex}().values()}
        """
        return self.__generatePathIndex().values()
    
    def _getStructures(self):
        """
        @rtype: [L{barGenericStructure}, ...]
        @return: representations of all structures in the slide
        """
        return self.values()
    
    def addStructures(self, *args):
        """
        Add provided structures to the slide. Existing structures
        are overwritten with new structures with the same name.

        @type  args: [L{barGenericStructure}, ...]
        """
        for newStructure in args:
            self.__setitem__(newStructure.name, newStructure)
   
    def __validateBoundingBoxes(self):
        """
        Validate bounding boxes. For some datasets it may happen that bounding
        boxes are calculated incorrectly due to data corruption.
        
        @rtype: None
        """
        # Define the broadest allowed bounding box.
        maxBbx = (0, 0, self.size[0], self.size[1])
        
        # Iterate over all structures checking if all of them are correct:
        for structure in self.structures:
            testBbx = structure.bbx
            
            if (maxBbx[0] > testBbx[0]) or (maxBbx[1] > testBbx[1]) \
                or (maxBbx[2] < testBbx[2]) or (maxBbx[3] < testBbx[3]):
                _printRed("Invalid bounding box for structure %s detected. The \
                        bounding box %s is not within allowed boundaries: %s. \
                        Manual investigation is required. Parser will now \
                        continue but probably the slide is corrupted." % \
                        (structure.name, str(testBbx), str(maxBbx)) )
                # Ehh... sometimes it raises false alerts
                #raw_input("Press any Key")
    
    def getXMLelement(self):
        """
        @return: XML representation of the slide
        @rtype: xml.dom.minidom.Document
        """
        # Validate bounding boxes: check if all of them are withing slide's
        # area.
        self.__validateBoundingBoxes()
        
        # Save tracing and rendering properties as metadata entries:
        self._setMetadata(\
                self._clsMetadataElement('tracingConf', repr(self._tracingConf)))
        self._setMetadata(\
                self._clsMetadataElement('rendererConf', repr(self._rendererConf)))
        slide = self._getSlideTemplate().cloneNode(True)
        
        svgElement = slide.getElementsByTagName('svg')[0]
        metadataDataset =\
                slide.getElementsByTagName(BAR_DATA_LOCATION_ELEMENT)[0]
        
        for svgGroupDataset in slide.getElementsByTagName('g'):
            if svgGroupDataset.hasAttribute('xml:space'):
                svgGroupDataset.removeAttribute('xml:space')
        
        for metadataElement in sorted(self._metadata.itervalues(), key=lambda x: x.name):
            metadataDataset.appendChild(metadataElement.getXMLelement())
        
        # Put vBrain as bottom-most structure:
        try:
            for pathElement in self._structures['vBrain'].getXMLelement():
                svgGroupDataset.appendChild(pathElement)
        except:
            pass
        
        for pathElementId in sorted(self.pathIndex):
            pathElement = self.pathIndex[pathElementId]
            if not pathElement.structName == 'vBrain':
                svgGroupDataset.appendChild(pathElement.getXMLelement())
        
        for labelElement in self.labels:
            svgGroupDataset.appendChild(labelElement.getXMLelement())
        
        # Redefine path definitions using absolute coordinates
        # svgfix.fixSvgImage(slide, pagenumber=self.slideNumber, fixHeader=True)
        return slide
    
    def recolor(self, colorMapping):
        """
        Change colour of every slide structure according to the given colour
        mapping. Colours of structures not included in the mapping are preserved.
        
        @param colorMapping: structure name to colour (in hexadecimal format)
                             mapping
        @type colorMapping: {str : str, ...}
        
        @return: self
        @rtype: L{barTracedSlide}
        """
        for structure in self.structures:
            try:
                structure.color = colorMapping[structure.name]
            except:
                pass
        return self
    
    def affineTransform(self, M):
        """
        Transform the location (in SVG coordinate system) of every label and
        path in the slide.

        @param M: transformation matrix
        @type M: numpy 3x3 array

        @return: self
        @rtype: L{barTracedSlide}
        """
        self.__affineTransform(M)
        return self
    
    def __affineTransform(self, M):
        """
        Transform the location (in SVG coordinate system) of every label and
        path in the slide.

        @param M: transformation matrix
        @type M: numpy 3x3 array
        """
        barVectorSlide.affineTransform(self, M)
        map(lambda x: x.affineTransform(M),  self.paths)
    
    def findDuplicatedRegions(self, Options = None, Apply = True):
        """
        Method for post processing of traced files. At this moment, has
        following capabilities:
            
            1. Find regions which are defined by the same path (the same path means
               that the definition of the path <d> attribute is the same for those
               paths). In other words find regions with the same <d> tags.
             
            2. Find corresponding labels for those regions.
                
            3. Remove all but one path.
                    - Leave only one label (the first one) defining given region
                    - Mark other labels as "spot labels" and make them red
            
        Traced file may have all kinds of labels (normal, spot label, comment label).
        Effect it that there should be no overlapping areas in output file, no new
        unlabelled areas and some new spotlabels.
        
        @param Options: dummy parameter - placeholder for further processing
                        options
        
        @type  Apply: bool
        @param Apply: determine if slide is processed or not; when C{True},
                      duplicated paths are removed and labels are
                      changed; otherwise slide is not processed, only
                      duplicated areas are found and returned
        
        @todo: Implement processing options 
        
        @return: mapping of keywords 'preserve' and 'remove' to representations
                 of slide paths to be preserved and removed
        @rtype: {str : [L{barPath}, ...], str : [L{barPath}, ...]}
        """
        
        pathData = map( lambda path: (path, path.pathDef), self.paths )
        pathData.sort(key=lambda path: path[1])
        toChange={'preserve':[],'remove':[]}
        
        # Now the hardest thing: determining which elements will be considered
        # as an actual paths and labels and which of them will be removed or
        # replaced. The approach is following: for each extracted path
        # definition find all other paths with the same definition. Store ID's
        # of those paths in temporary array.
        # Then for all id's of paths with the same definition take the last one
        # and move the id to list of paths that will be preserved. All other
        # paths are denoted as paths to remove. If there is only path with given
        # definition if would be preserved while list of paths to remove would
        # be empty
        
        for pathDef in pathData:
            tempresult = ([x[0] for x in pathData if x[1]==pathDef[1]], pathDef[1])
            elementToBePreserved = tempresult[0].pop()
            elementsToBeRemoved=tempresult[0]
            toChange['preserve'].append(elementToBePreserved)
            toChange['remove'].append(elementsToBeRemoved)
        
        # Make flat list of unique id's to remove and to preserve
        toChange['preserve']=list(set(flatten(toChange['preserve'])))
        toChange['remove']  =list(set(flatten(toChange['remove'])))
        
        # When processing flag is set to False, do not process slide - just
        # return list of duplicated labels
        if Apply:
            self.__processDuplicates(Options, toChange)
        
        return toChange

    def __processDuplicates(self, Options, listOfChanges):
        """
        Process paths and labels in following way:
            - Remove paths that should be removed
            - Change type of corresponding label to SpotLabel
        
        @param listOfChanges: mapping of keyword 'remove' to representation
                              of slide paths to be removed
        @type listOfChanges: {str : [L{barPath}, ...], ...}
        
        @param Options: dummy parameter - placeholder for further processing
                        options
        """
        
        # Iterate all paths that are marked for removal
        # remove them and change type of corresponfing label to barSpotLabel
        for pathToRemove in listOfChanges['remove']:
            # ltrID    = Label to rename id 
            # prtID    = path to remove id
            # ptrStrNa = path to remove structure name
            
            ltrID = pathToRemove.relLabelID
            prtID = pathToRemove.id
            ptrStrNa = pathToRemove.structName
            
            # Change type of corresponding label to spotlabel
            self._labels[ltrID] =\
                    self._clsStructureLabel.castToSpotLabel(self._labels[ltrID])
            
            # Print debugging information: 
            print >>sys.stderr, "Removing path with is %s" % prtID
            print >>sys.stderr, "\tFrom structure %s" % ptrStrNa
            print >>sys.stderr, "Type of label with id: '%s' changed to spotlabel" % str(prtID)
           
            # Finally remove path
            del  self[pathToRemove.structName]._paths[pathToRemove.id]
    
    def __setCrispEdges(self, boolValue):
        """
        Set 'L{crispEdges<barGenericStructure.crispEdges>}' attribute for
        every structure representation in the slide.
        
        @param boolValue: new value of the attribute
        @type boolValue: bool
        """
        assert type(boolValue) == type(True), "Boolean value expected"
        map(lambda x: setattr(x, 'crispEdges', boolValue), self.values())
    
    def __getCrispEdges(self):
        """
        @rtype: bool
        @return: C{True} if every structure representation in the slide has
                 the 'L{crispEdges<barGenericStructure.crispEdges>}' attribute
                 equal C{True}; C{False} false.
        """
        return all( map(lambda x: getattr(x, 'crispEdges'), self.values()) )
    
    paths       = property(_getPaths)
    """
    Representations of all paths in the slide.
    
    Read-only property.
    
    @type: [L{barPath}, ...]
    """
    
    pathIndex   = property(__generatePathIndex)
    """
    Path identifier to path representation mapping for all paths in the slide.
    
    Read-only property.
    
    @type: {str : L{barPath}, ...}
    """
    
    structures  = property(_getStructures)
    """
    Representations of all structures in the slide.
    
    Read-only property.
    
    @type: [L{barGenericStructure}, ...]
    """
    
    svgDocument = property(getXMLelement)
    """
    XML representation of the slide.
    
    Read-only property.
    
    @type: xml.dom.minidom.Document
    """
    
    crispEdges     = property(__getCrispEdges, __setCrispEdges)
    """
    The 'L{crispEdges<barGenericStructure.crispEdges>}' attribute of all contained 
    structures. When read C{True} if the value of the attribute of every contained
    structure is C{'crispEdges'}, C{False} otherwise.
    
    @type: bool
    """


class barTracedSlideRenderer(barTracedSlide):
    """
    L{barTracedSlide} class extension with method necessary to render CAF slide.
    """
    def __generateLabelLocation(self, path):
        """
        Generate best label localtion for given path representation. The optimal
        position of the label is determined using maximum value of distance
        transform.

        @type  path: L{barPath}
        @param path: path for which best label location is determined
        
        @rtype: (float, float)
        @return: optimal coordinates (x, y) of the label in SVG coords
        """
        slideRendering = self.renderPath(path)
        (x,y) = getBestLabelLocation(slideRendering)
        (x,y) = self._toSVGCoordinates((x,y))
        return (x, y)
    
    def getSlideMassCenter(self):
        """
        Calculate mass center of the slide basing on grayscale slide
        representation.

        @rtype: (float, float)
        @return: coordinates (x, y) of the mass center in SVG coords
        """
        imgMassCentre = massCentre(self.renderSlide())
        return self._toSVGCoordinates(imgMassCentre)
    
    def getMask(self, maskColor='#000000'):
        """
        Change colour of every structure in the slide to given colour.
        
        @param maskColor: colour in hexadecimal format
        @type maskColor: str
        
        @return: self
        @rtype: L{barTracedSlideRenderer}
        """
        map(lambda x: setattr(x, 'color', maskColor), self.structures)
        return self 
        
    def generateLabels(self, skipLabels = []):
        """
        Assign text label for each path in the slide and place it in the center
        (according to maximal value of distance transform) of the path.
        
        All existing regular labels are erased while comment labels and spot
        labels remains.
        
        @type  skipLabels: [str, ...]
        @param skipLabels: names of structures which labels are preserved
        
        @rtype: L{barTracedSlide}
        @return: self
        """
        # Clone existing slide and clear all regular labels.
        # Do not delete other types of labels
        toRemoveID = [l.ID for l in self.labels if l.__class__ == self._clsRegularLabel]
        map(lambda y: self._labels.__delitem__(y), toRemoveID)
        
        # Get path index from original slide
        pathIndex = self.pathIndex
        print pathIndex 
        
        # Iterate over all paths and generating new regular label for each
        # path
        #for (pathNo, pathID) in enumerate(pathIndex.keys()): 
        for path in pathIndex.values():
            newLabelID      = path.relLabelID 
            newLabelCaption = path.structName 
            print newLabelID,newLabelCaption
            # Skip processing this label if requested
            if newLabelCaption in skipLabels: continue
            newLabelCoords = self.__generateLabelLocation(path)
            print newLabelCoords
            # Generate new label and append it into the slide
            newLabel = self._clsRegularLabel(newLabelCoords, newLabelCaption, newLabelID)
            self.addLabel(newLabel)
        
        return self
    
    def renderStructureList(self, structureNameList):
        """
        Render image of requested structures. At least one of the structures
        has to be defined in the slide or blank white image will be returned.

        Structures are recognized by names of barStructure 
        
        Workflow:
            1. Get empty slide using template from existing slide.
            2. Copy desired structures into new slide leaving other structurees
            3. Render temporary slide and return generated image.

        @type  structureNameList: [str, ...]
        @param structureNameList: names of structures to be rendered
        
        @rtype: PIL.Image.Image
        @return: rendered image
        """
        tempSlide = self.getStructuresSubset(structureNameList)
        
        # Render temporary slide and return the results
        return self._renderSvgDrawing(tempSlide.getXMLelement())
    
    def getStructuresSubset(self, structureNameList):
        """
        @param structureNameList: structures to be included in the returned
                                  slide
        @type structureNameList: [str, ...]

        @return: slide containing only requested structures
        @rtype: L{barTracedSlideRenderer} 
        """
        
        # Create temporary slide
        tempSlide = self.__class__(\
                slideTemplate = self.slideTemplate.toxml(),
                slideNumber = self.slideNumber,
                rendererConfiguration = self._rendererConf,
                tracingConfiguration  = self._tracingConf)
        
        # Copy structures that we want to render into new slide
        slideStructNames = map(lambda x: getattr(x,'name'), self.values())
        existingStructures = list(set(structureNameList) & set(slideStructNames))
        for structureName in existingStructures:
            tempSlide[structureName] = self[structureName]
        
        # Also, remember to copy metadata
        tempSlide._metadata = self._metadata
        
        return tempSlide
    
    def renderPath(self, pathObject):
        """
        Render the path image.
        
        Returned image has two colors: white for background, black for
        foreground.

        @type  pathObject: L{barPath}
        @param pathObject: path representation
        
        @rtype: PIL.Image.Image
        @return: rendered image
        """
        # Generate temporary slide that will hold only the pathObject path.
        tempSlide = self.__class__(\
                self.slideTemplate.toxml(),
                slideNumber = self.slideNumber,
                rendererConfiguration = self._rendererConf,
                tracingConfiguration  = self._tracingConf)
        
        # Also, remember to copy metadata
        tempSlide._metadata = self._metadata
        
        # Unfortunately, we need to create xml document and append path in th
        # 'dom' manner :(
        singlePathDocument = tempSlide.getXMLelement()
        pe = pathObject.getXMLelement() # pe stands for pathElement
        
        # If path element has defined fill color remove it and overwrite it with
        # inline style
        if pe.hasAttribute('fill'): pe.removeAttribute('fill')
        styleDict = parseStyle(pe.getAttribute('style'))
        styleDict['fill']='#000000'
        pe.setAttribute('style', formatStyle(styleDict))
        
        # Append path to empty slide template
        for layer in singlePathDocument.getElementsByTagName('g'):
            if layer.getAttribute('id') == 'content':
                layer.appendChild(pe)       
        #singlePathDocument.getElementsByTagName('g')[0].appendChild(pe)
        
        # return prepared slide and return resulting image
        return self._renderSvgDrawing(singlePathDocument)
    
    def contourize(self):
        """
        Convert given CAF slide into contour slide by removing fill from paths
        and assigning them contours.

        @rtype: L{barPretracedSlideRenderer}
        @return: contour slide based on the CAF slide
        """
        contourSlideRen = barPretracedSlideRenderer.fromXML(
                self.getXMLelement())
        
        contourSlideRen.slideNumber = self.slideNumber
        contourSlideRen.modifyContours(
                newStrokeWidth = CONF_DEFAULT_CONTOUR_WIDTH,\
                newStrokeColour= CONF_DEFAULT_CONTOUR_COLOUR)
        
        # Check if vBrain labels are defined, if they are
        # skip, if not, add them 
        if not len(self.getLabelByName('vBrain')):
            contourSlideRen.addLabel(\
                    self._clsRegularLabel(CONF_DEFAULT_VBRAIN_LABEL_LOC,\
                    'vBrain', 'labelvBrain0'))
        
        return contourSlideRen


class barPretracedSlideRenderer(barPretracedSlide):
    """
    Class which converts contour slides into CAF slides.
    
    @todo: Perhaps replacing all PIL procedures with NumPy rutines will give
           some speedup?

    @type __labelCache: {str : L{barStructureLabel}, ...}
    @ivar __labelCache: temporary cache holding labels from contour slide;
                        removed after tracing
        
    @type __labelsLeft: [L{barStructureLabel}, ...]
    @ivar __labelsLeft: labels undergoing tracing procedure; removed after
                        tracing
        
    @type __vBrainLabels: [L{barStructureLabel}, ...]
    @ivar __vBrainLabels: subset of L{__labelCache} holding C{'vBrain'}
                          labels processed in different way than other labels
        
    @type __imageCache: [PIL.Image.Image, ...]
    @ivar __imageCache: images representing slide; consecutive elements have
                        thicker contours due to gap filling algorithm
        
    @type __brainOutline: PIL.Image.Image
    @ivar __brainOutline: whole brain outline; image is generated in moment
                          of provedding vBrain labels; during tracing consecutive
                          areas are substracted from brain outline; remaining
                          white areas are considered as ublabelled areas
        
    @type _tracingConf: {str : ?, ...}
    @ivar _tracingConf: tracing configuration (see module description for details)
    """
    
    def trace(self, colorMapping):
        """
        Perform tracing of the slide according to C{self.L{_tracingConf}}.

        @type   colorMapping: {str : str, ...}
        @param  colorMapping: structure name to hexadecimal color mapping
                              defining unique colour for each structure
        
        @rtype: L{barTracedSlideRenderer}
        @return: traced slide created by tracing the contour slide
        """
        if __debug__: _printRed("Initializing tracing...")
        
        # Remove unlabelled labels
        self.deleteLabelByCaption('Unlabelled')
        self.deleteLabelByCaption('Unlabeled')
        
        # Cache labels in order to add them later to the traced slide.
        # Extract regular labels - seeds for tracing
        self.__labelCache = self._labels
        self.__labelsLeft = self.getRegularLabels() # Holds labels yet unprocessed
        
        # Extract vBrain labels in order to create brain outline
        self.__vBrainLabels = self.getLabelByName('vBrain', oType = 'ref',\
                                                labelType=self._clsRegularLabel)
        if len(self.__vBrainLabels) == 0:
                _printRed("No vBrain labels detected. Skipping.")
                return None
        
        # Set growlevel=0 for vBrain labels.
        map(lambda x: x.__setattr__('growlevel',0), self.__vBrainLabels)
        map(self.__labelsLeft.remove, self.__vBrainLabels)
        
        self._trPathGen = 0 # Simple path number holder 
        
        # Remove labels from this slide so they
        #do not interrupt tracing process.
        self._labels = {}        
        
        # Create bitmap cache and load images into cache 
        self.__imageCache = []
        self.__loadImage()
        self.__createCache()
        
        # Create empty traced slide
        retSlide = barTracedSlideRenderer(
             slideTemplate = self.slideTemplate.toxml(),\
             rendererConfiguration = self._rendererConf,\
             tracingConfiguration  = self._tracingConf)
        retSlide._metadata = self._metadata
        
        # Append vBrain structure to the traced slide
        if __debug__: _printRed("Processing vBrain...")        
        map(retSlide.addPath, self.__processVbrain())
        map(retSlide.addLabel, self.__vBrainLabels)
        
        # This is a bit tricky: At first we detect all incorrectly placed labels
        # then we remove them from tracing, 
        if __debug__: _printRed("Detecting invalidly placed labels...")        
        labelsRejected =  self.__getMissplacedLabels()
        map(self.__labelsLeft.remove, labelsRejected)
        
        # Rejected labels has to be changed to comment labels in contour slide.
        # Fortunately they are distinguished by id. in order to avoid
        # duplicationg IDs first we remove labels with ids ofrejected labels and
        # then we put actual rejected labels
        map(self.__labelCache.__delitem__, map(lambda x: getattr(x,'ID'),labelsRejected))
        labelsRejected =  map(lambda x: x.castToSpotLabel(x), labelsRejected)
        map(lambda x: self.__labelCache.__setitem__(x.ID, x), labelsRejected)
        map(retSlide.addLabel, labelsRejected)
        
        # Processing correctly placed regular labels - main part of the script.
        if __debug__: _printRed("Processing labels...")  
        map(retSlide.addPath, self.__processLabels())
        map(retSlide.addLabel, self.__labelsLeft)
        
        if self._tracingConf['DetectUnlabelled']:
            if __debug__: _printRed("Detecting unlabelles areas...")
            #TODO: Remove unlabelled areas from the labelCache
            UnlabelledLabels, UnlabelledPaths = self.__getUnlabeled()
            map(retSlide.addPath, UnlabelledPaths)
            map(retSlide.addLabel, UnlabelledLabels)
        else:
            UnlabelledLabels = []
        
        if __debug__: _printRed("Finishing...")
        # Put all remaining labels back to the contour slide
        self._labels = self.__labelCache
        map(self.addLabel, UnlabelledLabels)
        
        self.__clearAfterTracing()
        
        return retSlide.recolor(colorMapping)
    
    #{ Subprocedures - in order of execution
    def __loadImage(self):
        """
        Render provided contour slide with given resolution and put
        rendered image as a first element of C{self.L{__imageCache}}.

        It is assumed that C{self.L{__imageCache} == []}.
        """
        self.__imageCache.append(\
                Image.eval(self.renderSlide(), self.__setContourColor))
    
    def __setContourColor(self, pixelColorValue):
        """
        Apply treshold function for given pixel value. All pixels which are
        non-white pixels becomes C{self.L{_tracingConf}['GrowDefaultBoundaryColor']}
        pixels. This procedure assures that output image has only two colours
        (white and boundary) which is very convinient in further processing.
        
        @type  pixelColorValue: int
        @param pixelColorValue: value of given pixel
        
        @rtype: int
        @return: 255 if white pixel is given, C{self.L{_tracingConf}['GrowDefaultBoundaryColor']}
                 otherwise
        """
        # Just make an alias (perhaps it executes faster)
        defaultBoundaryColour = self._tracingConf['GrowDefaultBoundaryColor']
        
        if pixelColorValue != 255: return defaultBoundaryColour
        else: return 255

    def __createCache(self):
        """
        Create image cache (C{self.L{__imageCache}}). First cached image is
        an original image. All other images (up to cacheLevel) are images with
        succesive grows (applications of MinFilter).
        """
        # Just aliases:
        intensity  = self._tracingConf['MinFiterTimesApplication']
        cacheLevel = self._tracingConf['CacheLevel']
        
        filter = ImageFilter.MinFilter(intensity)
        for l in range(cacheLevel):
            self.__imageCache.append(\
                    self.__imageCache[-1].filter(filter))

    def __processVbrain(self):
        """
        Create outline of the whole brain. The outline serves further as a
        reference for detecting missplaced labels and obviously as structure
        representing whole brain.
        
        Outline is created by substracting result of flooding each vBrain label
        and then inversing the result and tracing resulting bitmap.
        
        @rtype: [L{barPath}, ...]
        @return: paths representing outline of the whole brain
        """
        
        # Create empty white image for filling it with vBrain structure:
        self.__brainOutline =  ImageChops.constant(self.__imageCache[0], 255)
        
        # Then create image mask for vBrain structure;
        for (i, vBrainLabel) in enumerate(self.__vBrainLabels):
            self.__substractFromBrainOutline(\
                    self.__applyFill(self.__imageCache[0], vBrainLabel),\
                    source = 'Brain')
            
            if __debug__ and self._tracingConf['DumpVBrain']:
                self.__brainOutline.save("%d_vBrain_%s.png"\
                        % (self.slideNumber, vBrainLabel.ID))
        
        return self.__bitmapToPaths(self.__brainOutline, vBrainLabel, invert = True)
    
    def __getMissplacedLabels(self):
        """
        Dectect labels that cannot be traced as they are missplaced: placed
        over the contours or outside the brain area.
        
        @rtype: [L{barRegularLabel}, ...]
        @return: labels that has to be excluded from tracing
        """
        toRemove = []
        # Iterate over all labels and find those which are not suitable for
        # tracing
        for label in self.__labelsLeft:
            if not self.__isAllowedForFilling(self.__imageCache[0], label):
                toRemove.append(label)
        return toRemove
    
    def __processLabels(self):
        """
        Create list of paths basing on the list of labels to be traced
        (C{self.L{__labelsLeft}}).
        
        @rtype: [L{barPath}, ...]
        @return: paths created by tracing individual labels 
        """
        paths = []
        noLabels = len(self.__labelsLeft)
        for i, seedLabel in enumerate(self.__labelsLeft):
            print >>sys.stderr, "\nProcessing label %d of %d" % (i, noLabels)
            print >>sys.stderr, "\tStructure: %s, Id: %s" % (seedLabel.Caption, seedLabel.ID)
            print >>sys.stderr, "\tLocation: %3.1f,%3.1f" % seedLabel.Location
            paths.append(self.__processSingleLabel(seedLabel))
        return flatten(paths)
    
    def __getUnlabeled(self):
        """
        Create list of paths and corresponding labels by tracing areas that
        were not labeled in pretraced files (unlabeled areas). This process 
        is rather complicated so few words of explanation:
        
            1. We look for patches of N or more pixels. Only such areas
               are considered as unlabelled areas. Smaller areas are most
               probably residual white pixels and should be ommited.
            2. Every group of two or more adjacent white pixels is flooded
               on "1".
            3. Patch of N or more white pixels is flooded with value "2"
               after tracing.
        
        After fiding unlabelled areas we can find 4 values of pixels:
        
            1. "0": areas outside brain
            2. "1": pixels of more than one adjacent pixels but less than N
            3. "2": patches of N or more white pixels
        
        @rtype: ([L{barPath}, ...], [L{barRegularLabel}, ...])
        @return: pair of lists of paths and corresponding labels generated
                 during detections of unlabelled areas.
        """
        
        # Two types of elements are collected: patch covering unlabelled areas
        # and corresponding labels
        
        unlabeledAreasLabelsList= []   # Here we hold all newly generated labels
        unlabeledPathList       = []   # and here all newly generated labels
        whiteCoordList=[]              # List of coordinates white pixels. Coordinates
                                       # are corrected in on order to avoid analyzing
                                       # the same coordinates twice.
        
        #coords = self.__getUnlabeledAreas()# Get initial white pixel coordinate and start loop
        
        #while coords and (coords not in whiteCoordList):
        unlabelledTreshold = self._tracingConf['UnlabelledTreshold']
        for coords in self.__getUnlabeledAreas():
        
            # Flood image at give coordinates. "1" index is used, not "0". Also get number
            # number of flooded pixels.
            numberOfFloodedPixels = floodFillScanlineStack(self.__brainOutline, coords, 1)
            
            whiteCoordList.append(coords) # Append coordinates to list in order
                                          # to avoid duplication
            
            # When more than N pixels is flooded we should consider this area as
            # an actual unlabelled area (not some residual single white pixels)
            # and we should start tracing procedure.
            if numberOfFloodedPixels > unlabelledTreshold:
             
                # Replace colors to get image suitable for tracing:
                # all colors are converted to white. Values "1" are converted to "0"
                # so the structure is black and surroundings are white
                ImageForTracing = self.__brainOutline.point([255]+[0]+254*[255])
                newLabelLocation = getBestLabelLocation(ImageForTracing)
                
                newLabel = self._clsRegularLabel(\
                            self._toSVGCoordinates(newLabelLocation),\
                            'Unlabelled',\
                            'Unlabelled-%d-%d' % coords,\
                            growlevel = 0)
                unlabeledAreasLabelsList.append(newLabel)
                
                # Apply minimum filter to slightly increase size of trace structures.
                #ImageForTracing = ImageForTracing.filter(ImageFilter.MaxFilter(3))
                map(unlabeledPathList.append, self.__bitmapToPaths(ImageForTracing, newLabel))
                if __debug__ and self._tracingConf['DumpEachStepPNG']:
                    self.__brainOutline.save("%d_detected_ublabelled_%d_%d.png"%\
                            (self.slideNumber, coords[0], coords[1]), "PNG")
                
            # Finally, do some trick: replace all pixels with value "1" to "2",
            # which prevents from accumulating consecutive areas.
            print "Unlabelled area found at location %d, %d (img.)" % coords
            print "\tcreating Unlabelled label\n"
            numberOfFloodedPixels = floodFillScanlineStack(self.__brainOutline, coords, 2)
            
            # Get new coordinates and cotinue loop
            #coords = self.__getUnlabeledAreas()
        
        # Dump image after tracing unlabelled areas to show what we have done! :)
        if __debug__ and self._tracingConf['DumpEachStepPNG']:
            self.__brainOutline.save("%d_after_tracing.png"% self.slideNumber, "PNG")
        return (unlabeledAreasLabelsList, unlabeledPathList)

    def __clearAfterTracing(self):
        """
        Clear all temporary class attributes created for tracing purposes.
        Invoked by C{self.L{trace}} method as the last step of tracing.
        """
        
        # Remove all temporary attributtes
        del self.__labelCache
        del self.__labelsLeft
        del self.__vBrainLabels
        del self.__imageCache
        del self.__brainOutline
    #}
    
    #{ Main functions - they do most of the work
    def __processSingleLabel(self, seedLabel):
        """
        Extract a path defined by coordinates of the given seed label.

        If grow level for given seed label is not provided, perform automatic
        grow level selection, and finally create path with all properties.
        
        @type  seedLabel: L{barRegularLabel}
        @param seedLabel: seed label
        
        @rtype: [L{barPath}, ...]
        @return: list of paths resulting from tracing of the given source image
                 and provided L{seed label<seedLabel>}.

        @note: Function for determinating best grow level may be changed by
               assigning to C{self._tracingConf['BestFillAlgorithm']} reference
               for desired function.
        """
        
        # If growlevel is unassigned, select best growlevel automatically:
        if seedLabel.growlevel == -1:
            # Get area covered by each fill then choose best growlevel
            imgs, area    = self.__getCoveredAreasList(seedLabel)
            # Detect 'None' images and do not include them in automatic grow
            # level selection:
            if area.count(None)>0: area = area[0:area.index(None)]
            
            # Determine BestGrowLevel using provied BestFillAlgorithm
            BestGrowLevel = selectBestGapFillingLevel(area)
            imageToTrace  = imgs[BestGrowLevel]
            seedLabel.growlevel = BestGrowLevel
            print >>sys.stderr, "\tAssigned growlevel %d" % (BestGrowLevel,)
        
        # If growlevel is provided, use it:       
        elif 0 <= seedLabel.growlevel <= self._tracingConf['CacheLevel']:
            imageToTrace = self.__applyFill(\
                              self.__imageCache[seedLabel.growlevel],\
                              seedLabel)
            
            # Sometimes, image cannt be traced with given growlevel (ie. when
            # contours are overgrown). This should not happen when grow level is
            # determinated automatically.
            if not imageToTrace:
                #TODO: Provide error handling here
                print seedLabel
                return
             
            print >>sys.stderr, "\tUsing growlevel %d" % (seedLabel.growlevel,)            
        
        # If provided growlevel is not in allowed ragnge, skip tracing
        # particular label
        else:
            print >>sys.stderr, "Growlevel %d out of allowed range - \
                                skipping" % (seedLabel.growlevel,)
        
        # Substract traced structure from brain outline to mark that given area
        # is already traced.
        self.__substractFromBrainOutline(imageToTrace)
        return self.__bitmapToPaths(imageToTrace, seedLabel)
    
    def __bitmapToPaths(self, sourceImage, seedLabel, invert = False):
        """
        Perform all operation releted with tracing bitmap into list of paths:
             
            1. create DOM structure from PoTrace SVG output,
            2. create single path segments instead of long bezier paths,
            3. convert path coordinates to absolute,
            4. reduce transformation rules (using L{svgfix} module.
                    
        @type  sourceImage: PIL.Image.Image
        @param sourceImage: image for tracing
        
        @type  seedLabel: L{barRegularLabel}
        @param seedLabel: seed label
        
        @type  invert: bool
        @param invert: determine if image has to be inverted before tracing
        
        @rtype: [L{barPath}, ...]
        @return: paths resulting from tracing of the given source image
                 and the provided L{seed label<seedLabel>}.
        """
        # Invert source image, if requested:
        if invert:
            sourceImage = ImageOps.invert(sourceImage)
        
        # Perform tracing procedure and cleam output
        tracerOutput = performTracing(sourceImage,\
                           self._tracingConf['PoTraceConf'])
        svgdom = cleanPotraceOutput(tracerOutput)
        
        # Convert resulting svg document into set of barPaths
        newPathList = map(lambda x:\
                self._getPath(x, seedLabel),\
                svgdom.getElementsByTagName('path'))
        
        # If debuging procedures are enabled save tracing results (SVG file) and
        # source image (PNG file)
        if __debug__ and self._tracingConf['DumpEachStepSVG']:
            OutputFilename = "%d_%s_%s.svg" % (self.slideNumber,\
                    seedLabel.ID, seedLabel.Caption)
            self._saveSVG(svgdom, OutputFilename)
        
        if __debug__ and self._tracingConf['DumpEachStepPNG']:
            OutputFilename = "%d_%s_%s.png" % (self.slideNumber,\
                    seedLabel.ID, seedLabel.Caption)
            self._saveBitmap(sourceImage, OutputFilename)
        
        return newPathList
    
    def _getPath(self, pathElem, seedLabel):
        """
        Create L{barPath} from provided SVG path element (result of tracing)
        and seed label. Resulting path has proper identifier and structure name,
        however it has black colour assigned.

        @param pathElem: xml.dom.minidom.Node
        @type  pathElem: SVG path element 
        
        @param seedLabel: L{barRegularLabel}
        @type  seedLabel: seed label
        
        @rtype: L{barPath}
        @return: path representation created from provided SVG path element
        """
        #Assign dummy id and fill color to avoid parPath constructor errors
        pathElem.setAttribute('id','structure_0_dummy')
        pathElem.setAttribute('fill','#000000')
        
        # Create new path element
        newPath = self._clsPath.fromXML(pathElem, clearPathDef = True)
        newPath.id = self._getNewPathID(seedLabel)
        newPath.structName = seedLabel.Caption
        
        return newPath
    
    def _getNewPathID(self, seedLabel):
        """
        Generate proper path identifier of the path related to the seed label.

        @param seedLabel: L{barRegularLabel}
        @type  seedLabel: seed label
        
        @rtype: str
        @return: identifier of new path generated using
                 C{self.L{_tracingConf}['NewPathIdTemplate']}
        """
        self._trPathGen+=1
        newPathId = self._tracingConf['NewPathIdTemplate'] %\
                (self._trPathGen, seedLabel.ID, seedLabel.Caption)
        return newPathId
    
    def __substractFromBrainOutline(self, imageToSubstract, source = 'Struct'):
        """
        Mark traced areas on L{__brainOutline}. Depending on L{source} marking
        is performed in different way. Region denoted by vBrain regions are
        changed to black (0) while areas from tracing normal labels are changed
        to 100.

        @param imageToSubstract: PIL image
        @type  imageToSubstract: PIL.Image.Image
        
        @type  source: str
        @param source: determines source of L{imageToSubstract} (may be either
                       C{'Struct'} or C{'Brain'}).
        """
        
        # Save brain contour to further comparison
        # Apply treshold eliminating all non-black pixels
        if source == 'Struct':
            self.__brainOutline=\
                    ImageChops.darker(self.__brainOutline,\
                    imageToSubstract.point([100]+255*[255]))
        
        if source == 'Brain':
            self.__brainOutline=\
                    ImageChops.multiply(\
                    imageToSubstract.point([0]+255*[255]),\
                    self.__brainOutline)
    
    def __applyFill(self, sourceImage, seedLabel, retNPIX = False):
        """
        Apply flood fill to given image using coordinates passed in the
        seed label.
        
        Description:
            1. Extract coordinates and structure name from C{seedLabel}.
            2. Rescale SVG coordinates to rendered image coordinates
            3. Fill given image with black color 
            4. Extend filled region by applying C{MinFilter} filter. Do it C{l+1} times
            5. Return flooded image or return number of black pixels depending
               on C{retNPIX} value.
        
        @type  sourceImage: PIL.Image.Image
        @param sourceImage: image to be floodfilled
        
        @type  seedLabel: L{barRegularLabel}
        @param seedLabel: seed label
        
        @type  retNPIX: bool
        @param retNPIX: if C{True}, floodfilled image is returned along with
                        number of replaced pixels; otherwise only flooded
                        image is returned
        
        @rtype: (PIL.Image.Image, int) or PIL.Image.Image
        @return: flooded image (and number of flooded pixels if requested)
        """
        coords = self._toImageCoordinates(seedLabel.Location)
        
        # Determine if it is posssble to flood fill at given coordinate
        if not self.__isAllowedForFilling(sourceImage, seedLabel):
            return None
        
        # Copy input image in order to preserve original
        ImToFlood=sourceImage.copy()
        npix = floodFillScanlineStack(ImToFlood, coords, 0)
        
        # Extend flooded area in order to preserve initial structure area
        # Index of image C{im} in L{ImageCache<ImageCache>} list.
        # Used in extending grow region - MIN filter is applied to flooded
        # region C{l+1} times
        # in order to preserve area of the original structure (as initial edge
        # growing reduces it).
        # Factor 1 is arbitraty.
        for j in range(seedLabel.growlevel + 1):
            ImToFlood = ImToFlood.filter(ImageFilter.MinFilter(3))
        
        if retNPIX: return (ImToFlood, npix)
        else: return ImToFlood
    
    def __isAllowedForFilling(self, im, seedLabel):
        """
        Determine if bitmap with given seed label is suitable for tracing.
        There are briefly two conditions which need to be satisfied in order
        to allow the tracing:
        
            1. Seed has to be placed within brain contour. The brain contour is
               defined at the begining of tracing procedure.
            2. Seed has to be placed at white pixel. If seed points into
               non-white pixel is it a) border between two structures; b) area
               outside brain contour.
        
        In both cases debug information is printed.
        
        @type  im: PIL.Image.Image 
        @param im: image to be floodfilled
        
        @param seedLabel: L{barRegularLabel}
        @type  seedLabel: seed label
        
        @rtype: bool
        @return: C{True} if image is suitable for tracing (according to testing
                 conditions), C{False} otherwise
        """
        if not self.__isOutsideBrainOutline(seedLabel): return False
        if not self.__isOverContour(im, seedLabel): return False
        return True
    
    def __getUnlabeledAreas(self):
        """
        Find white pixels in the image. If found pixel has white neighbourhood,
        its coordinates are returned, otherwise iteration continues
        until all white pixels are spotted.
        
        Current algorithm is rather ineffective. Main reason is that function
        has to exit if patch of white pixels is spotted. Then function is
        invoked again and iteration starts from beginning which is extremely
        ineffective. What should be done in such case?  Perhaps implementation
        should include iterator. The problem is that we need to change array
        while we iterate over this array.
        
        @rtype: (int, int)
        @return: (x, y) image coordinates of first spotted pixel that belongs
                 to patch (two or more adjecent pixeles) of white pixels;
                 if there is no such pixel, C{None}
        """
        # Access image pixel by pixel
        pix = self.__brainOutline.load()
        
        # Holds current pixel number
        pn=0
        
        # Iterate over all image
        for i in self.__brainOutline.getdata():
            pn+=1
            # If white pixel is spotted, check if it belongs to group of adjacent white pixels.
            # If it belongs, return coordinates of the pixel. If not, continue iteration.
            if i==255:
                x = pn % self.__brainOutline.size[0]-1
                y = pn //self.__brainOutline.size[0]
                #print "White pixel found at coords %d,%d" % (x,y)#,\
                #self.__brainOutline.size, pn
                if pix[x-1,y]==255 and pix[x+1,y]==255 and pix[x,y+1]==255 and pix[x,y-1]==255:
                    #self.__brainOutline.save("%d_%d.png"% (y,x), "PNG")
                    #return (x,y)
                    print (x,y)
                    yield (x,y)
        #return None
    #}
   
    #{ Auxiliary functions
    def __isOutsideBrainOutline(self, seedLabel): 
        """
        Determine if label is placed outside brain outline according to values
        of C{self.L{__brainOutline}}.

        @param seedLabel: L{barRegularLabel}
        @type  seedLabel: seed label
        
        @rtype: bool
        @return: C{True} if label is placed outside brain, C{False} otherwise
        """
        # Verify, if the seed is placed within brain contour. This procedure
        # assures that only correctly placed labels (=labels inside brain)
        # are traced.
        coords = self._toImageCoordinates(seedLabel.Location)
        if self.__brainOutline.getpixel(coords) == 0:
            _printRed("Seed points outside brain area: "+str(coords))
            self.__dumpWrongSeed(self.__brainOutline, seedLabel)
            return False
        return True
    
    def __isOverContour(self, im, seedLabel):
        """
        Determine if label is not placed over boundary.

        @type  im: PIL.Image.Image 
        @param im: image to verify seed label location
        
        @param seedLabel: L{barRegularLabel}
        @type  seedLabel: seed label
        
        @rtype:  bool
        @return: C{True} if label is not placed over contour, C{False} otherwise
        """
        coords = self._toImageCoordinates(seedLabel.Location)
        if im.getpixel(coords) == self._tracingConf['GrowDefaultBoundaryColor']:
            # You cannot fill starting from point which is not white
            self.__dumpWrongSeed(im, seedLabel)
            return False
        return True
    
    def _saveBitmap(self, im, filename):
        """
        Save provided image.

        @type  im: PIL.Image.Image 
        @param im: bitmap image to be saved
        
        @type  filename: str
        @param filename: name of the output file (only filename - without path;
                         provide .png extension)
        
        @todo: integrate _saveBitmap and _saveSVG into one function
        """
        OutputFilename = os.path.join(\
                self._tracingConf['DumpDirectory'], filename)
        im.save(OutputFilename)

    def _saveSVG(self, svgdom, filename):
        """
        Save provided SVG.

        @type  svgdom: xml.dom.minidom.Document 
        @param svgdom: SVG image to be saved
        
        @type  filename: str
        @param filename: name of the output file (only filename - without path;
                         provide .png extension)

        @todo: integrate _saveBitmap and _saveSVG into one function
        """
        OutputFilename = os.path.join(\
                self._tracingConf['DumpDirectory'], filename)
        f=open(filename,'w')
        #svgdom.writexml(f)
        svgdom.writexml(f, indent="\n", addindent="\n", newl="\n")
        f.close()
    
    def __getCoveredAreasList(self, seedLabel):
        """
        For images from C{self.L{__imageCache}} perform floodfilling with
        seed label.
        
        @type  seedLabel: L{barRegularLabel}
        @param seedLabel: seed label
        
        @rtype: ([PIL.Image.Image, ...], [int, ...])
        @return: pair of lists of floodfilled images and area of floodfill
                 in pixels (both lists have the same length and are
                 corresponding to some prefix of C{self.L{__imageCache}})
        """
        # List of calculated areas
        result=[]
        
        # Save information about areas covered in each grow step
        # This data is usefull when it comes to define some heuristics about
        # number of grows that gives best recoinstruction accuracy.
        result = map(lambda x:\
                self.__applyFill(x, seedLabel, retNPIX = True),\
                self.__imageCache)
        
        # Dump rebug information if required
        if __debug__: print\
                "Structure:\t"+ seedLabel.Caption +"\t"        +\
                "Coords:\t" + "\t" + str(seedLabel.Location) + "\t" +\
                "Area:\t"+"\t" + " ".join(map(str,result))
        # Area of traced region can be either of None. None occures when
        # floodfill was pointing at non-white pixel. In such case we need to
        # remove occurences of None from the list and then return it.
        if result.count(None):
            print result.index(None)
            result = result[0:result.index(None)]
        
        #TODO: refactoring with unzip...
        images, areas = map(lambda x: x[0], result), map(lambda x: x[1], result)
        return (images, areas)
    
    def __dumpWrongSeed(self, im, seedLabel):
        """
        Output warning message to stderr and dump invalid image into a file.
        
        @type  im: PIL.Image.Image 
        @param im: image to be dumped
        
        @param seedLabel: L{barRegularLabel}
        @type  seedLabel: seed label
        """
        # Transform SVG coordinates to rasterized image coordinates.
        goodCoords = self._toImageCoordinates(seedLabel.Location)
        
        # Print warning that seed points at pixel with incorrect values
        _printRed("\tTracing of area %s located at coordinates %d,%d "\
                % (seedLabel.Caption, goodCoords[0], goodCoords[1]))
        _printRed("\tis ommited because of non-white seed pixel value.")
        _printRed("\ttry aligning label or manualy set boundary growing level.\n")
        
        if not self._tracingConf['DumpWrongSeed']: return
        
        ImToFlood = im.copy()
        # Draw gray circle at debug image in order to mark area when error
        # occured
        draw = ImageDraw.Draw(ImToFlood)
        draw.ellipse((
                (goodCoords[0]-10, goodCoords[1]-10),\
                (goodCoords[0]+10, goodCoords[1]+10)
                )\
                , 60)
        del draw
        
        # Generate debug filename. Filename consists from following
        # information: slidenumber, boundary growing level, labelID adn seed
        # coordinates.
        tempDumpFilename=\
            str(self.slideNumber)+'_'\
            'debug_filled_'+seedLabel.Caption+\
            '_grow_'+str(seedLabel.growlevel)+\
            '_%d_%d.png' % goodCoords
        
        self._saveBitmap(ImToFlood, tempDumpFilename)
    #}

barObject._clsBoundingBox                 = barBoundingBox
barObject._clsPath                        = barPath
barObject._clsGenericStructure            = barGenericStructure
barObject._clsStructureLabel              = barStructureLabel
barObject._clsRegularLabel                = barRegularLabel
barObject._clsSpotLabel                   = barSpotLabel
barObject._clsCommentLabel                = barCommentLabel
barObject._clsMetadataElement             = barMetadataElement
barObject._clsBregmaMetadataElement       = barBregmaMetadataElement
barObject._clsTransfMatrixMetadataElement = barTransfMatrixMetadataElement

barCafSlide = barTracedSlideRenderer # Just an alias
barContourSlide = barPretracedSlideRenderer # Just an alias

#TODO: stupid! do something. Algorithms settings:
#BAR_TRACER_DEFAULT_SETTINGS['BestFillAlgorithm'] = selectBestGapFillingLevel

    
def _printRed(str):
    """
    Print given string to stderr using red color.

    @type  str: str
    @param str: string to be printed
    """
    print >>sys.stderr, '\033[0;31m%s\033[m' % str

def debugOutput(msg, error=False):
    """
    Print debug message to stderr. Error messages are printed in red colour.
    
    If the message is not an error message it is printed only if
    C{__debug__ == True}.
    
    @type msg: str
    @param msg: debug message
    
    @type error: bool
    @param error: indicates if the debug message is an error message
    """
    if error:
        _printRed(msg)
    elif __debug__:
        print >>sys.stderr, msg

def processMarkers(m1, m2, bm):
    """
    Calculate stereotectical coordinates transformation matrix and
    anterior-posterior coordinate of slide from given markers.
    
    @param m1: marker of slide position in coronal plane
    @type m1: L{barCoordinateMarker}
    
    @param m2: marker of slide position in coronal plane
    @type m2: L{barCoordinateMarker}
    
    @param bm: marker of anterior-posterior slide position
    @type bm: L{barCoronalMarker}
    
    @rtype: (L{_clsTransfMatrixMetadataElement}, L{_clsBregmaMetadataElement})
    @return: representation of metadata elements containing stereotectical
             coordinates transformation matrix and anterior-posterior
             coordinate of slide.
    """
    (x1, y1)   = m1.svgLocation
    (x2, y2)   = m2.svgLocation
    (x1p, y1p) = m1.spatialLocation
    (x2p, y2p) = m2.spatialLocation
    (z,)       = bm.spatialLocation
    
    (a,b,c,d,z) = slides_aligner.calculateTransfFromMarkers(\
            (x1, y1), (x2, y2), (x1p, y1p), (x2p, y2p), z)
    
    
    TransfMatrixMeta = barObject._clsTransfMatrixMetadataElement((a,b,c,d))
    CoronalCoordMeta = barObject._clsBregmaMetadataElement(z)
    return (TransfMatrixMeta, CoronalCoordMeta)
    
def validateStructureName(structureName):
    """
    @type  structureName: str
    @param structureName: name to be verified
    
    @rtype: str or bool
    @return: L{structureName} if structure name if correct, C{Flase} otherwise.

    @note: Name is validated only when debug mode is not disabled. It means that
    reconstruction modules can have disabled __debug__ mode while parsers should
    always run WITHOUT python -OO switch.
    """
    if not __debug__:
        return  structureName
     
    return (len(structureName) <= 40 # length is within proper range
        and not structureName.startswith("-") and not structureName.endswith("-") # no bordering hyphens
        and CONF_ALOWED_STRUCTURE_CHARACTERS.search(structureName) and structureName) # contains only legal characters

def cleanPotraceOutput(tracerOutput):
    """
    Create SVG document (with fixed paths) from provided PoTrace output.

    @type  tracerOutput: str
    @param tracerOutput: string produced by PoTrace
    
    @rtype: xml.dom.minidom.Document
    @return: SVG image fixed by the procedure.
    """
    svgdom = dom.parseString(tracerOutput)
    svgfix.fixSvgImage(svgdom, pagenumber=None, fixHeader=False)
    return svgdom

def CleanFilename(filename):
    """
    Strip filename from prohibited characters.
    Prohibited characters are replaced by underscore characted.
    
    @type  filename : str
    @param filename : filename to strip
    
    @return         : corrected filename
    @rtype: str
    """
    return filename.replace('/','_')

def flatten(x):
    """
    Create a flat sequence containing all elements retrieved from the sequence
    recursively contained sub-sequences (iterables).
    
    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    
    @type  x: sequence
    @param x: sequence to be flatted
    
    @return: created sequence
    @rtype: [?, ...]
    """
    
    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def _removeWhitespacesXML(domNode, unlink=True):
    """
    Remove unnecessary white spaces from given XML element.
    
    @param domNode: XML element
    @type domNode: xml.dom.minidom.Node

    @param unlink: indicates if memory allocated for unnecessary DOM nodes has
                   to be released immediately (has to be True when no cyclic
                   garbage colector is availiable)
    @type nlink: bool
    """
    emptyTextElements = []
    for child in domNode.childNodes:
        if child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
            _removeWhitespacesXML(child, unlink)
        elif child.nodeType == xml.dom.minidom.Node.TEXT_NODE:
            child.data = child.data.strip()
            if child.data == '':
                emptyTextElements.append(child)
    for child in emptyTextElements:
        domNode.removeChild(child)
        if unlink:
            child.unlink()
    
def _recurseTextNodeExtract(tspanElement):
    retval = ""
    for t in tspanElement.childNodes:
        if t.nodeType == t.TEXT_NODE:
            retval += strip(t.nodeValue)
        retval += strip(_recurseTextNodeExtract(t))
    return retval              

