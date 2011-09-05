#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import colorsys
import os,bar
from base import flatten
from atlas_indexer import barIndexer

class barColor():
    def __init__(self, (r, g, b)):
        self.r=r
        self.g=g
        self.b=b
    
    @classmethod
    def fromInt(barColor, (rInt, bInt, gInt)):
        (r,g,b) = tuple(map(lambda x: x/255., (rInt, bInt, gInt)))
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

import color

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
        zc=color.barColor(colorsys.hsv_to_rgb(0, 1., 1.0))
        ec=color.barColor(colorsys.hsv_to_rgb(.9, 1., 1.0))
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
            newColor = color.get_item_color(span, depth, cola, colb)
            v.fill = newColor.html
        
        for (j, v) in enumerate(elem.children):
            
            if v is not elem.children[0]:
                # For all regular children
                cola = color.barColor.fromHTML(elem.children[j-1].fill)
                colb = color.barColor.fromHTML(v.fill)
            else:
               # For the last child
                cola = color.barColor.fromHTML(v.parent.prevSibling().fill)
                cola = color.barColor.fromHTML(v.fill)
            
            self.setChildColours(v, cola, colb, depth+1)

#-----------------------------------------------------
# Experimental landmark loading routine.
#-----------------------------------------------------

class barLandmarkIndexer(barIndexer):
    def loadSlide(self, slideNumber, cafFilename):
        slideFilename = self.properties['FilenameTemplate'].value % (slideNumber, 0) 
        cafPath = os.path.split(cafFilename)[0]
        slideFullPath = os.path.join(cafPath, slideFilename)
        return  bar.barTracedSlideRenderer.fromXML(slideFullPath)
    
    def _appendLandmarks(self, slideLandmarkList):
        pass
    
    def _appendLandmark(self, landmark, slide):
        pass
    
    def _assignLandmarks(self, landmarks):
        pass
    
    def appendLandmarksFromFile(self, landmarksFilename, cafp):
        def cmpf(x,y):
            if x[1][2] > y[1][2]: return 1
            elif x[1][2] == y[1][2]: return 0
            else: return -1
        lmData = self._loadLandmarksFile(landmarksFilename)
        lmData.sort(cmp = cmpf)
        
        lmToSlide = {}
        # Assign landmarks by nearest slides:
        for lm in lmData:
            cc = lm[1][2]
            dmap = map(lambda x: (x.name, abs(float(x.coronalcoord) - cc)), self.slides.values())
            nSl = min(dmap, key = lambda x: x[1])[0]
            try:
                lmToSlide[nSl].append(lm)
            except:
                lmToSlide[nSl] = [lm]
        
        for (slideNo, lmList) in lmToSlide.iteritems():
            sl = self.loadSlide(slideNo, cafp)
            for lm in lmList:
                lc = slide.toSVGcoordinate( (lm[1][0],lm[1][1]) )
                lmLabel = bar.barSpotLabel(lc, lm[0], lm[0])
                print lmLabel
                sl.addLabel(lmLabel)

            sl.Show()    
        return lmToSlide
    
    def _loadLandmarksFile(self, landmarksFilename):
        fileh = open(landmarksFilename)
        lmData = []
        for line in fileh.readlines():
            line = line.split()
            coords = map(float, line[1].split(","))
            name = line[0]
            shortdesc = line[2]
            longDesc = line[3]
            relURI = line[4]
            lmData.append((name, coords, shortdesc, longDesc, relURI))
            
        return lmData

if __name__ == '__main__':
    pass
