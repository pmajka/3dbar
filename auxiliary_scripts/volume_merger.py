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

import vtk
import sys
import os
import random 

from optparse import OptionParser,OptionGroup
from bar import barIndexer
from bar.rec.barreconstructor import barReconstructionModule
from bin.reconstructor.batchreconstructor import barBatchReconstructor

random.seed(0)
VOLUME_FILENAME_TEMPLATE = "volume_%s.vtk"

def printRed(str):
    """
    @type  str: string
    @param str: String to print to stderr in red.
    @return   : Nothing, just prints the string.
    
    Prints given string to stderr using red color.
    """
    print >>sys.stderr, '\033[0;31m%s\033[m' % str

def rgb(hexVal):
    """
    Converts html hexidecimal color value into RGB color components tuple.
    
    @type  hexVal: C{str}
    @param hexVal: html hexicedimal color string.
    
    @rtype: C{(int,int,int)}
    @return: RGB color components tuple.
    """
    n = eval('0x' + hexVal[1:])
    return (n>>16)&0xff, (n>>8)&0xff, n&0xff

def getImageMask(inputVtkImageData):
    """
    @type  inputVtkImageData: C{vtkImageData}
    @param inputVtkImageData: Image data to be normalized
    
    @rtype: C{vtkImageData}
    @return: Normalized (0-1) image data
    """
    norm = vtk.vtkImageNormalize()
    norm.SetInput(inputVtkImageData)
    norm.Update()
    return norm.GetOutput()

def getIndexedImageData(inputVtkImageData, indexVal):
    """
    @type  inputVtkImageData: C{vtkImageData}
    @param inputVtkImageData: Image data to be processed
    
    @type  indexVal: C{unsigned int}
    @param indexVal: Index value that will be assigned to all non-zero values.
    
    Function replaces all non-zero valued pixels of provided
    C{inputVtkImageData} with C{indexVal} and returns the result.
    
    @rtype: C{vtkImageData}
    @return: UnsignedInt vtkImageData with two values 0 and provided
             C{indexVal}.
    """
    # Convert normalized input image to unsigned int scalars
    cast = vtk.vtkImageCast()
    cast.SetInput(getImageMask(inputVtkImageData))
    cast.SetOutputScalarTypeToUnsignedInt()
    
    # Then multiply the normalized image data by priovided constant
    multip = vtk.vtkImageMathematics()
    multip.SetOperationToMultiplyByK()
    multip.SetConstantK(indexVal)
    multip.SetInput(cast.GetOutput())
    return multip.GetOutput()


class mergerStructPtsReader(vtk.vtkStructuredPointsReader):
    """
    Simple interface to the C{vtkStructuredPointsReader}. Reads data from
    provided file.
    """
    def __init__(self, filename):
        """
        @type  filename: C{str}
        @param filename: Filename to be read
        """
        self.SetFileName(filename)
        self.Update()


class mergerWriter(vtk.vtkStructuredPointsWriter):
    """
    Simple interface to the C{vtkStructuredPointsWriter}. Writes provided input
    data to the file.
    """
    def __init__(self, inputVtkImageData, filename):
        """
        @type  inputVtkImageData: C{vtkImageData}
        @param inputVtkImageData: Image data to be normalized
        
        @type  filename: C{str}
        @param filename: filename to which given input data will be written
        """
        self.SetInput(inputVtkImageData)
        self.SetFileName(filename)
        self.SetFileTypeToBinary()
        self.Update()


class normImageByUid():
    """
    Class providing basic operations on loaded volume like masking, normalizing 
    or assigning indexes.
    """
    def __init__(self, inputVtkImageData):
        """
        @type  inputVtkImageData: C{vtkImageData}
        @param inputVtkImageData: Image data to be processed
        """
        self._imageData = inputVtkImageData
    
    @classmethod
    def fromFile(cls, filename):
        """
        @type  filename: C{str}
        @param filename: file to load image from
        
        Loads volume from file.
        """
        reader = mergerStructPtsReader(filename)
        return cls(reader.GetOutput())
    
    def GetMask(self):
        """
        Alias to L{getImageMask}.
        """
        return getImageMask(self._imageData)
    
    def GetOutput(self):
        """
        Returns 
        """
        return self._imageData
    
    def GetIndexed(self, indexVal):
        """
        Alias to L{getIndexedImageData}.
        """
        return getIndexedImageData(self._imageData, indexVal)


