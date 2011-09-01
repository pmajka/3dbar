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
The module provides class necessary to perform thumbnail generation.

G{importgraph}
"""

from PIL import Image
import sys
import numpy
from optparse import OptionParser

class Thumbnail(Image.Image):
    """
    An extension of PIL.Image class - a method to generate a thumbnail of image has been added.
    """
    @classmethod
    def open(cls, *args, **kwargs): #infile, mode='r'
        """
        Because PIL.Image code is written in a messy way this method is necessary
        to load Thumbnail instance from file.
        
        #Piotrek: to raczej nie następi :)
        The code might become unstable when PIL.Image.Image class implementation changes.
        """
        # load the image
        image = Image.open(*args, **kwargs) #infile, mode='r'
        image.load()
        
        # copy attributes of image to cls instance
        newinstance = cls()
        for attribute in ['im', 'mode', 'size', 'palette', 'info']:
            setattr(newinstance, attribute, getattr(image, attribute))
        
        return newinstance
    
    def getthumbnail(self, (sizex, sizey) = (256,160), padding=10, background=(0, 0, 0, 0)):
        """
        Return the thumbnail of image.
        
        @note: the colour of left top pixel is considered to be the background
               colour
        
        @todo: mode recognition - if alpha chanel is present, use it
               to recognize background pixels
               
        @type (sizex, sizey): (int, int)
        @param (sizex, sizey): size of desired thumbnail (without padding)
        
        @type padding: int
        @param padding: size of padding
        
        @type background: [int, int, int, int]
        @param background: background colour in RGBA
        """
        
        # get numpy array representation of image
        arr = numpy.asarray(self)
        
        # get a map of background pixels - if not works, remove '.all(2)'
        indices = (arr == arr[0,0]).all(2)
        
        # get writable numpy array representation of image in RGBA format
        arr = numpy.asarray(self.convert('RGBA'))
        arr.flags.writeable = True
        
        # img is image with background pixels black and transparent
        arr[indices] = [0, 0, 0, 0]
        img = Image.fromarray(arr.astype(numpy.uint8), mode="RGBA")
        
        # get the bounding box of non-background (non-black and
        # non-transparent) part of img
        bbx = img.getbbox()
         
        # if necessary change background to requested
        if background != [0, 0, 0, 0]:
            arr[indices] = background
            img = Image.fromarray(arr.astype(numpy.uint8), mode="RGBA")
        
        # create image of requested size and filled with background colour
        newimg = Image.new('RGBA', (sizex+2*padding, sizey+2*padding),
                           tuple(background))
        
        # If the image contains mote than just background:
        if bbx != None:
            # anythyng but background
            brush = img.crop(bbx)
            
            # get new to old size ratio 
            (bbx_x, bbx_y) = brush.size
            xfactor, yfactor = float(sizex)/bbx_x, float(sizey)/bbx_y
            
            # resize brush to fit requested size
            if xfactor < yfactor:
                (newsizex, newsizey) = (sizex, int(round(xfactor * bbx_y)))
            else:
                (newsizex, newsizey) = (int(round(yfactor * bbx_x)), sizey)
            brush = brush.resize((newsizex, newsizey), Image.ANTIALIAS)
            
            # paste brush in the centre of newimg - remember, that one of brush
            # dimensions might have different value than requested
            dx = padding + (sizex - newsizex)/2
            dy = padding + (sizey - newsizey)/2
            newimg.paste(brush, (dx, dy))
        
        return newimg

if __name__ == '__main__':
    def parseArgs():
        """
        Parse script arguments.
        
        @return: (options, args)
        @rtype: (optparse.Values object, [str, ...])
        
        @note: The method exits if parse failed or requested to display help.
        """
        parser = OptionParser(usage="usage: [options] <input filename> <output filename>")
        parser.add_option('--size', '-s', dest='size',
                          type='int', nargs=2, default=(256, 160),
                          help='thumbnail size in pixels (width, height)')
        parser.add_option('--padding', '-p', dest='padding',
                          type='int', default=10,
                          help='padding arround the thumbnail (in pixels)')
        parser.add_option('--background', '-b', dest='background',
                          type='int', nargs=4, default=(0, 0, 0, 0),
                          help='thumbnail background colour (R, G, B, A)')
        
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.print_help()
            exit()
        return (options, args)
    
    options, args = parseArgs()
    Thumbnail.open(args[0]).getthumbnail(options.size,
                                         options.padding,
                                         options.background).save(args[1])
