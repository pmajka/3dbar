#!/bin/bash
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
set -xe
export DISPLAY=:0.0;

WORKING_DIR=`pwd`/relase_candidate_volume_testing_`date +"%Y-%m-%d_%H-%M"`/
REF_VOL_DIR=${WORKING_DIR}/reference_volumes/
RELASE_VOL_DIR=${WORKING_DIR}/relase_candidate_volumes/

LOG_FILENAME=${WORKING_DIR}/vol_comparison.log

JOB_TEMP_REFERENCE=${WORKING_DIR}/__temp__job__parallel__reference__comparison.sh
JOB_TEMP_RC=${WORKING_DIR}/__temp__job__parallel__testing__comparison

NUMBER_OF_CPUS=16
EXECUTION_COMMAND="parallel -j 16 -k"
#EXECUTION_COMMAND="bash" #TIP: Put bash if you don't have GNU parallel installed

DATASET_NAMES=(aba sba_DB08 sba_LPBA40_on_SRI24 sba_PHT00 sba_RM_on_F99 sba_WHS09 sba_WHS10 tem whs_0.5 whs_0.51 whs_0.5_symm whs_0.6.1)
DATASET_HROOT=(Brain Br Brain Brain Brain Brain Brain Brain Brain Brain Brain Brain)

mkdir -p ${RELASE_VOL_DIR} ${REF_VOL_DIR}
rm -rvf ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC}

for element in $(seq 0 $((${#DATASET_NAMES[@]} - 1)))
do
    dataset=${DATASET_NAMES[$element]}
    hierarchyroot=${DATASET_HROOT[$element]}
    testdir=${REF_VOL_DIR}/${dataset}/
    atlasdir=`pwd`/atlases/${dataset}/caf-reference/index.xml
    echo "mkdir -p $testdir; ./batchinterface.sh -g 999 $atlasdir --exportToNiftii -e $testdir" $hierarchyroot >> ${JOB_TEMP_REFERENCE}
done

for element in $(seq 0 $((${#DATASET_NAMES[@]} - 1)))
do
    dataset=${DATASET_NAMES[$element]}
    hierarchyroot=${DATASET_HROOT[$element]}
    testdir=${RELASE_VOL_DIR}/${dataset}/
    atlasdir=`pwd`/atlases/${dataset}/caf/index.xml
    echo "mkdir -p $testdir; ./batchinterface.sh -g 999 $atlasdir --exportToNiftii -e $testdir" $hierarchyroot >> ${JOB_TEMP_RC}
done

cat ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC} | ${EXECUTION_COMMAND}  > ${LOG_FILENAME}
rm -rvf ${JOB_TEMP_REFERENCE} ${JOB_TEMP_RC}

diff -r ${REF_VOL_DIR} ${RELASE_VOL_DIR} > $WORKING_DIR/comparison.diff
