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
@var  BAR_TRACER_DEFAULT_SETTINGS: all setting used by L{barPretracedSlideRenderer}
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
import cStringIO,  subprocess
from PIL import Image, ImageFilter, ImageChops, ImageOps, ImageDraw

import svgfix
from defaults import re_CoordinateMarker, re_CoronalCoord
from svgpathparse import parsePath,UnparsePath, extractBoundingBox,_mergeBoundingBox,\
                         modifyContour, parseStyle, formatStyle
import slides_aligner
import image_process

CONF_SVG_SLIDE_TEMPLATE="""
<svg baseProfile="full" height="900" id="body"
preserveAspectRatio="none"
version="1.1" 
viewBox="0 0 1200 900" width="1200"
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

BAR_XML_NAMESPACE = 'http://www.3dbar.org' 
BAR_XML_NAMESPACE_PREFIX    = 'bar:'
BAR_DEFAULT_GROWLEVEL      = 0
BAR_COORDINATE_MARKER_TEMPLATE = '(%f,%f)'
BAR_CORONAL_MARKER_TEMPLATE = 'Bregma:%f'
BAR_REGULAR_LABEL_PREFIX    = ''
BAR_COMMENT_LABEL_PREFIX    = ','
BAR_SPOT_LABEL_PREFIX       = '.'
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
    'stroke':'none',
    'positive':'True'}
CONF_DEFAULT_PATH_ATTRIBUTES_NS={'growlevel':0}

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

CONF_DEFAULT_RENDERER_SIZE =\
        (CONF_DEFAULT_RENDER_WIDTH, CONF_DEFAULT_RENDER_HEIGHT)

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
#BAR_TRACER_DEFAULT_SETTINGS['DumpDebugInformation']     = True
BAR_TRACER_DEFAULT_SETTINGS['DumpWrongSeed']            = True 
BAR_TRACER_DEFAULT_SETTINGS['DumpVBrain']               = False 
BAR_TRACER_DEFAULT_SETTINGS['DumpDirectory']            = '.'
BAR_TRACER_DEFAULT_SETTINGS['DetectUnlabelled']         = True
#BAR_TRACER_DEFAULT_SETTINGS['DetectIncorrectPlacement'] = True

# Basic configuration:
BAR_TRACER_DEFAULT_SETTINGS['CacheLevel']               = 5
BAR_TRACER_DEFAULT_SETTINGS['MinFiterTimesApplication'] = 3
BAR_TRACER_DEFAULT_SETTINGS['GrowDefaultBoundaryColor'] = 200
BAR_TRACER_DEFAULT_SETTINGS['RegionAlreadyTraced']      = 100
BAR_TRACER_DEFAULT_SETTINGS['UnlabelledTreshold']       = 500
BAR_TRACER_DEFAULT_SETTINGS['PoTraceConf'] = CONF_DEFAULT_POTRACE_PROPERTIES
BAR_TRACER_DEFAULT_SETTINGS['NewPathIdTemplate'] = 'structure%d_%s_%s'
#}

def getDictionaryFromFile(fileName, keyColumn=0, valueColumn=1):
    """
    @type fileName: str
    @param fileName: location of the file

    @type keyColumn: int
    @param keyColumn: number of column with keys

    @type valueColumn: int
    @param valueColumn: number of column with values

    @return A dictionary read from file fileName, where keys are stored in
            the column number keyColumn, and values in the column number
            valueColumn
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
    wto, 4 sty 2011, 15:08:58 CET: General element od 3D Brain Atlas
    Reconstructor. Element that holds any bar object. The general assumption is
    that every BAR element should have XML representation thus this class holds
    placeholdes for XML import / export methods but they are not always
    implemented in subclasses. Also all elements should have implementation of
    __str__ function but, again, some subclases do not have this function
    implemented.    
    
    This class have aslo some supplementary function as _getAttributesDict and
    getElementById which appears to be useful.
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
        Alias for getXMLelement().toxml()
        @return: XML string of given barAtlasSlideElement
        """
        return self.getXMLelement().toxml(encoding = BAR_XML_ENCODING)
    
    def getXMLelement(self):
        """
        Generates XML representation of given element.
        elements should be able to return their xml equivalent.
        
        @return: XML DOM object representing given object.
        """
        raise NotImplementedError, "Virtual method executed."
    
    def writeXMLtoFile(self, outputFilename):
        """
        Dumps given xml object to file with given filename.
        
        @type  outputFilename: string
        @param outputFilename: filename to save the file
        
        @return      : None
        """
        print outputFilename
        f=open(outputFilename,'w')
        self.getXMLelement().writexml(f,\
                indent="\t", addindent="\t", newl="\n",
                encoding=BAR_XML_ENCODING)
        f.close()
    
    @staticmethod
    def _getAttributesDict(xmlElement):
        """
        @type  xmlElement: DOM XML element
        @param xmlElement: svg from which all attributes will be extrated
        
        @return: Dictionary of extracted attributes and their values.
        
        Extracts attributes from given xmlElement and stores them in dictionary
        attrib:value. Please note that this is a static method and may be
        invoked from outside the class as well as instancing this class.
        """
        
        retDict = {}
        for (name, value) in xmlElement.attributes.items():
            retDict[name] = value
        
        return retDict
    
    def getElementById(self, domElement, tagName, id):
        """
        Stupid walkaround of faulty DOM getElementById. Do not use until there is
        not other way.
        """
        for element in domElement.getElementsByTagName(tagName):
            if element.hasAttribute('id') and element.getAttribute('id') == id:
                return element


class barAtlasSlideElement(barObject):
    """
    General class describing all elements that are part of slide. Ie. markers,
    paths, labels and metadata. Provides XML export and virtual XML import
    method.
    
    @type _attributes: dict
    @cvar _attributes: Dictionary of regular attribures. Keys are names of
                       attributes while values are... values of the attrubutes.
                       Regular attributes are exported without namespace prefix.
    
    @type _attributesNS: dict
    @cvar _attributesNS: Dictionary of namespace attributes. namespace
                         attributes are axported with C{BAR_XML_NAMESPACE_PREFIX}
                         prefix.
    @type _elementName: string
    @cvar _elementName: Name of the XML element.
    """
    # Attributes are divided into two parts: regular attribures and namespace
    # attributes. Regular attributes are exported without XML prefix, namespace
    # attributes are axported with C{BAR_XML_NAMESPACE_PREFIX} prefix. 
    
    _attributes = {}
    _attributesNS = {}
    _elementName = 'text'
    
    @classmethod
    def fromXML(self, sourceXMLElement):
        """
        Creates object from its (valid) xml representation. XML representation
        may be either string containing xml code or XML dom object. Ulimately
        all subclases should have implementation of this method, but currently
        implementation only for most important clases is completed.
        
        @type  sourceXMLElement: DOM XML or string containing xml
        @param sourceXMLElement: xml representation of the
                                 C{barAtlasSlideElement} basing on which object
                                 will be created.
        """
        raise NotImplementedError, "Virtual method executed."
    
    def getXMLelement(self, useBarNS = False):
        """
        @type  useBarNS: bool
        @param useBarNS: Determines, if element will use 3dBAR XML namespace.
        
        Generates XML DOM representation of given object.
        
        @rtype: XML DOM
        @return: XML DOM object representing given object.
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
        Generates XML DOM representation of given object. Used when given XML
        element has textnode child (ie. labels).
        
        @type  textNodeCaption: string
        @param textNodeCaption: Value of textnode
        
        @return: XML DOM object representing given object.
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
        @type  M: numpy 3x3 array
        @param M: transformation matrix
        
        Transforms whole element and its subelements using transformation matrix C{M}.
       
        @return: None
        """
        raise NotImplementedError, "Virtual method executed."
    
#-------------------------------------------------
# Labels
#-------------------------------------------------

class barStructureLabel(barAtlasSlideElement):
    """
    Class representing a generic label placed on slide (either pretraced or
    traced). This class should not be used itself but rather subclassed and
    customized (eg. L{barRegularLabel<barRegularLabel>},
    L{barSpotLabel<barSpotLabel>}, etc. as there three basic types of labels.
     
    @cvar _color: Color of label. In generic label color in undefined.
                  In sublasses colors as well as prefixes varies depending on
                  particular subclass.
    @type _color: string 
    
    @cvar _prefix: Prefix that is added when XML element is generated.
                   Prefix in generic labels is unassigned. In sublasses colors
                   as well as prefixes varies depending on particular subclass.
    @type _prefix: string
    """
    
    # Label types are distinguished by prefix and color thus generic label
    # has no particular color and prefix assigned.
    _color  = None
    _prefix = None
    _elementName = 'text'
    
    def __init__(self, labelLocation, labelCaption, labelID,
                       properties = None, growlevel = BAR_DEFAULT_GROWLEVEL):
        """
        @type  labelLocation: tuple of two integers
        @param labelLocation: point in which label will be anchored.
        
        @type  labelCaption: string
        @param labelCaption: text (name of the structure)
        
        @type  labelID: string
        @param labelID: Uniqe ID that will be assigned to this label
        
        @type  properties: dictionary
        @param properties: Dictionary with custom xml attributes which overrides
                           default text element settings. This argument should
                           be used when label is created from SVG element.
        """
        
        if properties:
            # if custom text element attributes are given use them:
            self._attributes = dict(properties)
        else:
            # Load default SVG properties from configuration file:
            self._attributes = dict(DEFAULT_TEXT_ELEMENTS_ATTRIBUTES)
        self._attributesNS = dict(CONF_DEFAULT_TEXT_ATTRIBUTES_NS)
        
        self.growlevel = growlevel
        #self._attributesNS['type'] = 'label'
        
        # Public
        self.Location = labelLocation 
        self.Caption  = self.__validateCaption(strip(labelCaption))
        self.ID = labelID
        
    @classmethod
    def fromXML(cls, svgTextElement):
        """
        @type  svgTextElement: XML DOM element
        @param svgTextElement: SVG element from which label will be created
        @return: New label created basing on provided XML element
        
        Creates barStructureLabel from given svg text element. Determines which
        type of label (regular, comment, spot) given text element describes and
        label object with the same type.
        
        @change:  pon, 11 paź 2010, 10:34:31 CEST, preserving font size of
                  input label
        """
        
        # Check if given element is text element:
        if not svgTextElement.tagName == 'text': 
            raise TypeError, "Invalid SVG element provided"
        
        # Extract all attributes from given element:
        propertiesDict =\
        cls._getAttributesDict(svgTextElement)
        
        # Extract label's coordinates, caption and id which will be used in
        # label's constructor.
        x, y = map(lambda x: float(propertiesDict[x]), ['x','y'])
        labelCaption = strip(svgTextElement.firstChild.nodeValue)
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
        Alias for C{castLabelType(sourceLabel, barCommentLabel)}.
        See L{castLabelType<castLabelType>} for more details.
        """
        return cls.castLabelType(sourceLabel, cls._clsCommentLabel)
    
    @classmethod
    def castToSpotLabel(cls, sourceLabel):
        """
        Alias for C{castLabelType(sourceLabel, barSpotLabel)}.
        See L{castLabelType<castLabelType>} for more details.
        """
        return cls.castLabelType(sourceLabel, cls._clsSpotLabel)
    
    @classmethod
    def castLabelType(cls, sourceLabel, targetLabelType):
        """
        Converts label type from one to another.
        
        @type  sourceLabel: barStructureLabel
        @param sourceLabel: Label that will be converted
        
        @type  targetLabelType: barStructureLabel
        @param targetLabelType: Type of the resulting label.
        
        @return: (barStructureLabel) label converted to now type.
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
    
    def __validateCaption(self, caption):
        if not validateStructureName(caption):
            raise ValueError, "Incorrect label caption: '%s'." % caption
        else: return caption
    
    #TODO: x, y should be float
    #TODO: add assertion
    def __getLocation(self):
        """
        @return: (x,y) Location of the label in SVG (slide) coordinates.
        """
        return tuple(map(lambda x: float(self._attributes[x]), ['x','y']))
    
    def __setLocation(self, newLocation):
        """
        @type  newLocation: tuple of two floats
        @param newLocation: (x,y) New location of the label
        
        @return: None
        """
        # Verify input data by mapping it into floats
        (x, y) = tuple(map(float, newLocation))
        self._attributes['x'] = str(x)
        self._attributes['y'] = str(y)
    
    def __affineTransform(self, M):
        self.Location = tuple(svgfix.transformPoint(self.Location, M))
        
    def affineTransform(self, M):
        return self.__affineTransform(M)
    
    def __getCaption(self):
        return self.__caption
    
    def __setCaption(self, newCaption):
        self.__caption = self.__validateCaption(newCaption)
    
    def __getID(self):
        return self._attributes['id']
    
    def __setID(self, newID):
        self._attributes['id'] = newID
    
    def __setGrowlevel(self, newGrowlevel):
        self._growlevel = int(newGrowlevel)
    
    def __getGrowlevel(self):
        return self._growlevel
    
    Location = property(__getLocation, __setLocation)
    Caption  = property(__getCaption,  __setCaption)
    ID       = property(__getID, __setID)
    growlevel= property(__getGrowlevel, __setGrowlevel)


class barRegularLabel(barStructureLabel):
    """
    Regular label is used to indicate area corresponding to ordinary brain
    structure.
    
    Regular label has no prefix and the fill color is #232323. This value is
    hardcoded as it is constant across all templates. 
    """
    _prefix = BAR_REGULAR_LABEL_PREFIX
    _color  = BAR_REGULAR_LABEL_COLOUR


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
    
    Comment labels are denoted by ',' (comma - comment) character as well as red
    font color.
    """
    _prefix = BAR_COMMENT_LABEL_PREFIX
    _color  = BAR_COMMENT_LABEL_COLOUR

#-------------------------------------------------
# Metadata elements
#-------------------------------------------------

class barMetadataElement(barAtlasSlideElement):
    """
    Class that describes generic metadata object and should be threaten as
    virtual class and not used as standalone class - only for subclassing
    """
    _elementName = 'data'
    
    def __init__(self, name, value):
        """
        @type  name: string
        @param name: Name of given metadata element
        
        @type  value: various, depends on subclass
        @param value: content of metadata
        
        @return: None
        """
        self._value = value
        self._name  = name
   
    @classmethod
    def fromXML(cls, svgMetadataElement):
        """        
        Creates metadata element from 3dBAR metadata element. Method determines
        which type of metadata is parsed and returns proper subclass of
        barMetadataElement.
        
        @type  svgMetadataElement: XML DOM element
        @param svgMetadataElement: SVG element from which barMetadataElement
                                   will be created
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
        Generates string representation of content of metadata. Such
        representation may by used in XML element as is required because
        metadata content may be not only string but also list, dictionary, etc.
        
        Default string represenataion is str() but, in general, it is overided
        by subclases.
        
        @return: (string) String representation of metadata content
        """
        return str(self._value)
    
    def _validateValue(self, NewValue):
        """
        Validates given value. Should be overriden and reimplemented in each
        subclass.
        """
        return True
    
    def _getValue(self):
        """
        Item getter for C{value} property.
        
        @return: content of metadata element
        """
        return self._value
    
    def _setValue(self, NewValue):
        """
        Item setter for C{value} property.
        Method validates new value and overrides old value when new value is
        valid
        """
        if self._validateValue(NewValue):
            self._value = NewValue
    
    def _getName(self):
        return self._name
    
    def getXMLelement(self):
        """
        @return: DOM object, SVG text element representing label in SVG
        document.
        """
        self._attributes['name']    = self._name
        self._attributes['content'] = self._getContentString()
        
        return barAtlasSlideElement.getXMLelement(self, useBarNS = True) 
    
    def getMetadataTuple(self):
        """
        Generates tuple that holds name and value of medatada object.
        
        @return: (tuple). Tuple of two values (name, value)
        """
        return (self._name, self._value)
    
    value = property(_getValue, _setValue)
    name  = property(_getName)
    

class barBregmaMetadataElement(barMetadataElement):
    """
    Holds bregma metadata element. Value of should be float.
    
    Obvilously, each slide may have only one BregmaMetadataElement otherwise
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
    Holds image to stereotectical coordinates transformation matrix as XML
    metadata.
    """
    def __init__(self, transformationMatrixTuple):
        """
        Transformation matrix coefficients (a, b, c, d)  that
        transforms image coordinate to stereotaxic (or other 'real') in
        following way: x'=a*x+b, y'=c*y+d.

        @type  transformationMatrixTuple: tuple or nested tuple
                                          (will be flatten anyway)
        @param transformationMatrixTuple: drawing to stereotaxic coordinate
                                          system transformation matrix.
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
    Markers are elements which allows to provide spatial coordinate system via
    graphical SVG element which can be easily done by various graphics
    software. Markers are recalculated into metadata elements by
    L{barPretracedSlide.parseMarkers<barPretracedSlide.parseMarkers>}. 
    """
    _elementName = 'text'
    
    def __init__(self, spatialLocation, svgLocation, properties = None):
        """
        @type  spatialLocation: tuple of two floats (x,y)
        @param spatialLocation: Location of the marker in spatial coordinate
                                system
        @type  svgLocation: tuple of two floats (x,y)
        @param svgLocation: Location of the markers in svg coordinate system.
        
        @type  properties: dictionary
        @param properties: additional dictionary of SVG attributes that will be
                           appended to the xml representation of the marker
                           (please renember that, in fact, marker is a text
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
    def fromXML(barMarker, svgTextElement):
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
        labelCaption       = svgTextElement.firstChild.nodeValue
        
        try:
            spatialCoordinates = map(float, re_CoordinateMarker.search(labelCaption).groups())
            return barCoordinateMarker(spatialCoordinates, (x,y))
        except AttributeError:
            pass
        
        try:
            spatialCoordinates = map(float, re_CoronalCoord.search(labelCaption).groups())
            return barCoronalMarker(spatialCoordinates, (x,y))
        except AttributeError:
            pass
    
    def getXMLelement(self, textNodeCaption = ""):
        # Put location (placement) of the marker
        # (expresed in SVG coordinate system)
        self._attributes['x'] = self._svgLocation[0]
        self._attributes['y'] = self._svgLocation[1]
#        self._attributes['id']= self._idAttrib
        return barAtlasSlideElement._getTextNodeXMLelement(\
                self, textNodeCaption)
    
    def _getSpatialLocation(self):
        return tuple(map(float, self._spatialLocation))
    
    def _setSpatialLocation(self, SpatialLocationTuple):
        self._spatialLocation = SpatialLocationTuple
    
    def _getSVGLocation(self):
        return tuple(map(float, self._svgLocation))
    
    def _setSVGLocation(self, SVGLocationTuple):
        self._svgLocation = SVGLocationTuple
    
    def __affineTransform(self, M):
        self.svgLocation = tuple(svgfix.transformPoint(self.svgLocation, M))
    
    def affineTransform(self, M):
        return self.affineTransform(M)
    
    spatialLocation = property(_getSpatialLocation, _setSpatialLocation)
    svgLocation     = property(_getSVGLocation, _setSVGLocation)


class barCoordinateMarker(barMarker):
    def getXMLelement(self):
        newTextNodeCaption =\
            BAR_COORDINATE_MARKER_TEMPLATE % tuple(self._spatialLocation)
        return super(self.__class__, self).getXMLelement(newTextNodeCaption)

    
class barCoronalMarker(barMarker):
    def getXMLelement(self):
        newTextNodeCaption =\
            BAR_CORONAL_MARKER_TEMPLATE % self._spatialLocation[0]
        return super(self.__class__, self).getXMLelement(newTextNodeCaption)

#-------------------------------------------------
# Paths and structures
#-------------------------------------------------

class barPath(barAtlasSlideElement):
    """
    Describes enclosed path denoting particular area in the slice. Note that
    'path' object does not mean 'structure' because structure may consist of
    many paths.
    """
    _elementName = 'path'
    
    def __init__(self, pathID, pathDefinition, fillColor, properties = None, clearPathDef = False):
        """
        @type  pathID: string
        @param pathID: id of the path element that will be stored as path id in XML
                   representation. Has to be valid path id.
        
        @type  pathDefinition: string
        @param pathDefinition: definition of the path. Has to be valid SVG path
                         definition
        
        @type  fillColor: string
        @param fillColor: color string in hexadecimal format. May begin with "#" char
                          or not
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
        # Extract id, definition and color from path
        pathDefinition = svgPathElement.getAttribute('d')
        pathID = svgPathElement.getAttribute('id')
        if clearPathDef:
            pathDefinition = cls.simplifyPathDef(pathDefinition)
        fillColor = svgPathElement.getAttribute('fill')
        
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
        return retPath
    
    @staticmethod
    def simplifyPathDef(pathDefinition):
        """
        @type  pathDefinition: DOM object
        @param pathDefinition: Path element which will be redefined
        @return: None
        
        Changes path 'd' attribute to absolute coordinates and eliminates all
        command shortcuts.
        """
        
        # Convert incompatible path format (relative coordinates, long curve segments)
        # to more legible format compatible with parser
        return  UnparsePath(parsePath(pathDefinition))
    
    def _getPathDefinition(self):
        """
        @return: SVG path definition attribute value
        """
        return self._attributes['d']
        
    def _setPathDefinition(self, newPathDefinition, clearPathDef = False):
        """
        @type  newPathDefinition: string
        @param newPathDefinition: SVG path definition attribute value
        
        Validates and sets new SVG path definition attribute value
        """
        if clearPathDef:
            if not self._validatePath(newPathDefinition):
                raise ValueError, "Invalid path definition provided"
            self._attributes['d'] = self.simplifyPathDef(newPathDefinition)
        else:
            self._attributes['d'] = newPathDefinition
        
    def _validatePath(self, pathDefinition):
        """
        @type  pathDefinition: string
        @param pathDefinition: SVG path definition to be validated.
        
        @return: (boolean) True, if path definition is correct, False otherwise 
        
        This method is supposed to do some basic valudation of given path. However,
        currently it does absolutely nothing and returns hardcoded True.
        """
        if len(parsePath(pathDefinition)) <= 3:
            print >>sys.stderr, "Invalid path detected: %s" % pathDefinition
            return False
        return True
        
    def _getGrowlevel(self):
        """
        @return: (int) growlevel property value.
        @todo: name attribute will be ultimately removed and replaced by
        bar:growlevel namespace attribute.
        """
        return self._attributesNS['growlevel']
    
    def _setGrowlevel(self, Growlevel = None):
        """
        Sets gap filling level for given path. Baceuse barBath class is used in
        already traced files, gap filling level describes with which gap filling
        level tracing was performed. So in such case it has only informative
        purpose.
        
        By default Growlevel is set to 0 which means that to erosion filter was
        applied.

        @type  Growlevel: int
        @param Growlevel: Level of gap filling that should be forced when
                           tracing is performed 
        """
        
        if not Growlevel:
            Growlevel = 0
        if int(Growlevel) >= -1 and int(Growlevel) <= 5:
            self._attributesNS['growlevel'] = Growlevel
        else:
            raise ValueError, "Given Growlevel is outside defined bounaries."
    
    def _validateID(self, ID):
        """
        @type  ID: string
        @param ID: SVG path 'id' attribute to be validated
        
        Validates given 'ID' of the path.
        
        The basic rule of valid 3dBAR path id is that it is list of values
        separated with '_' (underscore) character. First value has to be exactly
        'structure', second element is an actual uniqe id of the path while the last
        value is name of structure represented by particular path.
        
        Renember: NO SPACES please!
        
        Example of proper 3dBAR path id is 'structure_genetared-from-label-6_Olf'
        while wrong definition could be 'str_Olf_from label 87'
        
        @note: Method does not validate uniqness of given ID, only it's formal
               corectness.
        """
        valList = ID.split('_')
        #TODO: That should be: if not len(valList) == 3: return False
        if not len(valList) >= 3: return False
        if not valList[0].startswith('structure'): return False
        if not validateStructureName(valList[-1]): return False
        
        return True
    
    def _setID(self, newPathID):
        """
        @type  newPathID: string
        @param newPathID: New value of SVG path 'id' attribute

        Sets SVG 'id' attribute value. Id should be valid  3dBAR path id.
        """
        if self._validateID(newPathID):
            self._attributes['id'] = newPathID
        else:
            raise ValueError, "Invalid path ID: %s" % newPathID
    
    def _getID(self):
        """
        @return: (string) SVG 'id' attribute value.
        """
        return self._attributes['id']
    
    def _getPositive(self):
        """
        @return: (boolean)  Value of 'positive' property
        """
        return self._attributes['positive']
    
    def _setPositive(self, isPositive = True):
        """
        @type  isPositive: boolean
        @param isPositive: Determines if the positive property will be set to
                             True or false :)

        @note: Neither implemented properly nor tested :)

        Sets positive property. If set to true reconstructung given path will
        give "positive" volume otherwise this path will be substracted from the final
        volume. This paramater should be used to define "holes" in the tissue.
        """
        self._attributes['positive'] = isPositive
    
    def _getBbox(self):
        """
        @return: tuple of four integers: (x1,y1,x2,y2)
        
        Where x1,y2 are coordinates of top-left corner of bounding box and x2,y2 are
        coordinates of bottom-right corner of bounding box.

        Please note that bounding box is only approximation of actual bounding box
        and may be slightly larger as it is based on extreme coordinated of control
        points creating given path. However, the difference is neglectable.
        """
        return extractBoundingBox(self._attributes['d'])
    
    def _setBbox(self, newBBox):
        """
        Dummy setter that prevents overriding bbox property which is read only.
        Raises value error when invoked.

        @return: Raises ValueError
        """
        raise ValueError, "Bounding box is readonly property."
    
    def _getColor(self):
        """
        @return: (string) Fill color of path in hexadecimal represenataion
        """
        return self._attributes['fill']
    
    def _setColor(self, newColor):
        """
        Mtype  newColor: string
        @param newColor: color string in hexadecimal format. May begin with "#" char
                         or not
        @return: None
        
        Assigns color to path
        """
        if newColor[0] == "#": self._attributes['fill'] = newColor
        else: self._attributes['fill'] = "#" + newColor
    
    def _getCorrespondingStructureName(self):
        return self._getID().split('_')[-1]
    
    def _getCorrespondingLabelID(self):
        return self._getID().split('_')[-2]
    
    def _setCorrespondingLabelID(self, newID):
        raise ValueError, "Corresponding label ID is readonly property."
    
    def _rename(self, newStructName):
        newID     = self.id.split('_')
        newID[-1] = validateStructureName(newStructName)
        self._setID(join('_').join(newID))
        
    def __affineTransform(self, M):
        self.pathDef = svgfix.fixPathDefinition(self.pathDef,  M)
        
    def affineTransform(self, M):
        return self.__affineTransform(M)
    
    def __setCrispEdges(self, boolValue):
        if boolValue:
            self._attributes['shape-rendering'] = 'crispEdges'
        else:
            self._attributes['shape-rendering'] = 'geometric-precision'
    
    def __getCrispEdges(self):
        return self._attributes['shape-rendering']
        
    id         = property(_getID, _setID)
    positive   = property(_getPositive, _setPositive)
    growlevel  = property(_getGrowlevel, _setGrowlevel)
    pathDef    = property(_getPathDefinition, _setPathDefinition)
    boundingBox= property(_getBbox, _setBbox)
    bbx        = boundingBox
    color      = property(_getColor, _setColor)
    structName = property(_getCorrespondingStructureName, _rename)
    relLabelID = property(_getCorrespondingLabelID,_setCorrespondingLabelID)
    crispEdges = property(__getCrispEdges, __setCrispEdges)


class barGenericStructure(barAtlasSlideElement):
    def __init__(self, name, color, pathList = None):
        self._paths = {}
        self.name = name
        self._color = color
        
        if pathList:
            for path in pathList:
                self.addPaths(path)
    
    def __setitem__(self, key, value):
        self._paths[key] = value
        self._paths[key].color = self._color

    def __delitem__(self, key):
        del self[key]
        # Removes path with given key. If the path is the last path in the
        # structute, delete also the structure.
        if len(self) == 0: del self
    
    def __getitem__(self, key):
        return self._paths[key]
    
    def __str__(self):
        return "\n".join(map(str, self.values()))
    
    def __len__(self):
        return len(self._paths)
    
    def updatePaths(self):
        # Update color and name? Why to update name and color?
        # perhaps in should be split into separate functions?
        map(lambda path:  path._setColor(self.color), self.paths)
        map(lambda path:  path._rename(self.name), self.paths)
    
    def affineTransform(self, M):
        return map(lambda path: path.affineTransform(M), self.paths)
    
    def keys(self):
        return self._paths.keys()
    
    def items(self):
        return self._paths.items()
    
    def values(self):
        return self._paths.values()

    def itervalues(self):
        return self._paths.itervalues()

    def iterkeys(self):
        return self._paths.iterkeys()

    def iteritems(self):
        return self._paths.iteritems()
    
    def _getPaths(self):
        return self.values()
    
    def _getReverse(self):
        return True
    
    def _setReverse(self):
        pass
    
    def _setStructureName(self, name):
        self._name = validateStructureName(name)
        self.updatePaths()
    
    def _getStructureName(self):
        return self._name
    
    def _getStructureColor(self):
        return self._color
    
    def _setStructureColor(self, newColor):
        self._color = newColor
        self.updatePaths()
    
    def _getBbox(self):
        # Alias for merginig bounding boxes.
        return _mergeBoundingBox( map(lambda path: path.bbx, self.paths))
    
    def _setBbox(self, newBBox):
        """
        Dummy setter that prevents overriding bbox property which is read only.
        Raises value error when invoked.
        
        @return: Raises ValueError
        """
        raise ValueError, "Bounding box is readonly property."
    
    def getXMLelement(self):
        # Should return iterator
        for path in sorted(self.itervalues(), key=lambda x: x.id):
            yield path.getXMLelement()
   
    def addPaths(self, *args):
        for newPath in args:
            self.__setitem__(newPath.id, newPath)
            
    def __affineTransform(self, M):
        map(lambda x: x.affineTransform,  self.paths)
                
    def affineTrasnform(self, M):
        return self.__affineTransform(M)
    
    def __setCrispEdges(self, boolValue):
        map(lambda x: setattr(x, 'crispEdges', boolValue), self._paths.values())
    
    def __getCrispEdges(self):
        return all(map(lambda x: getattr(x, 'crispEdges'), self._paths.values()))
    
    name           = property(_getStructureName, _setStructureName)
    reversed       = property(_getReverse, _setReverse)
    color          = property(_getStructureColor, _setStructureColor)
    bbx            = property(_getBbox, _setBbox)
    paths          = property(_getPaths)
    crispEdges     = property(__getCrispEdges, __setCrispEdges)


class barBoundingBox(barObject):
    """
    Bounding box is a clever class that stores bounding box and implements
    simple operations that may be performed on bounding boxes such as
    extracting bounding box from SVG path definition, merging, printing etc.
    """
    def __init__(self, initialBoundaries = None):
        """
        @type  initialBoundaries: tuple
        @prarm initialBoundaries: tuple of four values holding initial bounding
                                  box.
        @return: None
        
        The C{initialBoundaries} tuple contains coordinates in following order
        (top, left, bottom, right).
        """
        if not initialBoundaries:
            self.boundaries = (None, None, None, None)
        else:
            self.boundaries = initialBoundaries
        pass
    
    @classmethod
    def fromPathDefinition(self, svgPathDefinition):
        """
        @type  svgPathDefinition: string
        @param svgPathDefinition: definition of path in SVG manner.
        
        @return: barBoundingBox object basing on SVG path definition
        
        Creates bounding box basing on SVG path definition.
        """
        return barBoundingBox(extractBoundingBox(svgPathDefinition))
    
    @classmethod
    def fromPathElement(self, svgPathElement):
        """
        @type  svgPathElement: DOM XML object 
        @param svgPathElement: SVG path object
        
        @return: barBoundingBox object basing on SVG path object.
        """
        barBoundingBox.fromPathDefinition(\
           svgPathElement.getAttribute('d'))
    
    def __merge(self, listOfBoundaries):
        """
        @type  listOfBoundaries: list of tuples
        @param listOfBoundaries: list of tuples that will be turned into one
                                 bounding boxes
        
        @return: tuple of four values holding merged boundaries
        """
        return _mergeBoundingBox(listOfBoundaries)

    def extend(self, extIterable):
        """
        @param extIterable: extension list
        @type  extIterable: iterable containing 4 numbers
        
        @rtype: C{None}
        @return: None
        
        Modifies bounding box boundaries by values in given iterable
        """
        b = np.array(self.boundaries)
        e = np.array(extIterable)
        self.boundaries = tuple(b+e)
    
    def __add__(self, obj):
        """
        Merges two bounding box objects into one.
        @return: barBoundingBox
        """
        merged = self.__merge((self.boundaries, obj.boundaries))
        return barBoundingBox(merged)
    
    def __iter__(self):
        return iter(self.boundaries)
   
    def __getitem__(self, index):
        return self.boundaries[index]
    
    def __mul__(self, number):
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
    C{barVectorSlide} is an abstract class representing all types of
    vector slides - slides that are based on SVG drawings.
    
    This class is an abstract class and should never be instanced.
    
    Slide template is empty SVG document which can be filled with labels,
    structures and metadata.
    
    @ivar slideTemplate: DOM object model holding slide template.
    
    @ivar _labels: Dictionary holding barGenericLabel instances. The keys are label's
    IDs
    
    @ivar _metadata: Dictionary holding metadata elements. Keys are names of particular
    metadata.
    
    @ivar slideNumber: Integer holding slide number.
    
    @change:  pią, 21 sty 2011, 12:25:01 CET, Implemented translating spatial
    coordinate into SVG coordinate and vice versa.
    """
    def __init__(self, slideTemplate = CONF_SVG_SLIDE_TEMPLATE, slideNumber = 0):
        self.slideTemplate    = slideTemplate
        
        self._labels           = {}
        self._metadata         = {}
        self.slideNumber = slideNumber
        self._setSlideTemplate(slideTemplate)
    
    def _getLabels(self):
        return self._labels.values()
    
    def _getMetadata(self):
        return self._metadata
    
    def _setMetadata(self, metadataElement):
        """
        @type  metadataElement: L{barMetadataElement<barMetadataElement>}
        @param metadataElement: metadata element to append.
        """
        self._metadata[metadataElement.name] = metadataElement
    
    def addLabel(self, newLabel):
        """
        @type  newLabel: L{barStructureLabel<barStructureLabel>}
        @param newLabel: Label to append into the slide
        
        Simply appends new label into the slide.
        """
        if not self._labels.has_key(newLabel.ID):
            self._labels[newLabel.ID] = newLabel
        else:
            #TODO: fixit
            #try:
            self._labels[newLabel.ID+'_'] = newLabel
            #except:
            #    print >>sys.stderr,\
            #    "Label with ID %s already in the slide! Skipping!\n" % (newLabel.ID,)
            #    raise KeyError
        
    #TODO: fix setter/getter type conflict
    def _getSlideTemplate(self):
        """
        Gets/Sets new slide template.
        
        @rtype: DOM object
        @return: Slide template
        """
        return self._slideTemplate
    
    def _setSlideTemplate(self, newSlideTemplate):
        """
        @type  newSlideTemplate: C{str}
        @param newSlideTemplate: Slide template to be used with given slide.
        
        @todo: Add slide validation before replacing the template.
        
        Gets/Sets new slide template.
        """
        if self._validateSlideTemplate(newSlideTemplate):
            self._slideTemplate = dom.parseString(newSlideTemplate)
    
    def _validateSlideTemplate(self, newSlideTemplate):
        #TODO: Add template validation.
        return True
    
    def alignToRefMatrix(self, refTuple, debugMode = False):
        """
        Transforms slide in the way that current transformation matrix will be
        equal to C{refTuple}. 
        
        Please note that scaling can be either positive and negative. When
        scaling is positive it means that stereotaxic axis has the same
        direction as image axis. When scaling is negative stereotaxic and image
        axes are oriented in opposite directions. Be very careful in such case.
        
        Workflow:
        
            1. Get initial transformation matrix from metadata,
            2. Calculate corrections basing on initial transformation matrix and
               reference matrix.
            3. Embed corrections as SVG transformation and put corrected
               transformation matrix as 3dBAR metedata
        
        @type  refTuple: tuple of 4 floats (sxref, xref, syref, yref)
        @param refTuple: Reference tuple for aligning.
        """
        
        currentTranfTuple = tuple(self._metadata[BAR_TRAMAT_METADATA_TAGNAME].value)
        (tranfMatrix, status) = slides_aligner.makeAlignment(refTuple, currentTranfTuple)
        
        # Status tells if given transformation should be applied:
        # yes, if it is non-identity transformation, no otherwise as we don't
        # want to waste time for multiplying all points by 1.
        if status:
            self.affineTransform(tranfMatrix)
            self._metadata[BAR_TRAMAT_METADATA_TAGNAME].value = refTuple
    
    def Show(self, binFile = 'eog',  tempFilename = "/tmp/barTemp.svg"):
        """
        @type  binFile: string
        @param binFile: name of the executable file that will be used instead of
                        detault SVG browser.
        
        @type  tempFilename: string
        @param tempFilename: Temporary file name used to store svg slide
        
        Displays slide in external SVG browser. Name of executable file may be
        customized using C{binFile}.
        """
        self.writeXMLtoFile(tempFilename)
        os.system(binFile + " " + tempFilename) 
     
    def getLabelByName(self, labelCaption, labelType = None, oType = 'id'):
        """
        @type  labelCaption: string
        @param labelCaption: obligatory argument holding caption of the label
        
        @type  labelType: class
        @param labelType: name of the label class type

        @type  oType: C{string}
        @param oType: When set to 'id' IDs of selected labels are returned, if
                      'ref' references are returned
        
        @return: list of label's IDs or references
        
        Returns list of IDs of labels matching searching criteria which are:
        caprion of the label and its type.
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
        for labelID in self.getLabelByName(labelCaption):
            self._labels[labelID] = self._clsStructureLabel.castLabelType(
                                self._labels[labelID], targetType)
    
    def deleteLabelByCaption(self, labelCaption):
        for labelID in self.getLabelByName(labelCaption):
            del self._labels[labelID]
       
    def deleteLabelByID(self, labelID):
        del self._labels[labelID]
    
    def renameLabelByCaption(self, oldCaption, newCaption):
        for labelID in self.getLabelByName(oldCaption):
            self._labels[labelID].Caption = newCaption
    
    def __getAllLabelsWithType(self, labelType):
        return [ label for label in self.labels if
                label.__class__.__name__ == labelType.__name__ ]
    
    def __affineTransform(self, M):
        map(lambda x: x.affineTransform(M),  self.labels)
    
    def affineTransform(self, M):
        self.__affineTransform(M)
        return self
    
    def __validateMetadata(self):
        """
        Checks if all metadata elements are provided.
        """
        try:
            temp = self._metadata[BAR_TRAMAT_METADATA_TAGNAME]
            temp = self._metadata[BAR_BREGMA_METADATA_TAGNAME]
        except KeyError:
            raise KeyError, "Metadata not provided. Cannot continue."
    
    def toSpatialCoordinate(self, svgCoord, ndims = 2):
        """
        @type  svgCoord: C{(float, float)}
        @param svgCoord: Coordinates in svg coordinate system to be converted
        into spatial coordinates.

        @type  ndims: C{int}
        @param ndims: Number of dimensions of returned value. Determines if
        output value will be 2 or 3 dimensional. When C{ndims=3} point is
        extended with coronal coordinate.

        @rtype: C{(float,...)}
        @return: Spatial coordinates corresponding to given svg coordinates.

        @requires: All metadata has to be provided and should be correct.
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
    
    def toSVGcoordinate(self, spatialCoord):
        """
        @type  spatialCoord: C{(float, float)}
        @param spatialCoord: Spatial coorrdinate to be converted into SVG
        coordinate.
        
        @rtype:  C{(float, float)}
        @return: Spatial coordinates corresponding to provided SVG coordinates.
        
        @requires: All metadata has to be provided and should be correct.
        """
        # Check metadata availability
        self.__validateMetadata()
        
        (a, b, c, d) = self._metadata[BAR_TRAMAT_METADATA_TAGNAME].value
        (xp, yp) = spatialCoord
        
        return ( (xp-b)/a, (yp-d)/c )
    
    def getCommentLabels(self):
        return self.__getAllLabelsWithType(self._clsCommentLabel)
    
    def getRegularLabels(self):
        return self.__getAllLabelsWithType(self._clsRegularLabel)
    
    def getSpotLabels(self):
        return self.__getAllLabelsWithType(self._clsSpotLabel)
    
    def _generateLabelIndex(self):
        """
        Generates dictionary of all paths from all strcutures. Keys are path IDs
        while values of dictionary are paths.
        
        @return: Dictionary C{d[label.id]=label}
        """
        labelIndexByID = dict(map(lambda lab: (lab.ID, lab), self.labels))
        return labelIndexByID

    @staticmethod
    def calculateTransfFromMarkers((x1, y1), (x2, y2), (x1p, y1p), (x2p, y2p), z):
        return slides_aligner.calculateTransfFromMarkers(\
                (x1, y1), (x2, y2), (x1p, y1p), (x2p, y2p), z)
    
    slideTemplate=property(_getSlideTemplate, _setSlideTemplate) 
    labels      = property(_getLabels)
    labelIndex  = property(_generateLabelIndex)
    metadata    = property(_getMetadata, _setMetadata)


class barSlideRenderer(barVectorSlide):
    """
    Class holding all operation related to rasterizing SVG slides. It allows
    rasteizing whole slide, particular structures (by their names), or paths
    with given ID or belonging to particular structures.

    Class has to be supplied with various parameters described better in class
    constructor. All rendered images are provided in form of PIL images.
    """

    def __init__(self, vectorSlide, rendererConfiguration, tracingConfiguration,
            slideNumber =0, debugMode = False):
        """
        @param rendererConfiguration: Dictionary rendering properties.
        @type  rendererConfiguration: dict

        @type  debugMode: boolean
        @param debugMode: Verbose mode on/off.

        Class requires providing following properties in order to work properly:
        rendererConfiguration['ReferenceWidth'] - Hold width of svg drawing
        (int).

        rendererConfiguration['ReferenceHeight'] - Integer holding height of svg
        drawing.

        rendererConfiguration['imageSize'] - tuple of integers (w,h) holding
        size of resulting bitmap image.
        """
        # Just for clarity - set it at the begining
        self._debugMode = debugMode
        
        # Save rendering and tracing properties
        self._rendererConf = rendererConfiguration 
        self._tracingConf = tracingConfiguration
        
        # Copy slide's data from provided vector slide info this instnace
        # (and hope that actual data will be copied, not only references ;)
        
        self._metadata         = vectorSlide._metadata
        self._labels           = vectorSlide._labels
        self._slideTemplate    = vectorSlide._slideTemplate
        self.slideNumber       = vectorSlide.slideNumber
    
    def renderSlide(self,  otype = 'pil'):
        """
        @return: (PIL image) Image of whole slide

        Renders whole slide with all paths and labels. Original path
        colors are preserved but whole image is in grayscale.
        """
        return self._renderSvgDrawing(self.getXMLelement(), otype=otype)
    
    def _toSVGCoordinates(self, ImageCoords):
        """
        @type  ImageCoords: tuple of two integers
        @param ImageCoords: Image coordinates to transform
        
        @return: tuple of two floats: (x,y)
        
        Transforms coordinates given in pixels (in image coordinate system) to
        coordinates in SVG drawing coordinate system (not stereotaxic coordinate
        system).
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
    
    def __setCrispEdges(self, boolValue):
        map(lambda x: setattr(x, 'crispEdges', boolValue), self.values())
    
    def __getCrispEdges(self):
        return all(map(lambda x:getattr(x, 'crispEdges'), self.values()))
    
    def _toImageCoordinates(self, svgCoords):
        """
        Converts coordinates from SVG image to coordinates in raster image system.
        By default, SVG drawings are rendered with 90 dpi resolution.
        In this resolution one point in SVG drawing is equivalent to one pixel of
        raster image. When SVG is rendered in larger resolution (we do not
        consider  smaller resolutions in this software), coordinates has to be
        rescaled. Returned values are rounded to integers.

        @type  svgCoords: tuple of two integers
        @param svgCoords: Coordinates in SVG drawing coordinates system.

        @return: (tuple of two integers) Image coordinates corresponding provided
                 svg coordinates.
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
    
    def _renderSvgDrawing(self, svgdoc, renderingSize=None, boundingBox=None, otype='pil', grayscale=True):
        """
        @type  svgdoc: DOM object
        @param svgdoc: SVG document to render
        
        @type  renderingSize: (int, int)
        @param renderingSize: Dimensions (in pixels) of the rendered image,
                              before an optional cropping.
        
        @type  boundingBox: (l,t,r,b)
        @param boundingBox: tuple of integers with cropping coordinates. Applies
                            only to 'rec' protocol.
        
        @type  otype: C{str}
        @param otype: Defines rendering protocol. May be: pil, npy, rec. pil
                      returns PIL Image with rendered image, 'npy' - numpy
                      array while 'rec' return also numpy array but processes
                      according to reconstruction module requirements.
        
        @type  grayscale: C{Bool}
        @param grayscale: Determines if returned image would be in grayscale
                          or RGB mode. Applies only to 'pil' protocol.
        
        Renders provided SVG image with varioous options and returns rendered
        image.
        
        Workflow:
            1. Render image and convert it to NumPy array
            2. Manipulate channels and colours, convert to indexed mode
            3. Create and return PIL image
        
        @todo: Consider rewriting this method to staticmethod
        
        @rtype: C{PIL image | np.array}
        @return: PIL image, or numpy array containing rendered SVG file.
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
        #if self._debugMode: surface.write_to_png ('debugfilename.png')
        
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
        if otype == 'rec':
            # Convert bitmap to grayscale
            image = Image.fromarray(a.astype(np.uint8),'RGBA').convert("L")
            
            # Crop region of interest:
            print boundingBox
            image = image.crop(tuple(map(int,boundingBox)))
            
            # By default reverse image to make background black and foreground
            # white:
            image = ImageChops.invert(image)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            volumeSlice = np.array(image.getdata()).reshape(int(image.size[0]), int(image.size[1]), 1)
            return volumeSlice
    
    crispEdges     = property(__getCrispEdges, __setCrispEdges)


class barPretracedSlide(barSlideRenderer):
    def __init__(self,\
            slideTemplate = CONF_SVG_SLIDE_TEMPLATE,\
            rendererConfiguration = CONF_DEFAULT_RENDERING_PROPS,\
            tracingConfiguration  = BAR_TRACER_DEFAULT_SETTINGS,\
            slideNumber = 0):
        """
        @type  slideTemplate: string
        @param slideTemplate: XML string containing slide template
        
        @type  slideNumber: int
        @param slideNumber: Number of slide
        """
        barSlideRenderer.__init__(self,\
                barVectorSlide(slideTemplate, slideNumber),\
                rendererConfiguration = rendererConfiguration,\
                tracingConfiguration  = tracingConfiguration,\
                slideNumber = slideNumber,\
                debugMode = True)
        
        self._svgPaths=[]
        self.markers =[]
    
    def __setitem__(self, key, newLabel):
        self._labels[newLabel.ID] = newLabel
    
    def __getitem__(self, key):
        return self._labels[key]
    
    def __delitem__(self, key):
        del self._labels[key]
    
    @classmethod
    def fromXML(cls, svgDocument):
        
        # Initialize empty slide with dummy tracing and rendering configuration,
        # slide number empty
        slide = cls()
        
        # Parse source SVG file if it is string, leave it otherwise
        if not svgDocument.__class__.__name__ == 'Document':
            svgdom = dom.parse(svgDocument)
        else:
            svgdom = svgDocument
        svgElement = svgdom.getElementsByTagName('svg')[0]
        # In case, when 3dBAR namespace is not defined, we declare it.
        svgElement.setAttribute('xmlns:bar', BAR_XML_NAMESPACE)
        
        # Information about stereotectic coordinate system may be presented in
        # form of markers or as metadata elements. Markers elements has priority
        # over metadata elements. If found, markers are processed first.
        
        # Get metadata element and extract all metadata
        # then iterate over all metadata elements and extract values.
        # If there is no metadata elements defined, the loop will not execute.
        metadataDataset =\
                svgdom.getElementsByTagName(BAR_DATA_LOCATION_ELEMENT)[0]
        
        for metadataEntry in metadataDataset.childNodes:
            try:
                metadata = cls._clsMetadataElement.fromXML(metadataEntry)
                slide._setMetadata(metadata)
            except:
                pass
        
        # Then extract all text elements and separate them between labels 
        # and markers. Labels are parsed at first as they are more probable
        for labelElement in svgdom.getElementsByTagName('text'):
            try:
                label = cls._clsStructureLabel.fromXML(labelElement)
                slide.addLabel(label)
            except:
                marker = barMarker.fromXML(labelElement)
                slide.markers.append(marker)
        
        for pathElement in svgdom.getElementsByTagName('path'):
            slide._svgPaths.append(pathElement)
        
        # remove all paths, labels, etc. leaving slide template
        for element in ['text', 'path','bar:data']:
            for elementToDelete in svgdom.getElementsByTagName(element):
                elementToDelete.parentNode.removeChild(elementToDelete)
         
        # Use extracted metadata elements to define tracing and rendering
        # properties:
        # TODO: Handle try/except with better way
        try:
            slide._tracingConf  = eval(slide._metadata['tracingConf'].value)
            slide._rendererConf = eval(slide._metadata['rendererConf'].value)
        except:
            pass
        
        slide._setSlideTemplate(svgdom.toxml())
        
        return slide
    
    def __processMarkers(self, m1, m2, bm):
        """
        """
        # TODO: add assertion
        (x1, y1)   = m1.svgLocation
        (x2, y2)   = m2.svgLocation
        (x1p, y1p) = m1.spatialLocation
        (x2p, y2p) = m2.spatialLocation
        (z,)       = bm.spatialLocation
        
        (a,b,c,d,z) = self.calculateTransfFromMarkers(
                (x1, y1), (x2, y2), (x1p, y1p), (x2p, y2p), z)
        
        TransfMatrixMeta = self._clsTransfMatrixMetadataElement((a,b,c,d))
        CoronalCoordMeta = self._clsBregmaMetadataElement(z)
        return (TransfMatrixMeta, CoronalCoordMeta)
    
    def affineTransform(self, M):
        self.__affineTransform(M)
        return self
    
    def __affineTransform(self, M):
        barVectorSlide.affineTransform(self, M)
        map(lambda x: x.affineTransform(M),  self.markers)
        for pathElem in self._svgPaths:
            pathElem.setAttribute('d',\
                    svgfix.fixPathDefinition(pathElem.getAttribute('d'),  M))
   
    def parseMarkers(self):
        m1 =[ m for m in self.markers if m.__class__ == barCoordinateMarker][0]
        m2 =[ m for m in self.markers if m.__class__ == barCoordinateMarker][1]
        bm =[ m for m in self.markers if m.__class__ == barCoronalMarker][0]
        map(self._setMetadata, self.__processMarkers(m1, m2, bm))
        self.markers = []
     
    def getXMLelement(self):
        """
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
        svgGroupDataset = slide.getElementsByTagName('g')[0]
        if svgGroupDataset.hasAttribute('xml:space'):
            svgGroupDataset.removeAttribute('xml:space')
        
        for metadataElement in self._metadata.values():
            metadataDataset.appendChild(metadataElement.getXMLelement())
        
        for pathElement in self._svgPaths:
            svgGroupDataset.appendChild(pathElement)
        
        for labelElement in self.labels:
            svgGroupDataset.appendChild(labelElement.getXMLelement())
        
        for markerElement in self.markers:
            svgGroupDataset.appendChild(markerElement.getXMLelement())
        
        # Redefine path definitions using absolute coordinates
        # svgfix.fixSvgImage(slide, pagenumber=self.slideNumber, fixHeader=True)
        return slide
    
    def modifyContours(self, newStrokeWidth = None, newStrokeColour = None):
        """
        @type  newStrokeWidth: float
        @param newStrokeWidth: New width of contour that will replace existing
                               contour width
        
        @param newStrokeColour: New colour of the contoru that will replace
                                existing colours of the path
        @type  newStrokeColour: colour string (#xxxxxx)
        
        @return: None
        
        Function that modifies width and colours of the contours.
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
    def __init__(self,\
            slideTemplate = CONF_SVG_SLIDE_TEMPLATE,\
            rendererConfiguration = CONF_DEFAULT_RENDERING_PROPS,\
            tracingConfiguration  = BAR_TRACER_DEFAULT_SETTINGS,\
            slideNumber = 0,\
            debugMode = False):
        
        barSlideRenderer.__init__(self,\
                barVectorSlide(slideTemplate, slideNumber),\
                rendererConfiguration = rendererConfiguration,\
                tracingConfiguration  = tracingConfiguration,\
                slideNumber = slideNumber,\
                debugMode = False)
        
        self._structures      = {}
   
    @classmethod
    def fromXML(cls, svgDocument, fixDrawing = False):
        # Initialize empty slide
        slide = cls()
        
        # Parse source SVG file if it is string, leave it otherwise
        #if not svgDocument.__class__.__name__ == 'Document':
        svgdom = dom.parse(svgDocument)
        _removeWhitespacesXML(svgdom)
        
        # Redefine path definitions using absolute coordinates
        if fixDrawing:
            svgfix.fixSvgImage(svgdom, pagenumber=0, fixHeader=False)
        
        svgElement = svgdom.getElementsByTagName('svg')[0]
        
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
        
        # Then extract all labels
        for labelElement in svgdom.getElementsByTagName('text'):
            try:
                label = cls._clsStructureLabel.fromXML(labelElement)
                slide.addLabel(label)
            except ValueError:
                _printRed("Error while reading labels: %s\nSkipping." %\
                        (labelElement.toxml(),))
        
        # remove all paths, labels, etc. leaving slide template
        for element in ['text', 'path','bar:data']:
            for elementToDelete in svgdom.getElementsByTagName(element):
                elementToDelete.parentNode.removeChild(elementToDelete)
        
        # Use extracted metadata elements to define tracing and rendering
        # properties:
        try:
            slide._tracingConf  = eval(slide._metadata['tracingConf'].value)
            slide._rendererConf = eval(slide._metadata['rendererConf'].value)
        except:
            pass
       
        slide._setSlideTemplate(svgdom.toxml())
        return slide
    
    def __setitem__(self, key, newStructure):
        self._structures[key] = newStructure
    
    def __getitem__(self, key):
        return self._structures[key]
   
    def __delitem__(self, key):
        """
        @type  key: string
        @param key: name of the L{barGenericStructure<barGenericStructure>}
        
        Removes structure detoted by provided structure name. All paths
        corresponding to given structure are removed. Also path with id
        corresponding to given structure is also removed.
        
        @return: None
        """
        for path in self._structures[key].paths:
            del self._labels[path.relLabelID]
        del self._structures[key]
    
    def keys(self):
        return self._structures.keys()
    
    def items(self):
        return self._structures.items()
    
    def values(self):
        return self._structures.values()
    
    def __len__(self):
        return len(self._structures)
    
    def __add__(self, op):
        """
        Defines operation of adding two slides.
        
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
        if key in self._structures: return True
        else: return False
    
    def __addPath(self, newPath):
        """
        @type  newPath: L{barPath<barPath>}
        @param newPath: Path to append into the slide
        
        Appends path to the slide. Note that slide element does not contain barPath
        elements directly. Paths are holded in structure elements so paths are
        added to the structures not to the slide directly.
        
        If structure corresponding to appended path exists, path is appeneded to
        the structure. Otherwise new structure holding appended path is created.
        This is possible as path element holds name of the structure which he
        belongs to.
        
        @return: None
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
        Alias of L{__addPath(newPathElement)<__addPath>}
        """
        return self.__addPath(newPathElement)
    
    def __generatePathIndex(self):
        """
        Generates dictionary of all paths from all strcutures. Keys are path IDs
        while values of dictionary are paths.
        
        @return: Dictionary C{d[pathEl.id]=pathEl}
        """
        pathIndexByID = {}
        for structureElement in self.structures:
            map(lambda pathEl: pathIndexByID.__setitem__(pathEl.id, pathEl), 
                          structureElement.paths)
        return pathIndexByID
    
    def _getPaths(self):
        """
        Alias for L{__generatePathIndex().values()<__generatePathIndex()>}
        @return: List of all path objects.
        """
        return self.__generatePathIndex().values()
    
    def _getStructures(self):
        """
        Returns list of all structures in the slide.
        @rtype: list
        @return: List of all structures.
        """
        return self.values()
    
    def addStructures(self, *args):
        """
        Appends provided list of structures to the slide. Existing structures
        will be overwritten with new structures with the same name.

        @type  args: list
        @param args: list of structues (L{barGenericStructure<barGenericStructure>})
        """
        for newStructure in args:
            self.__setitem__(newStructure.name, newStructure)
    
    def getXMLelement(self):
        # Save tracing and rendering properties as metadata entries:
        self._setMetadata(\
                self._clsMetadataElement('tracingConf', repr(self._tracingConf)))
        self._setMetadata(\
                self._clsMetadataElement('rendererConf', repr(self._rendererConf)))
        
        slide = self._getSlideTemplate().cloneNode(True)
        
        svgElement = slide.getElementsByTagName('svg')[0]
        metadataDataset =\
                slide.getElementsByTagName(BAR_DATA_LOCATION_ELEMENT)[0]
        svgGroupDataset = slide.getElementsByTagName('g')[0]
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
        
        #TODO: order of elements!!!
        for structureElement in self._structures.values():
            if not structureElement.name == 'vBrain':
                for pathElement in structureElement.getXMLelement():
                    svgGroupDataset.appendChild(pathElement)
        
        for labelElement in self.labels:
            svgGroupDataset.appendChild(labelElement.getXMLelement())
        
        # Redefine path definitions using absolute coordinates
        # svgfix.fixSvgImage(slide, pagenumber=self.slideNumber, fixHeader=True)
        return slide
    
    def recolor(self, colorMapping):
        for structure in self.structures:
            try:
                structure.color = colorMapping[structure.name]
            except:
                pass
        #map(lambda str: str.__setattr__('color', colorMapping[str.name]) ,self.structures)
        return self
    
    def affineTransform(self, M):
        self.__affineTransform(M)
        return self
    
    def __affineTransform(self, M):
        barVectorSlide.affineTransform(self, M)
        map(lambda x: x.affineTransform(M),  self.paths)
    
    def findDuplicatedRegions(self, Options = None, Apply = True):
        """
        Function for post processing of traced files. At this moment, has
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
        
        @type  Options: Dictionary
        @param Options: Dictionary holding processing options, currently
                        placeholder for further processing options
        
        @type  Apply: boolean
        @param Apply: Value which determines if slide will be processed or not.
                      When set to True, paths will be removed and labels will be
                      changed. Otherwise, slide will not be processed, only
                      duplicated areas are found and returned.
        
        @todo: Implement processing options 
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
        Processes paths and labels in following way:
            - Remove paths that should be removed
            - Change type of corresponding label to SpotLabel
        
        @type  listOfChanges: dict
        @param listOfChanges: List of id's if paths that should be preserved and
                              those that should be removed.
        
        @type  Options: Dictionary
        @param Options: Dictionary holding processing options, currently
                        placeholder for further processing options
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
    
    paths       = property(_getPaths)
    pathIndex   = property(__generatePathIndex)
    structures  = property(_getStructures)
    svgDocument = property(getXMLelement)


class barTracedSlideRenderer(barTracedSlide):
    def __generateLabelLocation(self, path):
        """
        @type  path: barPath
        @param path: path for which best label location will be determined.
        
        @rtype: C{(float x, float y)}
        @return: Optimal coordinates of the label provided in SVG coords.
        
        Generates best label localtion for givent barBath object. The optimal
        position of the label is determined using maximum value of distance
        transform.
        """
        #print path
        slideRendering = self.renderPath(path)
        (x,y) = image_process.getBestLabelLocation(slideRendering)
        (x,y) = self._toSVGCoordinates((x,y))
        return (x,y)
    
    def getSlideMassCenter(self):
        """
        @rtype: C{(float x, float y)}
        @return: Return coordinates of the mass center for given slide. Mass
        center is calculated basing on grayscale slide representation.
        
        @change: corrected buggy mass centre calculations
        """
        imgMassCentre = image_process.massCentre(self.renderSlide())
        return self._toSVGCoordinates(imgMassCentre)
    
    def getMask(self, maskColor ='#000000'):
        map(lambda x: setattr(x, 'color', maskColor), self.structures)
        return self 
        
    def generateLabels(self, skipLabels = []):
        """
        @type  skipLabels: List of strings
        @param skipLabels: Lablels for those structures will be skipped.
        
        Function assigns text label for each path in given slide and places it in
        center (according to maximal value of distance transform) of the path.
        
        All existing regular labels are erased while comment labels and spot
        labels remains.
        
        @rtype: L{barTracedSlide<barTracedSlide>}
        @return: Slide with regular labels generated for each barPath in given
        slide
        """
        # Clone existing slide and clear all regular labels.
        # Do not delete other types of labels
        toRemoveID = [l.ID for l in self.labels if l.__class__ == self._clsRegularLabel]
        map(lambda y: self._labels.__delitem__(y), toRemoveID)
        
        # Get path index from original slide
        pathIndex = self.pathIndex
        
        # Iterate over all paths and generating new regular label for each
        # path
        #for (pathNo, pathID) in enumerate(pathIndex.keys()): 
        for path in pathIndex.values():
            newLabelID      = path.relLabelID 
            newLabelCaption = path.structName 
            
            # Skip processing this label if requested
            if newLabelCaption in skipLabels: continue
            try:
                newLabelCoords = self.__generateLabelLocation(path)
                # Generate new label and append it into the slide
                newLabel = self._clsRegularLabel(newLabelCoords, newLabelCaption, newLabelID)
                self.addLabel(newLabel)
            except:
                pass
        
        return self
    
    def renderStructureList(self, structureNameList):
        """
        @type  structureNameList: list of strings
        @param structureNameList: List of structures abbrevations that will be
                                  rendered. Note that structure with given name
                                  must exist, otherwise exception will be
                                  raised.
        
        @rtype: C{PIL image}
        @return: Image with rendered structure
        
        Generates image of selected structure. Structure has to be defined in
        the slide or blank white image will be returned. Structures are
        recognized by names of barStructure 
        
        Workflow:
            1. Get empty slide using template from existing slide.
            2. Copy desired structures into new slide leaving other structurees
            3. Render temporary slide and return generated image.
        """
        tempSlide = self.getStructuresSubset(structureNameList)
        
        # Render temporary slide and return the results
        return self._renderSvgDrawing(tempSlide.getXMLelement())
    
    def getStructuresSubset(self, structureNameList):
        """
        Returns slide containing only structures from privided list
        """
        
        # Create temporary slide
        tempSlide = self.__class__(\
                self.slideTemplate.toxml(),
                self.slideNumber)
        
        # Copy structures that we want to render into new slide
        slideStructNames = map(lambda x: getattr(x,'name'), self.values())
        existingStructures = list(set(structureNameList) & set(slideStructNames))
        for structureName in existingStructures:
            tempSlide[structureName] = self[structureName]
        
        return tempSlide
    
    def renderPath(self, pathObject):
        """
        @type  pathObject: barPath
        @param pathObject: path element that will be rendered
        
        @rtype: L{barPath<barPath>}
        @return: (PIL) Image with path C{pathObject} rendered
        
        Renders selected path from the slide. Returned image has two colors:
        white for background, black for foreground.
        """
        # Generate temporary slide that will hold only the pathObject path.
        tempSlide = barTracedSlide(self.slideTemplate.toxml(), self.slideNumber)
        
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
        singlePathDocument.getElementsByTagName('g')[0].appendChild(pe)
        
        # return prepared slide and return resulting image
        return self._renderSvgDrawing(singlePathDocument)
    
    def contourize(self):
        """
        @type  tracingConfiguration: C{dict}
        @param tracingConfiguration: Dictionary holiding tracing properties
        like: L{BAR_TRACER_DEFAULT_SETTINGS<BAR_TRACER_DEFAULT_SETTINGS>}
        
        @rtype: L{barPretracedSlideRenderer<barPretracedSlideRenderer>}
        @return: Contour slide based on given CAF slide.
        
        Converts given CAF slide into contour slide by removing fill from paths
        and assigning them conturs.
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
    

    @todo: Mon Jan 31 23:09:35 CET 2011. Perhaps replacing all PIL procedures
    with NumPy rutines will give some speedup?
    
    @change: pon, 21 lut 2011, 16:06:26 CET, Partially merged with
    L{barPretracedSlide<barPretracedSlide>}. Several lines of code removed as a
    result.
    
    @change: Mon Jan 31 23:08:14 CET 2011. First version of tracer written in
    O-O manner. A bit slower that previous but still useful
    
    @change: sro, 25 sie 2010, 18:55:04 CEST
    
        1. Rebuilded path parsing. Now path parsing functions are moved to svgpathparse
           moule. 
        2. Some slight improvements
    
    @change: pia, 2 lip 2010, 12:21:14 CEST
    Implementing unlabeled structures handling.
    Assumptions:
    
        1. Areas with are not covered by regular labels are to be found and denoted
           as unlabelled areas.
        2. For each unlabelled area path and corresponding label should be created.
        3. Labels denoting unlabelled areas are backpropagated to pretraced file
        4. Labels denoting unlabelled areas are not traced - finding unalbelled areas
           is performed from scratch each time.
    
    Renember that brain contour bitmap has only two colors (black and white).
    Black clolor denotes region outside brain while white color denotes brain area.
    There is no contour in that bitmap. In case when many adjacent unlabeled regions
    exist they will be presented as a single unlabeled area.
    
    @change: Fri Jun 11 10:48:22 CEST 2010
    List of reviewing and error tracing procedures:

        1. When seed is placed outside brain region, warning is generated and
           debug information is dumped. Structure is not traced.
        2. When seed in placed on border (in non-white pixel in general),
           warning is generated and debug information is stored. Structure is not
           traced.
        3. Path naming scheme is constructed in a way which allows to quickly
           determine if tracing process was fully correct or not. Paths has to be
           numerated with consecutive numbers consistent with ID of corresponding
           labels.
        4. Spot labels and comment labels are not traced.
        5. For each step of processing, debug information may be stored. By debug
           information I mean SVG files with single traced structures as well as
           bitmaps from intermediate steps of processing
    
    @change: czw, 10 cze 2010, 16:32:41 CEST
    Replaced floodfilling alogrithm:
    Instead of currently used PIL ImageDraw.floodfill algorithm, the custom
    algorithm floodFillScanlineStack (implemented by me basing on http://) is
    now used. 
    
    The new algorithm appeared to be twice as fast as the previous algorithm.
    However, due to different method of performing filling the results of both
    algorithms are not exactly the same. The scanline algorithm seems to flood
    larger number of pixels than default algotithm. Neverless, the differences
    as rather slight and there is no need for further changes in the code.
    
    @change: Corrected brain contour treshold bug.
    In order to determine if structure labels are paced inside the brain regions
    the whole brain is traced in first step. Then brain region is cached for
    further comparision. However no treshold was applied and gray lines were not
    removed which produced unnecesarry errors. After applying treshold, all
    gray pixels where changed to white so the bug was removed. 
    
    @change: sro, 9 cze 2010, 13:50:10 CEST
    Structure path elements naming scheme: Generic structure name is >>structure%d_%s_%s<<
    where consecutive variables are:
    
        1. Subsequent structure number
        2. ID of the label basing on which given path was created
        3. Name of the structure modeled with given path
    
    Examples of valid path IDs:

        - structure92_label102_st
        - structure116_label131_Xi
        - structure1_label1_CPu
    
    When number of path doesn't match with number of label it means that tracing of some
    structures was ommited due to placing seed in non-white pixels.
    
    @change: sro, 9 cze 2010, 15:14:25 CEST
    Skipping tracing spotlabels and comment labels. 
    
    @change: sro, 9 cze 2010, 13:45:38 CEST
    Aditional image with brain area is cached after tracing whole brain area. This image is
    used in order to determina if flood fill seed is placed within brain area.
    
    @change: wto, 8 cze 2010, 14:09:13 CEST
    Removed generating vBrain structure, instead of this inverse of vBrain is traced.
    This procedure allows to generate area with brain ( instead of area of brain inverse)
    which is much more usefull.
    Note: vBrain is traced as first structure - not as last.
    
    @change: pon, 17 maj 2010, 19:25:38 CEST
    SVG image after rendering is converted to indexed color and then all
    non-white pixels are converted to color 200.
    """

    def trace(self, colorMapping):
        """
        @type   colorMapping: C{dict}
        @param  colorMapping: Holds color mapping defining unique colour for each
        structure: mapping[structureName] => colour.
        
        @rtype: L{barTracedSlideRenderer<barTracedSlideRenderer>}
        @return: Traced slide created by processing contour slide.
        
        @type     __labelCache: C{dict}
        @keyword  __labelCache: Temporary cache holding labels from contour slide.
        Removed after tracing.
        
        @type      __labelsLeft: C{dict}
        @keyword  __labelsLeft: Holds labels that will undergo tracing
        procedure. Removed after tracing.
        
        @type    __vBrainLabels: C{dict}
        @keyword __vBrainLabels: subset of C{__labelCache} holding C{vBrain}
        labels processed in different way than other labels.
        
        @type     __imageCache: C{list}
        @keyword  __imageCache: List of PIL images representing slide.
        Consecutive elements have thicker contours due to gap filling algorithm.
        
        @type     __brainOutline: PIL Image
        @keyword  __brainOutline: Whole brain outline. Image is generated in
        moment of provedding vBrain labels. During tracing consecutive areas are
        substracted from brain outline. Remaining white areas are considered as
        ublabelled areas.
        
        @type      _tracingConf: C{dict}
        @keyword   _tracingConf: Dictionary holiding tracing properties
        like: L{BAR_TRACER_DEFAULT_SETTINGS<BAR_TRACER_DEFAULT_SETTINGS>}
        
        Performs tracing of C{self} resulting in
        L{barTracedSlideRenderer<barTracedSlideRenderer>}
        depending on C{_tracingConf}.
        """
        if self._debugMode: _printRed("Initializing tracing...")
        
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
        if self._debugMode: _printRed("Processing vBrain...")        
        map(retSlide.addPath, self.__processVbrain())
        map(retSlide.addLabel, self.__vBrainLabels)
        
        # This is a bit tricky: At first we detect all incorrectly placed labels
        # then we remove them from tracing, 
        if self._debugMode: _printRed("Detecting invalidly placed labels...")        
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
        if self._debugMode: _printRed("Processing labels...")  
        map(retSlide.addPath, self.__processLabels())
        map(retSlide.addLabel, self.__labelsLeft)
        
        if self._tracingConf['DetectUnlabelled']:
            if self._debugMode: _printRed("Detecting unlabelles areas...")
            #TODO: Remove unlabelled areas from the labelCache
            UnlabelledLabels, UnlabelledPaths = self.__getUnlabeled()
            map(retSlide.addPath, UnlabelledPaths)
            map(retSlide.addLabel, UnlabelledLabels)
        else:
            UnlabelledLabels = []
        
        if self._debugMode: _printRed("Finishing...")
        # Put all remaining labels back to the contour slide
        self._labels = self.__labelCache
        map(self.addLabel, UnlabelledLabels)
        
        self.__clearAfterTracing()
        
        return retSlide.recolor(colorMapping)
    
    #{ Subprocedures - in order of execution
    def __loadImage(self):
        """
        Renders provided contour slide with given resolution and puts
        rendered image as a first element of cache.
        
        @rtype: C{None}
        @return: Nothing, only C{self.__imageCache} is updated.
        """
        self.__imageCache.append(\
                Image.eval(self.renderSlide(), self.__setContourColor))
    
    def __setContourColor(self , pixelColorValue):
        """
        Applies treshold function for given pixel value. All pixels which are
        non-white pixels becomes 'GrowDefaultBoundaryColor' pixels. This
        procedure assures that output image has only two colours (white and
        boundary) which is very convinient in further processing.
        
        @type  pixelColorValue: C{int}
        @param pixelColorValue: value of given pixel
        
        @rtype: C{int}
        @return: 255 if white pixel is given and C{GrowDefaultBoundaryColor}
                 otherwise.
        """
        # Just make an alias (perhaps it executes faster)
        defaultBoundaryColour = self._tracingConf['GrowDefaultBoundaryColor']
        
        if pixelColorValue != 255: return defaultBoundaryColour
        else: return 255

    def __createCache(self):
        """
        Creates image cache. First cached image is an original image. All other images
        (up to cacheLevel) are images with succesive grows (= applications of MinFilter).
        
        @rtype: C{None}
        @return: C{self.__imageCache} list is passed as a reference.
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
        Creates outline of the whole brain. The outline serves further as a
        reference for detecting missplaced labels and obviously as structure
        representing whole brain.
        
        Outline is created by substracting result of flooding each vBrain label
        and then inversing the result and tracing resulting bitmap.
        
        @rtype: C{[barPath, ... ]}
        @return: L{barPath<barPath>}s representing outline of the whole brain.
        """
        
        # Create empty white image for filling it with vBrain structure:
        self.__brainOutline =  ImageChops.constant(self.__imageCache[0], 255)
        
        # Then create image mask for vBrain structure;
        for (i, vBrainLabel) in enumerate(self.__vBrainLabels):
            self.__substractFromBrainOutline(\
                    self.__applyFill(self.__imageCache[0], vBrainLabel),\
                    source = 'Brain')
            
            if self._debugMode and self._tracingConf['DumpVBrain']:
                self.__brainOutline.save("%d_vBrain_%s.png"\
                        % (self.slideNumber, vBrainLabel.ID))
        
        return self.__bitmapToPaths(self.__brainOutline, vBrainLabel, invert = True)
    
    def __getMissplacedLabels(self):
        """
        Dectects labels that cannot be traced as they are missplaced: placed
        over the contours or outside the brain area.
        
        @rtype: C{[barRegularLabel, ...]}
        @return: List of labels that has to be removed from tracing.
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
        Creates list of paths basing on the list of
        L{barRegularLabels<barRegularLabel>} to trace -
        C{__labelsLeft}.
        
        @rtype: C{[barPath, ... ]}
        @return: L{barPath<barPath>} created by tracing individual labels 
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
        Creates list of paths and corresponding labels by tracing areas that were not
        labeled in pretraced files (unlabeled areas). This process is rather complicated
        so few words of explanation:
        
            1. We look for patches of N or more pixels. Only sych areas
               are considered as unlabelled areas. Smaller areas are most
               probably residual white pixels and should be ommited.
            2. Every group of two or more adjacent white pixels is flooded
               on "1".
            3. Patch of N or more white pixels is flooded with value "2"
               after tracing.
        
        After fiding unlabelled areas we can find 4 values of pixels:
        
            1. "0": areas outside brain
            2. "1": pixels of more than one adjacent pixels bu less than N
            3. "2": patches of N or more white pixels
        
        @rtype: C{( [barPath, ...], [barRegularLabel, ...] )}
        @return: Tuple containing list of paths and corresponding labels
        generated during detections of unlabelled areas.
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
                newLabelLocation = image_process.getBestLabelLocation(ImageForTracing)
                
                newLabel = self._clsRegularLabel(\
                            self._toSVGCoordinates(newLabelLocation),\
                            'Unlabelled',\
                            'Unlabelled-%d-%d' % coords,\
                            growlevel = 0)
                unlabeledAreasLabelsList.append(newLabel)
                
                # Apply minimum filter to slightly increase size of trace structures.
                #ImageForTracing = ImageForTracing.filter(ImageFilter.MaxFilter(3))
                map(unlabeledPathList.append, self.__bitmapToPaths(ImageForTracing, newLabel))
                if self._debugMode and self._tracingConf['DumpEachStepPNG']:
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
        if self._debugMode and self._tracingConf['DumpEachStepPNG']:
            self.__brainOutline.save("%d_after_tracing.png"% self.slideNumber, "PNG")
        return (unlabeledAreasLabelsList, unlabeledPathList)

    def __clearAfterTracing(self):
        """
        Clears all temporary class attributes created for tracing purposes.
        Invoked by L{trace<self.trace>} as last step of tracing.
        @rtype:None
        @return: None
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
        @type  seedLabel: L{barRegularLabel<barRegularLabel>}
        @param seedLabel: Seed label
        
        @rtype: C{[barPath, ...]}
        @return: List of paths resukting from tracing of the given source image
        and the provided C{seedLabel}.
        
        Extracts one L{barPath<barPath>} defined by coordinates of the given
        C{seedLabel}.
        If C{growlevel} for given seed label is not provided, performs automatic grow level selection, 
        and finally creates L{barPath<barPath>} element with all properties.
        
        @note: Function for determinating best grow level may be changed by
        assigning to C{self._tracingConf['BestFillAlgorithm']} reference for
        desired function.
        """
        
        # If growlevel is unassigned, select best growlevel automatically:
        if seedLabel.growlevel == -1:
            # Get area covered by each fill then choose best growlevel
            imgs, area    = self.__getCoveredAreasList(seedLabel)
            # Detect 'None' images and do not include them in automatic grow
            # level selection:
            if area.count(None)>0: area = area[0:area.index(None)]
            
            # Determine BestGrowLevel using provied BestFillAlgorithm
            #TODO: obsolete: BestGrowLevel = self._tracingConf['BestFillAlgorithm'](area)
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
        @type  sourceImage: PIL image
        @param sourceImage: image for tracing
        
        @type  seedLabel: L{barRegularLabel<barRegularLabel>}
        @param seedLabel: Seed label
        
        @type  invert: Boolean
        @param invert: Determine if image will be inverted before tracing
        
        @rtype: C{[barPath, ...]}
        @return: List of paths resukting from tracing of the given source image
        and the provided C{seedLabel}.
        
        Performs all operation releted with tracing bitmap into list of
        barPaths:
             
            1. Creates DOM structure from PoTrace SVG output
            2. Creates single path segments instead of long bezier paths
            3. Converts path coordinates to absolute
            4. Reduces transformation rules (using my own L{svgfix<svgfix>} module :)
                    
        """
        # Invert source image, if requested:
        if invert:
            sourceImage = ImageOps.invert(sourceImage)
        
        # Perform tracing procedure and cleam output
        tracerOutput = performTracing(sourceImage,\
                           self._tracingConf['PoTraceConf'])
        svgdom = _cleanPotraceOutput(tracerOutput)
        
        # Convert resulting svg document into set of barPaths
        newPathList = map(lambda x:\
                self._getPath(x, seedLabel),\
                svgdom.getElementsByTagName('path'))
        
        # If debuging procedures are enabled save tracing results (SVG file) and
        # source image (PNG file)
        if self._debugMode and self._tracingConf['DumpEachStepSVG']:
            OutputFilename = "%d_%s_%s.svg" % (self.slideNumber,\
                    seedLabel.ID, seedLabel.Caption)
            self._saveSVG(svgdom, OutputFilename)
        
        if self._debugMode and self._tracingConf['DumpEachStepPNG']:
            OutputFilename = "%d_%s_%s.png" % (self.slideNumber,\
                    seedLabel.ID, seedLabel.Caption)
            self._saveBitmap(sourceImage, OutputFilename)
        
        return newPathList
    
    def _getPath(self, pathElem, seedLabel):
        """
        @param pathElem: C{DOM object}
        @type  pathElem: svg path element 
        
        @param seedLabel: L{barRegularLabel<barRegularLabel>}
        @type  seedLabel: Seed label
        
        @rtype: L{barPath<barPath>}
        @return: barPath created from provided svg path element
        
        Creates C{barPath} from provided svg path element (result of tracing)
        and C{seedLabel}. Resulting path has proper id and structure name,
        however it has black colour assigned.
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
        @param seedLabel: L{barRegularLabel<barRegularLabel>}
        @type  seedLabel: Seed label
        
        @rtype: C{str}
        @return: id of new path generated using C{NewPathIdTemplate}
        """
        self._trPathGen+=1
        newPathId = self._tracingConf['NewPathIdTemplate'] %\
                (self._trPathGen, seedLabel.ID, seedLabel.Caption)
        return newPathId
    
    def __substractFromBrainOutline(self, imageToSubstract, source = 'Struct'):
        """
        @param imageToSubstract: PIL image
        @type  imageToSubstract:
        
        @type  source: C{str}
        @param source: determines source of C{imageToSubstract} may be either
        C{Struct} or C{Brain}.
        
        @rtype: C{None}
        @return: C{None}
        
        Marks traced areas on C{__brainOutline}. Depending
        on C{source} marking is performed in different way. Region denoted by
        vBrain regions are changed to black (0) while areas from tracing normal
        labels are changed to 100.
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
        Applies flood fill to given image using using coordinated passed in
        C{seedLabel,}.
        
        Description:
            1. Extract coordinates and structure name from C{seedLabel}.
            2. Rescale SVG coordinates to rendered image coordinates
            3. Fill given image with black color 
            4. Extend filled region by applying C{MinFilter} filter. Do it C{l+1} times
            5. Return flooded image or return number of black pixels depending
               on C{retNPIX} value.
        
        @type  sourceImage: C{PIL image}
        @param sourceImage: Image to flood
        
        @type  seedLabel: L<barRegularLabel{barRegularLabel}>
        @param seedLabel: Label used as seed.
        
        @type  retNPIX: C{bool}
        @param retNPIX: When C{True}, flooded image is returned along with
        number of replaced pixels. Otherwise only flooded image is returned.
        
        @rtype: C{(PIL image, int)}
        @return: Flooded image and number of flooded pixels depending on
        settings.
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
        Determines if bitmap with given seed is suitable for tracing. There are
        briefly two conditions which need to be satisfied in order to allow
        tracing:
        
            1. Seed has to be placed within brain contour. The brain contour is
               defined at the begining of tracing procedure.
            2. Seed has to be placed at white pixel. If seed points into
               non-white pixel is it a) border between two structures; b) area
               outside brain contour.
        
        In both cases debug information is printed.
        
        @type  im: PIL 
        @param im: Image to be floodfilled
        
        @param seedLabel: L{barRegularLabel<barRegularLabel>}
        @type  seedLabel: Seed label
        
        @rtype: C{bool}
        @return: True if image is suitable for tracing (according to testing
        conditions), False otherwise.
        """
        if not self.__isOutsideBrainOutline(seedLabel): return False
        if not self.__isOverContour(im, seedLabel): return False
        return True
    
    def __getUnlabeledAreas(self):
        """
        Finds white pixels in the image. If found pixel has white neighbourhood,
        its coordinates are returned, otherwise iteration continues
        until all white pixels are spotted.
        
        Current algorithm is rather ineffective. Main reason is that function has to exit
        if patch of white pixels is spotted. Then function is invoked again and iteration starts
        from beginning which is extremely ineffective. What should be done in such case?
        Perhaps implementation should include iterator. The problem is that we need to change array
        while we iterate over this array.
        
        @rtype: C{(int, int)}
        @return: (x,y) image coordinates of first spotted pixel that belongs to patch
        (two or more adjecent pixeles) of white pixels. If there is no such pixel,
        C{None} is returned.
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
                y = pn //self.__brainOutline.size[1]
                x = pn % self.__brainOutline.size[1]-1
                #print "White pixel found at coords %d,%d" % (x,y)
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
        @param seedLabel: L{barRegularLabel<barRegularLabel>}
        @type  seedLabel: Seed label
        
        @rtype:  C{bool}
        @return: True if label is placed outside brain, C{False} otherwise.
        
        Determines, if label is placed outside brain outline according to values
        of C{self.__brainOutline}.
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
        @type  im: PIL 
        @param im: Image to be verified
        
        @param seedLabel: L{barRegularLabel<barRegularLabel>}
        @type  seedLabel: Seed label
        
        @rtype:  C{bool}
        @return: True if label is not placed over contour, C{False} otherwise.
       
        Determined, if label not placed over boundary. 
        """
        coords = self._toImageCoordinates(seedLabel.Location)
        if im.getpixel(coords) == self._tracingConf['GrowDefaultBoundaryColor']:
            # You cannot fill starting from point which is not white
            self.__dumpWrongSeed(im, seedLabel)
            return False
        return True
    
    def _saveBitmap(self, im, filename):
        """
        @type  im: PIL 
        @param im: Image to be saved
        
        @type  filename: C{str}
        @param filename: name of the output file. Only filename, without path.
                         Provide .png extension.
        
        @rtype: C{None}
        @return: C{None}
        
        Saves provided BITMAP using given filename.
        
        @todo: integrate _saveBitmap and _saveBitmap into one function
        """
        OutputFilename = os.path.join(\
                self._tracingConf['DumpDirectory'], filename)
        im.save(OutputFilename)

    def _saveSVG(self, svgdom, filename):
        """
        @type  svgdom: DOM object 
        @param svgdom: SVG Image to be saved
        
        @type  filename: C{str}
        @param filename: name of the output file. Only filename, without path.
                         Provide .png extension.
        
        @rtype: C{None}
        @return: C{None}
        
        Saves provided svg using given filename.
        @todo: integrate _saveBitmap and _saveBitmap into one function
        """
        OutputFilename = os.path.join(\
                self._tracingConf['DumpDirectory'], filename)
        f=open(filename,'w')
        #svgdom.writexml(f)
        svgdom.writexml(f, indent="\n", addindent="\n", newl="\n")
        f.close()
    
    def __getCoveredAreasList(self, seedLabel):
        """
        Creates list of area covered by floodfill for each of cached images.
        
        @type  seedLabel: L{barRegularLabel<barRegularLabel>}
        @param seedLabel: Label used as seed
        
        @rtype: C{[int, ...}
        @return: List areas covered by floodfill for every image cached in
                 C{self.__imageCache}. Element of the list is
                 set to C{None} if tracing cannot be performed (ie. if given
                 label is unsuitable for tracing).
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
        print seedLabel
        
        images, areas = map(lambda x: x[0], result), map(lambda x: x[1], result)
        return (images, areas)
    
    def __dumpWrongSeed(self, im, seedLabel):
        """
        Outputs warning message to stderr and dumps invalid image into a file.
        
        @type  im: PIL 
        @param im: Image to be dumped
        
        @param seedLabel: L{barRegularLabel<barRegularLabel>}
        @type  seedLabel: Seed label
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


def floodFillScanlineStack(image, xy, value):
    """
    Custom floodfill algorithm that replaces original PIL ImageDraw.floodfill().
    This algorithm appears to be twice as fat as the original algorithm and more
    roboust. This algorithm requires reimplementing in C/Fortran and connecting
    to python somehow. Implementation is based on:
    http://www.academictutorials.com/graphics/graphics-flood-fill.asp
    
    This is implementaion on scanline floosfill algorithm using stack. The
    algorithm is not described here. To get insight please consult goole using
    'floodfill scanline'.
    
    @note: Please note that this algorithm assume floodfilling image in
           indexed color mode
    
    @type  image: PIL image object
    @param image: Image on which floodfill will be performed
    
    @type  xy: tuple of two integers
    @param xy: Coordinates of floodfill seed
    
    @type  value: integer
    @param value: Fill color value
    
    @rtype: C{int}
    @return: Update: sro, 30 cze 2010, 14:34:16 CEST returns number of pixels
             with changed color (area of floodfill).
             Nothing, image object is modifies in place.
    """
    
    pixel = image.load()
    x, y = xy
    w, h = image.size
    
    npix=0
    background = pixel[x, y]
    stack=[]
    stack.append((x,y))
    
    while stack:
        x,y=stack.pop()
        y1=y
        while y1>= 0 and pixel[x, y1] == background:
            y1-=1
        y1+=1
        
        spanLeft = spanRight = 0
        
        while y1 < h and pixel[x, y1] == background:
            pixel[x, y1] = value
            npix+=1
            
            if (not spanLeft) and x > 0 and pixel[x-1,y1] == background:
                stack.append((x-1,y1))
                spanLeft=1
            else:
                if spanLeft and x > 0 and pixel[x-1,y1] != background:
                    spanLeft=0
            
            if (not spanRight) and x<w-1 and pixel[x+1,y1] == background:
                stack.append((x+1, y1))
                spanRight=1
            else:
                if spanRight and x<w-1 and pixel[x+1,y1] != background:
                    spanRight=0
            y1+=1
    
    return npix                    

def selectBestGapFillingLevel(area):
    """
    Selects the best level of "gap filling" by analyzing number of flooded pixels
    for each "gap filling" level.
    
    Agorithm used for selecting best level is totally heuristic and relies
    on assumption that willing each gap is equivalent to rapid lowering of number of
    flooded pixels (as we have smaller region after closing the gap than before).
    
    Algorith tries to seach for such rapid changes and prefers smaller structures
    rather than larger.
    
    If number of flooded pixels do not changes rapidly across different levels of
    gap filling it means that most probably structure do not have any gaps.
    In such case, algorithm selects region defined without using "gap filling".
    
    There are several cases defined for detecting one, two and more gaps fills.
    You should be noted that algorithm do not exhaust every possible case and
    reconstructed structures should be reviewed manually.
    
    @type  area: list of integers
    @param area: Structure size defined by number of flooded pixels.
                 Each value for consecutive "gap filling" level.
    
    @rtype: C{int}
    @return: Gap filling level considered as the most proper.
    """
    
    a=area
    # Case 1.
    # All areas are simmilar
    # Percentage difference between two consecutive areas is less than x%
    if _areNearlyTheSame(area,0.02):
        return 0
    
    # Case 2.
    # First area is about 1.2 times larger than the second. (step)
    # Second and next are nearly the same as third and further
    # Take the second
    if a[0]>=1.2*a[1] and _areNearlyTheSame(a[1:],0.02):
        return 1
    
    # Case 4.
    # handling rapid jump to near-zero value
    # If, after second filtering area falls to near-zero in comparison with
    # previous fill, it means that filling was too large 
    if a[1]>=20*a[2] and\
            _areNearlyTheSame(a[0:2],0.02) and\
            _areNearlyTheSame(a[2:],0.02):
        return 1
    
    # Case 3.
    # First two are nearly the same and ~1.2 larger than other
    # 3rd and next are nearly the same
    # One region of overgrown take 3rd.
    if a[1]>=1.2*a[2] and\
            a[1]>=10*a[2] and\
            _areNearlyTheSame(a[0:2], 0.02) and\
            _areNearlyTheSame(a[2:] , 0.02):
        return 2
    
    # None of above return 1 to be at the safe side
    return 1

#TODO: stupid! do something. Algorithms settings:
#BAR_TRACER_DEFAULT_SETTINGS['BestFillAlgorithm'] = selectBestGapFillingLevel

def _areNearlyTheSame(TestList, Treshold):
    """
    Checks if elements "are nearly the same" - if they are quotient
    of consecutive items are less than given treshold:
    (a2/a1, a3/a2,...) > Treshold.
    
    @type  TestList : list
    @param TestList : List of elements to check relations between elements
    @type  Treshold : float
    @param Treshold : Threshold. Treshold value has to be larger than 0.
    
    @rtype          : C{bool}
    @return         : True if numbers may be considered as nearly the same,
                      False otherwise.
    """
    # Create temporary list of quotient if consecutive elements: (a2/a1, a3/a2,...)
    temp = map(lambda x,y: float(x)/float(y)-1, TestList[:-1], TestList[1:])
    
    # Check if all elements are withing given treshold
    return all( x <= Treshold and x >= -Treshold for x in temp)
    
def _printRed(str):
    """
    @type  str: string
    @param str: String to print to stderr in red.
    @return   : Just prints the string in red.
    
    Prints given string to stderr using red color.
    """
    print >>sys.stderr, '\033[0;31m%s\033[m' % str

def _cleanPotraceOutput(tracerOutput):
    """
    @type  tracerOutput: C{str}
    @param tracerOutput: String produced by PoTrace
    
    @rtype: C{DOM object}
    @return: DOM object fixed by the procedure.
    
    Creates DOM object and fix paths in SVG document from provided output.
    """
    svgdom = dom.parseString(tracerOutput)
    svgfix.fixSvgImage(svgdom, pagenumber=None, fixHeader=False)
    return svgdom

def performTracing(binaryImage, tracingProperties, dumpName = None):
    """
    Performs image tracing via potrace and pipes mechanism.
    Assumes that image has one, non-separable area filled with black pixels.
    This function do not perform parsing the output.

    Tracing Workflow:
        1. Save image in bmp format in dummy string
        2. Sends bmp string to potrace via pipe mechanism
        3. Perform tracing
        4. Read tracing output via pile
        5. Return raw tracing output

    @type  binaryImage: PIL image
    @param binaryImage: Flooded image for tracing. Image is assumed to be
                          grayscale image with only two colours used: black
                          and white. Black colour is considered as foreground
                          while white colour is background colour.

    @return: Raw tracing output string.
    """
    
    # Create file-like object which handles bmp string
    ImageString = cStringIO.StringIO()
    
    # Save image to this file-like object
    binaryImage.save(ImageString, "BMP")
    if dumpName: binaryImage.save(dumpName, "BMP")
    
    # Create process pipes
    # potrace parameters:
    # -s for settring SVG output
    # -O Optimization parameter
    # -r SVG Image resolution in DPI
    # -W,H Output dimensions of SVG drawing
    # -o - - Input and output via pipes
    process = subprocess.Popen(['potrace',\
            '-s',\
            '-O', tracingProperties['potrace_accuracy_parameter'],\
            '-r', tracingProperties['potrace_svg_resolution_string'],\
            '-W', tracingProperties['potrace_width_string'],\
            '-H', tracingProperties['potrace_height_string'],\
            '-o','-','-']\
            , stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    # Pass bmp string to pipe, close image string.
    process.stdin.write(ImageString.getvalue())
    ImageString.close()
    
    # Read and return tracing output
    return  process.stdout.read()

def validateStructureName(structureName):
    """
    @type  structureName: C{str}
    @param structureName: Name to be verified
    
    @rtype: C{str} or C{bool}
    @return: C{structureName} if structure name if correct, C{Flase} otherwise.
    
    Verifies structure name. Valid structure name has to be shorter than 16
    characters, cannot start or end with '-' and consists of alphanumeric
    charactes and hyphens.
    return (len(structureName) <= 30 # length is within proper range
        and not structureName.startswith("-") and not structureName.endswith("-") # no bordering hyphens
        and CONF_ALOWED_STRUCTURE_CHARACTERS.search(structureName) and structureName) # contains only legal characters
    """
    return structureName

def CleanFilename(filename):
    """
    Strip filename from prohibited characters.
    Prohibited characters are replaced by underscore characted.

    @type  filename : string
    @param filename : filename to strip
    @return         : corrected filename
    """
    return filename.replace('/','_')

def flatten(x):
    """
    @type  x: iterable sequence
    @param x: sequence to flat
    
    @return: (list). Flattened list. Read description for firther information.
    
    flatten(sequence) -> list
    
    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    
    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    
    """
    
    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def getCorrections(boundingBoxes, smoothedBBoxes):
    """
    Method calculates list of matriced allowing transforming set raw bouding
    boxes to smoothed bounding boxes.
    
    @type  boundingBoxes: numpy nd array
    @param boundingBoxes: array of raw bounding boxes (n x 4) extracted from
                          structures.
    
    @type  smoothedBBoxes: numpy nd array
    @param smoothedBBoxes: array of smoothed bounding boxes (n x 4) aquired by
                           smoothing procedure.
    
    @return: array of n 3 x 3 matrices allowing transforming each raw bounding
             box to smoothed bounding box.
    """
    # Make some usefull aliases
    (x1, y1) = boundingBoxes[:,0], boundingBoxes[:,1]
    (x2, y2) = boundingBoxes[:,2], boundingBoxes[:,3]
    (x1p, y1p) = smoothedBBoxes[:,0], smoothedBBoxes[:,1]
    (x2p, y2p) = smoothedBBoxes[:,2], smoothedBBoxes[:,3]
    
    # Calculate list of n transformation coefficients    
    c = barTracedSlide.calculateTransfFromMarkers(barTracedSlide,
            (x1, y1), (x2, y2), (x1p, y1p), (x2p, y2p), np.zeros(x1.size))
    c=np.asarray(c[:-1]).transpose()
    
    # Return set of matrices ready to use them for transformations
    return map(lambda x: np.array([ [x[0],0   ,x[1]],\
                                    [0   ,x[2],x[3]],\
                                    [0   ,0   ,  1]]),c)

def _removeWhitespacesXML(domNode, unlink = True):
    emptyTextElements = []
    for child in domNode.childNodes:
        if child.nodeType == xml.dom.Node.ELEMENT_NODE:
            _removeWhitespacesXML(child, unlink)
        elif child.nodeType == xml.dom.Node.TEXT_NODE:
            child.data = child.data.strip()
            if child.data == '':
                emptyTextElements.append(child)
    for child in emptyTextElements:
        domNode.removeChild(child)
        if unlink:
            child.unlink()


#if __name__=='__main__':
#    #sl = barTracedSlide.fromXML(sys.argv[1]) 
#    #print sl.svgDocument.toxml()
#    if True:
#        m1 = barCoordinateMarker((0,0),(10,10))
#        m2 = barCoordinateMarker((5,5),(500,500))
#        bm = barCoronalMarker(6.0, (800, 800))
#        sl = barPretracedSlideRenderer()
#        sl.markers.append(m1)
#        sl.markers.append(m2)
#        sl.markers.append(bm)
#        sl.writeXMLtoFile('1.svg')
#        sl = barPretracedSlide.fromXML('1.svg')
#        sl.parseMarkers()
#        sl.writeXMLtoFile('1.svg')
#        print sl
#    
#    if False:
#        for i in range(40, 80):
#            sl =\
#            barPretracedSlide.fromXML('/home/pmajka/3dbrainatlases/input_atlases/paxinos_franklin_mouse/raw_svg/%d_pretrace_pretrace_v2.svg' % i)
#            for (k,v) in sl._labels.items():
#                sl._labels[k].growlevel = 0
#            sl.writeXMLtoFile('/home/pmajka/3dbrainatlases/input_atlases/paxinos_franklin_mouse/raw_svg/%d_pretrace_pretrace_v2.svg'% i)
#    
#    if False:
#        import image_process
#        structureName = 'vBrain'
#        tracedSlideRange = range(28,128)
#        #tracedSlideRange = range(44,204)
#        tracedSlRangeArr = np.array(tracedSlideRange)
#        tracedSlTemp =\
#        '/home/pmajka/3dbrainatlases/input_atlases/paxinos_franklin_mouse/raw_svg/%d_traced_v0.svg'
#        
#        boundingBoxes = np.array(\
#            map(lambda x:\
#                barTracedSlide.fromXML(tracedSlTemp % x)[structureName].bbx,\
#                tracedSlRangeArr))
#        
#        smoothedBBoxes = map(lambda x:\
#                image_process.savitzky_golay(\
#                    boundingBoxes[:,x], window_size=15, order=5),\
#                [0,1,2,3])
#        smoothedBBoxes=np.array(smoothedBBoxes).transpose()
#        
#        correctionsTransforms = getCorrections(boundingBoxes, smoothedBBoxes)
#        ct = correctionsTransforms
#        
#        for i in tracedSlideRange:
#            print i
#            sl=barTracedSlide.fromXML(tracedSlTemp % (i,))
#            sl.affineTransform(ct[i-tracedSlideRange[0]])
#            sl.writeXMLtoFile('/home/pmajka/3dbrainatlases/input_atlases/pfm/%d_traced_v0.svg'% i)
#    
#    if False:
#        sl =\
#        barPretracedSlide.fromXML('/home/pmajka/3dbar/input_atlases/paxinos_franklin_mouse/raw_svg/70_pretrace_pretrace_v2.svg')
#        import pycallgraph
#        e = np.eye(3)
#        pycallgraph.start_trace()
#        sl.affineTransform(e)
#        pycallgraph.stop_trace()
#        pycallgraph.make_dot_graph('1.png')
