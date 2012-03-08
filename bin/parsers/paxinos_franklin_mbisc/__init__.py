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
Module dedicated for parsing Mouse atlas. Performs complete atlas parsing
starting from PDF file and finishing on filer requires by 3D Brain Atlas
Reconstructor. 

Module is intended for using with 3D Brain Atlas Reconstructor. However it may
be used as a standalone modlude. See __main__ funcion for further information.

czw, 26 sie 2010, 09:27:33 CEST
Removed obsolete code from frst version of parser done by G.Furga, other minor
improvements.

sro, 1 wrz 2010, 13:21:09 CEST
Corrected indexing errors and cleaning up ambigous slide indexing.

Example of standalone usage:
    >>> import atlasparser
    >>> ap=atlasparser.AtlasParser("directory_with_atlas")
    >>> ap.parse(1)

G{importgraph}

"""
from config import *
import svgfix, fcoords, matcharrows
import class_fill
import version_selector
import atlas_indexer 
import slides_aligner 
import os, sys
import xml.dom.minidom as dom
from string import *

# sro, 25 sie 2010, 18:57:44 CEST
# If, we want to measure performance: here You go
#import pycallgraph
#pycallgraph.start_trace()
#pycallgraph.make_dot_graph('test'+str(pagenumber)+'.png')

class AtlasParser:
    """
    Class which handles all parsing oparations.
    G{classtree: AtlasParser}

    sro, 25 sie 2010, 18:58:53 CEST

    Including slides_aligner as part of atlasparser. From now, slides aligning
    is performed on stage of parsing (however, aligning still remains in
    rendering process)

    Removing plenty of unnecessary functions - significant speedup.
    """

    def __init__(self, rawSlidesDirectory, cafDirectory):
        """
        @type cafDirectory: C{str}
        @param cafDirectory: Dummy directory name - used for compatibility
        reasons.
        
        @type  rawSlidesDirectory: string
        @param rawSlidesDirectory: Directory with raw SVG files (raw conversion from ie. PDF)
        """
        
        # Until better idea (and ability to implement in GUI)
        # pretraced and traced directories are assumed to be the same as raw slided dir.
        self.rawSlidesDirectory = rawSlidesDirectory
        self.pretracedSlidesDirectory = rawSlidesDirectory
        self.tracedSlidesDirectory=cafDirectory
        
        # Create version selector class instance.
        # This class holds structure of slides numbers and their names and allows
        # Quickly indexing and selecting most recent version of given slide
        # or stage of processing
        self.fileSelector=version_selector.VersionSelector(\
                self.rawSlidesDirectory,\
                self.pretracedSlidesDirectory,\
                self.tracedSlidesDirectory,\
                )
        self._slide_indx =\
                CONF_CORONAL_PAGE_RANGE # Holds number of pages with coronal slices
        self._indexer = atlas_indexer.AtlasIndexer()
        self.aligner = slides_aligner.slideAligner(CONF_ALIGNER_REFERENCE_COORDS, debugMode =  False)

    def _processFromRawSVG(self, pagenumber):
        """
        @type  pagenumber: integer
        @param pagenumber: Number of page to parse
        @return: Complex dataset, please read function description.

        Processes SVG files from 'Raw SVG' type to 'Pretraced SVG' status. Returns
        complex dataset:

            1. 'Pretraced SVG' file DOM object
            2. Matrix for transforming from SVG coordinate system to
               stereotactic coordinate system
            3. Bregma coordinate
            4. Dataset with information about all text elements (labels).
        Performs processing from rawSVG file status to pretraced status
        """

        # Select filename corresponding with given pagenumber
        filename = self.fileSelector._getMostAdvancedFilename(pagenumber)

        svgdom = dom.parse(filename)                    # Parse input file
        svg = svgdom.getElementsByTagName('svg')[0]
        svg.setAttribute('xmlns:bar',"http://www.3dbar.org")
        
        svgfix.fixSvgImage(svgdom, pagenumber)          # Simplify input file structure
        (bregma, offsets) = fcoords.processFile(svgdom) # Extracts bregma coordinate and 
                                                        #  scalings and offsets for
                                                        #  converting to stereotaxic coordinates

        matcharrows.DoMatch(svgdom)                    # Calculate labels coordinates
        matcharrows.symmetrizeLabels(svgdom, offsets)  # Make structures labels symmetric 
        fcoords._indexElements(svgdom)                 # Assign uniqe id to each SVG element

        if self.aligner.makeAlignment(svgdom):
            svgfix.fixSvgImage(svgdom, fixHeader=False)# If there's a need to
            print "FIXING"                             # was made - do it)
                                                       # fix image (if alignment 
                                                       # was made - do it)
        return svgdom

    def _processTT(self, pagenumber):
        """
        @type  pagenumber: integer
        @param pagenumber: Number of page to parse
        @return: Complex dataset, please read function description.

        Extracts various information from 'Pretraced SVG' and 'Traced SVG'.
        Return complex dataset:

            1. 'Pretraced SVG' file DOM object
            2. Matrix for transforming from SVG coordinate system to
               stereotactic coordinate system
            3. Bregma coordinate
            4. Dataset with information about all text elements (labels).
        """
        # Extract filename corresponding to most advanced version of give slide
        pretracedFilename = self.fileSelector._getMostAdvancedFilename(pagenumber)
        svgdom = dom.parse(pretracedFilename)    # Parse input fie
        
        #XXX Aligning slides to reference coordinates in advance (not used)
        # due to lack of performance
        if self.aligner.makeAlignment(svgdom):
            svgfix.fixSvgImage(svgdom, fixHeader=False)# If there's a need to
            wasFixed = True                            # fix image (if alignment
            print "FIXING"                             # was made - do it)
        else:
            wasFixed = False
        
        return svgdom, pretracedFilename, wasFixed
    
    def parseAll(self):
        map(self.parse, CONF_CORONAL_PAGE_RANGE)
        self.reindex()
   
    def reindex(self):
        self._indexer.createHierarchyFromFile(os.path.join(self.tracedSlidesDirectory,"parents.txt"))
        
        sourceFilename = os.path.join(self.tracedSlidesDirectory, "fullnames.txt")
        self._indexer.getFullnamesFromFile(sourceFilename)
        
        IndexFilename = os.path.join(self.tracedSlidesDirectory, "index.xml")
        self._indexer.saveIndexAsXML(IndexFilename)
    
    def parse(self, pagenumber, UseIndexer = True):
        """
        Performs parsing one page denoted with C{slideNo}. Parsing procedure includes:
            1. Simplyfying SVG file structure in in order to make further parsing simpler.
               Simplyfying means applying all transformations and calculating elements
               coordinates in image coodrinate system.
            2. Extracting bregma coordinate and transformation 
               to stereotaxic coodrinates system matrix (basing on grid lines and text labels)
            3. Removing unnecessary SVG elements:
                - gridlines,
                - non-brain paths
                - coordinatess labels
                - etc.

               Leaving only brain elements, arrows and brain structures labels.
            4. Matching arrows with text labels and cloning text labes
               in coordinates where arrows points.

        @type  pagenumber: integer
        @param pagenumber: Number of page to parse

        @return          : None
        """
        print >>sys.stderr, "Parsing slide " + str(pagenumber)
        
        # Read current status of given file
        currentSlideStatus=self.fileSelector._getSlideStatus(pagenumber)
        
        if currentSlideStatus=='raw':
            # Extract various information about given slide
            svgdom = self._processFromRawSVG(pagenumber)
            
            # VERY IMPORTANT LINE: Trace all structures basing on rendered SVG image
            # Size of rendered image is defined in cinfiguration file.
            (svgdom, oldSVG)=class_fill.ExtractAllPaths(svgdom, pagenumber)
            
            # In this case we need to save both of the files: pretraced and traced version.
            # We need to save them becase we did not created those files yet :) !
            
            # Generate pretraced and traced slide filename 
            pretracedFilename = self.fileSelector._genOutFilename(pagenumber, 'pretraced')
            tracedFilename = self.fileSelector._genOutFilename(pagenumber, 'traced')
            #Generate filename for pretraced file for modifications
            pretracedFilenameToMod =\
                self.fileSelector._genOutFilename(pagenumber, 'pretraced', slideVersion=1)
            
            # Save all those files.
            _debug_DumpXMLFile(svgdom, tracedFilename)
            _debug_DumpXMLFile(oldSVG, pretracedFilename)
            _debug_DumpXMLFile(oldSVG, pretracedFilenameToMod)
        
        if currentSlideStatus=='pretraced':
            # Extract various information about given slide
            (svgdom, pretracedFilename, wasFixed) = self._processTT(pagenumber)
            
            # VERY IMPORTANT LINE: Trace all structures basing on rendered SVG image
            (svgdom, oldSVG)=class_fill.ExtractAllPaths(svgdom, pagenumber)
            
            # Saving output file we save bot traced and pretraced version as
            # pretraced may be updated with 'UNLABELLED' text labels and we want
            # to preserve this information as it is very important!
            tracedFilename=self.fileSelector._genOutFilename(pagenumber, 'traced')
            _debug_DumpXMLFile(svgdom, tracedFilename)
            _debug_DumpXMLFile(oldSVG, pretracedFilename)
       
        if currentSlideStatus=='traced':
            # Extract various information about given slide
            (svgdom, pretracedFilename, wasFixed) = self._processTT(pagenumber)
            
            # If reference stereotactic coordinates were corrected and slide was
            # aligned, the updated version has to bes saved. Because slide has
            # status 'traced' only 'traced' slide will be updated ('pretraced'
            # slide is untouched.
            if wasFixed:
                tracedFilename=self.fileSelector._genOutFilename(pagenumber, 'traced')
                _debug_DumpXMLFile(svgdom, tracedFilename)
        
        if UseIndexer: self._indexer.indexSingleSlide(pagenumber, svgdom)

def _debug_DumpXMLFile(svgdom, OutputFilename):
    """
    Dumps given xml object to file with given filename.

    @type  svgdom: DOM object
    @param svgdom: Whole SVG document.

    @type  OutputFilename: string
    @param OutputFilename: filename to save the file

    @return      : None
    """

    # Dump the file
    f=open(OutputFilename,'w')
    svgdom.writexml(f)
    f.close()

if __name__=='__main__':
    pass
