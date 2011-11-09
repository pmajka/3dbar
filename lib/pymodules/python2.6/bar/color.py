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
The module provides classes necessary to handle basic structure colour processing.

G{importgraph}
"""
import sys
import colorsys
import numpy as np
from base import flatten
from atlas_indexer import barIndexer

def intColourToFloat(colour, maxValue = 255.):
    return tuple(x / maxValue for x in colour)

def floatColourToInt(colour, maxValue = 255):
    return tuple(int(x * maxValue) for x in colour)

class barColor():
    def __init__(self, (r, g, b)):
        self.r=r
        self.g=g
        self.b=b
    
    @classmethod
    def fromInt(barColor, (rInt, bInt, gInt)):
        (r,g,b) = intColourToFloat((rInt, bInt, gInt))
        return barColor((r,g,b))
    
    @classmethod
    def fromHTML(barColor, colorstring):
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return barColor.fromInt((r, g, b))
     
    @classmethod
    def fromHSVTuple(cls, (h,s,v)):
        return cls(colorsys.hsv_to_rgb(h,s,v))

    def __str__(self):
        return str(self())
    
    def __call__(self):
        return self.__getValues()
    
    def __getInt(self, x):
        return int(x*255.)
    
    def __getIntTuple(self):
        return tuple(map(self.__getInt, self()))
    
    def __getHTMLcolor(self):
        return '#%02X%02X%02X' % self.rgb
    
    def __getValues(self):
        return (self.r, self.g, self.b)

    def __getHSVTuple(self):
        return colorsys.rgb_to_hsv(*self())
     
    rgb = property(__getIntTuple)
    html= property(__getHTMLcolor)
    hsv = property(__getHSVTuple)


BAR_HIERARHY_ROOT_ELEM_COLOUR = barColor((0.4, 0.4, 0.4))
BAR_MAX_DEPTH = 6

def get_item_color(ic,d, depth):
    if depth == 0:
        return BAR_HIERARHY_ROOT_ELEM_COLOUR
    else:
        h = ic
        s = 0.3+0.7*d#1. - (depth -1)*.5 / BAR_MAX_DEPTH 
        v = 0.5 + 0.5*float(depth) / 8
        return barColor(colorsys.hsv_to_rgb(h,s,v))

#-----------------------------------------------------
# Experimental version of automatic color assgnment
#-----------------------------------------------------

class barColorIndexer(barIndexer):
    """
    Class enabling automated color assignment basing on provided structure
    hierarchy.
    """
    def getSpan(self, elem):
        """
        @return: number of nodes in elem tree
        """
        return len(flatten(elem.getChildList(depth=1)))
    
    def recolor(self):
        """
        Function invoking customizable recoloring procedure.
        """
        pass
    
    def setColors(self):
        brainRootElem = self.hierarchyRootElementName
        b=self.groups[brainRootElem]
        
        # this is something like initialization step
        # Each child of root element has span of colours proportional to the
        # number of structures that it covers.
        self.ccmap =  dict(\
            map(lambda x:\
            (x.name, self.getSpan(x)), self.groups.itervalues()))
        
        zc=0.1
        ec=.9
        self.setChildColours(b, (zc, ec, 0.5), depth=0)
        
        # Define new color mapping and use it
        newColorMap =\
         dict(map(lambda x: (x.name, x.fill), self.groups.values()))
    
    def setChildColours(self, elem, span, depth = 0):
        d = span[2]
        s = span[0:2]
        ic = sum(list(s))/2.
        #ic = s[1]
        print elem.name, s,ic, depth
        elem.fill = get_item_color(ic, d, depth).html
        
        if elem.children==[]: return
       
        n = sorted([x.name for x in elem.children])
        l = np.array(map(lambda x: self.ccmap[x], n))
        l = np.cumsum(l/float(sum(l)))
        r = abs(s[1]-s[0])
        #print r, s[0]
        lk = (l-l[0])*r+s[0]
        ll = l*r + s[0]
        #ll = l
        nn = [self.groups[x] for x in n]
        k = zip(nn, zip(lk,ll,l))
        
        for (c, v) in k:
            self.setChildColours(c, v, depth+1)

if __name__ == '__main__':
    pass
