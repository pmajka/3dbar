#!/bin/bash
set -xe

SCRIPT_FNAME='piptest.py'

for file in `ls $1/*.xml`
do
    ofn=`basename ${file}`
    python ${SCRIPT_FNAME} ${file} $1/${ofn%.*}.png
done
