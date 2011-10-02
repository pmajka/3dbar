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

CONF_PARSER_COMMENT = 'CAF dataset based on Allen Mouse Brain Atlas [Internet]. Seattle (WA): Allen Institute for Brain \
Science. (c) 2009. Available from: \
<a href="http://mouse.brain-map.org/atlas/index.html" target="_blank">http://mouse.brain-map.org</a>.'

CONF_PARSER_NAME = 'aba'
CONF_CONTACT_COMMENT= 'Piotr Majka, Nencki Institute of Experimental Biology.'
CONF_CONTACT_EMAIL = 'pmajka@nencki.gov.pl'
CONF_CAF_COMPIL_TIME = datetime.datetime.utcnow().strftime("%F %T")
CONF_CAF_FULL_NAME = 'The Allen Mouse Brain Reference Atlas'

REFERENCE_WIDTH  = 456
REFERENCE_HEIGHT = 320

voxelSize = 0.025

# ax+b, cy+d
coordinateTuple =\
        (voxelSize, -5.575, voxelSize, -1.025)
# c,d,a,c
alignerCoordinateTuple =\
(-5.575, -1.025, voxelSize, voxelSize)

tracedSlideTemplate = """<?xml version="1.0" ?><svg baseProfile="full"
height="%d"
id="body"
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
renderingProperties['imageSize']  = (REFERENCE_WIDTH*20, REFERENCE_HEIGHT*20)

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

imageToStructure=\
	{\
	"#010101"	:	"Brain",
	"#020202"	:	"CH",
	"#030303"	:	"CTX",
	"#040404"	:	"CTXpl",
	"#080808"	:	"OLF",
	"#090909"	:	"MOB",
	"#0a0a0a"	:	"AOB",
	"#0b0b0b"	:	"AON",
	"#0c0c0c"	:	"TT",
	"#0d0d0d"	:	"PIR",
	"#0e0e0e"	:	"NLOT",
	"#0f0f0f"	:	"PAA",
	"#101010"	:	"COA",
	"#111111"	:	"TR",
	"#181818"	:	"HPF",
	"#191919"	:	"HIP",
	"#1a1a1a"	:	"CA",
	"#1c1c1c"	:	"DG",
	"#1e1e1e"	:	"RHP",
	"#1f1f1f"	:	"SUB",
	"#222222"	:	"CNU",
	"#232323"	:	"STR",
	"#242424"	:	"STRd",
	"#252525"	:	"CP",
	"#262626"	:	"STRv",
	"#272727"	:	"ACB",
	"#282828"	:	"FS",
	"#292929"	:	"OT",
	"#2a2a2a"	:	"LSX",
	"#2b2b2b"	:	"LS",
	"#2c2c2c"	:	"SF",
	"#2d2d2d"	:	"sAMY",
	"#2e2e2e"	:	"CEA",
	"#2f2f2f"	:	"AAA",
	"#303030"	:	"MEA",
	"#313131"	:	"PAL",
	"#323232"	:	"PALd",
	"#333333"	:	"PALv",
	"#343434"	:	"MA",
	"#353535"	:	"SI",
	"#363636"	:	"PALc",
	"#373737"	:	"BAC",
	"#383838"	:	"BST",
	"#393939"	:	"PALm",
	"#3c3c3c"	:	"BS",
	"#3d3d3d"	:	"IB",
	"#3e3e3e"	:	"TH",
	"#3f3f3f"	:	"DORpm",
	"#404040"	:	"ATN",
	"#414141"	:	"AD",
	"#424242"	:	"AM",
	"#434343"	:	"AV",
	"#444444"	:	"IAD",
	"#454545"	:	"IAM",
	"#464646"	:	"LD",
	"#474747"	:	"RT",
	"#484848"	:	"LAT",
	"#494949"	:	"LP",
	"#4a4a4a"	:	"SGN",
	"#4b4b4b"	:	"GENv",
	"#4c4c4c"	:	"IGL",
	"#4d4d4d"	:	"LGv",
	"#4e4e4e"	:	"ILM",
	"#4f4f4f"	:	"CL",
	"#505050"	:	"CM",
	"#515151"	:	"PCN",
	"#525252"	:	"PF",
	"#535353"	:	"EPI",
	"#545454"	:	"LH",
	"#555555"	:	"MH",
	"#565656"	:	"MED",
	"#575757"	:	"IMD",
	"#585858"	:	"MD",
	"#595959"	:	"PR",
	"#5a5a5a"	:	"DORsm",
	"#5b5b5b"	:	"GENd",
	"#5c5c5c"	:	"LGd",
	"#5d5d5d"	:	"MG",
	"#5e5e5e"	:	"PP",
	"#5f5f5f"	:	"VENT",
	"#606060"	:	"VM",
	"#616161"	:	"VP",
	"#646464"	:	"HY",
	"#656565"	:	"PVZ",
	"#666666"	:	"ARH",
	"#676767"	:	"PVH",
	"#686868"	:	"PVR",
	"#696969"	:	"ADP",
	"#6a6a6a"	:	"AVP",
	"#6b6b6b"	:	"AVPV",
	"#6c6c6c"	:	"DMH",
	"#6d6d6d"	:	"MEPO",
	"#6e6e6e"	:	"PD",
	"#6f6f6f"	:	"PS",
	"#707070"	:	"SCH",
	"#717171"	:	"MEZ",
	"#727272"	:	"AHN",
	"#737373"	:	"MBO",
	"#747474"	:	"LM",
	"#757575"	:	"MM",
	"#767676"	:	"SUM",
	"#777777"	:	"MPN",
	"#787878"	:	"PH",
	"#797979"	:	"PMd",
	"#7a7a7a"	:	"PMv",
	"#7b7b7b"	:	"VMH",
	"#7c7c7c"	:	"LZ",
	"#7d7d7d"	:	"STN",
	"#7e7e7e"	:	"TU",
	"#7f7f7f"	:	"ZI",
	"#808080"	:	"MB",
	"#818181"	:	"MBsen",
	"#828282"	:	"IC",
	"#838383"	:	"MEV",
	"#848484"	:	"NB",
	"#858585"	:	"PBG",
	"#868686"	:	"SAG",
	"#878787"	:	"SCs",
	"#888888"	:	"MBmot",
	"#898989"	:	"SCm",
	"#8a8a8a"	:	"SNr",
	"#8b8b8b"	:	"VTA",
	"#8c8c8c"	:	"RR",
	"#8d8d8d"	:	"PAG",
	"#8e8e8e"	:	"INC",
	"#8f8f8f"	:	"PRT",
	"#909090"	:	"APN",
	"#919191"	:	"MPT",
	"#929292"	:	"NOT",
	"#939393"	:	"NPC",
	"#949494"	:	"OP",
	"#959595"	:	"MRNmg",
	"#969696"	:	"VTN",
	"#979797"	:	"AT",
	"#989898"	:	"CUN",
	"#999999"	:	"RN",
	"#9a9a9a"	:	"III",
	"#9b9b9b"	:	"EW",
	"#9c9c9c"	:	"IV",
	"#9d9d9d"	:	"MBsta",
	"#9e9e9e"	:	"SNc",
	"#9f9f9f"	:	"PPN",
	"#a0a0a0"	:	"RAmb",
	"#a1a1a1"	:	"CLI",
	"#a2a2a2"	:	"DR",
	"#a3a3a3"	:	"IPN",
	"#a4a4a4"	:	"HB",
	"#a5a5a5"	:	"P",
	"#a6a6a6"	:	"P-sen",
	"#a7a7a7"	:	"NLL",
	"#a8a8a8"	:	"PB",
	"#a9a9a9"	:	"PSV",
	"#aaaaaa"	:	"SOC",
	"#ababab"	:	"P-mot",
	"#acacac"	:	"B",
	"#adadad"	:	"DTN",
	"#aeaeae"	:	"PCG",
	"#afafaf"	:	"PG",
	"#b0b0b0"	:	"SG",
	"#b1b1b1"	:	"SUT",
	"#b2b2b2"	:	"TRN",
	"#b3b3b3"	:	"V",
	"#b4b4b4"	:	"VI",
	"#b5b5b5"	:	"VII",
	"#b6b6b6"	:	"P-sat",
	"#b7b7b7"	:	"CS",
	"#b8b8b8"	:	"LC",
	"#b9b9b9"	:	"NI",
	"#bababa"	:	"RPO",
	"#bbbbbb"	:	"SLC",
	"#bcbcbc"	:	"SLD",
	"#bdbdbd"	:	"MY",
	"#bebebe"	:	"MY-sen",
	"#bfbfbf"	:	"AP",
	"#c0c0c0"	:	"CN",
	"#c1c1c1"	:	"DCN",
	"#c2c2c2"	:	"CU",
	"#c3c3c3"	:	"GR",
	"#c4c4c4"	:	"ECU",
	"#c5c5c5"	:	"NTS",
	"#c6c6c6"	:	"SPVC",
	"#c7c7c7"	:	"SPVI",
	"#c8c8c8"	:	"SPVO",
	"#c9c9c9"	:	"MY-mot",
	"#cacaca"	:	"AMB",
	"#cbcbcb"	:	"DMX",
	"#cccccc"	:	"IO",
	"#cdcdcd"	:	"ISN",
	"#cecece"	:	"LIN",
	"#cfcfcf"	:	"LRN",
	"#d0d0d0"	:	"MARN",
	"#d1d1d1"	:	"PAS",
	"#d2d2d2"	:	"PGRN",
	"#d3d3d3"	:	"PPY",
	"#d4d4d4"	:	"VNC",
	"#d5d5d5"	:	"LAV",
	"#d6d6d6"	:	"MV",
	"#d7d7d7"	:	"XII",
	"#d8d8d8"	:	"x",
	"#d9d9d9"	:	"y",
	"#dadada"	:	"MY-sat",
	"#dbdbdb"	:	"RM",
	"#dcdcdc"	:	"RO",
	"#e0e0e0"	:	"CB",
	"#e4e4e4"	:	"CBN",
	"#e5e5e5"	:	"DN",
	"#e6e6e6"	:	"FN",
	"#e7e7e7"	:	"IP",
	"#e8e8e8"	:	"CBX",
	}

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
('Age', '56 days'),
('Sex', 'male'),
('Body weight', '25.19 +/- 1.59 g'),
('Source','http://community.brain-map.org/confluence/download/attachments/525267/data.zip?version=1'),
('Language', 'En'),
('SRSCode', 'INCF:0101'),
('SRSName', 'Mouse_ABAreference_1.0'),
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
('CAFCompilationTime',CONF_CAF_COMPIL_TIME)])
