#!/usr/bin/python
# -*- coding: utf-8 -*
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
The module provides a subclass of the L{barIndexer} class necessary to perform
structure reconstruction.

G{importgraph}
"""

from string import *
import sys
import os.path

from bar import barIndexer, barIndexerSlideElement
from bar.base import flatten

def qdist((z1, z2), zRes = None):
    thickness = abs(float(z2 - z1))
    
    if __debug__:
        print "\tqdist: span: ", z1, z2
        print "\tqdist: thickness:", thickness
    
    if not zRes:
        return thickness
    
    qthick    = thickness/float(zRes)
    if __debug__:
        print "\tqdist: qthick: ", qthick
        print "\tqdist: retval:", int(round(qthick))
        print
    
    return int(round(qthick))


class barReconstructorSlideElem(barIndexerSlideElement):
    """
    @ivar z: coordinate of the slide plane
    @type z: float
    
    @ivar idx: index in the slide
    @type idx: int
    
    @ivar span: spatial span of the slide
    @type span: (float, float)
    
    @ivar prev: reference to the slide with the previous index
    @type prev: L{barIndexerSlideElement}
    
    @ivar next: refrence to the slide with the next index
    @type next: L{barIndexerSlideElement}
    """
    
    def __init__(self, **kwargs):
        barIndexerSlideElement.__init__(self, **kwargs)
        
        self.z    = float(self.coronalcoord)
        self.idx  = None
        self.span = None #TODO: Implement as property
        self.prev = None
        self.next = None
    
    def getThickness(self, zRes):
        """
        Calculate thicknes of the slide in using zRes as quantification unit. If
        C{zRes == None}. Distance without applying quantyfication.
        
        @type  zRes: quantification unit
        @param zRes: float
        
        @return: thicknes of the slide in zRes units
        @rtype: int or flaot
        """
        return qdist(self.span, zRes)
    
    def defineSpan(self):
        """
        Calculate spatial span along plane perpendicular to slide plane.
        
        @return: None
        @rtype: None
        """
        #TODO: Implement as cacheable property
        if self.prev == None:
            self.span = self._calculateSlideSpan(\
                    [self.z, self.z, self.next.z])
        
        if self.next == None:
            self.span = self._calculateSlideSpan(\
                    [self.prev.z, self.z, self.z])
        
        if self.prev and self.next:
            self.span = self._calculateSlideSpan(\
                    [self.prev.z, self.z, self.next.z])
    
    def _calculateSlideSpan(self, l):
        """
        Slide spans are calculated using following formulas::
        
            s_n=
            \\left \\langle 
            b_n - \\frac{\\left | b_{n-1} - b_n \\right |}{2}
            ,
            b_n + \\frac{\\left | b_{n} - b_{n+1} \\right |}{2}
             \\right \\rangle
        
        @type  l: list
        @param l: list of three values of bregmas: left (the highest value),
                 middle (slide's bregma coordinate) and right (lowest value)
        @type  eq: Boolean
        @param eq: Determines wether left and rigth span are the same. If True,
                   left and right spans are the same. Option is implemented but
                   not used.
        @return: (tuple) Maximal and minimal bregma coordinate of given slide.
        """
        l.sort()
        dl = abs(l[0]-l[1])/2
        dr = abs(l[1]-l[2])/2
        return tuple(sorted((l[1]-dl,l[1]+dr)))


class barReconstructorIndexer(barIndexer):
    """
    """
    _slideElement = barReconstructorSlideElem
    
    def __init__(self):
        barIndexer.__init__(self)
        
        self.flipAxes = 3*[False]
        
        self.s = []
        self._equalDistribution = False
    
    @classmethod
    def fromXML(cls, filename):
        result = barIndexer._fromXML(cls, filename)
        
        # Create necessary mappings
        result._createMappings()
        return result
    
    def _createMappings(self):
        """
        Creates set of mappings for convinient processing by reconstruction
        procedures.
        
        @rtype: C{None}
        @return: None
        """
        # Dictionary translating name of hierarchy element to corresponing
        # hierarchy ID:
        # Example:
        # {u'csc': u'200003',  u'eml': u'200417', ... }
        # Please note that name of hierarchy element is different thing than
        # name of structure. Those names can be the same but they are two
        # different thigs.
        self.UIDtoHierarchyName =\
             dict(map(lambda (k,v): (v.id, k), self.groups.iteritems()))
        self.HierarchyNametoID  =\
             dict(map(lambda (k,v): (k, v.id), self.groups.iteritems()))
        
        # Dictionary translating name of structure to its ID:
        # Example:
        # {u'100274': u'V1',u'100279': u'PPt', ... }
        # Please note that name of hierarchy element is different thing than
        # name of structure. Those names can be the same but they are two
        # different thigs.
        self.uidToName =\
             dict(map(lambda (k,v): (v.uid, k), self.structures.iteritems()))
        self.structureBoundingBoxes =\
             dict(map(lambda (k,v): (k, v.bbx.boundaries), self.structures.iteritems()))
        
        # Initialize easy-and-fast-to-access aliases to slide elements
        # self.s[n] --> slide of index n
        skeys = sorted(self.slides.keys())
        for i in range(len(skeys)):
                self.s.append(self.slides[skeys[i]])
        
        # Assigns convenience references for each slide element.
        # .idx --> index of given slide; .prev, .next --> references to
        # previous/next slides, None for boundary slides
        for i in range(1,len(self.s)-1):
            self.s[i].idx = i
            self.s[i].prev = self.s[i-1]
            self.s[i].next = self.s[i+1]
        self.s[0].next = self.s[1]; self.s[0].idx = 0;
        self.s[-1].idx = range(len(self.s))[-1]; self.s[-1].prev = self.s[-2]
        
        self.__defineSpan()  
        self.__refCoords = map(float, self.properties['RefCords'].value.strip().split(','))
        self.__defineAxesFlips()
    
    def __defineSpan(self):
        """
        Defines span of all slides. Checks, if all slides have the same
        thickness.
        
        @rtype: None
        @return: None
        """
        map(lambda x: x.defineSpan(), self.s)
        
        # Check if the spacing between slides is constant
        if len(set(map(lambda x: round(x.getThickness(None),5), self.s[1:-1]))) == 1:
           self._equalDistribution = True
           if __debug__:
               print "\t__defineSpan: equal slide distances: ",\
                       self._equalDistribution
    
    def __defineAxesFlips(self):
        """
        Checks if the rasterized slided will be flipped during the
        reconstruction. 

        @rtype: None
        @return: None
        """
        # Axes are flipped if the spatial indexes are in the different direction
        # than image axes or slide indexes
        if self.refCords[2] < 0: self.flipAxes[0] = True
        if self.refCords[3] < 0: self.flipAxes[1] = True
        
        s = self.s
        if s[0].z < s[-1].z : self.flipAxes[2] = True
        
        if __debug__:
            for i in range(3): print "\t__defineAxesFlips: Flip %d: "%i, self.flipAxes[i]
            print
    
    def getUIDsForGivenGroupName(self, topStructureName):
        """
        @type  topStructureID: int
        @param topStructureID: GID of structure element for which UID's will be
                               be collected.
        @return: List of UIDs covered by C{topStructureID} GID.
        
        Extracts set of regular structures ID's (UID's) for given
        C{topStructureID}. 
        
        In other words: 
        topstructure GID -> list of substructures UIDs for C{topStructureID} and
        its child.
        """
        return self.uidList[topStructureName]
    
    def getHierarchyTree(self, root, depth = 100):
        return self.groups[root].getNameFullNameUid(depth = depth)
    
    def getStructureList(self, HierarchyRootElementName):
        """
        @type  HierarchyRootElementName: C{str}
        @param HierarchyRootElementName: Name of root structure
        
        @rtype: C{[str, str, ... ]}
        
        @return: List of of structures (not groups!) covered by given hierarchy
        element.
        """
        structureList = map(lambda x: self.uidToName[x],\
                self.groups[HierarchyRootElementName].uidList)
        return structureList
    
    def getSlidesSpan(self, HierarchyRootElementName):
        """
        @type  HierarchyRootElementName: C{str}
        @param HierarchyRootElementName: Name of root structure
        
        @rtype: (int, int)
        @return:Returns tuple if integers containing first and last containing
        structures covered by given hierarhy elemnt.
        """
        structureList = self.getStructureList(HierarchyRootElementName)
        return self._structList2SlideSpan(structureList)
    
    def _structList2SlideSpan(self, structuresList, rawIndexes = False):
        """
        @type  structuresList: list of strings 
        @param structuresList: list of structure's names for which slide span
                               will be calculated.
        
        @return: (tuple of two integers) (min. slide number, max. slide number)
        
        Function has self explaining name :). Purpose of this function is to
        define slide span (indexes of slides) for set of passed structures.
        """
        # Initialize results set
        returnSet = set()
        
        # Iterate over all names and for each structure extract slides on which
        # this structure appears
        for structureName in structuresList:
            returnSet |= set(self.structures[structureName].slideSpan)
        try:
            retSpan = ( min(returnSet), max(returnSet) )
        except ValueError:
            retSpan = ("Structure not defined on any slide")
        
        if rawIndexes:
            return tuple(map(lambda x: self.slides[x].idx, retSpan))
        else:
            return retSpan
    
    def getZOriginAndExtent(self, slideIdxSpan, zRes, margin, eqSpacing=False):
        """
        Calculates span of the given set of slides in plane perpendicular to the
        slide plane.
        
        @param slideIdxSpan: tuple containing boundary slides indexes.
        @type  slideIdxSpan: (int, int)
        
        @param zRes: Quantification unit of the reconstruction
        @type  zRes: float
        
        @param margin: Number of margin voxels (voxels not filled with the
                       reconstruction) in the z plane.
        @type  margin: int
        
        @param eqSpacing: Flag determining if the provided C{zRes} is equal to
                          the spacing of the all slides. Implies that all the
                          slides are qualy spaced.
        @type  eqSpacing: bool
        """
        n  = slideIdxSpan     # Just an alias
        
        if eqSpacing:
            lZcoord = self.s[n[0]].z
            rZcoord = self.s[n[1]].z
            zOrig = min(self.s[n[0]].z, self.s[n[1]].z)
        else:
            chList = [self.s[n[0]].span[1], self.s[n[0]].span[0],\
                      self.s[n[1]].span[1], self.s[n[1]].span[0]]
            zOrig   = min(chList)
            lZcoord = min(chList)
            rZcoord = max(chList)
        
        # We assume that the origin is located on the point having the lowest
        # coordinates! That is required by the vtkImageData class.
        
        zOrigin = zOrig - zRes*margin
        zExtent = qdist((lZcoord, rZcoord), zRes) + 2*margin
        
        if __debug__:
            print "\tgetZOriginAndExtent: eqSpacing:", eqSpacing
            print "\tgetZOriginAndExtent: slideIdxSpan:", slideIdxSpan 
            print "\tgetZOriginAndExtent: zOrig:",  zOrig 
            print "\tgetZOriginAndExtent: zRes:",  zRes
            print "\tgetZOriginAndExtent: margin:", zRes*margin
            print "\tgetZOriginAndExtent: origin:", zOrigin
            print "\tgetZOriginAndExtent: extent:", zExtent
            print 
        
        return zOrigin, zExtent
    
    def getStructuresListBbx(self, structuresList):
        """
        @param structuresList: List of structure names for which global bounding
                               box will be calculated.
        @type  structuresList: [str, str, ... ]
        
        @return: Merged bounding boxes for all provied structures.
        @rtype: L{barBoundingBox}
        
        Merges bounding boxes of all provided structures one after another.
        """
        bbxList = map(lambda x: self.structures[x].bbx, structuresList)
        return reduce(lambda x,y: x+y, bbxList)        
    
    def getDefaultZres(self):
        """
        Calculate distance between central slide in the stack and the next one.
        This value is considered as default interplane resolution.
        
        @rtype: float
        @return: Default interplane distance (default z resolution)
        """
        # TODO: implement as cacheable property
        s = self.s
        centralSl = s[int(len(s)/2)]
        return abs(centralSl.z - centralSl.next.z)
    
    def __getRefCords(self):
        return self.__refCoords
    
    def __setRefCords(self, value):
        raise ValueError, "Read only property"
    
    refCords = property(__getRefCords, __setRefCords)
