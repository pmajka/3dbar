import os, sys, csv
import xml.dom.minidom as dom
from string import *
import json
import urllib2
import numpy as np
import nifti
import uuid
import zipfile
import datetime, logging
import shutil

from bar.color import barColor
from barAllenApiAtlasSpace import barAllenApiAtlasSpace
from barAllenApiAtlas import barAllenApiAtlas

BAR_CONF_ALLEN_API_ATLASES_INDEX = 'http://www.brain-map.org/BrainExplorer2/atlases.xml'
BAR_CONF_ALLEN_API_ATLAS_INFO = 'Info.xml'
BAR_CONF_ALLEN_API_ATLAS_ANNOTATION = 'Annotation'
BAR_CONF_ALLEN_API_ATLAS_ONTOLOGY = 'ontology.csv'
BAR_CONF_ALLEN_API_HIERARCHY_FILANEME = 'parents.txt'
BAR_CONF_ALLEN_API_SPACES_DIRNAME = 'Spaces'
BAR_CONF_ALLEN_API_MAPPING_FILENAME   = 'mappings.txt'

BAR_CONF_ALLEN_API_VOL_RES_MULTIPLIER = 0.001

# Intialize the logging module.
logging.basicConfig(\
        level=getattr(logging, 'DEBUG'),
        format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
        datefmt='%m/%d/%Y %H:%M:%S')

def cleanStructName(structName):
    """
    Provided acronyms are usually fine but sometimes they are not compatibile
    with 3dBar naming convention. Here we process them so they can pass 3dBAR
    name validataion.

    @type  structName: C{str}
    @param structName: initial sturcture name, potentially invalid

    @rtype: C{str}
    @return: structure name transformed in the way that passes 3dBAR name validation

    @todo: this function should be a part of the base.py module
    """
    # transform name into its valid form by replacing '(',')', '$', '/',
    # "'", '+', ' ' characters with their names and stripping hypens
    # from beginning and end of the string
    replaceMap = [('(', 'OpParen'),
                  (')', 'ClParen'),
                  (',', '-'),
                  ('$', 'Dollar'),
                  ('/', 'Slash'),
                  ('\\', 'Backslash'),
                  ('+', 'Plus'),
                  (' ', '-'),
                  ('\'', 'Prime')]

    return reduce(lambda x, (y, z): x.replace(y, z),
                  replaceMap,
                  structName).strip('- ')

