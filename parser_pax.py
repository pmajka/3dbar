#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2012 Piotr Majka, Jakub M. Kowalski                   #
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

"""
This srcipt is designed to handle AtlasParser as a separate module,
preferably in batch mode, without involving GUI and whole visualization tools.

Purpose if the module is to create 'parsed SVG' files which can be used to create
actual 3D models using other 3D Brain Atlas Reconstructor modules. Because of that,
it does not require VTK library and other 3D graphics packages.

Ultimately, this script would handle PARSE and update actions.
Parse action created 'Traced SVG' file from scratch while update action removes
old versions of 'Traced' and 'Pretraced' files.

Typical execution command is:
chmod +x extract_from_input_atlas.py
./extract_from_input_atlas.py -s 44 -e 204 -o /home/pmajka/3dbrainatlases/input_atlases/paxinos_watson_rat/raw_svg

To create index file following command has to be executed:
./extract_from_input_atlas.py --create-structure-index-file
"""

import os
import sys
from optparse import OptionParser,OptionGroup

def printRed(str):
    """
    @type  str: string
    @param str: String to print to stderr in red.
    @return   : Nothing, just prints the string.

    Prints given string to stderr using red color.
    """
    print >>sys.stderr, '\033[0;31m%s\033[m' % str

def createOptionParser():
    """
    @return: C{OptionParser}
    Creates and returns OptionParser object suited for command line arguments processing.
    """
    parser = OptionParser()

    parser.add_option("-p", "--parsingModule", dest="parsingModule",
            action="store", help="Atlas parser for dedicated atlas", metavar="parsingModule")
    parser.add_option("-s", "--startpage", dest="startpage", action="store",
            help="First page of parsing sequence", metavar="page_number", type="int")
    parser.add_option("-e", "--endpage", dest="endpage", action="store",
            help="Last page of parsing sequence", metavar="page_number", type="int")
    parser.add_option("-o", "--outputAtlasDirecotry", dest="outputDir", action="store",
            help="Directory, where parsed file will be stored.", metavar="DIR")
    parser.add_option("-i", "--sourceDirecotry", dest="sourceDir", action="store",
            help="Directory, from which source data fill be read.", metavar="DIR")
    parser.add_option("--create-only-index-file", action="store_true", dest="only_index",
            default=False, help="Create only index file")
    return parser

def validateOptions(opts):
    """
    @type  opts: parsed OptionParsed object
    @param opts: Set of options extracted and parsed by OptionParser
    @return    : True when options set passes all validation rules, False otherwise.

    Validates provided options formally and logicaly.
    Detail of validation process are explained in comments.
    """

    # Check, if name of parsing module is correct:
    if opts.parsingModule == "":
        printRed("Pasing module defined incorrectly!")
        return False

    # Check, if the arguments are defined
    if opts.endpage<0 or opts.startpage<0 or opts.outputDir=="":
        printRed("Some arguments are not provided or has incorrect values.")
        return False

    # Check, if ending page is equal or greater than starting page
    if not opts.endpage>=opts.startpage:
        printRed("Endpage page should be greater or equal than startpage.")
        return False

    # Check, if provided output directory exists
    if not os.path.isdir(opts.outputDir):
        printRed("Provided directory is not a valid directory.")
        return False
    return True


if __name__=='__main__':
    # Create OptionParser object and parse provided command-line arguments.
    parser=createOptionParser()
    (options, args) = parser.parse_args()

    # Validate command line arguments
    # When arguments turns out invalid, print notification and quit script
    if not validateOptions(options):
        printRed("Invalid command line arguments. Please correct.")
        parser.print_help()
        exit(1)

    # Import atlas parsing module
    sys.path.append('bin/parsers')
    atlasparser = __import__(options.parsingModule, globals(), locals(), [], -1)

    # Define page range ('+1' is added due to pythonic way of indexing lists)
    pagesRange = range(options.startpage, options.endpage+1)
    ap = atlasparser.AtlasParser(options.sourceDir,  options.outputDir)

    #If only index should be created, od it and then exit the program:
    if options.only_index:
        printRed("Creating index file now.")
        ap.parseAll()
        exit(0)

    for slide in pagesRange:
        ap.parse(slide)
