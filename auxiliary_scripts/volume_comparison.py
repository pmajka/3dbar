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

SCRIPT_TEMPLATE = """#!/bin/bash
set -xe
export DISPLAY=:0.0;
source %(dir3dbar)s/setbarenv.sh

WORKING_DIR=%(dir3dbar)s/relase_candidate_volume_testing_`date +"%%Y-%%m-%%d_%%H-%%M"`/
REF_VOL_DIR=${WORKING_DIR}/reference_volumes/
RELASE_VOL_DIR=${WORKING_DIR}/relase_candidate_volumes/

LOG_FILENAME=${WORKING_DIR}/vol_comparison.log

JOB_TEMP_REFERENCE=${WORKING_DIR}/__temp__job__parallel__reference__comparison.sh
JOB_TEMP_RC=${WORKING_DIR}/__temp__job__parallel__testing__comparison

mkdir -p ${RELASE_VOL_DIR} ${REF_VOL_DIR}
rm -rvf ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC}

#BEGIN CAF-dependent lines

%(cafDependent)s

#END CAF-dependent lines

cat ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC} | %(executionCommand)s  > ${LOG_FILENAME}
rm -rvf ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC}

diff -r ${REF_VOL_DIR} ${RELASE_VOL_DIR} > $WORKING_DIR/comparison.diff
"""

def cafLines(cafName, dir3dbar):
    result = """#BEGIN %(cafName)s

testdir=${REF_VOL_DIR}/%(cafName)s/
echo "mkdir -p $testdir; %(dir3dbar)s/batchinterface.sh -g 999 %(dir3dbar)s/atlases/%(cafName)s/caf-reference/index.xml --exportToNiftii -e $testdir %(rootElement)s" >> ${JOB_TEMP_REFERENCE}

testdir=${RELASE_VOL_DIR}/%(cafName)s/
echo "mkdir -p $testdir; %(dir3dbar)s/batchinterface.sh -g  999 %(dir3dbar)s/atlases/%(cafName)s/caf/index.xml --exportToNiftii -e $testdir %(rootElement)s" >> ${JOB_TEMP_RC}

#END %(cafName)s"""
    indexer = bar.barIndexer.fromXML(os.path.join(dir3dbar,
                                                  'atlases',
                                                  cafName,
                                                  'caf-reference/index.xml'))
    return result % {'cafName': cafName,
                     'dir3dbar': dir3dbar,
                     'rootElement': indexer.hierarchyRootElementName}

def cafLines2(cafName, dir3dbar):
    #TODO: filtrowac index.groups.values() po uidList
    result = """#BEGIN %(cafName)s

testdir=${REF_VOL_DIR}/%(cafName)s/
%(cafGroupLines)s

testdir=${RELASE_VOL_DIR}/%(cafName)s/
%(refGroupLines)s

#END %(cafName)s"""

    cafLinePattern = 'echo "mkdir -p $testdir; %%(dir3dbar)s/batchinterface.sh %%(dir3dbar)s/atlases/%%(cafName)s/caf-reference/index.xml --exportToNiftii -e $testdir %s" >> ${JOB_TEMP_REFERENCE}'
    refLinePattern = 'echo "mkdir -p $testdir; %%(dir3dbar)s/batchinterface.sh %%(dir3dbar)s/atlases/%%(cafName)s/caf/index.xml --exportToNiftii -e $testdir %s" >> ${JOB_TEMP_RC}'

    refIndexer = bar.barIndexer.fromXML(os.path.join(dir3dbar,
                                                     'atlases',
                                                     cafName,
                                                     'caf-reference/index.xml'))

    cafIndexer = bar.barIndexer.fromXML(os.path.join(dir3dbar,
                                                     'atlases',
                                                     cafName,
                                                     'caf/index.xml'))

    cafGroups = [x.name for x in cafIndexer.groups.values() if x.uidList != []]
    refGroups = [x.name for x in refIndexer.groups.values() if x.uidList != []]
    
    cafGroupLines = '\n'.join(cafLinePattern % x for x in cafGroups)

    refGroupLines = '\n'.join(cafLinePattern % x for x in refGroups)    


    return result % {'cafName': cafName,
                     'dir3dbar': dir3dbar,
                     'cafGroupLines': cafGroupLines,
                     'refGroupLines': refGroupLines}


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: %s <3dbar directory> <# cpus> <caf name> [<caf name> ...]" % sys.argv[0]
        sys.exit()

    #workingDir = os.path.join(sys.argv[0],
    #                          datetime.datetime.now().strftime('relase_candidate_volume_testing_%Y-%m-%d_%H-%M'))

    dir3dbar = sys.argv[1]
    nCpus = int(sys.argv[2])

    executionCommand = 'parallel -j %d -k' % nCpus
    if nCpus <= 1:
        executionCommand = 'bash'

    cafDependent = '\n\n'.join(cafLines2(cafName, dir3dbar) for cafName in sys.argv[3:])

    print SCRIPT_TEMPLATE % {'dir3dbar': dir3dbar,
                             'cafDependent': cafDependent,
                             'executionCommand': executionCommand}