class merger():
    def __init__(self):
        """
        Creates empty output volume slot
        """
        self.outVol = None
    
    def GetMask(self):
            """
            Alias to L{getImageMask}.
            """
            return getImageMask(self.outVol)
    
    def getIndexed(self, uid):
        """
        Alias to L{getIndexedImageData}.
        """
        return getIndexedImageData(self.outVol, uid)
    
    def appendFromFn(self, filename, uid):
        """
        @type  filename: C{str}
        @param filename: imageData filename.
        
        @type  uid: C{int}
        @param uid: index to be assigned to this volume.
        
        @note: imput image data has to have the same in size and origin as
        L{self.outVol} otherwise the merging procedure cannot be performed.
        """
        volToAppend = normImageByUid.fromFile(filename)
        print volToAppend._imageData
        return self._appendSingle(volToAppend, uid)
    
    def appendFromVol(self, volToAppend, uid):
        """
        @type  volToAppend: C{vtkImageData}
        @param volToAppend: vtkImageData to be merged
        
        @type  uid: C{int}
        @param uid: index to be assigned to this volume.
        
        Merges C{volToAppend} with C{self.outVol}
        
        @return: C{None}
        
        @note: imput image data has to have the same in size and origin as
        L{self.outVol} otherwise the merging procedure cannot be performed.
        """
        return self._appendSingle(normImageByUid(volToAppend), uid)
    
    def _appendSingle(self, volToAppend, uid):
        """
        @type  uid: C{int}
        @param uid: index to be assigned to this volume.
       
        Method merges proivded volume with existing, cached volume. Following
        algorithm is used (e - existing image, n - new image, M - image mask):
        
        e = (n AND (M(n) XOR M(e))) + e
        
        @return: C{None}
        """
        # If privided volume is the first one, simply take it as output volume.
        if not self.outVol:
            self.outVol = volToAppend.GetIndexed(uid)
            print >>sys.stderr, "No volume found. Creating initial volume."
            return
        
        # Otherwise:
        
        # XOR existing volume with the new
        print "...start:"
        volCurNewXor = vtk.vtkImageLogic()
        volCurNewXor.SetInput1(volToAppend.GetMask())
        volCurNewXor.SetInput2(self.GetMask())
        volCurNewXor.SetOperationToXor()
        
        # Intersect xored image with the new volume getting the part of the
        # volume to be updated
        print "...start volXorAndNew:"
        volXorAndNew = vtk.vtkImageLogic()
        volXorAndNew.SetInput1(volToAppend.GetMask())
        volXorAndNew.SetInput2(volCurNewXor.GetOutput())
        volXorAndNew.SetOperationToAnd()
        
        # Change the image type
        print "...start imgCast:"
        cast = vtk.vtkImageCast()
        cast.SetInput(volXorAndNew.GetOutput())
        cast.SetOutputScalarTypeToUnsignedChar()
        
        # Assign index to the 'new' volume
        print "...start volToReplace"
        volToReplace = vtk.vtkImageMask()
        volToReplace.SetImageInput(volToAppend.GetIndexed(uid))
        volToReplace.SetMaskInput(cast.GetOutput())
        
        # Add both volumes
        print "...start newSumVol"
        newSumVol = vtk.vtkImageMathematics()
        newSumVol.SetOperationToAdd()
        newSumVol.SetNumberOfThreads(1)
        newSumVol.SetInput1(volToReplace.GetOutput())
        newSumVol.SetInput2(self.outVol)
        
        # This is funny :)
        # In order to not to store mass of the references we create deep copy
        # of the result - that gives much speedup.
        newSumVol.GetOutput().Update()
        self.outVol.DeepCopy(newSumVol.GetOutput())
        print "...stop:"
    
    def GetOutput(self):
        """
        Returns output volume
        
        @rtype: C{vtkImageData}
        @return: Processed volume.
        """
        return self.outVol

       
