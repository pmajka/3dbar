import xml.dom.minidom as dom
import uuid
from base import barTracedSlideRenderer, barAtlasSlideElement, parseStyle, formatStyle, _printRed,\
BAR_XML_NAMESPACE, barPretracedSlideRenderer

CONF_DEFAULT_BACKGROUND_ATTRIBUTES = { \
                       'height': None,
                       'width' : None,
                       'x' : None,
                       'y' : None,
                       'xlink:href' : None,
                       'style': '',
                       'id' : None}
"""
Dictionary of default parameters of L{barSlideBackgorundElement} within SVG
namespace.
"""

CONF_DEFAULT_BACKGROUND_ATTRIBUTES_NS = { \
                        'description' : None,
                        'modality' : None,
                        'preparation' : None}
"""
Dictionary of default parameters of L{barSlideBackgorundElement} within 3dBAR
namespace.
"""

CONF_DEFAULT_BACKGROUND_LIST = { \
                        'id' : None,
                        'style': ''}
"""
Dictionary of default parameters of L{barSlideBackgroundList} within SVG
namespace.
"""

CONF_DEFAULT_BACKGROUND_LIST_NS = { \
                        'elementinfo' : 'backgroundImageList'}
"""
Dictionary of default parameters of L{barSlideBackgroundList} within 3dBAR
namespace.
"""

