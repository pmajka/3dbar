#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# vim: set foldmethod=indent
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
The module provides classes necessary to parse MBAT atlases.

G{importgraph}
"""

import xml.dom.minidom as dom
import os
import re

import nifti
from PIL import Image,ImageChops
from parsers import barBitmapParser

def _parse_hex(string):
    """
    Parsers priovided color string (perhaps in shorthanded form) into
    '#xxxxxx' string. Code found somewhere over the internet.

    @type  string: string to process
    @param string: C{rgb} color string to parse

    @rtype: C{str}
    @return: Color code string '#xxxxxx"
    """
    if string[0] == '#':
        string = string[1:]

    n = len(string)
    fmt = {
        3: '([0-9A-Fa-f]{1})' * 3, # shorthand RGB
        4: '([0-9A-Fa-f]{1})' * 4, # shorthand RGBA
        6: '([0-9A-Fa-f]{2})' * 3, # RGB
        8: '([0-9A-Fa-f]{2})' * 4  # RGBA
    }

    match = re.match(fmt[n], string)

    if match:
        groups = match.groups()
        # shorthand RGB{,A} must be extended
        if n in [3,4]:
            groups = tuple([2*x for x in groups])
        return ("#"+"".join(groups))[:7]
    else:
        raise ValueError,'Unable to parse "%s"' % (string)


class barMbatLabel(object):
    """
    Helper class for mbat .lif file
    """
    _elementAttributes = ['abbreviation', 'color', 'name', 'id']
    _optionalAttributes = ['description']

    def __init__(self, xmlElement):
        """
        @type  xmlElement: C{xml DOM object}
        @param xmlElement: mbat .lif file xml element

        @rtype: C{None}
        @return: None
        """
        map(lambda x:\
                setattr(self, x, xmlElement.getAttribute(x)), self._elementAttributes)

        for optAttr in self._optionalAttributes:
            optAttrVal = xmlElement.getAttribute(optAttr)
            if optAttrVal == "":
                optAttrVal = None
            else:
                optAttrVal = optAttrVal.strip().replace(' ','_')
            setattr(self, optAttr, optAttrVal)

        self.id = int(self.id)
        self.color = _parse_hex(self.color)

        # Correct poor names - remove spaces, etc.
        self.name = self.name.strip()
        self.abbreviation = self.abbreviation.strip().replace(' ','-')
        self.abbreviation = self.abbreviation.strip().replace(',','-')

        # Extract parent, if marent is null, assing root element
        self.parent  = xmlElement.parentNode.getAttribute('abbreviation')
        self.parent = self.parent.strip().replace(' ','-')


class barMBATParser(barBitmapParser):
    """
    Generic parser for MBAT atlases (http://mbat.loni.ucla.edu/). Parser
    requires volumetric file and MBAT atlas file.

    @type _volume: C{niftii volume}
    @ivar _volume: Dataset containing labelled brain volume

    @type _pathNumber: C{int}
    @ivar _pathNumber: internal path number iterator. Required for correct path
                       parsing

    @change: Thu Mar 17 12:58:22 CET 2011. Initial version
    """
    _requiredInternalData = barBitmapParser._requiredInternalData +\
            ['_volume','_pathNumber']

    def __init__(self, inputAtlasFile, outputDirectory, **kwargs):
        """
        @type  inputAtlasFile: C{str}
        @param inputAtlasFile: location of mbat atlas file (.atlas)

        @type  outputDirectory: C{str}
        @param outputDirectory: directory, where resulting caf will be stored

        @rtype: C{None}
        @return: None
        """
        # Extend passed properties and invoke uperclass constuctor
        barBitmapParser.__init__(self, **kwargs)

        self.inputAtlasFile  = inputAtlasFile
        self.outputDirectory = outputDirectory

        # Load atlas filename and hierarchy filename, extracts hierarhy, color
        # and fullname mapping
        self.__loadAtlasFile()

        # path number and slide range should be defined in particular parser
        # if values are different than defined here
        self._defineSlideRange()
        self._pathNumber = 0

    def __loadAtlasFile(self):
        """
        Loads MBAT atlas file and extracts volumetric dataset and hierarchy
        filename.

        @rtype: C{None}
        @return: None
        """
        self.atlasDom = dom.parse(self.inputAtlasFile)

        # Extract labels filename
        volumeElem = self.atlasDom.getElementsByTagName('label')[0]
        volumeFilename = volumeElem.getAttribute('src')
        volumeFilename = os.path.join(os.path.dirname(self.inputAtlasFile), volumeFilename)

        # Extract hierarchy filename
        hierarchyElem = self.atlasDom.getElementsByTagName('hierarchy')[0]
        hierarchyFilename = hierarchyElem.getAttribute('src')
        hierarchyFilename = os.path.join(os.path.dirname(self.inputAtlasFile), hierarchyFilename)

        self.__loadVolume(volumeFilename)
        self.__extractHierarchy(hierarchyFilename)

    def _defineSlideRange(self):
        """
        Generates L{self.slideRange<self.slideRange>} attribute.

        @rtype: C{None}
        @return: None
        """
        raise NotImplementedError, "Method not implemented"

    def __loadVolume(self, volumeFilename):
        """
        Loads volumetric dataset, store header and volume data

        @type  volumeFilename: C{str}
        @param volumeFilename: full location of volumetric dataset

        @rtype: C{None}
        @return: None
        """

        self._volumeSrc = nifti.NiftiImage(volumeFilename)
        self._volume  = self._volumeSrc.data
        self._volumeHeader = self._volumeSrc.header

    def __extractHierarchy(self, hierarchyFilename):
        """
        Extracts fullname mapping, color mapping and hierarchy and stores them
        as instance attribuutes.

        @type  volumeFilename: C{str}
        @param volumeFilename: full location of volumetric dataset

        @rtype: C{None}
        @return: None
        """
        # Load hierarchy filename
        lifFile = dom.parse(hierarchyFilename)
        structures = map(lambda x: barMbatLabel(x),\
                            lifFile.getElementsByTagName('label'))

        # Extract hierarchy
        # Extract fullname mapping
        # Extract color mapping
        self.parents =\
                dict(map(lambda x: (x.abbreviation, x.parent), structures))
        self.fullNameMapping =\
                dict(map(lambda x: (x.abbreviation, x.name), structures))
        self.structureColours =\
                dict(map(lambda x: (x.abbreviation, x.color), structures))
        self.ontologyMapping =\
                dict(map(lambda x: (x.abbreviation, x.description), structures))
        self.imageToStructure =\
                dict(map(lambda x:\
                ("#%02x%02x%02x" % (x.id,x.id,x.id), x.abbreviation), structures))

    def parse(self, slideNumber,
                    generateLabels=True,
                    useIndexer=False,
                    writeSlide = True):
        tracedSlide = barBitmapParser.parse(self, slideNumber,\
                              generateLabels = generateLabels,
                              useIndexer = useIndexer,
                              writeSlide = writeSlide)
        return tracedSlide

    def reindex(self):
        # Do the regular stuff
        barBitmapParser.reindex(self)
        self.indexer.hierarchy = self.parents

        # Append ontology references if such mapping exist
        groups = self.indexer.groups
        for (k,v) in groups.iteritems():
            ontologyId = self.ontologyMapping.get(k)
            v.__setattr__('ontologyid', ontologyId)

    def parseAll(self):
        barBitmapParser.parseAll(self)
        self.reindex()

    def _getSourceImage(self, slideNumber):
        volumeSlide = self._volume[:, self.slideRange[slideNumber], :]
        volumeSlide[ volumeSlide[:,:]==0 ] = 255
        image = Image.fromarray(volumeSlide.astype(np.uint8), 'L').convert("RGB")
        image = image.transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
        return image

    def _createMask(self, image, colorValue):
        r,g,b = colorValue
        R, G, B = 0, 1, 2

        source = image.split()
        # select regions where red is less than 100
        mask = (source[R].point(lambda i: i == r and 255),\
        source[G].point(lambda i: i == g and 255),\
        source[B].point(lambda i: i == b and 255))

        # Resize image it order to get better tracing effects:
        # resizing is performed using high quality anialiasing filter
        # get size:
        resizeTuple = self.renderingProperties['imageSize']
        image = ImageChops.multiply(ImageChops.multiply(mask[1], mask[0]),mask[2])
        image = ImageChops.invert(image).resize(resizeTuple, Image.ANTIALIAS)
        return image

    def _getIndexerRefMatrix(self):
        """
        Returns reference matrix stored in index file.

        @rtype: C{(float, float, float, float)}
        @return: None
        """
        t = self._getSpatialTransfMatrix(0)
        return (t[1], t[3], t[0], t[2])

    def _getNewPathID(self, structName = None):
        self._pathNumber+=1
        return "structure%d_label%d_%s" % (self._pathNumber, self._pathNumber, structName)
