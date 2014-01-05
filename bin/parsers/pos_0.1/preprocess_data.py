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
Preprocessing file for the monodelphis domestica atpas parser.
As an input the script requires ITK snap labels descsription file with appropriately
embedded structures' hierarchy. The output of the file comprises the labels' fullname.txt file
as well as hierarchy file.
"""

import os, sys
import csv

def tuple_to_html_color_string(r, g, b):
    return '%02x%02x%02x' % (r, g, b)

if __name__ == "__main__":
    labels_description_file = sys.argv[1]
    output_fullname_file = sys.argv[2]
    output_parents_file = sys.argv[3]

    # The ITK snap file is loaded via the csv module.
    labels_descriptions  = open(labels_description_file, "rb")
    csv_reader = csv.reader(labels_descriptions, delimiter=' ', \
                            quotechar='"', quoting=csv.QUOTE_ALL)

    # Output arrays
    results_fullnames = []
    results_parents = []

    for row in csv_reader:
        # Throw away empty lines.
        row = filter(None, row)

        # Skip lines which are comments
        if row[0][0] != "#":
            label_id = int(row[0])

            # Skip 'empty label' row
            # and labels with indexes larger than 200
            # as they are not anatomical structures.
            if label_id == 0 or label_id >= 200:
                continue

            # Extract information about given structure
            # Assumptions on colums:
            # 0 - label id
            # 1,2,3 - r,g,b colors of the structure
            # 4,5,6 - not interesting,
            # 7 - string in format: fullname|abbrev|parent's abbrev
            print row
            r, g, b = tuple(map(int, row[1:4]))
            fullname = row[7].split("|")[0].replace('"', "")
            abbreviation = row[7].split("|")[1].replace('"', "")
            parent = row[7].split("|")[2].replace('"', "")

            # Get html colorstrings
            label_color_string =\
                tuple_to_html_color_string(label_id, label_id, label_id)
            structur_color_string =\
                tuple_to_html_color_string(r, g, b)

            # Append structure's properties to the output results array
            results_fullnames.append([label_color_string, abbreviation,\
                                      structur_color_string, fullname])

            results_parents.append([abbreviation,parent])

    # Dump the results
    writer = file(output_fullname_file, 'w')
    for line in results_fullnames:
        writer_string = "\t".join(map(str, line)) + "\n"
        writer.write(writer_string)

    writer = file(output_parents_file, 'w')
    for line in results_parents:
        writer_string = "\t".join(map(str, line)) + "\n"
        writer.write(writer_string)