class barSlideBackgorundElement(barAtlasSlideElement):
    """
    Extension of the 3dBAR API providing the ability to embed image underlays
    within an CAF slide. In SVG terms, the image underlays are implemented as
    C{image} tags contained within dedicated C{g} element represented with
    L{barSlideBackgroundList} object.

    @see: http://www.w3.org/TR/SVG/struct.html#ImageElement for full description
    of a SVG C{image} tag.
    """

    _elementName = 'image'

    def __init__(self, imageLink, position = (0,0), size=(100,100), id=None):
        """
        @type  imageLink: str
        @param imageLink: URI of image associated with the element.

        @type  position: (float, float)
        @param position: A position of a left upper corner of an image underlay.
                         See L{barSlideBackgorundElement.position} property for
                         details.

        @type  size: (float, float)
        @param size: Size of the given image underlay in SVG coordinates. See
                     L{barSlideBackgorundElement.size} property description for
                     details.

        @type  id: str
        @param id: Identifier of an instance. If not provided, it is assigned
                   automatically

        """
        self._attributes = dict(CONF_DEFAULT_BACKGROUND_ATTRIBUTES)
        self._attributesNS = dict(CONF_DEFAULT_BACKGROUND_ATTRIBUTES_NS)

        if id == None:
            id = str(uuid.uuid4())

        self.id = id
        self.position = position
        self.imageLink = imageLink
        self.position = position
        self.size = size
        self.opacity = 1

    @classmethod
    def fromXML(cls, svgImageElement):

        # Check if provided element is indeed an image tag. Stop if not.
        assert svgImageElement.tagName == cls._elementName,\
            "Provided element cannot be parsed. Wrong tag name?"

        # Extract image link from the provided image tag
        try:
            imageLink = svgImageElement.getAttribute('xlink:href').encode('utf-8')
        except:
            raise AttributeError, \
            "Provided element no xlink or provided xlink is invalid."

        # Extract element's id (it is required). While new barSlideBackgorundElement may have blank id,
        # the serialized one has contain a valid id.
        try:
            id = svgImageElement.getAttribute('id').encode('utf-8')
        except:
            raise AttributeError, \
            "Provided element no id attribute or provided id is invalid."

        # Create empty background element instance with a given image link and extracted id
        newBackgroundElement = cls(imageLink, id = id)

        # Extract and validate other attributes. Handling some of them is easy
        # while some of the other are more complicated to parse:

        if svgImageElement.hasAttribute('height') and \
           svgImageElement.hasAttribute('width'):
            height = float(svgImageElement.getAttribute('height'))
            width  = float(svgImageElement.getAttribute('width'))
            newBackgroundElement.size = (width,height)

        if svgImageElement.hasAttribute('x') and \
           svgImageElement.hasAttribute('y'):
            x = float(svgImageElement.getAttribute('x'))
            y = float(svgImageElement.getAttribute('y'))
            newBackgroundElement.position = (x,y)

        if svgImageElement.hasAttribute('style'):
            styleString = parseStyle(svgImageElement.getAttribute('style'))
            newBackgroundElement._style = styleString
            if styleString.has_key('opacity'):
                newBackgroundElement.opacity = float(styleString['opacity'])

        if svgImageElement.hasAttributeNS(BAR_XML_NAMESPACE, 'modality'):
            newBackgroundElement.modality = \
                svgImageElement.getAttributeNS(BAR_XML_NAMESPACE, 'modality')

        if svgImageElement.hasAttributeNS(BAR_XML_NAMESPACE, 'preparation'):
            newBackgroundElement.preparation = \
                svgImageElement.getAttributeNS(BAR_XML_NAMESPACE, 'preparation')

        if svgImageElement.hasAttributeNS(BAR_XML_NAMESPACE, 'description'):
            newBackgroundElement.description = \
                svgImageElement.getAttributeNS(BAR_XML_NAMESPACE, 'description')

        return newBackgroundElement

    def _getId(self):
        return self._attributes['id']

    def _setId(self, value):
        if type(value) != type(''):
            raise TypeError, "ID has to be string. Non-string value provided. Please provide string value."
        self._attributes['id'] = value

    def _getImage(self):
        return self._attributes['xlink:href']

    def _setImage(self, value):
        if type(value) != type(''):
            raise TypeError, "ID has to be string. Non-string value provided. Please provide string value."
        self._attributes['xlink:href'] = value.strip()

    def _getPosition(self):
        return self._position

    def _setPosition(self, value):
        self._position = map(float,value)
        self._attributes['x'] = str(self._position[0])
        self._attributes['y'] = str(self._position[1])

    def _getSize(self):
        return self._size

    def _setSize(self, value):
        self._size = map(float,value)
        self._attributes['height'] = str(self._size[1])
        self._attributes['width']  = str(self._size[0])

    def _getOpacity(self):
        return float(self._opacity)

    def _setOpacity(self, value):
        assert type(value) == type(1.) or \
               type(value) == type(0), \
            "Opacity has to be float between 0 and 1"

        self._opacity = float(value)
        styleDict = parseStyle(self._attributes['style'])
        styleDict['opacity'] = str(self._opacity)
        self._attributes['style'] = formatStyle(styleDict)

    def _getStain(self):
        return self._attributesNS['modality']

    def _setStain(self, value):
        assert type(value) == type('') or value == None,\
            "Stain has to be string or None. Non-string and not None value provided. Please provide string value."
        self._attributesNS['modality'] = value

    def _getPreparation(self):
        return self._attributesNS['preparation']

    def _setPreparation(self, value):
        assert type(value) == type('') or value == None,\
            "Preparation has to be string or None. Non-string and not None value provided. Please provide string value."
        self._attributesNS['preparation'] = value
        self._preparation = value

    def _getDescription(self):
        return self._attributesNS['description']

    def _setDescription(self, value):
        assert type(value) == type('') or value == None,\
            "Description has to be string or None. Non-string and not None value provided. Please provide string value."
        self._attributesNS['description'] = value

    id = property(_getId, _setId, None)
    """
    Identifier of the label. Usually a strange combination of digits and
    characters.

    @type: str
    """

    imageLink = property(_getImage, _setImage, None)
    """
    URI of a image. String value is required. Provided value will be translated
    into C{image}'s element C{xlink:href} attribute.

    @see: See http://www.w3.org/TR/SVG/struct.html#ImageElementHrefAttribute
           for full description of the attribute's meaning.

    @type: str
    """

    position = property(_getPosition, _setPosition, None)
    """
    Coordinates of a anchor point (the upper-left corner) of a image in SVG
    coordinates. Provided values are used to define C{image}'s tag C{x} and C{y}
    attributes.

    @see: http://www.w3.org/TR/SVG/struct.html#ImageElementXAttribute
    for full reference.

    @type: (float, float)
    """

    size = property(_getSize, _setSize, None)
    """
    Size of the image in SVG coordinates. The tuple is used to generate tag's
    height and width attributes.

    @see: C{http://www.w3.org/TR/SVG/struct.html#ImageElementWidthAttribute} for full
    SVG specification of the image tag.

    @type: (float, float)
    """

    opacity = property(_getOpacity, _setOpacity, None)
    """
    Opacity of the image. A float value between 0 and 1 is required. Other
    providing other values will raise an error.

    @type: float
    """

    modality = property(_getStain, _setStain, None)
    """
    Description of image's modality (Nissl, AChE, T1, etc.). Put wathever string
    you want.

    @type: str
    """

    preparation = property(_getPreparation, _setPreparation, None)
    """
    Image preparation description - arbitrary.

    @type: str
    """

    description = property(_getDescription, _setDescription, None)
    """
    An arbitrary comment.

    @type: str
    """


