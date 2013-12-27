#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2013 Piotr Majka, Jakub M. Kowalski                   #
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

CONF_PARSER_COMMENT = 'CAF dataset based on the  P80 data from the Evan Calabrese, Alexandra Badea, Charles Watson, G. Allan Johnson (2013) "A quantitative magnetic resonance histology atlas of postnatal rat brain development with regional estimates of growth and variability.", Neuroimage 71:196-206. 10.1016/j.neuroimage.2013.01.017.'
CONF_PARSER_NAME    = 'CBWJ13_P80'
CONF_CONTACT_COMMENT= 'Piotr Majka, Nencki Institute of Experimental Biology'
CONF_CONTACT_EMAIL  = 'pmajka@nencki.gov.pl'
CONF_CAF_COMPIL_TIME= datetime.datetime.utcnow().strftime("%F %T")
CONF_CAF_FULL_NAME = 'CAF dataset based on the  P80 data from the Evan Calabrese, Alexandra Badea, Charles Watson, G. Allan Johnson (2013) "A quantitative magnetic resonance histology atlas of postnatal rat brain development with regional estimates of growth and variability.", Neuroimage 71:196-206. 10.1016/j.neuroimage.2013.01.017.'

REFERENCE_WIDTH = 680
REFERENCE_HEIGHT = 660
voxelSize = 0.025
coronal_origin_voxel_index = 953
# Origin of the coordinate system in the source volume [953,340,379]

# ax+b, cy+d
a, b, c, d = -voxelSize, 8.5, voxelSize, -9.475
spatialTransformationMatrix = (a,b,c,d)
alignerCoordinateTuple = (b,d,a,c)

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

filenameTempates = dict(traced='%03d_traced_v%d.svg')

renderingProperties = {}
renderingProperties['ReferenceWidth']  = REFERENCE_WIDTH
renderingProperties['ReferenceHeight'] = REFERENCE_HEIGHT
renderingProperties['imageSize']       = (REFERENCE_WIDTH*5, REFERENCE_HEIGHT*5)

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

atlasparserProperties=(
('backgroundColor', (255,255,255)),
('filenameTemplates', filenameTempates),
('renderingProperties', renderingProperties),
('tracingProperties', tracerSettings),
('slideTemplate', tracedSlideTemplate))

indexerProperties = dict([
('Genus', 'Monodelphis'),
('Species', '<i>Rattus norvegicus</i>'),
('Strain', 'Wistar'),
('Age', 'adult, postnatal day 80'),
('Sex', 'male'),
('Source', 'http://civmvoxport.duhs.duke.edu/voxbase/preview.php?tid=B&studyid=208&datasetid=11970'),
('Language', 'En'),
('Licencing', '<a rel="license" href="http://creativecommons.org/licenses/by-nc/3.0/deed.pl" target="_blank"><img alt="Licencja Creative Commons" style="border-width:0" src="http://i.creativecommons.org/l/by-nc/3.0/80x15.png" /></a>'),
('SourceLicencing', 'CC-BY put details'),
('SRSCode', 'SRS origin defined verbally as the "Junction of the rostral and dorsal tangential planes of the anterior commissure with the mid-sagittal plane", which corresponds to voxel [953,340,379] in the original NIFTI dataset (link). See <a href="http://scalablebrainatlas.incf.org/CBWJ13_age_P80/AC_origin.jpg" target="_blank">this image</a> from the  <a href="http://scalablebrainatlas.incf.org" target="_blank">Scalable Brain Atlas website for details</a>'),
('ReferenceWidth', str(REFERENCE_WIDTH)),
('ReferenceHeight', str(REFERENCE_HEIGHT)),
('FilenameTemplate',filenameTempates['traced']),
('RefCords', ",".join(map(str,alignerCoordinateTuple))),
('CAFSlideOrientation', 'coronal'),
('CAFSlideUnits', 'mm'),
('CAFName', CONF_PARSER_NAME),
('CAFFullName', CONF_CAF_FULL_NAME),
('CAFComment', CONF_PARSER_COMMENT),
('CAFCreator', CONF_CONTACT_COMMENT),
('CAFCreatorEmail', CONF_CONTACT_EMAIL),
('CAFCompilationTime',CONF_CAF_COMPIL_TIME),
('CAFAxesOrientation', 'RSA')])
