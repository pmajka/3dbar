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
Module or simpylying input SVG file structure. In many converters SVG files are created with
preserving groups of objects. It results in generating lot of C{g} objets.
Each of nested C{g} may have own transformation matrix. What is more, most nested object
(text, path, line, etc. may have its own transformation matrix defined). Nesting all those
transformation causes lot of confusion and dissalows extracting filnal coordinates of objects
in a direct way.

This modlule applies all nested transfomarions and leaves objects with their final coordinates
allowing further modules direct extraction of coordinates and dimensions.

@note: Only absolute coordinates (capital letters in segmants names) are parsed properly.

G{importgraph}

Currently only translate and scale transformations are supprted.

re_trd - transformations dictionary:
    - translate: translate(number,number)
    - scalexy: scale(number,number)
    - scale: scale(number)

Usage exapmle:
    >>> import svgfix
    >>> _dev_fix_img(dom_svg_object)

@see: http://www.w3.org/TR/SVG/coords.html#NestedTransformations 

"""
import re
import xml.dom.minidom as dom
import numpy as np
import sys
from string import *
from defaults import *
from svgpathparse import parsePath, UnparsePath

def getTransformMatrix(tr):
    """
    @type  tr: string
    @param tr: Transformation. String extracted from 'transformation' attrubute
    of SVG element.
    @return  : NumPy transformation matrix equivalent to provided transformation string.

    How the function works?
        1. Transformation string is a serie of tanslate or scale commands:
        eg. 'translate(20,20) scale(.3)' thus we have two sepatate transformations which
        we need to parse separately and multiply to calculate final matrix.
        2. If an element does not have any transformation, indentity matrix should be returned.

    Expamples:
        >>> import atlasparser
        >>> atlasparser.svgfix.getTransformMatrix("")
        array([[ 1.,  0.,  0.],
              [ 0.,  1.,  0.],
              [ 0.,  0.,  1.]])
        >>> atlasparser.svgfix.getTransformMatrix("translate(.2,3) scale(.4)")
        array([[ 0.4,  0. ,  0.2],
               [ 0. ,  0.4,  3. ],
               [ 0. ,  0. ,  1. ]])
    
    @note: Subsequent transformations should be separated by one or more whitespace chars.
    @see: Details of transforming SVG objects: http://www.w3.org/TR/SVG/coords.html
    """
    # TODO: Make this function more general (ie. empty string exceptions handling...)
    # TODO implement more general splitting (re.split??)
    
    # Split transformation string by space
    # Except 'matrix' transformation: it should be handled separetely:
    tr = tr.replace(', ',',')
    if re.search(re_trd['matrix'], tr):
        transformations_list=[strip(tr)]
    else:
        transformations_list=split(strip(tr)," ")

    # Define initial transform matrix which is identity matrix:
    ctm=np.eye(3) #ctm - current transformation matrix
    
    # Iterate over transformations and define transformation matrix
    # for each elementaty transformation
    # TODO: It should be written in less time-consuming way.(string.beginswith??)
    for transformation in transformations_list:
        for tr_type in re_trd.keys():
            values=re_trd[tr_type].search(transformation)
            if values:
                # define transformation matrix for current elementary transformation
                # ntm - new transformation matrix
                ntm=__defineTransformationMatrix(tr_type,values)
                #if non-identity transformation was found, add new transformation
                #by multiplying current transformation matrix by new transformatiom matrix
                ctm=np.dot(ctm,ntm)
                continue

    #If no more transformations left, return current transformation matrix
    return ctm

def __defineTransformationMatrix(tr_type,v):
    """
    @type  tr_type: string 
    @param tr_type: Type of transformation, one of the re_trd dictionary keys.
    @type        v: tuple
    @param       v: Tuple of values extracted from transformation string
                    (ammount of translation, scaling factor, matrix elements,...).
                    In other words results of appying regular expression to transformation string.
    @return       : Transformation matrix for given elementary transformation string.

    """ 
    # v it's a shourtcut for values.
    # Handles all values extracted from transformation string
    v=map( float ,v.groups() )

    if tr_type=='translate':
        ret=[ [ 1  , 0  , v[0] ], \
              [ 0  , 1  , v[1] ], \
              [ 0  , 0  ,  1.  ] ]
        return np.array( ret, dtype=float)

    if  tr_type=='scalexy':
        ret=[ [ v[0] , 0    , 0.], \
              [ 0    , v[1] , 0.], \
              [ 0    , 0    , 1.] ]
        return np.array( ret, dtype=float)

    if  tr_type=='scalex':
        ret=[ [ v[0] , 0    , 0.], \
            [ 0    , v[0] , 0.], \
            [ 0    , 0    , 1.] ]
        return np.array( ret, dtype=float)

    if  tr_type=='matrix':
        ret=[ [ v[0] , v[2] , v[4] ], \
              [ v[1] , v[3] , v[5] ], \
              [ 0    , 0    , 1.   ] ]
        return np.array( ret, dtype=float)

    # No transformation has been found - use identity transformation
    return np.eye(3)

def __fixElement(el,gm):
    """
    @type  el: DOM object
    @param el: element to be fixed.
    @type  gm: NumPy array
    @param gm: Transformation matrix of parrent element
               (gm - global transformation matrix)
    @return  : nothing - only element C{ el} is modified.

    Converts coordinates in given element to absolute values depending on element type.
    Steps:
        1. Check, if given element has any transformation defined.
           If yes, compute transformation matrix for this element as well as new
           transformation matix..
        2. Correct coordinates of element depending on its type.
        3. Perform element-dependent corredtion (scale font size, stroke, etc.)
    """
    
    # Check if given element has "transform" element
    if el.hasAttribute('transform'):
        # Get transformation matrix for given element
        # (tm - transformation matrix of given element)
        tm=getTransformMatrix(el.attributes['transform'].value)

        # Remove transformation string - we do not need it anymore
        el.removeAttribute('transform')

        # Define current transformation matrix.
        cm=np.dot(gm,tm)
    else:
        # If there is no transformation string in given element,
        # Current transformation matrix is the same as
        # transformation matrix of parrent element (gm)
        cm=gm

    # Fix element depending on its type:

    if el.nodeName=='text':
        __fixText(el,cm)

    if el.nodeName=='line':
        __fixLine(el,cm)

    if el.nodeName=='polygon':
        __fixPolygon(el,cm)

    if el.nodeName=='polyline':
        __fixPolyline(el,cm)

    if el.nodeName=='path':
        __fixPath(el,cm)

def __fixLine(el,cm):
    """
    @type  el: DOM object
    @param el: Line SVG element to be modified.
    @type  cm: NumPy array
    @param cm: Transformation matrix to be applied.
    @return  : nothing - only element C{el} is modified.

    Transforms line element of SVG file to final coordinates.
    Function assumes that element has correctly defined x1,y1 and x2,y2 attributes.
    If an unhandled excepion is  raised, it means that element is defined incorretly.
    """
    # Transform point (x1,y1) to new coordinates (x1',y1')
    (el.attributes['x1'].value,el.attributes['y1'].value)=\
    map(str, __transformPoint( [el.attributes['x1'].value , el.attributes['y1'].value]  ,cm))

    # Transform point (x2,y2) to new coordinates (x2',y2')
    (el.attributes['x2'].value,el.attributes['y2'].value)=\
    map(str, __transformPoint( [el.attributes['x2'].value , el.attributes['y2'].value]  ,cm))

def __fixText(el,cm):
    """
    @type  el: DOM object
    @param el: Text SVG element to be modified.
    @type  cm: NumPy array
    @param cm: Transformation matrix to be applied.
    @return  : nothing - only element C{el} is modified.

    Transforms text element of SVG file to final coordinates. Initial coordinates are optional.
    Function tried to scale font size. If final font size is less than 1px it is forced to be 1px.
    """
    # TODO: Put lot of exceptions handling
    # If there are x and y attributes, renember their values and remove those attributes:
    if el.hasAttribute('x') and el.hasAttribute('y'):
        # Renember current coordiantes of label
        # cc - current coordinates: coordinates before transformation
        #      ( vector of three values: [x,y,1] ) 
        # p - temporary variable
        p=map(  float , [ el.attributes['x'].value , el.attributes['y'].value ]  )
        cc=np.array([ [p[0]] , [p[1]] , [1] ])
        
        # Remove currnet coordinates
        el.removeAttribute('x')
        el.removeAttribute('y')
    else:
        # If there are no x and y attributes, we assume that initial coordinates are (0,0)
        # thus vector of coordinates is (0,0,1)
        cc=np.array([[0],[0],[1]])
    
    # nc - New coordinates: coordinates after applying transformations
    nc=np.dot(cm,cc)
    
    # Update coordintes of labels
    el.setAttribute('x',str(nc[0][0]))
    el.setAttribute('y',str(nc[1][0]))
    
    # If element has 'font-size' attribute, update font size also
    if el.hasAttribute('font-size'):
        result = re_fontsizepx.search(el.attributes['font-size'].value)
        if result:
            CurrentFontSize=float(result.groups()[0])
            # New font-size value is:
            # (current font size) * (scale factor: cm[0][0])
            # then we need to round int, convert to integer and then to string
            
            # When font size is less or equal than zero, it causes many parsers to crash
            # In such case font size is forced to be at least one px
            NewFontSize=int(round(CurrentFontSize*cm[0][0]))
            if NewFontSize <= 1:
                el.attributes['font-size'].value='1px'
            else:
                el.attributes['font-size'].value=str(NewFontSize)+'px'

def __fixPolygon(el,cm):
    """
    @type  el: DOM object
    @param el: Polygon SVG element to be modified.
    @type  cm: NumPy array
    @param cm: Transformation matrix to be applied.
    @return  : nothing - only element C{el} is modified.
    
    @requires: Coordinates in 'points' attrubute has to be separated by whitespaces.
    @requires: Correctly defined coordinated eg. C{points='2.3,-5.0 34,5'}.

    Funtion transforms all points in polygon one by one using provided transformation matrix.
    """

    # Buffer which holds string that will be passed as a value of 'points' attribute
    buffer=""

    try:
        # Split "points" attribute value in order to get list of points
        PointsTable=split(el.attributes['points'].value)

        # Now we transform each point to new coordinates
        for pt in PointsTable:
            # Extract pair of points from string and then 
            # convert results to list
            PtPair=list(re_PointsPair.search(pt).groups() )

            # Transform given point using provided transformation matrix
            # and convert results tuple of strings and update buffer string
            buffer+="%s,%s " % tuple(map(str, __transformPoint(PtPair,cm)  ))
        
        # Update 'points' attribute of polygon element
        el.attributes['points'].value=buffer
    except:
        print "Error parsing polygon element"

def __fixPolyline(el,cm):
    """
    @type  el: DOM object
    @param el: Polyline SVG element to be modified.
    @type  cm: NumPy array
    @param cm: Transformation matrix to be applied.
    @return  : nothing - only element C{el} is modified.
    
    @requires: Coordinates in 'points' attrubute has to be separated by whitespaces.
    @requires: Correctly defined coordinated eg. C{points='2.3,-5.0 34,5'}.
    
    Funtion transforms all points in polygon one by one using provided transformation matrix.

    @todo    : In final version all polylines should be broken into lines.
               It is important because of further line <-> label assingment.
               Currenty, polylines are not broken into pieces.
    """
    # TODO: Broke polylines into lines

    # Again, we use loop+buffer method:
    # Define empty buffer:
    buffer=""

    # Split "points" attribute vallue it order to get list of points
    PointsTable=split(el.attributes['points'].value)
    
    # Now we transform each point to new coordinates
    for pt in PointsTable:
        # Extract pair of points from string and then 
        # convert results to list
        PtPair=list(re_PointsPair.search(pt).groups() )

        # Transform given point using provided transformation matrix
        # and convert results tuple of strings and update buffer string
        buffer+="%s,%s " % tuple(map(str, __transformPoint(PtPair,cm)  ))
    
    # Update 'points' attribute of polygon element
    el.attributes['points'].value=buffer

def __fixPath(el,cm):
    """
    @type  el: DOM object
    @param el: Path SVG element to be modified.
    @type  cm: NumPy array
    @param cm: Transformation matrix to be applied.
    @return  : nothing - only element C{el} is modified.
    
    @requires: Segments of paths has to be separated by whitespace so we split 'd' string by whitespace.
    
    Funtion transforms all points in path one by one using provided transformation matrix.
    """
    # Create table of path elements by splitting 'd' string
    pathDefinition = el.attributes['d'].value
    
    # Update path definition
    el.attributes['d'].value = fixPathDefinition(pathDefinition, cm) 

def __fixPathDefinition(pathDefinition, cm):
    """
    @type  pathDefinition: string
    @param pathDefinition: path 'd' attribute value to be modified

    @type  cm: NumPy array
    @param cm: Transformation matrix to be applied.

    @return: path difinition transformed using cm matrix
    """
    
    pathPoints = parsePath(pathDefinition)
    for i in range(len(pathPoints)):
        for j in [j for j in range(0, len(pathPoints[i][1:][0]), 2)]:
            pathPoints[i][1:][0][j:j+2] = __transformPoint(pathPoints[i][1:][0][j:j+2], cm)
    return UnparsePath(pathPoints)

def __transformPoint(point,matrix):
    """
    @type   point: list
    @param  point: List/tuple of two elements from which point coordinates could be extracted.
                   Coordinates may be either strings, integers or floats.
                   Mapping all values to floats is applied before calculations.
    @type  matrix: NumPy array 3x3
    @param matrix: Transformation matrix to be applied.
    @return      : List of transformated coordinates (floats): [x',y']
    
    Function simply transforms fiven point from one coodrinates system into another defined by
    transformation matrix.
    """
    #TODO: Implement exception handling
    # Convert passed list to float
    oc=map( float, point)

    # Create vector of three elements
    oc=np.array( [ [oc[0]],[oc[1]],[1] ] )
    
    # Multiply vector by transformation matrix
    nc=np.dot(matrix,oc)
    
    # Extract and return new point coordinates
    return [ nc[0][0], nc[1][0] ]

def __fixHeader(svgdom, pagenumber):
    """
    @type  svgdom: DOM object
    @param svgdom: Whole SVG document
    @type  pagenumber: integer
    @param pagenumber: Number of slide to parse 
    @return      : nothing, C{svgdom} is modified in-place.
    
    Function changes viewPort,viewBox and other defined parameters od SVG document
    in order to correct errors made by converters. Those properties are to be fixed
    before further operations.

    @note: New attributes and their values are defined manually in configuration module.
           Reason is that they differ among atlases and (esspecially) converters.
    """

    # Fix selected elements

    svg=svgdom.getElementsByTagName('svg')[0]
    for attr in CONFIG_AttrToFixSVG.keys():
        if svg.hasAttribute(attr): svg.removeAttribute(attr)
        svg.setAttribute(attr,CONFIG_AttrToFixSVG[attr])
    
    for g in svgdom.getElementsByTagName('g'):
        # Select custom heder
        # Custom header depends on slide number as different slides
        # may be prepared in slightly different way and may require 
        # some custom change
        for rng in range(len(CONFIG_SPECIAL_SLIDE_RANGE)):
            if pagenumber in CONFIG_SPECIAL_SLIDE_RANGE[rng]:
                customAttribFix=CONFIG_AttrToFixG[rng]
                #print pagenumber
                #print customAttribFix
                #print rng
                
                for attr in customAttribFix.keys():
                    if g.hasAttribute(attr): g.removeAttribute(attr)
                    g.setAttribute(attr,customAttribFix[attr])

def fixPathDefinition(pathDefinition, cm):
    """
    @type  pathDefinition: string
    @param pathDefinition: path 'd' attribute value to be modified

    @type  cm: NumPy array
    @param cm: Transformation matrix to be applied.

    @return: path difinition transformed using cm matrix.
    Alias for __fixPathDefinition for external usage
    """
    
    return __fixPathDefinition(pathDefinition, cm)

def transformPoint(point,matrix):
    """
    @type   point: list
    @param  point: List/tuple of two elements from which point coordinates could be extracted.
                   Coordinates may be either strings, integers or floats.
                   Mapping all values to floats is applied before calculations.
    @type  matrix: NumPy array 3x3
    @param matrix: Transformation matrix to be applied.
    @return      : List of transformated coordinates (floats): [x',y']
    
    Function simply transforms fiven point from one coodrinates system into another defined by
    transformation matrix.
    
    Alias for __transformPoint created for external usage.
    """
    return tuple(__transformPoint(point,matrix))

def fixSvgImage(svgdoc, pagenumber=None, fixHeader=True):
    """
    @type  svgdoc: DOM object
    @param svgdoc: Whole SVG document.

    @type  pagenumber: integer
    @param pagenumber: Number of slide to parse.
                       If set to none, this parameter would not be used

    @return      : nothing, C{svgdom} is modified in-place.
    Performs all operations related to fixing SVG file.
    Function fixes header as well applies all transformations for given SVG file.
    """
    # Fix viewbox if needed
    if fixHeader: __fixHeader(svgdoc, pagenumber)
    
    for g in svgdoc.getElementsByTagName('g'):
    
        # Get group transformation matrix:
        if g.hasAttribute("transform"):
            gmatrix=getTransformMatrix(g.attributes['transform'].value)
            g.removeAttribute('transform')
        else:
            gmatrix=np.eye(3)
        
        # Transform elements one by one
        for svgElement in g.childNodes:
            try:
                # TODO: Implement it somehow better. Checking for exception everytime is not good idea
                # TODO: Do it recursively for nested groups:)
                __fixElement(svgElement,gmatrix)
            except:
                continue

        # Remove transformation attribute from g element.

if __name__ == '__main__':
    svgdom = dom.parse(sys.argv[1])
    fixSvgImage(svgdom)
    f=open(sys.argv[2],'w')
    svgdom.writexml(f)
    f.close()

