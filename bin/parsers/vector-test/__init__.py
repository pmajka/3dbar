#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import datetime

from bar import parsers as bar

renderingProperties = {}
renderingProperties['imageSize'] = (1008 * 3, 1008 * 3)
renderingProperties['ReferenceWidth']  = 1008 
renderingProperties['ReferenceHeight'] = 1008

potraceProperties    = {}
potraceProperties['potrace_accuracy_parameter']   ='0.001'
potraceProperties['potrace_svg_resolution_string']='300x300'
potraceProperties['potrace_width_string']   =      '1008pt'
potraceProperties['potrace_height_string']  =      '1008pt'

tracerSettings={}
tracerSettings['DumpEachStepSVG']          = False 
tracerSettings['DumpEachStepPNG']          = False
tracerSettings['DumpWrongSeed']            = True 
tracerSettings['DumpVBrain']               = False 
tracerSettings['DumpDirectory']            = 'atlases/vector-test/src/'
tracerSettings['DetectUnlabelled']         = True
tracerSettings['CacheLevel']               = 5
tracerSettings['MinFiterTimesApplication'] = 3
tracerSettings['GrowDefaultBoundaryColor'] = 200
tracerSettings['RegionAlreadyTraced']      = 100
tracerSettings['UnlabelledTreshold']       = 500
tracerSettings['PoTraceConf'] = potraceProperties
tracerSettings['NewPathIdTemplate'] = 'structure%d_%s_%s'

filenameTempates = dict(traced='%d_traced_v%d.svg',\
                        pretraced='%s_pretrace_pretrace_v%d.svg')

indexerProps = [\
        ('ReferenceWidth', '1008'),
        ('ReferenceHeight', '1008'),
        ('FilenameTemplate', str('%d_traced_v%d.svg')),
        ('RefCords', '-9.5150660793,-1.535588442565,0.0176211453744,0.0176211453744'),
        ('CAFSlideOrientation', 'coronal'),
        ('CAFSlideUnits', 'mm'),
        ('CAFName', 'PW_RBSC_6th'),
        ('CAFComment', 'CAF dataset based on: George Paxinos, Charles Watson,\
                The rat brain in stereotactic coordinates, 6th edition.\
                Ontology tree created by, P. Majka, E, Kublik\
                Nencki Institute of Experimental Biology'),
        ('CAFCompilationTime', datetime.datetime.utcnow().strftime("%F %T")),
        ('CAFCreator', 'pmajka@nencki.gov.pl'),
        ('CAFCreatorEmail','pmajka@nencki.gov.pl')]


slideRange = range(44,205)
#slideRange = range(102,205)

