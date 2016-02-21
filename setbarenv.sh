#!/bin/bash

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

BAR_DIR=`dirname $(readlink -f $0)`
BAR_PATH=${BAR_DIR}'/lib/pymodules/python2.6/'
export PYTHONPATH=$PYTHONPATH:$BAR_PATH
export BAR_WEB_SERVICE_ATLASES_PATH=${BAR_DIR}'/atlases/'
