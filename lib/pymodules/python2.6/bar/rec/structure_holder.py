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
        #+1 is here because we want to have unit margin with zeros
        # around whole structure
        self.vol[:, :, slideIndex]=sliceArray[:,:,0]
    
    def __getVolume(self):
        #self.vol= numpy.swapaxes(self.vol, 0,2)
        #(x0,y0,z0)...(xnx,y0,z0)...(x0,y1,z0)

        zlist=range(self.size[2])
        ylist=range(self.size[1])
        xlist=range(self.size[0])
        self.vol=self.vol[:,:,::-1]
        
        self.vol= numpy.swapaxes(self.vol, 1,0)
    
    def prepareVolume(self):
        self.__getVolume()

    def saveVolume(self, filename):
        # create an uncompressed archive
        #numpy.savez(filename,
        #            volume=self.vol,
        #            origin=numpy.array(self.origin),
        #            spacing=numpy.array(self.spacing))

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

    def __init__(self, indexFilename, tracedFilesDirectory, debugMode = True):
        
        self.ih = self.clsIndexHolder.fromXML(indexFilename)
        self.tracedFilesDirectory =\
                os.path.join(tracedFilesDirectory,
                        self.ih.properties['FilenameTemplate'].value)
        
        self.refDimestions =\
                (float(self.ih.properties['ReferenceWidth'].value),
                 float(self.ih.properties['ReferenceHeight'].value))
        
        self.CurrentStructureProperties={}
        self.csp=self.CurrentStructureProperties #alias
        
        self.debugMode = debugMode 
    
    def __initializeVolume(self):
        """
        Calculates dimenstions, allocates memory of volume and creates
        vtkStructure for managing defined volume.
        
        @return: None.
        """
        
        # Calculate volume dimensions basing on set of slides and
        # (implicitly) values defined in C{indexHolder.volumeConfiguration}
        volumeDimensions = self.ih.defineVolumeSize( self.csp['slides'] )
        
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
        n   = self.ih.slidesBregmas['SlideNumber']
        res = self.ih.volumeConfiguration['CoronalResolution']
        rc  = self.ih.volumeConfiguration['AlignerReferenceCoords']
        bo  = self.ih.volumeConfiguration['BoundingBoxOffset']
        ppd = self.ih.volumeConfiguration['FullPlaneDimensions']
        sp  = self.ih.slidesBregmas['SlideSpans']
        bb  = self.ih.volumeConfiguration['CoronalBoundaryIndexes']
        rf  = self.ih.volumeConfiguration['ReduceFactor']
        m   = self.ih.volumeConfiguration['VolumeMargin']     # Margin in vol units.
        
        # Define scaling in x,y,z direction. Scaling in x and y are calculated
        # by taking scaling defined in svg file and multiplying it by some
        # resolution-dependent factor. Coronal scaling is taken directly from
        # coronal resolution.
        sx, sy, sz = rc[2]*rf, rc[3]*rf, res
        
        # Coordinates of upper left image corner and maximal bregma coordinate.
        # tx,ty are taken from AlignerReferenceCoords while tz is calculated by
        # taking bregma coordinate of "left" boundary of first slice of
        # structure.
        tx, ty, tz = rc[0] , rc[1], sp[n[0]][0]
        
        # Full width and height of image (the save values which are passed to
        # rederer
        w, h      = ppd[0], ppd[1]
        
        # Bounding box coordinates. Those coordinates are taking into accounts
        # fact that renderer module flips resulting image upside down to fit it
        # into vtk reruirements (by = h-bo[3]). Bz is calculated basing on
        # minimum bregma coordinate ("right" bregma coordinate of slide with
        # maximum index): bz = -bb[1]+margin.
        bx, by, bz = bo[0] , h-bo[3], -(bb[1]+m)

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
        O = numpy.array([0, h, 0, 1]).reshape(4,1)
        
        # Matrix transforming from image coordinate system to stereotaxic
        # coordinate system:
        # The exact form of T and S matrices depends on direction of axes.
        # Esspecialy direction of Y axis:
        if sy > 0 and  ty < 0:
            T = numpy.array( [[1 ,0,0,tx],[0,1 ,0,-ty],[0,0,1,tz],[0,0,0,1]])
            S = numpy.array( [[sx,0,0,0 ],[0,-sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
        elif sx < 0 and sy < 0 and ty > 0:
            T = numpy.array( [[1 ,0,0,w*sx+tx],[0,1 ,0,ty],[0,0,1,tz],[0,0,0,1]])
            S = numpy.array( [[-sx,0,0,0 ],[0,sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
        elif sy < 0 and ty > 0:
            T = numpy.array( [[1 ,0,0,tx],[0,1 ,0,ty],[0,0,1,tz],[0,0,0,1]])
            S = numpy.array( [[sx,0,0,0 ],[0,sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
        else:
            T = numpy.array( [[1 ,0,0,tx],[0,1 ,0,ty],[0,0,1,tz],[0,0,0,1]])
            S = numpy.array( [[sx,0,0,0 ],[0,sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
        
        # Bounding box vector
        #b = numpy.array([bx, by, bz, 1]).reshape(4,1)
        B = numpy.array( [[1,0,0,bx],[0,1,0,-by],[0,0,1,bz],[0,0,0,1]])
        
        # Origin after including bounding box
        Op = numpy.dot(T,numpy.dot(S,numpy.dot(B,O)))
        
        if __debug__:
            print >>sys.stderr, "Reference translation matrix:"
            print >>sys.stderr, T
            print >>sys.stderr, "Reference scaling matrix:"
            print >>sys.stderr, S
            print >>sys.stderr, "Origin in stereotaxic coordinates:"
            print >>sys.stderr, O
            print >>sys.stderr, "Bounding box transformation matrix:"
            print >>sys.stderr, B
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
        
        # Define some aliases:
        fpd = self.ih.volumeConfiguration['FullPlaneDimensions']
        ppd = self.ih.volumeConfiguration['PlaneDimensions']
        bbo = self.ih.volumeConfiguration['BoundingBoxOffset']
        
        self.tempCentralPlanes = []   # For collecting central planes indexes
        
        firstSlideIndex = self.csp['slides'][0]    # Index of first slide  
        lastSlideIndex  = self.csp['slides'][1] +1 # Index of last slide +1
        
        # Iterate trought all slides and process with 
        # volume extraction from each slide:
        slideNumbersRange = range(firstSlideIndex, lastSlideIndex)
        for slide in slideNumbersRange:
            print >>sys.stderr, "Processing slide: %d" % slide
            vp = self.__processSingleSlide(slide)\
        
    def __processSingleSlide(self, slideNumber):
        
        # Define some very useful aliases
        bgi = self.ih.slidesBregmas
        cs  = self.ih._scaleBregmaToCoronalBasic
        acs = self.ih.adjustedScaling
        
        # for getting adj. indexes of boundary coronal planes
        scbi= self.ih.setCoronalBoundaryIndexes
        
        # Another set of usefull aliases:
        firstSlideIndex = self.csp['slides'][0]
        lastSlideIndex  = self.csp['slides'][1]
        slideIndexSpan  = (firstSlideIndex, lastSlideIndex)
        
        # Get bregmaCoordinate and coronal span of currently processed slide
        bregmaCoordinate = bgi['Bregma'][slideNumber]
        currentSlideSpan = bgi['SlideSpans'][slideNumber]
        
        #  Get coronal plane indexes of boundaries of current slide
        slidePlanesSpan  = scbi((slideNumber, slideNumber))
        
        # Get adjusted coronal plane indexes of boundaries of whole slides set
        adjPlanesSpan    = (\
                acs(currentSlideSpan[0], slideIndexSpan),
                acs(currentSlideSpan[1], slideIndexSpan)\
                )
        
        # Get coronal plane index of center of processed slide: 
        centralAdj = acs(bregmaCoordinate, slideIndexSpan) 
        
        self.tempCentralPlanes.append(centralAdj)
        if __debug__:
            print >>sys.stderr,"Processing slide number:\t%d" % slideNumber
            print >>sys.stderr,"    Bregma:\t%f" %   bregmaCoordinate
            print >>sys.stderr,"    Slide span:\t" + str(currentSlideSpan)
            print >>sys.stderr,"    Rasterized span:\t" + str(slidePlanesSpan)
            print >>sys.stderr,"    Adjusted span:\t" + str(adjPlanesSpan)
            print >>sys.stderr,"    Central plane:\t" + str(cs(bregmaCoordinate))+"\t"+str(centralAdj)
        
        structuresToInclude = self.csp['StructuresList']  
        
        fpd = self.ih.volumeConfiguration['FullPlaneDimensions']
        bbo = self.ih.volumeConfiguration['BoundingBoxOffset']
        
        maskedSlide = self._loadSlide(slideNumber, structuresToInclude, version=0)
        maskedSlide.getMask()
        
        # ------------------ Experimental ---------------------
        if ENABLE_EXPERIMENTAL_FEATURES:
            #maskedSlide.writeXMLtoFile("%04d.svg"%slideNumber)
            map(lambda x: setattr(x,'crispEdges',True), maskedSlide.values())
        # ------------------ Experimental ---------------------
        
        volumeFromOneSlice = maskedSlide._renderSvgDrawing(\
                                maskedSlide.getXMLelement(),
                                renderingSize=fpd,
                                boundingBox=bbo,
                                otype='rec')
        
        for volumePlane in range(adjPlanesSpan[0], adjPlanesSpan[1]+1):
            if __debug__:
                print >>sys.stderr, "\t\tFilling plane %s" %volumePlane
            self.StructVol.setSlice(volumePlane, volumeFromOneSlice)
        return volumePlane
    
    def _loadSlide(self, slideNumber, structuresToInclude = None, version = 0):
        tracedSlideFilename = self.tracedFilesDirectory % (slideNumber,version)
        testslide = self.clsSlide.fromXML(tracedSlideFilename)
        maskedSlide = testslide.getStructuresSubset(structuresToInclude)
        return maskedSlide
    
    def __flushCache(self):
        del self.StructVol
        del self.tempCentralPlanes
    
    def __initModelGeneration(self, coronalResolution):
        mx = float(self.ih.refCords[2]) / float(coronalResolution)
        my = float(self.ih.refCords[3]) / float(coronalResolution)
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
        """
        """
        stlist = self.ih.getStructureList(HierarchyRootElementName)
        self.csp['StructuresList'] = stlist
        self.csp['slides'] = self.ih._structList2SlideSpan(stlist)
        
        bbx = self.ih.getStructuresListBbx(stlist)
        
        # ------------------ Experimental ---------------------
        if ENABLE_EXPERIMENTAL_FEATURES:
            xbbx=int(float(self.ih.properties['ReferenceWidth'].value))
            ybbx=int(float(self.ih.properties['ReferenceHeight'].value))
            bbx = barBoundingBox((1, 1, xbbx-1, ybbx-1))
            self.csp['slides'] =\
                    (self.ih.slidesBregmas['SlideNumber'][0],\
                     self.ih.slidesBregmas['SlideNumber'][-1])
        # ------------------ Experimental ---------------------
        
        self.ih.volumeConfiguration['StructureBoundingBoxes'] = bbx
        self.ih.volumeConfiguration['CoronalBoundaryIndexes'] = self.ih.setCoronalBoundaryIndexes(self.csp['slides'])
    
    def handleAllModelGeneration(self,\
            HierarchyRootElementName,\
            CoronalResolution,\
            saggitalResolution,\
            VolumeMargin = 10):
        """
        """
        self.ih.volumeConfiguration['AlignerReferenceCoords'] = self.ih.refCords
        self.ih.volumeConfiguration['CoronalResolution']      = saggitalResolution 
        self.ih.volumeConfiguration['VolumeMargin']           = VolumeMargin
        self.__getStructureList(HierarchyRootElementName)
        self.__initModelGeneration(CoronalResolution)
        self.__processModelGeneration()
    
    def getSlidesSpan(self, HierarchyRootElementName):
        return self.ih.getSlidesSpan(HierarchyRootElementName)
    
    def getDefaultZres(self):
        return self.ih.getDefaultZres()
