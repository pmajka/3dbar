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
http://www.ekips.org/comp/inkscape/parsepath.php
ekips path parsing code

G{importgraph}
"""
import re
import numpy as np


def lexPath(d):
    """
    returns and iterator that breaks path data
    identifies command and parameter tokens
    """
    offset = 0
    length = len(d)
    delim = re.compile(r'[ \t\r\n,]+')
    command = re.compile(r'[MLHVCSQTAZmlhvcsqtaz]')
    parameter = re.compile(r'(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)')
    while 1:
        m = delim.match(d, offset)
        if m:
            offset = m.end()
        if offset >= length:
            break
        m = command.match(d, offset)
        if m:
            yield [d[offset:m.end()], True]
            offset = m.end()
            continue
        m = parameter.match(d, offset)
        if m:
            yield [d[offset:m.end()], False]
            offset = m.end()
            continue
        #TODO: create new exception
        raise Exception, 'Invalid path data!'


'''
pathdefs = {commandfamily:
    [
    implicitnext,
    #params,
    [casts,cast,cast],
    [coord type,x,y,0]
    ]}
'''

pathdefs = {
    'M':['L', 2, [float, float], ['x','y']],
    'L':['L', 2, [float, float], ['x','y']],
    'H':['H', 1, [float], ['x']],
    'V':['V', 1, [float], ['y']],
    'C':['C', 6, [float, float, float, float, float, float], ['x','y','x','y','x','y']],
    'S':['S', 4, [float, float, float, float], ['x','y','x','y']],
    'Q':['Q', 4, [float, float, float, float], ['x','y','x','y']],
    'T':['T', 2, [float, float], ['x','y']],
    'A':['A', 7, [float, float, float, int, int, float, float], [0,0,0,0,0,'x','y']],
    'Z':['L', 0, [], []]
    }

def parsePath(d):
    """
    Parse SVG path and return an array of segments.
    Removes all shorthand notation.
    Converts coordinates to absolute.
    >>> print parsePath('M0e-100,.1E+1C1,1 2,2 3,3 1 1 2 2e+0 .3e-1 3E-0c2 2 3 3 4 4 4 4 5 5 6 6S100,101. 300,301Z')
    [['M', [0.0, 1.0]], ['C', [1.0, 1.0, 2.0, 2.0, 3.0, 3.0]], ['C', [1.0, 1.0, 2.0, 2.0, 0.03, 3.0]], ['C', [2.03, 5.0, 3.03, 6.0, 4.03, 7.0]], ['C', [8.030000000000001, 11.0, 9.030000000000001, 12.0, 10.030000000000001, 13.0]], ['C', [11.030000000000001, 14.0, 100.0, 101.0, 300.0, 301.0]], ['Z', []]]
    >>> print parsePath('L1 2M3 4')
    Traceback (most recent call last):
    Exception: Invalid path, must begin with moveto.
    >>> print parsePath('m 10,20 L1 2M3 ')
    Traceback (most recent call last):
    Exception: Unexpected end of path
    >>> print parsePath('m 10,20 L1 2M3,4z1,2')
    [['M', [10.0, 20.0]], ['L', [1.0, 2.0]], ['M', [3.0, 4.0]], ['Z', []], ['L', [4.0, 6.0]]]
    >>> print parsePath('m 10,20 L1 2M3,4C1 2')
    Traceback (most recent call last):
    Exception: Unexpected end of path
    >>> print parsePath('1,2hello world')
    Traceback (most recent call last):
    Exception: Invalid path, no initial command.
    >>> print parsePath('M 1000 1000 s100 200 10 10')
    [['M', [1000.0, 1000.0]], ['C', [1000.0, 1000.0, 1100.0, 1200.0, 1010.0, 1010.0]]]
    """
    retval = []
    lexer = lexPath(d)

    pen = (0.0,0.0)
    subPathStart = pen
    lastControl = pen
    lastCommand = ''

    while 1:
        try:
            token, isCommand = lexer.next()
        except StopIteration:
            break
        params = []
        needParam = True
        if isCommand:
            if not lastCommand and token.upper() != 'M':
                raise Exception, 'Invalid path, must begin with moveto.'
            else:
                command = token
        else:
            #command was omited
            #use last command's implicit next command
            needParam = False
            if lastCommand:
                if lastCommand.isupper():
                    command = pathdefs[lastCommand.upper()][0]
                else:
                    command = pathdefs[lastCommand.upper()][0].lower()
            else:
                raise Exception, 'Invalid path, no initial command.'
        numParams = pathdefs[command.upper()][1]
        while numParams > 0:
            if needParam:
                try:
                    token, isCommand = lexer.next()
                    if isCommand:
                        raise Exception, 'Invalid number of parameters'
                except StopIteration:
                                raise Exception, 'Unexpected end of path'
            cast = pathdefs[command.upper()][2][-numParams]
            param = cast(token)
            if command.islower():
                if pathdefs[command.upper()][3][-numParams]=='x':
                    param += pen[0]
                elif pathdefs[command.upper()][3][-numParams]=='y':
                    param += pen[1]
            params.append(param)
            needParam = True
            numParams -= 1
        #segment is now absolute so
        outputCommand = command.upper()

        #Flesh out shortcut notation
        if outputCommand in ('H','V'):
            if outputCommand == 'H':
                params.append(pen[1])
            if outputCommand == 'V':
                params.insert(0,pen[0])
            outputCommand = 'L'
        if outputCommand in ('S','T'):
            params.insert(0,pen[1]+(pen[1]-lastControl[1]))
            params.insert(0,pen[0]+(pen[0]-lastControl[0]))
            if outputCommand == 'S':
                outputCommand = 'C'
            if outputCommand == 'T':
                outputCommand = 'Q'

        #current values become "last" values
        if outputCommand == 'M':
            subPathStart = tuple(params[-2:])
        if outputCommand == 'Z':
            pen = subPathStart
        else:
            pen = tuple(params[-2:])

        if outputCommand in ('Q','C'):
            lastControl = tuple(params[-4:-2])
        else:
            lastControl = pen
        lastCommand = command

        retval.append([outputCommand,params])
    return retval

def UnparsePath(PathParsePath):
    """
    Creates string from L{svgpathparse.parsePath<svgpathparse.parsePath>} function output.
    This step is performed in order to generate C{d} attribute value compatibile with existing syntax.

    @type  PathParsePath: list
    @param PathParsePath: List of path segments parsed by L{svgpathparse.parsePath<svgpathparse.parsePath>}
                          which needs to be converted to string.

    @return: C{d} attrubute value of given path element.
    """
    b=""
    for s in PathParsePath:
        b+=s[0]
        b+=",".join(map(str,s[1]))
        b+=" "
    return b

def chunks(l, n):
    """
    @type  l: list (or other iterable)
    @param l: list that will be splited into chunks

    @type  n: int
    @param n: length of single chunk

    @return: list C{l} splited into chunks of length l

    Splits given list into chunks. Length of the list has to be multiple of
    C{chunk} or exception will be raised.
    """
    return [l[i:i+n] for i in range(0, len(l), n)]

def extractBoundingBox(pathString):
    """
    @type  pathString: string
    @param pathString: path definition according to SVG 1.1 specification

    @return: tuple of four integers: (x1,y1,x2,y2)

    Where x1,y2 are coordinates of top-left corner of bounding box and x2,y2 are
    coordinates of bottom-right corner of bounding box.

    Please note that bounding box is only approximation of actual bounding box
    and may be slightly larger as it is based on extreme coordinated of control
    points creating given path. However, the difference is neglectable.

    Examples:
        >>> print extractBoundingBox("M100,100 L200,200 C300,300 300,100 100,100 Z")
        (99.0, 99.0, 301.0, 301.0)
    """

    pathList = parsePath(pathString)
    pathArr = []

    for pointList in pathList:
        for point in chunks(pointList[1],2):
            pathArr.append(point)

    # Here we have list of string containing pairs of coordinates separated by
    # comma: ['1,1', '3,3', ...]. We need to extract numbers from thode strings
    pathArr = np.array(pathArr)
    pathArr = np.concatenate((np.min(pathArr,0), np.max(pathArr,0))) +  np.array([-1,-1,1,1])
    return tuple(np.around(pathArr))

def mergeBoundingBox(bbox1, bbox2):
    """
    @type  bbox1: tuple of four integers: (x1,y1,x2,y2)
    @param bbox1: definition of first bounding box

    @type  bbox2: tuple of four integers: (x1,y1,x2,y2)
    @param bbox2: definition of second bounding box


    @note: mergeBoundingBox(bbx1, bbx2) = mergeBoundingBox(bbx2, bbx1)
    """
    # Create temporary array from given bounding boxes:
    tempar = np.concatenate( (bbox1, bbox2) ).reshape(2,4)
    minarr = np.min(tempar, axis=0)
    maxarr = np.max(tempar, axis=0)
    return tuple( [minarr[0], minarr[1], maxarr[2], maxarr[3]] )

def parseStyle(s):
    """Create a dictionary from the value of an inline style attribute

    Copyright (C) 2005 Aaron Spike, aaron@ekips.org

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
    """
    if s is None:
      return {}
    else:
      return dict([i.split(":") for i in s.split(";") if len(i)])
def formatStyle(a):
    """Format an inline style attribute from a dictionary

    Copyright (C) 2005 Aaron Spike, aaron@ekips.org

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
    """
    return ";".join([att+":"+str(val) for att,val in a.iteritems()])
