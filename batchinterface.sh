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

export LC_ALL=C
BAR_DIR=`dirname $(readlink -f $0)`
source ${BAR_DIR}/setbarenv.sh
python -OO $BAR_DIR/bin/reconstructor/batchreconstructor.py $@
