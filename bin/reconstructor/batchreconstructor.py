#!/usr/bin/python
# -*- coding: utf-8 -*
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
The module provides the L{barBatchReconstructor} class for performing the
batch reconstruction process of structures from CAF datasets.

If run as a script, performs requested reconstructions of requested structures
from given CAF dataset. Run with C{--help} argument for details.

G{importgraph}
"""

import os
import random
import math
import vtk 
from batchinterface import batchInterface

from bar.base import debugOutput
from bar.color import intColourToFloat
import bar.rec.structure_holder as structureHolder
from bar.rec.barreconstructor import barReconstructionModule, HTMLColorToRGB,\
                             barPipeline, BAR_DEFAULT_RECONSTRUCTION_DIR,\
                             BAR_TEMPLATE, BAR_ATLAS_INDEX_FILENAME,\
                             BAR_BRAIN_OUTLINE_PROPS, SCENE_EXPORT_FORMAT_MASK

def rotateY(a, (x, y, z)):
    return (math.sin(a) * z + math.cos(a) * x,
            y,
            math.cos(a) * z - math.sin(a) * x)

def rotateZ(a, (x, y, z)):
    return (math.cos(a) * x - math.sin(a) * y,
            math.sin(a) * x + math.cos(a) * y,
            z)

def rotateX(a, (x, y, z)):
    return (x,
            math.sin(a) * z + math.cos(a) * y,
            math.cos(a) * z - math.sin(a) * y)

class barBatchReconstructor(object):
    """
    The class for performing batch reconstructions of structures from CAF datasets.
        
    @cvar MAX_HIERARCHY_DEPTH: the maximum supposed depth of hierarchy tree.
    @type MAX_HIERARCHY_DEPTH: int

    @ivar vtkapp: structure from volume reconstructor used by the object
    @type vtkapp: L{barReconstructionModule} object
    
    @ivar renWin: the render window used by the object
    @type renWin: vtk.vtkRenderWindow object
    
    @ivar iren: the render window interactor used by the object
    @type iren: vtk.vtkRenderWindowInteractor
    
    @ivar sh: an object holding structures data from CAF datasets
    @type sh: L{structureHolder} object
    
    @group Voxel size: xyres, zres
    
    @ivar xyres: Voxel size in coronal plane in mm
    @type xyres: float
    
    @ivar zres: Voxel size along anterior-posterios axis in mm
    @type zres: float
    
    @ivar exportDir: the path to a directory for reconstructions
    @type exportDir: str
    
    @ivar depth: the maximum level of substructures (in the structure tree)
                 to be generated
    @type depth: int
    
    @ivar formats: the set of reconstruction file formats to be generated
    @type formats: set(str)
    
    @ivar show: True if the reconstruction has to be displayed to the user,
                False otherwise
    @type show: bool
    
    @ivar composite: True if requested to perform a reconstruction of the
                     structure as a scene composed of the reconstructions of
                     the basic substructures in the hierarchy tree (up to the
                     level L{depth}), False otherwise.
    @type composite: bool
    
    @ivar brainoutline: Indicates if during reconstruction additional
                        translucent brain outline will be generated and appended
                        to the reguler reconstructions. Such outline may be
                        exported only to scene formats as VRML, X3D or into
                        thumbnails. The color and transparency of the outline
                        is defined by L{BAR_BRAIN_OUTLINE_PROPS} dictionary and
                        currently cannot be customized using command line
                        options. This option requires generated brain mesh to be
                        present in given output dir.
    @type brainoutline: bool
    
    @ivar _simpleQueue: the queue of simple reconstructions to perform; each queue
                        element is a pair of structure name and a set of export
                        formats
    @type _simpleQueue: [(str, set([str, ...])), ...]
    
    @ivar _compositeQueue: the queue of composite reconstructions to perform;
                           each queue element is a three of reconstruction name,
                           a set of component structure names and a set
                           of formats.
    @type _compositeQueue: [(str, set([str]), set([str, ...]), ...]
    """
    
    MAX_HIERARCHY_DEPTH = 999
    
    def __init__(self, vtkapp, index, options):
        """
        @param vtkapp: C{self.L{vtkapp}} value
        @type vtkapp: L{barReconstructionModule} object
        
        @param options: an object containing constructor options as its
                        attributes:
                          - C{cameraMovementAngles} - C{self.L{vtkapp}.L{cameraPosition<barReconstructionModule.cameraPosition>}}
                            and C{self.L{vtkapp}.L{cameraViewUp<barReconstructionModule.cameraViewUp>}}
                            values encoded as camera movement angles,
                          - C{background} - C{self.L{vtkapp}.L{background<barReconstructionModule.background>}},
                          - C{pipeline} - C{self.L{vtkapp}.L{pipeline<barReconstructionModule.pipeline>}} value,
                          - C{voxelDimensions} - C{(self.L{xyres}, self.L{zres})} value,
                          - C{exportDir} - C{self.L{exportDir}} value,
                          - C{generateSubstructures} - C{self.L{depth}} value,
                          - C{format} - C{self.L{formats}} members list,
                          - C{show} - C{self.L{show}} value,
                          - C{brainoutline} - C{self.L{brainoutline}} value,
                          - C{composite} - C{self.L{composite}} value; if True forces C{'exportToVTKPolydata' in self.L{formats}}
                          - C{ignoreBoundingBox} - C{self.L{ignoreBoundingBox}}
                            Overrides bounding box calculation - bounding box
                            will be always equal to hierarchy root element
                            bounding box. Volumes for all structures will always
                            have the same size and origin. This feature
                            increases memory usage and reconstruction time.
        
        @type options: optparse.Values object
        
        @param index: the path to a CAF dataset index file
        @type index: str
        
        @note: C{L{options}.attribute == None} means that the value of the
               constructor option was not given, so its default value is
               assumed. Word "attribute" mean any of the attributes of
               the option object.
        """
        # load CAF dataset
        atlasDir, indexFilename = os.path.split(index)
        self.loadAtlas(atlasDir, indexFilename)
        
        self._basicSetup(vtkapp, options)
        
        if options.pipeline != None:
            self.vtkapp.pipeline = barPipeline.fromXML(options.pipeline)
        
        if self.composite:
            self.formats.add('exportToVTKPolydata')

    def _basicSetup(self, vtkapp, options):
        """
        Constructor code common with derivative classes constructor.
        
        @param vtkapp: C{self.L{vtkapp}} value
        @type vtkapp: L{barReconstructionModule} object
        
        @param options: an object containing constructor options as its
                        attributes:
                          - C{cameraMovementAngles} - C{self.L{vtkapp}.L{cameraPosition<barReconstructionModule.cameraPosition>}}
                            and C{self.L{vtkapp}.L{cameraViewUp<barReconstructionModule.cameraViewUp>}}
                            values encoded as camera movement angles,
                          - C{background} - C{self.L{vtkapp}.L{background<barReconstructionModule.background>}},
                          - C{pipeline} - C{self.L{vtkapp}.L{pipeline<barReconstructionModule.pipeline>}} value,
                          - C{voxelDimensions} - C{(self.L{xyres}, self.L{zres})} value,
                          - C{exportDir} - C{self.L{exportDir}} value,
                          - C{generateSubstructures} - C{self.L{depth}} value,
                          - C{format} - C{self.L{formats}} members list,
                          - C{show} - C{self.L{show}} value,
                          - C{brainoutline} - C{self.L{brainoutline}} value,
                          - C{composite} - C{self.L{composite}} value; if True forces C{'exportToVTKPolydata' in self.L{formats}}
        
        @type options: optparse.Values object
        """
        self.vtkapp = vtkapp
        
        # Process options
        self.vtkapp.background = intColourToFloat(options.background)
        self.cameraMovementAngles = options.cameraMovementAngles

        if options.voxelDimensions != None:
            self.xyres, self.zres = options.voxelDimensions
        
        if options.exportDir != None:
            self.exportDir = options.exportDir
        
        if options.brainoutline:
            self.brainoutline = options.brainoutline
        else:
            self.brainoutline = False
        
        self.depth = options.generateSubstructures
        
        self.formats = set()
        if options.format != None:
            self.formats = set(options.format)
        
        self.show = options.show
        self.composite = options.composite
        self.ignoreBoundingBox = options.ignoreBoundingBox
        
        #---------------------- done with options
        
        # Proceed with VTK setup 
        # Create the RenderWindow and RenderWindowInteractor
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.SetSize(800,600)
        self.vtkapp.addRenderWindow(self.renWin)
        
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)
        self.iren.Initialize()
        
        self._simpleQueue = []
        self._compositeQueue = []

    def __getFileName(self, name, outputFormat):
        """
        @param name: the name of the structure
        @type name: str

        @param outputFormat: the requested file format (the name of the
                             suitable export method)
        @type outputFormat: str

        @return: a path to the reconstruction of the structure in the 
                 requested format
        @rtype: str
        """
        return os.path.join(self.exportDir,
                            BAR_TEMPLATE[outputFormat]%name)
    
    def _exportToFormats(self, name, formats=None):
        """
        Perform export of the reconstruction requested formats.
        
        @param name: name of the structure
        @type name: str
        
        @param formats: formats for which the export is performed; if not set,
                        the export is performed for formats requested
                        in C{self.L{formats<barBatchReconstructor.formats>}}.
        @type formats: [str, ...]
        """
        if formats == None:
            requestedFormats = self.formats
        else:
            requestedFormats = set(formats)
        
        for outputFormat in requestedFormats:
            print outputFormat, requestedFormats

            self._exportToFormat(name, outputFormat)

    def _exportToFormat(self, name, outputFormat):
        """
        Export the reconstruction to requested format.

        @param name: name of the structure
        @type name: str

        @param outputFormat: requested format
        @type outputFormat: str
        """
        # distinct reconstructions with and without brain outline
        exportName = name
        if self.brainoutline and outputFormat in SCENE_EXPORT_FORMAT_MASK:
            exportName = self.sh.ih.hierarchyRootElementName + '__' + name

        filename = self.__getFileName(exportName, outputFormat)
        getattr(self.vtkapp, outputFormat)(filename)

    def exportToWindow(self, updateRenderWindow=True):
        """
        Displays the reconstruction to the user and waits until the window
        is closed, then prints the final camera position and voxel size
        (C{self.L{xyres}} and C{self.L{zres}}) as the L{batchreconstructor}
        script arguments.

        @param updateRenderWindow: idicates if the method has to update the render
                                   window
        @type updateRenderWindow: bool
        """
        if updateRenderWindow:
            self.vtkapp.updateRenderWindow()
        self.iren.Start()
        
        print '-d', self.xyres, self.zres
        print '--cameraMovementAngles %f %f %f' % self.cameraMovementAngles

    def prepareLoop(self, structureNames):
        """
        Prepare the reconstruction queues L{_simpleQueue} and L{_compositeQueue}
        to perform requested reconstructions.

        @param structureNames: roots of hierarchy subtrees
        @type structureNames: [str, ...]
        """
        # get names of hierarchy subtrees nodes
        uniqueNames = self.sh.ih.unfoldSubtrees(structureNames, self.depth, leavesOnly=False)
        
        # and request performing of their simple reconstructions
        for name in uniqueNames:
            self.prepareSimpleLoop(name)

        # if composite reconstruction is requested
        if self.composite:
            # get names of hierarchy subtrees leaf nodes
            components = self.sh.ih.unfoldSubtrees(structureNames, self.depth, leavesOnly=True)

            # combine their names into reconstruction name
            name = '_'.join(sorted(list(components)))
            
            # and request the reconstruction
            self.prepareCompositeLoop(name, components)
    
    def prepareSimpleLoop(self, structureName, formats=None):
        """
        Append a request of reconstruction to L{_simpleQueue}.
        
        @param structureName: name of the structure to be reconstructed
        @type structureName: str
        
        @param formats: formats the reconstruction has to be exported to;
                        if not given the reconstruction is exported for every
                        format in L{self.formats<barBatchReconstructor.formats>}
        @type formats: sequence([str, ...])
        """
        
        if formats==None:
            requestedFormats = frozenset(self.formats)
        else:
            requestedFormats = frozenset(formats)
        
        queueElement = (structureName, requestedFormats)
        self._simpleQueue.append(queueElement)
    
    def prepareCompositeLoop(self, name, components, formats=None):
        """
        Append a composite reconstruction request to L{_compositeQueue}.
        
        @param structureName: name of the reconstruction
        @type structureName: str
        
        @param components: names of structures to be included into
                           the reconstruction
        @type components: sequence([str, ...])
        
        @param formats: formats the reconstruction has to be exported to;
                        if not given the reconstruction is exported for every
                        format in L{self.formats<barBatchReconstructor.formats>}
        @type formats: sequence([str, ...])
        """
        
        if formats==None:
            requestedFormats = frozenset(self.formats)
        else:
            requestedFormats = frozenset(formats)

        queueElement = (name,
                        components,
                        requestedFormats & SCENE_EXPORT_FORMAT_MASK)
        self._compositeQueue.append(queueElement)
    
    def runLoop(self):
        """
        Perform requested reconstructions.
        """
        if self.brainoutline:
            self._prepareBrainOutlineActor()
        
        # perform simple reconstructions
        for name, formats in self._simpleQueue:
            self.generateModel(name)
            
            if self.brainoutline:
                self._appendBrainOutlineActor()
            
            self._exportToFormats(name, formats)
            
            if self.show:
                self.exportToWindow()
        
        # Clean the quque. 
        self._simpleQueue = []
        
        # perform composite reconstructions
        for name, structures, formats in self._compositeQueue:
            self.vtkapp.clearScene()
            self.vtkapp.clearVolume()
            
            self._compositeReconstruction(name, structures)
            
            if self.brainoutline:
                self._appendBrainOutlineActor()
            #-----------------
            
            self._exportToFormats(name, formats)
            
            if self.show:
                self.exportToWindow()
        
        # flush the loop queue
        self._compositeQueue = []
    
    def _compositeReconstruction(self, name, structures):
        """
        Perform composite reconstruction.
        
        @param structureName: name of the reconstruction
        @type structureName: str
        
        @param components: names of structures to be included into
                           the reconstruction
        @type components: sequence([str, ...])
        """
        
        # When composite reconstruction is enabled, every model has to be cached
        # after reconstruction and loaded with all other reconstructed models
        # note that when composite reconstuction is enabled, exportToVTKPolydata
        # is forced to be true so models are already cached.
        
        # load all substructures and show them in renderwindow
        for structureName in structures:
            ct = self.getStructureColor(structureName)
            filename = self.__getFileName(structureName, 'exportToVTKPolydata')
            self.vtkapp.appendContextActor(structureName, filename, ct)
        self.vtkapp.refreshRenderWindow()
    
    def _prepareBrainOutlineActor(self):
        """
        Request the generation of the whole brain outline if necessary.
        """
        
        rootElemName = self.sh.ih.hierarchyRootElementName
        filename = self.__getFileName(rootElemName, 'exportToVTKPolydata')
        if not os.path.exists(filename):
            self._simpleQueue[:0] = [(rootElemName, frozenset(['exportToVTKPolydata']))] 
    
    def _appendBrainOutlineActor(self):
        """
        Loads the vtkPolyData file with the outline of the whole brain and
        appends it as translucent context actor.
        """
        
        rootElemName = self.sh.ih.hierarchyRootElementName
        filename = self.__getFileName(rootElemName, 'exportToVTKPolydata')
        if os.path.exists(filename):
            self.vtkapp.appendContextActor(\
                    rootElemName,\
                    filename,\
                    (0,0,0),\
                    BAR_BRAIN_OUTLINE_PROPS)
            self.vtkapp.refreshRenderWindow() 
    
    def _generateVolume(self, structureName):
        """
        @param structureName: the name of requested structure
        @type structureName: str
        
        @return: a volumetric representation of requested structure
        """
        self.sh.handleAllModelGeneration(\
                structureName, self.xyres, self.zres,\
                ignoreBoundingBox=self.ignoreBoundingBox) 
        return self.sh.StructVol
    
    def generateModel(self, structureName):
        """
        Generate a volumetric representation of requested structure and
        pass it to C{self.L{vtkapp}} as a source volume for model generation.
        
        @param structureName: the name of the structure to be reconstructed
        @type structureName: str
        """
        # Handling not defined structures
        if not type(self.sh.getSlidesSpan(structureName)) == type(("",)): return
        
        volume = self._generateVolume(structureName)
        volume.prepareVolume(self.sh.ih)
        
        # Get colour of the structure
        ct = self.getStructureColor(structureName)
       
        # Pass generated volume for model generation
        self.vtkapp.setReconstructionSource(volume, ct)
    
    def getStructureColor(self, structureName, rgb = False):
        """
        @param structureName: the name of the structure
        @type structureName: str
        
        @param rgb: True if requested colour format is 24-bit RGB (8 bits per
                    chanel), False otherwise.
        @type rgb: bool
        
        @return: the colour suitable for a model of requested structure
        @rtype: [int, int, int] | [float, float, float]
        """
        ct = HTMLColorToRGB(self.sh.ih.colorMapping[structureName])
        
        #TODO: Get rid of this after implementing automatic, hierarchy based
        # colour assignment.
        # Dummy patch: when colour is not provided (=structure has gray colour
        # defined) choose random one.
        if ct[0] == ct[1] == ct[2] == 119:
            random.seed(structureName)
            ct = map(lambda x: random.randint(0, 255), [0,0,0])
        
        if not rgb:
            ct = list(intColourToFloat(ct))
        return ct
    
    def loadAtlas(self, indexDirectory, indexFile = BAR_ATLAS_INDEX_FILENAME):
        """
        @type  indexDirectory: C{str}
        @param indexDirectory: directory containing caf index file and caf
        slides. In other words CAF dataset directory.
        
        Loads CAF dataset defined by provided index directory.
        """
        indexFile = os.path.join(indexDirectory, indexFile)
        self.sh = structureHolder.structureHolder(\
                indexFile, indexDirectory)
        
        self.__atlasDirectory   = indexDirectory
        
        # Try to create reconstruction directory, if directory cannot be created
        # leave default output directory undefined
        recDir =\
            os.path.abspath(os.path.join(self.__atlasDirectory,
                BAR_DEFAULT_RECONSTRUCTION_DIR))
        
        if not os.path.exists(recDir):
            try:
                os.mkdir(recDir)
                self.exportDir = recDir
            except:
                self.exportDir = self.__atlasDirectory
        else:
            self.exportDir = recDir
        
        # Getting and updating default reconstruction parameters:
        self.xyres = abs(float(self.sh.ih.refCords[-1]))
        self.zres  = abs(float(self.sh.ih.getDefaultZres()))

    def __setCameraMovementAngles(self, (azimuth, elevation, roll)):
        """
        Move camera to requested position.

        @param azimuth: azimuth angle [deg]
        @type azimuth: float

        @param elevation: elevation angle [deg]
        @type elevation: float

        @param roll: roll angle [deg]
        @type roll: float
        """
        camera = (0.0, 0.0, 1.0)
        top = (0.0, 1.0, 0.0)

        (azimuth, elevation, roll) = [x * math.pi / 180 for x in (azimuth, elevation, roll)]

        #camera = rotateZ(-roll, camera) # x,y are 0
        top = rotateZ(-roll, top)

        camera = rotateX(elevation, camera)
        top = rotateX(elevation, top)

        camera = rotateY(azimuth, camera)
        top = rotateY(azimuth, top)

        self.vtkapp.cameraViewUp = top
        self.vtkapp.cameraPosition = camera

    def __getCameraMovementAngles(self):
        """
        @return: camera position as its movement angles (azimuth, elevation
                 and roll) in degres
        @rtype: (float, float, float)
        """
        camera = self.vtkapp.cameraPosition
        top = self.vtkapp.cameraViewUp
        
        if camera[0] != 0 or camera[2] != 0:
            a = math.atan2(camera[0], camera[2])
            camera = rotateY(-a, camera)
            top = rotateY(-a, top)
        
        b = math.atan2(camera[1], camera[2])
        camera = rotateX(-b, camera)
        top = rotateX(-b, top)
        
        c = math.atan2(top[0], top[1])
        #camera = rotateZ(c, camera)
        top = rotateZ(c, top)

        debugOutput("initial top: %s" % str(top))
        debugOutput("initial camera: %s" % str(camera))
        return tuple(x * 180 / math.pi for x in (a, b, c))

    cameraMovementAngles = property(__getCameraMovementAngles, __setCameraMovementAngles)


if __name__ == '__main__':
    bi = batchInterface(barBatchReconstructor)
    bi.main() 
