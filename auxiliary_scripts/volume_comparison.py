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
    _linePattern = None
    _indexPath = None

    def __init__(self, dir3dbar, cafName):
        self.__indexer = bar.barIndexer.fromXML(os.path.join(dir3dbar,
                                                             'atlases',
                                                             cafName,
                                                             self._indexPath))
        self.__linePattern = self._linePattern % {'dir3dbar': dir3dbar,
                                                  'cafName': cafName}

    def __str__(self):
        groups = [k for (k, v) in self.__indexer.groups.items() if v.uidList != []]
        return '\n'.join(self.__linePattern % x for x in groups)


class cafStructureLines(structureLines):
    _linePattern = 'echo "mkdir -p $testdir; %(dir3dbar)s/batchinterface.sh %(dir3dbar)s/atlases/%(cafName)s/caf/index.xml --exportToNiftii -e $testdir %%s" >> ${JOB_TEMP_RC}'
    _indexPath = 'caf/index.xml'


class refStructureLines(structureLines):
    _linePattern = 'echo "mkdir -p $testdir; %(dir3dbar)s/batchinterface.sh %(dir3dbar)s/atlases/%(cafName)s/caf-reference/index.xml --exportToNiftii -e $testdir %%s" >> ${JOB_TEMP_REFERENCE}'
    _indexPath = 'caf-reference/index.xml'


class scriptGenerator(object):
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
        self.__cafNames = cafNames
        self.__dir3dbar = dir3dbar
        self.__nCpus = nCpus

    def __str__(self):
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