class barSlideBackgroundList(barAtlasSlideElement):
    """
    C{barSlideBackgroundList} is an object for holding all image underlays
    withing given SVG slide. It implements python list's interface and holds
    multiple L{barSlideBackgorundElement} objects. When serialized, SVG C{g}
    tag containing multiple C{image} tags are generated.
    """
    _elementName = 'g'

    def __init__(self, id=None, elements = None):
        """
        C{barSlideBackgroundList} constructor. Use this constructor to initialize
        empty/blank C{barSlideBackgroundList} object. If you parsing a slide and you
        want to recreate C{barSlideBackgroundList} from CAF slide's image layer, use
        L{barSlideBackgroundList.fromXML} method.

        @type  id: str
        @param id: Identifier you want to assign to the object. If no ID is
                   provided, it is generated automatically.

        @type  elements: [L{barSlideBackgorundElement},...]
        @param elements: Iterable of background images to be used as a content of
                         the object
        """
        self._attributes = dict(CONF_DEFAULT_BACKGROUND_LIST)
        self._attributesNS = dict(CONF_DEFAULT_BACKGROUND_LIST_NS)

        # Initialize empty elements list. This list will hold all image elements
        self._elements = []
        if id == None:
            id = str(uuid.uuid4())
        self.id = str(id)

        # Add elements to the list. Extend the list if another list
        # is provided or just append the given element.
        if getattr(elements, '__iter__', False):
            self.extend(elements)
        elif elements != None:
            self.append(elements)

    def __getslice__(self, i, j):
        return self._elements[i:j]

    def __getitem__(self, key):
        if type(key) is slice:
            return self._elements[i:j]
        else:
            return self._elements[key]

    def index(self, x):
        return self._elements.index[x]

    def insert(self, i, x):
        return self._elements.insert(i,x)

    def remove(self, x):
        del self._elements[x]

    def append(self, x):
        return self._elements.append(x)

    def extend(self, L):
        return self._elements.extend(L)

    def pop(self):
        return self._elements.pop()

    def _getId(self):
       """
       Returns ID attribute.

       @type str:
       @return: Image layer's identifier
       """
       return self._attributes['id']

    def _setId(self, value):
       """
       Assigns the ID value of the underlays holder

       @param value:
       @type  value:

       @return: None
       """
       if type(value) != type(''):
           raise TypeError, "ID has to be string. Non-string value provided. Please provide string value."
       self._attributes['id'] = value

    def getXMLelement(self):
       layerElement = super(self.__class__, self).getXMLelement()

       for imageElement in self._elements:
           layerElement.appendChild(imageElement.getXMLelement())
       return layerElement

    @classmethod
    def fromXML(cls, svgGroupElement):
        """
        Create L{barSlideBackgroundList} from and dedicated SVG C{g} tag.

        @type  svgGroupElement: C{xml.dom.minidom.Document}
        @param svgGroupElement: SVG {g} element to be processed

        @return: An L{barSlideBackgroundList} based on given C{svgGroupElement}.
        @rtype : L{barSlideBackgroundList}
        """

        # Check if provided element is indeed an image tag. Stop if not.
        assert svgGroupElement.tagName == cls._elementName,\
           "Provided element cannot be parsed. Wrong tag name?"
        assert svgGroupElement.getAttributeNS(BAR_XML_NAMESPACE, 'elementinfo') == 'backgroundImageList',\
           "Provided element cannot be parsed. Wrong 'elementinfo' attribute?"

        # Extract element's id (it is required). While new barSlideBackgorundElement may have blank id,
        # the serialized one has contain a valid id.
        try:
           id = str(svgGroupElement.getAttribute('id'))
        except:
           raise AttributeError, \
           "Provided element has no id attribute or provided id is invalid."

        # Create empty layer for the images
        newLayer = barSlideBackgroundList(id = id)

        # Load consecutive images into the layer.
        for ImageElement in svgGroupElement.getElementsByTagName('image'):
           newLayer.append(barSlideBackgorundElement.fromXML(ImageElement))

        return newLayer

    id = property(_getId, _setId, None, "Id of an element")
    """
    Id of an element.

    @type: str
    """


