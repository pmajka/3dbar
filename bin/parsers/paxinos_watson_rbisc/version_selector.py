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
Module which holds only C{VersionSelector} class and purpose of this module is mainly purpose of 
C{VersionSelector} class. Because of that, please read documentation of mentioned class.

G{importgraph}
"""

from config import *
import re
import os
import glob

class VersionSelector:
    """
    Read all atlas files (defined using L{CONF_FILENAME_TEMPLATES<CONF_FILENAME_TEMPLATES>})
    from given directories. Then put them into structure which allow easy indexing
    and determining level of processing and choosing the most advanced version of given slide.

    Allows:
        1. Coosing the filename of the most advanced file for given slide.
        2. Coosing the level of advancement for given slide (raw,pretraced,traced)
        3. Generating short report of data's consistency.
    """

    def __init__(self, rawSlidesDirectory, pretracedSlidesDirectory, tracedSlidesDirectory):
        """
        @type  rawSlidesDirectory: string
        @param rawSlidesDirectory: Directory with raw SVG files (raw conversion from ie. PDF)

        @type  pretracedSlidesDirectory: string
        @param pretracedSlidesDirectory: Directory with pretraced files.

        @type  tracedSlidesDirectory: string
        @param tracedSlidesDirectory: Directory with traced SVG files.

        @return: Nothing, it is a class constructor
        """
        # Store directories names
        self.rawSlidesDirectory=rawSlidesDirectory
        self.pretracedSlidesDirectory=pretracedSlidesDirectory
        self.tracedSlidesDirectory=tracedSlidesDirectory

        # Extract files of all types using defined filename templates and provided paths
        self.slideDirecotries=\
                {'raw':rawSlidesDirectory,\
                'pretraced':pretracedSlidesDirectory,\
                'traced':tracedSlidesDirectory}

        # Read information about files, their types and aggregate this information in dictionary.
        self._refreshIndex()


    def _refreshIndex(self):
        """
        @return: Nothing

        Scans provided directories for 'raw', 'traced' and 'pretraced' filed then groups files
        according to slide number, filetype and version in C{self.DictBySlide} dictionary.
        """
        self.PretrcedFiles=self._getFilesByMask(\
                os.path.join(self.pretracedSlidesDirectory, CONF_FILENAME_TEMPLATES['pretraced']))
        self.TracedFiles=self._getFilesByMask(\
                os.path.join(self.tracedSlidesDirectory, CONF_FILENAME_TEMPLATES['traced']))
        self.RawFiles=self._getFilesByMask(\
                os.path.join(self.rawSlidesDirectory, CONF_FILENAME_TEMPLATES['raw']))

        # Define file structure for storing files and their versions
        # structure[slideNo]\
        #       {'pretraced':[filenames],\
        #        'traced'   :[filenames],\
        #         raw'      :[filenames]}

        self.DictBySlide={}
        for slideNo in CONF_CORONAL_PAGE_RANGE:
            self.DictBySlide[slideNo]={'pretraced':[], 'traced':[], 'raw':[]}

        # Fill defined structure with data
        self._fillFiledict(self.PretrcedFiles, 'pretraced')
        self._fillFiledict(self.TracedFiles, 'traced')
        self._fillFiledict(self.RawFiles, 'raw')

    def _getFilesByMask(self, mask):
        """
        @type  mask: string
        @param mask: file mask defined according POSIX file masks.

        @return: List of all files covered by given mask with full paths.

        Gets all filed covered by given mask.
        """
        return glob.glob(mask)

    def _fillFiledict(self, fileListBase, listType):
        """
        @type  fileListBase: list
        @param fileListBase: List of filenames (with fill paths)
                             to spllit by slide number and status
        @type  listType: string
        @param listType: one of slide status C{raw}, C{pretraced}, C{traced}

        @return: None. Class variables are modified on-the-fly

        Puts all files into L{self.DictBySlide<self.DictBySlide>} dictionary
        as C{listType} slice status. The resulting structure is following:
        
        structure[slideNo]
        {'pretraced':[(version,filename)],
        'traced'   :[(version,filename)],
        ' raw'      :[(version,filename]}
        """

        # XXX This code is written in extremely stupid way, but screw it

        # Extract filenames from "path+filename" string
        justFilenames=map(lambda x: os.path.split(x)[1], fileListBase)

        # For each slice selct maching files and put them into DictBySlide
        # tagging it with listType
        for slideNo in CONF_CORONAL_PAGE_RANGE:
            for i in range(len(justFilenames)):

                result=CONF_RE_FILENAME_TEMPLATES[listType].search(justFilenames[i])
                if result and int(result.groups()[0])==slideNo:

                    # Extract version number for given file
                    if listType!='raw':
                        version=int(result.groups()[1])
                    else:
                        version=0

                    # Append pair (version, filename for given version)
                    self.DictBySlide[slideNo][listType].append((version, fileListBase[i]))

            # Now we sort (version,filename) by vesrion
            for SlideType in self.DictBySlide.keys():
                self.DictBySlide[slideNo][listType].sort(lambda x, y: x[0] - y[0])

    def _genOutFilename(self, slideNo, slideStatus, slideVersion=0):
        """
        Generates filename (in sense of path+filename) for given slidenumber
        and slide status.

        @type  slideNo: integer
        @param slideNo: slide number

        @type  slideStatus: string
        @param slideStatus: one of slide status C{raw}, C{pretraced}, C{traced}

        @type  slideVersion: optional parameter: integer, string
        @param slideVersion: version of the file (note that all slides statuses are
                             numbered independently). If the parameter if provided
                             default value (0) is overwritten.
        
        @note: User must not save raw files as thy are source files and should
               should not be owerwritten.
        """
        # TODO: Implelent excetion - when 'raw' slideStatus will be passed
        # user must not save raw files as thy are one of a kind :)
        # and we cannot overwirte them !
        return os.path.join(\
                self.slideDirecotries[slideStatus],\
                CONF_FILENAME_SAVE_TEMPLATES[slideStatus] % (int(slideNo), int(slideVersion) )\
                )

    def _getSlideStatus(self, slideNo):
        """
        @type  slideNo: integer
        @param slideNo: slide number

        @return: (string), One of slide statuses: C{raw}, C{pretraced}, C{traced}.

        Gets slide status for given slide number
        """
        # Create dictionary type:list_len

        # Declare possible slides status
        types=['pretraced','traced','raw']

        # Create list with number of files having each status
        # is. for slide n, there are 2 versions of traced file,
        # 3 version of pretraced and one raw file.
        lengths={}
        for type in types:
            lengths[type]=len(self.DictBySlide[slideNo][type])

        # Decide which status has given slide
        # NOTE that there should be at least one file - the raw file.
        if lengths['traced'] * lengths['pretraced'] * lengths['raw'] > 0: return 'traced'
        if lengths['traced'] == 0 and  lengths['pretraced'] > 0 and lengths['raw'] > 0: return 'pretraced'
        if lengths['traced'] == 0 and  lengths['pretraced'] == 0 and lengths['raw'] > 0: return 'raw'

        return "Error getting slide status %d" % slideNo

    def _defineMostAdvancedFilename(self, slideNo, slideType):
        """
        @type  slideNo: integer
        @param slideNo: slide number
        
        @type  slideType: string
        @param slideType: one of slide status C{raw}, C{pretraced}, C{traced}

        @return: filename (path+filename) of file holding the most recent version
        of the slide having particular C{slideType} status.
        """
        #print self.DictBySlide[slideNo]
        return  self.DictBySlide[slideNo][slideType][-1][1]

    def _getMostAdvancedFilename(self, slideNo):
        """
        @type  slideNo: integer
        @param slideNo: slide number

        @return: filename (path+filename) of file holding the most recent version
        of the slide having particular C{slideType} status.

        Function encapsulates functionality of L{_getSlideStatus<_getSlideStatus>} and
        L{_defineMostAdvancedFilename<_defineMostAdvancedFilename>} in one function
        so is just a shortcut.
        """
        mostProcessedType=self._getSlideStatus(slideNo)
        return self._defineMostAdvancedFilename(slideNo, mostProcessedType)

    def _getBriefSlidesReport(self):
        """
        Helper function, generatqes report about all slices. Print their statuses,
        available files, etc.
        
        @return: (string) Report containing information about most advanced version,
                 filename and location of all slices.
        """
        
        buffer=""
        for slideNo in CONF_CORONAL_PAGE_RANGE:
            buffer+=self._getShortSlideReport(slideNo)
        return buffer

    def _getShortSlideReport(self, slideNo):
        """
        @type  slideNo: integer
        @param slideNo: slide number

        @return: One line string with short information about one slide
        """
        return "Slice:\t%d\tstatus:\t%s\tfilename:\t%s\n" %\
            (slideNo,\
            self._getSlideStatus(slideNo),\
            self._getMostAdvancedFilename(slideNo))

    def _getDetailedSlideReport(self, slideNo):
        """
        @type  slideNo: integer
        @param slideNo: slide number

        @return: (string) Report with detailed information about slide with given number:
                 1. current status,
                 2. filename with most advanced version and its localization
                 3. list of files for each slide status

        Generated detailed report for given slide.
        """

        buffer=""
        buffer+=self._getShortSlideReport(slideNo)+"\n"
        buffer+="\tDetailed report:\n"
        for slideType in self.DictBySlide[slideNo]:
            buffer+= "\tSlide type:\t %s\n" % slideType
            buffer+= "\t"+"\n\t".join(self.DictBySlide[slideNo][slideType])+"\n"
        return buffer
    
if __name__=='__main__':
    vs=VersionSelector(\
            rawSlidesDirectory='/home/pmajka/3dbrainatlases/input_atlases/paxinos_franklin_mouse/raw_svg',\
            pretracedSlidesDirectory='/home/pmajka/3dbrainatlases/input_atlases/paxinos_franklin_mouse/svg_pretraced',\
            tracedSlidesDirectory='/home/pmajka/3dbrainatlases/input_atlases/paxinos_franklin_mouse/svg_traced'\
            )

    print vs._getBriefSlidesReport()
    for slideNo in CONF_CORONAL_PAGE_RANGE:
        print vs._getDetailedSlideReport(slideNo)
