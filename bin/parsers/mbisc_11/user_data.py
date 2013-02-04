#!/usr/bin/python
# -*- coding: utf-8 -*-

# Module in which the user configures behaviour
# of the parser.

# The number of slides creating the atlas
slideNumber = 51

# slideRange determines numbers of consecutive slides.
# Usually having n slides one may to enumerate them starting from 0 to n-1 or
# starting from 1 to n. In that case the slideRange should be defined equal to
# range(n) or range(1,n+1). The slide range may start from arbitrary integer
# (i.e. range(75,n+75+1). If you do not require any offset leave this value as it
# is.
slideOffset = 0
slideRange = range(slideOffset, slideNumber + slideOffset + 1)

#  renderingProperties dictionary defines the size of the rasterized conrour
#  slide and CAF slide.
renderingProperties = {}


# The width and height (in pixels) of the rasterized slide.
# Enter dimensions of your slides here. Note that width and height of all sldes
# has to be the same on all slides.
renderingProperties['ReferenceWidth']  = 842
renderingProperties['ReferenceHeight'] = 1191
renMultiplier = 5

renderingProperties['imageSize'] =\
	(renderingProperties['ReferenceWidth'] * renMultiplier,\
	renderingProperties['ReferenceHeight'] * renMultiplier)

# PoTrace settings - passed to PoTrace as command line parameters. Refer to
# PoTrace manual for their description and usage.
potraceProperties    = {}
potraceProperties['potrace_accuracy_parameter']   ='0.001'



# Settings of the contour slide tracing routine
tracerSettings={}

# Relative location of the directory for debugging information.
# Please change, according to specific needs.
tracerSettings['DumpDirectory']            = '.'

# Determines if PNG image containing binary bitmap (just before tracing) will be
# saved.
tracerSettings['DumpEachStepPNG']          = True

# Determines, if SVG drawing with each single traced path will be saved.
tracerSettings['DumpEachStepSVG']          = True

# Determines, if regions created by floodfilling areas pointed by
# labels placed above the contours or outside the brain outline
# will be dumped.
tracerSettings['DumpWrongSeed']            = True 

# Turns on/off detection of unlabelled areas.
tracerSettings['DetectUnlabelled']         = True

# Sets minimal area (in pixels) of the region to be considered as 'unlabelled'.
# Please modify according to specific needs.
tracerSettings['UnlabelledTreshold']       = 10

# Select number of border expansions in gap filling algorithm. If set to 0, gap
# filling algorithm idf turned off. If larger than 0 - gap filling is on.
#TODO: Change to MaxGrowLevel here and in the other fragments of code.
tracerSettings['CacheLevel']               = 0

potraceProperties['potrace_svg_resolution_string']='300x300'
potraceProperties['potrace_width_string']   =\
	'%dpt' % int(renderingProperties['ReferenceWidth'])
potraceProperties['potrace_height_string']  =\
	'%dpt' % int(renderingProperties['ReferenceHeight'])

tracerSettings['DumpVBrain']               = False 
tracerSettings['MinFiterTimesApplication'] = 3
tracerSettings['GrowDefaultBoundaryColor'] = 200
tracerSettings['RegionAlreadyTraced']      = 100
tracerSettings['PoTraceConf'] = potraceProperties
tracerSettings['NewPathIdTemplate'] = 'structure%d_%s_%s'

# CAF dataset metadata:
# Setting below set the metadata for the CAF dataset:

# RefCords:
# RefCords parameter is a set of coefficients user for translating CAF slide coordinates (SVG drawing coordinates into spatial coordinates. The coefficients are four values (a,b,c,d) so:
#x' = a*x+b
#y' = c*y+d
# Where (x,y) are SVG coordinated in the CAF slide and (x',y') are spatial coordinated of the same point

# CAFSlideOrientation:
# Defines orientation of the CAF slides (i.e. coronal, horizontal, sagital)

# CAFName:
# Defines short name (id name) if given CAF dataset. Allowed set of characters is limited to letters, numbers, hypen and underscore char: [a-zAz0-9_-]

# CAFSlideUnits:
# Defines the unit of the spatial coordinate system (e.g. milimeters, mm, micrometers, um, centimeters, cm, etc.)

# CAFComment:
# General comment fileld. It may hold for exmaple detailed information about source datasets (i.e. eferences, links to the datasets.

# CAFCreator:
# Information about given CAF dataset author (authors)

# CAFCreatorEmail: CAF authors email
userMetadata = dict([
        ('CAFName', 'mbisc_11'),
        ('CAFSlideOrientation', 'coronal'),
        ('CAFSlideUnits', 'mm'),
        ('CAFComment', 'please provide description'),
        ('RefCords', '0.0235184448749,-0.0235184496638,-1.09904044745,19.1636693709'),
        ('CAFCreator', 'pmajka@nencki.gov.pl'),
        ('CAFCreatorEmail','pmajka@nencki.gov.pl')])

# Color mapping filename:
# Filename holding color to structure abbreviation assignment.
# tab-separated file
colorMappingFilename = "atlases/mbisc_11/src/colors.txt"

# FullNameMapping file:
# File filename holding structure abbreviation => full structure name assignment
# tab-separated file
fullNameMappingFilename = "atlases/mbisc_11/src/fullnames.txt"

# Hierarchy file:
# File holding hierarchy of the structures
hierarchyFilename = "atlases/mbisc_11/src/parents.txt"