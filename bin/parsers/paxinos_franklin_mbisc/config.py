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

"""
Module which holds all details of configuration.
Intention of this module is to hold all configuration and not let to save configuration in other
(regular) modules. Ultimately, no configuration should be found in regular modules.

This file should be imported using "from config import *" which integrate namespaces
of this module and importing module.
"""
import re

CONF_PARSER_COMMENT  = ['CAF dataset based on: Keith B.J. Franklin, & George Paxinos',
                      'The mouse brain in stereotaxic coordinates, third edition.',
                      'Ontolog tree created by, P. Majka, E, Kublik',
                      'Nencki Institute of Experimental Biology']
CONF_PARSER_NAME    = ['PW_MBSC_3th']
CONF_CONTACT_COMMENT= ['Piotr Majka, Nencki Institute of Experimental Biology']
CONF_CONTACT_EMAIL  = ['pmajka@nencki.gov.pl']
#{ Some general definitions
CONF_ATLAS_START_SLIDE = 28
CONF_ATLAS_END_SLIDE = 127
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
CONF_TRACER_CACHE_LEVEL = 3
CONF_TRACER_IMAGE_SIZE  = (CONF_DEFAULT_RENDER_WIDTH, CONF_DEFAULT_RENDER_HEIGHT)

CONF_GROWFILL_DEFAULT_BOUNDARY_COLOUR = 200

CONF_TRACER_TAGS_TO_CLEAN=['text','rect','line']
#}

#{ Global constants - definitions of characteristic attributes
CONFIG_LABEL_FONT_SIZE=18.
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

