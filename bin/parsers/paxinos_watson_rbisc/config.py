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

"""
Module which holds all details of configuration.
Intention of this module is to hold all configuration and not let to save configuration in other
(regular) modules. Ultimately, no configuration should be found in regular modules.

This file should be imported using "from config import *" which integrate namespaces
of this module and importing module.
"""
import re

CONF_PARSER_COMMENT  = ['CAF dataset based on: George Paxinos, Charles Watson,',
                      'The rat brain in stereotaxic coordinates, 6th edition.',
                      'Ontology tree created by, P. Majka, E, Kublik',
                      'Nencki Institute of Experimental Biology']
CONF_PARSER_NAME    = ['PW_RBSC_6th']
CONF_CONTACT_COMMENT= ['Piotr Majka, Nencki Institute of Experimental Biology']
CONF_CONTACT_EMAIL  = ['pmajka@nencki.gov.pl']

#{ Some general definitions
CONF_ATLAS_START_SLIDE = 44
CONF_ATLAS_END_SLIDE = 204
CONF_CORONAL_PAGE_RANGE = range(CONF_ATLAS_START_SLIDE,CONF_ATLAS_END_SLIDE +1)
"""
Numbers of pages containing coronal slices. Rat Atlas contains 160 slices in coronal plane.
"""
CONF_HIERARCHY_ROOT_NAME = "Brain"

CONF_STRUCTURES_NON_SYMMETRIC=['rf','ri','vBrain']
"""
Declare names of structures that would not be symmetrized
(because they need to be single for sake of efficiency).
"""

CONF_STRUCTURES_NON_TRACE=['rf','ri']
"""
Define structures that would not be traced. Most of them are
structures outside the brain and we not want to trace them because
tracing them means tracing something which is not brain actually
"""

CONF_STRUCTURES_EMPTY=['cc','C','4V','RelC','MRe','IRe','3V','D3V','PiRe','Aq','chp','LV','IVF','RL4V']
"""
List of strucutres which are not actual structures but rather volumes where there is no
brain actually.
"""

CONF_BRAIN_STRUCTURE_COORDS=[100,100]
"""
Where on the slide put virtual brain (vBrain) structure label (defined in image coordinates).
"""
#}

#{ Some important file locations
CONF_FILENAME_TEMPLATES=\
		{'raw':'*.svg',
		'pretraced':'*_pretrace_v*.svg',
		'traced':'*_traced_v*.svg'}
"""
Dictionary containing templates of raw, pretraced and traced filenames used for reading files. Filenames used for saving are geneated using different templates. Raw files contains only number of slides. Pretraced and traced files contains version number as well.
"""

CONF_FILENAME_SAVE_TEMPLATES=\
		{'raw':'%d.svg',
		'pretraced':'%d_pretrace_v%d.svg',
		'traced':'%d_traced_v%d.svg'}
"""
Directory containing templates used for generating filenames while saving pretraced and traced files. Template for 'raw' files is also provided, however it is not used anywhere in code.
"""

CONF_RE_FILENAME_TEMPLATES=\
		{'raw':re.compile(r'(\d+).svg'),
		'pretraced':re.compile(r'(\d+)_pretrace_v(\d+).svg'),
		'traced':re.compile(r'(\d+)_traced_v(\d+).svg')}
"""
Templates used for searching for files of certain type (raw, pretraced or traced) via glob function.
It seems that is defining three version of templates is somehow redundant and... well it is.
However, at this moment I do not see a reasonable way to merge them to one template.
"""
#}

#{ Global constants - SVG drawing size and rendering
CONF_TRACER_REFERENCE_WIDTH=float(1008)
CONF_TRACER_REFERENCE_HEIGHT=float(1008)	

CONF_POTRACE_WIDTH_STRING =str(CONF_TRACER_REFERENCE_WIDTH )+'pt'
CONF_POTRACE_HEIGHT_STRING=str(CONF_TRACER_REFERENCE_HEIGHT)+'pt'
CONF_POTRACE_SVG_RESOLUTION_STRING='300x300'
CONF_POTRACE_ACCURACY_PARAMETER='0.2'

CONF_DEFAULT_RENDER_WIDTH =3360
CONF_DEFAULT_RENDER_HEIGHT=3360
CONF_TRACER_CACHE_LEVEL = 0
CONF_TRACER_IMAGE_SIZE  = (CONF_DEFAULT_RENDER_WIDTH, CONF_DEFAULT_RENDER_HEIGHT)

CONF_GROWFILL_DEFAULT_BOUNDARY_COLOUR = 200

CONF_TRACER_TAGS_TO_CLEAN=['text','rect','line']
#}

#{ Global constants - definitions of characteristic attributes
CONFIG_BRAIN_LINE_STROKE='#00aeef'
CONFIG_ARROW_LINE_STROKE='#231f1f'
CONFIG_BLACK_LINE_STROKE='#020505'
CONF_GRID_ELEMENT={\
		'stroke':'#a7a9ac',
		'stroke-width':'0.25'}
"""
Set of attributes characteristic to certain image elements: line, arrow and grid. 
"""

# Flag that indicates if we force stroke-width:
# None: stroke-width remains unchanged, otherwise: set stroke-width to
# indicatted value:
CONF_FORCE_PATH_STROKE_WIDTH = None

CONF_ARROWLINE_ELEMENT={'stroke':CONFIG_ARROW_LINE_STROKE}
"""
Stroke definition required to consider line element as an arrow (=the line attached to a label)
"""

CONF_GIRD_ELEMENT_MIN_LENGTH=100
"""
Minimal length of line to consider it as an grid element
"""

CONFIG_AttrToFixSVG={'width':'1008',
			'height':'1008',
			'viewBox':'0 0 1008 1008'}
"""
Attrubutes to be assigned to SVG element of SVG file (the root element of xml tree).
"""

CONF_TRACER_CUSTOM_PATH_SETTINGS={\
		'id':'None',
		'stroke':'none',
		'fill':'#ff0000'\
		}

CONFIG_SPECIAL_SLIDE_RANGE=[range(128,141)+range(142,145), range(44,128)+range(145,205)+[141]]
CONFIG_AttrToFixG=[{'transform':'translate(0,1008) translate(998,-803.84)  scale(1,-1)'},
		{'transform':'translate(0,1008) scale(1,-1)'}]
