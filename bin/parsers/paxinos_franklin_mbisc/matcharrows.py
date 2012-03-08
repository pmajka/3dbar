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
Module for adjusting labels positions. Module also clears drawing from unnecessary elements.
Details are provided in partucular functions.
G{importgraph}
"""

import xml.dom.minidom as dom
import sys
from string import *
from math import sqrt
from config import *

def _getAllArrowlines(svgdoc):
    """
    @type  svgdoc: DOM object
    @param svgdoc: Whole SVG document
    @return      : List of L{getArrowDetalils<getArrowDetalils>} results.

    Finds all lines which could be arrows - those lines which do not belong to any brain structure.
    Lined are usually distinquished by stroke color.
    """
    # Empty list of lines
    ArrowsTable=[]

    # On this moment of parsing SVG file there should be only two types of lines: Brain lines
    # and arrowlines.
    for el in svgdoc.getElementsByTagName('line'):
        if isArrowline(el): ArrowsTable.append( getArrowDetalils(el) )

    return ArrowsTable

def __isBrainLine(el):
    if el.hasAttribute('stroke') and el.getAttribute('stroke')==CONFIG_BRAIN_LINE_STROKE:
        return True
    else:
        return False

def isArrowline(el):
    """
    @type  el: DOM elemnet
    @param el: Line SVG object
    @return  : Boolean

    Determines if given line element is arrowline using
    L{CONF_ARROWLINE_ELEMENT<config.CONF_ARROWLINE_ELEMENT>} definition.
    """
    if el.attributes['stroke'].value==CONFIG_ARROW_LINE_STROKE: return True
    return False
    
def getArrowDetalils(el):
    """
    @type  el: DOM elemnet
    @param el: Line SVG object
    @return  : List of tuples: C{[('x1','y1'),('x2','y2')]}

    Extract coordinates of ends of given arrowline (or more generally - of any given
    SVG line object)
    """

    # List of attributes to extract
    attribs=[('x1','y1'),('x2','y2')]

    # List to be returned
    ret=[]
    
    # Extract attribute's values map them at floats and append to ret list
    for at in attribs:
        ret.append( tuple( map(lambda x: float(el.attributes[x].value),at  ))  )
    return ret

def extractTextnodeData(TextNode):
    """
    @type  TextNode: DOM elemnet
    @param TextNode: test DOM object - label which denotes the structure.

    Extracts coordinates of given text labes, its values and estimates bouding box
    of label. Text size is assumed to be 9px but should be extracted from given label.
    It is clear that this function is not fully optimized but it should work fine.

    @return: ((x,y),text,(x,y),(xt,yt),(x,yt),(xt,y)), where last four pairs are
             coordinates of roughly estimated bounding box of given label.

    @todo: This function should be optimized and generate bounding box for given
           label but I don't knot how to do it yet.
    """

    x,y=float(TextNode.attributes['x'].value),float(TextNode.attributes['y'].value)
    tl=len(TextNode.firstChild.nodeValue)
    tsize=9. #TODO: Make it more general perhaps CONFIG_LABEL_FONT_SIZE constant
    xt=int(x+tl*tsize/1.9)  # xt - xTop extimated X of top right corner of bounding box
    yt=int(y-tsize/1.5)     # yt - yTop extimated Y of top right corner of bounding box

    return (\
        (x,y),\
        str(TextNode.firstChild.nodeValue),\
        (x,y),(xt,yt),(x,yt),(xt,y)
        )

def extractTextNodesInfo(svgdom):
    """
    @type  svgdom: DOM object
    @param svgdom: Whole SVG document

    Creates lists of information extracted from all text labels in document via
    via L{extractTextnodeData<extractTextnodeData>}.

    @return: List of L{extractTextnodeData<extractTextnodeData>} results.
    """

    # Initialize empty array for data extracted from text labels
    TextNodes=[]

    # Update sro, 25 sie 2010, 18:47:06 CEST
    # Iterate over text elements and extract information
    for el in svgdom.getElementsByTagName('text'):
        # In some cases (usually when text elements are modified
        # manually) some errors may appear. In such case faulty text
        # element is removes and warning message is displayed.
        try:
            TextNodes.append(extractTextnodeData(el))
        except (TypeError, AttributeError):
            _pringTextNodeParsingWarning()
            el.parentNode.removeChild(el)
    return TextNodes

def _pringTextNodeParsingWarning():
    """
    Prints message about text node format incompatibility. Function invoked
    when L{extractTextnodeData<extractTextnodeData>} raises an exception.

    @return: None
    """
    message = "\t\tOne or more labels has incompatibile format which cannot be parsed\n"
    message +="\t\tAnd such labels will be removed leaving 'Unlabelled' areas.\n"
    message +="\t\tPerhaps those labels were created or modified manually.\n"
    message +="\t\tIn order to correct this error please recreate foul labels\n"
    message +="\t\tby copying labels created in first parsing.\n"
    print >>sys.stderr, "\033[0;31m" + message + "\33[m"
    raw_input('Press any key to confirm.')

def _MatchArrows(svgdoc,text,arrows):
    """
    Function performs matching labels with corresponding arrows basing on provided coordinates
    of arrowlines and extimated bounding boxes of labes.
    
    Mathing of performed in following way:
        1. Take coordinates of end of arrowline 
        2. Find label which is closet to 'left'. 
        3. Find label which is closet to 'right'.
        4. Choose end for which distance is smaller.
        5. Clone label and move the clone to the other end.

    @type  svgdoc: DOM object
    @param svgdoc: Whole SVG document
    @type    text: List of C{((x,y),text,(x,y),(xt,yt),(x,yt),(xt,y))} tuples.
    @param   text: Result of L{extractTextNodesInfo<extractTextNodesInfo>}
    @type  arrows: List
    @param arrows: List of coordinates of all arrowlines extracted via
                   L{_getAllArrowlines<_getAllArrowlines>} function
    @return      : Nothing. svgdoc is modified in-place.
    

    """
    # XXX Highly experimantal code!!!i
    # XXX Needs a lot of refactoring

    # Element which holds all of labels and arrowlines elements. 
    g=svgdoc.getElementsByTagName('g')[0]

    #list of new nodes 
    nodes_to_append=[]

    # List of nodes to remove
    nodes_to_remove=[]

    for a in arrows:
        # Get label which is closest to "left" and "right" end of arrowline
        ClosestLabels=map( lambda x: getClosestLabel(text,x), a)
        darr=ClosestLabels

        # Check, which distance is smaller
        if  darr[0][1]<=darr[1][1]:
#           print darr[0][0]
            # Create svg element at coordinates pointed by the other side of the arrow
            for el in svgdoc.getElementsByTagName('text'):
                if extractTextnodeData(el)[:2] == darr[0][0]:
                    # Now, we have found the proper svg text node
                    # We need to clone it and palce in a[1] coordinates
                    newnode=el.cloneNode(deep=True)
                    newnode.attributes['x'].value=str(a[1][0])
                    newnode.attributes['y'].value=str(a[1][1])
                    nodes_to_remove.append(el)
                    nodes_to_append.append(newnode)
        else:
#           print darr[1][0]
            for el in svgdoc.getElementsByTagName('text'):
                if extractTextnodeData(el)[:2] == darr[1][0]:
                    # Now, we have found the proper svg text node
                    # We need to clone it and palce in a[1] coordinates
                    newnode=el.cloneNode(deep=True)
                    newnode.attributes['x'].value=str(a[0][0])
                    newnode.attributes['y'].value=str(a[0][1])
                    nodes_to_append.append(newnode)
                    nodes_to_remove.append(el)

    for i in nodes_to_append:
        g.appendChild(i)

# Remove initial labels
    for el in svgdoc.getElementsByTagName('text'):
        if el in nodes_to_remove: el.parentNode.removeChild(el)

def _appendVBrainStructure(svgdom):
    """
    @type  svgdom: DOM object
    @param svgdom: Whole SVG document

    @return: Nothing, only svgdom is modified in-place

    Function appends virtual brain structure which corresponds to area
    outside the brain. Virtual structure is palced at C{CONF_BRAIN_STRUCTURE_COORDS}.
    vBrain structure would be used later to reconstruct whole brain surface.
    """
    # Assuming there is only one g element in SVG file.
    # Getting topmost g elements which holds all text labels
    g=svgdom.getElementsByTagName('g')[0]

    # Getting text object (only for cloning)
    el=svgdom.getElementsByTagName('text')[0]

    # Create virtual structure vBrain
    brainLabel = el.cloneNode(deep=True)
    brainLabel.attributes['x'].value=str(CONF_BRAIN_STRUCTURE_COORDS[0])
    brainLabel.attributes['y'].value=str(CONF_BRAIN_STRUCTURE_COORDS[1])
    brainLabel.firstChild.nodeValue='vBrain'

    # Put vBrain into document structure.
    g.appendChild(brainLabel)

def _cleanRestOfFile(svgdoc):
    """
    @type  svgdoc: DOM object
    @param svgdoc: Whole SVG document
    @return      : Nothing. svgdoc is modified in-place.

    Clean rest of document from all non-brain information
    and converts brain lines to paths.
    Particulary clears lines which shows label's placement (arrowlines).
    Also clears all other lines which are not structure contorus.

    All lines which are considered as brain-lines (=those lines which
    describes contours of strucutures) are converted to paths.
    After applying this function there should be no line elements in SVG document.
    """
    # Iterate thorought all line elements
    for el in svgdoc.getElementsByTagName('line'):
        # Remove non-brain elements
        if not __isBrainLine(el):
            el.parentNode.removeChild(el)
        else:
            # Convert line elements to equvelant paths.
            convertLineToPathElement(svgdoc,el)

def convertLineToPathElement(svgdoc,el):
    """
    @type  svgdoc: DOM object
    @param svgdoc: Whole SVG document

    @type  el: DOM element
    @param el: line element to be converted to path element

    @return      : Nothing. svgdoc is modified in-place.

    Converts SVG line element to equivalent path element. Copies all style.
    """
    # Renember coordinates (sCrds - starting coordinates, eCrds - end coordinates)
    sCrds=(el.getAttribute('x1'),el.getAttribute('y1'))
    eCrds=(el.getAttribute('x2'),el.getAttribute('y2'))

    # Generate d attribute value
    dString='M%s,%s L%s,%s ' % (sCrds[0], sCrds[1], eCrds[0], eCrds[1])
    
    # Create new DOM element and assign such attributes as path definition and styles
    newPath=svgdoc.createElement('path')
    newPath.setAttribute('d',dString)
    for attrib in ['stroke','stroke-width']:
        newPath.setAttribute(attrib ,el.getAttribute(attrib))

    # Insert new element into DOM structure and remove old line element
    el.parentNode.appendChild(newPath)
    el.parentNode.removeChild(el)

def _debugAddTextBoundingBoxes(svgdom, text):
    """
    @type  svgdom: DOM object
    @param svgdom: Whole SVG document

    @type  text: DOM elemnet
    @param text: test DOM object - label which denotes the structure.

    @return: Nothing. C{svgdom} is modified-in place.

    Helper/debug function. Creates bounding boxes of text labels for given text element.
    """
    g=svgdom.getElementsByTagName('g')[0]
    for t in text:
        newel=svgdom.createElement('rect')
        newel.setAttribute('x',str(t[4][0]))
        newel.setAttribute('y',str(t[4][1]))
        newel.setAttribute('width',str( abs(  t[2][0]-t[3][0])   ))
        newel.setAttribute('height',str(abs(  t[2][1]-t[3][1])   ))
        newel.setAttribute('stroke','red')
        g.appendChild(newel)

def getClosestLabel(text, end):
    """
    @type    text: List of C{((x,y),text,(x,y),(xt,yt),(x,yt),(xt,y))} tuples.
    @param   text: Result of L{extractTextNodesInfo<extractTextNodesInfo>}
    @type     end: Tuple of two floats.
    @param    end: Coordinates of end of arrow.

    Finds label which is closest to given coordinates (C{end})

    @return      : C{(((x,y),text), dist)}. Where C{(x,y)} are coordinates of closest
                   text label, C{text} - obvious, C{dist} - distance.
    """

    # Iterate over labels and calculate distance to each label
    # And choose the minimal one

    CurrentMinDist=1000
    for t in text:
        # t[2:4] - coordinates of bounding box ((x,y),(x,y))
        NewMinDist=calculateDistanceFromBoundingBox(end,t[2:4])
        if NewMinDist < CurrentMinDist:
            CurrentMinDist=NewMinDist
            RetVal=(t[:2], CurrentMinDist)
    return RetVal

def calculateDistanceFromBoundingBox(p,r):
    """
    @type  p: Tuple of floats (x,y)
    @param p: Point from which we want to calculate distance to rectangle.
    @type  r: Tuple of two tuples ((x,y),(x,y))
    @param r: Values (floats) of points which spans rectangle.
    
    @return      : (float) Minimum distance from point to rectangle.

    Calculate minimum distance from point given by (p1,p2)
    From rectanagle spanned on (r1,r2) and (r1',r2')
    Using formula:
    
    C{MD=Sum[   xi^2      ,i=1,2]}

    C{xi^2= ri-pi  if  ri > pi}

    C{pi-r'i if  ri'< pi}

    C{0  otherwise}
    
    Examples:   
        >>> print calculateDistanceFromBoundingBox((0,0),((1,1),(2,2)))
        1.4142135623730951
        >>> print calculateDistanceFromBoundingBox((0,0),((1,2),(3,4)))
        2.2360679774997898

    @see    : http://www.cs.mcgill.ca/~cs644/Godfried/2005/Fall/fzamal/concepts.htm
    """
    sum=0
    for i in range(2):
        if   r[0][i] > p[i]: sum+=(r[0][i]- p[i]    )**2; continue
        elif r[1][i] < p[i]: sum+=(p[i]   - r[1][i] )**2; continue

    return sqrt(sum)

def _embedTracelevel(svgdoc, ReversedTracelevelList=None):
    """
    Embeds information about tracelevels. To be clear: tracelevel is number of
    consecutive applications of MIN filter to the image in order to fill gaps.
    The larger tracelevel is, the larger gaps will be filled.
    Gap filling itself is performed by L{class_fill.GrowFill<class_fill.GrowFill>}
    class and C{ReversedTracelevelList} is a feedback information generated
    by tracing procedure.

    If C{ReversedTracelevelList} is {None} (it means that this function was executed before
    launching tracing procedure), tracing information is treaten as initial and dummy tracelevel
    id assigned (-1). Otherwise tracelevel is extracted from C{ReversedTracelevelList}.

    @type  svgdoc: DOM object
    @param svgdoc: Whole SVG document

    @type  ReversedTracelevelList: list of integers
    @param ReversedTracelevelList: holds information about tracelevel for consecutive
                                   text elements. Ie. first element holds tracelevel assigned
                                   to first text element in svgdoc, second element for second
                                   text element etc. When not provided dummy list with -1 is
                                   used instead.
    @return: nothind. C{svgdoc} is modified in-place.
    """
    
    if not ReversedTracelevelList:
        for TextNode in svgdoc.getElementsByTagName('text'):
            if not TextNode.hasAttribute('bar:growlevel'):
                TextNode.setAttribute('bar:growlevel','-1')
    else:
        TextNodesList=svgdoc.getElementsByTagName('text')
        #print len(TextNodesList)
        #print len(ReversedTracelevelList)
        #print ReversedTracelevelList
        # Unfortunately we have to use iterator :(
        i=0
        for i in range(len(ReversedTracelevelList)):
            # Froce setting attribute, do not check if the attribute already exists
            TextNodesList[i].setAttribute('bar:growlevel', str(ReversedTracelevelList[i]))

def symmetrizeLabels(svgdom, offsets):
    """
    @param offsets: Tuple of two pairs of valued used for transformation
                    do stereotaxic coordinates: ((a,b),(c,d))
    @type  offsets: floats

    @type  svgdom: DOM object
    @param svgdom: Whole SVG document

    Iterate through all structures in doument and mirrors selected labels.
    Mirroring conditions:

        1. Labels is single
        2. Labels has no simmilar labels in neighbourhood
    """

    # Extract information abotu all text labels
    text=extractTextNodesInfo(svgdom)

    # Create dictionary which allows to quckly get information
    # about structure with given name
    # dict[structure name] -> list of structures with given name
    structDict={}
    for i in text:
        structName=i[1]         # Just convinient alias
        if not structName in structDict: structDict[structName]=[]
        structDict[structName].append(i)
    #if __debug__: print >>sys.stderr,structDict

    # Now we iterate over each label looking for its symmetric element
    for i in text:
        structName=i[1]
        # Read, how many structures with the same name are on the slide
        structNumber=len(structDict[structName])
        if structNumber%2==1 and\
            (not structName in CONF_STRUCTURES_NON_SYMMETRIC):
            # If there is only one instance, we should mirror it
            _mirrorLabel(i, offsets, svgdom)

def _mirrorLabel(label, offsets, svgdom):
    """
    @type  svgdom: DOM object
    @param svgdom: Whole SVG document

    @param offsets: Tuple of two pairs of valued used for transformation
                    do stereotaxic coordinates: ((a,b),(c,d))
    @type  offsets: floats

    @type  label: nested list
    @param label: List with information about label: C{((xcord, ycord),text,(estimated bounding boc)}

    @return: nothing, only svgdom is modified in-place
    """

    # Extract stereotaxic transformation coefficients
    ((a,b),(c,d))=offsets

    # Make some calculation and assingments
    structName=label[1]
    oldStCoords=_stereotaxic(label[0], offsets)        # Get stereotaxic coordinates
    newDwXCoord=( (-oldStCoords[0]-d )/c, label[0][1]) # Drawing (-XoldSt) coordinate

    print "Symmetrizing structure:\t%s" % structName

    #XXX retrieving negative coordinates causes error!
    if newDwXCoord<=0:
        print >>sys.stderr,"\[\033[1;34m\]Error encountered while symmetrizing structure %s, nagative coordinate %f appeared. Skipping.\[\033[0m\]"\
                % (structName,newStXCoord)
        return

    # Clone 'whatever' text node - we just need a text DOM object
    # which we can customize
    # We customize cloned label and then we insert it into document strucutre
    newText=svgdom.getElementsByTagName('text')[0].cloneNode(deep=True)
    newText.firstChild.nodeValue=structName
    newText.setAttribute('x',str(newDwXCoord[0]))
    newText.setAttribute('y',str(newDwXCoord[1]))
    svgdom.getElementsByTagName('g')[0].appendChild(newText)

def _stereotaxic((x,y), offsets):
    """
    Transforms given image coordinates to stereotaxic coordinates.
    (x,y) coordinates has to be passed as a tuple of two values.

    @param offsets: Tuple of two pairs of valued used for transformation
                    do stereotaxic coordinates: ((a,b),(c,d))
    @type  offsets: floats

    @type  x      : float
    @type  y      : float
    @param x      : x coordinate 
    @param y      : y coordinate to transform
    @return       : Coordinates in 3D stereotaxic coordinates: (x',y')
    """

    ((a,b),(c,d))=offsets
    return (c*x+d, a*y+b)

def DoMatch(svgdoc):
    """
    Function which manages labels adjustment process. Performs following actions:

            1. Gather information about arrowlines (=lines which starts near label and points at structure)
            2. Extracts coordinates and labesl from text elements (structure labes)
            3. Adjust coorinates of labels by matching arrowlines with corresponding labes.
            4. Removes all lines from document
            5. Some minor modificartions
    
    After all those steps, documnet consists only of path (structures contours) and text (labesl) elements
    and is ready pof tracing.

    @type  svgdoc: DOM object
    @param svgdoc: Whole SVG document

    @return: Updated information about labels coordinates (=labels coordinates after adjusting)
             using outpu format of L{extractTextnodeData<extractTextnodeData>}. Modifies svgdoc in-place also.
    """

    arrows=_getAllArrowlines(svgdoc)
    text=extractTextNodesInfo(svgdoc)
    _MatchArrows(svgdoc, text, arrows)
    _appendVBrainStructure(svgdoc)
    _cleanRestOfFile(svgdoc)
#   _debugAddTextBoundingBoxes(svgdoc,text)

    # Embed initial tracelevels in document structure.
    _embedTracelevel(svgdoc)

if __name__=='__main__':
    pass