class opts(object):
    """
    This class emulated object with attributes passed as kwargs to constructor.
    """
    def __init__(self, kwargs):
        """
        @type  kwargs: C{dict}
        @param kwargs: Dictionary which keys will become name of class
                       attributes and values will become values of those
                       attributes.
        """
        for (k,v) in kwargs.iteritems():
            self.__setattr__(k,v)


class volumeIntegrator():
    """
    Class merging volumes from either files or from provided image data. The
    class requires providing L{barIndexer} object from which colors and
    identifires are extracted.
    """
    def __init__(self, indexer, workingDir = None, fnTemplate = VOLUME_FILENAME_TEMPLATE):
        """
        @type  indexer: L{barIndexer}
        @param indexer: barIndexerObject
        
        @type  workingDir: C{str}
        @param workingDir: Directory containing volumes to merge. Should be
                           defined only, when meging files from disk.
        
        @type  fnTemplate: C{str}
        @param fnTemplate: volume filename template. Should be provided only,
                           when merging volumes from disk. Template should
                           accept only one string value.
        """
        
        self._indexer = indexer        # Store indexer reference,
        self._workingDir = workingDir  # working directory
        self._fnTemplate = fnTemplate  # and volume filename template
        self.m = None                  # Empty slot for merger
        
        self.clear()                   # Removes all data from working variables
        self._createMappings()         # Creates index mappingd from given
                                       # indexer
    
    def integrateList(self, structuresList):
        """
        Merges volumes with names from the list by reading corresponding
        volumes from the disk.
        
        @type  structuresList: C{[str, str, ...]}
        @param structuresList: List with names of the structure to merge.
        
        @rtupe: C{None}
        @return: None
        """
        
        self.structureList = structuresList
        for name in structuresList:
            (filename, gid) = self._filenameGidMap[name]
            
            print >>sys.stderr, "Appending structure %s, %d: %s"\
                % (name, gid, filename)
            self.m.appendFromFn(filename, gid)
    
    def integrateSingle(self, inputVolume, structName):
        """
        Merges single C{inputVolume} represenring structure C{structName}.
        
        @type  inputVolume: C{vtkStructuredPoints} 
        @prarm inputVolume: volume to be integrated
        
        @type  structName: C{str}
        @param structName: Name of the structure representad by the volume
        
        @return: C{None}
        """
        
        # Get the uid of the structure and merge the volume with the global
        # volume
        uid = self._filenameGidMap[structName][1]
        self.m.appendFromVol(inputVolume, uid)
    
    def clear(self):
        """
        Clears internal cache. Removes cached structures and global volume
        """
        
        self.structureList = None
        self._filenameGidMap = None
        self.m = merger()
    
    def save(self, filename):
        """
        Saves merged volume into the file
        
        @type  filename: C{str}
        @prarm filename: full path to the output file
        """
        mergerWriter(self.m.GetOutput(), filename)
    
    def _getFilename(self, structureName):
        """
        @type  structureName: C{str}
        @param structureName: Name of the structure for which volume will be
                              returned.
        
        @type: C{str}
        @return: Path to the filename with volume representing structure defined
                 by C{structureName}.
        """
        return os.path.join(self._workingDir, self._fnTemplate % structureName)
    
    def _createMappings(self):
        """
        Creates mapping: structureName => (volume location, uid)
        """
        self._filenameGidMap = dict(map(self._createFnGidMap, self._indexer.groups.keys()))
    
    def _createFnGidMap(self, structureName):
        """
        @type  structureName: C{str}
        @param structureName: Structure name for which the filename and uid will
                              be determined.
        
        @rtype: (str, (str, int))
        @return: Tuple containing structure name and corresponding filename and  uid
        """
        group =  self._indexer.groups[structureName]
        filename = self._getFilename(structureName)
        return (structureName, (filename, group.id))
    