"""
Attrubutes to be assigned to topmost 'g' element of SVG file before simplyfying
SVG file structure (a kind of fix). We define ranges in C{CONFIG_SPECIAL_SLIDE_RANGE} and
corresponding values in C{CONFIG_AttrToFixG}.

In this particular atlas, slides 128-140,142,145 are constructed in different way than the other
slides: 44-127,141,145-205
"""
#}

#{ Additional labels that should be removed
CONF_PDF_HELPER_LABELS=['Home','Full Screen On/Off','Plate','<=','=>']
"""
List of labels which not describe brain structures and should be removed before further parsing.
Those labels are residues from PDF conversion and describes ie. atlas page numbers, headers, etc.
"""
#}

#{ Global regular expressions:
re_number='([0-9.-]+)'
""" 
Relavitely easy regexp for number should work in most cases.

More general regexp for anu kind of real number taken from 
http://books.google.pl/books?id=YEoiYr4H2A0C&printsec=frontcover&dq=Python+Scripting+for+Computational+Science
page 334. appears not to work correctly.

C{re_number=r'([+\-]?(\d+(\.\d*)?|\d*\.\d+)([eE][+\-]?\d+)?)'}
"""

#Define bregma regular expression >>Bregma number mm<<:
re_bregma=re.compile(r'Bregma\s+(-?\d\+.\d*|-?\d*\.\d+)\s+mm\s*')

re_trd={
'translate'  : re.compile(r'ranslate\('+re_number+','+re_number+'\)'),
'scalexy'    : re.compile(r'scale\('+re_number+','+re_number+'\)'),
'scalex'     : re.compile(r'scale\('+re_number+'\)'),
'matrix'     : re.compile(r'matrix\('+5*(re_number+',? ')+re_number+'\)\s*')
}
""" Holds regular expressions for supproted transformations. """


# Because we have many types of paths we define regular expression
# for different types of paths
# TODO: Extend regular expression below so they could cover all types of path
#       unsupported: A as arch are not likely to be used.
# TODO: Some types of paths are clearly wrong parsed! It should be corrected
# XXX: Note that only absolute coordinates (capital letters in segments type) are supported
# TODO: Probably SVGpathparse module should be used here.
re_path=[
		re.compile(r'([MLQT])'+re_number+','+re_number),\
		re.compile(r'([HV])'+re_number),\
		re.compile(r'(SQ)'+re_number+','+re_number+','+re_number+','+re_number),\
		re.compile(r'(C)'+re_number+','+re_number+','+re_number+','+re_number+','+re_number+','+re_number),\
		re.compile(r'(Z)')
		]
"""
List of regular expresions for supported types of paths:
	- M,L,Q,T
	- H,V
	- S,Q
	- C
	- Z
@attention: Unsupported path types: A
"""

re_PointsPair=re.compile(r''+re_number+','+re_number)
"""
Regexp for pair of points (comma separated, without whitespaces, bracketless: dd,dd)
"""

re_fontsizepx=re.compile(r'([0-9]+)px')
""" Regexp for fontsize in pixels. """
#}

