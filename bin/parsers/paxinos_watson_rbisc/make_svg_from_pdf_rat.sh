#!/bin/bash
set -xe

#------------------------------------------------------------------------------
# Author:       Piotr Majka, M.Sc.
# E-mail:       pmajka@nencki.gov.pl
# Affiliation:  Laboratory of Visual System 
#               Nencki Institute of Experimental Biology
#               3 Pasteur St, 02-093 Warsaw, Poland 
#
# Licencing:    GNU General Public License
#               http://www.gnu.org/licenses/gpl.html
#
# usage: ./make_svg_from_pdf_rat.sh source-pdf 2>&1 > res.txt
# Redirects stdout and stderr to file allowing further analysis.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Constants, directories and files definitions
#------------------------------------------------------------------------------
CONF_CORONAL_PAGE_START=44                            # First page of coronal slices
CONF_CORONAL_PAGE_END=204                             # Last page of coronal slices
CONF_SOURCE_PDF_ATLAS_FILENAME=$1                     # Atlas filename
CONF_OUTPUT_SVG_DIR=atlases/paxinos_watson_rbisc/caf-src/
CONF_PARSER_NAME=paxinos_watson_rbisc

#------------------------------------------------------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------------------------------------------------------
CONF_ATLASPARSER_SCRIPT="parser_pax.py -p $CONF_PARSER_NAME    
                         -s $CONF_CORONAL_PAGE_START
                         -e $CONF_CORONAL_PAGE_END
                         -o $CONF_OUTPUT_SVG_DIR
                         -i $CONF_OUTPUT_SVG_DIR"
#------------------------------------------------------------------------------
# Try to create output directory (just to avoid errors)
#------------------------------------------------------------------------------
mkdir -p $CONF_OUTPUT_SVG_DIR

#------------------------------------------------------------------------------
# Check if source atlas file exists (just to avoid errors)
#------------------------------------------------------------------------------
if [ not -e ${CONF_SOURCE_PDF_ATLAS_FILENAME} ]
then
	echo "Source atlas file (${CONF_SOURCE_PDF_ATLAS_FILENAME}) not exist!"
	echo "Check configuration file or atlas file localization."
fi	

#------------------------------------------------------------------------------
# Convert PDF file with atlas to serie of SVG files using pstoedit 
# Disadvantage of this solution is that its impossible to convert all pages
# at once - we have to do it in a loop as converter accepts only one page per
# execution.
#------------------------------------------------------------------------------
for pageNo in `seq -s ' ' $CONF_CORONAL_PAGE_START 1 $CONF_CORONAL_PAGE_END`
do
	fpn=`printf "%03d" $pageNo`
	pstoedit \
		-f plot-svg\
		-v\
		-mergetext\
		-ndt\
		-page $fpn\
		${CONF_SOURCE_PDF_ATLAS_FILENAME} ${CONF_OUTPUT_SVG_DIR}${fpn}.svg
done

#------------------------------------------------------------------------------
# Fix SVG files created by pstoedit as they have many many syntex errors
# - usually lack of spaces and other typos. Code below fixes typical errors
#
# Both loops are separated because they may be considered as separate steps
# which should not be mixed.
#------------------------------------------------------------------------------
for pageNo in `seq -s ' ' $CONF_CORONAL_PAGE_START 1 $CONF_CORONAL_PAGE_END`
do
	fpn=`printf "%03d" $pageNo`
	sed -i.bak 's/"stroke-dashoffset=/" stroke-dashoffset=/g' ${CONF_OUTPUT_SVG_DIR}/${fpn}.svg
	sed -i.bak 's/"fill=/" fill=/g' ${CONF_OUTPUT_SVG_DIR}/${fpn}.svg
done

# Remove backup files
rm ${CONF_OUTPUT_SVG_DIR}*.bak

#------------------------------------------------------------------------------
# Trace files using AtlasParser as a standalone module.
#------------------------------------------------------------------------------
python $CONF_ATLASPARSER_SCRIPT
python $CONF_ATLASPARSER_SCRIPT --create-only-index-file
