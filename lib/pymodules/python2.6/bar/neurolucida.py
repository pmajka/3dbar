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

import xml.dom.minidom as dom
import sys
import string
import numpy as np

from parsers import barExternalParser,  barGenericParser
from base import barObject, barCommentLabel, barPath, barTransfMatrixMetadataElement,\
                        barBregmaMetadataElement, barSpotLabel, barTracedSlideRenderer


global GLOBAL_LABEL_ID
GLOBAL_LABEL_ID=0

BAR_NL_DEFATULT_OBJ_TYPES = ['contour', 'text', 'marker']

class barNLfile(barObject):
    def __init__(self, xmlFile,\
                       objTypes = BAR_NL_DEFATULT_OBJ_TYPES,\
                       zAccuracy = -1):
        svgdom = dom.parse(xmlFile)
        
        self._contours = []
        self._markers  = []
        self._textElems= []
        self._sections = None
        self._zAccuracy= zAccuracy
        #TODO: Implement sections
        
        self._zindex = {}
        
        (self._scaling, self._coord, self._zspacing)=\
            self.__extractImageElement(svgdom.getElementsByTagName('image')[0])
        
        if 'contour' in objTypes: self.__processContours(svgdom)
        if 'marker' in objTypes:  self.__processMarkers(svgdom)
        if 'text' in objTypes:    self.__processTextElems(svgdom)
        self.__createZindex()
    
    def __extractImageElement(self, imageElement):
        scaleElement  = imageElement.getElementsByTagName('scale')[0]
        coordElement  = imageElement.getElementsByTagName('coord')[0]
        zpacingElement= imageElement.getElementsByTagName('zspacing')[0]
        
        dict  = self._getAttributesDict(scaleElement)
        scale = tuple(map(lambda x: float(dict[x]), ['x','y']))
        
        dict  = self._getAttributesDict(coordElement)
        coord = tuple(map(lambda x: float(dict[x]), ['x','y','z']))
        
        zpacing = float(zpacingElement.firstChild.nodeValue.strip())
        
        return (scale, coord, zpacing)
    
    def affineTransform(self, M):
        return self.__affineTransform(M)
    
    def __affineTransform(self, M):
        for elementType in [self._contours, self._markers, self._textElems]:
            map(lambda x: x.affineTransform(M), elementType)
        self.__affineTransformObjects(M) 
        self.__createZindex()
    
    def __affineTransformObjects(self, M):
        s = self._scaling
        c = self._coord
        z = self._zspacing
        
        C = np.array ([[s[0],    0,  0, c[0]],\
                      [0   , s[1],   0, c[1]],\
                      [0   ,    0,   1, c[2]],
                      [0   ,    0,   0, 1   ]])
        
        R = np.dot(C,M)
         
        self._scaling = (R[0][0], R[1][1])
        self._coord   = tuple(R[0:3,3])
    
    def __processContours(self, svgdom):
        for contour in svgdom.getElementsByTagName('contour'):
            self._contours.append(barNLcontour(contour))
    
    def __processMarkers(self, svgdom):
        for marker in svgdom.getElementsByTagName('marker'):
            self._markers.append(barMarkerElement(marker))
    
    def __processTextElems(self, svgdom):
        for text in svgdom.getElementsByTagName('text'):
            self._textElems.append(barTextElement(text))
    
    def __roundZcoord(self):
        for elementType in [self._contours, self._markers, self._textElems]:
            map(lambda c:\
                    c.__setattr__('_z', round(c._z, self._zAccuracy)),\
                    elementType)
    
    def __createZindex(self):
        self.__roundZcoord()
        
        zCoords = list(set(map(lambda x: x._z, self._contours)))
        zCoords.sort()
        
        self._zindex = {}
        for zc in zCoords:
            self._zindex[zc] = barNLzcoordList(zc)
        
        for elementType in [self._contours]:
            for element in elementType:
                self._zindex[element._z].paths.append(element)
        
        for elementType in [self._markers, self._textElems]:
            for element in elementType:
                try:
                    self._zindex[element._z].labels.append(element)
                except:
                    pass
    
    def __getSlideRange(self):
        return sorted(self._zindex.keys(), reverse=True)
    
    def getSlide(self, slideNumber = None, **kwargs):
        rc = kwargs['renderingProperties']
        tc = kwargs['tracingProperties']
        newSlide = barTracedSlideRenderer(\
               rendererConfiguration = rc,\
               tracingConfiguration  = tc)
        newSlide.slideNumber  = slideNumber
        
        if slideNumber == None:
            for contour in  self._contours:
                newSlide.addPath(contour.getBarPath())
            for marker in self._markers:
                newSlide.addLabel(marker.getLabel())
            for textElem in self._textElems:
                newSlide.addLabel(textElem.getLabel())
        
        if slideNumber is not None:
            # Choose slide element corresponding to provided slide number:
#            elementKey = self.slideRange[slideNumber]
#            coordElemList = self._zindex[elementKey]
            coordElemList = self._zindex[self.slideRange[slideNumber]]
            
            for contour in coordElemList.paths:
                newSlide.addPath(contour.getBarPath())
            for labelEl in coordElemList.labels:
                newSlide.addLabel(labelEl.getLabel())
            
            newSlide.updateMetadata(barBregmaMetadataElement(coordElemList.zCoord))
            transformationMatrixTuple=(\
                    self._scaling[0], self._coord[0],
                    self._scaling[1], self._coord[1])
            newSlide.updateMetadata =\
                (barTransfMatrixMetadataElement(transformationMatrixTuple))
        
        return newSlide
    
    slideRange = property(__getSlideRange)


class barNLzcoordList(object):
    def __init__(self, zCoord):
        self.zCoord = zCoord
        self.paths = []
        self.labels= []
    