CONF_FILL_COLOURS = {"MA3": "19A6D7", "Su3C": "2E00F2", "45Cb": "B2FFC3", "LPAG": "7678FF", "10Cb": "47DF72", "SPa": "FF8100", "Obex": "5917E1", "Pir-2": "DFE959", "Pir-1":
"DAE900", "SPO": "B2EAFF", "SPF": "EFB12C", "CGPn": "B2FFBF", "GP": "FFF8B2", "LarPh": "777777", "GI": "C3C900", "LPMR": "FFC259", "Gr": "2CCF7C", "Sacc": "777777", "SNL":
"1F00FF", "SNM": "6E59FF", "SNR": "BDB2FF", "Cb": "59FF80", "Gl": "D7FF59", "Gi": "85F2B2", "VLi": "DFB647", "10n": "CA00D4", "7DL": "3BDEFF", "me5": "A877F2", "LMol": "EEFF76",
"RtTg": "85E5D8", "LSp": "777777", "VEn": "5F17D4", "LSD": "DEFFB2", "10N": "4CBCDF", "VLL": "2CFF95", "LSO": "7FDEFF", "EVe": "4CA8C7", "VLG": "CF9500", "EntCx": "D6FF00", "LSV":
"92FF00", "AVVL": "FFE0B2", "PaLM": "FFB676", "LSS": "4700E5", "ZI": "FF8C00", "TSne": "777777", "AudC": "777777", "tz": "A16BE9", "Zo": "7E76E9", "Uvu": "47E977", "SolRL":
"00FFE9", "9n": "E959E5", "apal": "777777", "Stap": "777777", "m5": "6017CB", "EpiG": "777777", "Stg": "FF6800", "RLi": "3BDFC3", "Str": "FFFAB2", "V": "9776CB", "SChL": "777777",
"Sty": "777777", "gpal": "F247DE", "RLH": "59FFD6", "mm": "FF23DD", "ml": "00C0D8", "CVL": "99CDDF", "mt": "A082CB", "mp": "FFD9B2", "Ld": "B6FF59", "La": "E94100", "Li": "00FFB0",
"DPO": "32CBFF", "NPh": "777777", "LD": "FFAE2C", "LC": "4CAECF", "LA": "8C5FF2", "LO": "DCDF8E", "LM": "FF7100", "LH": "FFCFB2", "LV": "FF005D", "LT": "6623FA", "LS": "95FF00",
"LP": "DFAD59", "LZ": "DF5500", "A": "9877ED", "PaPo": "FF7700", "Subth": "FFB559", "8Cb": "00F446", "PlPAG": "7677E9", "DMTg": "00FDFF", "D3V": "FF0092", "9a,bCb": "967117",
"OlfCx-1": "F7FFB2", "rLL": "670BE5", "6Cb": "76E98D", "Eye": "777777", "TPal": "777777", "PRh": "E6E98E", "C1-CVL": "777777", "cll": "3200FF", "POHy": "777777", "SNRDM": "777777",
"iml": "6617DC", "InWh": "0A00FF", "Hil": "777777", "ZIV": "FFB659", "ZIR": "FFDCB2", "mxv": "777777", "ZID": "DF7900", "ZIC": "FF8900", "SNC": "1700FF", "APT": "0041FF", "PeFLH":
"9B76E1", "MRe": "DF0078", "APF": "777777", "ExOrb": "777777", "DLPAG": "3B41E9", "LPLR": "FFA000", "rs": "7317F2", "rf": "777777", "LPLC": "FFE2B2", "6aCb": "59E975", "dsc":
"7017FA", "MVPO": "9777DC", "DLG": "E9C76B", "ATg": "3BE9E9", "LPBV": "76FFC0", "DLO": "DADF47", "LPBS": "3BFFA4", "DLL": "6247F2", "LPBM": "777777", "3-4Cb": "23F45F", "LPBI":
"B2FFDB", "LPBD": "00E97B", "LPBE": "3BE997", "LPBC": "00FF85", "LgsCa": "777777", "ScVe": "777777", "SHThC": "777777", "RAmb": "A982F2", "CeC": "FF3C00", "CeM": "FF8159", "CeL":
"FFC4B2", "ECu": "B2FFCC", "RMg": "00FFD4", "RMC": "00FFC2", "1b": "778899", "RetroHippRegion": "F1FFB2", "B": "FFFBB2", "Fro-Par": "777777", "mRt": "777777", "BTel": "777777",
"RVRG": "896BBF", "InCG": "A18EFF", "VMH": "FF6F00", "Sep": "ABFF3B", "5mx": "777777", "MPOL": "FFD2B2", "MPOM": "FF9E59", "MPOC": "FF6A00", "StrD": "FFEC00", "STMP": "C1E976",
"STMV": "A3FF00", "ty9": "777777", "V1M": "FDFFB2", "V1B": "FBFF00", "STMA": "ADE93B", "IntDL": "00FF3D", "POH": "682FD8", "S1HL": "E8E93B", "PDTg": "3BFCFF", "VCA": "00F3FF",
"PaAP": "E9AC76", "VLH": "8C53E9", "IRtA": "A082E5", "TuLH": "6F23ED", "IML": "777777", "VCP": "00ECFF", "S1FL": "FEFFB2", "bsc": "FF0F00", "VCl": "9F6BF6", "VMPO": "FF7C00",
"PAP": "777777", "DCl": "FFDE00", "ectd": "D88ED0", "6RB": "00D7FF", "PAG": "7678FF", "LSI": "97FF00", "ASCC": "777777", "och": "5A0BCB", "occ": "777777", "ocb": "8153C3", "3Cb":
"23DF59", "5ADi": "3BD2E9", "VCAGr": "00F3FF", "df": "57FF00", "PLCo": "FF4F00", "X": "4CCEFF", "KF": "59FFB7", "bas": "FF6BF0", "AReCa": "777777", "eml": "752FE1", "emv":
"777777", "8vn": "F7B2FF", "DRL": "B2FFF0", "DMC": "FF5900", "DMD": "FFCEB2", "DMH": "FF9D59", "GeGl": "777777", "DMV": "FF6900", "Pr5VL": "B2FFE1", "HPtg": "777777", "DRD":
"00FFCA", "PeF": "E99159", "CxA2": "777777", "C": "A98EED", "CxA1": "FF8F59", "azac": "E58EDD", "Pr5DM": "00FF99", "InfM": "777777", "VLPO": "E95C00", "unx": "A56BF2", "Subiculum":
"F1FFB2", "MOB": "ECFFB2", "InfS": "7647E1", "prf": "23D458", "VRe": "FFAB00", "IRec": "777777", "12GH": "59DF99", "BCo": "777777", "VIEnt": "C3E900", "C3": "7FBBCF", "C2":
"65D9FF", "C1": "00AEE7", "PCRtA": "6423E9", "CI": "59FFA9", "lofr": "F28EE4", "VeCb": "23FF64", "CM": "FFE0B2", "CL": "FF9900", "CC": "FF5989", "CB": "FFF000", "CA": "E0FF00",
"1Cx": "777777", "CG": "85D892", "LSI-3": "BBFF59", "Utr": "777777", "1Cb": "00FF38", "IntP": "00FF3B", "LSI-1": "85DF00", "CV": "777777", "mcp": "8EF4AC", "CrP": "777777",
"LatPC": "00FF40", "Cl": "FFDF00", "7DI": "76E8FF", "MnPO": "693BCB", "HSCCA": "777777", "Cg": "777777", "7DM": "00D3FF", "Ce": "D43200", "DMSp5": "B2FFFA", "Cx": "E5E976", "LPMC":
"DF8C00", "Cu": "2CE569", "Ct": "00CF65", "tzx": "777777", "is": "B38EE9", "DLEnt": "D6FF00", "LOT": "F5FF59", "ia": "8F6BC7", "ic": "C559FF", "dhc": "4CFF00", "V1": "E7E959",
"V2": "FAFF59", "VA": "FFE8B2", "VC": "00D7E5", "InPl": "777777", "VG": "DF9F00", "SChDL": "FF7900", "VL": "FFB500", "VM": "F4D98E", "VO": "D1D48E", "VP": "FFE900", "VS": "F1FFB2",
"SplCa": "777777", "Y": "19BAF7", "PrEW": "733BDC", "NSpt": "777777", "TempS": "777777", "Ve": "9277BF", "ventricles": "FF0067", "CV2": "777777", "AmbSC": "00FF1F", "5T": "C80815",
"DRV": "00E9BC", "DRI": "59E9CC", "5N": "59E7FF", "5VM": "777777", "DRC": "59FFDC", "IOb": "777777", "RVL": "AD8EE5", "IOM": "B2FFE3", "5n": "777777", "IOK": "00FFA4", "IOD":
"00FFA9", "5a": "777777", "IOB": "B2FFE3", "IOA": "00E994", "5b": "FFEF00", "opt": "6300F2", "D": "777777", "Cxne": "777777", "ReIC": "FF0070", "STLD": "AAFF00", "Ary": "777777",
"STLI": "B9E959", "CEnt": "E5FF59", "STLJ": "C6FF59", "VCPO": "B082FA", "Arc": "FFA559", "STLP": "E4FFB2", "SCh": "FFD7B2", "PTg": "B59AE9", "PTe": "955FFF", "HB": "76EFC9", "Pa5":
"339FC7", "SCM": "777777", "SCO": "6A17FF", "Hy": "DF6000", "icf": "5E00ED", "Hi": "777777", "Hb": "777777", "icp": "B88EF6", "PBW": "B2FFDE", "PBP": "00FF92", "MPn": "B2FFE9",
"plf": "6000E9", "PBG": "2900E5", "AuD": "FFFDB2", "SNCV": "B9B2FF", "ATh ": "FFC223", "MPB": "00FF8D", "MPA": "E99659", "MPO": "FF6A00", "DMPAG": "3B40FF", "SNCD": "1500FF",
"SNCM": "1900DF", "ppf": "B88EF2", "7Gn": "777777", "sol": "00DFCD", "sox": "6517D0", "PrTh": "777777", "CuR": "00FF51", "LaDL": "FFC7B2", "iopha": "F223D7", "LaVM": "FF8859",
"LaVL": "FF4700", "ADP": "FF9F59", "C1-RVL": "777777", "AuV": "FFFA00", "Z": "8047DC", "ptgpal": "777777", "LDTgV": "00FFFB", "ScTy": "777777", "S1T": "8647F6", "LTer": "777777",
"azp": "E523D2", "mtg": "C09AF6", "Pre-Cb": "00FFAE", "Sim": "3BFF6F", "VMHVL": "E96700", "AOrb": "777777", "RtTgP": "00FFDE", "PrBo": "986BED", "MEnt": "F2FFB2", "EAC": "FFC5B2",
"ne": "777777", "RtTgL": "B2FFF4", "ns": "8453CB", "fornix": "55FF00", "SRec": "777777", "E": "FF0045", "Crus1": "6BFF96", "Crus2": "8EE9A9", "RtSt": "A082D4", "ESO": "B69AFA",
"Eyelid": "777777", "Cg1": "EFF447", "Cg2": "F7FF00", "VMHDM": "FF6F00", "GrDG": "E9FF59", "ECIC-1": "0038FF", "ECIC-3": "597AFF", "ECIC-2": "B2C2FF", "SalPh": "777777", "5Gn":
"0097C7", "Oral": "777777", "5MHy": "00C9E9", "r1Rt": "777777", "5Gn-5n": "777777", "Cir": "E97400", "PSTh": "DFAE00", "StA": "CEB2FF", "LHb": "F4C2C2", "Int": "00FF3C", "4-5Cb":
"6BF492", "StM": "777777", "SMGl": "777777", "pms": "6A00FF", "LPGiA": "008CFF", "iorb": "E547D0", "SObCa": "777777", "M1": "EFF46B", "M2": "ECF400", "ST": "96E900", "ophv":
"777777", "GrC": "9782C7", "GrA": "EDFFB2", "opha": "777777", "GrO": "C2FF00", "Me": "E96F3B", "LTe": "996BFF", "Mc": "777777", "occv": "777777", "v": "9253E5", "Mi": "A1D400",
"DCDp": "00CCFF", "PiSt": "AB8EE1", "MiTg": "76E8E9", "Lth": "6023E5", "Mx": "00DF6E", "LPal": "777777", "ME": "7847E5", "MD": "FFA300", "MG": "FFD485", "MB": "3B4CEF", "MM":
"FFEDB2", "E-OV": "FFB2D0", "MO": "FBFF8E", "hbc": "78866B", "PC5": "66D1F7", "Corti": "777777", "MT": "3D00C3", "MV": "4E17C3", "SupM": "777777", "MS": "82E900", "MZ": "FFD3B2",
"TyM": "777777", "V2MM": "FCFFB2", "V2ML": "F8FF00", "OvalW": "777777", "sphpl": "777777", "ial": "777777", "SubV": "FFB200", "Iris": "777777", "SubP": "7E53C7", "F": "FFAC59",
"SubG": "985FFA", "SubD": "FFE7B2", "SubB": "6C3BBF", "SubC": "777777", "RRF-A8": "2600CB", "TyC": "777777", "SubI": "C5A6FA", "cav": "777777", "S1ULp": "D2D400", "MPL": "5F2FC7",
"Min": "4B23FF", "AcbSh": "E9DA00", "BAC": "E94C00", "spa": "777777", "MiA": "D8FF59", "MPT": "9B8ED8", "s5": "7D47C7", "1": "777777", "VPM": "C99400", "VPL": "E9D18E", "STD":
"9DFF00", "STL": "E5FFB2", "STM": "90DF00", "STI": "C9FF59", "AHiPM": "FAD6A5", "AHiPL": "FF3300", "aot": "B6FF00", "STS": "A0FF00", "10Gn": "777777", "OmHy": "777777", "STh":
"696969", "st": "A782D8", "STr": "B4DF00", "sl": "777777", "AVDM": "FF9700", "PDig": "777777", "sf": "8C3BFA", "Rt": "E9B423", "Re": "DF9600", "tth": "9C5FED", "Rc": "777777",
"Ro": "560BDC", "Rh": "F4BC23", "SolVL": "2CFFEE", "RR": "4923F2", "SPTg": "00D1D4", "RA": "59D8C1", "RC": "76DFCD", "RL": "A58ED0", "RI": "9E82D0", "AtOc": "777777", "STMPM":
"E3FFB2", "STMPL": "96E900", "STMPI": "B9FF3B", "DpG": "7A76FF", "5Te": "B2F3FF", "DCGr": "59DDFF", "MVeMC": "B2FFD4", "ec": "CFFFB2", "5Tr": "5517F6", "PoMn": "D4B86B", "MCPC":
"8E5FF6", "5TT": "3BE3FF", "MCPO": "FF9A59", "MPtg": "777777", "RAPir": "F8FFB2", "8Gn": "66B5CF", "SolDM": "59DFD1", "SolDL": "00EFD6", "IsoCx": "FCFF00", "MPtA": "DBDF6B",
"StyMF": "777777", "FMag": "777777", "DTT-4": "EBFFB2", "DTT-2": "D5FF59", "DTT-3": "BEFF00", "DTT-1": "A7DF00", "PVP": "F4B200", "PVZ": "FF7800", "ATh": "777777", "PVA": "DFA300",
"2": "777777", "fmj": "9DFF59", "PVG": "777777", "fmi": "6BFF00", "Post": "E0FF59", "1n": "777777", "IMA": "FFD66B", "IMD": "E9BD47", "IMG": "B19AE5", "IntDM": "B2FFC5", "PDR":
"7447D0", "PDP": "FFD2B2", "SNRVL": "777777", "MRVL": "4CBFE7", "Rbd": "5B23BF", "CLi": "00EFC3", "OptF": "777777", "vBrain": "FF5961", "LAcbSh": "FFF459", "noradrenaline-cells":
"FF59C8", "RSD": "F9FF6B", "r": "8C5FCB", "CA2": "E1FF00", "DM": "FF9459", "DH": "777777", "DI": "D8DF00", "DG": "F4FFB2", "LSI-4": "DFFFB2", "LSI-2": "97FF00", "DC": "00CBFF",
"DA": "E9A159", "DT": "400BC3", "DR": "00FFCC", "DS": "E2FF59", "DP": "D1D46B", "Dk": "0005FF", "Di": "FF7E00", "Ect": "E4E947", "PSol": "0098CF", "PtPR": "E5E96B", "PtPC":
"F7FF23", "PtPD": "C3C923", "dlg": "E500CC", "PaR": "4723E5", "Apir": "D44400", "MCLH": "FF5E00", "ArcLP": "FFA559", "r3Rt": "777777", "Tu-1": "FFFAB2", "PDPO": "886BC3", "eMC":
"762FE5", "Pinna": "777777", "RIP": "00DFB8", "MEE": "6F2FFA", "sss": "777777", "hippocampal-white-matter": "CAFFB2", "Cornea": "777777", "ICjM": "FFEF00", "rmv": "777777",
"Atlas": "777777", "IPACL": "FFF6B2", "IPACM": "FFE300", "STIL": "E6FFB2", "PPit": "777777", "EMi": "6147E5", "STIA": "ADFF00", "JugF": "777777", "3": "777777", "9cCb": "00FF36",
"RGn": "777777", "arteries": "FF00DE", "21": "FFFF00", "ejugv": "777777", "SuVe": "66C9EF", "OlfCx": "F9FFB2", "ILG": "777777", "ILL": "A882FF", "LR4V": "FFB2D6", "ADig": "777777",
"S1DZO": "E8E900", "VMHC": "FFD3B2", "VMHA": "E99859", "6bCb": "00FF32", "DCFu": "00B2DF", "GeHy": "777777", "VPPC": "DFAD23", "6a": "B2FFC1", "6b": "59FF79", "6n": "FF00FB",
"P3V": "FFB2DA", "CGG": "00E924", "6N": "00C5E9", "Otic": "777777", "iala": "D823C2", "vesp": "783BC7", "AIV": "F1F48E", "ialn": "777777", "AIP": "E3E923", "7VI": "76D5E9", "7VM":
"00C0E9", "AID": "CFD423", "I8": "9376D8", "I3": "5F47D8", "StyPh": "777777", "ePC": "AA8ED4", "PtgC": "777777", "I": "FFC6B2", "IP": "001AD4", "IS": "9D76F6", "OPC": "FFBE59",
"II": "682FED", "VOLT": "B98EFF", "IM": "FF4300", "IL": "D8DF23", "IO": "00FFA6", "EAM": "FF4100", "IC": "3B58D4", "IB": "835FD8", "ID": "713BF2", "IG": "B2FF00", "IF": "4000D8",
"VG-2": "FFD059", "DPPn": "00FFB7", "IAud": "777777", "IRt": "7C5FBF", "costr": "AA82E9", "In": "7FCCE7", "AOVP": "C7FF00", "IRe": "777777", "sphml": "777777", "Sp5OVL": "777777",
"RCPMj": "777777", "CnF": "59CEE9", "EPl": "B2E900", "4": "777777", "mxa": "CB23B1", "sumx": "BE9AED", "psa": "777777", "psf": "956BD0", "A8": "FFB2EB", "RAPir-1": "F9FFB2",
"RAPir-2": "EAFF00", "RAPir-3": "F1FF59", "Pig": "777777", "Pir": "CFDF00", "PPTg": "3BE9B9", "ECIC": "0035FF", "AA": "E98759", "MeA": "FF4A00", "LOT-1": "FAFFB2", "VDB": "8BFF00",
"9Cb": "76FF93", "FrA": "5A2FC3", "Cx1": "777777", "PaDC": "FFD6B2", "isRt": "777777", "CxP": "777777", "ArcMP": "E96B00", "AVPO": "DF5E00", "CxA": "F2FF00", "VMHSh": "FFA259",
"aca": "DBFFB2", "aci": "AFFF59", "oc": "7823F2", "Me5": "4323D8", "acp": "82FF00", "ox": "FF7059", "Na": "777777", "RRe": "540BD8", "ArcD": "FF7400", "DPGi": "19A1CF", "ArcL":
"FFD5B2", "ArcM": "E99B59", "Nv": "916BE1", "RRF": "2300BF", "Pir-1b": "EDFF00", "Pir-1a": "F9FFB2", "ELS": "777777", "LScM": "777777", "IPAC": "DFC600", "vhc": "C8FFB2", "aa":
"9677C7", "cbc": "6BDF8D", "ac": "DAFFB2", "af": "777777", "cbw": "23E95E", "acer": "FF8EF5", "cbx": "777777", "SGe": "7223FF", "MZMG": "FFC559", "StapM": "777777", "5": "777777",
"Lat": "00E93B", "Lar": "777777", "ICM": "777777", "DpMe": "5C47CB", "PFl": "8EFFAF", "ICj": "FFF459", "masa": "FF47E4", "masn": "777777", "3-4": "F49AC2", "cpx": "777777", "masv":
"777777", "ICx": "777777", "Unknown": "5100DF", "scc": "D1FFB2", "SIB": "FFE600", "7Cb": "47D470", "alv": "8CFF59", "MxB": "777777", "scp": "00D43B", "Gonial": "777777", "ts":
"00EF7A", "Symp": "777777", "Sp5O": "00FFF5", "AHiAL": "FFC1B2", "AHiAM": "FF7A59", "vert": "9147F2", "Sp5I": "00DFD4", "AHi": "D45A3B", "Sp5C": "59FFF5", "SCGn": "777777", "AHC":
"FF9C59", "AHA": "FFD1B2", "CCrus": "777777", "ri": "777777", "AngT": "F4CE6B", "AHP": "DF5A00", "9-10n": "777777", "HSCC": "777777", "IOVL": "B2FFE5", "LPBCr": "76E9B3", "5Sol":
"FFB2BF", "BLV": "FF3700", "BLP": "FFC2B2", "SSp": "777777", "STMAL": "8AD400", "STMAM": "CFFF76", "BLA": "FF7B59", "VTAR": "76FCFF", "IODM": "00FFA6", "Cond": "777777", "pica":
"777777", "LRtS5": "59FFCB", "Aud": "777777", "S2": "CCD400", "S1": "E8E900", "vc": "777777", "xicp": "9747FF", "Hyoid": "777777", "REn": "777777", "5Cb": "6BE98F", "6": "777777",
"4Sh": "0050FF", "Sp": "6B2FD4", "MdD": "19C3FF", "Au1": "FFFB00", "InM": "85EFB9", "Au2": "FFFA00", "vn": "D0FF59", "Sc": "6823E1", "InG": "B5B2FF", "MdV": "00B7F7", "InC":
"3B48FF", "LPGiE": "B2D6FF", "MasM": "777777", "ASph": "777777", "Ins": "777777", "SI": "FFE600", "SO": "FF6400", "SN": "4E3BE9", "SM": "885FD0", "MoCb": "5017C7", "SC": "7C76E9",
"Inf": "47F479", "SG": "E9B759", "Inc": "777777", "SolIM": "59FFEF", "EthB": "777777", "pons": "2CCEF2", "CAT": "3900CB", "TyBu": "777777", "IntPPC": "00FF3B", "csc": "FFBAB2",
"cst": "BCFFB2", "JxO": "5423C3", "fr": "BD9AF2", "MVePC": "00FF76", "vtgx": "B2FDFF", "fi": "813BED", "a": "D800C6", "SimB": "B2FFC7", "CA3": "F6FFB2", "GlA": "C5FF00", "CA1":
"BCD400", "RSG": "FFFE00", "IOrC": "777777", "PSCCA": "777777", "Occ": "777777", "PCRt": "19ABDF", "VPPn": "00E9AA", "AOE": "D1E976", "AOD": "B9E900", "AOB": "C5FF00", "AOM":
"D5FF3B", "AOL": "E2FF76", "AOV": "EEFFB2", "apmf": "4900BF", "AOP": "C4E93B", "MyHy": "777777", "Bar": "32AFD7", "LacG": "777777", "L": "4500E1", "IPl": "ECFFB2", "BTelne":
"777777", "VG-3": "FFE9B2", "VG-1": "FFB700", "icpx": "9B6BE5", "SFi": "75D400", "SubCV": "4CB1D7", "IPC": "596FFF", "Rad": "E7FF3B", "IPA": "0024FF", "IPF": "500BED", "IPI":
"0019D4", "IPL": "5969E9", "IPR": "B2BAFF", "SFO": "6C3BC3", "SubCD": "00AEEF", "SubCA": "65B8D7", "2n": "DF493B", "Ent": "777777", "HDB": "DDFFB2", "BMA": "FF3800", "EnO":
"777777", "BMP": "FFC3B2", "E5": "BFA6FF", "asp": "F200DC", "EF": "5223C7", "EA": "FF6D3B", "mmp": "777777", "Mall": "777777", "EW": "816BF2", "EP": "440BD0", "MGD": "E99700",
"SHy": "8C53F2", "MGM": "FFA500", "MGV": "FFE4B2", "PMCo": "FF5400", "SHi": "A8E959", "PSphW": "777777", "asc7": "5E00F6", "7ni": "C800FF", "Fro": "777777", "MoDG": "F4FFB2",
"CVL-C1": "777777", "Eth": "E9AA00", "gpn": "777777", "LRtPC": "B2FFE6", "Sptne": "777777", "gpv": "777777", "VTA": "836BE5", "VTM": "D45400", "Fr3": "CFD447", "VTT": "EAFFB2",
"Tongue": "777777", "tfp": "AF77FA", "b": "4D00C7", "VTg": "A16BFA", "PLCo3": "777777", "PLCo2": "777777", "PLCo1": "777777", "stv": "777777", "str": "9E77D4", "AcbC": "FFF9B2",
"7n": "C900FF", "DTgC": "00FF5C", "AcbR": "FFED00", "dopamine-cells": "FFB2ED", "DTgP": "B2FFCF", "5Pt": "76EBFF", "A1-C1": "E959BD", "7N": "B2F1FF", "7L": "3BCBE9", "PaXi":
"D4C18E", "RPC": "B2FFED", "LatC": "777777", "RPF": "8253D8", "scpd": "B2FFC7", "RPO": "1998C7", "GrCb": "5923D8", "Thy": "777777", "321": "C08081", "PCom": "BB9AFF", "Aty":
"777777", "ThC": "777777", "DRGn": "777777", "DCMo": "B2EFFF", "OpD": "777777", "3ECIC": "ABCDEF", "CeAu": "777777", "IAM": "D49A00", "IAD": "D4AE47", "Xi": "FFCE47",
"Medulla-oblongolata": "85CBA8", "hif": "6417D8", "TzM": "777777", "PHA": "8B5FE5", "mcer": "D847C3", "PHD": "590BF6", "dtgx": "F0EAD6", "ParB": "777777", "StrV": "FFFAB2", "ParP":
"777777", "Acbne": "E9E059", "MedDL": "6BD489", "ECIC1": "777777", "ECIC3": "9076D0", "occs": "777777", "5oph": "777777", "BOcc": "777777", "Entne": "777777", "7SH": "B2F1FF",
"MHb": "AB4E52", "SPFPC": "FFAE00", "ANS": "400BC7", "InCo": "9D8EE5", "TMJ": "777777", "py": "8600FF", "Plat": "777777", "pc": "896BFF", "4Cb": "00DF40", "pm": "722FD0", "DTT1":
"777777", "Hipp": "DDFF00", "RPa": "3BEFD2", "p1": "6A0BF2", "mlf": "85DFB3", "Olf": "BDFF00", "PalGl": "777777", "Epith": "FFD759", "ML": "E96700", "mlx": "00E2FF", "IODMC":
"B2FFE4", "RCh": "E99A59", "Cop": "00E943", "Cor": "777777", "Com": "7A6BCB", "PMnR": "B2FFF1", "Sol": "2CD8C9", "LVe": "2500D8", "IOPr": "00FFA6", "Rath": "777777", "SuspLig":
"777777", "simf": "777777", "PIL": "FFE08E", "PIF": "470BBF", "SMV": "2CDF85", "r2Rt": "777777", "Pir-3": "C5D400", "SMT": "9053FA", "SpVe": "99DDF7", "bic": "9253F6", "5man":
"777777", "Intralaminar-Th-nu": "FFBD59", "Or": "CDE900", "2Cb": "B2FFC0", "Op": "443BFF", "OO": "777777", "ON": "C6E959", "OF": "777777", "OB": "777777", "OV": "FF005A", "OT":
"7D53D4", "PCTg": "00E7E9", "FF": "777777", "StHy": "6423D4", "LDDM": "FF9D00", "PSph": "777777", "DEn": "F4FF59", "AMV": "FF9500", "veme": "5F00DC", "O": "19B1E7", "IVF":
"6A3BD4", "LReCa": "777777", "EpP": "510BFA", "Scap": "777777", "Mo5VM": "777777", "Mst": "777777", "SphPal": "777777", "IOrbF": "777777", "BAOT": "FFF500", "chp": "FFB2C5", "ACo":
"E8FF00", "AmbL": "B2FFBB", "PaAM": "E96C00", "AmbC": "59FF69", "Mo5DL": "777777", "cic": "806BD8", "MEI": "510BE9", "infa": "FF00DE", "un": "9053E1", "Tz": "4CC8F7", "Apex":
"777777", "m": "6E2FCB", "Tu": "FFFAB2", "Tr": "AE82F6", "Th": "FFA700", "Tg": "85FEFF", "Te": "FF6100", "PtgPal": "777777", "A14": "FF00C3", "A11": "DF00B4", "A13": "FF59DB",
"TT": "ADE900", "TS": "865FC7", "A1": "E900A5", "A2": "FF59C9", "A5": "FF00A8", "A4": "777777", "A7": "FFB2E3", "TG": "9353FF", "Man": "777777", "LOT-3": "EFFF00", "LOT-2":
"F5FF59", "AC": "777777", "AD": "F4C447", "Med": "8EDFA6", "AI": "777777", "AH": "FFD1B2", "PalPh": "777777", "AM": "DF952C", "AL": "A38ED8", "AO": "CBE959", "DMSp5V": "777777",
"AP": "7FC2D7", "AV": "EFC485", "e": "AC82ED", "PrMC": "7847D4", "Al": "865FE9", "Aq": "DF0045", "Au": "FFFDB2", "LgCa": "777777", "olfa": "9677C3", "gr": "59EFA4", "CPO":
"66C7E7", "DMPn": "00D498", "GiV": "B2FFD2", "SuV": "8447ED", "Sp5": "59E5DE", "MedL": "00C93B", "GiA": "00FF67", "CPu": "FFEC00", "g7": "B98EFA", "vlh": "903BFF", "PFlCv":
"777777", "SpV": "590BE1", "P": "FFEF59", "SimA": "00FF43", "cctd": "CB00B6", "Spt": "777777", "Sph": "33B0DF", "SuMM": "FF6E00", "SuML": "FFD3B2", "STLV": "99E900", "trs":
"777777", "CtdB": "777777", "DTM": "FFA959", "3V": "FFB2DC", "3N": "B2CEFF", "EPlA": "ADDF00", "DTT": "BEFF00", "CeCv": "5F23F6", "IPit": "777777", "REth": "A676FF", "DTg":
"00F25A", "Alar": "777777", "3n": "FDB2FF", "DTr": "6D47CB", "StyGl": "777777", "S1Sh": "FEFF76", "HardG": "777777", "Clav": "777777", "IGL": "DFC98E", "32": "40826D", "Ahi":
"BDA6F6", "cty": "777777", "ctg": "A28EF2", "TrLL": "777777", "MnM": "7B53D0", "SolL": "2CDFCF", "SolM": "85FFF4", "FV": "622FDC", "SolI": "59EFE0", "SolG": "85EFE4", "p1PAG":
"B2B2FF", "PnR": "00FFB4", "SolC": "85DFD5", "PnV": "00FFB4", "FB": "F5FF3B", "FC": "DAFF00", "PnO": "76E9CA", "MnA": "99D8EF", "SolV": "2CEFDF", "PnC": "3BFFC9", "SMD": "777777",
"PrCnF": "772FFF", "Fu": "4900FA", "MDL": "FFE3B2", "MDM": "FFA400", "MDC": "FFC259", "ERS": "98E5FF", "Lens": "777777", "Fl": "47FF7C", "APTD": "0045FF", "8cn": "DD00FF", "pfs":
"00FF4B", "LPtg": "777777", "f": "CBFFB2", "ALD": "777777", "IObCa": "777777", "NasC": "777777", "MVe": "59CB8D", "LPtA": "EDF423", "JPLH": "886BCB", "11N": "00FF7A", "MRec":
"777777", "CnFV": "00CEFF", "CnFI": "59DFFF", "CnFD": "B2F0FF", "CPune": "777777", "gcc": "5DFF00", "sig": "777777", "BHy": "777777", "pcuf": "802FF2", "S9Gn": "777777", "Acs5":
"66AFC7", "Acs7": "33C1EF", "aopt": "DF0400", "EGL": "777777", "C1-A1": "645452", "DIEnt": "D2E959", "lc": "777777", "IPDM": "001EE9", "IPDL": "480BD4", "lo": "B8FF00", "ll":
"85FFC3", "Pr5": "00CB7D", "STSL": "A1FF00", "STSM": "E2FFB2", "IOC": "59E9B6", "PrC": "4900D4", "PrL": "F8FF47", "LPS": "777777", "LPO": "FFD0B2", "MEntR": "4C17BF", "Tu-2":
"E9DB00", "Tu-3": "E9E159", "PrS": "F0FFB2", "das": "00C7FF", "LPB": "B2FFDB", "cs-tract": "E0B2FF", "Sag": "3BD1D4", "2bCb": "00FF2E", "FVe": "66C0DF", "APit": "777777", "APir":
"F0FF59", "9-10-11n": "777777", "S1Tr": "FDFF3B", "lfp": "E7B2FF", "I9Gn": "777777", "8n": "F6B2FF", "S1BF": "E9E976", "sp5": "AF8EDC", "5Ma": "00DBFF", "CST": "2CFF00", "Ctd":
"777777", "Tu1": "8E5FDC", "BStap": "777777", "CGB": "59E96E", "ASt": "835FE1", "MeAD": "FFC8B2", "Amy": "FFC6B2", "AVPe": "DF6B00", "9bCb": "777777", "HMall": "777777", "R":
"2CFFCD", "ictd": "E56BD6", "LEnt": "777777", "dsc-oc": "6A0BFF", "CxA-1": "F3FF00", "CxA-2": "FBFFB2", "CxA-3": "F6FF59", "LDTg": "00FFFB", "AAD": "777777", "PoDG": "DCFF00",
"HippFormation": "CEE93B", "AAV": "777777", "Astr": "FFCBB2", "Pal": "777777", "Pir1": "777777", "xscp": "00FF47", "PaS": "D0FF00", "PaV": "E98D3B", "Unlabeled": "FF001B", "BIC":
"002FFF", "PaC": "9C76E5", "LPGi": "76BBFF", "pyx": "8400FF", "Pa4": "5D17E5", "sm": "7947BF", "Pa6": "6E3BD0", "PoT": "FFA900", "InCSh": "0011FF", "VCCap": "7B3BE5", "MCM":
"777777", "MedCM": "777777", "SLu": "D4E93B", "ijugv": "777777", "9a-bCb": "B2FFC2", "imvc": "6D17ED", "MoS": "D3FF00", "12n": "FA59FF", "PrLSp": "777777", "DLPn": "76FFD8", "12C":
"777777", "mfbb": "6C17E9", "mfba": "6E23DC", "12N": "33BCE7", "MPBE": "00FF8C", "HyGl": "777777", "GPF": "777777", "GHHy": "777777", "MidM": "777777", "ELm": "3E23CB", "Mo5":
"7FC6DF", "LRec": "777777", "VeGn": "777777", "Pr": "875FD4", "BSph": "777777", "SChVM": "FFD7B2", "Pt": "777777", "Py": "DBE976", "Pa": "FF7700", "Pe": "FFD7B2", "Pk": "9E76E9",
"Pi": "FFC900", "Pn": "59FFD0", "Po": "EF9E00", "PR": "4CC4EF", "PS": "FF6C00", "PP": "7A3BF6", "p1Rt": "8347D8", "PV": "D4A423", "PT": "DFBF6B", "dlo": "B8FF00", "RChL": "916BD8",
"HStap": "777777", "PB": "2CCB84", "PC": "DF8800", "PF": "FFBA00", "PH": "FFD4B2", "PN": "8ED4A3", "PL": "9882C3", "PM": "7FD7F7", "P7": "BFA6F2", "P5": "76D8E9", "AtAx": "777777",
"S": "777777", "APTV": "B2C5FF", "dcw-ec-cc-gcc-fmi-fmj": "64FF00", "OPT": "7653BF", "AntCh": "777777", "dpal": "F26BE3", "VTT-1": "EBFFB2", "VTT-2": "BBFF00", "VTT-3": "D2FF59",
"Axis": "777777", "MePD": "FF4C00", "cc": "69FF00", "cg": "3FFF00", "PCGS": "743BE9", "MePV": "8C6BD4", "Hem": "777777", "cp": "9C00FF", "cu": "B69AE1", "2-3Cb": "00D43C", "DCIC":
"5974FF", "PLCo-3": "FF8D59", "PLCo-2": "FF4F00", "PLCo-1": "FFCAB2", "Gem": "3D00D0", "lgn": "777777", "lga": "CB47B9", "PLd": "5B23CB", "lgv": "777777", "PLi": "8153DC", "V2L":
"FBFF59", "PLV": "5D23D0", "Ge5": "FFBA00", "Ant": "3BE962", "IEn": "9D82DC", "PSCC": "777777", "PLH": "5F2FBF", "SOb": "777777", "DpWh": "403BE9", "SOl": "777777", "VLPAG":
"0000E9", "PPy": "8347FA", "3PC": "005EFF", "MeAV": "FF4A00", "SOR": "946BDC", "PPT": "7147C3", "pcer": "D86BC7", "MTu": "FF6100", "mfb": "7E3BE1", "BG": "FFF376", "BL": "FF9476",
"BM": "E99176", "MEntV": "777777", "farfocle": "777777", "Bo": "33A8CF", "Fat": "777777", "T": "742FE9", "IOBe": "59FFC3", "VA-VL": "EFC359", "ptgcn": "777777", "B4": "19BBEF",
"nerves": "D476DF", "B9": "76FFE6", "Sub": "DFC485", "ROb": "76EFDB", "vsc": "852FF6", "LVPO": "00A0D7", "SuG": "0C00E9", "6cCb": "00E92E", "SuM": "E96400", "9aCb": "777777",
"SuS": "8C53ED", "MnR": "3BFFDC", "11n": "777777", "Su5": "99D2E7", "Su3": "6A47FF", "LRt": "B2FFE7", "dcw": "99FF59", "dcs": "2CEF8E", "Ptg": "777777", "Ptd": "777777", "mofr":
"CB6BBC", "subcortical-white-matter": "CBFFB2", "PaMP": "FF973B", "PaMM": "713BD8", "SGl": "00BAFF", "LHbL": "D19FE8", "LHbM": "F4BBFF", "CGn": "777777", "SubVCx": "777777", "PMn":
"00A4DF", "PMV": "D45F00", "CGO": "59FF73", "CGA": "00FF23", "DR3V": "FF59B5", "Amb": "59F26A", "Amg": "777777", "PMD": "FFA359", "SolCe": "00CFB9", "rcc": "777777", "TeA":
"E1E900", "S1DZ": "FEFF00", "Tel": "E0FF59", "Acs6-7": "33C7F7", "7gp": "777777", "CIC": "B2BFFF", "StyHy": "777777", "TempM": "777777", "MSO": "7FD2EF", "TempP": "777777", "IntA":
"59FF80", "DAx": "777777", "Brain": "666666", "mch": "8847E9", "other": "EF00B7", "Acb": "FFEE00", "Pi-3": "A382E1", "4V": "FF59A4", "LOT2": "777777", "LOT1": "7E5FC3", "mPAG":
"777777", "4N": "0049E9", "CD": "777777", "RSGa": "FFFEB2", "RSGb": "FFFE59", "RSGc": "FFFE00", "S1J": "D3D43B", "LDVL": "FFE1B2", "4n": "E900E9"}

CONF_STRUCTURES_LIMITED=[]

# Slides aligner reference coords:
CONF_ALIGNER_REFERENCE_COORDS =\
        (-9.5150660793, -1.535588442565, 0.0176211453744, 0.0176211453744)
