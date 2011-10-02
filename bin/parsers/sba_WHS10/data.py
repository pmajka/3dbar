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
###############################################################################
##                                                                           ##
##                   Configuration for WHS10 template                        ##
##               Mouse - Waxholm Space delineation 2010                      ##
##   template soure: http://scalablebrainatlas.incf.org/WHS10/template/      ##
##                                                                           ##
###############################################################################

import datetime

CONF_PARSER_COMMENT = 'CAF dataset (Waxholm Space for the mouse 2010) based on: \
Scalable Brain Atlas \
<a href="http://scalablebrainatlas.incf.org/main/coronal3d.php?template=WHS10" target="_blank">\
WHS10</a> template.'
CONF_PARSER_NAME = 'sba_WHS10'
CONF_CONTACT_COMMENT = 'Piotr Majka, Nencki Institute of Experimental Biology.'
CONF_CONTACT_EMAIL = 'pmajka@nencki.gov.pl'
CONF_CAF_COMPIL_TIME = datetime.datetime.utcnow().strftime("%F %T")
CONF_CAF_FULL_NAME = 'ScalableBrainAtlas: Mouse - Waxholm Space delineation 2010'

REFERENCE_WIDTH = 1417.74777
REFERENCE_HEIGHT = 1417.74777

slideRange = range(0,176)

alignerCoordinateTuple =\
    ( -5.4770870759, 4.7801952164, 0.007118290, -0.007118225)

filenameTempates = dict(traced='%d_traced_v%d.svg')

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
renderingProperties['imageSize']       = (REFERENCE_WIDTH  * 3, REFERENCE_HEIGHT * 3)

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

templateName = 'WHS10'
templateUrl=\
        "http://scalablebrainatlas.incf.org/WHS10/template/%s"

jsonFilelist=\
        {'svgpaths':'svgpaths.json', 'brainregions':'brainregions.json',
        'brainslices':'brainslices.json', 'rgb2acr':'rgb2acr.json',
        'config':'config.json', 'bregma':'slicepos.json'}

indexerProps = dict([\
        ('Genus', 'Mus'),
        ('Species', 'Mus musculus'),
        ('Strain', 'C57BL/6'),
        ('Age', '66-78 days'),
        ('Sex', 'male'),
        ('Source','http://scalablebrainatlas.incf.org/main/coronal3d.php?template=WHS10'),
        ('Language', 'En'),
        ('SRSCode', 'INCF:0002'),
        ('ReferenceWidth', str(REFERENCE_WIDTH)),
        ('ReferenceHeight', str(REFERENCE_HEIGHT)),
        ('FilenameTemplate', str('%d_traced_v%d.svg')),
        ('RefCords', '-5.4770870759, 4.7801952164, 0.007118290, -0.007118225'),
        ('CAFSlideOrientation', 'coronal'),
        ('CAFSlideUnits', 'mm'),
        ('CAFName', CONF_PARSER_NAME),
        ('CAFFullName', CONF_CAF_FULL_NAME),
        ('CAFComment', CONF_PARSER_COMMENT),
        ('CAFCompilationTime', CONF_CAF_COMPIL_TIME),
        ('CAFCreator', CONF_CONTACT_COMMENT),
        ('CAFCreatorEmail', CONF_CONTACT_EMAIL)])

hierarchyRootElementName = 'Brain'
