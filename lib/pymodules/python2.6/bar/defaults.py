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
The module provides global regular expressions.

G{importgraph}
"""

import re

#{ Global regular expressions:
re_number='([0-9.-]+)'
""" 
Relavitely easy regexp for number should work in most cases.

More general regexp for anu kind of real number taken from 
http://books.google.pl/books?id=YEoiYr4H2A0C&printsec=frontcover&dq=Python+Scripting+for+Computational+Science
page 334. appears not to work correctly.

C{re_number=r'([+\-]?(\d+(\.\d*)?|\d*\.\d+)([eE][+\-]?\d+)?)'}
"""

re_trd={
'translate'  : re.compile(r'ranslate\('+re_number+','+re_number+'\)'),
'scalexy'    : re.compile(r'scale\('+re_number+','+re_number+'\)'),
'scalex'     : re.compile(r'scale\('+re_number+'\)'),
'matrix'     : re.compile(r'matrix\('+5*(re_number+' +')+re_number+'\)\s*')
}
""" Holds regular expressions for supproted transformations. """


# Because we have many types of paths we define regular expression
# for different types of paths
# TODO: Extend regular expression below so they could cover all types of path
#       unsupported: A as arch are not likely to be used.
# TODO: Some types of paths are clearly wrong parsed! It should be corrected
# XXX: Note that only absolute coordinates (capital letters in segments type) are supported
# TODO: Probably SVGpathparse module should be used here.
re_path=[
        re.compile(r'([MLQT])'+re_number+','+re_number),\
        re.compile(r'([HV])'+re_number),\
        re.compile(r'(SQ)'+re_number+','+re_number+','+re_number+','+re_number),\
        re.compile(r'(C)'+re_number+','+re_number+','+re_number+','+re_number+','+re_number+','+re_number),\
        re.compile(r'(Z)')
        ]
"""
List of regular expresions for supported types of paths:
    - M,L,Q,T
    - H,V
    - S,Q
    - C
    - Z
@attention: Unsupported path types: A
"""

re_PointsPair=re.compile(r''+re_number+','+re_number)
"""
Regexp for pair of points (comma separated, without whitespaces, bracketless: dd,dd)
"""

re_CoronalCoord=re.compile(r'Bregma:'+re_number)
re_CoordinateMarker=re.compile(r'\('+re_number+','+re_number+'\)')

re_fontsizepx=re.compile(r'([0-9]+)px')
""" Regexp for fontsize in pixels. """
#}
