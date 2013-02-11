#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import datetime

from bar import parsers as bar
from bar.base import getDictionaryFromFile
from user_data import renderingProperties, tracerSettings,\
    userMetadata, slideRange,\
    colorMappingFilename, fullNameMappingFilename,\
    hierarchyFilename, \
    legitimateStructures, legitimateCommentLabels, legitimateSpotLabels, regularLabelsToRemove

# Some of the metadata has to be updated before parsing. This concerns
# especially some of the filename templates and slide rendering properties:

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
        # Update the parser properties dictionary before invoking an instance
        # of vector atlas parser (this is the way it works).
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

        # Add slide tracing and rendering settings to the parser's data
        self._tracingConf = tracerSettings
        self._rendererConf = renderingProperties

        # And now update the parser's indexer configuration (phew...) as
        # previously we were updating only properties and configuration of the
        # parser itself.
        self.indexer.updateProperties(indexerProps)

    def _getInputFilename(self, slideNumber):
        return bar.barVectorParser._getInputFilename(self, slideNumber, version=1)

    def parseAll(self):
        bar.barVectorParser.parseAll(self)
        self.reindex()

    def parse(self, slideNumber):
        tracedSlide = bar.barVectorParser.parse(self, slideNumber,
                                                useIndexer=False,
                                                writeSlide=False,
                                                writeContourBack=False)

        # The code above is quite easy: 1) we don't want to index slides as we
        # parse them (there will be dedicated indexer's sweep at the end of the
        # parsing. 2) We don't want to save the traced slide to the disk (as
        # there are some corrections to apply) 3). We don't want to put
        # any feedback from the tracing procedure to the contour slides (as
        # they look ugly then).

        # A series of corrections to apply to the caf slide before saving:
        # 1) Increase font size as the default one is a bit to small
        # 2) Removal of all the labels and structures which are not defined in
        # the structures hierarchy. This includes a verification of all the
        # labels and st

        map(lambda x:
            x._attributes.update({'font-size': '15px'}),
            tracedSlide.labels)

        for structure in tracedSlide.structures:
            if structure.name not in legitimateStructures:
                del tracedSlide[structure.name]

        for spotLabel in tracedSlide.getSpotLabels():
            if spotLabel.Caption not in legitimateSpotLabels:
                tracedSlide.deleteLabelByCaption(spotLabel.Caption)

        for commentLabel in tracedSlide.getCommentLabels():
            if commentLabel.Caption not in legitimateCommentLabels:
                tracedSlide.deleteLabelByCaption(commentLabel.Caption)

        for regularLabel in tracedSlide.getRegularLabels():
            if regularLabel.Caption in regularLabelsToRemove:
                tracedSlide.deleteLabelByCaption(regularLabel.Caption)

        #tracedSlide.size = (650, 850)
        #tracedSlide.bitmapSize = (650, 850)

        # Finally, we can write the slide
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
    ap.parseAll()
    #for i in range(2,51):
    #    ap.parse(i)
    #ap.reindex()
