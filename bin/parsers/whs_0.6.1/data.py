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

import datetime

CONF_PARSER_COMMENT = 'CAF dataset based on: \
<a href="http://software.incf.org/software/waxholm-space/home"\
target="_blank">Waxholm Space</a>, a coordinate-based reference space for the\
mapping and registration of neuroanatomical data in the mouse brain.<br/>\
See <a href="http://www.ncbi.nlm.nih.gov/pubmed/20600960" target="_blank">\
G.Johnson, et. al., NeuroImage 53 (2010) 365-372</a>, Delineation 0.6.1'
CONF_PARSER_NAME    = 'whs_0.6.1'
CONF_CONTACT_COMMENT= 'Piotr Majka, Nencki Institute of Experimental Biology'
CONF_CONTACT_EMAIL  = 'pmajka@nencki.gov.pl'
CONF_CAF_COMPIL_TIME= datetime.datetime.utcnow().strftime("%F %T")
CONF_CAF_FULL_NAME = 'The Waxholm Space - mouse brain reference space, delineation 0.6.1'

REFERENCE_WIDTH = 512
REFERENCE_HEIGHT = 512

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
renderingProperties['imageSize']       = (REFERENCE_WIDTH*2, REFERENCE_HEIGHT*2)

potraceProperties    = {}
potraceProperties['potrace_accuracy_parameter']   ='0.5'
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
('backgroundColor', (255,255,255)),
('filenameTemplates', filenameTempates),
('renderingProperties', renderingProperties),
('tracingProperties', tracerSettings),
('slideTemplate', tracedSlideTemplate)]

indexerProperties = dict([
('Genus', 'Mus'),
('Species', 'Mus musculus'),
('Strain', 'C57BL/6'),
('Age', '66-78 days'),
('Sex', 'male'),
('Source', 'http://www.sciencedirect.com/science/article/pii/S1053811910009274'),
('Language', 'En'),
('SRSCode', 'INCF:0002'),
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