CONFIG_AttrToFixG={'transform':'translate(0,1008) scale(1,-1)'}
CONFIG_SPECIAL_SLIDE_RANGE=[CONF_CORONAL_PAGE_RANGE]
CONFIG_AttrToFixG=[{'transform':'translate(0,1008) scale(1,-1)'}]
"""
Attrubutes to be assigned to topmost 'g' element of SVG file.
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
#       unsupported: A
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

CONF_FILL_COLOURS=\
{"EPl":"004000","Gl":"007FFF","ON":"00BFFE","GrO":"00FFFD","IPl":"013FFC","Mi":"017FFB","aci":"01BFFA","E/OV":"01FFF9","lo":"023FF8","vBrain":"027FF7","EPlA":"02BFF6","GrA":"02FFF5","vn":"033FF4","GlA":"037FF3","AOL":"03BFF2","dlo":"03FFF1","MiA":"043FF0","AOE":"047FEF","MO":"04BFEE","LO":"04FFED","AOB":"053FEC","AOM":"057FEB","AOV":"05BFEA","AOD":"05FFE9","FrA":"063FE8","VO":"067FE7","PrL":"06BFE6","DLO":"06FFE5","DTT":"073FE4","VTT":"077FE3","AOP":"07BFE2","IEn":"07FFE1","Pir":"083FE0","3":"087FDF","2":"08BFDE","1":"08FFDD","AI":"093FDC","M2":"097FDB","Cg1":"09BFDA","M1":"09FFD9","Fr3":"0A3FD8","AID":"0A7FD7","AIV":"0ABFD6","DTr":"0AFFD5","DEn":"0B3FD4","DP":"0B7FD3","OV":"0BBFD2","Tu":"0BFFD1","S1":"0C3FD0","fmi":"0C7FCF","aca":"0CBFCE","Cl":"0CFFCD","IL":"0D3FCC","Acb":"0D7FCB","S1J":"0DBFCA","AcbSh":"0DFFC9","21":"0E3FC8","CPu":"0E7FC7","DI":"0EBFC6","AcbC":"0EFFC5","SHi":"0F3FC4","4":"0F7FC3","ICj":"0FBFC2","mfb":"0FFFC1","LV":"103FC0","VP":"107FBF","Nv":"10BFBE","LSI":"10FFBD","ec":"113FBC","GI":"117FBB","cg":"11BFBA","LSD":"11FFB9","Cg2":"123FB8","S1FL":"127FB7","LAcbSh":"12BFB6","ICjM":"12FFB5","LSS":"133FB4","VDB":"137FB3","S1DZ":"13BFB2","S1ULp":"13FFB1","LSV":"143FB0","MS":"147FAF","gcc":"14BFAE","S2":"14FFAD","IG":"153FAC",".cg":"157FAB",".ec":"15BFAA",".MS":"15FFA9",".VDB":"163FA8",".gcc":"167FA7",".AcbSh":"16BFA6",".LAcbSh":"16FFA5",".S1ULp":"173FA4",",mfb":"177FA3",".IG":"17BFA2","VCl":"17FFA1","CB":"183FA0","DCl":"187F9F","HDB":"18BF9E","Ld":"18FF9D","cc":"193F9C","MPA":"197F9B","SIB":"19BF9A","ZL":"19FF99","LPO":"1A3F98","STMV":"1A7F97","MnPO":"1ABF96","VOLT":"1AFF95","SHy":"1B3F94","STLV":"1B7F93","AVPe":"1BBF92","STMA":"1BFF91","STLP":"1C3F90","S1HL":"1C7F8F","S1BF":"1CBF8E","MCPO":"1CFF8D","IPACM":"1D3F8C","IPACL":"1D7F8B","3V":"1DBF8A","VMPO":"1DFF89","AIP":"1E3F88","I":"1E7F87","PS":"1EBF86","STLD":"1EFF85","ic":"1F3F84","SFi":"1F7F83","acp":"1FBF82","VLPO":"1FFF81","Fu":"203F80","Pe":"207F7F","STLJ":"20BF7E","f":"20FF7D","StA":"213F7C","2n":"217F7B","STMAL":"21BF7A","MPOL":"21FF79","MPOM":"223F78","GP":"227F77","och":"22BF76","st":"22FF75","STLI":"233F74","STMAM":"237F73","StHy":"23BF72","CxA":"23FF71","AA":"243F70","BAC":"247F6F","STS":"24BF6E","D3V":"24FF6D",".AA":"253F6C",".cc":"257F6B","TS":"25BF6A",".mfb":"25FF69",".st":"263F68","A14":"267F67","VEn":"26BF66",",1":"26FF65",",2":"273F64",",3":"277F63","STMPI":"27BF62","STMPM":"27FF61","SFO":"283F60","ACo":"287F5F","LOT":"28BF5E","vhc":"28FF5D","sm":"293F5C","df":"297F5B","PV":"29BF5A","A":"29FF59","EA":"2A3F58","SCh":"2A7F57","STMPL":"2ABF56","APF":"2AFF55","PaAP":"2B3F54","AD":"2B7F53","PT":"2BBF52","PLH":"2BFF51","LA":"2C3F50","fi":"2C7F4F","B":"2CBF4E","AHA":"2CFF4D","opt":"2D3F4C","EAC":"2D7F4B","EAM":"2DBF4A","AV":"2DFF49","CM":"2E3F48","AM":"2E7F47","Rt":"2EBF46","Re":"2EFF45","SM":"2F3F44","ST":"2F7F43","SChDL":"2FBF42","PC":"2FFF41","ANS":"303F40","SChVM":"307F3F","MD":"30BF3E","AVVL":"30FF3D","Xi":"313F3C","BLA":"317F3B","CeM":"31BF3A","BMA":"31FF39","VRe":"323F38","RSD":"327F37","RSGc":"32BF36","VLH":"32FF35","AVDM":"333F34","IAD":"337F33","SO":"33BF32","PaV":"33FF31","PaMM":"343F30","VA":"347F2F","ESO":"34BF2E","AMV":"34FF2D","PaXi":"353F2C","sox":"357F2B","IPAC":"35BF2A","AHC":"35FF29","IAM":"363F28","MeAD":"367F27","SPa":"36BF26","PaLM":"36FF25","LDVL":"373F24","ZI":"377F23","CeC":"37BF22","CeL":"37FF21","MHb":"383F20","BAOT":"387F1F","VPL":"38BF1E","IM":"38FF1D","PaDC":"393F1C","PaMP":"397F1B","S1Sh":"39BF1A","Or":"39FF19","Py":"3A3F18","CA3":"3A7F17","DG":"3ABF16","LDDM":"3AFF15","VL":"3B3F14","Rh":"3B7F13","VM":"3BBF12","ZIR":"3BFF11","AHP":"3C3F10","RCh":"3C7F0F","dhc":"3CBF0E","mt":"3CFF0D","ASt":"3D3F0C","Sub":"3D7F0B","La":"3DBF0A","RChL":"3DFF09","Cir":"3E3F08","MeAV":"3E7F07","LHb":"3EBF06","GrDG":"3EFF05","MoDG":"3F3F04","SLu":"3F7F03","Rad":"3FBF02","BLV":"3FFF01","PaPo":"403F00","ns":"407EFF","A13":"40BEFE","MDL":"40FEFD","EP":"413EFC","TuLH":"417EFB","CA2":"41BEFA","alv":"41FEF9","PoDG":"423EF8","VMH":"427EF7","CL":"42BEF6","VMHSh":"42FEF5","MDM":"433EF4","MDC":"437EF3","LaDL":"43BEF2","VPM":"43FEF1","Arc":"443EF0","CA1":"447EEF","MeA":"44BEEE","PLCo":"44FEED","al":"453EEC","IMD":"457EEB","Stg":"45BEEA","S1Tr":"45FEE9","Ect":"463EE8","PRh":"467EE7","LMol":"46BEE6","Po":"46FEE5","SubI":"473EE4","DM":"477EE3","STIA":"47BEE2","MePD":"47FEE1","MePV":"483EE0","VMHDM":"487EDF","VMHC":"48BEDE","VMHVL":"48FEDD","SI":"493EDC","SOR":"497EDB","hif":"49BEDA","aot":"49FED9","fr":"4A3ED8","AngT":"4A7ED7","LaVL":"4ABED6","LPMR":"4AFED5","ZID":"4B3ED4","ZIV":"4B7ED3","LPtA":"4BBED2","MPtA":"4BFED1","BLP":"4C3ED0","DLG":"4C7ECF","PG":"4CBECE","MCLH":"4CFECD","ME":"4D3ECC","PeF":"4D7ECB","LHbM":"4DBECA","BMP":"4DFEC9","AuV":"4E3EC8","LaVM":"4E7EC7","LHbL":"4EBEC6","STh":"4EFEC5","DA":"4F3EC4","OPC":"4F7EC3","eml":"4FBEC2","ml":"4FFEC1","ArcD":"503EC0","ArcL":"507EBF","FC":"50BEBE","RAPir":"50FEBD","LPLR":"513EBC","PMCo":"517EBB","DMV":"51BEBA","DMD":"51FEB9","PHD":"523EB8","Te":"527EB7","MTu":"52BEB6","cp":"52FEB5","TeA":"533EB4","DMC":"537EB3","hbc":"53BEB2","PVP":"53FEB1","scp":"543EB0","AHiAL":"547EAF","VPPC":"54BEAE","PtPR":"54FEAD","PTPR":"553EAC","DLEnt":"557EAB","RRe":"55BEAA","A12":"55FEA9","PoMn":"563EA8","AuD":"567EA7","PF":"56BEA6","SPF":"56FEA5","PH":"573EA4","PSTh":"577EA3","PtPD":"57BEA2","RSGb":"57FEA1","ArcM":"583EA0","IMA":"587E9F","PGMC":"58BE9E","PGPC":"58FE9D","Au1":"593E9C","APTD":"597E9B","PrC":"59BE9A","SubG":"59FE99","LH":"5A3E98","PMV":"5A7E97","Me":"5ABE96","FF":"5AFE95","PR":"5B3E94","V2L":"5B7E93","V1":"5BBE92","V2ML":"5BFE91","V2MM":"5C3E90","VTM":"5C7E8F","ArcLP":"5CBE8E","ArcMP":"5CFE8D","DTM":"5D3E8C","SMT":"5D7E8B","Gem":"5DBE8A","SCO":"5DFE89","pc":"5E3E88","IGL":"5E7E87","A11":"5EBE86","LPMC":"5EFE85","AHiPM":"5F3E84","DS":"5F7E83","SPFPC":"5FBE82","RI":"5FFE81","F":"603E80","PMD":"607E7F","str":"60BE7E","OPT":"60FE7D","MPT":"613E7C","SNR":"617E7B","RMM":"61BE7A","VLi":"61FE79","scc":"623E78","Eth":"627E77","AHiPL":"62BE76","p1PAG":"62FE75","mtg":"633E74","Sc":"637E73","LT":"63BE72","bsc":"63FE71","SNC":"643E70","APir":"647E6F","REth":"64BE6E","LM":"64FE6D","ML":"653E6C","MM":"657E6B","MnM":"65BE6A","MRe":"65FE69","RML":"663E68","PCom":"667E67","APTV":"66BE66","PAG":"66FE65","fmj":"673E64","RPF":"677E63","MCPC":"67BE62","Lth":"67FE61","PIL":"683E60","rmx":"687E5F","PP":"68BE5E","PLi":"68FE5D","OT":"693E5C","pm":"697E5B","PPT":"69BE5A","PoT":"69FE59","LPLC":"6A3E58","SNL":"6A7E57","Dk":"6ABE56","MGV":"6AFE55","MGD":"6B3E54","VTAR":"6B7E53","SG":"6BBE52","MGM":"6BFE51","SNCD":"6C3E50","PrEW":"6C7E4F","PBP":"6CBE4E","mp":"6CFE4D","RM":"6D3E4C","VTA":"6D7E4B","ZIC":"6DBE4A","p1Rt":"6DFE49","Op":"6E3E48","InG":"6E7E47","InWh":"6EBE46","DIEnt":"6EFE45","Aq":"6F3E44","MZMG":"6F7E43","InC":"6FBE42","InCSh":"6FFE41","SuG":"703E40","IPF":"707E3F","IF":"70BE3E","RPC":"70FE3D","APT":"713E3C","DpG":"717E3B","csc":"71BE3A","V1M":"71FE39","RSGa":"723E38","V1B":"727E37","PN":"72BE36","MA3":"72FE35","Zo":"733E34","DpWh":"737E33","RLi":"73BE32","SNCM":"73FE31","MT":"743E30","IPR":"747E2F","RMC":"74BE2E","mRt":"74FE2D","vtgx":"753E2C","VS":"757E2B","Post":"75BE2A","IPC":"75FE29","LPAG":"763E28","PlPAG":"767E27","PIF":"76BE26","DMPAG":"76FE25","IPL":"773E24","3n":"777E23","DT":"77BE22","Pi":"77FE21","VIEnt":"783E20","mlf":"787E1F","IPI":"78BE1E","DLPAG":"78FE1D","IPDL":"793E1C","IPDM":"797E1B","SubB":"79BE1A","bic":"79FE19","PaR":"7A3E18","RRF":"7A7E17","EW":"7ABE16","Su3C":"7AFE15","bas":"7B3E14","3N":"7B7E13","Su3":"7BBE12","Pn":"7BFE11","rs":"7C3E10","dtgx":"7C7E0F","tfp":"7CBE0E","BIC":"7CFE0D","3PC":"7D3E0C","STr":"7D7E0B","PrS":"7DBE0A","MG":"7DFE09","A8":"7E3E08","MEnt":"7E7E07","MnR":"7EBE06","PMnR":"7EFE05","ts":"7F3E04","CLi":"7F7E03","DR":"7FBE02","B9":"7FFE01","IPA":"803E00","xscp":"807DFF","PrCnF":"80BDFE","IP":"80FDFD","VLPAG":"813DFC","PaS":"817DFB","PnO":"81BDFA","R":"81FDF9","ECIC":"823DF8","PTg":"827DF7","PL":"82BDF6","ll":"82FDF5","ATg":"833DF4","PBG":"837DF3","CEnt":"83BDF2","VLL":"83FDF1","RtTg":"843DF0","MiTg":"847DEF","Me5":"84BDEE","RR":"84FDED","lfp":"853DEC","Rbd":"857DEB","RtTgP":"85BDEA","mcp":"85FDE9","m5":"863DE8","DRD":"867DE7","ILL":"86BDE6","Pa4":"86FDE5","4N":"873DE4","DRV":"877DE3","DRL":"87BDE2","PDR":"87FDE1","ERS":"883DE0","4Sh":"887DDF","SPTg":"88BDDE","TrLL":"88FDDD","MPL":"893DDC","PLV":"897DDB","DRI":"89BDDA","vsc":"89FDD9","DLL":"8A3DD8","MVPO":"8A7DD7","CAT":"8ABDD6","5N":"8AFDD5","Sag":"8B3DD4","VTg":"8B7DD3","12":"8BBDD2","LVPO":"8BFDD1","4n":"8C3DD0","s5":"8C7DCF","A7":"8CBDCE","Pr5":"8CFDCD","Tz":"8D3DCC","P5":"8D7DCB","LDTgV":"8DBDCA","CnF":"8DFDC9","23":"8E3DC8","cic":"8E7DC7","KF":"8EBDC6","LDTg":"8EFDC5","CIC":"8F3DC4","Su5":"8F7DC3","RMg":"8FBDC2","5TT":"8FFDC1","py":"903DC0","DMTg":"907DBF","DCIC":"90BDBE","4/5Cb":"90FDBD","LPB":"913DBC","MPB":"917DBB","2Cb":"91BDBA","SubCV":"91FDB9","cll":"923DB8","SubCD":"927DB7","LPBS":"92BDB6","8n":"92FDB5","VCA":"933DB4","PnC":"937DB3","Pr5VL":"93BDB2","Sim":"93FDB1","Fl":"943DB0","DPO":"947DAF","LSO":"94BDAE","SPO":"94FDAD","DTgP":"953DAC","DRC":"957DAB","PnR":"95BDAA","5ADi":"95FDA9","Pr5DM":"963DA8","me5":"967DA7","LPBV":"96BDA6","LPBE":"96FDA5","LPBC":"973DA4","3Cb":"977DA3","PFl":"97BDA2","PnV":"97FDA1","DTgC":"983DA0","5Tr":"987D9F","1V":"98BD9E","RIP":"98FD9D","MPBE":"993D9C","4V":"997D9B","LPBD":"99BD9A","7n":"99FD99","LPBI":"9A3D98","4Cb":"9A7D97","A5":"9ABD96","PCRtA":"9AFD95","CGA":"9B3D94","Bar":"9B7D93","LC":"9BBD92","tz":"9BFD91","CGB":"9C3D90","SubCA":"9C7D8F","5Te":"9CBD8E","5Ma":"9CFD8D","prf":"9D3D8C","VCAGr":"9D7D8B","MSO":"9DBD8A","RPa":"9DFD89","pfs":"9E3D88","plf":"9E7D87","sp5":"9EBD86","Crus1":"9EFD85","IRt":"9F3D84","SMV":"9F7D83","MVe":"9FBD82","SuVe":"9FFD81","psf":"A03D80","pcn":"A07D7F","CGO":"A0BD7E","PCGS":"A0FD7D","un":"A13D7C","Sph":"A17D7B","ocb":"A1BD7A","pcuf":"A1FD79","CG":"A23D78","GiA":"A27D77","LPGi":"A2BD76","SuS":"A2FD75","GrC":"A33D74","EVe":"A37D73","LR4V":"A3BD72","6RB":"A3FD71","MVeMC":"A43D70","MVePC":"A47D6F","PDTg":"A4BD6E","icp":"A4FD6D","8vn":"A53D6C","CPO":"A57D6B","DC":"A5BD6A","Gi":"A5FD69","Pa6":"A63D68","6N":"A67D67","7N":"A6BD66","P7":"A6FD65","Sp5O":"A73D64","Lat":"A77D63","veme":"A7BD62","CGG":"A7FD61","PPy":"A83D60","LVe":"A87D5F","1Cb":"A8BD5E","VCP":"A8FD5D","DMSp5":"A93D5C","IntA":"A97D5B","IS":"A9BD5A","g7":"A9FD59","Pr":"AA3D58","DCMo":"AA7D57","7SH":"AABD56","I8":"AAFD55","DCDp":"AB3D54","DCFu":"AB7D53","SGe":"ABBD52","VeCb":"ABFD51","Crus2":"AC3D50","VCPO":"AC7D4F","Med":"ACBD4E","vesp":"ACFD4D","DPGi":"AD3D4C","icf":"AD7D4B","LPGiA":"ADBD4A","LatPC":"ADFD49","7DI":"AE3D48","7VI":"AE7D47","7L":"AEBD46","7DL":"AEFD45","7VM":"AF3D44","7DM":"AF7D43","Y":"AFBD42","acs7":"AFFD41","VCCap":"B03D40","LPGiE":"B07D3F","IntDL":"B0BD3E","Inf":"B0FD3D","SpVe":"B13D3C","Sp5I":"B17D3B","10Cb":"B1BD3A","X":"B1FD39","IntP":"B23D38","SolIM":"B27D37","5Sol":"B2BD36","ROb":"B2FD35","sol":"B33D34","das":"B37D33","MedDL":"B3BD32","cbc":"B3FD31","C3":"B43D30","IntPPC":"B47D2F","B4":"B4BD2E","SolI":"B4FD2D","SolV":"B53D2C","10N":"B57D2B","SolM":"B5BD2A","ppf":"B5FD29","6Cb":"B63D28","PM":"B67D27","MedL":"B6BD26","C1":"B6FD25","RVL":"B73D24","EF":"B77D23","apmf":"B7BD22","PCRt":"B7FD21","GiV":"B83D20","Bo":"B87D1F","Mx":"B8BD1E","Amb":"B8FD1D","9Cb":"B93D1C","CI":"B97D1B","Cop":"B9BD1A","FVe":"B9FD19","IOM":"BA3D18","IOPr":"BA7D17","IOD":"BABD16","ECu":"BAFD15","PrBo":"BB3D14","CVL":"BB7D13","SolL":"BBBD12","IODM":"BBFD11","SolDM":"BC3D10","Li":"BC7D0F","8Cb":"BCBD0E","12N":"BCFD0D","Ro":"BD3D0C","C2":"BD7D0B","7Cb":"BDBD0A","Cu":"BDFD09","In":"BE3D08","PMn":"BE7D07","SolCe":"BEBD06","LRt":"BEFD05","RVRG":"BF3D04","IOVL":"BF7D03","IOK":"BFBD02","Pa5":"BFFD01","PSol":"C03D00","SolDL":"C07CFF","SolVL":"C0BCFE","SolG":"C0FCFD","AP":"C13CFC","sf":"C17CFB","IOBe":"C1BCFA","MdD":"C1FCF9","11n":"C23CF8","MdV":"C27CF7","cbw":"C2BCF6","IOC":"C2FCF5","SubP":"C33CF4","SolC":"C37CF3","IOB":"C3BCF2","InM":"C3FCF1","CC":"C43CF0","C1/A1":"C47CEF","Sp5C":"C4BCEE","cu":"C4FCED","IOA":"C53CEC","CeCv":"C57CEB","CuR":"C5BCEA","Gr":"C5FCE9","12n":"C63CE8","12GH":"C67CE7","vert":"C6BCE6","gr":"C6FCE5","LRtPC":"C73CE4","dsc":"C77CE3","pyx":"C7BCE2","RAmb":"C7FCE1","11N":"C83CE0","A1":"C87CDF","A2":"C8BCDE","MnA":"C8FCDD"}

CONF_STRUCTURES_LIMITED=[]

# Slides aligner reference coords:
CONF_ALIGNER_REFERENCE_COORDS =\
        (-6.06467941507, -2.37689628048, 0.0112372176649, 0.0112485939258)
