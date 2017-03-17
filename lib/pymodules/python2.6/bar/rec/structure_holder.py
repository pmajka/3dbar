#!/usr/bin/python
# -*- coding: utf-8 -*
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
from bar import barCafSlide
from bar import barBoundingBox


class VTKStructuredPoints():
    def __init__(self, (nx, ny, nz)):
        # The ugly convertion to int is for the purpose of compatibility with
        # vtk. If casting is not performed, we end up with float64 instead
        # of int.)
        self.vol = \
            numpy.zeros(tuple(map(int, (nx, ny, nz))), dtype=numpy.uint8)
        self.size=self.vol.shape

    def setOrigin(self, (x, y, z)):\
        self.origin=(x, y, z)

    def setSpacing(self, (sx, sy, sz)):
        self.spacing=(sx, sy, sz)

    def setSlices(self, slideIndexList, sliceArray):
        self.vol[:, :, slideIndexList] = sliceArray

    def prepareVolume(self, indexholderReference):
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
    clsSlide = barCafSlide

    def __init__(self, indexFilename, tracedFilesDirectory):

        self.ih = self.clsIndexHolder.fromXML(indexFilename)
        self.tracedFilesDirectory =\
                os.path.join(tracedFilesDirectory,
                        self.ih.properties['FilenameTemplate'].value)

        self.refDimestions =\
                (float(self.ih.properties['ReferenceWidth'].value),
                 float(self.ih.properties['ReferenceHeight'].value))

        self.recSettings = {}
        self.StructVol = None

    def __initializeVolume(self):
        """
        Calculates dimenstions, allocates memory of volume and creates
        vtkStructure for managing defined volume.

        @return: None.
        """
        zExtent = self.recSettings['zExtent']
        dm = self.recSettings['CroppedImageSize']  # Bitmap size
        volumeDimensions = (dm[0], dm[1], zExtent)

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
        zRes = self.recSettings['zRes']
        rc  = self.ih.refCords
        bo  = self.recSettings['BoundingBox']
        ppd = self.recSettings['ScaledImageSize']
        bb  = self.recSettings['zOrigin']
        rf  = self.recSettings['ScaleFactor']

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
        # into vtk reruirements (e.g. by = h-bo[3]).
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

        @return: ((numpy 3x1 array),(3x1)):  spatial coordinates of vtk coordinate
                 system origin and spacing in x,y and z directions.
        """

        # Initial origin of coordinate system in image coordinates (it is
        # located in lower left corner of the image.
        O = numpy.array([0, 0, 0, 1]).reshape(4,1)
        B = numpy.array( [[1,0,0,bx],[0,1,0,by],[0,0,1,bz],[0,0,0,1]])

        # Matrix transforming from image coordinate system to stereotaxic
        # coordinate system:
        # The exact form of T and S matrices depends on direction of axes.
        # Esspecialy direction of Y axis:
        # We take absolute value of scalings and coronal resosolution as
        # VTK handles negavite scaling very poor.
        # TODO: Crashes for the following values: 8.45 -8.2 -0.025 0.025
        # TODO: Fix it!

        if sx > 0 and sy > 0:
            S = numpy.array( [[sx,0,0,0 ],[0,sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
            T = numpy.array( [[1 ,0,0,tx],[0,1 ,0,ty],[0,0,1,tz],[0,0,0,1]])
        elif sx > 0 and sy < 0:
            S = numpy.array( [[sx,0,0,0 ],[0,-sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
            T = numpy.array( [[1 ,0,0,tx],[0,1 ,0,sy*h+ty],[0,0,1,tz],[0,0,0,1]])
        elif sx < 0 and sy > 0:
            S = numpy.array( [[-sx,0,0,0 ],[0,sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
            # XXX proposal: T = numpy.array( [[1 ,0,0, tx],[0,1 ,0,ty],[0,0,1,tz],[0,0,0,1]])
            T = numpy.array( [[1 ,0,0,w*sx+tx],[0,1 ,0,ty],[0,0,1,tz],[0,0,0,1]])
        elif sx < 0 and sy < 0:
            S = numpy.array( [[-sx,0,0,0 ],[0,-sy,0,0 ],[0,0,sz,0],[0,0,0,1]])
            # XXX proposal: T = numpy.array( [[1 ,0,0, tx],[0,1,0,h*sy+ty],[0,0,1,tz],[0,0,0,1]])
            T = numpy.array( [[1 ,0,0,w*sx+tx],[0,1,0,h*sy+ty],[0,0,1,tz],[0,0,0,1]])

        # Origin after including bounding box
        Op = numpy.dot(T,numpy.dot(S,numpy.dot(B,O)))
        origin  = (Op[0,0], Op[1,0], Op[2,0])
        spacing = (abs(S[0,0]),  abs(S[1,1]),  abs(S[2,2]))

        if __debug__:
            print "\t__calcOriginAndSpacing: volume origin:", origin
            print "\t__calcOriginAndSpacing: volume spacing:", spacing

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

        firstSlideIndex = self.recSettings['slides'][0]    # Index of first slide
        lastSlideIndex  = self.recSettings['slides'][1] +1 # Index of last slide +1
        slideNumbersRange = range(firstSlideIndex, lastSlideIndex)

        Oz = self.StructVol.origin[2]
        ez = self.StructVol.size[2]
        sz = self.StructVol.spacing[2]

        z = numpy.array(map(lambda x: sz*(x) + Oz, range(0, ez)))
        zi= numpy.array(range(0, ez))

        slidePlanes = {}
        for s in map(lambda x: self.ih.s[x], slideNumbersRange):
            mask = (0>=numpy.round(s.span[0]-z,5)) & (0<=numpy.round(s.span[1]-z,5))
            slidePlanes[s.name] = (list(zi[mask]), list(z[mask]))

        self.recSettings['FlipFlags'] = self.__getFlips()

        for (slideNo, (planes,coor)) in slidePlanes.iteritems():
            if planes:
                self.__processSingleSlide(slideNo, (planes,coor))

    def __processSingleSlide(self, slideNumber, (planes,coor)):
        print "Processing slide number:\t%d" % slideNumber

        if __debug__:
            print "\t__processModelGeneration: planes:", planes
            print "\t__processModelGeneration: corresponding coords:",  coor
            print

        structuresToInclude = self.recSettings['StructuresList']
        fpd = self.recSettings['ScaledImageSize']
        bbo = self.recSettings['BoundingBox']
        otype = self.recSettings['FlipFlags']

        maskedSlide = self._loadSlide(slideNumber, structuresToInclude, version=0)
        maskedSlide.getMask()

        volumeFromOneSlice = maskedSlide._renderSvgDrawing(\
                                maskedSlide.getXMLelement(),
                                renderingSize=fpd,
                                boundingBox=bbo,
                                otype=otype)

        self.StructVol.setSlices(planes, volumeFromOneSlice)

    def _loadSlide(self, slideNumber, structuresToInclude = None, version = 0):
        tracedSlideFilename = self.tracedFilesDirectory % (slideNumber,version)
        testslide = self.clsSlide.fromXML(tracedSlideFilename)
        maskedSlide = testslide.getStructuresSubset(structuresToInclude)
        map(lambda x: setattr(x, 'crispEdges', True), maskedSlide.values())
        return maskedSlide

    def __getFlips(self):
        # Determine if, the rendered plane shoud be flipped in x and y axis.
        # It should be done if direction of spatial axes is opposite to image
        # direction
        otype = 'rec'
        if self.ih.flipAxes[0]:
            otype+='1'
            if __debug__: print '\t__getFlips: Flip x'
        if self.ih.flipAxes[1]:
            otype+='1'
            if __debug__: print '\t__getFlips: Flip y'
        print
        return otype

    def __flushCache(self):
        try:
            del self.StructVol
            del self.tempCentralPlanes
        except:
            pass
        self.recSettings = {}

    def __initModelGeneration(self, xyRes, ignoreBbx = False):
        mx, my = map(lambda x: abs(x/float(xyRes)), self.ih.refCords[2:])

        scaleFactor = mx
        self.recSettings['ScaleFactor'] = 1./scaleFactor

        self.recSettings['ScaledImageSize']=\
            map(lambda x: x* scaleFactor, self.refDimestions)

        bbx = self.ih.getStructuresListBbx(self.recSettings['StructuresList'])
        self.recSettings['CafBoundingBox'] = bbx

        if ignoreBbx:
            stlist = self.ih.getStructureList(self.ih.hierarchyRootElementName)
            bbx = self.ih.getStructuresListBbx(stlist)

        bbx*=scaleFactor
        bbx.extend((-1,-1,1,1))

        self.recSettings['BoundingBox'] = bbx
        self.recSettings['CroppedImageSize'] = (bbx[2]-bbx[0],bbx[3]-bbx[1])

        if __debug__:
            print "\t__initModelGeneration: xyRes:", xyRes
            print "\t__initModelGeneration: ignoreBbx:", ignoreBbx
            print "\t__initModelGeneration: final bbx:", self.recSettings['BoundingBox']
            print "\t__initModelGeneration: final bitmap size:", self.recSettings['CroppedImageSize']
            print

    def _checkEqualSpacing(self, roundoff=5):
        zRes = self.recSettings['zRes']
        refRes = self.getDefaultZres()

        if  round(zRes - refRes, roundoff) == 0:
            eqSpacing = True
        else:
            eqSpacing = False

        if __debug__:
            print "\t_checkEqualSpacing: fullDiff:", zRes - refRes
            print "\t_checkEqualSpacing: roundoff:", roundoff
            print "\t_checkEqualSpacing: eqSpacing:", eqSpacing
            print

        return eqSpacing

    def __getStructureList(self, rootElementName, ignoreBbx = False):
        stlist = self.ih.getStructureList(rootElementName)
        self.recSettings['StructuresList'] = stlist

        if ignoreBbx:
            self.recSettings['slides'] = (self.ih.s[0].idx, self.ih.s[-1].idx)
        else:
            self.recSettings['slides'] = self.ih._structList2SlideSpan(stlist, rawIndexes=True)

        (zOrigin, zExtent) = self.ih.getZOriginAndExtent(\
                self.recSettings['slides'], self.recSettings['zRes'],\
                self.recSettings['zMargin'], self._checkEqualSpacing())

        self.recSettings['slides'] = self.ih._structList2SlideSpan(stlist, rawIndexes=True)
        self.recSettings['zOrigin'], self.recSettings['zExtent'] =\
                zOrigin, zExtent

        if __debug__:
            Oz = self.recSettings['zOrigin']
            ez = self.recSettings['zExtent']
            sz = self.recSettings['zRes']
            print "\t__getStructureList: Zorigin, Zextent, Zspacing:", Oz, ez, sz
            print "\t__getStructureList: ignoreBbx:", ignoreBbx
            print "\t__getStructureList: slides:", self.recSettings['slides']

    def handleAllModelGeneration(self,\
            rootElementName,\
            xyRes, zRes,\
            VolumeMargin = 10,\
            ignoreBoundingBox = False):

        self.__flushCache()
        self.recSettings['zRes']    = zRes
        self.recSettings['zMargin'] = VolumeMargin
        self.__getStructureList(rootElementName, ignoreBbx = ignoreBoundingBox)
        self.__initModelGeneration(xyRes, ignoreBbx = ignoreBoundingBox)
        self.__processModelGeneration()

    def getSlidesSpan(self, rootElementName):
        return self.ih.getSlidesSpan(rootElementName)

    def getDefaultZres(self):
        return self.ih.getDefaultZres()
