#------------------------------------------------------------------------------
# Author:       Piotr Majka, M.Sc.
# E-mail:       pmajka@nencki.gov.pl
# Affiliation:  Laboratory of Neuroinformatics
#               Nencki Institute of Experimental Biology
#               3 Pasteur St, 02-093 Warsaw, Poland 
#
# Licencing:    GNU General Public License
#               http://www.gnu.org/licenses/gpl.html
#
#------------------------------------------------------------------------------
PARSERS_DIR  = bin/parsers/
ATLASES_DIR  = atlases/

SBA_PARSERS  = sba_DB08 sba_PHT00 sba_WHS09 sba_WHS10 sba_LPBA40_on_SRI24 sba_RM_on_F99 sba_FVE91_on_F99
FAST_PARSERS = nl_olek ${SBA_PARSERS} tem
WHS          = whs_0.5 whs_0.51 whs_0.5_symm whs_0.6.1 whs_0.6.2
PARSERS      = aba aba2011 ${FAST_PARSERS} ${WHS}

all: clean ${PARSERS} doc
	echo "Done"

doc_clean:
	rm -rfv doc/api doc/gui/ doc/service

doc: doc_api doc_gui doc_service
	echo "Done doc"

doc_api:
	mkdir -p doc/api/html
	epydoc lib/pymodules/python2.6/bar -v --graph all --no-sourcecode --output doc/api/html
	cd doc/sphinx/; make html; python -m doctest source/*.rst

doc_gui:
	mkdir -p doc/gui/html
	epydoc bin/reconstructor -v --graph all  --output doc/gui/html

doc_service:
	mkdir -p doc/service/html
	epydoc bin/sql -v --graph all   --output doc/service/html

parsers: ${PARSERS}

parsers_fast: ${FAST_PARSERS}
	echo "Done"

parsers_sba: ${SBA_PARSERS}
	echo "Done"
	
whs_0.5:
	mkdir -p ${ATLASES_DIR}whs_0.5/src
	mkdir -p ${ATLASES_DIR}whs_0.5/caf
	wget --keep-session-cookies --save-cookies ${ATLASES_DIR}whs_0.5/src/cookies.txt --post-data 'username=civmpub&password=civmpub' http://civmvoxport.duhs.duke.edu/voxbase/login.php -O /dev/null
	wget --load-cookies ${ATLASES_DIR}whs_0.5/src/cookies.txt http://civmvoxport.duhs.duke.edu/voxbase/downloaddataset.php?stackID=18746 -O ${ATLASES_DIR}whs_0.5/src/canon_labels_r.nii.gz
	rm  ${ATLASES_DIR}whs_0.5/src/cookies.txt
	gunzip -f -d ${ATLASES_DIR}whs_0.5/src/canon_labels_r.nii.gz
	python   ${PARSERS_DIR}whs_0.5/__init__.py
	if [ -e ${ATLASES_DIR}whs_0.5/caf-reference ]; then diff -r  ${ATLASES_DIR}whs_0.5/caf ${ATLASES_DIR}whs_0.5/caf-reference > diff_whs_0.5.txt; fi

whs_0.5_symm:
	mkdir -p ${ATLASES_DIR}whs_0.5_symm/src
	mkdir -p ${ATLASES_DIR}whs_0.5_symm/caf
	wget --keep-session-cookies --save-cookies ${ATLASES_DIR}whs_0.5_symm/src/cookies.txt --post-data 'username=civmpub&password=civmpub' http://civmvoxport.duhs.duke.edu/voxbase/login.php -O /dev/null
	wget --load-cookies ${ATLASES_DIR}whs_0.5_symm/src/cookies.txt http://civmvoxport.duhs.duke.edu/voxbase/downloaddataset.php?stackID=20494 -O ${ATLASES_DIR}whs_0.5_symm/src/SYMCLabel.nii.gz
	rm  ${ATLASES_DIR}whs_0.5_symm/src/cookies.txt
	gunzip -f -d ${ATLASES_DIR}whs_0.5_symm/src/SYMCLabel.nii.gz
	python   ${PARSERS_DIR}whs_0.5_symm/__init__.py
	if [ -e ${ATLASES_DIR}whs_0.5_symm/caf-reference ]; then diff -r  ${ATLASES_DIR}whs_0.5_symm/caf ${ATLASES_DIR}whs_0.5_symm/caf-reference > diff_whs_0.5_symm.txt; fi

whs_0.51:
	mkdir -p ${ATLASES_DIR}whs_0.51/src
	mkdir -p ${ATLASES_DIR}whs_0.51/caf
	wget -O ${ATLASES_DIR}whs_0.51/src/whs051mbatatlas.zip "http://software.incf.org/software/waxholm-space/waxholm-space/LabeledAtlas0.5.1/file_download?file_field=file"
	unzip -o ${ATLASES_DIR}whs_0.51/src/whs051mbatatlas.zip -d ${ATLASES_DIR}whs_0.51/src/
	rm ${ATLASES_DIR}whs_0.51/src/whs051mbatatlas.zip
	python   ${PARSERS_DIR}whs_0.51/__init__.py
	if [ -e ${ATLASES_DIR}whs_0.51/caf-reference ]; then diff -r  ${ATLASES_DIR}whs_0.51/caf ${ATLASES_DIR}whs_0.51/caf-reference > diff_whs_0.51.txt; fi

whs_0.6.1:
	mkdir -p ${ATLASES_DIR}whs_0.6.1/src
	mkdir -p ${ATLASES_DIR}whs_0.6.1/caf
	python   ${PARSERS_DIR}whs_0.6.1/__init__.py
	if [ -e ${ATLASES_DIR}whs_0.6.1/caf-reference ]; then diff -r  ${ATLASES_DIR}whs_0.6.1/caf ${ATLASES_DIR}whs_0.6.1/caf-reference > diff_whs_0.6.1.txt; fi

whs_0.6.2:
	mkdir -p ${ATLASES_DIR}whs_0.6.2/src
	mkdir -p ${ATLASES_DIR}whs_0.6.2/caf
	wget -O ${ATLASES_DIR}whs_0.6.2/src/whs_0.6.2_atlas.zip "http://software.incf.org/software/waxholm-space/waxholm-space/mbat-ready-label-volume-v0.6.2/file_download?file_field=file"
	unzip -o ${ATLASES_DIR}whs_0.6.2/src/whs_0.6.2_atlas.zip -d ${ATLASES_DIR}whs_0.6.2/src/
	rm ${ATLASES_DIR}whs_0.6.2/src/whs_0.6.2_atlas.zip
	python   ${PARSERS_DIR}whs_0.6.2/__init__.py
	if [ -e ${ATLASES_DIR}whs_0.6.2/caf-reference ]; then diff -r  ${ATLASES_DIR}whs_0.6.2/caf ${ATLASES_DIR}whs_0.6.2/caf-reference > diff_whs_0.6.2.txt; fi

nl_olek:
	mkdir -p ${ATLASES_DIR}nl_olek/caf
	python ${PARSERS_DIR}nl_olek/__init__.py
	if [ -e ${ATLASES_DIR}nl_olek/caf-reference ]; then diff -r ${ATLASES_DIR}nl_olek/caf ${ATLASES_DIR}nl_olek/caf-reference > diff_neurolucidaXML.txt; fi

vector-test:
	mkdir -p ${ATLASES_DIR}vector-test/caf
	python ${PARSERS_DIR}vector-test/__init__.py
	if [ -e ${ATLASES_DIR}vector-test/caf-reference ]; then diff -r ${ATLASES_DIR}vector-test/caf ${ATLASES_DIR}vector-test/caf-reference > diff_vector-test.txt; fi

sba_DB08:
	mkdir -p ${ATLASES_DIR}sba_DB08/src
	mkdir -p ${ATLASES_DIR}sba_DB08/caf
	python ${PARSERS_DIR}sba_DB08/__init__.py
	if [ -e ${ATLASES_DIR}sba_DB08/caf-reference ]; then diff -r ${ATLASES_DIR}sba_DB08/caf ${ATLASES_DIR}sba_DB08/caf-reference > diff_sba_DB08.txt; fi

sba_PHT00:
	mkdir -p ${ATLASES_DIR}sba_PHT00/src
	mkdir -p ${ATLASES_DIR}sba_PHT00/caf
	python ${PARSERS_DIR}sba_PHT00/__init__.py
	if [ -e ${ATLASES_DIR}sba_PHT00/caf-reference ]; then diff -r ${ATLASES_DIR}sba_PHT00/caf ${ATLASES_DIR}sba_PHT00/caf-reference > diff_sba_PHT00.txt; fi

sba_WHS09:
	mkdir -p ${ATLASES_DIR}sba_WHS09/src
	mkdir -p ${ATLASES_DIR}sba_WHS09/caf
	python ${PARSERS_DIR}sba_WHS09/__init__.py
	if [ -e ${ATLASES_DIR}sba_WHS09/caf-reference ]; then diff -r ${ATLASES_DIR}sba_WHS09/caf ${ATLASES_DIR}sba_WHS09/caf-reference > diff_sba_WHS09.txt; fi

sba_WHS10:
	mkdir -p ${ATLASES_DIR}sba_WHS10/src
	mkdir -p ${ATLASES_DIR}sba_WHS10/caf
	python ${PARSERS_DIR}sba_WHS10/__init__.py
	if [ -e ${ATLASES_DIR}sba_WHS10/caf-reference ]; then diff -r ${ATLASES_DIR}sba_WHS10/caf ${ATLASES_DIR}sba_WHS10/caf-reference > diff_sba_WHS10.txt; fi

sba_LPBA40_on_SRI24:
	mkdir -p ${ATLASES_DIR}sba_LPBA40_on_SRI24/src
	mkdir -p ${ATLASES_DIR}sba_LPBA40_on_SRI24/caf
	python ${PARSERS_DIR}sba_LPBA40_on_SRI24/__init__.py
	if [ -e ${ATLASES_DIR}sba_LPBA40_on_SRI24/caf-reference ]; then diff -r ${ATLASES_DIR}sba_LPBA40_on_SRI24/caf ${ATLASES_DIR}sba_LPBA40_on_SRI24/caf-reference > diff_sba_LPBA40_on_SRI24.txt; fi

sba_RM_on_F99:
	mkdir -p ${ATLASES_DIR}sba_RM_on_F99/src
	mkdir -p ${ATLASES_DIR}sba_RM_on_F99/caf
	python ${PARSERS_DIR}sba_RM_on_F99/__init__.py
	if [ -e ${ATLASES_DIR}sba_RM_on_F99/caf-reference ]; then diff -r ${ATLASES_DIR}sba_RM_on_F99/caf ${ATLASES_DIR}sba_RM_on_F99/caf-reference > diff_sba_RM_on_F99.txt; fi

sba_FVE91_on_F99:
	mkdir -p ${ATLASES_DIR}sba_FVE91_on_F99/src
	mkdir -p ${ATLASES_DIR}sba_FVE91_on_F99/caf
	python ${PARSERS_DIR}sba_FVE91_on_F99/__init__.py
	if [ -e ${ATLASES_DIR}sba_FVE91_on_F99/caf-reference ]; then diff -r ${ATLASES_DIR}sba_FVE91_on_F99/caf ${ATLASES_DIR}sba_FVE91_on_F99/caf-reference > diff_sba_FVE91_on_F99.txt; fi

sba_B05_on_Conte69:
	mkdir -p ${ATLASES_DIR}sba_B05_on_Conte69/src
	mkdir -p ${ATLASES_DIR}sba_B05_on_Conte69/caf
	wget -O ${ATLASES_DIR}sba_B05_on_Conte69/src/Human_Conte69_L_brodmann_paint_to_volume.nii.gz "http://sba.incf.org/B05_on_Conte69/source/Human_Conte69_L_brodmann_paint_to_volume.nii.gz"
	wget -O ${ATLASES_DIR}sba_B05_on_Conte69/src/index2acr_Human_Conte69_L_brodmann_paint_to_volume.json "http://sba.incf.org/B05_on_Conte69/source/index2acr_Human_Conte69_L_brodmann_paint_to_volume.json"
	python ${PARSERS_DIR}sba_B05_on_Conte69/__init__.py
	python ${PARSERS_DIR}sba_B05_on_Conte69/__init__volume.py
	if [ -e ${ATLASES_DIR}sba_B05_on_Conte69/caf-reference ]; then diff -r ${ATLASES_DIR}B05_on_Conte69/caf ${ATLASES_DIR}sba_B05_on_Conte69/caf-reference > diff_sba_B05_on_Conte69.txt; fi

aba:
	mkdir -p ${ATLASES_DIR}aba/src
	mkdir -p ${ATLASES_DIR}aba/caf
	python   ${PARSERS_DIR}aba/preprocess_volume.py
	python   ${PARSERS_DIR}aba/__init__.py
	if [ -e ${ATLASES_DIR}aba/caf-reference ]; then diff -r  ${ATLASES_DIR}aba/caf ${ATLASES_DIR}aba/caf-reference > diff_aba.txt; fi

aba2011:
	mkdir -p ${ATLASES_DIR}aba2011/src
	mkdir -p ${ATLASES_DIR}aba2011/caf
	python   ${PARSERS_DIR}aba2011/__init__.py
	if [ -e ${ATLASES_DIR}aba2011/caf-reference ]; then diff -r  ${ATLASES_DIR}aba2011/caf ${ATLASES_DIR}2011/caf-reference > diff_aba2011.txt; fi

tem:
	mkdir -p ${ATLASES_DIR}tem/src
	mkdir -p ${ATLASES_DIR}tem/caf
	python ${PARSERS_DIR}tem/preprocess_data.py
	python ${PARSERS_DIR}tem/__init__.py
	if [ -e ${ATLASES_DIR}tem/caf-reference ]; then diff -r  ${ATLASES_DIR}tem/caf ${ATLASES_DIR}tem/caf-reference > diff_tem.txt; fi

mbisc_11:
	mkdir -p ${ATLASES_DIR}mbisc_11/src
	mkdir -p ${ATLASES_DIR}mbisc_11/caf
	#python ${PARSERS_DIR}/mbisc_11/preprocessSVG.py ${ATLASES_DIR}mbisc_11/src/src_atlas.svg "${ATLASES_DIR}mbisc_11/src/%03d_v1.svg"
	python ${PARSERS_DIR}/mbisc_11/__init__.py
	if [ -e ${ATLASES_DIR}mbisc_11/caf-reference ]; then diff -r  ${ATLASES_DIR}mbisc_11/caf ${ATLASES_DIR}mbisc_11/caf-reference > diff_mbisc_11.txt; fi

clean: clean_diff doc_clean
	rm -rfv ${ATLASES_DIR}sba_DB08/caf ${ATLASES_DIR}sba_DB08/src
	rm -rfv ${ATLASES_DIR}sba_PHT00/caf ${ATLASES_DIR}sba_PHT00/src
	rm -rfv ${ATLASES_DIR}sba_WHS09/caf ${ATLASES_DIR}sba_WHS09/caf/src
	rm -rfv ${ATLASES_DIR}sba_WHS10/caf ${ATLASES_DIR}sba_WHS10/src
	rm -rfv ${ATLASES_DIR}sba_LPBA40_on_SRI24/caf ${ATLASES_DIR}sba_LPBA40_on_SRI24/src
	rm -rfv ${ATLASES_DIR}sba_RM_on_F99/caf ${ATLASES_DIR}sba_RM_on_F99/src
	rm -rfv ${ATLASES_DIR}sba_FVE91_on_F99/caf ${ATLASES_DIR}sba_FVE91_on_F99/src
	rm -rfv ${ATLASES_DIR}sba_B05_on_Conte69/caf ${ATLASES_DIR}sba_B05_on_Conte69/src
	rm -rfv ${ATLASES_DIR}whs_0.51/caf
	rm -rfv ${ATLASES_DIR}whs_0.6.1/caf
	rm -rfv ${ATLASES_DIR}whs_0.6.2/caf
	rm -rfv ${ATLASES_DIR}whs_0.5/caf 
	rm -rfv ${ATLASES_DIR}whs_0.5_symm/caf 
	rm -rfv ${ATLASES_DIR}vector-test/caf
	rm -rfv ${ATLASES_DIR}nl_olek/caf
	rm -rfv ${ATLASES_DIR}aba/caf ${ATLASES_DIR}aba/src
	rm -rfv ${ATLASES_DIR}aba2011/caf ${ATLASES_DIR}aba2011/src
	rm -rfv ${ATLASES_DIR}tem/caf ${ATLASES_DIR}tem/src
	rm -rfv ${ATLASES_DIR}mbisc_11/caf ${ATLASES_DIR}mbisc_11/src

reference_datasets:
	rm -rf ${ATLASES_DIR}whs_0.5/caf-reference; cp -r ${ATLASES_DIR}whs_0.5/caf ${ATLASES_DIR}whs_0.5/caf-reference
	rm -rf ${ATLASES_DIR}whs_0.5_symm/caf-reference; cp -r ${ATLASES_DIR}whs_0.5_symm/caf ${ATLASES_DIR}whs_0.5_symm/caf-reference
	rm -rf ${ATLASES_DIR}whs_0.51/caf-reference; cp -r ${ATLASES_DIR}whs_0.51/caf ${ATLASES_DIR}whs_0.51/caf-reference
	rm -rf ${ATLASES_DIR}whs_0.6.1/caf-reference; cp -r ${ATLASES_DIR}whs_0.6.1/caf ${ATLASES_DIR}whs_0.6.1/caf-reference
	rm -rf ${ATLASES_DIR}whs_0.6.2/caf-reference; cp -r ${ATLASES_DIR}whs_0.6.2/caf ${ATLASES_DIR}whs_0.6.2/caf-reference
	rm -rf ${ATLASES_DIR}nl_olek/caf-reference; cp -r ${ATLASES_DIR}nl_olek/caf ${ATLASES_DIR}nl_olek/caf-reference
	rm -rf ${ATLASES_DIR}vector-test/caf-reference; cp -r ${ATLASES_DIR}vector-test/caf ${ATLASES_DIR}vector-test/caf-reference
	rm -rf ${ATLASES_DIR}sba_DB08/caf-reference; cp -r ${ATLASES_DIR}sba_DB08/caf ${ATLASES_DIR}sba_DB08/caf-reference
	rm -rf ${ATLASES_DIR}sba_PHT00/caf-reference; cp -r ${ATLASES_DIR}sba_PHT00/caf ${ATLASES_DIR}sba_PHT00/caf-reference
	rm -rf ${ATLASES_DIR}sba_WHS09/caf-reference; cp -r ${ATLASES_DIR}sba_WHS09/caf ${ATLASES_DIR}sba_WHS09/caf-reference
	rm -rf ${ATLASES_DIR}sba_WHS10/caf-reference; cp -r ${ATLASES_DIR}sba_WHS10/caf ${ATLASES_DIR}sba_WHS10/caf-reference
	rm -rf ${ATLASES_DIR}sba_LPBA40_on_SRI24/caf-reference; cp -r ${ATLASES_DIR}sba_LPBA40_on_SRI24/caf ${ATLASES_DIR}sba_LPBA40_on_SRI24/caf-reference
	rm -rf ${ATLASES_DIR}sba_RM_on_F99/caf-reference; cp -r ${ATLASES_DIR}sba_RM_on_F99/caf ${ATLASES_DIR}sba_RM_on_F99/caf-reference
	rm -rf ${ATLASES_DIR}sba_FVE91_on_F99/caf-reference; cp -r ${ATLASES_DIR}sba_FVE91_on_F99/caf ${ATLASES_DIR}sba_FVE91_on_F99/caf-reference
	rm -rf ${ATLASES_DIR}sba_B05_on_Conte69/caf-reference; cp -r ${ATLASES_DIR}sba_B05_on_Conte69/caf ${ATLASES_DIR}sba_B05_on_Conte69/caf-reference
	rm -rf ${ATLASES_DIR}aba/caf-reference; cp -r ${ATLASES_DIR}aba/caf ${ATLASES_DIR}aba/caf-reference
	rm -rf ${ATLASES_DIR}aba2011/caf-reference; cp -r ${ATLASES_DIR}aba2011/caf ${ATLASES_DIR}aba2011/caf-reference
	rm -rf ${ATLASES_DIR}tem/caf-reference; cp -r ${ATLASES_DIR}tem/caf ${ATLASES_DIR}tem/caf-reference
	rm -rf ${ATLASES_DIR}mbisc_11/caf-reference; cp -r ${ATLASES_DIR}mbisc_11/caf ${ATLASES_DIR}mbisc_11/caf-reference

clean_diff:
	rm -rfv diff_neurolucidaXML.txt diff_vector-test.txt\
		    diff_whs_0.51.txt diff_whs_0.5.txt diff_sba_PHT00.txt diff_sba_DB08.txt\
			diff_sba_WHS09.txt diff_sba_WHS10.txt diff_sba_LPBA40_on_SRI24.txt\
			diff_sba_RM_on_F99.txt diff_aba.txt diff_tem.txt diff_whs_0.6.1.txt diff_whs_0.6.2.txt\
			diff_sba_FVE91_on_F99.txt diff_aba2011.txt diff_sba_B05_on_Conte69.txt \
			diff_mbisc_11.txt

