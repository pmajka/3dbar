set -xe
export DISPLAY=:0.0;

VIEWPORT=" --cameraMovementAngles -45.126941 23.103881 121.881318 "

TPL_VOLUME=".nii.gz"
TPL_VRML_RAW=".wrl"
TPL_VRML_GZIP=".wrl.gz"
TPL_X3D_RAW=".x3d"
TPL_X3D_GZIP=".x3d.gz"
TPL_SCREENSHOT="screenshot"
TPL_THUMBNAIL="thumbnail"

#ATLAS=$1
#PIPELINE=$2

function processSingleRegularPipeline {
    local PIPELINE=$2
    local ATLAS=$1
    local PIPELINE_DIR=`pwd`/pipeline_test_`date +"%Y-%m-%d"`/`basename ${PIPELINE} .xml`_`date +%s`/
    mkdir -p $PIPELINE_DIR
    
    local LOGFILE=${PIPELINE_DIR}/log.txt
    local REPORTFILE=${PIPELINE_DIR}/report.txt
    
   DISPLAY=:0.0;
   /home/pmajka/3dbrainatlases/batchinterface.sh $ATLAS \
       Brain -g 999 \
       -p ${PIPELINE} \
       -e $PIPELINE_DIR \
       ${VIEWPORT} \
       --exportToNiftii \
       --exportToVRML \
       --exportToX3d \
       --exportScreenshot \
       --exportThumbnail > $LOGFILE
    
    echo -e "Volumes size:\t` filesSize $PIPELINE_DIR/\*$TPL_VOLUME`" >> $REPORTFILE
    echo -e "VRML (uncompressed) size:\t` filesSize $PIPELINE_DIR/\*$TPL_VRML_RAW`" >> $REPORTFILE
    echo -e "X3D (uncompressed) size:\t` filesSize $PIPELINE_DIR/\*$TPL_X3D_RAW`" >> $REPORTFILE
    echo -e "Thumbnails size:\t`filesSize $PIPELINE_DIR/\*$TPL_THUMBNAIL\*`" >> $REPORTFILE
    echo -e "Screenshots size:\t`filesSize $PIPELINE_DIR/\*$TPL_SCREENSHOT\*`" >> $REPORTFILE
    
    gzip $PIPELINE_DIR/*$TPL_VRML_RAW
    gzip $PIPELINE_DIR/*$TPL_X3D_RAW
    
    echo -e "VRML (compressed) size:\t` filesSize $PIPELINE_DIR/\*$TPL_VRML_GZIP`" >> $REPORTFILE
    echo -e "X3D (compressed) size:\t` filesSize $PIPELINE_DIR/\*$TPL_X3D_GZIP`" >> $REPORTFILE
    echo -e "Numer of reconstructions:\t`ls -1 $PIPELINE_DIR/thumbnail*.png | wc -l`" >> $REPORTFILE
    
}

function filesSize {
local size=`ls -lS --block-size=1 $1 \
    | awk '{print $5,$6,$7,$8,$9}' \
    | awk '{sum = sum + $1} END {print sum/(1024*1024)}'`
echo ${size}
}

for ATLAS in paxinos_watson_rbisc/caf-src/index.xml paxinos_franklin_mbisc/caf-src/index.xml
do
    for PIPELINE in pf_hi.xml pf_low.xml pf_sm.xml
    do
        processSingleRegularPipeline ${ATLAS} ${PIPELINE}
    done
done
