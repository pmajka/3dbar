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

import os
import sys
import datetime
import bar


class structureLines(object):
    """
    An virtual class for generation commandlines performing volume
    reconstructions of all available structures in the CAF hierarchy tree.

    @cvar _linePattern: pattern of a pattern of the commandline associated
                        to the structure
    @type _linePattern: str

    @cvar _indexPath: path to the index file of the CAF in the directory
                      subtree mentioned in the note
    @type _indexPath: str

    @ivar __indexer: indexer of the CAF
    @type __indexer: L{bar.atlasIndexer}

    @ivar __linePattern: pattern of the commandline associated to the structure
    @type __linePattern: str

    @note: It is assumed that the CAF is stored in a subtree of a common 3dBAR
           atlas directory rooted in its child subdirectory of the same name as
           the CAF.
    """
    _linePattern = None
    _indexPath = None

    def __init__(self, dir3dbar, cafName):
        """
        @param dir3dbar: absolute path to the main 3dBAR directory
        @type dir3dbar: str

        @param cafName: name of the CAF
        @type cafName: str
        """
        self.__indexer = bar.barIndexer.fromXML(os.path.join(dir3dbar,
                                                             'atlases',
                                                             cafName,
                                                             self._indexPath))
        self.__linePattern = self._linePattern % {'dir3dbar': dir3dbar,
                                                  'cafName': cafName}

    def __str__(self):
        """
        @return: commandlines performing volume reconstruction for every
                 structure available in the CAF hierarchy tree
        @rtype: str
        """
        groups = [k for (k, v) in self.__indexer.groups.items() if v.uidList != []]
        return '\n'.join(self.__linePattern % x for x in groups)


class cafStructureLines(structureLines):
    """
    A subclass of L{structureLines} for generation volumes of structures in the
    main CAF.
    """
    _linePattern = 'echo "mkdir -p $testdir; %(dir3dbar)s/batchinterface.sh %(dir3dbar)s/atlases/%(cafName)s/caf/index.xml --exportToNiftii -e $testdir %%s" >> ${JOB_TEMP_RC}'
    _indexPath = 'caf/index.xml'


class refStructureLines(structureLines):
    """
    A subclass of L{structureLines} for generation volumes of structures in the
    reference CAF.
    """
    _linePattern = 'echo "mkdir -p $testdir; %(dir3dbar)s/batchinterface.sh %(dir3dbar)s/atlases/%(cafName)s/caf-reference/index.xml --exportToNiftii -e $testdir %%s" >> ${JOB_TEMP_REFERENCE}'
    _indexPath = 'caf-reference/index.xml'


class scriptGenerator(object):
    """
    A class for generation a volume comparision script for structures
    reconstructed from current and reference CAFs.

    @cvar __scriptTemplate: template of the script
    @type __scriptTemplate: str

    @cvar __linePattern: template of the CAF-related part of the script
    @type __linePattern: str

    @ivar __cafNames: names of CAFs to be compared
    @type __cafNames: [str, ...]

    @ivar __dir3dbar: absolute path to the main 3dBAR directory
    @type __dir3dbar: str

    @ivar __nCpus: number of CPU cores to be engaged
    @type __nCpus: int
    """
    __scriptTemplate = """#!/bin/bash
set -xe
export DISPLAY=:0.0;
source %(dir3dbar)s/setbarenv.sh

WORKING_DIR=%(dir3dbar)s/relase_candidate_volume_testing_`date +"%%Y-%%m-%%d_%%H-%%M"`/
REF_VOL_DIR=${WORKING_DIR}reference_volumes/
RELASE_VOL_DIR=${WORKING_DIR}relase_candidate_volumes/

LOG_FILENAME=${WORKING_DIR}vol_comparison.log

JOB_TEMP_REFERENCE=${WORKING_DIR}__temp__job__parallel__reference__comparison.sh
JOB_TEMP_RC=${WORKING_DIR}__temp__job__parallel__testing__comparison.sh

mkdir -p ${RELASE_VOL_DIR} ${REF_VOL_DIR}
rm -rvf ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC}

#BEGIN CAF-dependent lines

%(cafDependent)s

#END CAF-dependent lines

cat ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC} | %(executionCommand)s  > ${LOG_FILENAME}
rm -rvf ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC}

diff -r ${REF_VOL_DIR} ${RELASE_VOL_DIR} > $WORKING_DIR/comparison.diff
"""

    __linePattern = """#BEGIN %(cafName)s

testdir=${REF_VOL_DIR}/%(cafName)s/
%(cafGroupLines)s

testdir=${RELASE_VOL_DIR}/%(cafName)s/
%(refGroupLines)s

#END %(cafName)s"""

    def __init__(self, dir3dbar, cafNames = [], nCpus = 1):
        """
        @param dir3dbar: absolute path to the main 3dBAR directory
        @type dir3dbar: str

        @param cafNames: names of CAFs to be compared
        @type cafNames: [str, ...]

        @param nCpus: number of CPU cores to be engaged
        @type nCpus: int
        """
        self.__cafNames = cafNames
        self.__dir3dbar = dir3dbar
        self.__nCpus = nCpus

    def __str__(self):
        """
        @return: volume comparision script for structures reconstructed from
                 current and reference CAFs
        @rtype: str
        """
        def cafLine(cafName):
            return self.__linePattern % {'cafName': cafName,
                                         'cafGroupLines': cafStructureLines(self.__dir3dbar,
                                                                            cafName),
                                         'refGroupLines': refStructureLines(self.__dir3dbar,
                                                                            cafName)}

        cafDependent = '\n\n'.join(cafLine(x) for x in self.__cafNames)

        executionCommand = 'bash'
        if self.__nCpus > 1:
            executionCommand = 'parallel -j %d -k' % self.__nCpus

        return self.__scriptTemplate % {'dir3dbar': self.__dir3dbar,
                                        'cafDependent': cafDependent,
                                        'executionCommand': executionCommand}

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: %s <3dbar directory> <# cpus> <caf name> [<caf name> ...]" % sys.argv[0]
        sys.exit()

    dir3dbar = sys.argv[1]
    nCpus = int(sys.argv[2])

    print scriptGenerator(dir3dbar, sys.argv[3:], nCpus)
