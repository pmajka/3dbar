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
The module provides functions to handle basic image processing.

G{importgraph}
"""
import unittest
import numpy as np
from PIL import Image,ImageOps,ImageDraw
import cStringIO,  subprocess
from scipy.ndimage.morphology import distance_transform_edt as dtransform
import scipy.ndimage as ndimage
import colorsys

def tonpArray(PILImage):
    """
    @type  PILImage: PIL image instance
    @param PILImage: Image that should be converted into np array.
                     Image should be in grayscale (indexed) mode.
    @return: array corresponging to provided image
    """
    a = np.asarray(PILImage)
    return a

def distance_transform(bitmap):
    """
    @type  bitmap: np array
    @param bitmap: image for which distance transform will be calculated
    
    @return: np array holding distance transform of provided bitmap
    
    Calculates distance transtofm of provided bitmap. This function is wrapper
    for actual distance transform.
    """
    return dtransform(bitmap)

def getBestLabelLocation(ImageForTracing):
    """
    @type  ImageForTracing: PIL image
    @param ImageForTracing: Image to calculate distance transform

    @return: tuple of two integers (x,y): coordinates of best-placed label

    Calculates coordinates corresponding to visual-center of given area defined
    by black pixels. "visual-center" means: 'looks like is is in the center of
    the structure". Coordinates of central points are calculated basing on
    maximum of distance transform: Central point coordinate = location of
    distance transform's maximum.

    Input bitmap: object: black, background: white
    Used to dtransform: obj. white, bg - black
    """
    ImageForTracing = ImageOps.invert(ImageForTracing)
    Imbbox = ImageForTracing.getbbox()
    
    # We need to provide frame with background color ensure proper results
    Imbbox = tuple(np.array(Imbbox) + np.array([-1, -1, 1, 1]))

    # Crop input image so distance transform is not calculated only in essential
    # part of the image. Plain backgroud area is skipped.
    CroppedImTracing = ImageOps.invert(ImageForTracing.crop(Imbbox).convert("L") )
    CroppedImTracing = ImageOps.invert(CroppedImTracing)

    # Cacluate distance transform and extract its maximum.
    distanceTransform = dtransform(tonpArray(CroppedImTracing))
    (y,x) = ( distanceTransform.argmax() // distanceTransform.shape[1] ,\
            ( distanceTransform.argmax() % distanceTransform.shape[1] ))

    # Take into account that initial image was cropped -> return to original
    # image coordinates
    x,y = x+Imbbox[0],y+Imbbox[1]

    return (x,y)

def massCentre(bitmap):
    """
    the bitmap should be binary image
    """
    binaryImage = bitmap.point(255*[255]+[0])
    return ndimage.measurements.center_of_mass(tonpArray(binaryImage))

def savitzky_golay(y, window_size, order, deriv=0):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techhniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv]
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m, y, mode='valid')

def performTracing(binaryImage, tracingProperties, dumpName = None):
    """
    Perform image tracing via potrace and pipes mechanism.
    
    Assumes that image is a grayscale image with only two colours used: black
    and white. Black colour is considered as foreground while white colour is
    background colour. The foreground is assumed to be a non-separable area.
    
    This function do not perform parsing the output.
    
    Tracing Workflow:
        1. Save image in bmp format in dummy string
        2. Send bmp string to potrace via pipe mechanism
        3. Perform tracing
        4. Read tracing output via pile
        5. Return raw tracing output
    
    @type  binaryImage: PIL.Image.Image
    @param binaryImage: flooded image for tracing
    
    @return: raw tracing output string
    @rtype: str
    """
    
    # Create file-like object which handles bmp string
    ImageString = cStringIO.StringIO()
    
    # Save image to this file-like object
    binaryImage.save(ImageString, "BMP")
    if dumpName: binaryImage.save(dumpName, "BMP")
    
    # Create process pipes
    # potrace parameters:
    # -s for settring SVG output
    # -O Optimization parameter
    # -r SVG Image resolution in DPI
    # -W,H Output dimensions of SVG drawing
    # -o - - Input and output via pipes
    commandLineParams = ['potrace',\
            '-s',\
            '-O', tracingProperties['potrace_accuracy_parameter'],\
            '-r', tracingProperties['potrace_svg_resolution_string'],\
            '-W', tracingProperties['potrace_width_string'],\
            '-H', tracingProperties['potrace_height_string'],\
            '-o','-','-']
    
    # potrace_turdsize is an optional parameter
    if 'potrace_turdsize' in tracingProperties:
        commandLineParams.insert(2, str(tracingProperties['potrace_turdsize']))
        commandLineParams.insert(2, '-t')
    
    process = subprocess.Popen(commandLineParams,\
              stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    # Pass bmp string to pipe, close image string.
    process.stdin.write(ImageString.getvalue())
    ImageString.close()
    
    # Read and return tracing output
    return  process.stdout.read()

def floodFillScanlineStack(image, xy, value):
    """
    Custom floodfill algorithm that replaces original PIL ImageDraw.floodfill().
    This algorithm appears to be twice as fast as the original algorithm and more
    roboust. This algorithm requires reimplementing in C/Fortran and connecting
    to python somehow. Implementation is based on:
    http://www.academictutorials.com/graphics/graphics-flood-fill.asp
    
    This is implementaion on scanline floodfill algorithm using stack. The
    algorithm is not described here. To get insight please consult google using
    'floodfill scanline'.
    
    @note: Please note that this algorithm assume that floodfilled image is in
           indexed colour mode.
    
    @type  image: PIL.Image.Image
    @param image: image on which floodfill will be performed
    
    @type  xy: (int, int)
    @param xy: coordinates of floodfill seed
    
    @type  value: int
    @param value: fill colour
    
    @rtype: int
    @return: number of pixels with changed color (area of floodfill)
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
    
    return npix                    

