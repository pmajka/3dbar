CONF_PARSER_COMMENT = ['CAF dateset of P&F Mouse Brain In Stereotactic\
        coordinates based on bitmaps provided by Andreas Hess.']
CONF_PARSER_NAME    = ['a_hess_pfmbaisc']
CONF_CONTACT_COMMENT= ['Piotr Majka, Nencki Institute of Experimental Biology']

#conf_fullNameMapping  = dict(map(lambda x: (x,x), imageToStructure.values()))
#conf_structureColours = dict(map(lambda x: ('structure%d' %x, '#%02x%02x%02x' % (x,255-x,128)), range(256)))


conf_bragma={28:4.28, 29:3.92, 30:3.56, 31:3.2, 32:3.08, 33:2.96, 34:2.8, 35:2.68, 36:2.58,
        37:2.46, 38:2.34, 39:2.22, 40:2.1, 41:1.98, 42:1.94, 43:1.78, 44:1.7,
        45:1.54, 46:1.42, 47:1.34, 48:1.18, 49:1.1, 50:0.98, 51:0.86, 52:0.74,
        53:0.62, 54:0.5, 55:0.38, 56:0.26, 57:0.14, 58:0.02, 59:-0.1, 60:-0.22,
        61:-0.34, 62:-0.46, 63:-0.58, 64:-0.7, 65:-0.82, 66:-0.94, 67:-1.06,
        68:-1.22, 69:-1.34, 70:-1.46, 71:-1.58, 72:-1.7, 73:-1.82, 74:-1.94,
        75:-2.06, 76:-2.18, 77:-2.3, 78:-2.46, 79:-2.54, 80:-2.7, 81:-2.8,
        82:-2.92, 83:-3.08, 84:-3.16, 85:-3.28, 86:-3.4, 87:-3.52, 88:-3.64,
        89:-3.8, 90:-4.04, 91:-4.04, 92:-4.16, 93:-4.24, 94:-4.36, 95:-4.48,
        96:-4.6, 97:-4.72, 98:-4.84, 99:-4.96, 100:-5.02, 101:-5.2, 102:-5.34,
        103:-5.4, 104:-5.52, 105:-5.68, 106:-5.8, 107:-5.88, 108:-6.0,
        109:-6.12, 110:-6.24, 111:-6.36, 112:-6.48, 113:-6.64, 114:-6.72,
        115:-6.84, 116:-6.96, 117:-7.08, 118:-7.2, 119:-7.32, 120:-7.48,
        121:-7.56, 122:-7.64, 123:-7.76, 124:-7.92, 125:-8.0, 126:-8.12,
        127:-8.24}

# ax+b, cy+d
spatialTransformationMatrix=\
        (0.01000614, -4.91360806, 0.01000614, -5.34884476)

alignerCoordinateTuple =\
        (-4.91360806, -5.34884476, 0.01000614, 0.01000614)

#        (-6.06467941507, -2.37689628048, 0.0112372176649, 0.0112485939258)
#w=[0.0112372177, -6.0646794151, 0.0112485939, -2.3768962805]
#s=matrix([[w[0], 0, w[1]],[0,w[2],w[3]],[0,0,1]])
#t=matrix([[1.1230322, 0, -115.0365],[0,1.1230322,296.712093],[0,0,1]])
#s*t.I

tracedSlideTemplate = """<?xml version="1.0" ?><svg baseProfile="full" height="800.0" id="body"
preserveAspectRatio="none" version="1.1" viewBox="0 0 1000 800"
width="1000.0" xmlns="http://www.w3.org/2000/svg"
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
"""

filenameTempates = dict(traced='%d_traced_v%d.svg')

potraceProperties    = {}
potraceProperties['potrace_accuracy_parameter']   ='0.001'
potraceProperties['potrace_svg_resolution_string']='300x300'
potraceProperties['potrace_width_string']   =      '1000pt'
potraceProperties['potrace_height_string']  =      '800pt'

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
renderingProperties['ReferenceWidth']  = 1000
renderingProperties['ReferenceHeight'] = 800
renderingProperties['imageSize']       = (2*1000, 2*800)
