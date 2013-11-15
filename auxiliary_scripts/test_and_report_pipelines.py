#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from optparse import OptionParser, OptionGroup
import sys
import os

from bar.rec.formats import BAR_EXPORT_FORMAT_INFO

from volume_comparison import cafStructureLines

VIEWPORT=" --cameraMovementAngles -45.126941 23.103881 121.881318 "


class pipelineLinePattern(cafStructureLines):
    _linePattern = 'echo "%(dir3dbar)s/batchinterface.sh %(dir3dbar)s/atlases/%(cafName)s/caf/index.xml %%s -p %(dir3dbar)s/auxiliary_scripts/pipelines/%%%%(pipeline)s.xml -e $PIPELINE_DIR %%%%%%%%(options)s" >> ${JOB_TEMP_RC}'


class reportGenerator(object):
    def __init__(self, formats):
        self.__formats = formats

    def __str__(self):
        result = []
        for f in self.__formats:
            pattern = BAR_EXPORT_FORMAT_INFO[f]['template'] % '*'
            zipName = (BAR_EXPORT_FORMAT_INFO[f]['template'] % f) + '.zip'
            desc = BAR_EXPORT_FORMAT_INFO[f]['desc']
            result.append('echo -e "%s size:\t` filesSize $PIPELINE_DIR/%s`" >> $REPORTFILE' % (desc, pattern))
            result.append('zip -m $PIPELINE_DIR/%s $PIPELINE_DIR/%s' % (zipName, pattern))
            result.append('echo -e "%s (compressed) size:\t` filesSize $PIPELINE_DIR/%s`" >> $REPORTFILE' % (desc, zipName))

        result.append('echo -e "Numer of reconstructions:\t`wc -l $JOB_TEMP_RC`" >> $REPORTFILE')
        return '\n'.join(result)


class scriptGenerator(object):
    __scriptTemplate = """#!/bin/bash
set -xe
export DISPLAY=:0.0;

function filesSize {
local size=`ls -lS --block-size=1 $* \
    | awk '{print $5,$6,$7,$8,$9}' \
    | awk '{sum = sum + $1} END {print sum/(1024*1024)}'`
echo ${size}
}

%s
"""

    __linePattern = """# BEGIN %%(pipeline)s

PIPELINE_DIR=`pwd`/pipeline_test_`date +"%%%%%%%%Y-%%%%%%%%m-%%%%%%%%d"`/%%(pipeline)s_`date +%%%%%%%%s`/
mkdir -p $PIPELINE_DIR

LOGFILE=${PIPELINE_DIR}/log.txt
REPORTFILE=${PIPELINE_DIR}/report.txt
JOB_TEMP_RC=${PIPELINE_DIR}/job.sh

rm -vf $LOGFILE
rm -vf $REPORTFILE
rm -vf $JOB_TEMP_RC

%(generateJob)s

cat $JOB_TEMP_RC | %(executionCommand)s > $LOGFILE

%(generateReport)s

# END %%(pipeline)s"""

    def __init__(self, dir3dbar, cafName, pipelines, formats, command, res):
        self.__dir3dbar = dir3dbar
        self.__pipelines = pipelines
        options = [VIEWPORT] + ['--' + f for f in formats]
        if res != None:
            options.append('-d %f %f' % res)
        self.__options = ' '.join(options)
        self.__pipelineLine = self.__linePattern % {'generateJob': pipelineLinePattern(dir3dbar, cafName),
                                                    'generateReport': reportGenerator(formats),
                                                    'executionCommand': ec}

    def __str__(self):
        lines = [self.__pipelineLine % {'pipeline': p} for p in self.__pipelines]

        scriptTemplate = self.__scriptTemplate % '\n\n'.join(lines)
        return scriptTemplate % {'options': self.__options}


scriptUsage = "%s [options] <3dbar directory> <CAF name> <pipeline 1> [<pipeline 2> [<pipeline 3> ...]]" % sys.argv[0]

output_format = [('exportToX3d', 'exports as X3D scene'),
                 ('exportToVRML', 'exports as VRML scene'),
                 ('exportToPOVRay', 'exports to POV-Ray'),
                 ('exportToVTKPolydata', 'exports as VTKpolyMesh'),
                 ('exportToVolume', 'exports as VTKstructGrid'),
                 ('exportToNiftii', 'exports as Niftii file'),
                 ('exportToNumpy', 'exports as Numpy array'),
                 ('exportScreenshot', 'saves screenshot as an PNG image'),
                 ('exportThumbnail', 'saves scaled screenshot as an PNG image')]

parser = OptionParser(usage=scriptUsage)
parser.add_option('--nCpus', '-c',
                          type='int', dest='nCpus', default=1,
                          help='number of CPUs to be engaged; defaults to 1')

parser.add_option('--voxelDimensions', '-d', type='float',
                  nargs=2, dest='voxelDimensions',
                  help='voxel size [mm] (in coronal plane, along anterior-posterior axis)')

formatOptions = OptionGroup(parser, 'Output Format Switches')
for (keyword, description) in output_format:
    formatOptions.add_option('--'+keyword, action='append_const',
                             const=keyword, dest='format', help=description)

parser.add_option_group(formatOptions)
(options, args) = parser.parse_args()

if len(args) < 3 or options.format == None:
    parser.print_help()
    exit()

ec = 'bash'
if options.nCpus > 1:
    ec = 'parallel -j %d -k' % options.nCpus

dir3dbar = args[0]
cafName = args[1]
pipelines = args[2:]

print scriptGenerator(dir3dbar, cafName, pipelines, options.format, ec, options.voxelDimensions)


#TODO: multiple pipelines, one set; switches