def selectBestGapFillingLevel(area):
    """
    Select the best level of "gap filling" by analyzing number of flooded pixels
    for each "gap filling" level.
    
    Agorithm used for selecting best level is totally heuristic and relies
    on assumption that filling each gap is equivalent to rapid lowering of number of
    flooded pixels (as we have smaller region after closing the gap than before).
    
    Algorith tries to seach for such rapid changes and prefers smaller structures
    rather than larger.
    
    If number of flooded pixels do not changes rapidly across different levels of
    gap filling it means that most probably structure do not have any gaps.
    In such case, algorithm selects region defined without using "gap filling".
    
    There are several cases defined for detecting one, two and more gaps fills.
    You should note that algorithm do not exhaust every possible case and
    reconstructed structures should be reviewed manually.
    
    @type  area: [int, ...]
    @param area: structure size defined by number of floodfilled pixels
                 (each value for consecutive "gap filling" level)
    
    @rtype: int
    @return: gap filling level considered to be the most proper
    """
    
    a=area
    # Case 1.
    # All areas are simmilar
    # Percentage difference between two consecutive areas is less than x%
    if _areNearlyTheSame(area,0.02):
        return 0
    
    # Case 2.
    # First area is about 1.2 times larger than the second. (step)
    # Second and next are nearly the same as third and further
    # Take the second
    if a[0]>=1.2*a[1] and _areNearlyTheSame(a[1:],0.02):
        return 1
    
    # Case 4.
    # handling rapid jump to near-zero value
    # If, after second filtering area falls to near-zero in comparison with
    # previous fill, it means that filling was too large 
    if a[1]>=20*a[2] and\
            _areNearlyTheSame(a[0:2],0.02) and\
            _areNearlyTheSame(a[2:],0.02):
        return 1
    
    # Case 3.
    # First two are nearly the same and ~1.2 larger than other
    # 3rd and next are nearly the same
    # One region of overgrown take 3rd.
    if a[1]>=1.2*a[2] and\
            a[1]>=10*a[2] and\
            _areNearlyTheSame(a[0:2], 0.02) and\
            _areNearlyTheSame(a[2:] , 0.02):
        return 2
    
    # None of above return 1 to be at the safe side
    return 1


################################################################################ 
##  Code below not used in 3dBAR yet - it is just for testing purposes        ## 
##  and, well.. it's experimental...                                          ## 
################################################################################ 

def rgb(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)