colorMapping=\
{u'MA3': '5D8AA8', u'gr': 'F0F8FF', u'CPO': 'E32636', u'VMHDM': 'EFDECD',
u'Su3C': 'E52B50', u'scc': 'CD2682', u'GrDG': '9F2B68', u'SIB': 'ED3CCA',
u'7Cb': 'F19CBB', u'LPAG': 'AB274F', u'alv': 'FFBF00', u'SPa': 'FF7E00',
u'5Sol': 'CC8899', u'scp': 'FF033E', u'VMHSh': '00DDDD', u'GiV': '9966CC',
u'tz': 'A4C639', u'ts': '915C83', u'MedL': 'FAEBD7', u'LaDL': '91A3B0', u'GiA':
'0000FF', u'SPO': '008000', u'VM': '00755E', u'InC': '8DB600', u'CPu': 'FBCEB1',
u'SPF': '00FFFF', u'g7': '7FFFD0', u'Sp5O': 'F2F3F4', u'AHiAL': '3B444B',
u'CGPn': 'E9D66B', u'vert': 'B2BEB5', u'GP': '87A96B', u'Sp5C': 'FF9966',
u'SpV': '6D351A', u'Cir': 'FDEE00', u'SimA': '6E7F80', u'PSTh': 'FF2052',
u'apmf': 'E9692C', u'LPMR': 'FFF5EE', u'AHC': '89CFF0', u'AHA': 'A1CAF1',
u'LHb': 'F4C2C2', u'SNL': 'FAE7B5', u'AngT': '848482', u'AHP': '98777B',
u'SuML': 'BCD4E6', u'SNR': '9F8170', u'Gl': 'F5F5DC', u'Gi': '3D2B1F', u'aci':
'CB4154', u'VLi': 'FE6F5E', u'10n': 'FFEBCD', u'DTM': '318CE7', u'pms':
'ACE5EE', u'3V': 'FAF0BE', u'me5': '0000FF', u'10Cb': '333399', u'M1': '0247FE',
u'3N': 'A2A2D0', u'EPlA': '6699CC', u'M2': '00DDDD', u'E-OV': 'DE5D83', u'VLH':
'79443B', u'LSD': '0095B6', u'10N': 'CC0000', u'VLL': '0070FF', u'CeCv':
'B5A642', u'LSO': 'CB4154', u'REth': '1DACD6', u'EVe': '66FF00', u'VLG':
'BF94E4', u'LSI': 'C32148', u'LSV': 'FF007F', u'PaLM': '08E8DE', u'LSS':
'D19FE8', u'IOVL': 'F4BBFF', u'GrA': 'FF55A3', u'GrO': 'FB607F', u'LPBCr':
'004225', u'ZL': 'CD7F32', u'ZI': '964B00', u'Sim': 'E34234', u'S1BF': 'A52A2A',
u'BLV': 'FFC1CC', u'Mi': 'E7FEFF', u'BLP': 'F0DC82', u'VLPAG': '480607',
u'PiSt': '800020', u'STMAL': 'DEB887', u'STMAM': 'CC5500', u'MiTg': 'E97451',
u'Sp5I': '8A3324', u'IGL': 'BD33A4', u'BLA': '702963', u'Mx': '536872', u'VTAR':
'5F9EA0', u'ME': '91A3B0', u'MD': '006B3C', u'Zo': 'F88379', u'mfba': 'EEE8AA',
u'MM': 'FFF600', u'ML': '1E4D2B', u'31': 'A3C1AD', u'PBG': '0247FE', u'hbc':
'78866B', u'MT': 'FFEF00', u'MV': 'FF0800', u'MS': 'E4717A', u'Su3': 'A2A2D0',
u'PLH': '0FC0FC', u'MnM': '6699CC', u'SolRL': 'C41E3A', u'SolL': '00CC99',
u'SolM': '960018', u'FV': 'EB4C42', u'9n': 'FF0038', u'S2': 'FFA6C9', u'S1':
'B31B1B', u'SMT': '99BADD', u'SolC': 'ED9121', u'PnV': '92A1CF', u'FC':
'ACE1AF', u'xicp': '4997D0', u'RIP': 'FADADD', u'PnO': 'EC3B83', u'MnA':
'FF033E', u'SolV': '2A52BE', u'PnC': 'F7E7CE', u'EW': 'CF1020', u'V2MM':
'DFFF00', u'V2ML': '7FFF00', u'PrCnF': 'FFB7C5', u'Fu': 'CD5C5C', u'MDL':
'7B3F00', u'MDM': 'FFA700', u'MDC': '98817B', u'La': '734F96', u'LPBC':
'D2691E', u'chp': 'E4D00A', u'4-5Cb': 'FBCCE7', u'5Cb': '00FF6F', u'AuV':
'0047AB', u'AP': '08457E', u'Fl': '9BDDFF', u'APTD': '8FCFD1', u'SubV':
'002E63', u'Stg': '8C92AC', u'RLi': 'B87333', u'4Sh': '996666', u'F': 'FF3800',
u'Sp': 'FF7F50', u'8cn': 'F88379', u'aca': '0095B6', u'MdD': '893F45', u'Au1':
'FBEC5D', u'SubG': 'B31B1B', u'pfs': 'FFD12A', u'SubB': 'FFF8DC', u'V':
'FFF8E7', u'Sc': 'FFBCD9', u'MPB': 'CC0000', u'InG': 'DC143C', u'MdV': 'BE0032',
u'SubI': '00FFFF', u'StA': '00B7EB', u'f': 'FFFF31', u'LPGiE': 'F0E130', u'ml':
'00008B', u'LPGiA': '654321', u'DLEnt': 'E4D96F', u'ST': 'A40000', u'mt':
'08457E', u'SO': 'C2B280', u'mp': '986960', u'LTe': 'DAA520', u'MoCb': '000000',
u'VEn': '536878', u'SG': 'B8860B', u'LPtA': '013220', u'JPLH': '1A2421',
u'SolIM': 'BDB76B', u'Ld': '483C32', u'ERS': 'E34234', u'mofr': '66FF00',
u'CnFV': '003366', u'CAT': '556B2F', u'AcbSh': 'FF8C00', u'CnFI': '779ECB',
u'BAC': '03C03C', u'AID': 'F28500', u'DPO': '966FD6', u'CnFD': 'C23B22', u'ic':
'FFCC00', u'PMD': 'FFF600', u'gcc': '003399', u'OPC': 'FF6FFF', u'LC': '872657',
u'LA': '8B0000', u'MiA': 'E9967A', u'LO': '560319', u'LM': '3C1414', u'IntPPC':
'2F4F4F', u'MPT': 'FF007F', u's5': 'FF003F', u'1': 'FFA812', u'LT': '483C32',
u'acp': '08E8DE', u'VPM': '00CED1', u'cst': '9400D3', u'JxO': '00693E', u'A':
'5218FA', u'fr': 'DA9100', u'vsc': 'FFA6C9', u'sp5': 'DA3287', u'AHiPM':
'FAD6A5', u'AHiPL': 'B94E48', u'aot': 'C154C1', u'fi': '004B49', u'a': 'CC00CC',
u'LHbM': 'F4BBFF', u'PlPAG': 'FF1493', u'DMTg': 'FF9933', u'SimB': '00BFFF',
u'D3V': '014421', u'CA2': 'C19A6B', u'CA1': 'EDC9AF', u'STh': '696969', u'st':
'1E90FF', u'123': '77DD77', u'sm': 'D71868', u'InCSh': '85BB65', u'9a,bCb':
'967117', u'sf': '00009C', u'Rt': 'E1A95F', u'rLL': 'C2B280', u'6Cb': '614051',
u'SM': 'CD5B45', u'PRh': 'F0EAD6', u'Re': '1034A6', u'tth': '7DF9FF', u'csc':
'918151', u'Ro': '00FF00', u'Rh': '6F00FF', u'SolVL': 'F4BBFF', u'cll':
'CCFF00', u'LV': 'BF00FF', u'AOE': '3F00FF', u'AOD': '8F00FF', u'21': 'FFFF00',
u'IPDM': '50C878', u'23': '96C8A2', u'lo': 'C19A6B', u'AOM': '801818', u'AOL':
'B53389', u'iml': 'F400A1', u'SPTg': 'E5AA70', u'AOV': '4D5D53', u'STSL':
'4F7942', u'GI': '007FFF', u'AOP': '6C541E', u'RL': 'B22222', u'RCh': 'E2725B',
u'RI': 'E25822', u'ZIV': 'F7E98E', u'CeL': 'F08080', u'ZIR': 'FF004F', u'PrC':
'228B22', u'PrL': 'A67B5B', u'L': '0072BB', u'IPl': '86608E', u'LPO': 'F64A8A',
u'ZID': 'FF00FF', u'MEntR': 'FF77FF', u'icpx': 'E48400', u'ZIC': 'CC6666',
u'PrS': 'DCDCDC', u'SFi': 'E49B0F', u'LPB': 'F8F8FF', u'Gr': '6082B6', u'SubCV':
'D4AF37', u'IPC': 'FFD700', u'STMPM': '996515', u'STMPL': 'FCC200', u'IPF':
'FFDF00', u'STMPI': 'A8E4A0', u'IPI': '808080', u'Sag': '465945', u'IPL':
'00FF00', u'DpG': '008000', u'SFO': '00A550', u'SubCD': '66B032', u'SubCA':
'ADFF2F', u'PeFLH': 'A99A86', u'MRe': '00FF7F', u'2bCb': '663854', u'MeAD':
'F984EF', u'STD': '555555', u'APir': 'E9D66B', u'VA': '0ABAB5', u'DCGr':
'C90016', u'PaPo': '00B7EB', u'ec': 'DF73FF', u'DLPAG': 'F0FFF0', u'HDB':
'726631', u'sox': '800020', u'ICjM': 'D1E231', u'PoMn': 'DEB887', u'Sph':
'71A6D2', u'BMA': 'FCF75E', u'LPLR': 'B2EC5D', u'rs': '138808', u'SuMM':
'E3A857', u'BMP': '00416A', u'MCPC': '4B0082', u'BAOT': 'CC5500', u'5TT':
'FF4F00', u'LPLC': '5A4FCF', u'E5': 'CD9575', u'dsc': '009000', u'MCPO':
'FFFFF0', u'MVPO': '00A86B', u'asp': 'D73B3E', u'DLG': 'A50B5E', u'PVP':
'B19CD9', u'LPBV': 'BDDA57', u'EF': '29AB87', u'EA': '4CBB17', u'LPBS':
'C3B091', u'DLL': 'F0E68C', u'5Ma': '087830', u'RAPir': 'D6CADD', u'LPBI':
'26619C', u'CST': 'FEFE22', u'LPBD': '36454F', u'LPBE': 'B57EDC', u'EP':
'E6E6FA', u'VP': 'DEAA88', u'SolDM': 'C4C3D0', u'SolDL': '9457EB', u'MGD':
'EE82EE', u'SHy': '008B8B', u'MGM': '967BB6', u'vtgx': 'FBA0E3', u'MGV':
'7CFC00', u'MPtA': 'FFF700', u'PMCo': 'FFFACD', u'SHi': 'FDD5B1', u'SChDL':
'FD0E35', u'CeC': 'ADD8E6', u'MeAV': 'B5651D', u'CeM': 'E66771', u'7ni':
'EEDC82', u'ECu': 'E0FFFF', u'RMg': '446CCF', u'MoDG': 'FAFAD2', u'SChVM':
'D99058', u'Eth': '536895', u'VPPC': '8B4513', u'ATg': 'FADA5E', u'FrA':
'FFB6C1', u'PMnR': '7B3F00', u'LRtPC': 'FF5C5C', u'RMC': '87CEEB', u'1b':
'778899', u'fmj': 'B38B6D', u'fmi': 'E68FAC', u'Post': 'FFFFED', u'VTA':
'20B2AA', u'8Cb': '00FF00', u'B': '32CD32', u'IMD': 'FAF0E6', u'IMG': '534B4F',
u'IntDM': 'E62020', u'VTM': 'FFBD88', u'PDR': 'FF00FF', u'Fr3': 'FF0090',
u'RAmb': 'AAF0D1', u'ictd': 'F8F4FF', u'vlh': '4B5320', u'GrC': 'DE3163',
u'Rbd': 'FBEC5D', u'tfp': '6050DC', u'Xi': '979AAA', u'CLi': 'FF8243', u'VMH':
'800000', u'PLCo1': 'B03060', u'vBrain': 'E0B0FF', u'LAcbSh': '915F6D', u'CA3':
'1560BD', u'r': '73C2FB', u'MPOL': 'E5B73B', u'GlA': 'ED872D', u'LMol':
'0000CD', u'AmbC': 'A3C1AD', u'RtTg': 'E2062C', u'IMA': 'BFFF00', u'DM':
'F3E5AB', u'DI': '1C352D', u'PoDG': 'DDA0DD', u'DG': '0067A5', u'DTgC':
'9370DB', u'STMV': 'BB3385', u'LaVM': 'C19A6B', u'DA': 'C9DC87', u'RPa':
'00FA9A', u'V1M': '48D1CC', u'V1B': 'FDBCB4', u'DTgP': '191970', u'DT':
'004953', u'STMA': 'FFC40C', u'DR': '3EB489', u'DS': '98FF98', u'Pir1':
'FFE4E1', u'ASt': 'FAEBD7', u'xscp': 'CCCCFF', u'PaS': '73A9C2', u'Dk':
'AE0C00', u'PaV': 'ADDFAD', u'Unlabeled': '30BA8F', u'7L': '997A8D', u'PaXi':
'C54B8C', u'BIC': 'FFDB58', u'RPC': '21421E', u'Ect': '006633', u'POH':
'F6ADC6', u'VTT1': '2A8000', u'S1HL': 'FADA5E', u'PSol': '9955BB', u'DTT':
'000080', u'LPGi': 'FFA343', u'pyx': 'A4DDED', u'IPACL': '01796F', u'PaAP':
'008000', u'GrCb': '8A2BE2', u'Pa5': 'FDF5E6', u'Pa6': '796878', u'PS':
'FFC0CB', u'IRtA': '674C47', u'TuLH': '808000', u'PoT': '6B8E23', u'PCom':
'3C341F', u'M': '9AB973', u'VCP': 'B784A7', u'S1FL': 'FF7F00', u'PtPC':
'FB9902', u'PtPD': 'FFA500', u'VCCap': 'FF9F00', u'PV': 'F78FA7', u'bsc':
'DA70D6', u'2': 'FFD1DC', u'Aq': '779ECB', u'SLu': '654321', u'MCLH': '414A4C',
u'p1PAG': '0F4D92', u'imvc': 'FF6E4A', u'VMPO': '002147', u'VTT': 'C04000',
u'ArcLP': '273BE2', u'DCl': '682860', u'5MHy': 'DDBEC3', u'MoS': 'BCD4E6',
u'DCMo': 'AFEEEE', u'12n': '987654', u'6RB': '21ABCD', u'PAG': '9BC4E2',
u'STIA': 'DDADAF', u'AL': '654321', u'och': 'DA8A67', u'3ECIC': 'ABCDEF',
u'mfbb': 'E6BE8A', u'eMC': 'E30022', u'ocb': 'F984E5', u'12N': 'DE3163', u'3Cb':
'DDA0DD', u'MPBE': 'DB7093', u'5ADi': '96DED1', u'VCAGr': 'C9C0BB', u'3n':
'BC987E', u'IAM': '78184A', u'MEE': '00CC99', u'pcuf': 'FFFF31', u'df':
'50C878', u'IAD': 'AEC6CF', u'PLCo': 'CFCFC4', u'b': 'ECEBBD', u'3/4': 'F49AC2',
u'hif': 'FFB347', u'X': '00FFFF', u'PH': 'FF6961', u'KF': 'CB99C9', u'bas':
'FDFD96', u'PCRt': '40404F', u'eml': 'FFE5B4', u'PHA': 'FFCC99', u'IPAC':
'EB4C42', u'mcer': 'FADFAD', u'PHD': 'FF69B4', u'dtgx': 'F0EAD6', u'4V':
'00B7EB', u'8vn': 'E6E200', u'Pr': '1C39BB', u'DMC': '32127A', u'DMD': 'D3D3D3',
u'Py': 'F77FBE', u'DMV': '701C1C', u'Pe': 'CC3333', u'Pk': 'FE28A2', u'Pi':
'EC5800', u'Pn': '000F89', u'Po': '123524', u'PR': 'CC7722', u'IPACM': '673147',
u'PP': 'FF9966', u'p1Rt': 'E7ACCF', u'Pr5VL': 'FF4500', u'PT': '93C572',
u'6aCb': 'F4F0EC', u'dlo': '8E4585', u'RChL': 'DDA0DD', u'MedDL': 'FFA07A',
u'PC': 'B0E0E6', u'3': 'FF8F00', u'PF': '003153', u'DIEnt': 'DD00FF', u'9cCb':
'836953', u'ECIC3': '0F0F0F', u'PN': '800080', u'VG1': 'A020F0', u'PL':
'69359C', u'PM': '9678B6', u'C': 'FE4EDA', u'CxA1': '50404D', u'P7': 'FDDDE6',
u'P5': 'E5E4E2', u'asc7': 'E30B5D', u'MPOM': '66DDAA', u'S1Sh': '915F6D',
u'APTV': 'E25098', u'MPOC': 'B3446C', u'azac': '826644', u'DCDp': 'FF33CC',
u'Pr5DM': 'E3256B', u'OPT': 'FF0000', u'RR': 'EF3038', u'unx': 'FE2712', u'7SH':
'A52A2A', u'IPDL': 'C71585', u'MHb': 'AB4E52', u'SPFPC': 'E25098', u'PeF':
'FF7518', u'LDTg': 'F1A7FE', u'InfS': 'D70040', u'll': '0892D0', u'dsc-oc':
'A76BCF', u'aa': '4997D0', u'MePD': 'B03060', u'Bo': 'FFA089', u'AcbC':
'AF4035', u'cc': '00CCCC', u'ILL': 'FF007F', u'cg': 'F9429E', u'PCGS': '674846',
u'LR4V': 'CA1F7B', u'prf': 'E32636', u'VRe': 'FF66CC', u'9Cb': 'AA98A9', u'cp':
'905D5D', u'cu': 'AB4E52', u'S1DZO': '65000B', u'Lth': 'D40000', u'VMHC':
'BC8F8F', u'Pir1a': '0038A8', u'DCIC': '002366', u'Sol': '014421', u'6bCb':
'CA2C92', u'DCFu': '6B3FA0', u'pc': 'E0115F', u'VVL': 'FFFFFF', u'VIEnt':
'FF0028', u'C3': 'BB6528', u'C2': 'E18E96', u'C1': 'A81C07', u'PCRtA': '80461B',
u'4Cb': 'B7410E', u'Gem': '00563F', u'STSM': 'FF2800', u'6a': 'FF6700', u'6b':
'F4C430', u'lofr': '23297A', u'IntA': 'FF8C69', u'CM': 'FF91A4', u'CL':
'00A693', u'CC': '967117', u'CB': 'ECD540', u'CG': 'F4A460', u'6n': '967117',
u'S1T': '92000A', u'S1J': '507D2A', u'PLd': '082567', u'IntP': 'CBA135', u'PLi':
'FF2000', u'VLPO': 'ED1C24', u'PLV': '76FF7A', u'p1': '2E8B57', u'mlf':
'321414', u'LatPC': 'F0FFFF', u'Ge5': 'FFBA00', u'Cl': '704214', u'7DI':
'8A795D', u'MnPO': '009E60', u'7DL': '882D17', u'7DM': 'C0C0C0', u'6N':
'CB410B', u'DMSp5': '87CEEB', u'Cx': 'CF71AF', u'LPMC': '708090', u'str':
'FF355E', u'IEn': '003399', u'mlx': '933D41', u'5b': 'FFEF00', u'MO': '100C08',
u'Cu': 'FFFAFA', u'Ct': '00BFFF', u'DpWh': 'FEFDFF', u'vesp': 'A7FC00', u'is':
'00FF7F', u'AIV': '4682B4', u'AIP': 'FADA5E', u'CVL': '5D3954', u'7VI':
'FFCC33', u'LOT': 'FAD6A5', u'7VM': 'D2B48C', u'ia': 'F94D00', u'Bar': 'F400A1',
u'PPy': 'E75480', u'3PC': '483C32', u'5Pt': '8B8589', u'I8': 'D0F0C0', u'dhc':
'F4C2C2', u'1Cb': '734F96', u'7n': '008080', u'V1': '367588', u'SOR': 'CD5700',
u'InWh': 'CE2029', u'DP': 'D8BFD8', u'PPT': 'DE6FA1', u'ePC': 'FC89AC', u'Cop':
'3FFF00', u'pcer': 'E08D3C', u'RSD': 'EF98AA', u'VG': 'DBD7D2', u'I': 'EEE600',
u'IP': 'FF6347', u'IS': '746CC0', u'ANS': '004040', u'VL': '808080', u'PaR':
'967117', u'VO': '417DC1', u'II': 'FFF0F5', u'VOLT': 'B57281', u'VS': '00FFEF',
u'IM': '823535', u'IL': '8A496B', u'Y': '66023C', u'EAM': '00FF6F', u'PrEW':
'F0E68C', u'IB': 'FFB300', u'Com': '3CD070', u'ID': 'FF9999', u'IG': '4166F5',
u'IF': 'C8A2C8', u'Ve': '0BDA51', u'DPPn': '5B92E5', u'IRt': 'FFFF66', u'PDPO':
'FF5A36', u'MTu': '7B1113', u'LVe': 'AE2029', u'costr': 'E1AD21', u'In':
'990000', u'mfb': 'FFCC00', u'DLO': 'D3003F', u'AmbSC': 'F3E5AB', u'BL':
'C5B358', u'5T': 'C80815', u'DTT1': 'C2B280', u'das': '43B3AE', u'DRV':
'B39EB5', u'DRI': '8F00FF', u'V2L': 'FFD800', u'5N': '7F00FF', u'DRL': 'CCCCFF',
u'RVRG': '990000', u'DRC': 'EE82EE', u'32': '40826D', u'DRD': '922724', u'PIL':
'9F1D35', u'LRtS5': 'DA1D81', u'Tu1': 'E6E6FA', u'PIF': '9F00FF', u'RVL':
'004242', u'C1-A1': '645452', u'EPl': 'F5DEB3', u'321': 'C08081', u'IOK':
'F5F5F5', u'4': 'A2ADD0', u'SMV': 'FF43A4', u'5': '893F45', u'IOD': 'FC0FC0',
u'IOC': 'FC8EAC', u'IOB': '007474', u'IOA': 'FFFF00', u'5a': '738678', u'opt':
'FEFE33', u'PnR': '9ACD32', u'D': '0014A8', u'sumx': '2C1608', u'RPF': '5D8AA8',
u'psf': 'F0F8FF', u'bic': 'FE59C2', u'IPA': 'EFDECD', u'T': 'E52B50', u'ReIC':
'CD2682', u'IOBe': '9F2B68', u'scpd': 'FFDEAD', u'2Cb': 'F19CBB', u'Op':
'AB274F', u'MePV': 'B76E79', u'PDTg': 'FF7E00', u'STLI': '9966CC', u'CEnt':
'A4C639', u'STLJ': 'F2F3F4', u'StHy': 'CD9575', u'VCPO': '915C83', u'STLV':
'FAEBD7', u'STLP': '0000FF', u'OV': '008000', u'Pir': '8DB600', u'OT': 'FBCEB1',
u'B9': '00FFFF', u'ECIC': '7FFFD0', u'SCh': '4B5320', u'VCA': '3B444B', u'PTg':
'E9D66B', u'ROb': 'B2BEB5', u'PtPR': '87A96B', u'VDB': 'FF9966', u'APT':
'6D351A', u'STLD': 'FFBF00', u'Pa4': 'CFB53B', u'VDM': '6E7F80', u'2-3Cb':
'0047AB', u'SuG': 'FF2052', u'IPR': '007FFF', u'SCO': '4169E1', u'LDDM':
'89CFF0', u'6cCb': 'A1CAF1', u'olfa': 'F4C2C2', u'icf': '21ABCD', u'/':
'FAE7B5', u'SuV': 'FFD12A', u'Arc': '848482', u'SuS': '98777B', u'DEn':
'BCD4E6', u'VCl': 'A0785A', u'icp': 'F5F5DC', u'LOT1': 'F0E130', u'AMV':
'FE6F5E', u'12GH': '000000', u'ArcMP': 'FFEBCD', u'PBP': '318CE7', u'12':
'966FD6', u'veme': 'ACE5EE', u'MnR': 'FAF0BE', u'PFl': '0000FF', u'plf':
'333399', u'Su5': 'C19A6B', u'Li': 'FAFEFD', u'LRt': '592720', u'dcw': '007BA7',
u'dcs': '8A2BE2', u'AuD': 'DE5D83', u'SNCV': '79443B', u'IVF': 'FF4040',
u'3-4Cb': 'FFFDD0', u'MPA': '0070FF', u'MPO': 'B5A642', u'DMPAG': 'DCD0FF',
u'11N': '1DACD6', u'oc': '8B008B', u'PaMP': 'BF94E4', u'Me5': 'C32148', u'SNCD':
'177245', u'PaMM': 'CC4E5C', u'LHbL': 'D19FE8', u'SNCM': 'FFCBA4', u'IntDL':
'C9A0DC', u'IC': 'FF55A3', u'VPL': 'FB607F', u'py': '004225', u'ppf': 'CD7F32',
u'RRe': '964B00', u'sol': 'A52A2A', u'ArcD': 'FFC1CC', u'IOPr': 'E7FEFF',
u'DPGi': 'F0DC82', u'Rad': 'E32636', u'ArcL': '480607', u'ArcM': 'FF1DCE',
u'PMn': '355E3B', u'Nv': '002FA7', u'Sub': 'E97451', u'm5': '8A3324', u'PMV':
'BD33A4', u'CuR': '702963', u'CGO': '536872', u'CGA': '5F9EA0', u'RRF':
'8601AF', u'CGB': '006B3C', u'ACo': 'ED872D', u'CGG': 'E30022', u'AmbL':
'A9203E', u'SolCe': '1E4D2B', u'Obex': 'A0785A', u'AOVP': '3CB371', u'LaVL':
'78866B', u'S1DZ': 'FFEF00', u'6': 'FF0800', u'A1-C1': 'E4717A', u'mcp':
'00BFFF', u'IOM': '592720', u'Z': 'C41E3A', u'TS': 'FF7F50', u'cic': 'FFEFD5',
u'LDTgV': '960018', u'ELm': 'FFDAB9', u'MEI': 'FF0038', u'un': '701C1C', u'azp':
'B31B1B', u'pm': '99BADD', u'mtg': 'ED9121', u'vhc': '92A1CF', u'lfp': 'ACE1AF',
u'CIC': 'B666D2', u'cbc': '414833', u'ac': 'EC3B83', u'v': '007BA7', u'Tz':
'2A52BE', u'm': '30D5C8', u'Tu': 'F7E7CE', u'Tr': '36454F', u'CI': 'DFFF00',
u'Al': 'FF8C00', u'MSO': '7FFF00', u'cbw': 'FFB7C5', u'LVPO': 'FDEE00', u'acer':
'CD5C5C', u'Te': 'FFA700', u'SGe': '98817B', u'Or': 'ED3CCA', u'SolI': 'D2691E',
u'EpP': 'E4D00A', u'VMHVL': 'FBCCE7', u'A11': '8878C3', u'SubP': '035096',
u'RtTgP': '635147', u'PrBo': '002E63', u'MEnt': '8C92AC', u'MPL': 'B87333',
u'EAC': '996666', u'mch': 'FF3800', u'AM': '00008B', u'MZMG': 'E34234', u'A1':
'F88379', u'A2': 'FF4040', u'A5': 'FC6C85', u'A7': 'FBEC5D', u'Lat': 'B31B1B',
u'TG': '6495ED', u'RtTgL': 'FFF8DC', u'ns': 'FFF8E7', u'AA': 'FFBCD9', u'E':
'FFFDD0', u'AD': 'DC143C', u'VTg': 'BE0032', u'Med': '00FFFF', u'PaC': '120A8F',
u'Crus1': '9F8170', u'Crus2': '3D2B1F', u'vscx': 'FBAED2', u'PaDC': 'F0FFFF',
u'RtSt': '5D3954', u'4N': 'A40000', u'A13': '9BDDFF', u'AV': 'C2B280', u'ESO':
'986960', u'SolG': 'CD5B45', u'RSGa': '008B8B', u'RSGb': '536878', u'RSGc':
'B8860B', u'ICj': '013220', u'e': 'BDB76B', u'PrMC': '483C32', u'InM': '93CCEA',
u'S1ULp': '8B008B', u'LDVL': '003366', u'IODM': '556B2F', u'SubD': '6495ED',
u'4n': 'AF4035', u'Cg1': '03C03C', u'Cg2': '1A2421', u'SuM': 'C23B22'}

