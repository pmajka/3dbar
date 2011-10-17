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
The module provides class necessary to create a reconstruction model from
a volume.

G{importgraph}

@var SCENE_EXPORT_FORMAT_MASK: the mask of formats allowing to export a scene
                               ("allowing to" is not "dedicated to")
@type SCENE_EXPORT_FORMAT_MASK: frozenset([str, ...])
"""


import sys
import vtk 
import numpy as np
import nifti

from bar.rec.pipeline import barPipeline, VTK_PIPELINE

# to enable the possibility of importing classes from the module
from bar.rec.pipeline import barPipeElem, barParam, DISPLAYABLE
from bar.rec.formats import BAR_SCENE_TEMPLATE, BAR_VOLUME_TEMPLATE,\
                            BAR_EXPORT_FORMATS, getFormatInfo, BAR_TEMPLATE,\
                            BAR_EXPORT_FORMAT_INFO, BAR_EXPORT_VOLUME_FORMATS,\
                            BAR_EXPORT_SCENE_FORMATS, SCENE_EXPORT_FORMAT_MASK,\
                            IMAGE_EXPORT_FORMAT_MASK, BAR_CACHED_MODEL_MASK
                
from bar.rec.thumbnail import Thumbnail

#TODO: documentation
BAR_RECONSTRUCTOR_VERSION = "ver. 0.1"

BAR_DEFAULT_RECONSTRUCTION_DIR = '../reconstructions'
BAR_ATLAS_INDEX_FILENAME = 'index.xml'


# Defines property of the whole brain outline
# when it is appended along with regular reconstructions.
BAR_BRAIN_OUTLINE_PROPS = {'SetColor':(0.8,0.8,0.8), 'SetOpacity': 0.05}

BAR_RENDERER_BACKGROUND = (1.0, 1.0, 1.0)
#BAR_RENDERER_BACKGROUND = (0.93, 0.87, 0.67)


def VTKtoNumpy(vol):
    """
    Implemented from:
    http://public.kitware.com/pipermail/vtkusers/2002-September/062934.html
    """
    
    exporter = vtk.vtkImageExport()
    exporter.SetInput(vol)
    dims = exporter.GetDataDimensions()
    
    # Define Numpy data type depending on the vtkImageData scalar type
    if (exporter.GetDataScalarType() == 3):
       type = np.uint8
    if (exporter.GetDataScalarType() == 4):
       type = np.short
    if (exporter.GetDataScalarType() == 11):
       type = np.double
    
    # Create empty Numpy array of length equal to size of vtkImage data
    # then convert it into string and pass the pointer to the beginning of the
    # string into vtkExporter so the image data could be rewritten to the
    # string.
    a = np.zeros(reduce(np.multiply,dims), type)
    s = a.tostring()
    exporter.SetExportVoidPointer(s)
    exporter.Export()
    
    # Recreate nympy array from the string and return the result.
    a = np.reshape(np.fromstring(s,type),(dims[2],dims[1],dims[0]))
    return a


def HTMLColorToRGB(colorstring):
    """
    convert #RRGGBB to an (R, G, B) tuple
    """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)


class dataImporterFromNumpy(vtk.vtkImageImport):
    def __init__(self, structVol):
        # For VTK to be able to use the data, it must be stored as a VTK-image. This can be done by the vtkImageImport-class which
        # imports raw data and stores it.
        # The preaviusly created array is converted to a string of chars and imported.
        volExtent = structVol.size
        volSpacing = structVol.spacing
        volOrigin = structVol.origin
        
        data_string = structVol.vol.tostring('F')
        self.CopyImportVoidPointer(data_string, len(data_string))
        
        del data_string
        
        # The type of the newly imported data is set to unsigned char (uint8)
        self.SetDataScalarTypeToUnsignedChar()
        
        # Because the data that is imported only contains an intensity value (it
        # isnt RGB-coded or someting similar), the importer must be told this is
        # the case.
        self.SetNumberOfScalarComponents(1)
        
        # honestly dont know the difference between SetDataExtent() and
        # SetWholeExtent() although VTK complains if not both are used.
        
        self.SetDataExtent (0, volExtent[0]-1, 0, volExtent[1]-1, 0, volExtent[2]-1)
        self.SetWholeExtent(0, volExtent[0]-1, 0, volExtent[1]-1, 0, volExtent[2]-1)
        self.SetDataSpacing(volSpacing[0], volSpacing[1], volSpacing[2])
        self.SetDataOrigin (volOrigin[0],  volOrigin[1],  volOrigin[2])


class barReconstructionModule(object):
    """
    The class provides an interface to create reconstruction model from a volume.
    
    @ivar renderer: The renderer used by the object.
    @type renderer: VTK renderer
    
    @ivar renWin: The window used by the object to render.
    @type renWin: vtkRenderWindow
    
    @ivar __mainActorCol: The colour of model to be reconstructed.
    
    @group Actors: __mainActor, __contextActors
    
    @ivar __mainActor: The displayable reconstructed model of structure. 
                       The model is a result of execution the final part
                       of the pipeline (C{self.L{__finalPipeline}})
                       on C{self.L{vtkMesh}}
    @type __mainActor: VTK actor
    
    @ivar __contextActors: The structure name to displayable model mapping.
    @type __contextActors: dict(str: VTK actor)
    
    @ivar __sourceVolume: The source volume to perform reconstruction from.
    @type __sourceVolume: dataImporterFromNumpy object
    
    @group Cache: __vtkVolume, __vtkMesh
    
    @ivar __vtkVolume: The cached result of execution the volumetric part 
                       of the pipeline (C{self.L{__volumePipeline}})
                       on C{self.L{__sourceVolume}}.
    
    @ivar __vtkMesh: The cached result of execution the mesh processing part
                     of the pipeline (C{self.L{__meshPipeline}}) 
                     on C{self.L{vtkVolume}}.
    
    @group Pipelines: __pipeline, __volumePipeline, __meshPipeline,
                      __finalPipeline
    
    @ivar __pipeline: The pipeline used by the object. See L{pipeline} for
                      details.
        
    @type __pipeline: L{barPipeline} object
    
    @ivar __volumePipeline: The volume processing part of the pipeline. See
                            L{pipeline} for details.
    @type __volumePipeline: L{barPipeline} object
    
    @ivar __meshPipeline: The mesh processing part of the pipeline See
                          L{pipeline} for details.
    @type __meshPipeline: L{barPipeline} object
    
    @ivar __finalPipeline: The actor creating part of the pipeline. See
                           L{pipeline} for details.
    @type __finalPipeline: L{barPipeline} object

    @ivar exportVolumeByExt: file extension to volume export method mapping
    @type exportVolumeByExt: {str: function}

    @ivar exportSceneByExt: file extension to scene export method mapping
    @type exportSceneByExt: {str: function}
    """
    
    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.background = BAR_RENDERER_BACKGROUND
        self.renWin = None
        
        self.__mainActorCol = None
        self.__mainActor = None
        self.__contextActors = {}
        
        self.__sourceVolume = None
        self.__vtkVolume = None
        self.__vtkMesh = None
        
        self.pipeline = VTK_PIPELINE
        
        self.exportVolumeByExt = self.__createExportByExt(BAR_EXPORT_VOLUME_FORMATS)
        self.exportSceneByExt = self.__createExportByExt(BAR_EXPORT_SCENE_FORMATS)

    def __createExportByExt(self, formatInfo):
        """
        Create file extension to export method mapping.
        
        @param formatInfo: information about formats to be included in the mapping
        @type formatInfo: {str: {'ext': str, ...}, ...}
        
        @return: file extension to export method mapping
        @rtype: {str: function}
        """
        return dict((info['ext'], getattr(self, method))\
                    for (method, info) in formatInfo.iteritems())
    
    def addRenderWindow(self, renderWindow):
        """
        Assign the C{renderWindow} to L{renWin};
        add L{renderer} as one of the window renderers.
        
        @type renderWindow:
        @param renderWindow: the window to perform rendering.
        """
        if self.renWin != None and self.renWin.HasRenderer(self.renderer):
            self.renWin.RemoveRenderer(self.renderer)
        self.renWin = renderWindow
        self.renWin.AddRenderer(self.renderer)
    
    def __createMainActor(self):
        """
        If no main actor (C{self.L{__mainActor} == None}) create it from the
        volume C{self.L{__sourceVolume}} (if exists). The colour of main actor
        is given by C{self.L{__mainActorCol}}
        """
        if self.__mainActor == None and self.__sourceVolume != None:
            ct = self.__mainActorCol
            vtksource = self.__finalPipeline.execute(self.vtkMesh)
            
            self.__mainActor = vtk.vtkLODActor()
            self.__mainActor.SetMapper(vtksource)
            self.__mainActor.GetProperty().SetColor(ct[0],ct[1],ct[2])
            
            self.renderer.AddActor(self.__mainActor)
    
    def setReconstructionSource(self, structVol, ct):
        """
        Assign requested model colour and source volume for reconstruction.
        
        @param structVol: source volume for reconstruction
        @type structVol: L{VTKStructuredPoints} object
        
        @param ct: requested colour of reconstructed model
        
        @note: Method removes current reconstruction.
        """
        self.__clearCache()
        
        # set up renderer source volume and colour
        self.__sourceVolume = dataImporterFromNumpy(structVol)
        self.__mainActorCol = ct

#{ Clearing methods

    def clearVolume(self):
        """
        Remove source volume.
        """
        self.__sourceVolume = None
        
    def clearScene(self):
        """
        Remove all actors (main actors as well as context actors) from the scene.
        """
        self.__removeMainActor()
        
        for actor in self.__contextActors.itervalues():
            self.renderer.RemoveActor(actor)
        self.__contextActors = {}
        
        self.refreshRenderWindow()
    
    def __clearCache(self):
        """
        Remove all cached result of source volume processing.
        
        @note: the main actor in the scene is also considered as a cached result.
        """
        self.__removeMainActor()
        self.__vtkVolume = None
        self.__vtkMesh = None
    
    def __removeMainActor(self):
        """
        Remove the main actor from the scene.
        """
        if self.__mainActor != None:
            self.renderer.RemoveActor(self.__mainActor)
        self.__mainActor = None

#}

#{ Context actor manipulation methods

    def appendContextActor(self, name, filename, color, customProps = dict()):
        """
        Add a context actor (actor with a name) loaded from a file to the
        scene.
        
        @param name: the name of the actor
        @type name: str
        
        @param filename: path to a file containing the actor
        @type filename: str
        
        @param color: the requested colour of the actor
        @type color: (float, float, float)
        
        @param customProps: C{dict}
        @type  customProps: dictionary storing additional properties to be applied to
                       the actor (opacity, diffuse color, etc.)
        
        @note: the method DOES NOT trigger the scene to render
        """
        
        # If if actor with given name already exists,
        # remove it
        if self.hasContextActor(name):
            self.removeContextActor(name)
        
        # Read the vtkPolyData file from the disk
        # and load it into render window trough the mapper
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(filename)
        
        mapMesh = vtk.vtkPolyDataMapper()
        mapMesh.SetInputConnection(reader.GetOutputPort())
        
        meshActor = vtk.vtkLODActor()
        meshActor.SetMapper(mapMesh)
        meshActor.GetProperty().SetColor(color)
       
        print customProps
        # Apply additional setting as given by customProps
        for (k,v) in customProps.items():
            # Apply the property depending on its type:
            if v:
                getattr(meshActor.GetProperty(), k)(v)
            else:
                getattr(meshActor.GetProperty(), k)()
        
        # Create reference for the appended actor
        self.__contextActors[name] = meshActor
        self.renderer.AddActor(meshActor)
    
    def removeContextActor(self, name):
        """
        Remove the context actor from the scene.
        
        @param name: the name of the actor to be removed.
        @type name: str
        
        @note: the method DOES NOT trigger the scene to render
        """
        self.renderer.RemoveActor(self.__contextActors[name])
        del self.__contextActors[name]
    
    def hasContextActor(self, name):
        """
        Check if the context actor is in the scene.
        
        @param name: the name of the context actor
        @type name: str
        
        @return: True if the actor named name is in the scene, False otherwise.
        @rtype: bool
        """
        return name in self.__contextActors

#}

#{ Render window refreshing methods

    def refreshRenderWindow(self):
        """
        Render the scene to the render window.
        """
        if self.renWin != None:
            self.renWin.Render()
    
    def updateRenderWindow(self, resetCamera=True):
        """
        Focus the camera on the scene and render the scene to the render window.
        
        @param resetCamera: indicates if the camera has to be resetted
        @type resetCamera: bool
        
        @note: if there is no main actor in the scene and the source volume is
               set, the actor will be created and added to the scene before
               rendering
        """
        print "BEGIN updateRenderWindow"
        # create main actor from volume if possible and necessary
        self.__createMainActor()
        print "main actor created"
        
        # Reset camera if necesarry
        if resetCamera:
            self.renderer.ResetCamera()
        self.refreshRenderWindow()
        print "END updateRenderWindow"

#}

#{ Export methods
    
    def exportPipeline(self, filename):
        """
        Export an XML representation of the L{pipeline} to a file.
        
        @param filename: the name of the file
        @type filename: str
        """
        self.__pipeline.writeXMLtoFile(filename)
    
    def __exportToVtkExporter(self, vtkExporterObj, filename):
        """
        Export the rendered scene to a file.
        
        @param vtkExporterObj: exporter of the scene to requested file format
        @type vtkExporterObj: vtkExporter
        
        @param filename: the name of the file
        @type filename: str
        """
        self.updateRenderWindow(resetCamera=False)
        vtkExporterObj.SetRenderWindow(self.renWin)
        vtkExporterObj.SetFileName(filename)
        vtkExporterObj.Write()
    
    def exportToVRML(self, filename):
        """
        Export the rendered scene to a VRML file.
        
        @param filename: the name of the file
        @type filename: str
        """
        self.__exportToVtkExporter(vtk.vtkVRMLExporter(), filename)
    
    def exportToX3d(self, filename):
        """
        Export the rendered scene to an X3D file.
        
        @param filename: the name of the file
        @type filename: str
        """
        self.__exportToVtkExporter(vtk.vtkX3DExporter(), filename)

    def exportToPOVRay(self, filename):
        """
        Export the rendered scene to a POV-Ray file.
        
        @param filename: the name of the file
        @type filename: str
        
        @note: some VTK revisions do not implement necessary
               C{vtk.vtkPOVExporter.SetFileName} method
        """
        try:
            self.__exportToVtkExporter(vtk.vtkPOVExporter(), filename)
        except AttributeError:
            print "UPS... vtk.vtkPOVExporter implementation problem."
    
    def exportScreenshot(self, filename):
        """
        Save screenshot of the render window into a PNG file.
        
        @param filename: the name of the file
        @type filename: str
        """
        self.updateRenderWindow()
        w2i = vtk.vtkRenderLargeImage()
        writer = vtk.vtkPNGWriter()
        w2i.SetMagnification(2)
        w2i.SetInput(self.renderer)
        w2i.Update()
        writer.SetInputConnection(w2i.GetOutputPort())
        writer.SetFileName(filename)
        writer.Write()

    def exportThumbnail(self, filename):
        """
        Save scaled screenshot of the render window into a PNG file.
        
        @param filename: the name of the file
        @type filename: str
        """
        self.exportScreenshot(filename)
        Thumbnail.open(filename).getthumbnail().save(filename)

    def __exportToVtkDataExporter(self, vtkDataWriterObj, data, filename):
        """
        Export the reconstruction to a file.
        
        @param data: the reconstruction
        
        @param vtkDataWriterObj: the writer of VTK data to the requested file
                                 format
        @type vtkDataWriterObj: vtkDataWriter object
        
        @param filename: the name of the file
        @type filename: str
        """
        vtkDataWriterObj.SetInput(data)
        vtkDataWriterObj.SetFileName(filename)
        vtkDataWriterObj.SetFileTypeToBinary()
        vtkDataWriterObj.Write()
    
    def exportToVolume(self, filename):
        """
        Export the reconstructed volume to a VTKstructGrid file.
        
        @param filename: the name of the file
        @type filename: str
        """
        self.__exportToVtkDataExporter(vtk.vtkStructuredPointsWriter(),
                                       self.vtkVolume.GetOutput(),
                                       filename)
    
    def exportToVTKPolydata(self, filename):
        """
        Export the reconstructed mesh to a VTKpolyMesh file.
        
        @param filename: the name of the file
        @type filename: str
        """
        self.__exportToVtkDataExporter(vtk.vtkPolyDataWriter(),
                                       self.vtkMesh.GetOutput(),
                                       filename)
    
    def exportToNiftii(self, filename):
        """
        Export the reconstructed volume to a Niftii file.
        
        @param filename: the name of the file
        @type filename: str
        """
        vtkVolume = self.vtkVolume.GetOutput()
        nim = nifti.NiftiImage(VTKtoNumpy(vtkVolume))
        nim.setVoxDims(list(vtkVolume.GetSpacing()))
        h = nim.header
        h['qoffset'] = list(vtkVolume.GetOrigin())
        h['qform_code'] =1
        
        #Print header in debug mode
        if __debug__: print sys.stderr, h
        
        nim.header = h
        # http://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/nifti1fields_pages/qsform.html
        nim.save(filename)
    
    def exportToNumpy(self, filename):
        """
        Export the reconstructed volume as an 3D array to a Numpy file.
        
        @param filename: the name of the file
        @type filename: str
        """
        numpyVolume = VTKtoNumpy(self.vtkVolume.GetOutput())
        np.save(filename, numpyVolume)

#}

#{ Property access methods
    
    def __getCameraPosition(self):
        """
        The L{cameraPosition} property getter.
        """
        camera = self.renderer.GetActiveCamera()
        position = camera.GetPosition()
        fp = camera.GetFocalPoint()
        return tuple(map(lambda x, y: x - y, position, fp))
    
    def __setCameraPosition(self, position, fp = (0., 0., 0.)):
        """
        The L{cameraPosition} property setter.
        """
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(position)
        camera.SetFocalPoint(fp)
    
    def __setCameraViewUp(self, top):
        """
        The L{top} property setter.
        """
        camera = self.renderer.GetActiveCamera()
        camera.SetViewUp(top)
    
    def __getCameraViewUp(self):
        """
        The L{top} property getter.
        """
        camera = self.renderer.GetActiveCamera()
        return tuple(camera.GetViewUp())
    
    def __getPipeline(self):
        """
        The L{pipeline} property getter.
        """
        return self.__pipeline
    
    def __setPipeline(self, newPipeline):
        """
        The L{pipeline} property setter.
        
        The pipeline is stored in the object as:
          - L{__pipeline},
          - L{__volumePipeline},
          - L{__meshPipeline},
          - L{__finalPipeline}.
        """
        self.__pipeline = newPipeline
        
        types = self.__pipeline.getOutputDataTypes()
        volumePipeIdx = types['vtkImageData']
        polyDataPipeIdx = types['vtkPolyData']
        self.__volumePipeline = self.__pipeline[slice(*volumePipeIdx)]
        self.__meshPipeline   = self.__pipeline[slice(*polyDataPipeIdx)]
        self.__finalPipeline  = self.__pipeline[-1:]
        self.__clearCache()
    
    def __getVtkVolume(self):
        """
        The L{vtkVolume} property getter.
        """
        if self.__sourceVolume == None:
            raise ValueError, 'no source volume has been provided'
        if self.__vtkVolume == None:
            self.__vtkVolume = self.__volumePipeline.execute(\
                                    self.__sourceVolume)
        return self.__vtkVolume
    
    def __setVtkVolume(self, value):
        """
        The L{vtkVolume} property setter.

        When called raises L{ValueError}.
        """
        raise ValueError, 'vtkVolume is a read-only property'
    
    def __getVtkMesh(self):
        """
        The L{vtkMesh} property getter.
        """
        if self.__vtkMesh == None:
            self.__vtkMesh = self.__meshPipeline.execute(self.vtkVolume)
        return self.__vtkMesh
    
    def __setVtkMesh(self, value):
        """
        The L{vtkMesh} property setter.
        
        When called raises L{ValueError}.
        """
        raise ValueError, 'vtkMesh is a read-only property'

    def __setBackground(self, background):
        """
        Background colour setter.

        @type background: (float, float, float)
        @param background: RGB components of background colour
        """
        self.renderer.SetBackground(background)

    def __getBackground(self):
        """
        @return: RGB components of background colour
        @rtype: (float, float, float)
        """
        return tuple(self.renderer.GetBackground())

#}

    pipeline = property(__getPipeline, __setPipeline)
    """
    The reconstruction pipeline used by the object.
    
    The pipeline is composed of three parts:
      1. volume processing pipeline (ends with the last filter returning
         vtkImageData object),
      2. mesh processing pipeline (ends with the last filter returning
         vtkPolyData object)
      3. actor creating pipeline (mapper element of the pipeline - usually
         vtkPpolyDataMapper) 
    """
    
    cameraPosition = property(__getCameraPosition, __setCameraPosition)
    """
    The direction from the center of the scene to the camera position.
    """

    cameraViewUp = property(__getCameraViewUp, __setCameraViewUp)
    """
    The "up" direction.
    """
    
    vtkVolume = property(__getVtkVolume, __setVtkVolume)
    """
    The result of execution of the volume processing part of the L{pipeline}
    on the reconstruction source volume.
    
    @note: the results are cached
    @note: read-only property
    """
    
    vtkMesh = property(__getVtkMesh, __setVtkMesh)
    """
    @note: read-only property
    """

    background = property(__getBackground, __setBackground)
    """
    RGB components of background colour.

    @type: (float, float, float)
    """
