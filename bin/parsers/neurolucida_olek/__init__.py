#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xml.dom.minidom as dom
import os
import numpy as np
import datetime

import bar.neurolucida as nl
from bar import base as bar

renderingProperties={}
renderingProperties['imageSize'] = (1200 * 3, 900 * 3)
renderingProperties['ReferenceWidth']  = 1200
renderingProperties['ReferenceHeight'] = 900

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
tracerSettings['DumpDirectory']            = '/home/pmajka/3dbrainatlases/atlases/vector-test/src/'
tracerSettings['DetectUnlabelled']         = True
tracerSettings['CacheLevel']               = 5
tracerSettings['MinFiterTimesApplication'] = 3
tracerSettings['GrowDefaultBoundaryColor'] = 200
tracerSettings['RegionAlreadyTraced']      = 100
tracerSettings['UnlabelledTreshold']       = 500
tracerSettings['PoTraceConf'] = potraceProperties
tracerSettings['NewPathIdTemplate'] = 'structure%d_%s_%s'

class AtlasParser(nl.nlParser):
    """
    This class is an extension of generic neurolucida xml parser dedicated for
    parsing neurolucida XML file having checksum
    68c848681832d9742036443019590d07
    
    Only contours are extracted from this dataset. This parser is not suitable
    for extracting markers from the dataset as they are poorly defined. Do not
    try to extract them :).
    """
    def __init__(self, inputFilename, outputDirectory, **kwargs):
        """
        """
        # First of all load neurolucida slide. Extract only contours. Round z
        # coordinates up to second decimal place.
        nl.nlParser.__init__(self,\
                inputFilename, ['contour'], 2, **kwargs)
        
        #assing tracing and rendering properties
        self.renderingProperties = renderingProperties
        self.tracingProperties   = tracerSettings
        
        # Rescale micrometers to milimeters and define some arbitrary
        # transformation that centers all slices.
        M = 0.001*np.eye(4)
        Ms= np.array([ [28.18249, 0, 0, 1000*80.11477],\
                       [0, 28.18249, 0, 1000*530.76565],\
                       [0,        0, 1, 0],\
                       [0,        0, 0, 1]])
        Mt= np.array([ [1, 0, 0, 80.11477],\
                       [0, 1, 0, 530.76565],\
                       [0, 0, 1, 0],\
                       [0, 0, 0, 1]])
        
        # Apply defined transfomrmations to the slide.
        initialCorrection = np.dot(np.dot(M,Ms),Mt)
        self.affineTransform(initialCorrection)
        
        # Define very important parser constants :)
        self.setProperty('outputDirectory', outputDirectory)
        self.setProperty('filenameTemplates', dict(traced='%d_traced_v%d.svg'))
    
    def parse(self, slideNumber, useIndexer = False):
        """
        This parsing procedure extracts slide with given number and translates
        it in the way that its centre of the mass is located in (0,0).
        """
        # Gest slide
        tracedSlide = nl.nlParser.parse(self, slideNumber)
        
        # Calculate mass center, move the slide to the begining of the
        # coordinate system and rotate -90.
        mc = tracedSlide.getSlideMassCenter()
        mc = (600-mc[1], 450-mc[0])
        Mc= np.array([ [1, 0, mc[0]],\
                       [0, 1, mc[1]],\
                       [0, 0, 1]])
        
        Mp= np.array([ [1, 0, -600],\
                       [0, 1, -450],\
                       [0, 0, 1]])
        
        Mpp= np.array([ [1, 0, 600],\
                       [0, 1, 450],\
                       [0, 0, 1]])
        
        Mr= np.array([ [0, 1, 0],\
                       [-1, 0, 0],\
                       [0, 0, 1]])
        
        # Enlarge the slide 5 times.
        Ms = 5.*np.eye(3)
        
        # Execute all defined transformations.
        tracedSlide.affineTransform(Mp)
        tracedSlide.affineTransform(Mc)
        tracedSlide.affineTransform(Ms)
        tracedSlide.affineTransform(Mr)
        tracedSlide.affineTransform(Mpp)
        tracedSlide.generateLabels()
        
        # Apply metadata
        tracedSlide._metadata[bar.BAR_TRAMAT_METADATA_TAGNAME] =\
        bar.barTransfMatrixMetadataElement((0.010345983719932001,\
                                            -6.0646794151,\
                                            0.010345983719932001,\
                                            -2.3768962805))
        
        # Then index and save the slide.
        ofilename = self._getOutputFilename(slideNumber)
        tracedSlide.writeXMLtoFile(ofilename)
        if useIndexer: self.indexer.indexSlingleSlide(tracedSlide, slideNumber)

    def parseAll(self):
        nl.nlParser.parseAll(self)
        self.reindex()
        
        self.indexer.properties = ('ReferenceWidth', 1200)
        self.indexer.properties = ('ReferenceHeight', 900)
        self.indexer.properties = ('FilenameTemplate',\
                                  self.filenameTemplates['traced'])
        self.indexer.properties = ('RefCords',\
            '-6.06467941507, -2.37689628048,0.010345983719932001,0.010345983719932001')
        self.indexer.properties = ('CAFSlideOrientation', 'coronal')
        self.indexer.properties = ('CAFSlideUnits', 'mm')
        self.indexer.properties = ('CAFName', '')
        self.indexer.properties = ('CAFComment', '')
        self.indexer.properties = ('CAFCreator', "Dataset prepared by Piotr Majka, Nencki Institute of Experimental Biology")
        self.indexer.properties = ('CAFCreatorEmail', 'pmajka@nencki.gov.pl')
        self.indexer.properties = ('CAFCompilationTime', datetime.datetime.utcnow().strftime("%F %T"))
        
        self.indexer.createFlatHierarchy()
        
        # Creating structure name to structure color mapping
        cnmap = dict(map(lambda x: (x.name, x.color[1:]),\
                            self._nlSlide.getSlide(\
                            tracingProperties   = self.tracingProperties,
                            renderingProperties = self.renderingProperties).structures))
        self.indexer.colorMapping   = cnmap
        
        fullNameMapping = dict(map(lambda x: (x[0],x[0]),cnmap.iteritems()))
        self.indexer.fullNameMapping= fullNameMapping
        self.writeIndex()


if __name__ == '__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  = 'atlases/nl_olek/src/SI_SA250_tracing.xml'
        outputDirectory = 'atlases/nl_olek/caf/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parseAll()
    
