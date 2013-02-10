#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime

from bar import parsers as bar
from bar.base import getDictionaryFromFile, barCafSlide
from user_data import renderingProperties, tracerSettings,\
    userMetadata, slideRange,\
    colorMappingFilename, fullNameMappingFilename,\
    hierarchyFilename, \
    legitimateStructures, legitimateCommentLabels, legitimateSpotLabels

filenameTempates = dict(traced='%02d_traced_v%d.svg',
                        pretraced='%03d_v%d.svg')

indexerProps = userMetadata
indexerProps.update({
    'ReferenceWidth': str(renderingProperties['ReferenceWidth']),
    'ReferenceHeight': str(renderingProperties['ReferenceHeight']),
    'FilenameTemplate': str('%02d_traced_v%d.svg'),
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

        self._tracingConf = tracerSettings
        self._rendererConf = renderingProperties

        self.indexer.updateProperties(indexerProps)

    def _getInputFilename(self, slideNumber):
        return bar.barVectorParser._getInputFilename(self, slideNumber, version=1)

    def parseAll(self):
        bar.barVectorParser.parseAll(self)
        self.reindex()

    def parse(self, slideNumber):
        tracedSlide = bar.barVectorParser.parse(self, slideNumber,
                                                useIndexer=False,
                                                writeSlide=False)
        map(lambda x:
            x._attributes.update({'font-size': '10px'}),
            tracedSlide.labels)

        for structure in tracedSlide.structures:
            if structure.name not in legitimateStructures:
                del tracedSlide[structure.name]

        for spotLabel in tracedSlide.getSpotLabels():
            if spotLabel.Caption not in legitimateSpotLabels:
                tracedSlide.deleteLabelByCaption(spotLabel.Caption)

        for commentLabel in tracedSlide.getCommentLabels():
            if spotLabel.Caption not in legitimateCommentLabels:
                tracedSlide.deleteLabelByCaption(commentLabel.Caption)

        tracedSlide.writeXMLtoFile(self._getOutputFilename(slideNumber))

        return tracedSlide

    def reindex(self):
        bar.barVectorParser.reindex(self)

        self.indexer.setParentsFromFile(hierarchyFilename)
        self.indexer.setNameMappingFromFile(fullNameMappingFilename)
        self.indexer.setColorMappingFromFile(colorMappingFilename)
        self.writeIndex()


if __name__ == '__main__':
    try:
        inputDirectory = sys.argv[1]
        outputDirectory = sys.argv[2]
    except:
        inputDirectory = 'atlases/mbisc_11/src/'
        outputDirectory = 'atlases/mbisc_11/caf/'

    ap = AtlasParser(inputDirectory, outputDirectory)
    #ap.parseAll()
    #ap.reindex()
    ap.parse(19)