class barIndexerColorMapper():
    """
    Class that transforms indexed volume into RGB colored volume basing on
    provided atlas indexer.
    
    @type  _inputVolume: C{vtkImageData}
    @param _inputVolume: Placeholder for indexer volume
    
    @type  _indexer: L{barIndexer}
    @param _indexer: Indexer holding caf index
    
    @type  _gidToColorMap: C{dict}
    @param _gidToColorMap: gid to rgb color mapping
    """
    
    def __init__(self, indexer):
        """
        @type  indexer: L{barIndexer}
        @param indexer: Indexer holding caf index
        """
        
        self._indexer = indexer
        self._gidToColorMap  = self._createGidColorMap()
        self._inputVolume = None
        print self._gidToColorMap
    
    def _createGidColorMap(self):
        """
        Creates group identifier to rgb color mapping
        """
        groupsItems = self._indexer.groups.values()
        return dict(map(lambda x: (x.id, rgb(x.fill)), groupsItems))
    
    def _makeLut(self):
        """
        Creates vtkLookupTable for mapping the volumes
        """
        
        lut = vtk.vtkLookupTable()
        cm  = self._gidToColorMap   # Just simple alias
        
        # Number of colors in LUT is equal to the largest GID +1
        lut.SetNumberOfColors(max(cm.keys())+1)
        
        # Then, allocate the table with the colors. Iterate over all color
        # slots and assign proper color
        for i in range(lut.GetNumberOfColors()):
            # If given index is defined in indexer:
            # assign its color to the lookup table
            # otherwise set it to black
            if i in cm:
                if cm[i][0] == cm[i][1] == cm[i][2] == 119:
                    c = map(lambda x: float(random.randint(0, 255))/255., [0,0,0])
                    lut.SetTableValue(i, c[0], c[1], c[2], 1)
                else:
                    c = cm[i]
                    c = map(lambda x: float(x)/255., c)
                    lut.SetTableValue(i, c[0], c[1], c[2], 1)
            else:
                lut.SetTableValue(i, 0., 0., 0., 0.)
        
        # Build the LUT and return it
        lut.SetRange(0, max(cm.keys()))
        lut.Build()
        
        return lut
    
    def _getRGBVolume(self):
        """
        Calculates the RBG volume from the indexed volume. Note that the input
        volume has to be 1 channel, 16bpp indexed volume.
        
        @rtype: C{vtkImageData}
        @return: RGB colored, 24bpp volume
        
        """
        # input volume has to 
        srcRead = self._inputVolume
        
        # Create and configure proper vtk fiter:
        map = vtk.vtkImageMapToColors()
        map.SetInput(srcRead)
        map.SetOutputFormatToRGB()
        map.SetLookupTable(self._makeLut())
        map.Update()
        
        # and return the result
        return map.GetOutput()
    
    def save(self, filename):
        """
        Saves colored volume into the file
        
        @type  filename: C{str}
        @prarm filename: full path to the output file
        """
        mergerWriter(self._getRGBVolume(), filename)
    
    def SetInput(self, inputVtkImageData):
        """
        Sets the input indexer C{vtkImageData}.
        
        @note: the input volume has to be 1 channel (single component),
               16bpp indexed volume.
        """
        self._inputVolume = inputVtkImageData
    
    def GetOutput(self):
        return self._getRGBVolume()


def createOptionParser():
    """
    @return: C{OptionParser}
    Creates and returns OptionParser object suited for command line arguments processing.
    """
    parser = OptionParser()
    
    parser = OptionParser(usage="usage: %s [options] CAF_index structure1 structure2 ...  structureN")

    parser.add_option("-l", "--mergeFromListOfVolumes", dest="mergeList",
            action="store_true", default=False,
            help="Merge structures from volume files stored in single directory. Requires providing working directory.")
    
    parser.add_option("-d", "--volumesDirectory", dest="workingDir", action="store",
            help="Directory containing volumes with corresponding structures.",
            metavar="DIR", default=".")
    
    parser.add_option("-m", "--mergeFromRecontructor",
            dest="mergeReconstructor", action="store_true", default=False,
            help="Merge volumes during reconstructrion")
    
    parser.add_option("-r", "--recolorOnly", dest="recolorOnly",
            action="store_true", default=False,
            help="Do not merge any volume, recolor provided volume only.")

    parser.add_option("-i", "--inputLabeledVolume", dest="inputLabeledVolume",
            default=None,
            action="store", help="Input labeled volume to be colored using indexer.")
    parser.add_option("-o", "--outputVolumeName", dest="outVolFilename", action="store",
            help="Output volume filename.", metavar="FILENAME", default=None)
    parser.add_option("-c", "--colorVolumeFilename", dest="oColorFilename", action="store",
            default=None,
            help="Output volume filename.", metavar="FILENAME")
    
    parser.add_option("-t", "--volumeFilenameTemplate", dest="volFnTemplate",
            action="store", default=VOLUME_FILENAME_TEMPLATE, type="string")
    return parser