class barNLelement(barObject):
    def __init__(self, domElement):
        self._color      = None
        self._name       = None
        self._sid        = None
        self._points     = []
        self._properties = self.__getProperties(domElement)
    
    def affineTransform(self, M):
        for (i,p) in enumerate(self._points):
            t = self.__transformPoint((p[0], p[1], self._z), M)
            self._points[i] = (t[0][0], t[1][0])
        self._z         = self._z * M[2][2] + M[2][3]
    
    def __transformPoint(self, point, M):
        p = point
        oc = np.array( [ [p[0]],[p[1]],[p[2]],[1] ] )
        nc = np.dot(M, oc)
        return nc
    
    def __getProperties(self, contourElement):
        properties = {}
        for propertyElement in contourElement.getElementsByTagName('property'):
            pe = self.__parsePropertyElement(propertyElement)
            properties[pe[0]] = pe[1]
        return properties
    
    def __parsePropertyElement(self, propertyElement):
        propertyName  = propertyElement.getAttribute('name').strip()
        propertyValue = propertyElement.firstChild.nodeValue.strip()
        return (propertyName, propertyValue)
    
    def _calcPathDefinition(self, contourElement):
        points = []
        for point in contourElement.getElementsByTagName('point'):
            (coord, z, sid) = self.__getPointCoords(point)
            points.append(coord)
            self._z   = z
            self._sid = sid
        return points
    
    def __getPointCoords(self, pointElement):
        """
        dict  = self._getAttributesDict(pointElement)
        coord = tuple(map(lambda x: float(dict[x]), ['x','y']))
        z     = float(dict['z'])
        sid   = dict.get('sid', None)
        """
        coord = tuple(map(lambda x: float(pointElement.getAttribute(x)), ['x','y']))
        z     = float(pointElement.getAttribute('z'))
        sid   = pointElement.getAttribute('sid')
        return (coord, z, sid)


class barTextElement(barNLelement):
    def __init__(self, textElement):
        self._color      = textElement.getAttribute('color')
        self._points     = barNLelement._calcPathDefinition(self, textElement)
        
        valueElement = textElement.getElementsByTagName('value')[0].firstChild.nodeValue
        self._name = valueElement
    
    def getLabel(self):
        global GLOBAL_LABEL_ID
        GLOBAL_LABEL_ID+=1
        return barCommentLabel(self._points[0], self._name, str(GLOBAL_LABEL_ID))


class barMarkerElement(barNLelement):
    def __init__(self, markerElement):
        self._type  = None
        
        self._color      = markerElement.getAttribute('color')
        self._name       = markerElement.getAttribute('name').strip()\
                           .replace('_','-').replace(' ','-')
        self._points     = barNLelement._calcPathDefinition(self, markerElement)
    
    def getLabel(self):
        global GLOBAL_LABEL_ID
        GLOBAL_LABEL_ID+=1
        return barSpotLabel(self._points[0], self._name, str(GLOBAL_LABEL_ID))


class barNLcontour(barNLelement):
    def __init__(self, contourElement, restrictive = True):
        barNLelement.__init__(self, contourElement)
        self._resolution = None
        self._z          = None
        
        # Do restrictive validation of the provided contour element.
        if restrictive: self.__restrictiveValidation(contourElement)
        
        self._color      = contourElement.getAttribute('color')
        self._points     = barNLelement._calcPathDefinition(self, contourElement)
        self._name       = contourElement.getAttribute('name').strip()\
                           .replace('_','-').replace(' ','-')
        self._resolution = contourElement.getAttribute('resolution')
        self._points     = self._calcPathDefinition(contourElement)

    def __restrictiveValidation(self, contourElement):
        if contourElement.getAttribute('closed') != "true":
            raise TypeError, "Invalid contour element provided" 
        if contourElement.getAttribute('style') != "solid":
            raise TypeError, "Invalid contour element provided" 

    def __getPathDefinition(self):
        s = "M%f,%f " % self._points[0] +\
            " ".join(map(lambda x: "L%f,%f" % x, self._points[1:])) +\
            " Z"
        return s
    
    def __setPathDefinition(self, newDef):
        pass
    
    def getBarPath(self):
        # Valid path element should have at least 3 points otherwise, SVG path
        # cannot be generated.
        if len(self._points) < 3:
            raise TypeError,\
            "Invalid contour element provided. Contour should consist of 3 and more points." 
        
        # The structure0 prefix is to adjust the path id to the general template
        # which is structure%numer%_%nazwalabelki%_%nazwastruktury%
        pathID = 'structure0_%s_%s' % (self._properties['GUID'], self._name)
        return barPath(pathID, self.pathDefinition, self._color) 
    
    pathDefinition = property(__getPathDefinition, __setPathDefinition)


class nlParser(barExternalParser):
    _requiredInternalData=barGenericParser._requiredInternalData +\
            ['renderingProperties', 'tracingProperties', 'slideRange']
    
    def __init__(self, inputFilename, contour, zAccuracy, **kwargs):
        barGenericParser.__init__(self, **kwargs)
        self._nlSlide = barNLfile(inputFilename, contour, zAccuracy)
    
    def __getSlideRange(self):
        return range(len(self._nlSlide._zindex.keys()))
    
    def parse(self, slideNumber, useIndexer = True):
        super(nlParser, self).parse(slideNumber)
        return self._nlSlide.getSlide(slideNumber,\
               tracingProperties     =  self.tracingProperties,\
               renderingProperties   =  self.renderingProperties)
    
    def affineTransform(self, M):
        self._nlSlide.affineTransform(M)
    
    slideRange = property(__getSlideRange)
 

if __name__ == '__main__':
    pass
