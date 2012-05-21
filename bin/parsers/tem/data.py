import datetime

CONF_PARSER_COMMENT = 'Put description of the dataset and infdormation about source dataset here.'
CONF_PARSER_NAME    = 'put_unix-like_dataset_name_here'
CONF_CONTACT_COMMENT= 'Put names of the persons preparing the CAF dataset (not the autors of the source data)'
CONF_CONTACT_EMAIL  = 'Put contatct email here'
CONF_CAF_COMPIL_TIME = datetime.datetime.utcnow().strftime("%F %T") #leave as it is
CONF_CAF_FULL_NAME = 'Put full name of the CAF dataset here'

REFERENCE_WIDTH  = 520
REFERENCE_HEIGHT = 520

SLIDE_RANGE = range(0,30)

INPUT_FILENAME_TEMPLATE = 'membranes-neurites-glia-%d.png'
IMAGE_TO_STRUCTURE_FN = 'imagecol2structname.txt'
COLOR_MAPPING_FN = 'fullnames.txt'
FULLNAME_MAPPING_FN = 'fullnames.txt'

# Code used to generate colormap:
# import colorsys
# for i in range(256):
#    r,g,b = colorsys.hsv_to_rgb( float(i)/256, 0.85, 95)
#    print '%d\t%d\t%02X%02X%02X' % (i,i,r,g,b)

# Dimensions of voxel in-plane
voxelSize = 1.38312586445

# ax+b, cy+d
spatialTransformationMatrix =\
        (voxelSize, -5, voxelSize, -5)
# The same as above but in different order: c,d,a,c
alignerCoordinateTuple =\
(-5, -5, voxelSize, voxelSize)

tracedSlideTemplate = """<?xml version="1.0" ?><svg baseProfile="full"
height="%d" 
width="%d"
viewBox="0 0 %d %d"
id="body"
xmlns="http://www.w3.org/2000/svg"
preserveAspectRatio="none" version="1.1"
xmlns:ev="http://www.w3.org/2001/xml-events"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:bar="http://www.3dbar.org">

<title></title>
<desc></desc>
<defs></defs>
<g id='content'></g>

</svg>
""" % (REFERENCE_HEIGHT, REFERENCE_WIDTH, REFERENCE_WIDTH, REFERENCE_HEIGHT)

filenameTempates = dict(traced='%02d_traced_v%d.svg')

renderingProperties = {}
renderingProperties['ReferenceWidth']  = REFERENCE_WIDTH
renderingProperties['ReferenceHeight'] = REFERENCE_HEIGHT
renderingProperties['imageSize']  = (REFERENCE_WIDTH*1, REFERENCE_HEIGHT*1)

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
('backgroundColor', (168,168,168)),
('filenameTemplates', filenameTempates),
('renderingProperties', renderingProperties),
('tracingProperties', tracerSettings),
('slideTemplate', tracedSlideTemplate))

indexerProperties = dict([
('Source','http://link.to.source.dataset.if.available'),
('Language', 'En'),
('ReferenceWidth', str(REFERENCE_WIDTH)),
('ReferenceHeight', str(REFERENCE_HEIGHT)),
('FilenameTemplate',filenameTempates['traced']),
('RefCords', ",".join(map(str,alignerCoordinateTuple))),
('CAFSlideOrientation', 'N/A'),
('CAFSlideUnits', 'nm'),
('CAFName', CONF_PARSER_NAME),
('CAFFullName', CONF_CAF_FULL_NAME),
('CAFComment', CONF_PARSER_COMMENT),
('CAFCreator', CONF_CONTACT_COMMENT),
('CAFCreatorEmail', CONF_CONTACT_EMAIL),
('CAFCompilationTime',CONF_CAF_COMPIL_TIME),
('CAFAxesOrientation', 'RSA')])
