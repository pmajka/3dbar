set -x 

dataset=sba_PHT00
rootstructure=Brain
wd=atlases/${dataset}/benchmark/
res=0.0215

    mkdir -p ${wd}/hq ${wd}/raw ${wd}/lq
    ./batchinterface.sh -g 99 -d $res $res -e ${wd}/raw/ -p auxiliary_scripts/pipelines/${dataset}-Thumbnail.xml atlases/${dataset}/caf/index.xml --exportToVTKPolydata ${rootstructure}
    ./batchinterface.sh -g 99 -d $res $res -e ${wd}/hq/ -p auxiliary_scripts/pipelines/${dataset}-HQ.xml atlases/${dataset}/caf/index.xml --exportToVTKPolydata ${rootstructure}
    ./batchinterface.sh -g 99 -d $res $res -e ${wd}/lq/ -p auxiliary_scripts/pipelines/${dataset}-LQ.xml atlases/${dataset}/caf/index.xml --exportToVTKPolydata ${rootstructure}


for f in `ls $wd/raw/*`
do
   ff=`basename $f`
   python x.py $ff $res $res $f ${wd}/hq/${ff} ${wd}/lq/$ff >> ${dataset}_benchmark.txt
done
