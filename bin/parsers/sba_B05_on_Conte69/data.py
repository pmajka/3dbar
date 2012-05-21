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
###############################################################################
##                                                                           ##
##                  Configuration for B05_on_Conte69 template                ##
##         Macaque - parcellation from Markov, Misery, et al. (2011)         ##
## template src: http://scalablebrainatlas.incf.org/B05_on_Conte69/template/ ##
##                                                                           ##
###############################################################################

import datetime

CONF_PARSER_NAME = 'sba_B05_on_Conte69'
CONF_PARSER_COMMENT = 'CAF dataset (Macaque - Brodmann 05 mapped onto the Conte69) based on: \
Scalable Brain Atlas \
<a href="http://scalablebrainatlas.incf.org/main/coronal3d.php?template=B05_on_Conte69" target="_blank">\
B05_on_Conte69</a> template.'
CONF_CONTACT_COMMENT = 'Piotr Majka, Nencki Institute of Experimental Biology.'
CONF_CONTACT_EMAIL = 'pmajka@nencki.gov.pl'
CONF_CAF_COMPIL_TIME = datetime.datetime.utcnow().strftime("%F %T")
CONF_CAF_FULL_NAME = 'ScalableBrainAtlas: Macaque - Brodmann 05 mapped onto the Conte69 (2012)'

REFERENCE_WIDTH = 182.
REFERENCE_HEIGHT = 182.

filenameTempates = dict(traced='%03d_traced_v%d.svg')

# Define filenames for color mapping, fullname mapping and mapping
# from the source volume label index to the soucture's abbreviation.
CONF_FULLNAME_MAPPING_FILE = 'fullname_mapping.txt'
CONF_COLOR_MAPPING_FILE = 'color_mapping.txt'
CONF_VOLUME_LABEL_MAPPING_FILE = 'color_to_abbreviation_mapping.txt'
CONF_VOLUME_LABEL_MAPPING_SOURCE = 'index2acr_Human_Conte69_L_brodmann_paint_to_volume.json'

SOURCE_VOLUME_FILENAME = 'Human_Conte69_L_brodmann_paint_to_volume.nii.gz'

templateName = 'B05_on_Conte69'
templateUrl=\
        "http://scalablebrainatlas.incf.org/B05_on_Conte69/template/%s"

jsonFilelist=\
        {'svgpaths':'svgpaths.json', 'brainregions':'brainregions.json',
         'brainslices':'brainslices.json', 'rgb2acr':'rgb2acr.json',
         'bregma':'slicepos.json', 'config':'config.json', 
         'acr2full' : 'acr2full.json'}

# Just to meed formal SBA parser requirements. Slide range is not used in
# any calculations
slideRange = range(0,160)

origTransformationMatrix =\
        [-91., 110., 1., -1.]

tracedSlideTemplate = """<?xml version="1.0" ?><svg baseProfile="full"
height="%f"
id="body"
preserveAspectRatio="none"
version="1.1"
viewBox="0 0 %f %f"
width="%f"
xmlns="http://www.w3.org/2000/svg"
xmlns:ev="http://www.w3.org/2001/xml-events"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:bar="http://www.3dbar.org">
<title></title>
<desc></desc>

<defs>
</defs>

<g id='content'>
</g>

</svg>
""" % (REFERENCE_HEIGHT, REFERENCE_WIDTH, REFERENCE_HEIGHT, REFERENCE_WIDTH)


potraceProperties    = {}
potraceProperties['potrace_accuracy_parameter']   ='0.001'
potraceProperties['potrace_svg_resolution_string']='300x300'
potraceProperties['potrace_width_string']   =      '%fpt' % REFERENCE_WIDTH
potraceProperties['potrace_height_string']  =      '%fpt' % REFERENCE_HEIGHT

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

renderingProperties = {}
renderingProperties['ReferenceWidth']  = REFERENCE_WIDTH
renderingProperties['ReferenceHeight'] = REFERENCE_HEIGHT
renderingProperties['imageSize']       = (REFERENCE_WIDTH * 10, REFERENCE_HEIGHT * 10)

indexerProps = dict([\
        ('Source','http://scalablebrainatlas.incf.org/main/coronal3d.php?template=B05_on_Conte69'),
        ('ReferenceWidth', str(REFERENCE_WIDTH)),
        ('ReferenceHeight', str(REFERENCE_HEIGHT)),
        ('FilenameTemplate', str(filenameTempates['traced'])),
        ('RefCords', ",".join(map(str, origTransformationMatrix))),
        ('CAFSlideOrientation', 'coronal'),
        ('CAFSlideUnits', 'mm'),
        ('CAFName', CONF_PARSER_NAME),
        ('CAFFullName', CONF_CAF_FULL_NAME),
        ('CAFComment', CONF_PARSER_COMMENT),
        ('CAFCompilationTime', CONF_CAF_COMPIL_TIME),
        ('CAFCreator', CONF_CONTACT_COMMENT),
        ('CAFCreatorEmail', CONF_CONTACT_EMAIL),
        ('CAFAxesOrientation', 'LSA')])

atlasparserProperties=(
('backgroundColor', 0),
('filenameTemplates', filenameTempates),
('renderingProperties', renderingProperties),
('tracingProperties', tracerSettings),
('slideTemplate', tracedSlideTemplate))

hierarchyRootElementName = 'Brain'
