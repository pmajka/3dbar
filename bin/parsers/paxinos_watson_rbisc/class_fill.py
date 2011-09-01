#!/usr/bin/python
# -*- coding: utf-8 -*-
#!/usr/bin/python
# vim: set fileencoding=utf-8
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

from PIL import Image,ImageDraw,ImageFilter,ImageChops,ImageOps
import image_process
import xml.dom.minidom as dom
from svgpathparse import parsePath, UnparsePath, parseStyle, formatStyle
from config import *
import subprocess
import svgfix
import string
import cStringIO
import cairo
import rsvg
import numpy
import sys
from matcharrows import _embedTracelevel

#TODO implement warnings as exceptions
#TODO Implement complex brain structure (very important!@!!)

class GrowFill:
    """
    Class which generates floodfilled areas on selected coordinates.
    
    Improvements: 
    
    pon, 17 maj 2010, 19:25:38 CEST
    SVG image after rendering is converted to indexed color and then all
    non-white pixels are converted to color 200.
    
    wto, 8 cze 2010, 14:09:13 CEST
    Removed generating vBrain structure, instead of this inverse of vBrain is traced.
    This procedure allows to generate area with brain ( instead of area of brain inverse)
    which is much more usefull.
    Note: vBrain is traced as first structure - not as last.
    
    sro, 9 cze 2010, 13:45:38 CEST
    Aditional image with brain area is cached after tracing whole brain area. This image is
    used in order to determina if flood fill seed is placed within brain area.
    
    sro, 9 cze 2010, 13:50:10 CEST
    Structure path elements naming scheme: Generic structure name is >>structure%d_%s_%s<<
    where consecutive variables are:

        1. Subsequent structure number
        2. ID of the label basing on which given path was created
        3. Name of the structure modeled with given path
    
    Examples of valid path IDs:

        - structure92_label102_st
        - structure116_label131_Xi
        - structure1_label1_CPu
    
    When number of path doesn't match with number of label it means that tracing of some
    structures was ommited due to placing seed in non-white pixels.
    
    sro, 9 cze 2010, 15:14:25 CEST
    Skipping tracing spotlabels and comment labels. 
    
    czw, 10 cze 2010, 16:32:41 CEST
    Replaced floodfilling alogrithm:
    Instead of currently used PIL ImageDraw.floodfill algorithm, the custom
    algorithm floodFillScanlineStack (implemented by me basing on http://) is
    now used. 
    
    The new algorithm appeared to be twice as fast as the previous algorithm.
    However, due to different method of performing filling the results of both
    algorithms are not exactly the same. The scanline algorithm seems to flood
    larger number of pixels than default algotithm. Neverless, the differences
    as rather slight and there is no need for further changes in the code.
    
    Corrected brain contour treshold bug.
    In order to determine if structure labels are paced inside the brain regions
    the whole brain is traced in first step. Then brain region is cached for
    further comparision. However no treshold was applied and gray lines were not
    removed which produced unnecesarry errors. After applying treshold, all
    gray pixels where changed to white so the bug was removed. 

    Fri Jun 11 10:48:22 CEST 2010
    List of reviewing and error tracing procedures:

        1. When seed is placed outside brain region, warning is generated and
           debug information is dumped. Structure is not traced.
        2. When seed in placed on border (in non-white pixel in general),
           warning is generated and debug information is stored. Structure is not
           traced.
        3. Path naming scheme is constructed in a way which allows to quickly
           determine if tracing process was fully correct or not. Paths has to be
           numerated with consecutive numbers consistent with ID of corresponding
           labels.
        4. Spot labels and comment labels are not traced.
        5. For each step of processing, debug information may be stored. By debug
           information I mean SVG files with single traced structures as well as
           bitmaps from intermediate steps of processing

    
    pia, 2 lip 2010, 12:21:14 CEST
    Implementing unlabeled structures handling.
    Assumptions:

        1. Areas with are not covered by regular labels are to be found and denoted
           as unlabelled areas.
        2. For each unlabelled area path and corresponding label should be created.
        3. Labels denoting unlabelled areas are backpropagated to pretraced file
        4. Labels denoting unlabelled areas are not traced - finding unalbelled areas
           is performed from scratch each time.

    Renember that brain contour bitmap has only two colors (black and white).
    Black clolor denotes region outside brain while white color denotes brain area.
    There is no contour in that bitmap. In case when many adjacent unlabeled regions
    exist they will be presented as a single unlabeled area.

    sro, 25 sie 2010, 18:55:04 CEST

        1. Rebuilded path parsing. Now path parsing functions are moved to svgpathparse
           moule. 
        2. Some slight improvements


    G{classtree: GrowFill}
    """
    
    def __init__(self, svgdoc):
        """
        Class constructor. Caches SVG document and creates  empty
        dictionaries/list for imageCache, StructuresIterator, growLevelList and
        ConfigurationDictionary. All those variables are filles with data in
        further steps of processing.

        @type  svgdoc: DOM object
        @param svgdoc: Svg documnet to render,
                       it would be cleaned out from any text objects,
                       rectangles circles and so on.
        """

        self.imageCache=[]          # Holds all preformated images
        self.StructuresIterator=0   # Number for ID generation
        self.BestGrowList=[]        # List which hold growLevels for each structure
                                    # In order defined by getElementByTagName
        self.tracerConf={}          # Dictionary which holds all configuation
                                    # or at least is supposed to do
        
        # Cache SVG document (it will be deleted soon)
        self.svgdoc = svgdoc
        
    def LoadImageInit(self):
        """
        @return: None

        Performs all operations related to loading and rasterizinig SVG image
        and creating the image chache. This method should be invoked directly
        after defining tracer properties. At the final step SVG document is
        removed from the cache as it is no longer needed.
        """
        
        # Load images into cache array
        self._preprocessSVGDrawing()  # Apply last-time changes to svg
        self._LoadImage()             # Render svg file
        self._CreateCache()

        # If we want to dump file
        #f=open('qwe.svg','w')
        #self.svgdoc.writexml(f)
        #f.close()

        del self.svgdoc

        #import pycallgraph
        #pycallgraph.start_trace()
        #pycallgraph.make_dot_graph('test.png')

    def _preprocessSVGDrawing(self):
        """
        @return: None
        
        Function applies custom slide processing if such procesing is required.
        Currenly supported custom processing rules are:
        
        pią, 10 wrz 2010, 17:04:55 CEST:
            - Force stroke width: Reason, why this option was implemented is
              provided in parser.py file.
        """
        
        # Is 'Force stroke width defined'?
        if CONF_FORCE_PATH_STROKE_WIDTH:
            print >>sys.stderr, "Changing stroke-width of all paths to %1.2f"%\
                    CONF_FORCE_PATH_STROKE_WIDTH
            for pathElement in self.svgdoc.getElementsByTagName('path'):
                style = parseStyle(pathElement.getAttribute('style'))
                style['stroke-width'] = CONF_FORCE_PATH_STROKE_WIDTH
                pathElement.setAttribute('style', formatStyle(style))
    
    def setProperty(self, propertyName, propertyValue):
        """
        Sets tracer configuration by updating internal dictionary of the class.

        @type  propertyName: string - dictionatry key
        @param propertyName: name of defined property. Please avoid spaces -
                             use underscores instead.
        @type  propertyValue: Arbitraty python expression (usually integer,
                              string or list).
        @param propertyValue: Property value.
        @return: None
        """

        self.tracerConf[propertyName]=propertyValue
    
    def _StripSVGImage(self):
        """
        Strips SVG document from obcjects that are not related to brain
        (labels, labels rectangles, circles etc.). List of elements for removing
        is stored in configuration dictionary.

        @return: None
        """
        
        for tagTypeToClean in self.tracerConf['TagsToClean']:
            for el in self.svgdoc.getElementsByTagName(tagTypeToClean):
                el.parentNode.removeChild(el)

    def _ToImageCoordinates(self, SVGcoords):
        """
        Converts coordiantes from SVG image to coordinates in raster image system.
        By default, SVG drawings are rendered with 90 dpi resolution.
        In this resolution one point in SVG drawing is equivalent to one pixel of
        raster image. When SVG is rendered in larger resolution (we do not consired smaller
        resolutions in this software), coordiantes has to be rescaled. Retured
        values are rounded to integers.

        @type  SVGcoords: tuple of two integers
        @param SVGcoords: Coordinates in SVG drawing coordinates system.

        @return: (tuple of two integers) Image coordinates corresponding provided
                 svg coordinates.
        """

        # Just create few aliases
        imSize    = self.tracerConf['imageSize']
        refWidth  = self.tracerConf['ReferenceWidth' ]
        refHeight = self.tracerConf['ReferenceHeight']

        # The formula is extremely simple x/xref * svg_size
        # Where x is size of rendered image, xref - reference size, 
        # svg_size - svg coordinate value

        return (int(float( imSize[0] / refWidth * SVGcoords[0] )),\
                int(float( imSize[1] / refHeight* SVGcoords[1] )))

    def _ToSVGCoordinates(self, ImageCoords):
        """
        @type  ImageCoords: tuple of two integers
        @param ImageCoords: Image coordinates to transform

        @return: tuple of two floats: (x,y)

        Transforms coordinates given in pixels (in image coordinate system) to
        coordinates in SVG drawing coordinate system (not stereotaxic coordinate
        system).
        """
        # Just create few aliases
        imSize    = self.tracerConf['imageSize']
        refWidth  = self.tracerConf['ReferenceWidth' ]
        refHeight = self.tracerConf['ReferenceHeight']

        # The formula is extremely simple x/xref * svg_size
        # Where x is size of rendered image, xref - reference size, 
        # svg_size - svg coordinate value

        return (float( 1./(imSize[0] / refWidth )* ImageCoords[0] ),\
                float( 1./(imSize[1] / refHeight)* ImageCoords[1] ))

    
    def _LoadImage(self):
        """
        Renders provided SVG image with given resolution and puts rendered image into cache.
        
        Workflow:
            1. Strip SVG from unnecessary objects,
            2. Render image and convert it to NumPy array
            3. Manipulate channels and colours, convert to indexed mode
            4. Cache rendered image.

        @return: Nothing, only C{self.imageCache} is updated.
        """
        
        # Strip SVG drawing 
        self._StripSVGImage()
        
        # Put XML to rsvg
        svg = rsvg.Handle(data = self.svgdoc.toxml())
        width, height = self.tracerConf['imageSize']
        
        # Allocate memory and create context
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(surface)
        
        # Define dimensions, rescale and render image
        wscale = float(width) / svg.props.width
        hscale = float(height) / svg.props.height
        cr.scale(wscale, hscale)
        svg.render_cairo(cr)

        # Save snapshot of rendered image for debug purposes
        #if __debug__ :  surface.write_to_png ('debugfilename.png')

        # Now we need generate PIL image from raw data extracted
        # from cairo surface. The workflow is following:
        # Dump raw image data to numpy, correct channels sequence 
        # And then convert NumPy array to PIL image object.

        # Dump image information to NumPy array
        # surface.get_data() returns RGBA array thus we have to
        # reshape this array manually
        a = numpy.frombuffer(surface.get_data(), numpy.uint8)
        a.shape = (width, height, 4)

        # Swap channels (orig) [B,G,R,A] -> [R,G,B,A]
        b=a.copy()
        a[:,:,0]=b[:,:,2]
        a[:,:,2]=b[:,:,0]
        t=(255-a[:,:,3])

        # TODO: Optimize it
        a[:,:,0]+=t
        a[:,:,1]+=t
        a[:,:,2]+=t
        
        # Remove unnecesarry arrays 
        del b
        del t

        # TODO: Perhaps desaturation should be done manually (using numpy)

        # Put final image into cache
        # Ok, we convert numpy array to image, then we convert it to indexed
        # colour and then every color that is not white is set to 200 and after
        # that we have indexed image with 255 colors in which only white and 200
        # are used
        self.imageCache.append(\
                Image.eval(\
                Image.fromarray(a, 'RGBA').convert("L"),\
                    self._setDefaultMiddleColour )\
                )
    
    def _setDefaultMiddleColour(self, pixelColorValue):
        """
        Applies treshold function for given pixel value. All pixels which are
        non-white pixels becomes 'GrowDefaultBoundaryColor' pixels. This
        procedure assures that output image has only two colours (white and
        boundary) which is very convinient in further processing.

        @type  pixelColorValue: Integer
        @param pixelColorValue: pixel value which  should be modified when it is
                                non-white pixel.

        @return: 255 if white pixel is given and DefaultBoundaryColor otherwise.
        """

        # Just make an alias (perhaps it executes faster)
        defaultBoundaryColour = self.tracerConf['GrowDefaultBoundaryColor']
        
        if pixelColorValue != 255:
            return defaultBoundaryColour
        else:
            return 255
    
    def _CreateCache(self):
        """
        Creates image cache. First cached image is an original image. All other images
        (up to cacheLevel) are images with succesive grows (= applications of MinFilter).
        
        @return: Nothing, C{self.imageCache} list is passed as a reference.
        """
        
        # Just aliases:
        minLevApp=self.tracerConf['MinFiterTimesApplication']
        cacheLevel=self.tracerConf['cacheLevel']
        
        for l in range(cacheLevel):
            self.imageCache.append(\
                    self.imageCache[-1].filter(ImageFilter.MinFilter(minLevApp))\
                    )
    
    def _ClearCache(self):
        """
        Clears image cache. Explicit cache cleaning is required after parsing full slice.
        Clearing cache consists from removing all images from cache and reseting structure
        iterator.
        
        @return: None, C{self.imageCache} list is passed as a reference.
        """
        
        self.imageCache=[]
        self.StructuresIterator=0
    
    def _getCoveredAreasList(self, LabelInfo):
        """
        Creates list of area covered by floodfill for each of cached images.
        
        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates.
        
        @return: Array of areas covered by floodfill for every image cached in
                 C{self.imageCache}.
        """
        # List of calculated areas
        result=[]
        
        # Save information about areas covered in each grow step
        # This data is usefull when it comes to define some heuristics about
        # number of grows that gives best recoinstruction accuracy.
        
        for i in range(len(self.imageCache)):
            result.append(\
                    self._ApplySingleFill(self.imageCache[i], i, LabelInfo)\
                    )
        
        # Dump rebug information if required
        if __debug__: print\
                "Structure:\t"+ LabelInfo[1] +"\t"        +\
                "Coords:\t" + "\t".join(map(str,LabelInfo[0])) + "\t" +\
                "Area:\t"+"\t".join(map(str,result))
        
        return result
    
    def _getNumberOfBlackPixels(self,im):
        """
        @type  im: PIL image
        @param im: Image from which number of black pixels will be extracted.

        @return: Number of pixels with black colour (with index 0 in indexed mode)
        """
        # TODO: Probably this function would work much better if written in C 
        return im.histogram()[0]
    
    def _ApplySingleFill(self, im, l, LabelInfo, ForTracing=False):
        """
        Applies flood fill to given image using using coordinated passed in C{LabelInfo} list.
        Description:
            1. Extract coordinates and structure name from C{LabelInfo}.
            2. Rescale SVG coordinates to rendered image coordinates
            3. Fill given image with black color 
            4. Extend filled region by applying C{MinFilter} filter. Do it C{l+2} times
            5. Return flooded image or return number of black pixels depending on C{ForTracing} value.
        
        @type  im: PIL image
        @param im: Image to flood
        
        @type  l: integer
        @param l: Index of image C{im} in L{ImageCache<ImageCache>} list.
                  Used in extending grow region - MIN filter is applied to flooded region C{l+2} times
                  in order to preserve area of the original structure (as initial edge growing reduces it).
                  Factor 2 is arbitraty.
        
        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates.
        
        @type  ForTracing: boolean
        @param ForTracing: Determines wheter the file should be passed for tracing after counting
                           number of black pixels. If this parameter is set to C{True},
                           flooded image is returned instead of number of black pixels.
        @return: Number of black pixels if C{ForTracing} is C{False}, flooded image otherwise.
        """
        
        # Extract important data from label info 
        coords=LabelInfo[0]       # Label's anchor
        LabelName=LabelInfo[1]    # Text
        
        # Transform SVG coordinates to rasterized image coordinates.
        goodCoords=self._ToImageCoordinates(coords)
        
        # Chceck if structure satisfied all conditions and may be traced
        if not self.isStructAllowedForTracing(LabelInfo, im, l, goodCoords)\
                and ForTracing:
            # In such case we do not want to create any path. To NOT CREATE path
            # we need to trace blank image. To get a blank image we need to
            # create uniformly white image and this is what we do in the line
            # below - we create and return image filled with white color
            return ImageChops.constant(im, 255)
        
        # Copy input image in order to preserve original
        ImToFlood=im.copy()
        
        # Apply floodfill at given coordinates, fill it black.
        #ImageDraw.floodfill(ImToFlood, goodCoords, 0, border=None)
        self.floodFillScanlineStack(ImToFlood, goodCoords, 0)
        
        # Extend flooded area in order to preserve initial structure area
        for j in range(l+1):
            ImToFlood=ImToFlood.filter(ImageFilter.MinFilter(3))
        
        # Most common case as first
        if not ForTracing:
            return self._getNumberOfBlackPixels(ImToFlood)
        else:
            return ImToFlood

    def aafloodFillScanlineStack(self, image, xy, value):
        a = numpy.asarray(image).astype(numpy.int8)
        x, y = xy
        #numpy.savetxt('%d-%d.txt'%(x,y),a, fmt="%d")
        npix = testnp.trace(a, x, y, value)
        image = Image.fromarray(a, 'L')
        image.save('%d-%d.png'%(x,y),"PNG")
        
        print npix
        return npix

    def floodFillScanlineStack(self, image, xy, value):
        """
        Custom floodfill algorithm that replaces original PIL ImageDraw.floodfill().
        This algorithm appears to be twice as fat as the original algorithm and more
        roboust. This algorithm requires reimplementing in C/Fortran and connecting
        to python somehow. Implementation is based on:
        http://www.academictutorials.com/graphics/graphics-flood-fill.asp

        This is implementaion on scanline floosfill algorithm using stack. The
        algorithm is not described here. To get insight please consult goole using
        'floodfill scanline'.

        @note: Please note that this algorithm assume floodfilling image in
               indexed color mode

        @type  image: PIL image object
        @param image: Image on which floodfill will be performed

        @type  xy: tuple of two integers
        @param xy: Coordinates of floodfill seed

        @type  value: integer
        @param value: Fill color value

        @return: Nothing, image object is modifies in place.
                 Update: sro, 30 cze 2010, 14:34:16 CEST returns number of pixels
                 with changed color (area of floodfill).
        """

        pixel = image.load()
        x, y = xy
        w, h = image.size

        npix=0
        background = pixel[x, y]
        stack=[]
        stack.append((x,y))

        while stack:
            x,y=stack.pop()
            y1=y
            while y1>= 0 and pixel[x, y1] == background:
                y1-=1
            y1+=1
            
            spanLeft = spanRight = 0
            
            while y1 < h and pixel[x, y1] == background:
                pixel[x, y1] = value
                npix+=1
                
                if (not spanLeft) and x > 0 and pixel[x-1,y1] == background:
                    stack.append((x-1,y1))
                    spanLeft=1
                else:
                    if spanLeft and x > 0 and pixel[x-1,y1] != background:
                        spanLeft=0
                
                if (not spanRight) and x<w-1 and pixel[x+1,y1] == background:
                    stack.append((x+1, y1))
                    spanRight=1
                else:
                    if spanRight and x<w-1 and pixel[x+1,y1] != background:
                        spanRight=0
                y1+=1
        
        print npix
        return npix

    def isStructAllowedForTracing(self, LabelInfo, im, l, goodCoords):
        """
        Determines if bitmap with given seed is suitable for tracing. There are
        briefly two conditions which need to be satisfied in order to allow
        tracing:
        
            1. Seed has to be placed within brain contour. The brain contour is
               defined at the begining of tracing procedure.
            2. Seed has to be placed at white pixel. If seed points into
               non-white pixel is it a) border between two structures; b) area
               outside brain contour.
        
        In both cases debug information is printed.
        
        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates.
        @type  im: PIL 
        @param im: Image to be floodfilled
        @type  l: integer
        @param l: Boundary growing level
        @type  goodCoords: tuple of two integers
        @param goodCoords: Floodfill seed in rasterized image coordinates
                           system.
        
        @return: True if image is suitable for tracing (according to testing
        conditions), False otherwise.
        """

        # Both conditions results in the same bahaviour of the program, however
        # they were presented separately for clarity.
        
        # Check, if color of the pixels at given coordinates is suitable pixel
        # for flood filling (it should be hardcoded white color)
        # We check it only when image is prepared for tracing.
        if im.getpixel(goodCoords) != 255:
            _printRed("Seed points at non white pixels: "+str(im.getpixel(goodCoords)))
            self.dumpWrongSeed(LabelInfo, im, l, goodCoords)
            return False
        
        # Verify, if the seed is placed within brain contour. This procedure
        # assures that only correctly placed labels (=labels inside brain)
        # are traced.
        try:
            if self.brainContourImage.getpixel(goodCoords) == 0:
                _printRed("Seed points outside brain area: "+str(im.getpixel(goodCoords)))
                self.dumpWrongSeed(LabelInfo, im, l, goodCoords)
                return False
        except:
            pass

        # Check if the region was not traced already
        # Each traced region has is marked by RegionAlreadyTraced colour on self.brainContourImage
        #try:
        #   if self.brainContourImage.getpixel(goodCoords) == 100:
        #       _printRed("Seed of label %s at coords (img coords: %s)" % ((LabelInfo[1],LabelInfo[0]),self._ToImageCoordinates(LabelInfo[0])))
        #       _printRed("is placed on area which was already traced and WILL NOT be traced.")
        #       return False
        #except:
        #   pass
        
        return True

    def dumpWrongSeed(self, LabelInfo, im, l, goodCoords):
        """
        Method invoked by L{isStructAllowedForTracing<isStructAllowedForTracing>}.
        Outputs warning message to stderr and dumps invalid image into a file.
        
        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates.
        @type  im: PIL 
        @param im: Image to be floodfilled
        @type  l: integer
        @param l: Boundary growing level
        @type  goodCoords: tuple of two integers
        @param goodCoords: Floodfill seed in rasterized image coordinates
                           system.
        @return: None
        """

        # Extract important data from label info 
        coords=LabelInfo[0]       # Label's anchor
        LabelName=LabelInfo[1]    # Text
        
        # Transform SVG coordinates to rasterized image coordinates.
        goodCoords=self._ToImageCoordinates(coords)
        
        # Print warning that seed points at pixel with incorrect values
        _printRed("tracing of area %s located at coordinates %d,%d "\
                % (LabelName, goodCoords[0], goodCoords[1]))
        _printRed("is ommited because of non-white seed pixel value.")
        _printRed("try aligning label or manualy set boundary growing level.")
        
        # Do the regular filling to achieve flooded file
        ImToFlood=im.copy()
        #old floodfill: ImageDraw.floodfill(ImToFlood, goodCoords, 0, border=None)
        self.floodFillScanlineStack(ImToFlood, goodCoords, 0)
    
        if not self.tracerConf['DumpWrongSeed']: return

        # Draw gray circle at debug image in order to mark area when error
        # occured
        draw = ImageDraw.Draw(ImToFlood)
        draw.ellipse((
                (goodCoords[0]-20, goodCoords[1]-20),\
                (goodCoords[0]+20, goodCoords[1]+20)
                )\
                , 60)
        del draw
        
        # Generate debug filename. Filename consists from following
        # information: slidenumber, boundary growing level, labelID adn seed
        # coordinates.
        tempDumpFilename=\
            self.tracerConf['SetDebugDumpOutputDirectory']+\
            'slide_'+ str(self.tracerConf['slidenumber'])+'_'\
            'debug_filled_'+\
            CleanFilename(LabelName)+\
            '_grow_'+str(l)+\
            '_%d_%d.png' % goodCoords
        
        # Dump image which caused error.
        _printRed("Dumping image to %s" % tempDumpFilename)
        if __debug__:
            ImToFlood.resize((\
                    self.tracerConf['ReferenceWidth' ]  ,\
                    self.tracerConf['ReferenceHeight'])).\
                save(tempDumpFilename, "PNG")   
    
    def _DoTracing(self, im):
        """
        Performs image tracing via potrace and pipes mechanism.
        Assumes that image has one, non-separable area filled with black pixels.
        This function do not perform parsing the output.
        
        Tracing Workflow:
            1. Save image in bmp format in dummy string
            2. Sends bmp string to potrace via pipe mechanism
            3. Perform tracing
            4. Read tracing output via pile
            5. Return raw tracing output
        
        @type  im: PIL image
        @param im: Flooded image for tracing
        
        @return: Raw tracing output string.
        """
        
        # Create file-like object which handles bmp string
        ImageString = cStringIO.StringIO()
        
        # Save image to this file-like object
        im.save(ImageString, "BMP")
        
        # Create process pipes
        # potrace parameters:
        # -s for settring SVG output
        # -O Optimization parameter
        # -r SVG Image resolution in DPI
        # -W,H Output dimensions of SVG drawing
        # -o - - Input and output via pipes
        process = subprocess.Popen(['potrace',\
                '-s',\
                '-O', self.tracerConf['PotraceAccuracyParameter']  ,\
                '-r', self.tracerConf['PotraceSVGResolutionString'],\
                '-W', self.tracerConf['PotraceWidthString']         ,\
                '-H', self.tracerConf['PotraceHeightString'],\
                '-o','-','-']\
                , stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        
        # Pass bmp string to pipe, close image string.
        process.stdin.write(ImageString.getvalue())
        ImageString.close()
        
        # Read and return tracing output
        output = process.stdout.read()
        return output
    
    def _CreatePathFromTracer(self, svgdom, LabelInfo):
        """
        Creates SVG path element basing on path created by tracing (from PoTrace).
        Adds SVG attributes such as fill, stoke, id, etc and append it to C{svgdom} structure.

        @type  svgdom: DOM object
        @param svgdom: SVG document - result of bitmap tracing.
                       At current stage, this document should have exactly one C{PATH}
                       element as flood fill is performed on only one place.
                       If there is more than one C{path} element, there is surely an error.

        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates.
        
        @return: Nothing, Only svgdom object is modified in-place.
        """
        
        LabelName=LabelInfo[1]
        LabelID=LabelInfo[3]
        BestGrowLevel=LabelInfo[2]
        
        # Iterate over path elements in resulting file, extract each path, add
        # some attributes - just modyfying and simplyfying path definition at
        # in-place:
        # notice that arbitrary number of path elements is assumed but it is
        # better not to use this feature as all paths would have the same id
        # (they are created basing on the same text element)
        
        # Check if the number of paths is larger than 1, if it is print warning
        if len(svgdom.getElementsByTagName('path'))>1:
            self._printManyPathsTracerOutputWarning(LabelName, LabelID)
        
        # Get default path settings and customize them
        # Apply fill colour which depends structure name 
        # Then assign path name (the name will include tracelevel)
        attributes=self.tracerConf['CustomTracedPathSettings']
        attributes['fill'] = self.assignFillColor(LabelName)
        attributes['bar:growlevel'] = "%d" % (BestGrowLevel)
        
        # Iterate over each path in tracer results
        # (as we still assume that tracing result may consist of more than one
        # separate regions)
        for path in svgdom.getElementsByTagName('path'):
            # Apply boudary growing metadata and assign uniqe ID
            #TODO: Create traced path ID template
            attributes['id']="structure%d_%s_%s" %\
                    (self.StructuresIterator, LabelID, LabelName)
            self.StructuresIterator+=1
            
            print >>sys.stderr,"\tProcessing path %s" % attributes['id']
            
            # If there is a need, dump each traced path:
            if self.tracerConf['DumpEachStepSVG']:
                self._dumpSVGDebugPurpose(LabelInfo, svgdom)
            
            # Convert incompatibile path format (relative coordinates, long cuvre segmants)
            # to more legible format compatibile with parser
            d=path.attributes['d'].value
            path.attributes['d'].value = UnparsePath(parsePath(d))
            
            # Finally apply attributes to created path element
            for AttributeName in attributes:
                path.setAttribute( AttributeName, attributes[AttributeName] )
    
    def _printManyPathsTracerOutputWarning(self, LabelName, LabelID):
        """
        Helper function for _CreatePathFromTracer. This function is invoked when
        tracing results consist from more than one path. This situation indicates
        that apparently an error has occured and slide requires revalidating.

        @type  LabelName: string
        @param LabelName: Name of label that caused warning

        @type  LabelID:
        @param LabelID: ID of label that caused warning

        @return: None
        """
        _printRed("Warning while tracing structure with name: %s, id: %s." %\
                tuple([LabelName, LabelID]))
        _printRed("\tThere are more than one areas with the same id assigned.")
        _printRed("\tCaution and reviewing advised.")
        _printRed("\tProbably pretraced file is ambigous.")

    def _dumpSVGDebugPurpose(self, LabelInfo, svgdom):
        """
        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates.

        @type  svgdom: DOM object
        @param svgdom: Document generated by PoTrace that will be dupmed into file

        @return: None
        """

        #Aliases:
        LabelName=LabelInfo[1]
        LabelID=LabelInfo[3]
        BestGrowLevel=LabelInfo[2]
        
        print >>sys.stderr, "\t\tDumping tracing result for:"
        print >>sys.stderr, "\t\t" + LabelName
        print >>sys.stderr, "\t\t" + LabelID

        tempDumpFilename=\
                self.tracerConf['SetDebugDumpOutputDirectory']+\
                "structure%d_%s_%s.svg" % \
                (self.StructuresIterator,\
                LabelID,\
                CleanFilename(LabelName))+".svg"

        svgdom.writexml(open(tempDumpFilename, 'w'))

    def _PorcessTracerOutputString(self, TracerOutput, LabelInfo):
        """
        Change PoTrace SVG output in the way which will be usefull later:
            1. Creates DOM structure from PoTrace SVG output
            2. Creates single path segments instead of long bezier paths
            3. Converts path coordinates to absolute
            4. Reduces transformation rules (using my own L{svgfix<svgfix>} module :)

        @type  TracerOutput: string
        @param TracerOutput: PoTrace SVG output string

        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates.

        @return: SVG XML DOM stucture generated from PoTrace SVG output string.
        """
        # Create DOM object and fix paths in SVG document
        svgdom = dom.parseString(TracerOutput)
        self._CreatePathFromTracer(svgdom, LabelInfo)

        # Apply file simplification with some custom options
        svgfix.fixSvgImage(svgdom, fixHeader=False)

        return svgdom
    
    def selectBestGapFillingLevel(self, area):
        """
        Selects the best level of "gap filling" by analyzing number of flooded pixels
        for each "gap filling" level.
        
        Algorithm used for selecting best level is totally heuristic and relies
        on assumption that willing each gap is equivalent to rapid lowering of number of
        flooded pixels (as we have smaller region after closing the gap than before).
        
        Algorithm tries to search for such rapid changes and prefers smaller structures
        rather than larger.
        
        If number of flooded pixels do not changes rapidly across different levels of
        gap filling it means that most probably structure do not have any gaps.
        In such case, algorithm selects region defined without using "gap filling".
        
        There are several cases defined for detecting one, two and more gaps fills.
        You should be noted that algorithm do not exhaust every possible case and
        reconstructed structures should be reviewed manually.
        
        @type  area: list of integers
        @param area: Structure size defined by number of flooded pixels.
                     Each value for consecutive "gap filling" level.
        
        @return: integer. Gap filling level considered as the most proper.
        """
        
        a=area
        # Case 1.
        # All areas are simmilar
        # Percentage difference between two consecutive areas is less than x%
        if self._areNearlyTheSame(area,0.02):
            return 0
        
        # Case 2.
        # First area is about 1.2 times larger than the second. (step)
        # Second and next are nearly the same as third and further
        # Take the second
        if a[0]>=1.2*a[1] and self._areNearlyTheSame(a[1:],0.02):
            return 1
        
        # Case 4.
        # handling rapid jump to near-zero value
        # If, after second filtering area falls to near-zero in comparison with
        # previous fill, it means that filling was too large 
        if a[1]>=20*a[2] and\
                self._areNearlyTheSame(a[0:2],0.02) and\
                self._areNearlyTheSame(a[2:],0.02):
            return 1
        
        # Case 3.
        # First two are nearly the same and ~1.2 larger than other
        # 3rd and next are nearly the same
        # One region of overgrown take 3rd.
        if a[1]>=1.2*a[2] and\
                a[1]>=10*a[2] and\
                self._areNearlyTheSame(a[0:2], 0.02) and\
                self._areNearlyTheSame(a[2:] , 0.02):
            return 2
        
        # None of above return 1 to be at the safe side
        return 1
    
    def _areNearlyTheSame(self, TestList, Treshold):
        """
        Checks if elements "are nearly the same" - if they are quotient
        of consecutive items are less than given treshold:
        (a2/a1, a3/a2,...) > Treshold.
        
        @type  TestList : list
        @param TestList : List of elements to check relations between elements
        @type  Treshold : float
        @param Treshold : Threshold. Treshold value has to be larger than 0.
        @return         : Boolean value
        """
        # Create temporary list of quotient if consecutive elements: (a2/a1, a3/a2,...)
        temp = map(lambda x,y: float(x)/float(y)-1, TestList[:-1], TestList[1:])
        
        # Check if all elements are withing given treshold
        return all( x <= Treshold and x >= -Treshold for x in temp)
    
    def _ExtractSingleStructure(self, LabelInfo, isWholeBrain = False, holdTracing = False, AllowTracing = False):
        """
        Extracts one area defined by coordinates of the given text label.
        Performs automatic grow level selection, scales the output path the way it fits to initial image
        and finally creates SVG path element with additional metadata.

        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates.

        @type  isWholeBrain: Booleam
        @param isWholeBrain: True if given structure represents whole brain, False otherwise.
        
        @return: (DOM object) List of traced SVG path elements (however, it should
                 be only one element - more than onle path elements means that
                 this structure is inproperly defined)
        """
        LabelCoords   = LabelInfo[0]
        LabelName     = LabelInfo[1]
        BestGrowLevel = LabelInfo[2]
        LabelID       = LabelInfo[3]
        
        # Print information which structure are we currently processing
        print >>sys.stderr,"Creating representation of structure %s" % LabelName
            
        # If pretraced image has information about desired growlevel,
        # use this information, otherwise determine what tracelevel is the best one
        if BestGrowLevel==-1:
            # Get area covered by each fill then choose best growlevel
            area=self._getCoveredAreasList(LabelInfo)
            BestGrowLevel=self.selectBestGapFillingLevel(area)
        else:
            pass
        
        if __debug__:
            print >>sys.stderr, "\tSelected best grow level:\t" + str(BestGrowLevel)
    
        if not holdTracing:
            self.BestGrowList.append(BestGrowLevel)
        
        # Create image for tracing by flooding grown image at given coordinates
        ImageForTracing=self._ApplySingleFill(\
                self.imageCache[BestGrowLevel],\
                BestGrowLevel,\
                LabelInfo,\
                ForTracing=True).point([0]+255*[255])
        #ImageForTracing.save("contour1.png", "PNG")
        
        if isWholeBrain:
            try:
                self.brainContourImage
            except:
                self.brainContourImage =  ImageChops.constant(ImageForTracing, 255)

            # Save brain contour to further comparison
            # Apply treshold eliminating all non-black pixels
            self.brainContourImage = ImageChops.multiply(ImageForTracing.point([0]+255*[255]), self.brainContourImage)
            if holdTracing: return

        if isWholeBrain and AllowTracing:
            ImageForTracing = ImageOps.invert(self.brainContourImage)
            #ImageForTracing = self.brainContourImage
            #ImageForTracing.save("contour3.png", "PNG")
            #self.brainContourImage.save("contour2.png", "PNG")

        #TODO: unfortunate dirty patch: we need to update LabelInfo list with
        #XXX:  current grow level (BestGrowLevel). This needs to be changed:
        LabelInfo=(LabelCoords, LabelName, BestGrowLevel, LabelID)
        
        # Dump filled bitmap for debug purposes
        if self.tracerConf['DumpEachStepPNG']:
            self.saveDebugTracerImage(LabelName, LabelCoords, ImageForTracing)
        
        # Send flooded image for tracing and read tracer output
        TracerOutput=self._DoTracing(ImageForTracing)
        svgdom=self._PorcessTracerOutputString(TracerOutput, LabelInfo)
        
        # Update whole brain contour marking flooded area.
        # TODO: Explain what is happening here!
        if not isWholeBrain:
            self.brainContourImage=ImageChops.darker(self.brainContourImage,ImageForTracing.point([100]+255*[255]))

        # There should be only one path in traced bitmap
        # However, arbitrary number of path elements is allowed but it is
        # strongly recommended not to use more than one path
        return svgdom.getElementsByTagName('path')

    def saveDebugTracerImage(self, LabelName, coords, ImageForTracing):
        """
        @type  LabelName: string
        @param LabelName: Name of the label being dupmed
        
        @type  coords: tuple of two integers
        @param coords: Coordinates of seed in rasterized image coordinate system
        
        @type  ImageForTracing: PIL image
        @param ImageForTracing: Image that will be dumped
        
        @return: None
        """
        # get width and haight atlases:
        (width, height) = self.tracerConf['imageSize']
        
        # generate filename
        tempDumpFilename=\
            self.tracerConf['SetDebugDumpOutputDirectory']+\
            'slide_'+ str(self.tracerConf['slidenumber'])+'_'\
            'debug_filled_'+\
            CleanFilename(LabelName)+\
            '_%d_%d.png' % coords
        
        # Resize and save the resized image (resizing is performed in order to avoid
        # transfering enormuns files over internet
        print tempDumpFilename
        ImageForTracing.resize((width/2, height/2)).\
            save(tempDumpFilename, "PNG")
    
    def assignFillColor(self, structureName):
        """
        Assigns fill color for structure with given name. Fill colour is determined
        by structureName. If no colour is matched to given structure, black color
        is returned.
        
        @type  structureName: string
        @param structureName: structure acronym that will be used in order to
                              determine fill colour.
        @return: None
        """
        
        try:
            return "#"+self.tracerConf['DefaultFillColour'][structureName]
        except:
            _printRed("Error: color for structure %s not found."\
                            % structureName)
            _printRed("Black fill color assigned instead.\n" +\
                            "Review color mapping and try again.")
            return "#000000"

    def traceUnlabeledAreas(self):
        """
        Creates list of paths and corresponding labels by tracing areas that were not
        labeled in pretraced files (unlabeled areas). This process is rather complicated
        so few words of explanation:

            1. We look for patches of N or more pixels. Only sych areas
               are considered as unlabelled areas. Smaller areas are most
               probably residual white pixels and should be ommited.
            2. Every group of two or more adjacent white pixels is flooded
               on "1".
            3. Patch of N or more white pixels is flooded with value "2"
               after tracing.

        After fiding unlabelled areas we can find 4 values of pixels:

            1. "0": areas outside brain
            2. "1": pixels of more than one adjacent pixels bu less than N
            3. "2": patches of N or more white pixels
        """
        
        # Two types of elements are collected: patch covering unlabelled areas
        # and corresponding labels
        unlabeledAreasList=[]              # Here we hold all paths
        self.unlabeledAreasLabelsList=[]   # Here we hold all labels. Because we to return
                                           # only list of path, labels are stored
                                           # inside the structure.
        whiteCoordList=[]                  # List of coordinates white pixels. Coordinates
                                           # are corrected in on order to avoid analyzing
                                           # the same coordinates twice.
        coords = self.findUnlabeledAreas() # Get initial white pixel coordinate and start loop
        
        while coords and (coords not in whiteCoordList):
        
            # Flood image at give coordinates. "1" index is used, not "0". Also get number
            # number of flooded pixels.
            numberOfFloodedPixels = self.floodFillScanlineStack(self.brainContourImage, coords, 1)
            
            whiteCoordList.append(coords) # Append coordinates to list in order
                                          # to avoid duplication
            
            # When more than N pixels is flooded we should consider this area as
            # an actual unlabelled area (not some residual single white pixels)
            # and we should start tracing procedure.
            if numberOfFloodedPixels > 500:
            
                # Replace colors to get image suitable for tracing:
                # all colors are converted to white. Values "1" are converted to "0"
                # so the structure is black and surroundings are white
                ImageForTracing = self.brainContourImage.point([255]+[0]+254*[255])
                
                # Apply minimum filter to slightly increase size of trace structures.
                ImageForTracing = ImageForTracing.filter(ImageFilter.MinFilter(3))
                TracerOutput = self._DoTracing(ImageForTracing)
                
                # Generate data needed to create SVG text element required to traced
                # and pretraced file
                LabelInfo=[]
                LabelInfo.append(image_process.getBestLabelLocation(ImageForTracing))
                LabelInfo.append('Unlabeled')
                LabelInfo.append(0)
                LabelInfo.append('Unlabeled-%d-%d' % coords)
                
                # Create SVG path element from traced path and LabelInfo data
                svgdom = self._PorcessTracerOutputString(TracerOutput, LabelInfo)
                
                # Apped traced path to list of all traced paths.
                unlabeledAreasList.append(svgdom.getElementsByTagName('path'))
                # Append SVG text element to list of new labels.
                self.unlabeledAreasLabelsList.append(self.createLabelElement(LabelInfo))
            
            # Finally, do some trick: replace all pixels with value "1" to "2",
            # which prevents from accumulating consecutive areas.
            numberOfFloodedPixels = self.floodFillScanlineStack(self.brainContourImage, coords, 2)
            
            # Get new coordinates and cotinue loop
            coords = self.findUnlabeledAreas()
        
        # Dump image after tracing unlabelled areas to show what we have done! :)
        # self.brainContourImage.save("after_tracing_%d.png"% self.tracerConf['slidenumber'], "PNG")

        return unlabeledAreasList

    def findUnlabeledAreas(self):
        """
        Finds white pixels in the image. If found pixel has white neighbourhood,
        its coordinates are returned, otherwise iteration continues
        until all white pixels are spotted.

        Current algorithm is rather ineffective. Main reason is that function has to exit
        if patch of white pixels is spotted. Then function is invoked again and iteration starts
        from beginning which is exttremely ineffective. What should be done in such case?
        Perhaps implementation should include iterator. The problem is that we need to change array
        while we iterate over this array.

        return: (x,y) image coordinates of first spotted pixel that belongs to patch
        (two or more adjecent pixeles) of white pixels. If there is no such pixel,
        C{None} is returned.
        """

        # Access image pixel by pixel
        pix = self.brainContourImage.load()

        # Holds current pixel number
        pn=0

        # Iterate over all image
        for i in self.brainContourImage.getdata():
            pn+=1
            # If white pixel is spotted, check if it belongs to group of adjacent white pixels.
            # If it belongs, return coordinates of the pixel. If not, continue iteration.
            if i==255:
                y = pn //self.brainContourImage.size[1]
                x = pn % self.brainContourImage.size[1]-1
                #print "White pixel found at coords %d,%d" % (x,y)
                if pix[x-1,y]==255 and pix[x+1,y]==255 and pix[x,y+1]==255 and pix[x,y-1]==255:
                    #self.brainContourImage.save("q%d_%d.png"% (y,x), "PNG")
                    return (x,y)
        return None

    def getLabelTemplate(self, svgdom):
        """
        @type  svgdom: DOM object 
        @param svgdom: DOM object representing pretraced file. It is assumed that it has
                       at least one text element
        @return: None

        Caches first text element from svg dom as a label template for generating new labels.
        """
        self.labelTemplate = svgdom.getElementsByTagName('text')[0].cloneNode(deep=True)

    def createLabelElement(self, LabelInfo):
        """
        Creates SVG text element with properties taken from LabelInfo list
        (properties: (x,y) coordinates, Structure name, tracelevel, id).

        @type  LabelInfo: nested list
        @param LabelInfo: List with label and its coordinates

        @return: SVG text element containing data from LabelInfo

        Creates SVG text element with properties taken from LabelInfo list
        (properties: (x,y) coordinates, Structure name, tracelevel, id).
        """
        newLabelElement = self.labelTemplate.cloneNode(deep=True)

        x, y = self._ToSVGCoordinates(LabelInfo[0])
        name = LabelInfo[1]
        TraceLevel = LabelInfo[2]
        id = LabelInfo[3]

        newLabelElement.setAttribute('x', str(x))
        newLabelElement.setAttribute('y', str(y))
        newLabelElement.firstChild.nodeValue = name
        newLabelElement.setAttribute('bar:growlevel',str(TraceLevel))
        newLabelElement.setAttribute('id',id)

        return newLabelElement


def _isVariableDefined(variable):
    """
    @type  variable: Any python object
    @param variable: Variable that will be checked

    @return: True, if given variable is defined, false otherwise.

    Checks, if passed variable is correctly defined.
    """
    try:
        variable
    except:
        return False
    return True

def _printRed(str):
    """
    @type  str: string
    @param str: String to print to stderr in red.
    @return   : Nothing, just prints the string.

    Prints given string to stderr using red color.
    """
    print >>sys.stderr, '\033[0;31m%s\033[m' % str

def getTextnodesInfo(svgdom):
    """
    @type  svgdom: DOM object
    @param svgdom: Whole SVG document
    
    Creates lists of information extracted from all text labels in document via
    via L{ParseSingleTextnode<ParseSingleTextnode>}.
    
    @return: List of L{ParseSingleTextnode<ParseSingleTextnode>} results.
    """
    
    TextNodes=[];
    for el in svgdom.getElementsByTagName('text'):
        TextNodes.append(ParseSingleTextnode(el))
    return TextNodes

def ParseSingleTextnode(TextNode):
    """
    @type  TextNode: DOM elemnet
    @param TextNode: test DOM object - label which denotes the structure.
    
    Extracts coordinates of given text labes, its value and additional metadata.
    At this moment C{metadata} consists only with C{bar:tracelevel} attribute value.
    However, it might be changed in further updates.
    
    @return: ((x,y),text,metadata,id
    """
    x, y = float(TextNode.attributes['x'].value), float(TextNode.attributes['y'].value)
    TraceLevel = int(TextNode.getAttribute('bar:growlevel'))
    Id = TextNode.getAttribute('id')
    
    return (\
        (x,y),\
        str(TextNode.firstChild.nodeValue),\
        TraceLevel,\
        Id)

def ExtractAllPaths(svgdom, slidenumber):
    """ 
    Traces given image according to provided list of labels.
    Supplements passed SVG DOM with traced paths.
    
    Description step by step:
        1. Clone original SVG document,
        2. Create GrowFill class instance
        3. Extract each structure from provoded list
        5. Put extracted structures into DOM structure
        5. Perform minor fixes.
    
    @type  svgdom: DOM object
    @param svgdom: Original SVG drawing sutiable for path tracing (cleaned, with matched arrow, etc.).
                   In the other words: correct pretraced file.

    @type  slidenumber: int
    @param slidenumber: Number of currently parsed slide.
    
    @return: DOM object with paths traced according to provided labels list and initial SVG drawing
             modified by changing default growlevels: C{(newSVG,origSVG)}
    
    @bug: slidenumber Argument should be eliminated and actual slide number should be
          extracted from the SVG file metadata. 
    """
    # Remove labels denoting unlabeled areas:
    for label in svgdom.getElementsByTagName('text'):
        if label.firstChild.nodeValue=='Unlabeled':
            label.parentNode.removeChild(label)
    
    # Clone SVG object (we want to leave original DOM untouched)
    WorkSVG=svgdom.documentElement.cloneNode(deep=True)
    
    # Parse textnodes
    texts=getTextnodesInfo(WorkSVG)
    
    # Define class for extracting and set class properties, finally cache slide images.
    extractor=GrowFill(WorkSVG)
    setTracerProperties(extractor)
    extractor.setProperty('slidenumber', slidenumber) #TODO: Put slidenumer as metadata
    extractor.setProperty('SetDebugDumpOutputDirectory','')
    extractor.LoadImageInit()

    # Extract label template forom svgdom:
    extractor.getLabelTemplate(svgdom)
    
    # Initialize array which holds all new paths 
    NewPaths=[]
    
    # XXX Very dirty trick it should be written better :)
    # Extract all vBrain structures and create complex image by merging consecutive
    # selections.
    [ extractor._ExtractSingleStructure(label, isWholeBrain=True, holdTracing=True) for label in texts if label[1]=='vBrain' ]

    # Then trace brain contour. In this case dummy label has to be passed.
    DummyvBrainLabel = [ label for label in texts if label[1]=='vBrain' ]
    NewPaths.append(extractor._ExtractSingleStructure(DummyvBrainLabel[0], isWholeBrain=True, AllowTracing=True))

    # Create list of labels without vBrain labels - just for tracing regular structures.
    RegularLabels = [ label for label in texts if label[1]!='vBrain' ]
    
    # And now handle regular structures
    i=0 # stupid iterator
    for RegularLabel in RegularLabels:
        i+=1 # increment stupid iterator
        # Print debuging information if required
        if extractor.tracerConf['DumpDebugInformation']:
            print >>sys.stderr,""
            print >>sys.stderr,"Extracting structure %d of %d (%s)" % (i, len(RegularLabels), RegularLabel[1])
            print >>sys.stderr,"\tSVG Coords: %f,%f" % RegularLabel[0]
        
        # Skip tracing comment and spotlabels (comment labels starts with comma
        # while spotlabels starts with dot)
        if RegularLabel[1][0] in [',','.']:
            print >>sys.stderr,"\tLabel %s comment label or spot label. Skipping..." 
            continue

        # Trace path for given text label and appent it to NewPaths array
        NewPaths.append(extractor._ExtractSingleStructure(RegularLabel))
    
    # Extract unlabeled areas, but earlier apply min filter in order to remove thin residual lines
    # that left after tracing 
    extractor.brainContourImage=extractor.brainContourImage.filter(ImageFilter.MinFilter(3))
    NewPaths.extend(extractor.traceUnlabeledAreas())

    # Dump brain contour with all traced regions for determinig if all regions were traced
    # extractor.brainContourImage.save(CleanFilename("fill_"+str(slidenumber)+".png"), "PNG")

    # Insert computed tracelevels to original drawing
    _embedTracelevel(svgdom, extractor.BestGrowList)

    # Delete extractor class - frees a lot of memory
    extractor._ClearCache()
    
    # Remove initial paths, Restore initial labels
    DoFinalProcessing(svgdom, WorkSVG, NewPaths, extractor.unlabeledAreasLabelsList)

    del extractor
    
    return (WorkSVG,svgdom)

def setTracerProperties(extractorClassInstance):
    """
    Sets all important parameters of extractor class. All those parameters
    should be defined as constants in ie. external configuration file. Be awared
    that configuarion parametes may be various python, not only strings. It is
    especially important when one plans to import configuration from text file.
    
    Description of configuration parameters:
    cachelevel: (integer) Number of chached images (number of growth levels +1).
    Ie. if cacheLevel=4, there would be 5 images chached - first would be the
    original image, next: images with succesive growth.
    
    imageSize: (tuple of two integers), Defines size of rendered SVG image:
    (width, height)

    TagsToClean: (list of strings) List of tag names that will be removed
    in order to make the image suitable for tracing. In this list one should put
    text, rect, line, arc, etc. and all other unnecesarry elements.

    ReferenceWidth, ReferenceHeight: (Integer): Width and height of
    non-rasterized SVG image

    GrowDefaultBoundaryColor: Integer from range of (0-255)
    GrowDefaultBoundaryColor: Color for which all boundary pixels will be converted

    MinFiterTimesApplication: (Integer) PIL Min filter parameter -
    very important for  boundary growing procedure.

    PotraceAccuracyParameter, PotraceSVGResolutionString,
    PotraceWidthString, PotraceHeightString: PoTrace configuration options.
    For further details, read PoTrace manual.

    DumpEachStepSVG, DumpEachStepPNG: (boolen) Save SVG/PNG files for every structure?
    DumpDebugInformation: (boolean) Print information about currently traced structure with
    some additional information.

    SetDebugDumpOutputDirectory: (string) Directory in which debuging information
    will be stored. It is convinient to use the same dictionary in which raw files are stored.
    """
    # Basic configuration:
    extractorClassInstance.setProperty('cacheLevel',      CONF_TRACER_CACHE_LEVEL )
    extractorClassInstance.setProperty('imageSize',       CONF_TRACER_IMAGE_SIZE  )
    
    # SVG rasterization options:
    extractorClassInstance.setProperty('TagsToClean',     CONF_TRACER_TAGS_TO_CLEAN   )
    extractorClassInstance.setProperty('ReferenceWidth' , CONF_TRACER_REFERENCE_WIDTH )
    extractorClassInstance.setProperty('ReferenceHeight', CONF_TRACER_REFERENCE_HEIGHT)
    
    extractorClassInstance.setProperty('GrowDefaultBoundaryColor',\
        CONF_GROWFILL_DEFAULT_BOUNDARY_COLOUR)
    
    extractorClassInstance.setProperty('MinFiterTimesApplication', 3)
   
    # PoTrace properties
    extractorClassInstance.setProperty('PotraceAccuracyParameter'  , CONF_POTRACE_ACCURACY_PARAMETER   )
    extractorClassInstance.setProperty('PotraceSVGResolutionString', CONF_POTRACE_SVG_RESOLUTION_STRING)
    extractorClassInstance.setProperty('PotraceWidthString'        , CONF_POTRACE_WIDTH_STRING)
    extractorClassInstance.setProperty('PotraceHeightString'       , CONF_POTRACE_HEIGHT_STRING)

    # Path generation properties
    extractorClassInstance.setProperty('CustomTracedPathSettings', CONF_TRACER_CUSTOM_PATH_SETTINGS)
    extractorClassInstance.setProperty('DefaultFillColour',        CONF_FILL_COLOURS)
    extractorClassInstance.setProperty('RegionAlreadyTraced',        100)
    
    # Debugging settings
    extractorClassInstance.setProperty('DumpEachStepSVG', False)
    extractorClassInstance.setProperty('DumpEachStepPNG', False)
    extractorClassInstance.setProperty('DumpDebugInformation', True)
    extractorClassInstance.setProperty('DumpWrongSeed', False)
    
def DoFinalProcessing(SourceSVG, OutputSVG, NewPaths, NewLabels = []):
    """
    @type  SourceSVG: DOM object
    @param SourceSVG: Original SVG drawing sutiable for path tracing
                      from which text labels will be copied to new SVG drawing.
    
    @type  OutputSVG: DOM object
    @param OutputSVG: Newly created SVG drawing that will be returned as output of tracing.
    
    @type  NewPaths: List of DOM objects
    @param NewPaths: List of traced paths. Those paths need to be merged with C{OutputSVG} structure. 

    @type  NewLabels: List of DOM objects
    @param NewLabels: List of Newly created paths that were not present in pretraced file.
                      In most cases those labels denotes areas that were unlabeled

    @return: None. All DOM objects are passed by reference and modified in-place.

    Performs final correction to the file:
        1. Removes initial paths as they are no longer needed
        2. Appends newly generated paths 
        3. Restores initial labels (they were removed as they obstructed path tracing)
    """

    mainGroup=OutputSVG.getElementsByTagName('g')[0]
    mainSourceGroup=SourceSVG.getElementsByTagName('g')[0]
    for newPathGroup in NewPaths:
        for newPath in newPathGroup:
            mainGroup.appendChild(newPath)

    # Restore original labels:
    # We copy labels from pretraced doccument to traced SVG document because
    # we want to preserve original labels (they locations and properties)
    for label in SourceSVG.getElementsByTagName('text'):
        mainGroup.appendChild(label.cloneNode(deep=True))

    # Insert new labels (usually labels for unlabeled areas):
    # New labels are inserted to traced file as well as pretraced file
    for label in NewLabels:
        mainGroup.appendChild(label.cloneNode(deep=True))
        mainSourceGroup.appendChild(label.cloneNode(deep=True))

    # Remove non structure-path elements from WorkSVG document
    # = remove paths without propetly definied id attribute
    for pathElement in OutputSVG.getElementsByTagName('path'):
    #   try:
        if not hasProperStructureIdValue(pathElement):
            pathElement.parentNode.removeChild(pathElement)
    #   except:
            # TODO Put error information here
    #       pass

def hasProperStructureIdValue(pathElement):
    """
    Checks if given path element has properly defined structure name
    (according to pathID naming scheme)
    """
    if str(pathElement.getAttribute('id').split('_')[0]).startswith('structure'):
        return True

    return False

def CleanFilename(filename):
    """
    Strip filename from prohibited characters.
    Prohibited characters are replaced by underscore characted.

    @type  filename : string
    @param filename : filename to strip
    @return         : corrected filename
    """
    return filename.replace('/','_')
    
if __name__=='__main__':
    pass