def validateOptions(opts):
    """
    @type  opts: parsed OptionParsed object
    @param opts: Set of options extracted and parsed by OptionParser
    @return    : True when options set passes all validation rules, False otherwise.
    
    Validates provided options formally and logicaly.
    Detail of validation process are explained in comments.
    """
    # print opts
    
    # If "recolor only" is set no volume merging is allowed:
    if opts.recolorOnly and ( opts.mergeReconstructor or opts.mergeList):
        printRed("Enabling 'recolor only' disables merging.")
        return False
    
    # Merging can be performed exclusively from files or from volumes generated
    # at runtime.
    if opts.mergeReconstructor and opts.mergeList:
        printRed("Merging can be performed exclusively from files or from at runtime.")
        return False
    
    # Merging from files requires providing directory with volumes:
    if opts.mergeList and not opts.workingDir:
        printRed("Merging from files requires providing directory with volumes.")
        
    # Output volume filename  is required 
    if (opts.mergeReconstructor or opts.mergeList) and not opts.outVolFilename:
        printRed("Output volume filename is required")
        return False
    
    # Chech if directory containing columes exist.
    if opts.workingDir and (not os.path.isdir(opts.workingDir)):
        printRed("Provided working directory is not a valid directory.")
        return False
    
    return True

if __name__ == '__main__':

    parser=createOptionParser()
    (options, args) = parser.parse_args()
    
    # Validate command line arguments
    # When arguments turns out invalid, print notification and quit script
    if not validateOptions(options) or len(args) < 2:
        printRed("Invalid command line arguments. Please correct.")
        parser.print_help()
        exit(1)
    
    cafInfexFilename   = args[0]
    structuresList     = args[1:]
    
    # Atlas indexer is required in all processing cases
    indexer = barIndexer.fromXML(cafInfexFilename)
    
    # If recolor only is choosen, do nothing but recoloring:
    if options.recolorOnly:
        inputVolReader = mergerStructPtsReader(options.inputLabeledVolume)
        colorMapper = barIndexerColorMapper(indexer)
        colorMapper.SetInput(inputVolReader.GetOutput())
        colorMapper.save(options.oColorFilename)
        exit(0)
    
    # In all further cases volume integrator will be required,
    # define him here:
    integrator = volumeIntegrator(indexer, options.workingDir)
    
    # Merging from file list:
    if options.mergeList:
        integrator.integrateList(structures)
    
    # Merging volumes reconstructed on the fly
    if options.mergeReconstructor:
        o = {'pipeline': None,\
             'exportDir': '.',\
             'show': False,\
             'composite': False,\
             'brainoutline': False,\
             'format': None,\
             'voxelDimensions': [0.2, 0.2],\
             'format': ['exportToVolume'],\
             'camera': (0.0, 0.0, 1.0),\
             'generateSubstructures': 10}
        
        dummyOpts = opts(o)
        
        class berMergerRec(barReconstructionModule):
            def exportToVolume(self, filename):
                print os.path.split(filename)
                strtcName = os.path.split(filename)[-1].split('.')[0].split('_')[1]
                integrator.integrateSingle(self.vtkVolume.GetOutput(), strtcName)
        vtkapp = berMergerRec()
        
        recModule = barBatchReconstructor(vtkapp, cafInfexFilename, dummyOpts)
        recModule.prepareLoop(structuresList)
        recModule.runLoop()
    
    # Saving merged and labeled volume
    integrator.save(options.outVolFilename)
    
    # Exporting colored volume:
    if options.oColorFilename:
        colorMapper = barIndexerColorMapper(indexer)
        colorMapper.SetInput(integrator.m.GetOutput())
        colorMapper.save(options.oColorFilename)
