#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import datetime

from bar import parsers as bar
from bar.base import getDictionaryFromFile
from user_data import renderingProperties, potraceProperties, tracerSettings,\
                      userMetadata, slideRange,\
                      colorMappingFilename, fullNameMappingFilename,\
                      hierarchyFilename, renMultiplier

renderingProperties['imageSize'] =\
	(renderingProperties['ReferenceWidth'] * renMultiplier,\
	renderingProperties['ReferenceHeight'] * renMultiplier)

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

filenameTempates = dict(traced='%d_traced_v%d.svg',\
                        pretraced='%s_pretrace_v%d.svg')

indexerProps = userMetadata
indexerProps.update({\
        'ReferenceWidth':  str(renderingProperties['ReferenceWidth']),
        'ReferenceHeight': str(renderingProperties['ReferenceHeight']),
        'FilenameTemplate': str('%d_traced_v%d.svg'),
        'CAFCompilationTime': datetime.datetime.utcnow().strftime("%F %T")})


class AtlasParser(bar.barVectorParser):
    def __init__(self, inputDirectory, outputDirectory):
        props = {}
        props['filenameTemplates'] = filenameTempates
        props['slideRange'] = slideRange
        colorMapping = getDictionaryFromFile(colorMappingFilename)
        props['structureColours'] = colorMapping
        props['renderingProperties'] = renderingProperties
        props['tracingProperties'] = tracerSettings
        props['inputDirectory'] = inputDirectory
        props['outputDirectory'] = outputDirectory
        
        bar.barVectorParser.__init__(self, **props)
        
        self.indexer.updateProperties(indexerProps)
    
    def _getInputFilename(self, slideNumber):
        return bar.barVectorParser._getInputFilename(self, slideNumber, version=1)
     
    def parseAll(self):
        bar.barVectorParser.parseAll(self)
        self.reindex()
        
    def reindex(self):
        bar.barVectorParser.reindex(self)
        
        #self.indexer.createFlatHierarchy()
        #hierarhySourceFilename = os.path.join(self.inputDirectory, 'parents.txt')
        self.indexer.setParentsFromFile(hierarchyFilename)
        
        #fullnameMappingFile = os.path.join(self.inputDirectory,'fullnames.txt')
        self.indexer.setNameMappingFromFile(fullNameMappingFilename)
        
        self.indexer.setColorMappingFromFile(colorMappingFilename)
        self.writeIndex()

if __name__=='__main__':
    try:
        inputDirectory  = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory  = 'atlases/gvp/caf-src/'
        outputDirectory = 'atlases/gvp/caf-src/'
    
    ap = AtlasParser(inputDirectory, outputDirectory)
    ap.parse(44)
    ap.parseAll()