class AtlasParser(bar.barVectorParser):
    def __init__(self, inputDirectory, outputDirectory):
        props = {}
        props['filenameTemplates'] = filenameTempates
        props['slideRange'] = slideRange
        props['structureColours'] = colorMapping
        props['renderingProperties'] = renderingProperties
        props['tracingProperties'] = tracerSettings
        props['inputDirectory'] = inputDirectory
        props['outputDirectory'] = outputDirectory
        
        bar.barVectorParser.__init__(self, **props)
        
        for prop in indexerProps:
            self.indexer.properties = prop
    
    def _getInputFilename(self, slideNumber):
        return bar.barVectorParser._getInputFilename(self, slideNumber, version=1)
     
    def parseAll(self):
        bar.barVectorParser.parseAll(self)
        self.reindex()
        
    def reindex(self):
        bar.barVectorParser.reindex(self)

        #self.indexer.createFlatHierarchy()
        hierarhySourceFilename = os.path.join(self.inputDirectory, 'parents.txt')
        self.indexer.setParentsFromFile(hierarhySourceFilename)
        
        fullnameMappingFile = os.path.join(self.inputDirectory,'fullnames.txt')
        self.indexer.setNameMappingFromFile(fullnameMappingFile, 0 , 1)
        
        self.indexer.colorMapping = self.structureColours
        self.writeIndex()

if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  = 'atlases/vector-test/src/'
        outputDirectory = 'atlases/vector-test/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
