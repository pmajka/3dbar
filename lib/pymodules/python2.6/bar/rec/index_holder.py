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

from bar import barIndexer

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
        self.slidesBregmas={ 'Bregma':{}, 'SlideNumber':[], 'SlideSpans':{} }
        self.slidesBregmas['Bregma'] =\
             dict(map(lambda (k,v): (k, float(v.coronalcoord)), self.slides.iteritems()))
        self.slidesBregmas['SlideNumber'] = self.slides.keys()
        self.slidesBregmas['SlideNumber'].sort()
        self.__defineSlicesSpan()
        
        self.__refCoords =  map(float, self.properties['RefCords'].value.strip().split(','))
        self.__defineAxesFlips()
        
        if __debug__:
            print >>sys.stderr, self.slidesBregmas['SlideSpans']
            print >>sys.stderr, self.slidesBregmas['Bregma']
            print >>sys.stderr, self.slidesBregmas['SlideNumber']
            print >>sys.stderr, self.flipAxes
    
    def __defineAxesFlips(self):
        if self.refCords[2] < 0: self.flipAxes[0] = True
        if self.refCords[3] < 0: self.flipAxes[1] = True
        
        n = self.slidesBregmas['SlideNumber']
        b = self.slidesBregmas['Bregma']
        if  b[n[0]] > b[n[-1]]: self.flipAxes[2] = True
    
    def __defineSlicesSpan(self):
        """
        Calculate span for each slide. By span I mean minimal and maximal bregma
        coordinate on which given slide exists::
        
            min bregma     slide bregma     max bregma
            |                   ||            |
            |<------------------||----------->|
            |                   ||            |
            <--------------------------------->
                               slide span
        
        @return: None
        """
        #alias: sn - slideNumbers
        sN = self.slidesBregmas['SlideNumber']
        
        #alias: sp - slideSpans. We will will this dictionary with data
        sp = self.slidesBregmas['SlideSpans']
        
        #alias: b - Bregma
        b = self.slidesBregmas['Bregma']
        
        #alias csp - calculateSlideSpan
        csp = self._calculateSlideSpan
        
        # We need to manually set slide spans for first, last and last but one
        # slide
        sp[sN[0]]  = csp( map( lambda x: b[x], [sN[1] , sN[0] , sN[1]]  ) )
        sp[sN[-2]] = csp( map( lambda x: b[x], [sN[-3], sN[-2], sN[-1]] ) )
        sp[sN[-1]] = csp( map( lambda x: b[x], [sN[-2], sN[-1], sN[-2]] ) )
        
        # For other slide we do it in a loop
        for seg in  listPartition(sN, 3):
            sp[ seg[1] ] = csp( map( lambda x: b[x], seg ) )
    
    def _calculateSlideSpan(self, l, eq=False):
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
        
        dl = (abs(l[0]-l[1])/2)
        if eq:
            dr=dl
        else:
            dr=(abs(l[1]-l[2])/2)
         
        return tuple(sorted((l[1]+dl,l[1]-dr)))
    
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
    
    def _bregmaToVolumeCoordinates(self, bregmaCoordinate):
        """
        @type  bregmaCoordinate: float
        @param bregmaCoordinate: bregma coordinate to be converted to volume
               coordinate using defined coronal resolution.
        
        @return: bregmaCoordinate in volumetric units.
        """
        return bregmaCoordinate / self.volumeConfiguration['CoronalResolution']
    
    def _scaleBregmaToCoronalBasic(self, bregmaCoordinate):
        """
        @type  bregmaCoordinate: float
        @param bregmaCoordinate: bregma coordinate to be rescaled
        @return: (integer) coronal plane index according to scaling and offset
        
        Converts bregma coordinate to pixel number in coronal plane.
        It is very important function widely used in other functions :)
        
        Following steps are performed in order to rescale given bregma
        coordinate:
            
            1. Total number of coronal planes C{vc} is defined. C{vc} is
                dependent from coronal resolution and calculated by:
                volumetric plane index of "left" boundary of first slide - 
                volumetric plane index of"right" boundary of last slide
                
                C{v_c( s(1)^L) - v_c( s(n)^P)}
            
            2. Offset and scaling are calculated in the way that leftmost value (max
               bregma) is transformed o 0 coronal plane index while rightmost
               (min bregma coordinate) is transformed to last (tcp) coronal plane.
               So the lower bregma coordinate, the higher coronal plane index.
        
        Please note that calculations abov do not include margins!
        """
        r = self.volumeConfiguration['CoronalResolution']
        vc = self._bregmaToVolumeCoordinates
        sp = self.slidesBregmas['SlideSpans']
        n  = self.slidesBregmas['SlideNumber']
        b  = self.slidesBregmas['Bregma']
        
        # offset:
        o = 1./r * sp[n[0]][0] 
        
        # scaling (if slides are in descending/descending order)
        if b[n[0]] > b[n[-1]]: a = -1./r
        else: a = 1./r
        
        return int( a * bregmaCoordinate + o)
    
    def adjustedScaling(self, bregmaCoordinate, slideIndexSpan):
        """
        Calculates adjusted scaling. Adjustd scaling means that volume margins
        and current structure slide span are taken into account. Adjustmets are
        made by shifting regular scaling and adding margin:
        
        C{ adj.scaling = reg.scaling(bregmaCoord) - reg.scaling(leftBoundary)+margin}
        
        So the leftmost bregma value is translatesd to m coronal plane (not m+1
        as coronal planes starts from 0)::
        
            asc(sll)=m
        
        @type  bregmaCoordinate: float
        @param bregmaCoordinate: bregma coordinate to be rescaled
        
        @type  slideIndexSpan: tuple of two integers
        @param slideIndexSpan: slide span of structure: (lowest slide number,
                               highest slide number).
        
        @return: Adjusted coronal plane index.
        """
        
        slb = self.slidesBregmas['SlideSpans']
        sc  = self._scaleBregmaToCoronalBasic
        m   = self.volumeConfiguration['VolumeMargin']
        
        # Get bregma coordinates of extreme slide numbers:
        # slide number -> ( b_left in mm, b_right in mm) 
        slideCoronalSpan = map( lambda x: slb[x], slideIndexSpan)
        
        scp = slideCoronalSpan # Just convinient alias
        
        return +sc(bregmaCoordinate) - sc(scp[0][0]) +m
    
    def defineVolumeSize(self, slideNumberSpan):
        """
        Defines size of volumetrix box for given structure taking into account
        slide span of given structure and margins. Number of voxels in x and y
        is taken directly from bitmap resolution while number of coronal planes
        is calculated basing on slide span and margins.

        @type  slideNumberSpan: tuple of two integers
        @param slideNumberSpan: min and max slide number of given structure
        
        @return: tuple of three integers with numbers ov voxels in x,y and z
                 dimensions
        """
        
        sc = self._scaleBregmaToCoronalBasic              # Alias
        sp = self.slidesBregmas['SlideSpans']             # Alias
        n  = slideNumberSpan                              # Just alias
        dm = self.volumeConfiguration['PlaneDimensions']  # Bitmap size
        m  = self.volumeConfiguration['VolumeMargin']     # Margin in vol units.
        
        leftBregmaValueIndex  = sc(sp[n[0]][0])           # left plane index 
        rigthBregmaValueIndex = sc(sp[n[1]][1])           # right plane index
        
        # Number of voxels in coronal plane:
        # Total number of planes is difference of indexes + 1 + 2*margin
        coronalDimension = abs(leftBregmaValueIndex - rigthBregmaValueIndex)+1 + 2*m
        return (dm[0], dm[1], coronalDimension)
    
    def setCoronalBoundaryIndexes(self, slideNumberSpan):
        """
        @type  slideNumberSpan: tuple of two integers
        @param slideNumberSpan: min and max slide number of given structure
        
        @return: tuple of two integers: (adj. coronal plane index of left plane,
        adj. coronal plane index of right plane). Left plane is a plane with
        max. bregma coordinate while right coronal plane is plane with min.
        bregma coordinate.
        
        Defines size of volumetrix box for given structure taking into account
        slide span of given structure and margins. Number of voxels in x and y
        is taken directly from bitmap resolution while number of coronal planes
        is calculated basing on slide span and margins.
        """
        sc = self._scaleBregmaToCoronalBasic              # Alias
        sp = self.slidesBregmas['SlideSpans']             # Alias
        n  = slideNumberSpan                              # Just alias
        leftBregmaValueIndex  = sc(sp[n[0]][0])           # left plane index 
        rigthBregmaValueIndex = sc(sp[n[1]][1])           # right plane index
        
        return  tuple(sorted((leftBregmaValueIndex, rigthBregmaValueIndex)))
    
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
    
    def _structList2SlideSpan(self, structuresList):
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
        return retSpan
    
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
        
        slidesNumber = len(self.slidesBregmas['SlideNumber'])
        firstSlideNo = self.slidesBregmas['SlideNumber'][0]
        b = self.slidesBregmas['Bregma'] # Just an alias
        
        centralSlNo = int(slidesNumber/2) + firstSlideNo
        return abs(b[centralSlNo] - b[centralSlNo+1])
    
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
    
def listPartition(sourceList, length = 0):
    """
    @type  sourceList: list
    @param sourceList: list to be splited
    
    @type  length: integer
    @param length: Length of single piece.
    
    @return: (list) C{sourceList} splitted into pieces of length C{length}.
    
    Splits list C{sourceList} into elements of length C{length}.
    If list cannot be splitted into pieces of equal length, last piece is
    shorter. If C{length} is not provided exeption will appear and function
    would not work properly.
    
    Please look at the examples to be sure how this function works.
    
        >>> listPartition(range(10),0)
        [[], [], [], [], [], [], [], [], [], []]
        
        >>> listPartition(range(10),1)
        [[0], [1], [2], [3], [4], [5], [6], [7], [8]]
        
        >>> listPartition(range(10),2)
        [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8]]
        
        >>> listPartition(range(10),6)
        [[0, 1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8]]
    """
    resultingList = []
    
    for i in range(len(sourceList) - length):
        resultingList.append( sourceList[i:i+length])
    
    return resultingList
