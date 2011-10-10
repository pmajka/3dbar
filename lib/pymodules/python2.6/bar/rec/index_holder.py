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
        
        return int(round(qthick))


class barReconstructorSlideElem(barIndexerSlideElement):
    def __init__(self, *args):
        barIndexerSlideElement.__init__(self, *args)
        
        self.z    = float(self.coronalcoord)
        self.idx  = None
        self.span = None
        self.prev = None
        self.next = None
    
    def getThickness(self, zRes):
        return qdist(self.span, zRes)
    
    def defineSpan(self):
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
        #print tuple(sorted((l[1]-dl,l[1]+dr))) 
        return tuple(sorted((l[1]-dl,l[1]+dr)))
        

barIndexer._slideElement = barReconstructorSlideElem

class barReconstructorIndexer(barIndexer):
    """
    @ivar _visibleGID: GIDs of visible in CAF slides hierarchy tree elements
    @type _visibleGID: set(int)
    """
    def __init__(self):
        barIndexer.__init__(self)
        
        self.volumeConfiguration = {}
        self._visibleGID = None
        self.flipAxes = 3*[False]
    
    def _findVisibleGIDs(self):
        """
        Generate C{self.L{_visibleGID}} for the CAF index.
        """
        self._visibleGID = frozenset(self.groups[name].id for name, uidList\
                                     in self.uidList.iteritems()\
                                     if len(uidList) > 0)
    
    def unfoldSubtrees(self, rootStructures, defaultDepth=0, leavesOnly=False):
        """
        @param rootStructures: names of root elements of hierarchy subtrees or
                               pairs of root element name and depth of the subtree
        @type rootStructures: iterable([str | (str, int), ...])
        
        @param defaultDepth: the default depth of hierarchy subtrees
        @type defaultDepth: int
        
        @param leavesOnly: indicates if only the leaf nodes has to be returned
        @type leavesOnly: bool
        
        @return: names of hierarchy subtree tree nodes
        @rtype: set([str, ...])
        """
        def unfoldSubtree(arg):
            # check the argument type
            if type(arg) is tuple:
                root, depth = arg
            else:
                root, depth = arg, defaultDepth
            
            hierarchyTree = self.getHierarchyTree(root, depth)
            return set(self.names(hierarchyTree, leavesOnly=leavesOnly))
        
        return reduce(lambda x, y: x | y, (unfoldSubtree(z) for z in rootStructures))

    def names(self, tree, leavesOnly=False):
        """
        @param tree: hierarchy tree
        @type tree: see L{getHierarchyTree} for details
        
        @param leavesOnly: True if requested to iterate over names of the
                           leaves of the hierarchy tree only, False otherwise
        @type leavesOnly: bool
        
        @return: iterator over names of the nodes of a given C{tree}
        @rtype: generator
        """
        if len(tree) > 1:
            # tree is not a leaf
            for subtree in tree[1]:
                for name in self.names(subtree, leavesOnly):
                    yield name
            
            if leavesOnly:
                # do not iterate over the root element name of the tree
                return
        
        if tree[0][2] in self._visibleGID:
            yield tree[0][0]

    
    @classmethod
    def fromXML(cls, filename):
        result = barIndexer._fromXML(cls, filename)
        
        # Create necessary mappings
        result._createMappings()
        result._findVisibleGIDs()
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
        
        # Initialize empty data structures. C{slidesBregmas} hold information
        # about slide bregma coordinates, slide numbers and slide spans, all in
        # following form
        # Bregma: { Consecutive slide number: its bregma coordinate }
        # SlideNumber: [ list of numbers of consecutive slides ]
        # in general it is possible that slide enumeration starts from number
        # other than 1.
        # SlideSpans { Consecutive slide number: tuple (min border, max border) }
        # eg: 
        # 'Bregma': {1: 22.5, 2: 21.6, 3: 20.25, 4: 19.8, ...
        # 'SlideNumber': [1,2,3,4,...]
        # 'SlideSpans' {1: (22.949999999999999, 22.050000000000001),
        #               2: (22.050000000000001, 20.925000000000001),...
        
        self.s = []
        skeys = sorted(self.slides.keys())
        for i in range(len(skeys)):
                self.s.append(self.slides[skeys[i]])
        for i in range(1,len(self.s)-1):
            self.s[i].idx = i
            self.s[i].prev = self.s[i-1]
            self.s[i].next = self.s[i+1]
        self.s[0].next = self.s[1]
        self.s[0].idx = 0;
        self.s[-1].idx = range(len(self.s))[-1]
        self.s[-1].prev = self.s[-2]
        map(lambda x: x.defineSpan(), self.s) 
        
        self.__refCoords =  map(float, self.properties['RefCords'].value.strip().split(','))
        self.__defineAxesFlips()
        
        if __debug__:
