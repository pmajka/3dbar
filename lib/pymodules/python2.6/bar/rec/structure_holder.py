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
The module provides class necessary to perform structure reconstruction.

G{importgraph}
"""

import sys
import os
import numpy
import zipfile
import tempfile
import xml.dom.minidom as dom

import bar.rec.index_holder as index_holder

from PIL import Image 
from bar import barTracedSlideRenderer
from bar import barBoundingBox

# DO NOT CHANGE!
ENABLE_EXPERIMENTAL_FEATURES = False

class VTKStructuredPoints():
    def __init__(self, (nx, ny, nz)):
        self.vol=numpy.zeros( (nx, ny, nz), dtype=numpy.uint8 )
        self.size=self.vol.shape
    
    def setOrigin(self, (x, y, z)):\
        self.origin=(x, y, z)
    
    def setSpacing(self, (sx, sy, sz)):
        self.spacing=(sx, sy, sz)
    
    def setSlice(self, slideIndex, sliceArray):
        self.vol[:, :, slideIndex]=sliceArray[:,:,0]
    
    def prepareVolume(self, indexholderReference):
        # Optional reverse of z axis:
        #if indexholderReference.flipAxes[2]:
        #print >>sys.stderr, "\tFlipping z"
        #self.vol=self.vol[:,:,::-1]
        
        # Obligatory (required by vtk):
        self.vol= numpy.swapaxes(self.vol, 1,0)
    
    def saveVolume(self, filename):       
        # create a compressed zip archive instead
        zip = zipfile.ZipFile(filename, mode="w", compression=zipfile.ZIP_DEFLATED)
        # Place to write temporary .npy files
        #  before storing them in the zip
        (fh, filepath) = tempfile.mkstemp('.npy', 'numpy')
        os.close(fh)
        
        # the list containing (filename, numpy array) pairs
        # controls execution of subsequent loop
        mainloop = [('volume.npy', self.vol),
                    ('origin.npy', numpy.array(self.origin)),
                    ('spacing.npy',numpy.array(self.spacing))]
        
        for (name, data) in mainloop:
            # add 'data' to the archive 'zip' as 'name'
            fh = open(filepath, "wb")
            numpy.save(fh, data)
            fh.close()
            zip.write(filepath, arcname=name)
        zip.close()
        
        # remove temporary file
        os.remove(filepath)
    
    @classmethod
    def loadVolume(cls, filename):
        arch = numpy.load(filename)
        result = cls((1, 1, 1))
        result.vol = arch['volume']
        result.size = result.vol.shape
        result.origin = tuple(arch['origin'].tolist())
        result.spacing = tuple(arch['spacing'].tolist())
        return result


class structureHolder():
    """
    Main class for generating and processing slides.
    """
    clsIndexHolder = index_holder.barReconstructorIndexer
    clsSlide = barTracedSlideRenderer
    
    def __init__(self, indexFilename, tracedFilesDirectory):
        
        self.ih = self.clsIndexHolder.fromXML(indexFilename)
        self.tracedFilesDirectory =\
                os.path.join(tracedFilesDirectory,
                        self.ih.properties['FilenameTemplate'].value)
        
        self.refDimestions =\
                (float(self.ih.properties['ReferenceWidth'].value),
                 float(self.ih.properties['ReferenceHeight'].value))
        
        self.CurrentStructureProperties = {}
        self.csp = self.CurrentStructureProperties #alias
    
    def __initializeVolume(self):
        """
        Calculates dimenstions, allocates memory of volume and creates
        vtkStructure for managing defined volume.
        
        @return: None.
        """
        
        # Calculate volume dimensions basing on set of slides and
        # (implicitly) values defined in C{indexHolder.volumeConfiguration}
        
        if round(self.ih.volumeConfiguration['zRes'] - self.getDefaultZres(),5) == 0:
            eqSpacing = True
        else:
            eqSpacing = False
         
        zSize = self.ih.getZExtent( self.csp['slides'],\
                self.ih.volumeConfiguration['zRes'],
                self.ih.volumeConfiguration['zMargin'], eqSpacing)
        
        dm = self.ih.volumeConfiguration['PlaneDimensions']  # Bitmap size
        volumeDimensions = (dm[0], dm[1], zSize)
        
        self.ih.volumeConfiguration['zSize'] = zSize
        
        print >>sys.stderr, "Defining volume for structure:"
        print >>sys.stderr, "\tDimensions: (%d, %d, %d)" % volumeDimensions
        
        # Create class for managing defined volume
        self.StructVol = VTKStructuredPoints(volumeDimensions)
        
        # Define origin and spacing for created volume
        origin, spacing = self.__defineOriginAndSpacing()
        
        # Put origin and spacing into volume
        self.StructVol.setOrigin(origin)
        self.StructVol.setSpacing(spacing)
    
    def __defineOriginAndSpacing(self):
        """
        Makes some preparations to calculating origin and spacing of volume.
        Actial calculation are performed by
        L{__calcOriginAndSpacing<__calcOriginAndSpacing>} function.
        
        @return: Origin of vtk volume and spacing between consecitive pixels.
        """
        
        # Aliases
        zRes = self.ih.volumeConfiguration['zRes']
        rc  = self.ih.refCords
        bo  = self.ih.volumeConfiguration['BoundingBoxOffset']
        ppd = self.ih.volumeConfiguration['FullPlaneDimensions']
        bb  = self.ih.volumeConfiguration['zOrigin']
        rf  = self.ih.volumeConfiguration['ReduceFactor']
        
        # Define scaling in x,y,z direction. Scaling in x and y are calculated
        # by taking scaling defined in svg file and multiplying it by some
        # resolution-dependent factor. Coronal scaling is taken directly from
        # coronal resolution.
        sx, sy, sz = rc[2]*rf, rc[3]*rf, zRes
        
        # Coordinates of upper left image corner and maximal bregma coordinate.
        # tx,ty are taken from AlignerReferenceCoords while tz is calculated by
        # taking bregma coordinate of "left" boundary of first slice of
        # structure.
        tx, ty, tz  = rc[0] , rc[1], bb
        
        # Full width and height of image (the save values which are passed to
        # rederer
        w, h      = ppd[0], ppd[1]
        
        # Bounding box coordinates. Those coordinates are taking into accounts
        # fact that renderer module flips resulting image upside down to fit it
        # into vtk reruirements (by = h-bo[3]). Bz is calculated basing on
        # minimum bregma coordinate ("right" bregma coordinate of slide with
        # maximum index): bz = -bb[1]+margin.
        if sx > 0: bx =     bo[0]
        else:      bx = w - bo[2]
        
        if sy > 0: by =     bo[1]
        else:      by = h - bo[3]
        
        bz = 0
        
        return self.__calcOriginAndSpacing((sx, sy, sz), (tx, ty, tz), (w, h), (bx,by, bz))
    
    def __calcOriginAndSpacing(self, (sx, sy, sz), (tx, ty, tz), (w, h), (bx, by, bz)):
        """
        Calculates origin of volumetric coordinate system and spacing in x,y and
        z dimensions.
        
        Function takes following arguments:
        
            1. C{(sx, sy, sz)} - scaling in x,y,z directions. All scaling values
               has to be positive, otherwise significant error will appear.
            2. (tx, ty, tz)    - Reference oordinates of the upper-left image corner in
               stereotactic coordinate system (ty, tx) and maximum value of
               bregma coordinate (tz).
            3. (w, h) - width and height if the image.
            4. (bx, by, bz) - bounding box corner calculates in some VERY
               SPECIAL described elsewhere. If you want to understand it -
               follow documentation of L{__defineOriginAndSpacing<__defineOriginAndSpacing>}
        
        Origin of the volumetric coordinate system is located in point where all
        coordinates have their lowest values. That happens because spacing has to be
        posivite every coordinate is "more positive" that previous. In such case we
        start from the lowest coordinate possible.
        
        What do we do in this function:
        
            1. Define origin of coordinate system in lower left corner (0,h)
               image coordinates.
            2. Define a scaling and translation matrices taking into account
               stereotaxic axes direction
            3. Define matrix describing bounding box.
            4. Use all matrices defined above to calculate new origin.
        
        @return: ((numpy 3x1 array),(3x1)):  stereotactic coordinates of vtk coordinate
                 system origin and spacing in x,y and z directions.
        """
        
        # Initial origin of coordinate system in image coordinates (it is
        # located in lower left corner of the image.
        O = numpy.array([0, 0, 0, 1]).reshape(4,1)
        
        # Matrix transforming from image coordinate system to stereotaxic
        # coordinate system:
        # The exact form of T and S matrices depends on direction of axes.
        # Esspecialy direction of Y axis:
        
        if sx > 0 and sy > 0:
            O = numpy.array([0, 0, 0, 1]).reshape(4,1)
            B = numpy.array( [[1,0,0,bx],[0,1,0,by],[0,0,1,bz],[0,0,0,1]])
            T = numpy.array( [[1 ,0,0,tx],[0,1 ,0,ty],[0,0,1,tz],[0,0,0,1]])
            S = numpy.array( [[sx,0,0,0 ],[0,sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
        elif sx > 0 and sy < 0:
            O = numpy.array([0, 0, 0, 1]).reshape(4,1)
            B = numpy.array( [[1,0,0,bx],[0,1,0,by],[0,0,1,bz],[0,0,0,1]])
            S = numpy.array( [[sx,0,0,0 ],[0,-sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
            T = numpy.array( [[1 ,0,0,tx],[0,1 ,0,sy*h+ty],[0,0,1,tz],[0,0,0,1]])
        elif sx < 0 and sy > 0:
            O = numpy.array([0, 0, 0, 1]).reshape(4,1)
            B = numpy.array( [[1,0,0,bx],[0,1,0,by],[0,0,1,bz],[0,0,0,1]])
            S = numpy.array( [[-sx,0,0,0 ],[0,sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
            T = numpy.array( [[1 ,0,0,w*sx+tx],[0,1 ,0,ty],[0,0,1,tz],[0,0,0,1]])
        elif sx < 0 and sy < 0:
            O = numpy.array([0, 0, 0, 1]).reshape(4,1)
            B = numpy.array( [[1,0,0,bx],[0,1,0,by],[0,0,1,bz],[0,0,0,1]])
            S = numpy.array( [[-sx,0,0,0 ],[0,-sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
            T = numpy.array( [[1 ,0,0,w*sx+tx],[0,1,0,h*sy+ty],[0,0,1,tz],[0,0,0,1]])
        
        # Origin after including bounding box
        Op = numpy.dot(T,numpy.dot(S,numpy.dot(B,O)))
        
        if __debug__:
            print >>sys.stderr, "Origin in stereotaxic coordinates:"
            print >>sys.stderr, O
            print >>sys.stderr, "Bounding box transformation matrix:"
            print >>sys.stderr, B
            print >>sys.stderr, "Reference scaling matrix:"
            print >>sys.stderr, S
            print >>sys.stderr, "Reference translation matrix:"
            print >>sys.stderr, T
            print >>sys.stderr, "Final origin of stereotaxic coordinate system:"
            print >>sys.stderr, Op
        
        origin  = (Op[0,0], Op[1,0], Op[2,0])
        # We take absolute value of scalings and coronal resosolution as
        # VTK handles negavite scaling very poor.
        spacing = (abs(S[0,0]),  abs(S[1,1]),  abs(S[2,2]))
        return (origin, spacing)
    
    def __processModelGeneration(self):
        """
        Performs all operation related to rasterizing slides and
        putting this rasterized data into volume:
        
            1. Define volume
            2. Define indexes of slides that will be parsed
            3. Parse all slides one by one
        
        @return: None
        """
        self.__initializeVolume()
        
        self.tempCentralPlanes = []   # For collecting central planes indexes
        
        firstSlideIndex = self.csp['slides'][0]    # Index of first slide  
        lastSlideIndex  = self.csp['slides'][1] +1 # Index of last slide +1
        
        # Iterate trought all slides and process with 
        # volume extraction from each slide:
        self.slideNumbersRange = range(firstSlideIndex, lastSlideIndex)
        
        Oz = self.StructVol.origin[2]
        ez = self.StructVol.size[2]
        sz = self.StructVol.spacing[2]
        print (Oz,sz,ez)
        
        z = numpy.array(map(lambda x: sz*(x+0) + Oz, range(0, ez)))
        zi= numpy.array(range(0, ez))
        print z
        ass = {}
        css = {}
        
        for s in map(lambda x: self.ih.s[x], range(firstSlideIndex, lastSlideIndex)):
            mask = (0>=numpy.round(s.span[0]-z,5)) & (0<=numpy.round(s.span[1]-z,5))
            #print "z >", s.span[0], "& z <=", s.span[1]
            #print list(zi[mask])
            #print list(z[mask])
            ass[s.name] = (list(zi[mask]), list(z[mask]))
        print ass
        
        raw_input()
        for (slideNo, (planes,coor)) in ass.iteritems():
            print slideNo
            print planes
            print coor
            self.__processSingleSlide(slideNo, planes)
     
    def __processSingleSlide(self, slideNumber, planes):
        # Another set of usefull aliases:
        
        print >>sys.stderr,"Processing slide number:\t%d" % slideNumber
#       
        structuresToInclude = self.csp['StructuresList']  
        fpd = self.ih.volumeConfiguration['FullPlaneDimensions']
        bbo = self.ih.volumeConfiguration['BoundingBoxOffset']
        
        maskedSlide = self._loadSlide(slideNumber, structuresToInclude, version=0)
        maskedSlide.getMask()
        
        # Determine if, the rendered plane shoud be flipped in x and y axis.
        # It should be done if
        otype = 'rec'
        if self.ih.flipAxes[0]:
            otype+='1'
            if __debug__: print >>sys.stderr, '\tFlip x'
        if self.ih.flipAxes[1]:
            otype+='1'
            if __debug__: print >>sys.stderr, '\tFlip y'
        
        volumeFromOneSlice = maskedSlide._renderSvgDrawing(\
                                maskedSlide.getXMLelement(),
                                renderingSize=fpd,
                                boundingBox=bbo,
                                otype=otype)
        
        for z in planes:
            self.StructVol.setSlice(z, volumeFromOneSlice)
    
    def _loadSlide(self, slideNumber, structuresToInclude = None, version = 0):
        tracedSlideFilename = self.tracedFilesDirectory % (slideNumber,version)
        testslide = self.clsSlide.fromXML(tracedSlideFilename)
        maskedSlide = testslide.getStructuresSubset(structuresToInclude)
        return maskedSlide
    
    def __flushCache(self):
        del self.StructVol
        del self.tempCentralPlanes
        self.csp = {}
    
    def __initModelGeneration(self, coronalResolution):
        mx = self.ih.refCords[2] / float(coronalResolution)
        my = self.ih.refCords[3] / float(coronalResolution)
        multiplier = abs(mx)
        self.ih.volumeConfiguration['ReduceFactor'] = 1./multiplier
        
        self.ih.volumeConfiguration['FullPlaneDimensions']=\
        (self.refDimestions[0] * multiplier, self.refDimestions[1] * multiplier)
        
        boundingBox = self.ih.volumeConfiguration['StructureBoundingBoxes']
        boundingBox*=multiplier
        if not ENABLE_EXPERIMENTAL_FEATURES:
            boundingBox.extend((-1,-1,1,1))
        
        self.ih.volumeConfiguration['BoundingBoxOffset'] = boundingBox
        
        bb = boundingBox
        self.ih.volumeConfiguration['PlaneDimensions']   = (bb[2]-bb[0],bb[3]-bb[1])
    
    def __getStructureList(self, HierarchyRootElementName):
        stlist = self.ih.getStructureList(HierarchyRootElementName)
        self.csp['StructuresList'] = stlist
        self.csp['slides'] = self.ih._structList2SlideSpan(stlist,rawIndexes=True)
        
        bbx = self.ih.getStructuresListBbx(stlist)
        
        # ------------------ Experimental ---------------------
        if ENABLE_EXPERIMENTAL_FEATURES:
            xbbx, ybbx = tuple(map(int, self.refDimestions))
            bbx = barBoundingBox((1, 1, xbbx-1, ybbx-1))
            self.csp['slides'] =\
                    (self.ih.slidesBregmas['SlideNumber'][0],\
                     self.ih.slidesBregmas['SlideNumber'][-1])
        # ------------------ Experimental ---------------------
        
        self.ih.volumeConfiguration['StructureBoundingBoxes'] = bbx

        #XX: REPLACE WITH EQUAL THICKNESS
        print round(self.ih.volumeConfiguration['zRes'] - self.getDefaultZres(),5)
        if  round(self.ih.volumeConfiguration['zRes'] - self.getDefaultZres(),5) == 0:
            eqSpacing = True
        else:
            eqSpacing = False
        
        self.ih.volumeConfiguration['zOrigin'] =\
                self.ih.getZOrigin(self.csp['slides'],\
                self.ih.volumeConfiguration['zRes'],
                self.ih.volumeConfiguration['zMargin'],\
                eqSpacing)
    
    def handleAllModelGeneration(self,\
            HierarchyRootElementName,\
            xyRes, zRes,\
            VolumeMargin = 10):
        
        #TODO: Remove: self.ih.volumeConfiguration['AlignerReferenceCoords'] = self.ih.refCords
        self.ih.volumeConfiguration['zRes']    =  zRes
        self.ih.volumeConfiguration['zMargin'] = VolumeMargin
        self.__getStructureList(HierarchyRootElementName)
        self.__initModelGeneration(xyRes)
        self.__processModelGeneration()
    
    def getSlidesSpan(self, HierarchyRootElementName):
        return self.ih.getSlidesSpan(HierarchyRootElementName)
    
    def getDefaultZres(self):
        return self.ih.getDefaultZres()
