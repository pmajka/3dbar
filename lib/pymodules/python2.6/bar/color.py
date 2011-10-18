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


BAR_HIERARHY_ROOT_ELEM_COLOUR = barColor((0.83, 0.84, 0.82))
BAR_MAX_DEPTH = 6


def splitRainbow(border):
    return barColor(colorsys.hsv_to_rgb(border, 1., 1.0))

def interpolate_colors(colora, colorb, percentage):
    color = barColor((0,0,0))

    (a,b,c) = colora.hsv
    (d,e,f) = colorb.hsv
    #print >>sys.stderr, a,d, percentage, abs(d-a), abs(d-a)*percentage
    #print >>sys.stderr, colorb.hsv 
    #print >>sys.stderr, abs(a-d)*percentage
    diff = a+abs(d-a)*percentage
    print >>sys.stderr, diff
    
    color =  barColor.fromHSVTuple((diff,b,c))
    return color

def get_item_color(relPos, depth, parentColor, nextColor):
    
    if depth == 0:
        return BAR_HIERARHY_ROOT_ELEM_COLOUR
    else:
        percentage = relPos
        (r,g,b) = interpolate_colors(parentColor, nextColor, percentage)()
        
        #print >>sys.stderr, (r,g,b)
        h,s,v = colorsys.rgb_to_hsv(r,g,b)
        #intensity = 1. - (depth -1)*.5 / BAR_MAX_DEPTH 
        saturation = 1. - (depth -1)*.5 / BAR_MAX_DEPTH 
        #v *= intensity
        s *= saturation
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
        return len(flatten(elem.getChildList(depth=999)))
    
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
        zc=barColor(colorsys.hsv_to_rgb(0, 1., 1.0))
        ec=barColor(colorsys.hsv_to_rgb(.9, 1., 1.0))
        self.setChildColours(b, zc, ec, depth=1)
        
        # Define new color mapping and use it
        newColorMap =\
         dict(map(lambda x: (x.name, x.fill), self.groups.values()))
    
    def setChildColours(self, elem, cola, colb, depth = 0):
        groupLen = float(self.getSpan(elem))*1.0
        
        # Cannot set children colors when there are no children
        if elem.children == []:
            return
        
        span = 0
        for (j, v) in enumerate(elem.children):
            span += float(self.getSpan(v))/groupLen
            #print >>sys.stderr, span
            newColor = get_item_color(span, depth, cola, colb)
            v.fill = newColor.html
        
        for (j, v) in enumerate(elem.children):
            
            if v is not elem.children[0]:
                # For all regular children
                cola = barColor.fromHTML(elem.children[j-1].fill)
                colb = barColor.fromHTML(v.fill)
            else:
               # For the last child
                cola = barColor.fromHTML(v.parent.prevSibling().fill)
                cola = barColor.fromHTML(v.fill)
            
            self.setChildColours(v, cola, colb, depth+1)

if __name__ == '__main__':
    pass
