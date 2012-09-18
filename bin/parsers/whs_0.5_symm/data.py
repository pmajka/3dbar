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
<a
href="http://civmvoxport.duhs.duke.edu/voxbase/downloaddataset.php?stackID=20494"
target="_blank">
<i>A symmetrical Waxholm canonical mouse brain for NeuroMaps.</i></a> by <a href="http://www.ncbi.nlm.nih.gov/pubmed/21163300" target="_blank">Bowden DM, et. al.,</a>.
The original Waxholm Space was introduced by <a href="http://www.ncbi.nlm.nih.gov/pubmed/20600960" target="_blank">Johnson, et. al., 2010</a>.
"""
CONF_PARSER_NAME    = 'whs_0.5_symm'
CONF_CONTACT_COMMENT= 'Piotr Majka, Nencki Institute of Experimental Biology'
CONF_CONTACT_EMAIL  = 'pmajka@nencki.gov.pl'
CONF_CAF_COMPIL_TIME= datetime.datetime.utcnow().strftime("%F %T")
CONF_CAF_FULL_NAME = 'Symmetrical Waxholm Space - mouse brain reference space'

REFERENCE_WIDTH = 512
REFERENCE_HEIGHT = 512

imageToStructure=\
    {\
    "#0a0a0a" : "ac",
    "#212121" : "Acb",
    "#1f1f1f" : "Amy",
    "#141414" : "APT",
    "#020202" : "Bs",
    "#252525" : "cb",
    "#1a1a1a" : "cc",
    "#232323" : "Co",
    "#0d0d0d" : "cp",
    "#010101" : "Cx",
    "#111111" : "DpMe",
    "#191919" : "fi",
    "#1c1c1c" : "Fnx",
    "#0f0f0f" : "GP",
    "#181818" : "Hc",
    "#202020" : "Hyp",
    "#101010" : "ic",
    "#050505" : "IC",
    "#0e0e0e" : "IP",
    "#121212" : "LD",
    "#060606" : "ll",
    "#131313" : "MGen",
    "#222222" : "Olf",
    "#151515" : "ot",
    "#070707" : "PAG",
    "#1d1d1d" : "Aq",
    "#0b0b0b" : "Pg",
    "#1e1e1e" : "Pin",
    "#1b1b1b" : "LGen",
    "#040404" : "SC",
    "#080808" : "Sn",
    "#0c0c0c" : "SN",
    "#242424" : "sp5",
    "#171717" : "Str",
    "#030303" : "Th",
    "#161616" : "VS",
    "#090909" : "VT",
    "#ffffff" : "bcg"}

voxelSize = 0.0215
# ax+b, cy+d
# for some reason d ccoeff has to be 5.590 instead of 5.5685 (wchich is a reault
# of calculations) - difference of a single voxel
a, b, c, d = voxelSize, -5.504, -voxelSize, 5.5685+voxelSize
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

filenameTempates = dict(traced='%d_traced_v%d.svg')

renderingProperties = {}
renderingProperties['ReferenceWidth']  = REFERENCE_WIDTH
renderingProperties['ReferenceHeight'] = REFERENCE_HEIGHT
renderingProperties['imageSize']       = (REFERENCE_WIDTH*1,REFERENCE_HEIGHT*1)

potraceProperties    = {}
potraceProperties['potrace_accuracy_parameter']   ='1.0'
potraceProperties['potrace_svg_resolution_string']='300x300'
potraceProperties['potrace_width_string']   =      '%dpt' % REFERENCE_WIDTH
potraceProperties['potrace_height_string']  =      '%dpt' % REFERENCE_HEIGHT
potraceProperties['potrace_turdsize']       = 60

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
tracerSettings['UnlabelledTreshold']       = 200
tracerSettings['PoTraceConf'] = potraceProperties
tracerSettings['NewPathIdTemplate'] = 'structure%d_%s_%s'

atlasparserProperties=(
('backgroundColor', (255,255,255)),
('imageToStructure', imageToStructure),
('filenameTemplates', filenameTempates),
('renderingProperties', renderingProperties),
('tracingProperties', tracerSettings),
('slideTemplate', tracedSlideTemplate))

indexerProperties = dict([
('Genus', 'Mus'),
('Species', 'Mus musculus'),
('Strain', 'C57BL/6'),
('Age', '66-78 days'),
('Sex', 'male'),
('Source', 'http://www.ncbi.nlm.nih.gov/pubmed/21163300'),
('Language', 'En'),
('Licencing', '<a rel="license" href="http://creativecommons.org/licenses/by-nc/3.0/deed.pl" target="_blank"><img alt="Licencja Creative Commons" style="border-width:0" src="http://i.creativecommons.org/l/by-nc/3.0/80x15.png" /></a>'),
('SourceLicencing', ' CC-BY (<a href="http://software.incf.org/software/waxholm-space/home" target="_blank">see details</a>)'),
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
