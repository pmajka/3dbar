#!/bin/bash
set -xe

SCRIPT_FNAME='piptest.py'

for file in `ls $1/*.xml`
do
    python ${SCRIPT_FNAME} ${file} > temp.dot
    dot -T png -o temp.png temp.dot
    
    ofn=`basename ${file}`
    mv temp.png $1/${ofn%.*}.png
    rm temp.dot
done
