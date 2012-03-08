#!/usr/bin/python 
# -*- coding: utf-8 -*-
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

import unittest

import numpy
from PIL import Image,ImageOps,ImageDraw
from scipy.ndimage.morphology import distance_transform_edt as dtransform
import scipy.ndimage as ndimage
import colorsys

def toNumpyArray(PILImage):
    """
    @type  PILImage: PIL image instance
    @param PILImage: Image that should be converted into numpy array.
                     Image should be in grayscale (indexed) mode.
    @return: array corresponging to provided image
    """
    a = numpy.asarray(PILImage)
    return a

def distance_transform(bitmap):
    """
    @type  bitmap: numpy array
    @param bitmap: image for which distance transform will be calculated
    
    @return: numpy array holding distance transform of provided bitmap
    
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
    Imbbox = tuple(numpy.array(Imbbox) + numpy.array([-1, -1, 1, 1]))

    # Crop input image so distance transform is not calculated only in essential
    # part of the image. Plain backgroud area is skipped.
    CroppedImTracing = ImageOps.invert(ImageForTracing.crop(Imbbox).convert("L") )
    CroppedImTracing = ImageOps.invert(CroppedImTracing)

    # Cacluate distance transform and extract its maximum.
    distanceTransform = dtransform(toNumpyArray(CroppedImTracing))
    (y,x) = ( distanceTransform.argmax() // distanceTransform.shape[1] ,\
            ( distanceTransform.argmax() % distanceTransform.shape[1] ))

    # Take into account that initial image was cropped -> return to original
    # image coordinates
    x,y = x+Imbbox[0],y+Imbbox[1]

    return (x,y)

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
    a1 = toNumpyArray(Image.open('../85.tiff').convert('L')).copy()
    a2 = toNumpyArray(Image.open('../86.tiff').convert('L')).copy()
    
    a1[a1>10] = 40
    a1[a1<=10]= 0
    a2[a2>10]=90
    a2[a2<=10]=0
    numpy.savetxt('a1.out', a1)
    numpy.savetxt('a2.out', a2)
    a1a2=numpy.logical_xor(a1,a2)
    numpy.savetxt('a1a2.out',numpy.logical_xor(a1,a2))
    print numpy.unique(numpy.logical_xor(a1,a2))
    print numpy.unique(a1)
    print numpy.unique(a2)
    footprint = ndimage.generate_binary_structure(2, 1)
    cnt1 = a1 - ndimage.grey_erosion(a1, footprint=footprint)
    cnt2 = a2 - ndimage.grey_erosion(a2, footprint=footprint) 
    cnt =  cnt1+cnt2
    cnt[cnt==numpy.amax(a1)+numpy.amax(a2)]= numpy.amax(a1)
    numpy.savetxt('cnt.out', cnt)

    numpy.savetxt('ics.out', a1a2)

    icscnt = a1+a2
    icscnt[a1a2!=0] = 255
    icscnt[icscnt!=255] = 0
    icscnt[cnt!=0] = cnt[cnt!=0]
    numpy.savetxt('start.out', icscnt)
    print numpy.unique(icscnt)

    w = icscnt
    t = a1a2
    i=0
    while numpy.max(w[a1a2])==255:
        wold = w
        w = ndimage.grey_erosion(wold,size=(2,2), footprint=footprint)
        w[wold!=255] = wold[wold!=255]
        numpy.savetxt('%d.out' % (i), w)
        print numpy.unique(w)
        i+=1

    print i
    numpy.savetxt('%d.out' % (i), w)


    #w[t==0]=0
    mh = numpy.zeros(w.shape)
    ml = numpy.zeros(w.shape)
    ml[w==40] = 40
    mh[w==90] = 90

    ml = ndimage.grey_dilation(ml,size=(2,2), footprint=footprint)
    mh = ndimage.grey_dilation(mh,size=(2,2), footprint=footprint)

    numpy.savetxt('mh.out', mh)
    numpy.savetxt('ml.out', ml)
    v = numpy.logical_and(ml,mh)


    numpy.savetxt('fin.out', v)
    """
    footprint = ndimage.generate_binary_structure(2, 1)
    cnt1 = a1 - ndimage.grey_erosion(a1, footprint=footprint)
    cnt2 = a2 - ndimage.grey_erosion(a2, footprint=footprint) 
    cnt =  cnt1+cnt2
    print numpy.unique(cnt)
    numpy.savetxt('start.out', cnt1+cnt2)
    a1[a1>10] = 40
    a1[a1<=10]= 0
    a2[a2>10]=90
    a2[a2<=10]=0

    sum = a1+a2
    sum[numpy.logical_xor(a1,a2)]=255
    sum[numpy.logical_and(a1,a2)]=0
    sum[sum<255]=0
    numpy.savetxt('ics.out', sum)
    print numpy.unique(sum)

    sum[cnt!=0]=cnt[cnt!=0]
    numpy.savetxt('go.out', sum)

    a=cnt
    t=a
    w=sum
    i=0
    while numpy.amax(w)==255:
        print numpy.amax(w)
        w[cnt!=0]=cnt[cnt!=0]
        w = ndimage.grey_erosion(w,size=(2,2), footprint=footprint) 
        numpy.savetxt('%d.out' % (i), w)
        i+=1

    u = ndimage.grey_dilation(w, footprint=footprint)
    u[cnt==0]=0
    numpy.savetxt('fin.out', w)
    """