class barAllenApiAtlasPreprocessor:
    """Class barAllenApiAtlasPreprocessor

    Purpose of the script below is to prepare input data for the Allen Brain Atlas
    2011 volumetric dataset. Two partial datasets are processed.  The first one is
    the labelled volume containing volume element to structure's name assignment. This
    volume is provided by Allen Institute in form of raw binary file and one needs
    to figure out what are the voxel dimensions and volume origin.  Volume is
    processed by L{preprocessVolume} function.
    """

    def __init__(self, outputDirectory = None):
        """
        @type  outputDirectory: str
        @param outputDirectory: Working directory for the atals preprocessor.
        Usually this directory should be 'src' directory of a given atlas. For
        tesing purposes it may be changed. Default working directory is the
        current working dir.

        """
        # Load available atlases
        self.availableAtlases = self._updateAvailableAtlases()

        # Set initial values of current atlas id and current space name to null
        self.currentAtlasId = None
        self.currentSpaceName = None

        # Handle undefined output directory name.
        if outputDirectory == None:
            outputDirectory = '.'
        self.outputDirectory = outputDirectory

        # Just be sure that output directory axists:
        if not os.path.exists(self.outputDirectory):
            logging.debug('Creating output directory: %s', self.outputDirectory)
            os.makedirs(self.outputDirectory)

        logging.debug('Setting output directory: %s', self.outputDirectory)

    def _updateAvailableAtlases(self):
        """
        This method downloads and parses summary of atlases available trought
        Allen Brain Institute API.

        @rtype: {str : barAllenApiAtlas, ... }
        @return: A dictionary mapping id of a given atlas to the atlas object.
        """

        # Connect to Allen Institute Website and download xml file containing
        # list of available atlases
        logging.info('Fetching file: %s', BAR_CONF_ALLEN_API_ATLASES_INDEX)
        urlRequest  = urllib2.Request(BAR_CONF_ALLEN_API_ATLASES_INDEX)
        urlResponse = urllib2.urlopen(urlRequest).read()
        logging.info('Done.')

        # Parse retrieved xml document
        allenAtlasesDom = dom.parseString(urlResponse)

        # Process entries from xml file and parse each entry
        # as a result you sould get a dictionary atlas_id => atlas_object
        # which is a result of this method
        atlasElements = allenAtlasesDom.getElementsByTagName('atlas')
        logging.info('%d Atlases found in the index file. Loading details...',
                len(atlasElements))

        # Iterate over all atlases and load atlas details.
        availableAtlases \
                = map(lambda x: barAllenApiAtlas.fromXML(x), atlasElements)
        availAtlasDict = dict(map(lambda x: (x.id, x), availableAtlases))

        return availAtlasDict

    def _downloadAtlas(self):
        """
        Download source data for currently processed atlas.

        @rtype: None
        @return: None
        """

        # 1) Get id and name of currently processed atlas.
        # 2) Define url where source data can be found
        # 3) Define location where downloaded data will be stored
        #    before extraction
        atlasId = self.currentAtlasId
        atlasName = self.availableAtlases[atlasId].name
        sourceDataUrl = self.availableAtlases[atlasId].url
        outputFilename = self._getSourceDatasetZipfileName()

        logging.info('Downloading data for atlas %s (%s).', atlasId, atlasName)
        logging.info('Fetching file: %s', sourceDataUrl)
        logging.info('Data will be saved to: %s', outputFilename)

        # Fetch the source dataset from Allen Institute's website
        # and write to disk
        logging.debug('Starting downloading...')

        remoteContent = urllib2.urlopen(sourceDataUrl)
        logging.debug('Done. Writing data to %s.', outputFilename)
        open(outputFilename, "wb").write(remoteContent.read())

        # Open the downloaded package and extract its contents.
        localZipfile = zipfile.ZipFile(outputFilename)
        outputZipDirectory = self._getZipOutputZipfilename()
        logging.info('Extracting contents to %s.', outputZipDirectory)
        localZipfile.extractall(path = outputZipDirectory)

    def _loadAtlasSpaces(self):
        """
        Extract all available atlas spaces from the atlas.

        @type: None
        @return: None
        """
        # Get identifier and name of currently processed atlas.
        atlasId = self.currentAtlasId
        atlasName = self.availableAtlases[atlasId].name

        logging.debug('Loading available atlas spaces for atlas id %d (%s)', atlasId, atlasName)

        # Load atlas info file. This file contains metadata about the atlas. In
        # particualr information about available atlas spaces. Parse the file
        # into XML DOM onject.
        infoFilePath = self._getInfoFilename()
        logging.info('Loading and parsing atlas XML info file: %s.', infoFilePath)
        infoFileDom = dom.parse(infoFilePath)

        # Iterate over all 'space' elements and create 'barAllenApiAtlasSpace'
        # for each element found.
        availableSpaces = infoFileDom.getElementsByTagName('space')
        for i, spaceElem in enumerate(availableSpaces):
            logging.debug('Loading atlas space data for space %d of %d', i+1, len(availableSpaces))

            newSpace = barAllenApiAtlasSpace.fromXML(spaceElem)
            newSpace.sourceXmlFilename = infoFilePath
            self.availableAtlases[atlasId].spaces[newSpace.name] = newSpace
            logging.debug('Data for space %s loaded.' % newSpace.name)

    def processAtlas(self, atlasId, spaceName, fetchSourceData = True):
        """
        @type  atlasId: str or int
        @param atlasId: Identifier of the atlas according to Allen Brain
                        Institute identifiers of atlases :)

        @type  spaceName: str
        @param spaceName: Name of atlas space from given atlas. Atlas space is
        kind of subatlas - a sigle atlas can have multiple spaces ie. taken in
        different time points ot for different specimens, etc. By this parameter
        you define a particular atlas space to process. The atlas space name has
        to be known in advance.

        @type  fetchSourceData: Bool
        @param fetchSourceData: Force source data downloading. True by default.
        Use when you want to download and extract the source data. Set to
        C{False} when you already have the source data and there is no need to
        download it again.

        @rtype: None
        @return: None

        Fundamental function of the whole class :) Function performs all steps of
        processing: 3) Downloading and extracting package with the atlas. 2) Reading
        information about atlas spaces available in given atlas. 4) Processing
        ontology from given atlas to form acceptable by 3dBAR's parsers. 5)
        Processing other mappings (as hierarchy or color mappings) to form
        acceptable by 3dBAR's parser.
        """

        logging.debug('processAtlas: Init: atlas id: %s', str(atlasId))
        logging.debug('processAtlas: Init: space name: %s', str(spaceName))
        logging.debug('processAtlas: Init: fetching source: %s', str(fetchSourceData))

        self.currentAtlasId = str(atlasId)

        if fetchSourceData == True:
            logging.info('Fetching source data.')
            self._downloadAtlas()

        logging.debug('processAtlas: Loading atlas spaces...')
        self._loadAtlasSpaces()

        logging.debug('processAtlas: Processing ontology...')
        self._processOntology()

        logging.debug('processAtlas: Setting atlas space...', )
        self._setCurrentAtlasSpace(spaceName)

    def _setCurrentAtlasSpace(self, spaceName):
        """
        @type  spaceName: str
        @param spaceName: Atlas Space identifier. Determines subpart of atlas
                          for which volume is defined.

        @trype: None
        @return: None

        Fix atlas space identifier so it can be used in further calculations.
        Method used internally. Better noy use it for your own.
        """

        self.currentSpaceName = spaceName
        self.currentSpace = \
                self.availableAtlases[self.currentAtlasId].spaces[spaceName]

    def _getSourceDatasetZipfileName(self):
        filename = \
                os.path.join(self.outputDirectory, \
                             self.currentAtlasId + '.zip')
        return filename

    def _getZipOutputZipfilename(self):
        filename = \
                os.path.join(self.outputDirectory, \
                             self.currentAtlasId)
        return filename

    def _getAnnotationsFilename(self):
        filename = \
                os.path.join(self.outputDirectory, \
                             self.currentAtlasId, \
                             BAR_CONF_ALLEN_API_SPACES_DIRNAME, \
                             self.currentSpaceName, \
                             BAR_CONF_ALLEN_API_ATLAS_ANNOTATION)
        return filename

    def _getInfoFilename(self):
        filename = \
                os.path.join(self.outputDirectory, \
                             self.currentAtlasId, \
                             BAR_CONF_ALLEN_API_ATLAS_INFO)
        return filename

    def _getOntologyFilename(self):
        filename = \
                os.path.join(self.outputDirectory, \
                             self.currentAtlasId, \
                             BAR_CONF_ALLEN_API_ATLAS_ONTOLOGY)
        return filename

    def _getOutputLabeledVolumeFilename(self):
        """
        Generate filename for NIfTII volume generated from raw annotation
        volume.

        @rtype: str
        @return: name of the output NiFTII volume
        """
        id = self.currentAtlasId
        space = self.currentSpace.name

        filename = \
                os.path.join(self.outputDirectory,
                             'labeled_volume_%s_%s.nii.gz' % (id, space))
        return filename

    def _getHierarchyFilename(self):
        filename = \
                os.path.join(self.outputDirectory,
                             BAR_CONF_ALLEN_API_HIERARCHY_FILANEME)
        return filename

    def _getMappingsFilename(self):
        filename = \
                os.path.join(self.outputDirectory,
                             BAR_CONF_ALLEN_API_MAPPING_FILENAME)
        return filename

    def processVolume(self, applyPermutation = (0,1,2), reverseAxes = (False, False, False), \
            dataType = np.uint16, reshapePermutation = (0, 1, 2), headerUpdate = {}, qfac = 1):
        """
        @type  applyPermutation: (int, int, int)
        @param applyPermutation: Permutation of the axis' order. Use to adjust
                                 image orientation. When the volume doesn't look
                                 like a correct volume (I'll notice that).

        @type  reverseAxes: (Bool, Bool, Bool)
        @param reverseAxes: Directives for reversing particular axis of the
                            volume. Use to change orientation within given axis
                            (iie. to change left to right side)

        @type  dataType: NumPy array type
        @param dataType: Data type to which values from initial volume will be
                         converted. This is a very important parameter. Be
                         carefull about that.

        @type  reshapePermutation: (int, int, int)
        @param reshapePermutation: Permutation of the axis' order. Use to adjust
                                   image orientation

        @type  headerUpdate: dict
        @param headerUpdate: Custom header values that will be assigned to the
                           header. Use this dictionary to override default NiFTI
                           header fields.

        @type  qfac: -1 or 1
        @param qfac: Additional parameter for manipulating image orientation.
                     See NiFTIi specification for details

        Function for processing raw anntotation volume (raw labelled volume)
        into niftii file that can be parsed in the further steps of processing.
        The exac way in which the raw volume will be processed by applying
        permutations, selecting particular data type or overriding default
        niftii header entries.

        @type: None
        @return: None
        """
        logging.debug('processVolume: dataType: %s', str(dataType))
        logging.debug('processVolume: reshapePermutation: %s', str(reshapePermutation))
        logging.debug('processVolume: applyPermutation: %s', str(applyPermutation))
        logging.debug('processVolume: reverseAxes: %s', str(reverseAxes))
        logging.debug('processVolume: headerUpdate: %s', str(headerUpdate))
        logging.debug('processVolume: qfac: %s', str(qfac))

        logging.debug('Loading source data...')
        read_data = self._loadRawAnnotationFile(dataType, reshapePermutation)
        read_data = np.transpose(read_data, applyPermutation)

        logging.debug('Reversing arrays...')
        # Reverse array data if requested
        if reverseAxes[0]: read_data = read_data[::-1,:,:]
        if reverseAxes[1]: read_data = read_data[:,::-1,:]
        if reverseAxes[2]: read_data = read_data[:,:,::-1]

        logging.debug('Creating niftii file...')
        # Prepare nifti volume from numpy array. Create proper header and store all
        # of them into target volume file.
        annotatedVolume = nifti.NiftiImage(read_data)
        self._assignHeaderInformation(annotatedVolume,
                                      applyPermutation = applyPermutation,
                                      reshapePermutation = reshapePermutation,
                                      headerDict = headerUpdate,
                                      qfac = qfac)

        outputPath = self._getOutputLabeledVolumeFilename()
        annotatedVolume.save(outputPath)

    def _loadRawAnnotationFile(self, dataType = np.uint16, reshapePermutation =  (0, 1, 2)):
        """
        @type  dataType: NumPy array type
        @param dataType: Data type to which values from initial volume will be
                         converted. This is a very important parameter. Be
                         carefull about that.

        @type  reshapePermutation: (int, int, int)
        @param reshapePermutation: Permutation of the axis' order. Use to adjust
                                   image orientation

        @rtype: numpy volume
        @return: NumPy volume created ba parsing raw annotation file.
        """
        annotationVolumeFilename = self._getAnnotationsFilename()
        logging.debug('Loading raw volume from %s.' % annotationVolumeFilename)

        # Load labelled volume from the raw binary file using numpy. The values are
        # stored as unsigned short integers one after another. After loading all
        # values, resulting array is reshaped to match the atlas volume shape.
        volumeDimensions = \
                map(lambda x: self.currentSpace.tissueVolumeSize[x], reshapePermutation)
        logging.debug('Using data type: %s.' % str(dataType))
        logging.debug('Reshaping volume to %s voxels' % str(volumeDimensions))

        fd = open(annotationVolumeFilename, 'rb')
        read_data = np.fromfile(file=fd, dtype = dataType).reshape(volumeDimensions)

        logging.debug('Done. Returning.')

        return read_data

    def _assignHeaderInformation(self, niftiImage, applyPermutation = (0, 1, 2),
                                       reshapePermutation = (0, 1, 2),
                                       headerDict = {}, qfac = 1):
        """
        @type  niftiImage: NiftiImage
        @param niftiImage: Image for which header information will be assigned

        @type  applyPermutation: (int, int, int)
        @param applyPermutation: Axis permitation with regard to default axes
                                 order. Parameter used to compute final order of
                                 axes and corresponding origin and pixel
                                 dimensions.

        @type  reshapePermutation: (int, int, int)
        @param reshapePermutation: Permutation applied to the raw binary data,
                                   just afte rreshaping. Parameter used to
                                   compute final order of axes and corresponding
                                   origin and pixel dimensions.

        @type  headerDict: dict
        @param headerDict: Custom header values that will be assigned to the
                           header.

        @type  qfac: -1 or 1
        @param qfac: Additional parameter for manipulating image orientation.
                     See NiFTIi specification for details

        @rtype: None
        @return: None

        """

        # Compute voxel spacing for the volume. In order to compute the spacing,
        # the initial spacing has to be permuted and scaled by a predefined
        # multiplier
        volumeSpacing = map(lambda x: \
                BAR_CONF_ALLEN_API_VOL_RES_MULTIPLIER * x,
                self.currentSpace.tissueVolumePixelSpacing)
        volumeSpacing = map(lambda x: volumeSpacing[x], applyPermutation)
        logging.debug('Computed voxel size: %s.' % str(volumeSpacing))

        # Compute origin of the volume. Order of values is determined by two
        # opermutations: used for raw volume and the second permutation used to
        # adjust the volume for the second time.
        volumeOrigin = self.currentSpace.tissueVolumeOrigin
        volumeOrigin = map(lambda x: volumeOrigin[x], reshapePermutation)
        volumeOrigin = map(lambda x: volumeOrigin[x], applyPermutation)
        volumeOrigin = map(lambda x: volumeOrigin[x] * volumeSpacing[x], range(3))
        logging.debug('Computed volume origin: %s.' % str(volumeOrigin))

        # Set volume header. Use custom header dictionary if provided. Apply
        # image spacing and volume origin. Apply orientation information (qfac)
        logging.debug('Setting header.')
        niftiImage.setVoxDims(volumeSpacing)
        niftiImageHeader = niftiImage.header
        niftiImageHeader['qoffset'] = volumeOrigin
        niftiImageHeader['pixdim'][0] = qfac
        niftiImageHeader.update(headerDict)
        niftiImage.header = niftiImageHeader

        logging.info('Assigning following header to the niftii volume: %s', str(niftiImage.header))

    def _processOntology(self):
        """
        Extract and process structure ontology information from source dataset.

        Ontology file contains a number of lines. Each of the line consists of:
            1) Structure's abbreviated name
            2) Strucutre's parent abbreviated name
            3) Full name of the structure
            4) Ontlogy id (I don't know where the full ontology is provided)
            5) Structure's index as provided in the labelled volume
            6) RGB color arrigned to the particular structure (note the colour may be no uniqe)

        @return: None
        """

        # String that will hold contents of the ontology file.
        ontologyString = ""

        # String that will hold contents of the structure's hierarchy file.
        parentsString = ""

        # Load the ontology file using csv reader.
        ontologyFilename = self._getOntologyFilename()
        logging.debug('Loading and parsing ontology filename: %s.' % ontologyFilename)
        csvReader = csv.reader(open(ontologyFilename, 'r'), delimiter=',', quotechar='"')

        # Read line by line from ontology file and extract information about
        # the structures.
        for ontologyLine in csvReader:
            toOntStringData, toParentsData =\
                hstr, ontstr = self._processSingleOntologyFileLine(ontologyLine)
            ontologyString += hstr
            parentsString  += ontstr

        # Create files with processed ontology data as well as hierarchy data.
        logging.debug('Saving color and fullname mapping (filenames not presented)')
        open(self._getHierarchyFilename(), 'w').write(parentsString)
        open(self._getMappingsFilename(), 'w').write(ontologyString)

    def _processSingleOntologyFileLine(self, ontologyLine):
        """
        Helper function for processing sungle ontology file line. A single line with
        ontology records contains following elements:
            - Fullname, abbreviation, parent, assigned color, volume index,
              ontologyID

        @type  ontologyLine: str
        @param ontologyLine: tab separatd line containing data with single ontology
                             record.

        @rtype: (str, str)
        @return: Strings that could be appended to ontology and hierarchy string.
        """

        logging.debug('Processing ontology line: %s', ontologyLine)

        # Extract data from provided string.
        abbreviation = cleanStructName(ontologyLine[1])
        parent = cleanStructName(ontologyLine[2])
        fullname = ontologyLine[0]
        ontologyId = ontologyLine[7]
        structureIdx = ontologyLine[6]

        # Convert color components into html color string.
        rgbTuple = tuple(map(lambda x: int(ontologyLine[x]), [3,4,5]))
        htmlColour = barColor.fromInt(rgbTuple).html[1:]
        toOntStringData = [abbreviation, fullname, htmlColour, ontologyId, structureIdx]
        toParentsData = [abbreviation, parent]

        # From final string that will be returned.
        toOntStringData = "\t".join(map(str, toOntStringData)) + "\n"
        if parent == "":
            toParentsData=""
        else:
            toParentsData = "\t".join(map(str, toParentsData)) + "\n"

        return toOntStringData, toParentsData

    def cleanup(self):
        """
        Remove atals package and extracted files of currently processed atlas.
        This functions is not executed automatically and has to be invoked
        manually.
        """
        logging.info('Performing cleanup...')

        extractedDir = self._getZipOutputZipfilename()
        zipFilename  = self._getSourceDatasetZipfileName()

        logging.debug('Removing source dataset: %s.', zipFilename)
        shutil.rmtree(zipFilename)

        logging.debug('Removing extracted source dataset: %s.', extractedDir)
        shutil.rmtree(extractedDir)


if __name__ == '__main__':
    pass
