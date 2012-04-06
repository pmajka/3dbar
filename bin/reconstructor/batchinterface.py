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
The module provides the L{barBatchReconstructor} class for performing the
batch reconstruction process of structures from CAF datasets.

If run as a script, performs requested reconstructions of requested structures
from given CAF dataset. Run with C{--help} argument for details.

G{importgraph}
"""

import sys
import time
from optparse import OptionParser, OptionGroup
from bar.color import floatColourToInt
from bar.rec.barreconstructor import barReconstructionModule, SCENE_EXPORT_FORMAT_MASK,\
                                     BAR_RECONSTRUCTOR_VERSION, BAR_RENDERER_BACKGROUND

BAR_DESCRIPTION = "3d Brain Atlas Reconstructor ver." + BAR_RECONSTRUCTOR_VERSION + " Batch reconstruction interface\n"

class batchInterface(object):
    """
    Class providing the commandline interface for L{barBatchReconstructor} class.

    @cvar output_format: possible output formats description as a three of:
                         commandline switch, L{barReconstructionModule} class
                         export method, commandline switch description
    @type output_format: [(str, str, str), ...]

    @cvar usage: commandline syntax
    @type usage: str

    @cvar delay: delay (in seconds) between displaying requested reconstruction
                 parameters and the start of reconstruction process
    @type delay: int

    @ivar structures: list of roots of hierarchy subtrees to be reconstructed
    @type structures: [str, ...]

    @ivar rm: reconstructor object
    @type rm: L{reconstructorClass<batchInterface.reconstructorClass>}

    @ivar options: an object containing
                   L{reconstructorClass<batchInterface.reconstructorClass>}
                   constructor options
    @type options: optparse.Values object

    @ivar index: the path to a CAF dataset index file
    @type index: str

    @ivar reconstructorClass: class of L{self.rm<batchInterface.rm>} object
    @type reconstructorClass: class

    @ivar parser: commandline arguments parser
    @type parser: optparse.OptionParser
    """
    output_format = [('exportToX3d', 'exports as X3D scene'),
                     ('exportToVRML', 'exports as VRML scene'),
                     ('exportToPOVRay', 'exports to POV-Ray'),
                     ('exportToVTKPolydata', 'exports as VTKpolyMesh'),
                     ('exportToVolume', 'exports as VTKstructGrid'),
                     ('exportToNiftii', 'exports as Niftii file'),
                     ('exportToNumpy', 'exports as Numpy array'),
                     ('exportScreenshot', 'saves screenshot as an PNG image'),
                     ('exportThumbnail', 'saves scaled screenshot as an PNG image')]

    description = BAR_DESCRIPTION
    usage = "./batchinterface.sh [options] <CAF index> [<structure 1> [<structure 2> ...]]"
    version = BAR_RECONSTRUCTOR_VERSION
    
    # Determines, how many second script waits before launching the reconstruction
    # process
    delay = 1
    
    def __init__(self, reconstructorClass):
        self.structures = None
        self.rm = None
        self.options = None
        self.index = None
        self.reconstructorClass = reconstructorClass

        parser = OptionParser(usage=self.usage,description=self.description,version=self.version)
        parser.add_option('--generateSubstructures', '-g',
                          type='int', dest='generateSubstructures', default=0,
                          help='maximum level of substructures (in the structure tree) to be generated; defaults to 0')
        parser.add_option('--voxelDimensions', '-d', type='float',
                          nargs=2, dest='voxelDimensions',
                          help='voxel size [mm] (in coronal plane, along anterior-posterior axis)')
        parser.add_option('--exportDir', '-e', dest='exportDir',
                          help='the path to a directory for reconstructions')
        parser.add_option('--usePipeline', '-p', dest='pipeline',
                          help='the path to a custom pipeline definition')
        parser.add_option('--cameraMovementAngles', '-a', type='float', nargs=3, dest='cameraMovementAngles',
                          default=(0.0, 0.0, 0.0),
                          help='camera movement angles (azimuth, elevation, roll)')
        parser.add_option('--background', '-b', type='float', nargs=3, dest='background',
                          default=floatColourToInt(BAR_RENDERER_BACKGROUND),
                          help='RGB background colourcomponents (within 0.0-255.0 range)')
        
        formatOptions = OptionGroup(parser, 'Output Format Switches')
        for (keyword, description) in self.output_format:
            formatOptions.add_option('--'+keyword, action='append_const',
                                     const=keyword, dest='format', help=description)
        parser.add_option_group(formatOptions)
        parser.add_option('--exportToWindow', '--show', action='store_const',
                          const=True, dest='show', default=False,
                          help='the reconstruction is displayed to the user')
        parser.add_option('--composite', action='store_const',
                          const=True, dest='composite', default=False,
                          help='perform a reconstruction of the structure as a scene composed of the reconstructions of the basic substructures in the hierarchy tree (up to the maximum given level)')
        parser.add_option('--includeBrainOutline', action='store_const',
                          const=True, dest='brainoutline', default=False,
                          help='Includes additional translucent brain outline to the reconstructions. Applies only when exporting to VRML, X3D or thumbnail.')
        parser.add_option('--ignoreBoundingBox', action='store_const',
                          const=True, dest='ignoreBoundingBox', default=False,
                          help='Overrides bounding box calculation - bounding\
                          box will be always equal to hierarchy root element\
                          bounding box. Volumes for all structures will always\
                          have the same size and origin. This feature increases\
                          memory usage and reconstruction time.')
        self.parser = parser
    
    
    def parseArgs(self):
        """
        Parse script arguments.

        @return: (options, args)
        @rtype: (optparse.Values object, [str, ...])

        @note: The method exits if parse failed or requested to display help.
        """
        (options, args) = self.parser.parse_args()
        if len(args) == 0:
            self.parser.print_help()
            exit()
        return (options, args)
    
    def printParameters(self):
        """
        Print the parameters of the reconstruction.
        """
        print "CAF:", self.index
        print "Structures for reconstruction:", ', '.join(self.structures)
        print
        print "Options:"
        print "  --generateSubstructures:", self.rm.depth
        print "  --voxelDimensions:", self.rm.xyres, self.rm.zres
        print "  --exportDir:", self.rm.exportDir
        if self.options.pipeline != None:
            print "  --usePipeline:", self.options.pipeline
        else:
            print "    DEFAULT PIPELINE"
        print "  --cameraMovementAngles: %f %f %f" % self.rm.cameraMovementAngles
        print "Output:"
        for (keyword, description) in self.output_format:
            if keyword in self.rm.formats:
                print "    --%s" % keyword
        if self.rm.show:
            print "  --exportToWindow"
        if self.rm.composite:
            print "  --composite"
        if self.rm.brainoutline:
            print "  --includeBrainOutline"
        print
    
    def setup(self):
        """
        Prepare everything for reconstruction.
        """
        # parse the arguments
        self.options, args = self.parseArgs()
        vtkapp = barReconstructionModule()
        self.index = args[0]
        self.structures = args[1:]
        
        # create the reconstructor
        self.rm = self.reconstructorClass(vtkapp, self.index, self.options)

        self.printParameters()
    
    def waitDelay(self):
        """
        Wait L{delay} seconds allowing user to review reconstruction settings
        and, if needed, stop the process before it starts.
        
        @note: assumed call to the function just before the reconstruction starts.
        """
        print "Reconstruction is starting in %d seconds. Press Ctrl-C to stop." % self.delay
        print "To reconstruction start:",
        
        for toGo in reversed(xrange(1, self.delay + 1)):
            print toGo,
            sys.stdout.flush()
            time.sleep(1)
        print 0

    def main(self):
        """
        Handle the reconstruction process.
        """
        self.setup()
        self.waitDelay()
        self.rm.prepareLoop(self.structures)
        self.rm.runLoop()



