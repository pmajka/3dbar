import json
import urllib2
import numpy as np
import os, sys
import xml.dom.minidom as dom
from string import *
import uuid

from bar.base import barAtlasSlideElement

BAR_CONF_DEFAULT_ALLEN_API_SPACE = { \
        'name' : None}
"""
Dictionary of default parameters of L{barAllenApiAtlasSpace} element.
"""

class barAllenApiAtlasSpace(barAtlasSlideElement):
    """
    Class representing the 'space' element from Info.xml file delivered with
    atlases provided by the Allen Institute.
    """

    _elementName = 'space'

    def __init__(self, name, **kwargs):
        """
        @type  name: str
        @param name: name of the atlas space
        """
        # Load default attributes:
        self._attributes = dict(BAR_CONF_DEFAULT_ALLEN_API_SPACE)

        # Yeap, store the name
        self.name = name

        # Initilalize various parameters with none valie
        self._viewVolumeSize = None
        self._viewVolumePixelSpacing = None
        self._tissueVolumeSize = None
        self._tissueVolumePixelSpacing = None
        self._tissueVolumeOrigin = None

        # This one will hold path to the info file from which given instance
        # was generated (in case it actually was generated from an xml file)
        self._sourceXmlFilename = None

    @classmethod
    def fromXML(cls, svgImageElement):

        # Check if provided element is indeed an image tag. Stop if not.
        assert svgImageElement.tagName == cls._elementName,\
            "Provided element cannot be parsed. Wrong tag name (%s) ?" \
            % svgImageElement.tagName

        # Extract element's id (it is required). While new barSlideBackgorundElement may have blank id,
        # the serialized one has contain a valid id.
        try:
            name = svgImageElement.getAttribute('name').encode('utf-8')
        except:
            raise AttributeError, \
            "Provided element no id attribute or provided id is invalid."

        # Create empty element instance with a given image link and extracted id
        newAllenApiSpaceElement = cls(name)

        # Extract view-volume data:
        viewVolumeAttrs = {'size': ('width', 'height', 'depth'),
                           'pixel-spacing' : ('width', 'height', 'depth')}

        # Extract tissue-volume data (THE structural data)
        tissueVolumeAttrs = {'size': ('width', 'height', 'depth'),
                             'pixel-spacing' : ('width', 'height', 'depth'),
                             'origin' : ('x', 'y', 'z')}

        # TODO: Whole code below should be rewritten in more pythonic way...
        # but it requires a bit more information about structure of info.xml
        # file.

        viewVolumeRes   = {}
        tissueVolumeRes = {}

        viewVolume = svgImageElement.getElementsByTagName('view-volume')[0]
        for tag, attrs in viewVolumeAttrs.iteritems():
            tagN = viewVolume.getElementsByTagName(tag)[0]
            viewVolumeRes[tag] = map(lambda x: int(tagN.getAttribute(x)), attrs)

        tissueVolume = svgImageElement.getElementsByTagName('tissue-volume')[0]
        for tag, attrs in tissueVolumeAttrs.iteritems():
            tagN = tissueVolume.getElementsByTagName(tag)[0]
            tissueVolumeRes[tag] = map(lambda x: int(tagN.getAttribute(x)), attrs)

        newAllenApiSpaceElement.viewVolumeSize = viewVolumeRes['size']
        newAllenApiSpaceElement.viewVolumePixelSpacing = viewVolumeRes['pixel-spacing']
        newAllenApiSpaceElement.tissueVolumeSize = tissueVolumeRes['size']
        newAllenApiSpaceElement.tissueVolumePixelSpacing = tissueVolumeRes['pixel-spacing']
        newAllenApiSpaceElement.tissueVolumeOrigin = tissueVolumeRes['origin']

        return newAllenApiSpaceElement

    def _get_name(self):
        return self._attributes['name']

    def _set_name(self, value):
        if type(value) != type(''):
            raise TypeError, "Non-string value provided. Please provide string value."
        self._attributes['name'] = value

    def _get_viewVolumeSize(self):
        return self._viewVolumeSize

    def _set_viewVolumeSize(self, value):
        self._viewVolumeSize = map(int, value)

    def _get_viewVolumePixelSpacing(self):
        return self._viewVolumePixelSpacing

    def _set_viewVolumePixelSpacing(self, value):
        self._viewVolumePixelSpacing = map(int, value)

    def _get_tissueVolumeSize(self):
        return self._tissueVolumeSize

    def _set_tissueVolumeSize(self, value):
        self._tissueVolumeSize = map(int, value)

    def _get_tissueVolumePixelSpacing(self):
        return self._tissueVolumePixelSpacing

    def _set_tissueVolumePixelSpacing(self, value):
        self._tissueVolumePixelSpacing = map(int, value)

    def _get_tissueVolumeOrigin(self):
        return self._tissueVolumeOrigin

    def _set_tissueVolumeOrigin(self, value):
        self._tissueVolumeOrigin = map(int, value)

    def _get_sourceXmlFilename(self):
        return self._sourceXmlFilename

    def _set_sourceXmlFilename(self, value):
        if type(value) != type(''):
            raise TypeError, "Non-string value provided. Please provide string value."
        self._sourceXmlFilename = value

    name = property(_get_name, _set_name, None)
    """
    Name of given atlas space
    @type: str
    """

    viewVolumeSize = property(_get_viewVolumeSize, _set_viewVolumeSize, None)
    """
    @type: (int, int, int)
    """

    viewVolumePixelSpacing = property(_get_viewVolumePixelSpacing,  _set_viewVolumePixelSpacing, None)
    """
    @type: (int, int, int)
    """

    tissueVolumePixelSpacing = property(_get_viewVolumePixelSpacing, _set_viewVolumePixelSpacing, None)
    """
    Voxel size of the structural data.

    @type: (int, int, int)
    """

    tissueVolumeSize = property(_get_tissueVolumeSize, _set_tissueVolumeSize, None)
    """
    Volume extent of the structural data.

    @type: (int, int, int)
    """

    tissueVolumeOrigin = property(_get_tissueVolumeOrigin, _set_tissueVolumeOrigin, None)
    """
    Index of voxel beeing origin of the srs

    @type: (int, int, int)
    """

    sourceXmlFilename = property(_get_sourceXmlFilename, _set_sourceXmlFilename, None)
    """
    Filename (and path) of the xml file from which given instance was generated.

    @type: str
    """

if __name__ == '__main__':
    pass
