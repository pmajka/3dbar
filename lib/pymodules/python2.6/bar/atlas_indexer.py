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
The module provides classes necessary to handle basic CAF dataset index
manipulations.

G{importgraph}

@var CONF_HIERARCHY_ROOT_NAME: Default value of C{L{barIndexer.__init__}()}
                               argument.
"""

CONF_HIERARCHY_ROOT_NAME = "Brain"
CONF_ALIGNER_REFERENCE_COORDS = ( 1.0, -6.0, 0.01, -0.01)

import os
import sys
import xml.dom.minidom as dom
import base
from string import *

class barIndexerObject(base.barObject):
    """
    Virtual class parental to all classes defined in the module.
    """
    def __init__(self):
        pass
    
    @classmethod
    def fromXML(cls, sourceXMLElement):
        """
        Creates object from its (valid) xml representation. XML representation
        may be either string containing a path to an XML document, an object of
        xml.dom.Node class, an XML string or an object containing a method named
        read that returns an XML string.

        @type  sourceXMLElement: xml.dom.Node or str or file
        @param sourceXMLElement: XML representation of the L{barIndexerObject} on which
                                 the object is based

        @return: created object
        @rtype: cls
        """

        raise NotImplementedError, "Virtual method executed."


class barIndexerElement(barIndexerObject):
    """
    Virtual class parental to classes representing CAF dataset index file
    elements.

    @cvar _elementName: name of the XML element represented by class instances
    @type _elementName: str

    @cvar _elementAttributes: names of attributes of the XML element represented by class
                              instances
    @type _elementAttributes: [str, ...]
    """
    _elementAttributes = []
    _elementName = None
    
    def getXMLelement(self):
        """
        @return: dom XML object describing the object
        """
        retDocument = dom.Document()
        retDocument.endocing = base.BAR_XML_ENCODING
        retElement  = retDocument.createElement(self._elementName)
        
        # Put all attrubutes into text element
        for attribName in self._elementAttributes:
            if hasattr(self, attribName):
                attribValue = getattr(self, attribName)
                if attribValue != None:
                    retElement.setAttribute(attribName, unicode(attribValue))
        
        return retElement
    
    @classmethod
    def fromXML(cls, sourceXMLElement, retClassName = None, indexer=None):
        """
        Creates object from its (valid) xml representation.

        @note: method designed to be utilized only by methods overriding it in
               derived classes
        
        @type  sourceXMLElement: xml.dom.Node
        @param sourceXMLElement: XML description of the C{barIndexer} object
                                 to be created

        @type retClassName: class
        @param retClassName: class of the object to be created

        @type indexer: L{barIndexer}
        @param indexer: the object encapsulating returned class instance
        
        @return: object based on sourceXMLElement description
                 (initiation of the object might be unfinished)
        @rtype: L{retClassName}
        """
        assert retClassName, "No return class given"
        attrs = {}
        for attribute in retClassName._elementAttributes:
            if sourceXMLElement.hasAttribute(attribute):
                attrs[attribute] = sourceXMLElement.getAttribute(attribute)

        return retClassName(**attrs)


class barIndexerPropertyElement(barIndexerElement):
    """
    Class of objects representing 'property' elements of CAF dataset index file.

    @ivar _type: property name
    @type _type: str

    @ivar _value: property value
    @type _value: str
    """
    _elementName = 'property'
    _elementAttributes = ['type', 'value']
    
    def __init__(self, type, value):
        """
        @param type: value of the 'type' attribute of represented XML element
        @type type: str

        @param value: value of the 'value' attribute of represented XML element
        @type value: str
        """
        self._type = type
        self._value = value
    
    def __getType(self):
        """
        @return: value of the 'type' attribute of represented XML element
        """
        return self._type
    
    def __setType(self, newType):
        """
        Sets value of the 'type' attribute to L{newType}.

        @param newType: new value of the 'type' attribute of represented XML element
        @type newType: str
        """
        self._type = newType
    
    def __getValue(self):
        """
        @return: value of the 'value' attribute of represented XML element
        """
        return self._value
    
    def __setValue(self, newValue):
        """
        Sets value of the 'value' attribute to L{newValue}.

        @param newValue: new value of the 'value' attribute of represented XML element
        @type newValue: str
        """
        self._value = newValue
    
    @classmethod
    def fromXML(cls, sourceXMLElement, indexer=None):
        """
        Creates object from its (valid) xml representation.
        
        @type  sourceXMLElement: xml.dom.Node
        @param sourceXMLElement: XML description of the C{barIndexerPropertyElement} object
                                 to be created

        @type indexer: L{barIndexer}
        @param indexer: the object encapsulating returned class instance
        
        @return: object based on L{sourceXMLElement} description
        @rtype: cls
        """
        return barIndexerElement.fromXML(sourceXMLElement, cls, indexer=indexer)
    
    type = property(__getType, __setType)
    """
    The 'type' attribute of represented 'property' element.

    @type: str
    """

    name = type
    """
    An alias for L{type} property.
    """

    value = property(__getValue,__setValue)
    """
    The 'value' attribute of represented 'property' element.

    @type: str
    """


class barIndexerGroupElement(barIndexerElement):
    """
    Class of objects representing 'group' elements of CAF dataset index file.

    @ivar _name: value of the 'name' attribute of represented XML element
    @type _name: str

    @ivar _id: value of the 'id' attribute of represented XML element
    @type _id: int

    @ivar _fill: value of the 'fill' attribute of represented XML element
    @type _fill: str

    @ivar _fullname: value of the 'fullname' attribute of represented XML element
    @type _fullname: str

    @ivar _uid: value of the 'uid' attribute of represented XML element
    @type _uid: int

    @ivar _structure: object handling manipulation of the 'structure' element related
                      to the represented element; its L{uid<barIndexerStructureElement.uid>}
                      value overrides the L{_uid} value if given
    @type _structure: L{barIndexerStructureElement}

    @ivar parent: object handling manipulations of the 'group' element parental to the 
                  represented element
    @type parent: L{barIndexerGroupElement}

    @ivar children: objects handling manipulations of the 'group' elements child to the
                    represented element
    @type children: [L{barIndexerGroupElement}, ...]
    """
    _elementName = 'group'
    _elementAttributes = ['name', 'id', 'fill', 'fullname', 'uid', 'ontologyid']
    
    def __init__(self, **kwargs):
        """
        Accepted keyword arguments:
          - 'name' (str) - value of the 'name' attribute of represented XML
             element,
          - 'id' (int) - value of the 'id' attribute of represented XML
             element,
          - 'fill' (str) - value of the 'fill' attribute of represented XML
            element,
          - 'fullname' (str) - value of the 'fullname' attribute of represented
             XML element,
          - 'uid' (int) - value of the 'uid' attribute of represented XML
            element,
          - 'structure' (L{barIndexerStructureElement}) - object handling
            manipulation of the structure related to the group;
            its L{uid<barIndexerStructureElement.uid>} overrides the L{uid}
            argument if given,
          - 'ontologyid' - value of the 'ontologyid' of represented XML.
        """
        self.structure   = None

        # Set initial settings
        for attribute in self._elementAttributes:
            setattr(self, attribute, kwargs.get(attribute))

        if 'structure' in kwargs:
            self.structure   = kwargs['structure']
        
        # By default parents and children list is empty
        self.parent = None
        self.children = []
    
    def __getName(self):
        """
        @return: value of the 'name' attribute of represented XML element
        @rtype: str
        """        
        return self._name
    
    def __setName(self, newName):
        """
        Set the value of the 'name' attribute  of represented XML element.

        @param newName: a new value of the 'name' attribute  of represented XML element
        @type newName: str
        """
        self._name = newName
    
    def __getGID(self):
        """
        @return: value of the 'id' attribute  of represented XML element
        @rtype: int
        """
        return self._id
    
    def __setGID(self, newID):        
        """
        Set value of the 'id' attribute  of represented XML element.

        @param newID: value of the 'id' attribute  of represented XML element
        @type newID: int
        """
        self._id = int(newID)
    
    def __getFill(self):
        """
        @return: value of the 'fill' attribute  of represented XML element
        @rtype: str
        """
        return self._fill
    
    def __setFill(self, newFill):        
        """
        Set value of the 'fill' attribute  of represented XML element.

        @param newFill: value of the 'fill' attribute  of represented XML element
        @type newFill: str
        """
        self._fill = newFill
    
    def __getFullname(self):
        """
        @return: value of the 'fullname' attribute  of represented XML element
        @rtype: str
        """
        return self._fullname
    
    def __setFullname(self, newFullName):        
        """
        Set value of the 'fullname' attribute  of represented XML element.

        @param newFullName: value of the 'fullname' attribute  of represented XML element
        @type newFullName: str
        """
        if newFullName:
            self._fullname = unicode(newFullName)
    
    def __getUID(self):
        """
        @return: value of the 'uid' attribute of represented XML element
        @rtype: int
        """
        if self._structure != None:
            return self._structure.uid
        return self._uid
    
    def __setUID(self, newUID):        
        """
        Set value of the 'uid' attribute  of represented XML element.

        @param newUID: value of the 'uid' attribute  of represented XML element
        @type newUID: int

        @note: If L{_structure} is assigned the ValueError is raisen.
        """
        # uid is read only when structure is assigned
        if self._structure != None:
            raise ValueError, "uid is read only property when corresponding structure is assigned."
        
        # uid can be none if the group is not among paths
        # error if None given to int()
        if newUID == None:
            nuid = newUID
        else:
            nuid = int(newUID)
        self._uid = nuid
    
    def __getStructure(self):
        """
        @return: object representing the 'structure' element related to represented element
        @rtype: L{barIndexerStructureElement}
        """
        return self._structure
    
    def __setStructure(self, newStructure):
        """
        Assign L{_structure} an object representing the 'structure' element related to represented element.

        @param newStructure: an object representing the 'structure' element related
                             to represented element
        @type newStructure: L{barIndexerStructureElement}
        """
        if newStructure == None:
            self._uid = None
        self._structure = newStructure
    
    def __getUidList(self):
        """
        Return list of 'uid' attributes of 'structure' elements assigned to the represented element.
        'structure' elements are gathered from all children as well as from the root element.
        
        @rtype: [int, ...]
        @return: identifiers of 'structure' elements related to the represented
                 hierarchy group.
        """
        allUids = base.flatten(\
                self.__getMappedChildList(depth=999, properties=('uid',)))
        return filter(lambda x: isinstance(x, int), allUids)
    
    def __setUidList(self, newValues):
        """
        Raise ValueError.
        """
        raise ValueError, "uidList is read only property."
    
    def getXMLelement(self):
        groupElement  = barIndexerElement.getXMLelement(self)
       
        orderedChildren = sorted(self.children, key = lambda x: x.name) 
        for childElement in orderedChildren:
            groupElement.appendChild(childElement.getXMLelement())
        
        return groupElement
    
    @classmethod
    def fromXML(cls, sourceXMLElement, indexer=None):
        """
        Creates object from its (valid) xml representation.

        @type  sourceXMLElement: xml.dom.Node
        @param sourceXMLElement: XML description of the C{barIndexerGroupElement} object
                                 to be created.

        @type indexer: L{barIndexer}
        @param indexer: the object encapsulating returned class instance
        
        @return: Object based on sourceXMLElement description.
        @rtype: cls
        """
        result = barIndexerElement.fromXML(sourceXMLElement, cls, indexer=indexer)
        
        for child in sourceXMLElement.childNodes:
            if child.nodeType == dom.Node.ELEMENT_NODE:
                result.children.append(cls.fromXML(child))
        return result
    
    def getStructureNameIterator(self, depth=999):
        """
        @param depth: hierarchy tree iteration depth limit
        @type depth: int

        @return: iterator over names of structures composing the group
                 in the hierarchy tree deep up to the given L{depth}
        @rtype: generator
        """
        if self._structure != None:
            yield self._structure.name
        elif self._uid != None:
            yield self.name

        if depth > 0:
            for child in self.children:
                for name in child.getStructureNameIterator(depth - 1):
                    yield name

    def getVisibleGroupIterator(self, depth=999, leavesOnly=False):
        """
        @param depth: hierarchy tree iteration depth limit
        @type depth: int

        @param leavesOnly: True if requested to iterate over names of
                           the leaves of the iteration tree only, False
                           otherwise
        @type leavesOnly: bool

        @return: iterator over groups ascendant to any structure included 
                 in CAF slides in the hierarchy tree deep up to the given 
                 L{depth}
        @rtype: generator
        """
        isVisible = self.uid != None
        isNotLeaf = False

        for group in self.children:
            if depth == 0:
                if isVisible:
                    break
                for subgroup in group.getVisibleGroupIterator(0, leavesOnly):
                    isVisible = True
                    break
            else:
                for subgroup in group.getVisibleGroupIterator(depth - 1, leavesOnly):
                    isVisible = True
                    isNotLeaf = True
                    yield subgroup

        if isVisible and not (leavesOnly and isNotLeaf):
            yield self

    def getChildList(self, depth=1):
        """
        An alias for C{self.L{__getMappedChildList<barIndexerGroupElement.__getMappedChildList>}(depth, ('name',))}
        """
        return self.__getMappedChildList(depth, ('name',))
    
    def getNameUidChildList(self, depth=1):
        """
        An alias for C{self.L{__getMappedChildList<barIndexerGroupElement.__getMappedChildList>}(depth, ('name', 'id'))}
        """
        return self.__getMappedChildList(depth, ('name', 'id'))
    
    def getNameFullNameUid(self, depth=1):
        """
        An alias for C{self.L{__getMappedChildList<barIndexerGroupElement.__getMappedChildList>}(depth, ('name', 'fullname', 'id'))}
        """
        return self.__getMappedChildList(depth, ('name', 'fullname', 'id'))
    
    def printHierarchyTree(self, depth = 0):
        """
        Print hierarchy tree of 'group' elements rooted in the represented element.

        @type depth: int
        @param depth: level of nesting - margin for printing
        
        @return: tree representation of hierarchy
        @rtype: str
        """
        tree = self.children
        
        if depth == 0: print self.name
        if tree == None or len(tree) == 0:
            pass
        else:
            for val in tree:
                print >>sys.stderr, "|"+" |   " * depth, val.name
                val.printHierarchyTree(depth+1)
    
    def nextSibling(self):
        """
        An alias for C{self.L{_getSibling<barIndexerGroupElement._getSibling>}(+1)}.
        """
        return self._getSibling(+1)
    
    def prevSibling(self):
        """
        An alias for C{self.L{_getSibling<barIndexerGroupElement._getSibling>}(-1)}.
        """
        return self._getSibling(-1)
    
    def _getSibling(self, direction = -1):
        """
        @type  direction: int
        @param direction: determines, if next or previous sibling is returned
        
        @rtype: L{barIndexerGroupElement}
        @return: next (if C{L{direction} = +1}) or previous (if C{L{direction} = -1})
                 sibling of given group element. If given group element has no parent,
                 the element itself is returned.
        """
        if not self.parent:
            return self
        
        spc = self.parent.children
        index = spc.index(self) + direction
        if index < 0:
            index = 0
        if index > len(spc)-1:
            index = len(spc)-1
        return spc[index]
    
    def __getMappedChildList(self, depth = 1, properties = ('name','id')):
        """
        @param depth: height of the returned hierarchy tree
        @type depth: int

        @param properties: requested attribute names
        @type properties: (str, ...)

        @return: tuple-based hierarchy tree containing tuples with requested attributes
                 of 'group' elements rooted in the represented element
        @rtype: tuple
        """
        if depth >= 0:
            retList = map(lambda x:\
                    x.__getMappedChildList(depth - 1, properties),  self.children)
            mappedInfo = tuple(map(lambda x: getattr(self,x), properties))
            
            if retList == []:
                return (mappedInfo,)
            else:
                if all(retList):
                    return (mappedInfo, tuple(retList))
                else:
                    return (mappedInfo,)
    
    name = property(__getName, __setName)
    """
    The 'name' attribute of represented XML element.

    @type: str
    """

    id = property(__getGID, __setGID)
    """
    The 'id' attribute of represented XML element.
    
    @type: int
    """

    fill = property(__getFill, __setFill)
    """
    The 'fill' attribute of represented XML element.
    
    @type: str
    """

    fullname  = property(__getFullname, __setFullname)
    """
    The 'fullname' attribute of represented XML element.
    
    @type: str
    """

    uid       = property(__getUID, __setUID)
    """
    The 'uid' attribute of represented XML element.

    Read-only property if a L{barIndexerStructureElement} object is assigned
    to the object.

    @type: int
    """

    uidList   = property(__getUidList, __setUidList)
    """
    List of 'uid' attributes of 'structure' elements assigned to the represented element.

    Read-only property.

    @type: [int, ...]
    """

    structure = property(__getStructure, __setStructure)
    """
    Object representing 'structure' element related to the represented element.

    @type: L{barIndexerStructureElement}
    """


class barIndexerSlideElement(barIndexerElement):
    """
    Class of objects representing 'slide' elements of CAF dataset index file.

    @ivar _coronalcoord: value of the 'coronalcoord' attribute of the represented element
    @type _coronalcoord: str

    @ivar _slidenumber: value of the 'slidenumber' attribute of the represented element
    @type _slidenumber: int

    @ivar _transformationmatrix: value of the 'transformationmatrix' attribute of the represented element
    @type _transformationmatrix: (float, float, float, float)
    """
    _elementName = 'slide'
    _elementAttributes = ['coronalcoord',
                          'slidenumber',
                          'transformationmatrix']
    
    def __init__(self, coronalcoord, slidenumber, transformationmatrix):
        """
        @param coronalcoord: value of the 'coronalcoord' attribute of the represented element
        @type coronalcoord: str

        @param slidenumber: value of the 'slidenumber' attribute of the represented element
        @type slidenumber: convertable to int

        @param transformationmatrix: value of the 'transformationmatrix' attribute of the represented element
        @type transformationmatrix: (float, float, float, float)
        """
        self.coronalcoord = coronalcoord
        self.slideNumber = slidenumber
        self.transformationmatrix = transformationmatrix
    
    def __getCoronalCoord(self):
        """
        @return: value of the 'coronalcoord' attribute of the represented element
        @rtype: str
        """
        return self._coronalcoord
    
    def __setCoronalCoord(self, newValue):        
        """
        Set value of the 'coronalcoord' attribute of represented XML element.

        @param newValue: value of the 'coronalcoord' attribute of represented XML element
        @type newValue: str
        """
        self._coronalcoord = newValue
    
    def __getSlideNumber(self):
        """
        @return: value of the 'slidenumber' attribute of represented XML element
        @rtype: int
        """
        return self._slidenumber
    
    def __setSlideNumber(self, newValue):
        """
        Set value of the 'slidenumber' attribute of represented XML element.
        
        @param newValue: value of the 'slidenumber' attribute of represented XML element
        @type newValue: convertable to int
        """
        self._slidenumber = int(newValue)
    
    def __getTransfomarionMatrix(self):
        """
        @return: value of the 'transformationmatrix' attribute of represented XML element
        @rtype: (float, float, float, float)
        """
        return self._transformationmatrix
    
    def __setTransformationMatrix(self, newValue):
        """
        Set value of the 'transformationmatrix' attribute of represented XML element.

        @param newValue: value of the 'transformationmatrix' attribute of represented XML element
        @type newValue: (float, float, float, float)
        """
        self._transformationmatrix = newValue
    
    def getXMLelement(self):
        slideElement  = barIndexerElement.getXMLelement(self)
       
        slideElement.setAttribute('transformationmatrix',
                                   ','.join(map(str, self.transformationmatrix)))
        return slideElement
 
    @classmethod
    def fromXML(cls, domXMLElement, indexer=None):
        """
        Creates object from its (valid) xml representation.
        
        @type  domXMLElement: xml.dom.Node
        @param domXMLElement: XML description of the C{barIndexerSlideElement} object
                              to be created

        @type indexer: L{barIndexer}
        @param indexer: the object encapsulating returned class instance
        
        @return: object based on L{domXMLElement} description
        @rtype: cls
        """
        transformationmatrix = tuple(map(float,
                domXMLElement.getAttribute('transformationmatrix').split(',')))
        
        return cls(domXMLElement.getAttribute('coronalcoord'),
                   domXMLElement.getAttribute('slidenumber'),
                   transformationmatrix)
    
    coronalcoord = property(__getCoronalCoord, __setCoronalCoord)
    """
    Value of the 'coronalcoord' attribute of represented XML element.

    @type: str
    """

    slideNumber = property(__getSlideNumber, __setSlideNumber)
    """
    Value of the 'slidenumber' attribute of represented XML element.

    @type: int
    """

    slidenumber = slideNumber
    """
    An alias for C{self.L{slideNumber<barIndexerSlideElement.slideNumber>}}
    """

    name = slideNumber
    """
    An alias for C{self.L{slideNumber<barIndexerSlideElement.slideNumber>}}
    """

    transformationmatrix = property(__getTransfomarionMatrix,  __setTransformationMatrix)
    """
    Value of the 'transformationmatrix' attribute of represented XML element.

    @type: (float, float, float, float)
    """


class barIndexerStructureElement(barIndexerElement):
    """
    Class of objects representing 'structure' elements of CAF dataset index file.
    
    @ivar _name: value of the 'name' attribute of the represented element
    @type _name: str
    
    @ivar _bbx: value of the 'bbx' attribute of the represented element
    @type _bbx: L{barIndexerStructureElement._clsBoundingBox}
    
    @ivar _uid: value of the 'uid' attribute of the represented element
    @type _uid: int 
    
    @ivar _type: value of the 'type' attribute of the represented element
    @type _type: str
    
    @ivar _slides: 'slide' element attribute 'slidenumber' to 'slide' element
                   representation mapping for 'slide' elements associated with
                   represented 'structure' element
    @type _slides: {int: L{barIndexerSlideElement}, ...}
    """
    _elementName = 'structure'
    _elementAttributes = ['name', 'bbx', 'type', 'uid']
    
    def __init__(self, name, bbx, uid, type = None, slideList = None):
        """
        @param name: value of the 'name' attribute of the represented element
        @type name: str
        
        @param bbx: value of the 'bbx' attribute of the represented element
        @type bbx: L{barIndexerStructureElement._clsBoundingBox}
        
        @param uid: value of the 'uid' attribute of the represented element
        @type uid: convertable to int
        
        @param type: value of the 'type' attribute of the represented element
        @type type: str
        
        @param slideList: representations of 'slide' elements related to
                          the represented element
        @type slideList: L{barIndexerSlideElement} or [L{barIndexerSlideElement}, ...] 
        
        """
        self.name = name
        self.bbx = bbx 
        self.uid = uid
        self.type = type
        
        self._slides = dict()
        if slideList != None:
            self.addSlide(slideList)
    
    def getXMLelement(self):
        structureDocument = dom.Document()
        structureDocument.encoding = base.BAR_XML_ENCODING
        structureElement = barIndexerElement.getXMLelement(self)
        
        slideListElement = structureDocument.createElement('slides')
        slideListText = " ".join(map(str, self.slideList))
        slideListNode = structureDocument.createTextNode(slideListText)
        
        slideListElement.appendChild(slideListNode)
        structureElement.appendChild(slideListElement)
        return structureElement
    
    @classmethod
    def fromXML(cls, domXMLElement, indexer=None):
        """
        Creates object from its (valid) xml representation.
        
        @type  domXMLElement: xml.dom.Node
        @param domXMLElement: XML description of the C{barIndexerStructureElement}
                              object to be created.
        
        @type indexer: L{barIndexer}
        @param indexer: the object encapsulating returned class instance
        
        @return: object based on L{domXMLElement} description
        @rtype: cls
        """
        result = barIndexerElement.fromXML(domXMLElement, cls, indexer=indexer)
        
        result.bbx = cls._clsBoundingBox(tuple(map(float, result.bbx.split(','))))
        for slides in domXMLElement.getElementsByTagName('slides'):
            for text in slides.childNodes:
                if text.nodeType == dom.Node.TEXT_NODE:
                    slideNumbers = map(int, text.data.strip().split())
                    map(lambda x: result.addSlide(indexer.slides[x]), slideNumbers)
        return result
     
    def __getBbx(self):
        """
        @return: value of the 'bbx' attribute of the represented element
        @rtype: L{barIndexerStructureElement._clsBoundingBox}
        """
        return self._bbx
    
    def __setBbx(self, newValue):
        """
        Set value of the 'bbx' attribute of the represented element.

        @param newValue: value of the 'bbx' attribute of the represented element
        @type newValue: L{barIndexerStructureElement._clsBoundingBox}
        """
        self._bbx = newValue
    
    def __getName(self):
        """
        @return: value of the 'name' attribute of the represented element
        @rtype: str
        """
        return self._name
    
    def __setName(self, newValue):
        """
        Set value of the 'name' attribute of the represented element.

        @param newValue: value of the 'name' attribute of the represented element
        @type newValue: str
        """
        self._name = newValue
    
    def __getUid(self):
        """
        @return: value of the 'uid' attribute of the represented element
        @rtype: int
        """
        return self._uid
    
    def __setUid(self, newValue):
        """
        Set value of the 'uid' attribute of the represented element.

        @param newValue: value of the 'uid' attribute of the represented element
        @type newValue: convertable to int
        """
        self._uid = int(newValue)
    
    def __getType(self):
        """
        @return: value of the 'type' attribute of the represented element
        @rtype: str
        """
        return self._type
    
    def __setType(self, newValue):
        """
        Set value of the 'type' attribute of the represented element.

        @param newValue: value of the 'type' attribute of the represented element
        @type newValue: str or None
        """
        assert type(newValue) is str or type(newValue) is unicode\
               or newValue == None, "String or 'None' value expected"
        self._type = newValue
    
    def __getSlideList(self):
        """
        @return: an ordered list of 'slidenumber' attributes of 'slide' elements
                 related to the represented element
        @rtype: [int, ...]
        """
        return sorted(list(self._slides))
    
    def __setSlideList(self, newValue):
        """
        Raise ValueError.
        """
        raise ValueError, "Slide list is readonly property."
    
    def addSlide(self, slidesToAppend):
        """
        Assign 'slide' element(s) to the represented element.

        @param slidesToAppend: representation of 'slide' element(s) to be assigned
                               to the represented element
        @type slidesToAppend: L{barIndexerSlideElement} or [L{barIndexerSlideElement}, ...]
        """
        if not hasattr(slidesToAppend, '__getitem__'):
            slidesToAppend = [slidesToAppend]
        self._slides.update((x.slidenumber, x) for x in slidesToAppend)
    
    def __getSlideSpan(self):
        """
        @rtype: (int, int)
        @return: The lowest and the highest value of 'slidenumber' attribute of
                 'slide' elements related to represented element 
        """
        return ( min(self.slideList), max(self.slideList) )
    
    def __setSlideSpan(self, newValue):
        """
        Raise ValueError.
        """
        raise ValueError, "Slide span is readonly property."
    
    name     = property(__getName, __setName)
    """
    Value of the 'name' attribute of the represented element.

    @type: str
    """

    bbx      = property(__getBbx, __setBbx)
    """
    Value of the 'bbx' attribute of the represented element.

    @type: L{barIndexerStructureElement._clsBoundingBox}
    """

    uid      = property(__getUid, __setUid)
    """
    Value of the 'uid' attribute of the represented element.

    @type: int
    """

    type = property(__getType, __setType)
    """
    Value of the 'type' attribute of the represented element.

    @type: str
    """

    slideList= property(__getSlideList, __setSlideList)
    """
    Ordered list of 'slidenumber' attributes of 'slide' elements related
    to the represented element

    Read-only property.

    @type: [int, ...]
    """

    slideSpan= property(__getSlideSpan, __setSlideSpan)
    """
    Slide span (the lowest and the highest value of 'slidenumber' attribute
    of 'slide' elements related to represented element).

    Read-only property.

    @type: (int, int)
    """


class barIndexer(barIndexerObject):
    """
    Class of objects representing whole CAF dataset index.

    The class provides also methods to create CAF dataset index de novo.
    
    It is assumed that structure names are unique and it is not necessary to introduce
    another uniqe ID.  However, a kind of UID (unique ID) is introduced inside
    the index. The UID is used to create complex structure hierarchy.

    Please note that this class operates in two ways when creating CAF dataset index:
        
        1. First stage is collecting information about slides and structures.
           When slide is parsed, module extracts all information about slide number,
           spatial coordinates etc. 
           
        2. Second stage is generating XML representation of stored data.
           XML file is generated and saved.
    
    @note: Be advised that hierarchy and mappings should be assigned in defined
    order:
        
        1. Indexing all slides 
        2. Defining hierarchy (using L{createFlatHierarchy<createFlatHierarchy>}
           or L{setParentsFromFile<setParentsFromFile>}),
        3. Then assigning full name mapping using e.g. using
           L{self.fullNameMapping<self.fullNameMapping>} or
           L{setNameMappingFromFile<setNameMappingFromFile>},
        4. Assigning color mapping using
           L{self.colorMapping<self.colorMapping>} or
           L{setColorMappingFromFile<setColorMappingFromFile>}.
    
    
    @group color_mappings: *ColorMapping*
    @group fullname_mappings: *NameMapping*
    @group hierarchy: *Hierarchy*
    
    @todo: Handle utf-8 structure names somehow...

    @cvar _requiredInternalData: names of required CAF dataset properties
    @type _requiredInternalData: [str, ...]

    @cvar _elementsList: names of XML elements partitioning CAF dataset index file
    @type _elementsList: [str, ...]

    @cvar _initialIDs: initial values of UID/GID sequences
    @type _initialIDs: {str: int}

    @cvar _indexerElement: parental class for classes of objects representing
                           encapsulated elements
    @type _indexerElement: class

    @cvar _propertyElement: class of objects representing 'property' elements
    @type _propertyElement: class

    @cvar _groupElement: class of objects representing 'group' elements
    @type _groupElement: class

    @cvar _slideElement: class of objects representing 'slide' elements
    @type _slideElement: class

    @cvar _structureElement: class of objects representing 'structure' elements
    @type _structureElement: class

    @ivar _uid: current value of UID sequence
    @type _uid: int

    @ivar _gid: current value of GID sequence
    @type _gid: int

    @ivar _hierarchyGroups: hierarchy group name to object representing related 
                            'group' element mapping
    @type _hierarchyGroups: {str : L{_groupElement}, ...}

    @ivar _slides: CAF slide number to object representing related 'slide' element
                   mapping
    @type _slides: {int : L{_slideElement}, ...}

    @ivar _properties: CAF dataset property name to object representing related 
                       'property' element mapping
    @type _properties: {str : L{_propertyElement}, ...}

    @ivar _structures: structure name to object representing related 'structure'
                       element mapping
    @type _structures: {str : L{_structureElement}, ...}

    @ivar _fullNameMapping: cached hierarchy group name to full name mapping
    @type _fullNameMapping: {str : str}

    @ivar _colorMapping: cached hierarchy group name to colour mapping dictionary
    @type _colorMapping: {str : str}

    @ivar _hierarchyRootElementName: name of the superior group of the hierarhy
                                     gathering all structures
    @type _hierarchyRootElementName: str

    @ivar cafDirectory: path to the directory where the CAF dataset index file
                        is located
    @type cafDirectory: str
    """
    _requiredInternalData = ['ReferenceWidth', 'ReferenceHeight',
            'FilenameTemplate', 'RefCords', 'CAFName', 'CAFComment',
            'CAFCreator', 'CAFCreatorEmail', 'CAFCompilationTime',
            'CAFSlideUnits', 'CAFFullName', 'CAFAxesOrientation']
    
    _elementsList = ['slideindex',
                     'atlasproperties',
                     'slidedetails',
                     'structureslist',
                     'hierarchy']
    
    _initialIDs = {'uid': 100000,
                   'gid': 200000}
   
    _indexerElement = barIndexerElement
    _propertyElement = barIndexerPropertyElement
    _groupElement = barIndexerGroupElement
    _slideElement = barIndexerSlideElement
    _structureElement = barIndexerStructureElement
   
    def __init__(self, hierarchyRootElementName=CONF_HIERARCHY_ROOT_NAME):
        """
        @type  hierarchyRootElementName: str
        @param hierarchyRootElementName: Name of the root element of the
                                         hierarchy. The root element is
                                         the superior group of the hierarhy
                                         gathering all structures. 
                                         L{CONF_HIERARCHY_ROOT_NAME} by default.
        """
        self._uid = self._initialIDs['uid'] # Initial number for UID generation
        self._gid = self._initialIDs['gid'] # Initial number for GID generation
        
        # Define empty structure hierarchy tree:
        self._hierarchyGroups = {}
        
        # Define placeholder for structures
        self._slides     = {}
        self._properties = {}
        self._structures = {}
        
        self._fullNameMapping = None #Ultimately dict
        self._colorMapping    = None #Ultimately dict
        
        self._hierarchyRootElementName = hierarchyRootElementName
        
        # CAF dataset location
        self.cafDirectory = None
    
    def __fromXML(cls, sourceXMLElement):
        cafdirectory = None
        
        # Argument type chcecking
        if type(sourceXMLElement) is str or type(sourceXMLElement) is unicode:
            if os.path.exists(sourceXMLElement):
                # sourceXMLElement is a valid file path
                slideindexElement = dom.parse(sourceXMLElement)
                cafdirectory = os.path.dirname(sourceXMLElement)
            else:
                # sourceXMLElement is assumed to be an XML string
                slideindexElement = dom.parseString(sourceXMLElement)
        elif isinstance(sourceXMLElement, dom.Node):
            # sourceXMLElement is a dom.Node
            slideindexElement = sourceXMLElement
        elif hasattr(sourceXMLElement, 'read'):
            # sourceXMLElement is object similiar to file-object
            xmlString = sourceXMLElement.read()
            slideindexElement = dom.parseString(xmlString)
        else:
            # unsupported sourceXMLElement type
            raise TypeError, "Bad type of sourceXMLElement argument."
        
        (propertiesElement,
         slidedetailsElement,
         structurelistElement,
         hierarchyElement) =\
                map(lambda x: slideindexElement.getElementsByTagName(x)[0],
                    cls._elementsList[1:])
        
        result = cls()
        result.cafDirectory = cafdirectory
        # the mainloop list contains tuples
        # (sourceXMLElement, elementClass, destination). Each tuple
        # controls an iteration the of following for loop - the destination
        # dictionary is being filled with instances of the elementClass class,
        # that were based on children of the sourceXMLElement dom XML node
        mainloop = [(propertiesElement, cls._propertyElement,
                     result._properties),
                    (slidedetailsElement, cls._slideElement,
                     result._slides),
                    (structurelistElement, cls._structureElement,
                     result._structures),
                    (hierarchyElement, cls._groupElement,
                     result._hierarchyGroups)]
        
        for (sourceXMLElement, elementClass, destination) in mainloop:
            for xmlElement in sourceXMLElement.childNodes:
                if xmlElement.nodeType == dom.Node.ELEMENT_NODE and\
                        xmlElement.tagName == elementClass._elementName:
                    #print cls.__name__, elementClass.__name__
                    newElement = elementClass.fromXML(xmlElement, indexer=result)
                    # warning - may violate encapsulation of barIndexerPropertyElement
                    destination[newElement.name] = newElement
        
        # According to CAF specification, the <hierarchy> XML node contains one
        # <group> node, that is the root element of the hierarchy tree.
        (result.hierarchyRootElementName, group) =\
                                          result._hierarchyGroups.items()[0]
        
        # The group hierarchy tree contains important information about
        # color mapping, fullname mapping, hierarchy and UID/GID maximum value.
        # The information has to be copied to the result object.
        result.__addGroup(group)
        result.__normaliseIDs()
        return result
    
    def normaliseIDs(self):
        """
        An alias for C{self.L{__normaliseIDs}()}.
        """
        return self.__normaliseIDs()
    
    def __normaliseIDs(self):
        """
        Normalise ID and UID of groups and structures.
        """
        
        # reset ID generators
        (self._gid, self._uid) = map(lambda x: self._initialIDs[x], ['gid', 'uid'])
        # list of touples (attrName, idGenerator, src, dst) controlling iteration of top-level for loop.
        # attrName is the name of object ID attribute to be normalised, idGenerator - ID generator
        # for barIndexer object, src - list of objects containing every ID value in the object,
        # dst - list of lists of objects to be normalised with uniformed ID values
        mainloop = [('id', lambda: self.gid, self._hierarchyGroups),
        #             [self._hierarchyGroups]),
                    ('uid', lambda: self.uid, self._structures)]#,
        #             [self._structures, self._hierarchyGroups])]

        for (attrName, idGenerator, src) in mainloop:
            # oldVals - redundant list of all ID values in the object ordered by the name of group
            # (or structure) containing it
            oldVals = (getattr(y, attrName) for y in\
                       sorted((x for x in src.itervalues() if hasattr(x, attrName)\
                                                           and getattr(x, attrName) != None),
                              key=lambda x: x.name))
            
            try:
                # newVals - old ID to new ID mapping dictionary
                newVals = {}
                # because of ID generator the order of execution is important!
                for val in oldVals:
                    if val in newVals:
                        # ID is ambiguous
                        print "ID = %d is ambigous, trying to fix it" % val
                        raise KeyError

                    newVals[val] = idGenerator()

                # iterate an iterator over objects in dst updating ID attributes
                # of the objects according to newVal dictionary
                for x in src.itervalues():
                    if hasattr(x, attrName) and getattr(x, attrName) != None:
                        setattr(x, attrName, newVals[getattr(x, attrName)])

            except KeyError:
                # an attempt of IDs disambiguation

                # reset ID generators
                (self._gid, self._uid) = map(lambda x: self._initialIDs[x], ['gid', 'uid'])
                names = set()
                
                elementList = sorted((x for x in src.itervalues() if hasattr(x, attrName)\
                                                               and getattr(x, attrName) != None),
                                  key=lambda x: x.name)

                for element in elementList:
                    if element.name in names:
                        print element.name, "is also ambigous"
                        raise KeyError, "name %s is ambiguous" % element.name
                    names.add(element.name)
                    if hasattr(element, attrName) and getattr(element, attrName) != None:
                        setattr(element, attrName, idGenerator())

    def __getGID(self):
        """
        @return: value of the next element of the GID sequence
        @rtype: int
        """
        self._gid += 1
        return self._gid

    def __setGID(self, val):
        """
        Increase the value of the current element of the GID sequence.

        @type val:  int
        @param val: a new value of the current element of the GID sequence

        @note: L{val} must be greater than the value of the current element
               of the GID sequence.
        """
        assert self._gid <= val, "gid can not be reduced"
        self._gid = max(self._gid, val)
    
    def __getUID(self):
        """
        @return: value of the next element of the UID sequence
        @rtype: int
        """
        self._uid += 1
        return self._uid
    
    def __setUID(self, val):
        """
        Increase the value of the current element of the UID sequence.

        @type val:  int
        @param val: a new value of the current element of the UID sequence.

        @note: L{val} must be greater than the value of the current element
               of the UID sequence.
        """
        assert self._uid <= val, "uid can not be reduced"
        self._uid = max(self._uid, val)
        
    def __indexStructures(self, structure, slide):
        """
        Index provided structure with slide. If structure already exists 
        in index only new path are appended to it, otherwise new index entry 
        for this structure is created.

        @type  structure: L{barGenericStructure}
        @param structure: structure to index

        @type  slide: L{_slideElement}
        @param slide: slide to be indexed with the structure
        """
        # If given structure exists:
        if structure.name not in self._structures:
            self._structures[structure.name] =\
                 self._structureElement(\
                    structure.name,
                    self._clsBoundingBox(structure.bbx),
                    self.uid,
                    slideList = slide)
        # Otherwise:
        else:
            self._structures[structure.name].addSlide(slide)
            self._structures[structure.name].bbx+=self._clsBoundingBox(structure.bbx)

    def __getFullNameMapping(self):
        """
        @return: hierarchy group name to full name mapping
        @rtype: {str : str}

        @note: Result of the method is cached in L{_fullNameMapping}.
        """
        if self._fullNameMapping == None:
            self._fullNameMapping =\
             dict(map(lambda (k, v): (k, v.fullname), self.groups.iteritems()))
        return self._fullNameMapping
    
    def __setFullNameMapping(self, sourceDictionary=None, dummyNameElement="------"):
        """
        Assign full names to the hierarchy groups. Update cached hierarchy
        group name to full name mapping.

        @param sourceDictionary: hierarchy group name to full name assignment
        @type sourceDictionary: {str : str}

        @param dummyNameElement: full name assigned to groups not included in
                                 L{sourceDictionary}
        @type dummyNameElement: str

        @note: Full name mapping has to be assigned after creating strucutre
               hierarchy - either flat or structured.
        """
        #TODO: Provide documentation
        if sourceDictionary != None:
            self._fullNameMapping = sourceDictionary
        else:
            sourceDictionary = self.fullNameMapping
        
        for group in self._hierarchyGroups.values():
            # Assign fullname mapping. If given group element has no fullname
            # use the goup name as the fullname
            group.fullname = sourceDictionary.get(group.name, group.name)
    
    def setNameMappingFromFile(self, filename, nameCol=0, fullNameCol=1):
        """
        Assign full names to the hierarchy groups. Update cached hierarchy
        group name to full name mapping.

        @type filename: str
        @param filename: path to the file containing name to full name assignment

        @type nameCol: int
        @param nameCol: column containing names

        @type fullNameCol: int
        @param fullNameCol: column containing full names
        """
        fullNameDictionary =\
                base.getDictionaryFromFile(filename, nameCol, fullNameCol)
        self.fullNameMapping = fullNameDictionary
    
    def __setHierarchyRoot(self, hierarchyRootElementName):
        """
        Define the name of the superior group of the CAF dataset structures hierarhy.

        @param hierarchyRootElementName: name of the superior group of the CAF
                                         dataset structures hierarhy
        @type hierarchyRootElementName: str
        """
        self._hierarchyRootElementName = hierarchyRootElementName 
    
    def __getHierarchyRoot(self):
        """
        @return: name of the superior group of the CAF dataset structures hierarhy
        @rtype: str
        """
        return self._hierarchyRootElementName
    
    def __getColorMapping(self):
        """
        @return: hierarchy group name to colour mapping
        @rtype: {str : str}

        @note: Result of the method is cached in L{_colorMapping}.
        """
        if self._colorMapping == None:
            self._colorMapping =\
             dict(map(lambda (k, v): (k, v.fill), self.groups.iteritems()))
        return self._colorMapping
    
    def __setColorMapping(self, sourceDictionary=None, dummyElementColor="#777777"):
        """
        Assign colours to the hierarchy groups. Update cached hierarchy
        group name to colour mapping.

        @param sourceDictionary: hierarchy group name to colour assignment
        @type sourceDictionary: {str : str}

        @param dummyElementColor: colour assigned to groups not included in
                                 L{sourceDictionary}
        @type dummyElementColor: str

        @note: Color mapping has to be assigned after creating strucutre
               hierarchy - either flat or structured.
        """
        if sourceDictionary != None:
            self._colorMapping = sourceDictionary
        else:
            sourceDictionary = self.colorMapping
        
        # Iterate over all group structures and try to assign colors to
        # every structure. If there is no mapping strutc => color, apply dummy
        # color
        for group in self._hierarchyGroups.values():
            newCol = sourceDictionary.get(group.name, dummyElementColor)
            if newCol.startswith("#"):
                group.fill = newCol
            else:
                group.fill = "#" + newCol
    
    def setColorMappingFromFile(self, colorFilename, nameCol = 0, colourCol = 1 ):
        """
        Assign colours to the hierarchy groups. Update cached hierarchy
        group name to colour mapping.

        @type colorFilename: str
        @param colorFilename: path to the file containing name to colour assignment

        @type nameCol: int
        @param nameCol: column containing names

        @type colourCol: int
        @param colourCol: column containing colour
        """
        ColorFillDictionary =\
                base.getDictionaryFromFile(colorFilename, nameCol, colourCol)
        self.colorMapping = ColorFillDictionary

    def fixOrphanStructures(self, parentGrpName = None):
        """
        Search for structures not covered by hierarchy, then bind them to
        the requested hierarchy group.
        
        @param parentGrpName: name of group element which orphan structures
                              are binded to; if C{None} - orphan structures are
                              binded directly to hierarchy root element
        @type  parentGrpName: str
        
        @note: If hierarchy group of name L{parentGrpName} does not exist it
               is created and binded directly to hierarchy root element.
        """

        # None parent means that orphans will be binded to hierarhy root
        if parentGrpName == None:
            parentGrpName = self._hierarchyRootElementName
        elif parentGrpName not in self._hierarchyGroups:
            # Chceck if parent node exist, create it if not. Newly created group
            # will have hierarchy root as its parent.
            self._hierarchyGroups[parentGrpName] =\
                    self._groupElement(parentGrpName, self.gid)
            self._setHierarchyRelation(parentGrpName, self._hierarchyRootElementName)
        
        # Extract names of orphan structures
        orphans = [name for name in self.structures\
                if not name in self._hierarchyGroups]
        
        # Fore every orphan create corresponding structure and bind it to the
        # parent group element
        for structureName in orphans:
            group = self._groupElement(\
                      structureName,
                      self.gid,
                      structure=self._structures[structureName]) 
            self._hierarchyGroups[structureName] = group
            self._setHierarchyRelation(structureName, parentGrpName)
    
    def _setHierarchyRelation(self, child, parent):
        """
        Create parent - child relation between two hierarchy groups.
        
        @type  child: str
        @param child: Name of the child element
        
        @type  parent: str
        @param parent: Name of the parent element
        """
        parentGroup = self._hierarchyGroups[parent]
        childGroup  = self._hierarchyGroups[child]
        parentGroup.children.append(childGroup)
        childGroup.parent = parentGroup
    
    def __setHierarchy(self, sourceDictionary):
        """
        Create structure hierarchy according to provided relation.
        
        @type  sourceDictionary: {str : str}
        @param sourceDictionary: children to parent mapping

        @todo: Implement hierarchy validation.

        @attention: the method destroys all existing elements attributes!
        """
        
        #TODO: Implement hierarhy validataion:
        if not self.__validateHierarchy(sourceDictionary): return
        
        # Clear existing hierarchy:
        if len(self._hierarchyGroups):
            del self._hierarchyGroups
            self._hierarchyGroups = {}
        
        # Define unique list of hierarchy elements basing on provided dict
        uniqeNames = list(set(base.flatten(sourceDictionary.items())))
        
        #Create index groups items for each structure
        for groupName in uniqeNames:
            if self._structures.has_key(groupName):
                structure = self._structures[groupName]
            else:
                structure = None
            
            self._hierarchyGroups[groupName]=\
                self._groupElement(groupName, self.gid,
                        structure=structure)
        
        # Bind all group elements into hierarchy by assigning child - parent
        # relation
        for (child, parent) in sourceDictionary.items():
            self._setHierarchyRelation(child, parent)
    
    def __getHierarchy(self):
        """
        @return: tuple-based hierarchy tree
        @rtype: tuple
        """
        brainRoot = self._hierarchyRootElementName
        return self._hierarchyGroups[brainRoot].getChildList(depth=999)
    
    def __validateHierarchy(self, sourceDictionary):
        """
        Just a stub.

        @todo: Implementation.
        """
        return True
        #TODO: Implement this
        pass
    
    def createFlatHierarchy(self):
        """
        Create flat hierary: gather all component structures under common
        superior L{hierarchyRootElementName} hierarchy group element.
        
        No external ontology tree is required.
        
        @note: This method has to be inveoked AFTER indexing all slides.
        """
        
        # Extract all names of structures from self._structures
        listOfStructs = self._structures.keys()
        rootStruct = self._hierarchyRootElementName
        
        flatHierDict ={}
        # Create dictionary by assigning rootStruct to every structure found.
        map(lambda x: flatHierDict.__setitem__(x, rootStruct), listOfStructs)
        
        # Create actual hierarchy from flat dictionary
        self.__setHierarchy(flatHierDict)
    
    def setParentsFromFile(self, hierarchyFilename, childCol = 0, parentCol = 1):
        """
        Create structure hierarchy according to relation provided in the file.

        @type hierarchyFilename: str
        @param hierarchyFilename: path to the child name to parent name mapping
                                  file
        @type childCol: int
        @param childCol: column containing child names
        @type parentCol: int
        @param parentCol: column containing parent names
        """
        cpDictionary =\
                base.getDictionaryFromFile(hierarchyFilename, childCol, parentCol)
        self.hierarchy = cpDictionary
    
    def _validateInternalData(self):
        """
        Perform internal indexed properties validation. If invalid - raise ValueError.
        """
        # Iterate over list of required attributes and checks if they are
        # defined. If an attribute is not defined, raise an exception.
        for dataElement in self._requiredInternalData:
            if not self._properties.has_key(dataElement):
                raise ValueError(\
                        "Required index property not provided: %s.",\
                        (dataElement,))
    
    def indexSingleSlide(self, tracedSlide, slideNumber):
        """
        Register given CAF slide to the CAF dataset index.

        @type  slideNumber: int
        @param slideNumber: slide number
        
        @type  tracedSlide: L{base.barTracedSlide}
        @param tracedSlide: CAF slide representation
        """
        
        print >>sys.stderr, "Indexer: indexing slide %d" % (slideNumber,)
        
        slide = self._slideElement(\
                tracedSlide.metadata[base.BAR_BREGMA_METADATA_TAGNAME].value,
                slideNumber,
                tracedSlide.metadata[base.BAR_TRAMAT_METADATA_TAGNAME].value)
        
        # Iterate over all structures in given slide and create index entry for
        # each of the structure:
        map(lambda struct: self.__indexStructures(struct, slide),\
                tracedSlide.values())
        
        # Extract metadata from the slide
        self._slides[slideNumber] = slide
    
    def getXMLelement(self):
        """
        @return: XML representation of represented CAF dataset index
        @rtype: xml.dom.Document
        """
        # Check if all required properties are assigned
        self._validateInternalData()
        self.__normaliseIDs()
        indexerDocument = dom.Document()
        indexerDocument.encoding=base.BAR_XML_ENCODING
        
        (slideindexElement,
         propertiesElement,
         slidedetailsElement,
         structurelistElement,
         hierarchyElement) =\
                map(lambda x: indexerDocument.createElement(x),
                    self._elementsList)
        
        indexerDocument.appendChild(slideindexElement)
        slideindexElement.appendChild(propertiesElement)
        slideindexElement.appendChild(slidedetailsElement)
        slideindexElement.appendChild(structurelistElement)
        slideindexElement.appendChild(hierarchyElement)
        
        for (name, slide) in sorted(self._slides.items()):
            slidedetailsElement.appendChild(slide.getXMLelement())
        
        for (name, structure) in sorted(self._structures.items()):
            structurelistElement.appendChild(structure.getXMLelement())
        
        for (name, property) in sorted(self._properties.items()):
            propertiesElement.appendChild(property.getXMLelement())
        
        hierarchyElement.appendChild(self._hierarchyGroups[self._hierarchyRootElementName].getXMLelement())
        
        return indexerDocument 
    
    def __addGroup(self, group, parent=None):
        """
        Parse the hierarchy group (sub)tree and update C{self.L{_hierarchyGroups}}
        according to information in the tree nodes; update information about
        parental nodes in the nodes of the tree.

        @type  group: L{barIndexerGroupElement}
        @param group: hierarchy group (sub)tree to be parsed
        
        @type  parent: L{barIndexerGroupElement}
        @param parent: parental node for the L{group} subtree
        """
        name = group.name
        self._hierarchyGroups[name] = group
        group.parent = parent
        for grp in group.children:
            self.__addGroup(grp, group)
        
        if name in self._structures:
            group.structure = self._structures[name]

    def visibleGroups(self, depth = 999, leavesOnly = False):
        """
        An alias for C{self.L{groups}[self.L{hierarchyRootElementName}].L{getVisibleGroupIterator<barIndexerGroupElement.getVisibleGroupIterator>}()}.
        """
        group = self.hierarchyRootElementName

        return self.groups[group].getVisibleGroupIterator(depth = depth,
                                                          leavesOnly = leavesOnly)
    
    def unfoldSubtrees(self, rootStructures, defaultDepth=0, leavesOnly=False):
        """
        @param rootStructures: names of root elements of hierarchy subtrees or
                               pairs of root element name and depth of the subtree
        @type rootStructures: iterable([str | (str, int), ...])
        
        @param defaultDepth: the default depth of hierarchy subtrees
        @type defaultDepth: int
        
        @param leavesOnly: indicates if only the leaf nodes has to be returned
        @type leavesOnly: bool
        
        @return: names of hierarchy subtree tree nodes related to any structure
                 present in CAF slides
        @rtype: set([str, ...])
        """
        def unfoldSubtree(arg):
            # check the argument type
            if type(arg) is tuple:
                root, depth = arg
            else:
                root, depth = arg, defaultDepth

            group = self.groups[root]

            return set(x.name\
                       for x in group.getVisibleGroupIterator(depth = depth,
                                                              leavesOnly=leavesOnly))
        
        return reduce(lambda x, y: x | y, (unfoldSubtree(z) for z in rootStructures))

    def __getProperty(self):
        """
        @return: CAF dataset index property name to 'property' element
                 representation mapping
        @rtype: {str : L{barIndexerPropertyElement}}
        """
        return self._properties
    
    def clearProperties(self):
        """
        Remove all CAF dataset index properties.
        """
        self._properties = {}
    
    def updateProperties(self, propsDict):
        """
        Updates properties of the indexer with the data from
        provided dictionary.
        
        @type  propsDict: dict
        @param propsDict: dictionary holding indexer's properties in which keys
                          are names of the properties.
        
        @return: None
        """
        for (name, value) in propsDict.items():
            self._properties[name] = self._propertyElement(name, value)
    
    def __setProperty(self, newValue):
        """
        Raise ValueError.
        """
        raise ValueError, "'Properties' is readonly property."
    
    def __setSlides(self, newValue):
        """
        Raise ValueError.
        """
        raise ValueError, "Slides is readonly property."
    
    def __getSlides(self):
        """
        @return: slidenumber to 'slide' element representation mapping
        @rtype: {int : L{barIndexerSlideElement}}
        
        @note: be aware that it is not a copy, but the original dictionary!
        """
        return self._slides
    
    def __setStructures(self, newValue):
        """
        Raise ValueError.
        """
        raise ValueError, "Structures is readonly property."
    
    def __getStructures(self):
        """
        @return: name to 'structure' element representation mapping
        @rtype: {str : L{barIndexerStructureElement}}
        
        @note: be aware that it is not a copy, but the original dictionary!
        """
        return self._structures
    
    def __getUidList(self):
        """
        For each of hierarchy groups find UIDs of structures assigned to it.
        
        Example usage:
            1. Filter out elements which may be reconstructed:
               C{[name for (name, uid) in self.uidList.iteritems() if uid]}
            2. Filter out elements that cannot be reconstructed as they don't
               have children with paths assigned and they do not have uid
               assigned itself:
               C{[name for (name, uid) in self.uidList.iteritems() if not uid]}
        
        @rtype: {str : [int, ...]}
        @return: hierarchy group name to UIDs of assigned structures mapping
        """
        
        return dict(map(lambda x: (x.name, x.uidList),
                        self._hierarchyGroups.values()))
    
    def __setUidList(self, newList):
        """
        Raise ValueError.
        """
        raise ValueError, "uidList is read only property."
    
    def __getHierarchyGroups(self):
        """
        @rtype:  {str : L{barIndexerGroupElement}}
        @return: name to 'group' element representation mapping 
        """
        return self._hierarchyGroups
    
    def __setHierarchyGroups(self, newValue):
        """
        Raise ValueError.
        """
        raise ValueError, "Read only property."
    
    fromXML  = classmethod(__fromXML)
    """
    L{__fromXML} method bound to the class as its classmethod.
    """
    
    _fromXML = staticmethod(__fromXML)
    """
    L{__fromXML} method not bound to the class nor to the class instance.
    """
    
    hierarchy = property(__getHierarchy, __setHierarchy)
    """
    Hierarchy of the CAF dataset structures.
    
    @type: non consistent
    """
    
    hierarchyRootElementName = property(__getHierarchyRoot, __setHierarchyRoot)
    """
    Name of the superior group of the CAF dataset structures hierarhy.
    
    @type: str
    """
    
    groups = property(__getHierarchyGroups, __setHierarchyGroups)
    """
    Name to 'group' element representation mapping.
    
    Read-only property.
    
    @type: {str : L{barIndexerGroupElement}}
    """
    
    properties = property(__getProperty, __setProperty)
    """
    Name to 'property' element representation mapping.
    
    Read-only property.
    
    @type: {str : L{barIndexerPropertyElement}}
    """
    
    slides = property(__getSlides, __setSlides)
    """
    Slide number to 'slide' element representation mapping.
    
    Read-only property.
    
    @type: {str : L{barIndexerSlideElement}}
    """
    
    structures = property(__getStructures, __setStructures)
    """
    Name to 'structure' element representation mapping.
    
    Read-only property.
    
    @type: {str : L{barIndexerGroupElement}}
    """
    
    colorMapping = property(__getColorMapping, __setColorMapping)
    """
    Hierarchy group name to colour mapping.
    
    @type: {str : str}
    """
    
    fullNameMapping = property(__getFullNameMapping, __setFullNameMapping)
    """
    Hierarchy group name to fullname mapping.
    
    @type: {str : str}
    """
    
    uid = property(__getUID, __setUID)
    """
    If read - he value of the next element of the UID sequence.
    
    If write - the value of the current element of the sequence.
    The value of the current element of the sequence can be only increased.
    
    @type: int
    """
    
    gid = property(__getGID, __setGID)
    """
    If read - the value of the next element of the GID sequence.
    
    If write - the value of the current element of the sequence.
    The value of the current element of the sequence can be only increased.
    
    @type: int
    
    @note: The property can be only increased.
    """
    
    uidList = property(__getUidList, __setUidList)
    """
    Hierarchy group name to UIDs of assigned structures mapping.
    
    Read-only property.
    
    @type: {str : [int, ...]}
    """


if __name__=='__main__':
    pass
