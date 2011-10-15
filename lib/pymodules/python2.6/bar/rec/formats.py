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
The module provides basic information about availiable export formats.

G{importgraph}

@var SCENE_EXPORT_FORMAT_MASK: the mask of formats allowing to export a scene
                               ("allowing to" is not "dedicated to")
@type SCENE_EXPORT_FORMAT_MASK: frozenset([str, ...])
"""

#TODO: documentation

BAR_SCENE_TEMPLATE = 'scene_%s'
BAR_VOLUME_TEMPLATE = 'volume_%s'

BAR_EXPORT_FORMATS = [('exportToVRML', 'VRML files', '.wrl', BAR_SCENE_TEMPLATE),
                      ('exportToX3d', 'X3D files', '.x3d', BAR_SCENE_TEMPLATE),
                      ('exportToPOVRay', 'POV-Ray files', '.pov', BAR_SCENE_TEMPLATE),
                      ('exportToNiftii', 'NIfTI files', '.nii.gz', BAR_VOLUME_TEMPLATE),
                      ('exportToVTKPolydata', 'vtk polydata files', '.vtk', 'model_%s'),
                      ('exportToNumpy', 'NumPy array files', '.npy', BAR_VOLUME_TEMPLATE),
                      ('exportToVolume', 'vtk structured grid files', '.vtk', BAR_VOLUME_TEMPLATE),
                      ('exportScreenshot', 'PNG images', '.png', 'screenshot_%s'),
                      ('exportThumbnail', 'PNG thumbnails', '.png', 'thumbnail_%s'),
                      ('exportToWindow', None, '', '%s'),
                      ('exportPipeline', 'pipeline files', '.xml', 'pipeline_%s')]


def getFormatInfo(formats=None):
    """
    Return descriptions of requested formats.

    Description is a dictionary containing keys:
    - C{'desc'} for text describing the format,
    - C{'ext'} for the format filename suffix,
    - C{'template'} for default output filename template.

    @param formats: requested formats; if not given - all formats are requested
    @type formats: set([str, ...])

    @return: format name to its description mapping
    @rtype: {str: {str: str}, ...}
    """
    if formats == None:
        formats = set(row[0] for row in BAR_EXPORT_FORMATS)

    formatInfo = {}
    for (method, description, extension, template) in BAR_EXPORT_FORMATS:
        if method in formats:
            formatInfo[method] = {'desc': description,
                                  'ext': extension,
                                  'template': template + extension}
    return formatInfo

BAR_EXPORT_FORMAT_INFO = getFormatInfo()

BAR_EXPORT_VOLUME_FORMATS = getFormatInfo(frozenset(['exportToNiftii',
                                                     'exportToNumpy',
                                                     'exportToVolume']))

BAR_EXPORT_SCENE_FORMATS = getFormatInfo(frozenset(['exportToVRML',
                                                    'exportToX3d',
                                                    'exportToPOVRay']))

SCENE_EXPORT_FORMAT_MASK = frozenset(['exportToVRML',
                                      'exportToX3d',
                                      'exportToPOVRay',
                                      'exportThumbnail',
                                      'exportScreenshot']) 

IMAGE_EXPORT_FORMAT_MASK = frozenset(['exportThumbnail',
                                      'exportScreenshot'])

# mapping of export format to default pattern of output filename
BAR_TEMPLATE = dict((method, template + extension)\
                    for (method, description, extension, template)\
                    in BAR_EXPORT_FORMATS)

# filename mask for cached models
BAR_CACHED_MODEL_MASK = BAR_TEMPLATE['exportToVTKPolydata'] % '*'

