#!/bin/sh
#remove the paczuszka directory (if exists)
rm -rf /tmp/3dbar
#and create it
mkdir /tmp/3dbar

#download latest revision
svn co  http://svn.3dbar.org/svn/3dbar_sharable/trunk /tmp/3dbar/

#remove svn entries
find /tmp/3dbar -iname '.svn' -print0 | xargs -0 rm -rfv

#remove unnecessary parsers
rm -rfv /tmp/3dbar/bin/parsers/gvp 
rm -rfv /tmp/3dbar/bin/parsers/nl_olek/
rm -rfv /tmp/3dbar/bin/parsers/tem     
rm -rfv /tmp/3dbar/bin/parsers/vector-test 
rm -rfv /tmp/3dbar/bin/parsers/whs_0.6.1

#backup pipelines...
mv /tmp/3dbar/auxiliary_scripts/pipelines /tmp/3dbar/
#...and remove auxilary scripts
rm -rfv /tmp/3dbar/auxiliary_scripts

#provide paczuszka's makefile
mv /tmp/3dbar/Makefile.paczuszka /tmp/3dbar/Makefile

#remove existing paczuszka
rm 3dbar.zip

#and create a new one
wd=`pwd`
echo "directory: $wd"
cd /tmp/3dbar
zip -9 -r $wd/3dbar.zip *
cd $wd
rm -rf /tmp/3dbar
