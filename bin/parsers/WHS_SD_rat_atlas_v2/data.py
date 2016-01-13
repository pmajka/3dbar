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

import datetime

CONF_PARSER_COMMENT = """CAF dataset based on: \
<a href="http://software.incf.org/software/waxholm-space-atlas-of-the-sprague-dawley-rat-brain/waxholm-space-atlas-of-the-sprague-dawley-rat-brain-package/quick-pack/mbat-ready-sprague-dawley-atlas-v2-bundle/at_download/file" target="_blank">\
Waxholm Space atlas of the Sprague Dawley rat brain</a>: \
Papp, E.A., Leergaard, T.B., Calabrese, E., Johnson, G.A., & Bjaalie, J.G. (2014). <i>NeuroImage Waxholm Space atlas of the Sprague Dawley rat brain</i>. NeuroImage, 97, 374–386. http://doi.org/10.1016/j.neuroimage.2014.04.001"""

CONF_PARSER_NAME    = 'WHS_SD_rat_atlas_v2'
CONF_CONTACT_COMMENT= 'Piotr Majka, Nencki Institute of Experimental Biology'
CONF_CONTACT_EMAIL  = 'pmajka@nencki.gov.pl'
CONF_CAF_COMPIL_TIME= datetime.datetime.utcnow().strftime("%F %T")
CONF_CAF_FULL_NAME = 'Waxholm Space atlas of the Sprague Dawley rat brain, version 2'

REFERENCE_WIDTH = 512
REFERENCE_HEIGHT = 512

# The values below are tweaked values which are automatically
# extrated from the niftii file, but these are slightly modified
# for better reconstruction accuracy
# a * x + b, c * y + d
voxelSize = 0.0390625
a, b, c, d = voxelSize, -9.53240414, -voxelSize, 10.31178775
spatialTransformationMatrix = (a,b,c,d)
alignerCoordinateTuple = (b,d,a,c)

C_HIERARCHY_ROOT_ELEMENT_ABBREV = 'Brain-region-hierarchy'
C_HIERARCHY_ROOT_ELEMENT_FULLNAME = 'Brain region hierarchy'

tracedSlideTemplate = """<?xml version="1.0" ?><svg baseProfile="full" height="%d" id="body"
preserveAspectRatio="none" version="1.1" viewBox="0 0 %d %d"
width="%d" xmlns="http://www.w3.org/2000/svg"
xmlns:ev="http://www.w3.org/2001/xml-events"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:bar="http://www.3dbar.org">

<title></title>
<desc></desc>

<defs></defs>

<g id='content'>
</g>

</svg>
""" % (REFERENCE_HEIGHT, REFERENCE_WIDTH, REFERENCE_HEIGHT, REFERENCE_WIDTH)

filenameTempates = dict(traced='%d_traced_v%d.svg')

renderingProperties = {}
renderingProperties['ReferenceWidth']  = REFERENCE_WIDTH
renderingProperties['ReferenceHeight'] = REFERENCE_HEIGHT
renderingProperties['imageSize']       = (REFERENCE_WIDTH*16, REFERENCE_HEIGHT*16)

potraceProperties    = {}
potraceProperties['potrace_accuracy_parameter']   ='0.001'
potraceProperties['potrace_svg_resolution_string']='300x300'
potraceProperties['potrace_width_string']   =      '%dpt' % REFERENCE_WIDTH
potraceProperties['potrace_height_string']  =      '%dpt' % REFERENCE_HEIGHT

tracerSettings={}
tracerSettings['DumpEachStepSVG']          = False
tracerSettings['DumpEachStepPNG']          = False
tracerSettings['DumpWrongSeed']            = True
tracerSettings['DumpVBrain']               = False
tracerSettings['DumpDirectory']            = '.'
tracerSettings['DetectUnlabelled']         = False
tracerSettings['CacheLevel']               = 5
tracerSettings['MinFiterTimesApplication'] = 3
tracerSettings['GrowDefaultBoundaryColor'] = 200
tracerSettings['RegionAlreadyTraced']      = 100
tracerSettings['UnlabelledTreshold']       = 500
tracerSettings['PoTraceConf'] = potraceProperties
tracerSettings['NewPathIdTemplate'] = 'structure%d_%s_%s'

atlasparserProperties=[
('backgroundColor', (0, 0, 0)),
('filenameTemplates', filenameTempates),
('renderingProperties', renderingProperties),
('tracingProperties', tracerSettings),
('slideTemplate', tracedSlideTemplate)]

indexerProperties = dict([
('Genus', 'Rattus'),
('Species', 'Rattus norvegicus'),
('Strain', 'Sprague Dawley'),
('Age', 'adult, postnatal day 80, mass: 397.6g'),
('Sex', 'male'),
('Source', 'http://software.incf.org/software/waxholm-space-atlas-of-the-sprague-dawley-rat-brain/waxholm-space-atlas-of-the-sprague-dawley-rat-brain-package/quick-pack/mbat-ready-sprague-dawley-atlas-v2-bundle/at_download/file'),
('Language', 'En'),
('Licencing', '<a rel="license" href="http://creativecommons.org/licenses/by-nc/3.0/deed.pl" target="_blank"><img alt="CC-BY-NC-SA" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/80x15.png" /></a>'),
('SourceLicencing', ' CC-BY-NC-SA (<a href="http://software.incf.org/software/waxholm-space-atlas-of-the-sprague-dawley-rat-brain" target="_blank">see details</a>)'),
('ReferenceWidth', str(REFERENCE_WIDTH)),
('ReferenceHeight', str(REFERENCE_HEIGHT)),
('FilenameTemplate',filenameTempates['traced']),
('CAFSlideOrientation', 'coronal'),
('CAFSlideUnits', 'mm'),
('CAFName', CONF_PARSER_NAME),
('CAFFullName', CONF_CAF_FULL_NAME),
('CAFComment', CONF_PARSER_COMMENT),
('CAFCreator', CONF_CONTACT_COMMENT),
('CAFCreatorEmail', CONF_CONTACT_EMAIL),
('CAFCompilationTime',CONF_CAF_COMPIL_TIME),
('CAFAxesOrientation', 'RSA')])
