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
import os
import colorsys
import numpy as np
from math import sqrt, ceil
from random import seed, shuffle
from base import flatten, barCafSlide
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

def get_item_color(h, s, v, depth):
    if depth == 0:
        return BAR_HIERARHY_ROOT_ELEM_COLOUR
    
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
        Estimate span of spectrum required by hierarchy element.

        @param elem: hierarchy element for which spectrum span is estimated
        @type elem: C{self.{L{_groupElement}}

        @return: estimated spectrum span for element L{elem}.
        @rtype: float
        """
        if elem.children == []:
            return 0.

        result = sum(self.getSpan(x) for x in elem.children)
        if any(x.uid for x in elem.children): #elem.uid:
            result += 1

        return result
    
    def recolor(self):
        """
        Recolor CAF slides.
        """
        pattern = self.properties['FilenameTemplate'].value
                               
        for i in self.slides:
            # assumed version == 0
            version = 0
            filename = os.path.join(self.cafDirectory,
                                    pattern % (i, version))

            barCafSlide.fromXML(filename).recolor(self.colorMapping).writeXMLtoFile(filename)
    
    def setColors(self):
        """
        Assign colours to the hierarchy groups elements automatically.
        """
        brainRootElem = self.hierarchyRootElementName
        b = self.groups[brainRootElem]
        
        # this is something like initialization step
        # Each descedant of root element has span of sprctrum somehow related
        # to the structures it covers.
        self.ccmap = dict((x.name, self.getSpan(x))\
                          for x in self.groups.itervalues()\
                          if x.uidList != [])
        
        # hue circle is now complete
        zc = 0.0
        ec = 1.0
        self.setChildColours(b, (zc, ec), 0, 0)
        
    def setChildColours(self, elem, span, es, ev, depth = 0):
        """
        Assign colours to elements of hierarchy tree.

        @param elem: hierarchy tree
        @type elem: C{self.{L{_groupElement}}

        @param span: beginningg (included) and end (excluded) of the spectrum
                     (hue) span
        @type span: (float, float)

        @param es: saturation of colour assigned to L{elem} root node
        @type ev: float

        @param ev: value of colour assigned to L{elem} root node
        @type ev: float

        @param depth: DO NOT TOUCH

        @note: Colours are defined in HSV colourspace. Range of accepted
               values is 0-1.
        """
        # colour the root element
        eh = (span[0] + span[1]) / 2. #put the root hue in the middle of
                                      #a spectrum span
        elem.fill = get_item_color(eh, es, ev, depth).html
        
        if elem.children == []:
            # no children - nothing to do
            return


        # set all alements without spectrum span assigned white
        for x in elem.children:
            if x.name not in self.ccmap:
                # no span -> no colour
                # and it propagates to children because span propagates
                # to parents (so if parent has no span assigned nor have its
                # children)
                self.setChildColours(x, (0,0),0,1, depth - 1)

        # the code below needs some initiations
        if depth == 0:
            # at the beginning there was a word...
            # ...and the word initized the random number generator
            seed(elem.name)

        # use is a fraction of spectrum span inherited by root node children
        use = 0.9

        # r is hierarchy tree spectrum span size
        r = span[1] - span[0] #

        # sorted names of hierarchy groups elements of significant spectrum span
        names = sorted(x.name for x in elem.children if self.ccmap.get(x.name))

        # sorted names of hierarchy groups elements of insignificant spectrum
        # span (OMG)
        childless = sorted((x for x in elem.children if self.ccmap.get(x.name) == 0),
                           key = lambda x: x.name)

        # l is normalised spectrum span estimation vector for hierarchy groups
        # in names
        l = np.array([sqrt(self.ccmap[x]) for x in names])

        # sl is normalisation divisor for l
        sl = float(sum(l))

        if sl != 0:
            if childless != []:
                # if any children of insignificant spectrum span estimation
                # is present, some spectrum span is reserved for them by
                # incrementation of the normalisation divisor
                sl += 1

            l = l / sl

        else: #l == []
            sl = 1.

        # if any group has significant spectrum span assigned...
        n = len(names)
        if n > 0:

            # ll is normalised vector of spectrum span beginning for hierarchy
            # groups in names
            ll = np.cumsum(l) - l

            # lhb and lhr are (respectively) vectors of beginning and end of
            # spectrum span for hierarchy groups in names
            lhb = span[0] + ll * r
            lht = lhb + l * r * use

            # list of hierarchy nodes and spectrum span assigned to them...
            groups = zip([self.groups[x] for x in names],
                         lhb,
                         lht)
            # ...shuffled in order to break h:s and h:v corelation in s while
            # s and v values distribution
            shuffle(groups)

            # minimum s and v values (it might happen that v < v0, so keep
            # v0 large enough for that case)
            s0 = 0.3
            v0 = 0.5

            # steps computed in a magic way that covers almost half of
            # s:v area
            stepV = (0.5 / ceil(sqrt(n))) * (1.0 - v0)
            stepS = (1. / ceil(n / ceil(sqrt(n)))) * (1.0 - s0)

            # initial s and v values
            v = 1.
            s = 1.

            for (c, hb, ht) in groups:
                if v < v0:
                    # debug message
                    print "v < v0! : %f < %f" % (v, v0)

                self.setChildColours(c, (hb, ht), s, v, depth - 1)
    
                s -= stepS / v # the lower v, the greater s distance
                               # is necessary to keep the chroma distance
                if s < s0:
                    v -= stepV
                    s = 1.

        # ...and if any has insignificant span assigned
        n = len(childless)
        if n > 0:
            # redundant code - see comments in the if above
            s0 = 0.3
            v0 = 0.5

            stepV = (0.5 / ceil(sqrt(n))) * (1.0 - v0)
            stepS = (1. / ceil(n / ceil(sqrt(n)))) * (1.0 - s0)

            # distribute spectrum span reserved for hierarchy groups of
            # insignificant span
            childlessH = [span[0] + r * (sl - 1.) / sl + r * use / sl * (2. * i + 1.) / 2 / n for i in xrange(n)]
            groups = zip(childless, childlessH)
            shuffle(groups)

            v = 1.
            s = 1.
            for c, h in groups:
                if v < v0:
                    # debug message
                    print "v < v0! : %f < %f" % (v, v0)

                c.fill = get_item_color(h, s, v, depth - 1).html
    
                s -= stepS / v
                if s < s0:
                    v -= stepV
                    s = 1.


if __name__ == '__main__':
    pass