if __name__ == '__main__':

    import config
    for color in config.CONF_FILL_COLOURS.items():
            c = rgb(color[1])
            H = colorsys.rgb_to_hsv(c[0]/255.,c[1]/255.,c[2]/255.)
            H = map( lambda x: int(x*256) , H)
            print "%s\t%d\t%d\t%d\t%d\t%d\t%d" % (color[0],c[0],c[1],c[2],H[0],H[1],H[2])

    exit(1)
    """
    class TestCase1(unittest.TestCase):

        def testRect(self):
            im = Image.new("L", (300, 300), 255)
            draw = ImageDraw.Draw(im)
            draw.rectangle((100, 100, 200, 200), fill = 0)
            labelLocation = getBestLabelLocation(im)
            
            self.assertEqual(str(labelLocation),'(150, 150)')

        def testEllipse(self):
            im = Image.new("L", (300, 300), 255)
            draw = ImageDraw.Draw(im)
            draw.ellipse((100, 100, 200, 200), fill = 0)
            labelLocation = getBestLabelLocation(im)
            
            self.assertEqual(str(labelLocation),'(150, 149)')
        
        def testPoly1(self):
            im = Image.new("L", (300, 300), 255)
            draw = ImageDraw.Draw(im)

            polygonPoints =\
                    (\
                    10,10,  10,300,  300,300,  150,250,  20,20\
                            )

            draw.polygon(polygonPoints, fill = 0)
            labelLocation = getBestLabelLocation(im)
            
            self.assertEqual(str(labelLocation),'(72, 237)')
    """

    #unittest.main()

    #im1 = Image.open('47.tiff').convert('L')
    #im2 = Image.open('48.tiff').convert('L')
    a1 = tonpArray(Image.open('../85.tiff').convert('L')).copy()
    a2 = tonpArray(Image.open('../86.tiff').convert('L')).copy()
    
    a1[a1>10] = 40
    a1[a1<=10]= 0
    a2[a2>10]=90
    a2[a2<=10]=0
    np.savetxt('a1.out', a1)
    np.savetxt('a2.out', a2)
    a1a2=np.logical_xor(a1,a2)
    np.savetxt('a1a2.out',numpy.logical_xor(a1,a2))
    print np.unique(numpy.logical_xor(a1,a2))
    print np.unique(a1)
    print np.unique(a2)
    footprint = ndimage.generate_binary_structure(2, 1)
    cnt1 = a1 - ndimage.grey_erosion(a1, footprint=footprint)
    cnt2 = a2 - ndimage.grey_erosion(a2, footprint=footprint) 
    cnt =  cnt1+cnt2
    cnt[cnt==np.amax(a1)+numpy.amax(a2)]= numpy.amax(a1)
    np.savetxt('cnt.out', cnt)

    np.savetxt('ics.out', a1a2)

    icscnt = a1+a2
    icscnt[a1a2!=0] = 255
    icscnt[icscnt!=255] = 0
    icscnt[cnt!=0] = cnt[cnt!=0]
    np.savetxt('start.out', icscnt)
    print np.unique(icscnt)

    w = icscnt
    t = a1a2
    i=0
    while np.max(w[a1a2])==255:
        wold = w
        w = ndimage.grey_erosion(wold,size=(2,2), footprint=footprint)
        w[wold!=255] = wold[wold!=255]
        np.savetxt('%d.out' % (i), w)
        print np.unique(w)
        i+=1

    print i
    np.savetxt('%d.out' % (i), w)


    #w[t==0]=0
    mh = np.zeros(w.shape)
    ml = np.zeros(w.shape)
    ml[w==40] = 40
    mh[w==90] = 90

    ml = ndimage.grey_dilation(ml,size=(2,2), footprint=footprint)
    mh = ndimage.grey_dilation(mh,size=(2,2), footprint=footprint)

    np.savetxt('mh.out', mh)
    np.savetxt('ml.out', ml)
    v = np.logical_and(ml,mh)


    np.savetxt('fin.out', v)
    """
    footprint = ndimage.generate_binary_structure(2, 1)
    cnt1 = a1 - ndimage.grey_erosion(a1, footprint=footprint)
    cnt2 = a2 - ndimage.grey_erosion(a2, footprint=footprint) 
    cnt =  cnt1+cnt2
    print np.unique(cnt)
    np.savetxt('start.out', cnt1+cnt2)
    a1[a1>10] = 40
    a1[a1<=10]= 0
    a2[a2>10]=90
    a2[a2<=10]=0

    sum = a1+a2
    sum[np.logical_xor(a1,a2)]=255
    sum[np.logical_and(a1,a2)]=0
    sum[sum<255]=0
    np.savetxt('ics.out', sum)
    print np.unique(sum)

    sum[cnt!=0]=cnt[cnt!=0]
    np.savetxt('go.out', sum)

    a=cnt
    t=a
    w=sum
    i=0
    while np.amax(w)==255:
        print np.amax(w)
        w[cnt!=0]=cnt[cnt!=0]
        w = ndimage.grey_erosion(w,size=(2,2), footprint=footprint) 
        np.savetxt('%d.out' % (i), w)
        i+=1

    u = ndimage.grey_dilation(w, footprint=footprint)
    u[cnt==0]=0
    np.savetxt('fin.out', w)
    """
