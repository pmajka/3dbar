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
The module provides classes necessary to handle basic VTK pipeline manipulation.

G{importgraph}

@var BAR_VTK_TRANSFORMATION: alias to VTK pipeline element class mapping
@type BAR_VTK_TRANSFORMATION: {str: type, ...}

@var VTK_PIPELINE: the default pipeline
@type VTK_PIPELINE: L{barPipeline}

@var DISPLAYABLE: the displayable elements of the L{VTK_PIPELINE}
@type DISPLAYABLE: [parPipeElem, ...]
"""
import __builtin__
import vtk
import xml.dom.minidom as dom
import os

from bar.base import barObject, BAR_XML_ENCODING

# TODO: Clear the file, provide description and documentation
# Tue May 17 15:32:28 CEST 2011

class barVtkMirror(vtk.vtkAppendPolyData):
    def SetInput(self, sourcePolyData):
        mirror_transform = vtk.vtkTransform()
        mirror_transform.Scale(-1,1,1)
        transformer = vtk.vtkTransformPolyDataFilter()
        transformer.SetTransform(mirror_transform)
        transformer.SetInput(sourcePolyData)
        rev = vtk.vtkReverseSense()
        rev.SetInput(transformer.GetOutput())

        self.AddInput(rev.GetOutput())
        self.AddInput(sourcePolyData)

class barVtkConstantPad(object):
    def __init__(self):
        self._input = vtk.vtkImageData()
        self._padding = (0, 0, 0)

    def SetInput(self, imageData):
        self._input = imageData

    def SetPaddingValues(self, padx, pady, padz):
        self._padding = (padx, pady, padz)

    def GetClassName(self):
        return self.__class__.__name__

    def Update(self):
        # If a dummy input is defined  then, probaby a diagnostic run asking
        # for output data type is performed. In such case, just generate a
        # blank ImageData object just to be able to determine filter's output
        # data type.
        if self._input.GetWholeExtent() == (0, -1, 0, -1, 0, -1):
            self._output = self._input
            return

        # XXX: (note the date: Mon Mar 25 22:57:45 CET 2013)
        # Ok, when we arrived here, it means that we're doing sometging
        # significant.
        source = self._input
        self._output = vtk.vtkImageData()

        padx, pady, padz = self._padding
        initial_extent = self._input.GetWholeExtent()
        sx, sy, sz = self._input.GetSpacing()

        if __debug__:
            print "\tInitial image extent: " + str(initial_extent)
            print "\tInitial image origin: " + str(self._input.GetOrigin())
            print "\tRequested padding: %d, %d, %d" % (padx, pady, padz)

        translator = vtk.vtkImageChangeInformation()
        translator.SetExtentTranslation(padx, pady, padz)
        translator.SetOriginTranslation(-padx*sx, -pady*sy, -padz*sz)
        translator.SetInput(source)

        # Now we actually pad the image filling the extended canvas with the
        # "0" value.
        pad_filter = vtk.vtkImageConstantPad()
        pad_filter.SetConstant(0)
        pad_filter.SetOutputWholeExtent(initial_extent[0], initial_extent[1]+2*padx,
                                        initial_extent[2], initial_extent[3]+2*pady,
                                        initial_extent[4], initial_extent[5]+2*padz)
        pad_filter.SetInput(translator.GetOutput())
        pad_filter.Update()

        # Assign the resulting image to the output
        self._output = pad_filter.GetOutput()

        if __debug__:
            print "\tFinal image extent: " + str(self._output.GetWholeExtent())
            print "\tFinal image origin: " + str(self._output.GetOrigin())

    def GetOutput(self):
        self.Update()
        return self._output

class barVtkAllFlip(object):
    def __init__(self):
        self._flip       = [False, False, False]
        self._flipOrigin = [False, False, False]
        self._input = vtk.vtkImageData()

        for (si,bi) in [('On', True), ('Off', False)]:
            for (sj,bj) in [('x',0),('y',1),('z',2)]:
                def flip(self, x, y):
                    self._flip[x] = y

                def origin(self, x, y):
                    self._flipOrigin[x] = y

                setattr(self,'SetFlip'+sj+si, lambda s=self,x=bj,y=bi: flip(s,x,y))
                setattr(self,'SetFlipAbOrigin'+sj+si, lambda s=self,x=bj,y=bi: origin(s,x,y))

    def GetClassName(self):
        return self.__class__.__name__

    def SetInput(self, imageData):
        self._input = imageData

    def Update(self):
        source = self._input
        output = vtk.vtkImageData()
        self._output = vtk.vtkImageData()

        if not any(self._flip):
            output = source

        for i in range(3):
            if self._flip[i]:
                transpose = vtk.vtkImageFlip()
                transpose.SetFilteredAxis(i)
                if self._flipOrigin[i]:
                    transpose.FlipAboutOriginOn()
                else:
                    transpose.FlipAboutOriginOff()
                transpose.SetInput(source)
                transpose.Update()
                output = transpose.GetOutput()
                source = output

        self._output = output

    def GetOutput(self):
        self.Update()
        return self._output


BAR_VTK_TRANSFORMATION = {'barVtkMirror' : barVtkMirror, 'barVtkAllFlip' : barVtkAllFlip, 'barVtkConstantPad' : barVtkConstantPad}

class barPipelineXML(barObject):
    """
    A virtual class parental to all VTK pipeline classes.

    @cvar _elementName: name of the XML element related to the class object.
    @type _elementName: str

    @cvar _singleelements: a list of the singular children XML elements' names
    @type _singleelements: [str, ...]

    @cvar _listelements: a list of the multiple children XML elements' names
    @type _listelements: [str, ...]

    @cvar _attributes: a list of the related XML attributes
    @type _attributes: [str, ...]
    """

    _elementName = None
    _singleelements = []
    _listelements = []
    _attributes = []

    def getXMLelement(self, domDocument = None):
        """
        @param domDocument: DOM XML document for creation of the XML element
                            (if not given, a new DOM XML document object is
                            created)
        @type domDocument: L{xml.dom.minidom.Document}

        @return: DOM XML representation of the object
        @rtype: L{xml.dom.minidom.Element}
        """
        # if no DOM XML document given - create a new object
        if domDocument:
            pipelineDocument = domDocument
        else:
            pipelineDocument = dom.Document()
            pipelineDocument.encoding = BAR_XML_ENCODING

        pipelineXMLElement = pipelineDocument.createElement(self._elementName)

        # set attributes of XML element
        for attr in self._attributes:
            pipelineXMLElement.setAttribute(attr, unicode(getattr(self, attr)))

        # append singular children XML elements
        for el in self._singleelements:
            val = getattr(self, el)
            if val != None:
                if hasattr(val, 'getXMLelement'):
                    pipelineXMLElement.appendChild(val.getXMLelement(pipelineDocument))
                else:
                    elXML = pipelineDocument.createElement(el)
                    elXML.appendChild(pipelineDocument.createTextNode(unicode(val)))
                    pipelineXMLElement.appendChild(elXML)

        # append multiple children XML elements
        for el in self._listelements:
            listelements = getattr(self, el)
            if listelements != None:
                listXML = pipelineDocument.createElement(el)
                pipelineXMLElement.appendChild(listXML)
                for (val, order) in zip(listelements, xrange(len(listelements))):
                    if hasattr(val, 'getXMLelement'):
                        elXML = val.getXMLelement(pipelineDocument)
                    else:
                        elXML = pipelineDocument.createElement('value')
                        elXML.appendChild(pipelineDocument.createTextNode(unicode(val)))
                        elXML.setAttribute('type', unicode(type(val).__name__))
                    elXML.setAttribute('order', unicode(order))
                    listXML.appendChild(elXML)

        return pipelineXMLElement

    @staticmethod
    def _getSingle(xmlElement, tagName, default = None):
        """
        @param xmlElement: DOM XML element
        @type xmlElement: L{xml.dom.minidom.Element}

        @param tagName: name of the singular child XML element
        @type tagName: str

        @param default: value to be returned if L{xmlElement} has no child
                        of name L{tagName}

        @return: value of the requested child XML element
        @rtype: str

        @attention: works properly on the assumption that
                    xmlElement.getElementsByTagName preserves elements order
        """
        elemList = xmlElement.getElementsByTagName(tagName)
        if len(elemList):
            return  elemList[0].firstChild.nodeValue.strip()
        else:
            return default

    @staticmethod
    def _getSingleNested(xmlElement, tagName, childElemName = 'value', default = None):
        """
        @param xmlElement: DOM XML element
        @type xmlElement: L{xml.dom.minidom.Element}

        @param tagName: name of the singular child XML element
        @type tagName: str

        @param childElemName: name of children XML elements of the L{tagName}
                              element
        @type childElemName: str

        @param default: value to be returned if L{xmlElement} has no child
                        of name L{tagName}

        @return: the requested grandchildren XML elements
        @rtype: [Element, ...]

        @attention: works properly on the assumption that
                    xmlElement.getElementsByTagName preserves elements order
        """
        elemList = xmlElement.getElementsByTagName(tagName)
        if len(elemList):
            return elemList[0].getElementsByTagName(childElemName)
        else:
            return default


class barPipeline(barPipelineXML, list):
    """
    VTK pipeline class.
    """

    _elementName = 'pipeline'
    _listelements = ['elements']

    def __generateorder(self):
        """
        Set the order attribute for every pipeline element.
        """
        [setattr(pipeelem, 'order', i) for (i, pipeelem) in enumerate(self)]

    #{ overrided list methods

    def __getslice__(self, i, j):
        return self.__class__(list.__getslice__(self, i, j))

    def __getitem__(self, key):
        if type(key) is slice:
            return self.__class__(list.__getitem__(self, key))
        else:
            return list.__getitem__(self, key)

    def index(self, x):
        for i in xrange(len(self)):
            if id(self[i]) == id(x): return i
        return None

    def remove(self, x):
        del self[self.index(x)]

    #}

    def displayable(self):
        """
        @return: displayable pipeline elements (in pipeline order)
        @rtype: [L{barPipeElem}, ...]
        """
        return [x for x in self if x.displayable]

    def nondisplayable(self):
        """
        @return: nondisplayable pipeline elements (in pipeline order)
        @rtype: [L{barPipeElem}, ...]
        """
        return [x for x in self if not x.displayable]

    @staticmethod
    def __executeElement(vtksource, vtkAlgorithmObj):
        """
        Apply the pipeline element L{vtkAlgorithmObj} to L{vtksource}.

        @param vtksource: VTK data source

        @param vtkAlgorithmObj: pipeline element

        @return: L{vtkAlgorithmObj} object
        """
        vtkAlgorithmObj.SetInput(vtksource.GetOutput())
        vtkAlgorithmObj.Update()
        if __debug__:
            print "\tAppying: " + vtkAlgorithmObj.__class__.__name__
            print "\tOutput data type: " + vtksource.GetOutput().GetClassName()
        return vtkAlgorithmObj

    def execute(self, imImport):
        """
        Apply the pipeline to L{imImport}.

        @param imImport: VTK data source

        @return: result of application of the pipeline to L{imImport}
        """
        return reduce(self.__executeElement, (p() for p in self if p.on), imImport)

    def __fromXML(cls, sourceXMLElement):
        """
        Create a pipeline based on the L{sourceXMLElement}.

        @param sourceXMLElement: the source DOM XML element or a path to the XML
                                 document.
        @type sourceXMLElement: L{xml.dom.minidom.Element} or str

        @return: the pipeline
        @rtype: L{cls}
        """
        # check sourceXMLElement type; load the XML document if necessary
        if type(sourceXMLElement) is str or type(sourceXMLElement) is unicode:
            domXML = dom.parse(sourceXMLElement)
        else:
            if sourceXMLElement.nodeType != dom.Node.ELEMENT_NODE or\
               sourceXMLElement.tagName != cls._elementName:
                raise TypeError, "Invalid XML element provided"
            domXML = sourceXMLElement

        result = cls()

        # append elements to the pipeline
        for node in domXML.getElementsByTagName('elements')[0].childNodes:
            if node.nodeType == dom.Node.ELEMENT_NODE:
                result.append(barPipeElem.fromXML(node))
        return result

    def getXMLelement(self):
        pipelineDocument = dom.Document()
        pipelineDocument.appendChild(\
                        barPipelineXML.getXMLelement(self, pipelineDocument))
        return pipelineDocument

    def getOutputDataTypes(self):
        """
        @return: Dictionary mapping fioter data output type to span of list
                 elements that return given output data type.
        @rtype: {'str':(int,int),...}
        """
        dataTypesList  = map(lambda x: x.outputDataType, self[0:-1])
        uniqeDataTypes = list(set(dataTypesList))
        dataTypesMapping = {}

        for dataType in uniqeDataTypes:
            firstIxd = dataTypesList.index(dataType)
            nElems   = dataTypesList.count(dataType)
            dataTypesMapping[dataType] =\
                    (firstIxd, firstIxd + nElems)
        return dataTypesMapping

    def __setElements(self, val):
        """
        Replace pipeline elements with L{val} content.

        @param val: pipeline elements
        @type val: [barPipeElem, ...]
        """
        self[:] = val

    def __getElements(self):
        """
        @return: elements of the pipeline.
        @rtype: [barPipeElem, ...]
        """
        return list(self)

    elements = property(__getElements, __setElements)
    fromXML = classmethod(__fromXML)
    _fromXML = staticmethod(__fromXML)


class barPipeElem(barPipelineXML):
    """
    VTK pipeline element class.

    @cvar _defaults: default values of object attributes
    @type _defaults: dict

    @ivar cls: the VTK pipeline element class
    @type cls: type
    """
    _defaults = {'on': False,
                 'params': [],
                 'disable': False,
                 'desc': None,
                 'displayable': True}
    _attributes = ['on',
                   'displayable',
                   'disable']
    _singleelements = ['vtkclass',
                       'desc']
    _listelements = ['params']
    _elementName = 'pipelineelement'

    def __init__(self, vtkclass, **kwargs):
        """
        @param vtkclass: name of the VTK pipeline element class
        @type vtkclass: str

        @param kwargs: values of object attributes
        """
        self.vtkclass = vtkclass
        # sets attributes to values from kwargs if present
        # otherwise to default values
        [setattr(self, k, kwargs.get(k, v)) for (k, v) in self._defaults.iteritems()]
        self.default = self.on
        self._widget = None
        self.order = None

        if not self.desc:
            self.desc = self.cls

    def __call__(self):
        """
        @return: VTK pipeline element
        """
        obj = self.cls()
        for param in self.params:
            if param.type is bool:
                getattr(obj,param.name+(param.args[0] and 'On' or 'Off'))()
            else:
                getattr(obj,param.name)(*param.args)
        return obj

    def __getOutputDataType(self):
        """
        """
        return self.cls().GetOutput().GetClassName()

    def __setOutputDataType(self, newValue):
        """
        """
        raise ValueError, "Read only property."

    def set(self, on, show=True):
        """
        Set the element activity and visibility.

        @param on: indicates if the element is turned on
        @type on: bool

        @param show: indicates if the element is visible
        @type show: bool
        """
        self.on = on
        if show and self._widget is not None: self._widget.set_active(on)

    @classmethod
    def fromXML(cls, sourceXMLElement):
        """
        Create the pipeline element based on L{sourceXMLElement}.

        @param sourceXMLElement: XML DOM element
        @type sourceXMLElement: L{xml.dom.minidom.Element}

        @return: the pipeline element
        @rtype: L{cls}
        """
        # check the argument type
        if sourceXMLElement.nodeType != dom.Node.ELEMENT_NODE or\
           sourceXMLElement.tagName != cls._elementName:
            raise TypeError, "Invalid XML element provided"

        # collect the values of the pipeline element attributes
        initArgs = {}
        for attr in cls._attributes:
            if sourceXMLElement.hasAttribute(attr):
                initArgs[attr] = 'True' == sourceXMLElement.getAttribute(attr).strip()

        # collect the values of singular XML element children
        for elem in cls._singleelements:
            initArgs.setdefault(elem, cls._getSingle(sourceXMLElement, elem))

        # collect the pipeline element parameters
        initArgs['params'] =\
            [barParam.fromXML(x) for x\
             in cls._getSingleNested(sourceXMLElement, 'params', 'param', [])]

        return cls(**initArgs)


    def __setCls(self, val):
        """
        @param val:  L{self.cls<barPipeElem.cls>} class (or its name/alias
                     in L{BAR_VTK_TRANSFORMATION})
        @type val: str or type
        """
        # TODO - filtrować val!!!
        if type(val) is str or type(val) is unicode:
            if hasattr(vtk, val):
                v = getattr(vtk, val)
            elif val in BAR_VTK_TRANSFORMATION:
                v = BAR_VTK_TRANSFORMATION[val]
            else:
                raise NotImplementedError, "Unknown class alias: %s" %val
        else:
            v = val
        self.cls = v

    def __getCls(self):
        """
        @return: name of the L{self.cls<barPipeElem.cls>}
        @rtype: unicode
        """
        return unicode(self.cls.__name__)

    vtkclass = property(__getCls, __setCls)
    outputDataType = property(__getOutputDataType, __setOutputDataType)


class barParam(barPipelineXML):
    """
    VTK pipeline element parameter class.

    @cvar _defaults: default values of object attributes
    @type _defaults: dict

    @ivar name: the parameter name
    @type name: str

    @ivar args: the parameter value
    @type args: list

    @ivar defaults: the backup of L{args}
    @type defaults: list

    @ivar type: type of L{args} items
    @type type: type
    """
    _attributes = ['hidden',
                   'display']
    _singleelements = ['name',
                       'desc']
    _listelements =  ['args',
                      'span']
    _elementName = 'param'
    _defaults = {'span':   None,
                 'hidden':  False,
                 'display': False,
                 'desc':    None}

    def __init__(self, name, args, **kwargs):
        """
        @param name: name of the parameter
        @type name: str

        @param args: DOM XML-encoded value of the parameter
        @type args: [Element, ...]

        @param kwargs: values of object attributes
        """
        self.__dict__.update(self._defaults)
        [setattr(self, k, v) for (k, v) in kwargs.iteritems()]
        self.name, self.args = name, args
        self.defaults = list(self.args)

    @classmethod
    def fromXML(cls, xmlElement):
        """
        Create the pipeline element parameter object based on L{sourceXMLElement}.

        @param xmlElement: XML DOM element
        @type xmlElement: L{xml.dom.minidom.Element}

        @return: the pipeline element parameter object
        @rtype: L{cls}
        """
        # check the argument type
        if xmlElement.nodeType != dom.Node.ELEMENT_NODE or\
           xmlElement.tagName != cls._elementName:
            raise TypeError, "Invalid XML element provided"

        # Extract values from elements
        name = cls._getSingle(xmlElement, 'name')
        args = map(cls._getValue, cls._getSingleNested(xmlElement, 'args', default=[]))

        optArgs = {}
        # Optional values
        span = cls._getSingleNested(xmlElement, 'span')
        if span: optArgs['span'] = map(cls._getValue, span)
        optArgs['desc'] = cls._getSingle(xmlElement, 'desc')

        # Extract optional attributtes
        attrs = cls._getAttributesDict(xmlElement)
        optArgs['hidden']  = (attrs.get('hidden') == 'True')
        optArgs['display'] = (attrs.get('display') ==  'True')

        retParam = cls(name, args, **optArgs)
        return retParam

    @staticmethod
    def _getValue(valueNode):
        """
        @param valueNode: DOM XML element describing parameter value component
        @type valueNode: L{xml.dom.minidom.Element}

        @return: the value of the L{valueNode} parsed according to L{valueNode}
                 C{type} attribute
        """
        stringValue = valueNode.firstChild.nodeValue.strip()
        valType     = valueNode.getAttribute('type')
        if valType == 'bool':
            return (stringValue == 'True')
        else:
            return getattr(__builtin__, valType)(stringValue)

    def __setArgs(self, val):
        self.type = type(val[0])
        self.__args = val

    def __getArgs(self):
        return self.__args

    args = property(__getArgs, __setArgs)


VTK_PIPELINE = barPipeline.fromXML(os.path.join(os.path.dirname(__file__), 'default_pipeline.xml'))
DISPLAYABLE = VTK_PIPELINE.displayable()
