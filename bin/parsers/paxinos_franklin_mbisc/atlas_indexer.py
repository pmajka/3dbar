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
import xml.dom.minidom as dom
import datetime
import sys
from config import *
from string import strip, split
from svgpathparse import parsePath, extractBoundingBox, mergeBoundingBox 

"""
G{importgraph}
"""

class AtlasIndexer:
    """
    Class which hold and create index of structures in atlas as well as structure hierarchy.
    
    This class (and probably other clases in atlas parser) assumes that structure names are
    uniqe and we do not need to introduce another unie ID.
    
    However, we need to introduce a kind od UID inside index file. This UID will be used
    to create complex structures internally inside index file. Probably, those UIDs may be
    exported outside index file (for example into database)
    
    Slides are stored in set structure to be sure that slides number would not be duplicated.
    Then, after parsing all slides, sets are converted to list and sorted. This procedure assures
    that slides are saved in ascending order.
    
    G{classtree: AtlasIndexer}
    
    Please note that this module operates in two ways:
        
        1. First stage is a collecting information about slides and structures itself.
           When slide is parsed, module extracts all information about slide number,
           bregma coordinate, stereotaxic coordinate system etc. 
           
           When it comes to structures, all data except path information is cached.
           
        2. Second stage is prepared in order to generate XML representation of stored data.
           XML file is generated and saved.


    sro, 25 sie 2010, 19:06:50 CEST
    New ferure implemented: Finding bounding boxes while indexing slide.
    Bounding boxes defined by taking extreme coordinates among all control
    points from path. Such bounding box may be a bit larger than actual bounding
    box but it does't make significant difference.
    """
    
    def __init__(self):
        """
        Class constructor.

        Most important thing is constructuion of self.globaIndex dictionary.
        This distionary holds all information about single structures and it has
        following form:
        
            1. Keys are name of the structures,
            2. Eeach element is dictionary holding:
                - C{slides}: set of slides on which given structure appears,
                - C{attrubutes}: reversed: True|False, uid: Integer.
        """
        self.globaIndex={}        # Keys are structures names
        self.ids={}               # Name<->ID dictionary
        self.names={}             # ID<->name dictionary
        self.stereotaxic={}       # Indexing stereotaxic coordinate system 
        self.CurrentUID=100000    # Initial number for UID generation
        self.CurrentGID=200000    # Initial number for UID generation

    def _printRed(self, str):
        """
        @type  str: string
        @param str: String to print to stderr in red.
        @return   : Nothing, just prints the string.

        Prints given string to stderr using red color.
        """
        print >>sys.stderr, '\033[0;31m%s\033[m' % str

    def indexSingleSlide(self, pagenumber, svgdom):
        """
        @type  pagenumber: integer
        @param pagenumber: Number of atlas page
        @type  svgdom: DOM object
        @param svgdom: Whole SVG document which will be indexed,
        @return: Nothing.

        Appends one slide to atlasindex. Function assumes that labels are only decorations
        (they are not actually reruired to prepare index - only path elements are necessary).
        On other words - actual structure definitions are paths and their id's.
        """
        
        # Iterate over all path elements and index each structure
        # However, before actual indexing, short validation is performed - all propoerly defined
        # paths should have named according to some template. Chcecking, if the name is correct
        # is subject of validation.
        for structure in svgdom.getElementsByTagName('path'):
            self._validatePathElement(structure)
            self._indexSingleStructure(structure, pagenumber)

        # Extract information about stereotaxic coordinate system and bregma coordinate
        # and store it into self.stereotaxic data structure
        self.stereotaxic[pagenumber]=self._extractStereotaxicMatrix(pagenumber, svgdom)

    def _validatePathElement(self, PathElement):
        """
        @type  PathElement: DOM object
        @param PathElement: SVG path element to validate.
        @return: Nothing

        Checks if given element is proper SVG path element representing structure.
        Currently, the only criterion is ID(name??) of the element. Element has to be named
        accoting to some template.

        If invalid element is detected, script will print proper notification and then exit.
        No C{False} or C{True} bool values are returned. Just simple exit() command.
        Such behaviour was choosed in order to minimize posibility of error.
        """

        # Check if path elements are defined properly
        # (= structures are defined according to some template)
        # If not, print error notification and then exit
        try:
            if not str(PathElement.getAttribute('id').split('_')[0]).startswith('structure'):
                self._printRed("Error indexing structure. File is probably incorrectly defined.")
                sys.exit(2)
        except:
            pass

    def _indexSingleStructure(self, PathElement, pagenumber):
        """
        @type  pagenumber: integer
        @param pagenumber: Number of atlas page

        @type  PathElement: DOM object
        @param PathElement: SVG path element representing one structure.
                            Function assumes that all requred attrubutes are correctly defined.
        @return: Nothing

        Index single structure (path corresponding that sqtructure) into index.
        Function implements following worflow:

            1. Extract name of structure
            2. If structure was not indexed previously (i.e. on earlier slide), define
               empty data set for this structure.
            3. Mark that given structure exist on the slide
            4. Save attributes enumerated on C{AttributesList} list.
        """
        
        # Extract structure name from elemet's ID:
        structureName = PathElement.getAttribute('id' ).split('_')[-1]
        
        # If current structure was not indexed until now, perform some initial actions
        # which creates IDs and empty dictionaries for new structure:
        if (structureName not in self.ids) and (structureName not in self.globaIndex):
        
            # Generate new ID for current structure,
            # Create dataser for previously not indexed structure:
            # Distionary[StructureName]={slides: set, attributes:{}}
        
            self.CurrentUID+=1                                    # Generate new ID
            self.ids[structureName]=self.CurrentUID               # Create hash
            self.names[self.ids[structureName]]=\
                    self.ids[structureName]                       # Create reverse hash
        
            self.globaIndex[structureName]=\
                    {'slides': set(), 'attrubutes':{}}            # Create empty
                                                                  # data structure 
            self.globaIndex[structureName]['attrubutes']['uid']=\
                    self.CurrentUID                               # Assign UID 
                                                                  # to new structure
            #  Extract bounding box and store it in dictionary
            self.globaIndex[structureName]['attrubutes']['bbx']=\
                    extractBoundingBox(PathElement.getAttribute('d'))
        
        # If the dataset is already prepared do the following:
        # Append pagenumber
        self.globaIndex[structureName]['slides'].add(pagenumber)
        
        # Append attributes defined in att
        AttributesList=['reversed']
        for attribute in AttributesList:
            self.globaIndex[structureName]['attrubutes'][attribute]=PathElement.getAttribute(attribute)

        # There is a special attribute: bounding box is handled separately:
        # Merge existing bounding box with new one:
        currentBbx = self.globaIndex[structureName]['attrubutes']['bbx']
        newBbx = extractBoundingBox( PathElement.getAttribute('d'))

        self.globaIndex[structureName]['attrubutes']['bbx']=\
            mergeBoundingBox(currentBbx, newBbx)
        
    def _sortSlidesList(self):
        """
        Converts set of slides to list, then sorts the lists.
        Whole procedure is performed in order to save nice looking XML
        where slides numbers are presented in ascending order
        """
        for structureName in self.globaIndex.keys():
            self.globaIndex[structureName]['slides']=list(self.globaIndex[structureName]['slides'])
            self.globaIndex[structureName]['slides'].sort()

    def _printGlobalStructuresIndex(self):
        """
        @return: None
        
        Dumps raw index of structures.
        """
        print >>sys.stderr, self.globaIndex

    def _createIdElement(self, id):
        """
        @type  id: integer
        @param id: ID of basic structure
        @return: DOM element 

        Creates single entry representing one component (basic structure) of complex structure.
        """
        newIdElem = self.doc.createElement('struct')
        newIdElem.setAttribute('id', str(id))
        return newIdElem

    def _createStructureElement(self, StructureName):
        """
        @type  StructureName: string
        @param StructureName: Name of structure
        @return: (DOM object) Complete DOM for given structure.
        
        Creates DOM object for single structure:
        
            1. Creates proper DOM element
            2. Assigns attributes: name, uid, reversed
            3. Appends information on which slides given structure can be found.
        """
        # Create structure node
        newStructElem=self.doc.createElement('structure')

        # Define nice looking dictionary of attributes to set
        AttributesToSet={
                 'uid': str(self.globaIndex[StructureName]['attrubutes']['uid']),
            'reversed': str(self.globaIndex[StructureName]['attrubutes']['reversed']),
                 'bbx': ",".join(map(str,self.globaIndex[StructureName]['attrubutes']['bbx'])),
                'name': StructureName}

        # Assign attributes to created structure
        # using previously defined dictionary:
        for attribute in AttributesToSet.keys():
            newStructElem.setAttribute(attribute, AttributesToSet[attribute])

        # Create node which will handle slide numbers textnode
        newSlidesElement=self.doc.createElement('slides')

        # Create text node with space-separated list of slides on which given structure apperars.
        slicedList =\
                self.doc.createTextNode( " ".join(map(str, list(self.globaIndex[StructureName]['slides']))) )

        # Collect and append all nodes togeather    
        newSlidesElement.appendChild(slicedList)
        newStructElem.appendChild(newSlidesElement)
        
        # Return complete node 
        return newStructElem

    def _createAtlasPropertiesElement(self):
        """
        Creates atlas properties elemens holding all technical information about
        further processing of given dataset such as:
        CONF_TRACER_REFERENCE_WIDTH
        CONF_TRACER_REFERENCE_HEIGHT
        CONF_FILENAME_SAVE_TEMPLATES
        CONF_ALIGNER_REFERENCE_COORDS
        """
        DataToInsert =\
                [{'type':'ReferenceWidth',  'value':str(CONF_TRACER_REFERENCE_WIDTH)},
                 {'type':'ReferenceHeight', 'value':str(CONF_TRACER_REFERENCE_HEIGHT)},
                 {'type':'FilenameTemplate','value':str('%d_traced_v%d.svg')},
                 {'type':'RefCords','value':",".join(map(str,CONF_ALIGNER_REFERENCE_COORDS))},
                 {'type':'CAFSlideOrientation', 'value':'coronal'},
                 {'type':'CAFSlideUnits', 'value':'mm'},
                 {'type':'CAFName','value':CONF_PARSER_NAME[0]},
                 {'type':'CAFComment','value':' '.join(CONF_PARSER_COMMENT)},
                 {'type':'CAFCreator','value':' '.join(CONF_CONTACT_COMMENT)},
                 {'type':'CAFCreatorEmail','value':''.join(CONF_CONTACT_EMAIL)},
                 {'type':'CAFCompilationTime',\
                         'value':datetime.datetime.utcnow().strftime("%F %T")}]

        for entry in DataToInsert:
            newAtlasPropertiesElement = self.doc.createElement('property')
            newAtlasPropertiesElement.setAttribute('type',entry['type'])
            newAtlasPropertiesElement.setAttribute('value',entry['value'])
            yield newAtlasPropertiesElement 

    def _createDOMStructure(self):
        """
        @return: (DOM object) Initial frame of slideindex XML file

        Creates initial structure of slideindex XML file. The framework consist from
        two main elements:

            1. List of structures,
            2. Hierarchy of structures,
            3. List of slides with stereotaxic coordinate system information

        Of course, those elements are mutually connected. Each structure has assigned uniqe ID.
        Those ID are used later to define hierarchy of structures. 
        """

        self.doc = dom.Document()
        
        # Root element 'slideindex'
        slideindexRootElement=self.doc.createElement('slideindex')
        self.doc.appendChild(slideindexRootElement)

        # Atlas properties - holds all technical infortmation about data
        # processing as well as metadata (in future)
        propertiesRootElement=self.doc.createElement('atlasproperties')
        slideindexRootElement.appendChild(propertiesRootElement)

        # Index of all slides - hold information about basic slide information:
        # slideNumber, bregma coordinate, stereotaxic coordiante system matrix
        slidesRoot=self.doc.createElement('slidedetails')
        slideindexRootElement.appendChild(slidesRoot)

        # Index of all structures with numbers of slides on which they appear.
        structuresRoot=self.doc.createElement('structureslist')
        slideindexRootElement.appendChild(structuresRoot)
    
        # Hierarchy of structures for further usage
        hierarchyRootElem=self.doc.createElement('hierarchy')
        slideindexRootElement.appendChild(hierarchyRootElem)
        
        return (propertiesRootElement, structuresRoot, hierarchyRootElem, slidesRoot)

    def _getGID(self):
        """
        @return: (string) Uniqe group ID
        Returns GroupUniqeIdentifier (GID) as string.
        """

        self.CurrentGID+=1
        return str(self.CurrentGID)

    def _defineSingleHierarhyElem(self, groupName):
        """
        @type  groupName: string
        @param groupName: Name of structures group that woluld be created
        @return: (DOM element) Group element with elementary structures IDs as a child elements.

        Generates hierarchy of structures for given root node. In order to
        define full hierarchy function has to be invoked with 'Brain' agrument.
        Please note that GID numbers are not connected with names of the groups
        so 'Brain' group does not necesairly has to have GID=200001.

        Description of GROUP element (group elements tag)L.....

        @note: this function is ivnoked recursively.
        """

        # Create new group element, then assign GID and name of the group
        newHierarchyElem=self.doc.createElement('group')
        newHierarchyElem.setAttribute('name', groupName)
        newHierarchyElem.setAttribute('id', self._getGID() )

        try:
            newHierarchyElem.setAttribute('fullname', self.fullNameDictionary[groupName.strip()])
        except:
            newHierarchyElem.setAttribute('fullname', groupName.strip())
        
        if self.globaIndex.has_key(groupName):
            newHierarchyElem.setAttribute('fill',"#"+ self.globaIndex[groupName]['attrubutes']['fill'] )
        else:
            newHierarchyElem.setAttribute('fill',"#777777")

        # Try to extract UID for structure which has the same name as
        # groupName. If such structure exists, it will be part of the hierarchy.
        try:
            # uid is defined just for clear look (extract UID from strucutres
            # index
            uid = str(self.globaIndex[groupName]['attrubutes']['uid'])
            newHierarchyElem.setAttribute('uid', uid )
        except KeyError:
            self._printRed("Structure %s not found while generating hierarchy" % (groupName))

        if self.structuresTree.has_key(groupName):
            componentsList=self.structuresTree[groupName]
        else:
            componentsList=[]

        for structureName in componentsList:
            newHierarchyElem.appendChild(self._defineSingleHierarhyElem(structureName))
            # Excetion below handles event when a passed structure name
            # does not exist in structures list
            # In such case, just print the notification and pass
        
        return newHierarchyElem

    def generateDummyHerarchy(self):
        """
        Generates flat hierarchy where all structures are childs of root structure (Brain).
        
        @return: Dictionary with flat structure's hierarchy {'structure name':'Brain'}
        """
        
        rootStructureName='Brain'
        retDictionary={}
        
        for structureName in self.globaIndex.keys():
            retDictionary[structureName]=rootStructureName

        return retDictionary

    def getFullnamesFromFile(self, fullnamesFile):
        """
        Assigns full names to hierarchy group elements
        """
        self.fullNameDictionary ={}
        sourceFile = open(fullnamesFile)

        for sourceLine in sourceFile:
            if strip(sourceLine).startswith('#') or strip(sourceLine) == "":
                continue
            else:
                line = split(strip(split(sourceLine,"#")[0]),'\t')
                # Validate line 
                if len(line) != 3:
                    self._printRed("Wrong number of fields. Skipping line...")
                    continue

                abbrev = line[0]
                fullname =line[1]
                color = line[2]
                # Check, if there is only one child -> parent definition for
                # each child.
                if self.fullNameDictionary.has_key(abbrev):
                    self._printRed("Fullname for structure %s defined more than once. Skipping..."% abbrev)
                    continue
                else:
                    self.fullNameDictionary[abbrev] = fullname
                    if self.globaIndex.has_key(abbrev):
                        self.globaIndex[abbrev]['attrubutes']['fill'] = color

        sourceFile.close()

    def createHierarchyFromFile(self, hierarchyFilename):
        """
        Function manages creating hierarhy basing on file describing mutual
        relation between structures:

            1. Parrent - child relations are read from given file.
            2. Actual hierarchy is created using  L{devCreateHierarchyList<devCreateHierarchyList>}
               function

        @type  hierarchyFilename: string
        @param hierarchyFilename: path to file containing hierarchy.

        @return: None
        """

        # Initialize child -> parent dictionary
        cpDictionary = {}

        # Open given file and read every line that doesn't have # as initial
        # character.
        sourceFile = open(hierarchyFilename)

        for sourceLine in sourceFile:
            if strip(sourceLine).startswith('#') or strip(sourceLine) == "":
                continue
            else:
                line = split(strip(split(sourceLine,"#")[0]),'\t')
                
                # Validate line 
                if len(line) != 2:
                    #self._printRed("Wrong number of fields. Skipping line...")
                    continue

                child = line[0]
                parent =line[1]
                # Check, if there is only one child -> parent definition for
                # each child.
                if cpDictionary.has_key(child):
                    self._printRed("Parent for structure %s defined more than  once. Skipping..."% child)
                    continue
                else:
                    cpDictionary[child] = parent

        sourceFile.close()

        # After loading all entries, build herarchy
        self.devCreateHierarchyList(cpDictionary)

    def devCreateHierarchyList(self, structureHierarchy):
        """
        @type  structureHierarchy: dictionary
        @param structureHierarchy: Dictionaty containing structures hierarchy in
                                   in format desctibed below.
        @return: None, only C{self.structuresTree} is generated.
        
        Method generates hierarchy od structures for given atlas basing on
        provided dictionary. Form of the dictionary has to be following: keys
        are name of child structures and elements are names of parent's. Eg.:
        {'Ctx':'brain'} means that group Ctx is memeber of brain group.
        
        Generated dictionary C{self.structuresTree} has following form: keys are
        names of groups while elements are lists of given group offspring. If
        element has no childrens, empty list has to be provided. Eg.:
        {'brain':['s1','s2'], 's1':['s3'], 's2':[]} means that brain has two
        substructures (s1 and s2), s1 has single substructure (s3) while s2 has no
        substructures.
        
        Short description of differences between naming of gruops and single
        structures: Structures and groups can have the same names and they can
        be distinguished by assigned number UID UniqeID for sigle structures and GID
        GroupIdentifier for groups. UID starts from 100000 while GID - from 200000. 
        
        Group contains from elements which have representation in signle
        structures or not. Also topmost element can have representation or not.
        For example in some atlases whole brain area can be defined a a single structure
        while in other atlases whole brain area is defined by joining all substructures
        togeather. This situation has following reflection in hierarhy: When
        brain contour is defined, 'Brain' group element has defined representation,
        otherwise has no representation. Regardless of that final structure is
        generated using by joining all substructures.
        """
        # Define empty structure hierarchy tree:
        self.structuresTree={}

        # And fill it with elements:

        # Take each element in dictionary, extract parent's name and list of
        # childrens. If self.structuresTree has no parent element, create one,
        # otherwise append child to parrent's element.
        for child in structureHierarchy.keys():
            # Extract parrent's name
            parent = structureHierarchy[child]
            
            # If list of parent childs is not initialized do so:
            if not self.structuresTree.has_key(parent):
                self.structuresTree[parent]=[]
            
            # Append child
            self.structuresTree[parent].append(child)
        
    def _printHierarchyTree(self, s, depth = 0):
        """
        @type  s: string
        @param s: Name of the topmost structure for which tree will be genereate
        
        @type  depth: integer
        @param depth: level of nesting - margin for printing.
        
        @return: (string) String containing tree representation of hierarchy.
        
        Prints tree representation of defined structure. Function starts from
        the topmost element and is invoked recursively for each child element.
        """
        if self.structuresTree.has_key(s):
            tree=self.structuresTree[s]
        else:
            tree=None
        
        if tree == None or len(tree) == 0:
            pass
        else:
            for val in tree:
                print >>sys.stderr, "|"+" |---" * depth, val
                self._printHierarchyTree(val, depth+1)
    
    def _extractStereotaxicMatrix(self, pagenumber, svgdom):
        """
        @type  pagenumber: integer
        @param pagenumber: Number of atlas page
        @type  svgdom: DOM object
        @param svgdom: Whole SVG document which will be indexed,
        @return: (tuple) bregma coordinate and stereotaxic coordinate system matrix
        
        Extract bregma coordinate and and stereotaxoc coordinate matrix from single slide.
        """
        for element in svgdom.getElementsByTagName('bar:data'):
            if element.getAttribute('name') == 'transformationmatrix':
                transfArr = element.getAttribute('content')
            if element.getAttribute('name') == 'coronalcoord':
                bregma = element.getAttribute('content').strip()
        return (bregma, transfArr)
    
    def _appSingleSliedeStereotaxicMatrix(self, pagenumber):
        """
        @type  pagenumber: integer
        @param pagenumber: Atlas page number
        @return: (DOM object) DOM element holding extracted information.

        Createdreates XML element holding information about one slide.
        Holds information about:
        
            1. Slide number,
            2. Stereotaxic coordinate system transformation matrix,
            3. Bregma coordinate.
        """
        # Get cached stereotaxic information for given slide
        (bregma, transfArr)=self.stereotaxic[pagenumber]

        # Put extracted information into XML structure
        newSlideElem=self.doc.createElement('slide')
        newSlideElem.setAttribute('slidenumber', str(pagenumber) )
        newSlideElem.setAttribute('transformationmatrix', transfArr )
        newSlideElem.setAttribute('coronalcoord', str(bregma) )
        return newSlideElem

    def saveIndexAsXML(self, IndexFilename, RootElementName = 'Brain'):
        """
        @type  IndexFilename: string
        @param IndexFilename: path to XML index filename
        
        @type  RootElementName: string
        @param RootElementName: Name of the structure which is placed at the top
                                of structure's hierarchy.
        
        Generates and saves XML representation of slide index info C{IndexFilename} file.
        Workflow:
        
            1. Sort lists of slides,
            2. Create DOM backbone,
            3. Append each indexed structure into DOM structure,
            4. Define some herarhy,
            5. Dump DOM into file.
        """
        self._sortSlidesList()
        (propertiesRootElement, structuresRoot, hierarchyRootElem, slidesRootElem) = self._createDOMStructure()

        # Fill atlas properties element with data:
        for entry in self._createAtlasPropertiesElement():
            propertiesRootElement.appendChild(entry)
        
        # Putting information about all structures into XML structure
        for structure in self.globaIndex.keys():
            structuresRoot.appendChild(self._createStructureElement(structure))
        
        # Putting information about transformation to stereotaxic coordiante system
        # for each slide
        for slideNumber in self.stereotaxic.keys():
            slidesRootElem.appendChild(self._appSingleSliedeStereotaxicMatrix(slideNumber))
        
        # Creating Structure hierarchy
        hierarchyRootElem.appendChild(\
                self._defineSingleHierarhyElem( RootElementName ))
        
        f=open(IndexFilename,'w')
        self.doc.writexml(f,\
                indent="\t", addindent="\t", newl="\n",\
                encoding='utf-8')
        f.close()

if __name__=='__main__':
    pass
