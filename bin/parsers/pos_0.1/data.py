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

CONF_PARSER_COMMENT = 'CAF dataset based on: \
<a href="http://put_the_url_of_the_opossum_segmentation" target="_blank">\
pos_template</a>'
CONF_PARSER_NAME    = 'pos_0.1'
CONF_CONTACT_COMMENT= 'Piotr Majka, Nencki Institute of Experimental Biology'
CONF_CONTACT_EMAIL  = 'pmajka@nencki.gov.pl'
CONF_CAF_COMPIL_TIME= datetime.datetime.utcnow().strftime("%F %T")
CONF_CAF_FULL_NAME = 'Stereotaxic multimodal template of the gray-short tailed opossum (monodelphis domestica).'

REFERENCE_WIDTH = 320
REFERENCE_HEIGHT = 250
voxelSize = 0.05

# ax+b, cy+d
a, b, c, d = -voxelSize, 8.05, -voxelSize, 1.05
spatialTransformationMatrix= (a,b,c,d)
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
('Species', '<i>Monodelphis domestica</i>'),
('Strain', 'outbred'),
('Age', '1 year (xxx) days'),
('Sex', 'male'),
('Source', 'url_to_the_segmentaion'),
('Language', 'En'),
('Licencing', '<a rel="license" href="http://creativecommons.org/licenses/by-nc/3.0/deed.pl" target="_blank"><img alt="Licencja Creative Commons" style="border-width:0" src="http://i.creativecommons.org/l/by-nc/3.0/80x15.png" /></a>'),
('SourceLicencing', 'CC-BY put details'),
('SRSCode', '-'),
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