class barBackgroundImageSlide(barTracedSlideRenderer):
    """
    Extenstion of the regular L{bar.barTracedSlideIndexer} allowing the user to
    load a number of different image underlays in addition to the annotation
    layer. This class preserves its patent's ability to handle all annotation
    features.
    """
    def __init__(self,  **kwargs):
        barTracedSlideRenderer.__init__(self, **kwargs)
        self.backgroundImages = barSlideBackgroundList()

    @classmethod
    def _fromXML_BeforeCleanUpHook(cls, slide, svgdom):
        # Handling removal of image underlays. As these underlays are extension
        # with respect to regular CAF slide, they have to be parsed separately.
        # Code below handles such parsing:

        # Check if the slide contains layers containing background images.
        for layer in svgdom.getElementsByTagName('g'):
            if layer.getAttributeNS(BAR_XML_NAMESPACE, 'elementinfo') == \
               CONF_DEFAULT_BACKGROUND_LIST_NS['elementinfo']:
                slide.backgroundImages = barSlideBackgroundList.fromXML(layer)

    @classmethod
    def _fromXML_AfterCleanUpHook(cls, slide, svgdom):
        # Remove image layer (if such exists):
        for layer in svgdom.getElementsByTagName('g'):
            if layer.getAttributeNS(BAR_XML_NAMESPACE, 'elementinfo') == \
               CONF_DEFAULT_BACKGROUND_LIST_NS['elementinfo']:
                layer.parentNode.removeChild(layer)

        # Remove 'rect' tags (there shouldn't be any but just in case)
        for element in svgdom.getElementsByTagName('rect'):
            element.parentNode.removeChild(element)

    def getXMLelement(self):
        slide = barTracedSlideRenderer.getXMLelement(self)
        svgGroupDataset = slide.getElementsByTagName('g')[0]
        svgElement = slide.getElementsByTagName('svg')[0]
        svgElement.insertBefore(self.backgroundImages.getXMLelement(), svgGroupDataset)
        return slide


class barBackgroundImageContourSlide(barPretracedSlideRenderer):
    """
    Extenstion of the regular L{bar.barTracedSlideIndexer} allowing the user to
    load a number of different image underlays in addition to the annotation
    layer. This class preserves its patent's ability to trace contours into
    structures.
    """
    def __init__(self, **kwargs):
        barPretracedSlideRenderer.__init__(self, **kwargs)
        self.backgroundImages = barSlideBackgroundList()

    @classmethod
    def _fromXML_BeforeCleanUpHook(cls, slide, svgdom):
        # Handling removal of image underlays. As these underlays are extension
        # with respect to regular CAF slide, they have to be parsed separately.
        # Code below handles such parsing:

        # Check if the slide contains layers containing background images.
        for layer in svgdom.getElementsByTagName('g'):
            if layer.getAttributeNS(BAR_XML_NAMESPACE, 'elementinfo') == \
               CONF_DEFAULT_BACKGROUND_LIST_NS['elementinfo']:
                slide.backgroundImages = barSlideBackgroundList.fromXML(layer)

    @classmethod
    def _fromXML_AfterCleanUpHook(cls, slide, svgdom):
        # Remove image layer (if such exists):
        for layer in svgdom.getElementsByTagName('g'):
            if layer.getAttributeNS(BAR_XML_NAMESPACE, 'elementinfo') == \
               CONF_DEFAULT_BACKGROUND_LIST_NS['elementinfo']:
                layer.parentNode.removeChild(layer)

    def trace(self, colorMapping):
        self._tracingConf['DetectUnlabelled'] = False

        for imageElement in self.backgroundImages:
            imageElement.opacity = 0

        retSlide = barPretracedSlideRenderer.trace(self, colorMapping)
        retSlide = barBackgroundImageSlide.fromXML(retSlide.getXMLelement())

        for imageElement in self.backgroundImages:
            imageElement.opacity = 1
        retSlide.backgroundImages = self.backgroundImages

        return retSlide

    def getXMLelement(self):
        slide = barPretracedSlideRenderer.getXMLelement(self)
        svgGroupDataset = slide.getElementsByTagName('g')[0]
        svgElement = slide.getElementsByTagName('svg')[0]
        svgElement.insertBefore(self.backgroundImages.getXMLelement(), svgGroupDataset)
        return slide

if __name__ == '__main__':
    pass