#           print >>sys.stderr, map(lambda sl: sl.span, self.s)
#           print >>sys.stderr, map(lambda sl: sl.z, self.s)
#           print >>sys.stderr, map(lambda sl: sl.name, self.s)
            print >>sys.stderr, self.flipAxes
    
    def __defineAxesFlips(self):
       if self.refCords[2] < 0: self.flipAxes[0] = True
       if self.refCords[3] < 0: self.flipAxes[1] = True
       
       s = self.s
       if s[0].z < s[-1].z : self.flipAxes[2] = True
       
       print s[0].z,s[-1].z
    
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
    
    def getZOrigin(self, slideNumberSpan, zRes, margin, eqSpacing = False):
        n  = slideNumberSpan                              # Just alias
        
        if eqSpacing:
            zOrig = min(self.s[n[0]].z, self.s[n[1]].z)
        else:
            zOrig = min([self.s[n[0]].span[1],\
                         self.s[n[0]].span[0],\
                         self.s[n[1]].span[1],\
                         self.s[n[1]].span[0]])
        
        retval = zOrig - zRes*margin
        
        if __debug__:
            print "\tgetZOrigin: eqSpacing:", eqSpacing
            print "\tgetZOrigin: slides:", slideNumberSpan
            print "\tgetZOrigin: zOrig:",  zOrig 
            print "\tgetZOrigin: zRes:",  zRes
            print "\tgetZOrigin: margin:", zRes*margin
            print "\tgetZOrigin: final:", retval
        return retval
    
    def getZExtent(self, slideNumberSpan, zRes, margin, eqSpacing = False):
         
        n  = slideNumberSpan                              # Just alias
        
        if eqSpacing:
            lZcoord = self.s[n[0]].z
            rZcoord = self.s[n[1]].z
        else:
            chList = [self.s[n[0]].span[1],\
                      self.s[n[0]].span[0],\
                      self.s[n[1]].span[1],\
                      self.s[n[1]].span[0]]
            lZcoord = min(chList)
            rZcoord = max(chList)
        
        retval = qdist((lZcoord, rZcoord), zRes) + 2*margin
        
        if __debug__:
            print "\tgetZExtent: eqSpacing:", eqSpacing
            print "\tgetZExtent: slideNumberSpan:", slideNumberSpan
            print "\tgetZExtent: extent coords:", lZcoord, rZcoord
            print "\tgetZExtent: zRes:", zRes
            print "\tgetZExtent: margin:", margin
            print "\tgetZExtent: retval:", retval
        
        return retval
    
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
        
        s = self.s
        centralSl = s[int(len(s)/2)]
        return abs(centralSl.z - centralSl.next.z)
    
    def __getRefCords(self):
        return self.__refCoords
    
    def __setRefCords(self, value):
        raise ValueError, "Read only property"
    
    def __getVisibleGIDs(self):
        if self._visibleGID == None:
            self._findVisibleGIDs()
        return self._visibleGID
    
    def __setVisibleGIDs(self, value):
        raise ValueError, "Read only property"
    
    refCords = property(__getRefCords, __setRefCords)
    visibleGIDs = property(__getVisibleGIDs, __setVisibleGIDs)
