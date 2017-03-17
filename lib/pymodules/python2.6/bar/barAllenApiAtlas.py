import json
import urllib2
import numpy as np
import os, sys
import xml.dom.minidom as dom
from string import *
import uuid

from bar.base import barAtlasSlideElement
from barAllenApiAtlasSpace import barAllenApiAtlasSpace

BAR_CONF_DEFAULT_ALLEN_API_ATLAS = { \
                       'id' : None,
                       'version' : None,
                       'minAppVersion' : None,
                       'name' : None,
                       'datePublished' : None,
                       'url': None,
                       'size' : None}
"""
Dictionary of default parameters of L{barAllenApiAtlas} element.
"""

class barAllenApiAtlas(barAtlasSlideElement):
    """
    Class representing 'atlas' element that can be found in index of all Allen
    Institute atlases.
    """

    _elementName = 'atlas'

    def __init__(self, url, id = None, **kwargs):
        """
        @type  id: int or str
        @param id: Identifier of a given atlas. Id is an integer but it is
                   immediately converted to string.

        @type  url: str
        @param url: URL from which given dataset was downloaded
        """
        self._attributes = dict(BAR_CONF_DEFAULT_ALLEN_API_ATLAS)

        if id == None:
            id = str(uuid.uuid4())

        # Dictionary holding atlas spaced available for given atlas. The set of
        # atlas spaces is not defined in the genetal index file. This dictionary
        # is update upon request by other classes outside this one.
        self.spaces = {}

    @classmethod
    def fromXML(cls, svgImageElement):

        # Check if provided element is indeed an image tag. Stop if not.
        assert svgImageElement.tagName == cls._elementName,\
            "Provided element cannot be parsed. Wrong tag name?"

        # Extract element's id (it is required). While new barSlideBackgorundElement may have blank id,
        # the serialized one has contain a valid id.
        try:
            id = svgImageElement.getAttribute('id').encode('utf-8')
        except:
            raise AttributeError, \
            "Provided element no id attribute or provided id is invalid."

        # Url is also a required attribute: try to extract it. If URL is not
        # presented, raise an exception.
        try:
            url = svgImageElement.getAttribute('url').encode('utf-8')
        except:
            raise AttributeError, \
            "Provided element has no url attribute or provided url is invalid."

        # Create empty element instance with a given image link and extracted id
        newAllenApiAtlasElement = cls(url = url, id = id)

        # Let's try to handle attribute assignment in a pythonic way:
        # Optional attributes are gathered in tuples (name, type)
        optionalAttribs = \
                dict((('id', str), ('version', str), ('minAppVersion', str), \
                     ('name', str), ('datePublished', str), ('url', str), \
                     ('size', int)))

        for attrName, attrType in optionalAttribs.iteritems():
            attrValue = attrType(svgImageElement.getAttribute(attrName))
            setattr(newAllenApiAtlasElement, attrName, attrValue)

        return newAllenApiAtlasElement

    def _get_id(self):
        return self._attributes['id']

    def _set_id(self, value):
        if type(value) != type(''):
            raise TypeError, "Non-string value provided. Please provide string value."
        self._attributes['id'] = value

    def _get_version(self):
        return self._attributes['version']

    def _set_version(self, value):
        if type(value) != type(''):
            raise TypeError, "Non-string value provided. Please provide string value."
        self._attributes['version'] = value

    def _get_minAppVersion(self):
        return self._attributes['minAppVersion']

    def _set_minAppVersion(self, value):
        if type(value) != type(''):
            raise TypeError, "Non-string value provided. Please provide string value."
        self._attributes['minAppVersion'] = value

    def _get_name(self):
        return self._attributes['name']

    def _set_name(self, value):
        if type(value) != type(''):
            raise TypeError, "Non-string value provided. Please provide string value."
        self._attributes['name'] = value

    def _get_datePublished(self):
        return self._attributes['datePublished']

    def _set_datePublished(self, value):
        if type(value) != type(''):
            raise TypeError, "Non-string value provided. Please provide string value."
        self._attributes['datePublished'] = value

    def _get_url(self):
        return self._attributes['url']

    def _set_url(self, value):
        if type(value) != type(''):
            raise TypeError, "Non-string value provided. Please provide string value."
        self._attributes['url'] = value

    def _get_size(self):
        return self._attributes['size']

    def _set_size(self, value):
        if type(value) != type(0):
            raise TypeError, "Non-integer value provided. Please provide integer value."
        self._attributes['size'] = value

    id = property(_get_id, _set_id, None)
    """
    Identifier of given atlas. Identifier has to be string.

    @type: str
    """

    version = property(_get_version, _set_version, None)
    """
    Version of given atlas. String value required.

    @type: str
    """

    minAppVersion = property(_get_minAppVersion, _set_minAppVersion, None)
    """
    This property in included only for compatibility purposes and it is not used
    anywhere in the code. Consult Allen Brain Institute API reference for meaning
    of 'minAppVersion' field.

    @type: str
    """

    name = property(_get_name, _set_name, None)
    """
    Full name of the atlas. String value required

    @type: str
    """

    datePublished = property(_get_datePublished, _set_datePublished, None)
    """
    Publication date of given atlas. Although is a date, the value is stored as
    string.

    @note: This property in included only for compatibility purposes and it is not used
    anywhere in the code. Consult Allen Brain Institute API reference for meaning
    of 'datePublished' field.

    @type: str
    """

    size = property(_get_size, _set_size, None)
    """
    Size of the zip package with source dataset pointed by url property. Value
    of this property may be overriden but what for...

    @type: int
    """

    url = property(_get_url, _set_url, None)
    """
    URL pointing to zipfile with the atlas itself.

    @type: str
    """

if __name__ == '__main__':
    pass
