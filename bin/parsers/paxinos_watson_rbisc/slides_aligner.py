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

import os
import xml.dom.minidom as dom
from sys import *
from string import *
import numpy
import sys

"""
G{importgraph}
"""

class slideAligner():
    """
    Class for rescaling and aligning slides to given reference coordinate
    system by modyfying transformation matrix for topmost g element.
    
    Required input:
    
        1. SVG document to be modified,
        2. Reference scaling and offsets.
    
    Workflow:
    
        1. Get initial transformation matrix from SVG,
        2. Calculate corrections basing on initial transformation matrix and
           reference matrix.
        3. Embed corrections as SVG transformation and put corrected
           transformation matrix as 3dBAR metedata
    
    Output:
    
    SVG drawing with reference scaling and offsets.
    """
    def __init__(self, (xref, yref, sxref, syref), debugMode = True):
        """
        Class constructor. Requires set of reference scaling and offsets.
        
        @type   xref: float
        @param  xref: Reference x coordinate of reference coordinate system
                      origin ( x coordinate (in mm) of point (0,0) in image
                      coordiantes).
        @type   yref: float
        @param  yref: y coordinate (in mm) of point (0,0) in image coordinates.
        @type  sxref: float
        @param sxref: Reference scaling in x direction. Increasing by one pixel
                      in image coordinates means increasing by sxref in
                      stereotaxic coordinates.
        @type  syref: float
        @param syref: Reference scaling in y direction. Increasing by one pixel
                      along image y coorginate means increasing by syref in
                      stereotaxic coordinates.
        @type  debugMode: boolean
        @param debugMode: If C{True} full debug information would be printed.
                          C{False} by default.
        @return: None
        
        Please note that scaling can be either positive and negative. When
        scaling is positive it means that stereotaxic axis has the same
        direction as image axis. When scaling is negative stereotaxic and image
        axes are oriented in opposite directions. Be very careful in sych case.
        """
        self.xref  = xref
        self.yref  = yref
        self.sxref = sxref
        self.syref = syref
        
        # Set debug mode:
        self.debugMode = debugMode
    
    def getAlignmentTuple(self):
        """
        Returns tuple of aligning parameters (the same tuple which was passed to
        the constructor)
         
        @return: tuple (xref, yref, sxref, syref)
        """
        return (self.xref, self.yref, self.sxref, self.syref) 

    def makeAlignment(self, svgdom):
        """
        Function that manages aligning process. Should be invoked from outside
        the class with SVG document as an argument. Modifies C{svgdom} only.

        @type  svgdom: DOM object
        @param svgdom: DOM model of SVG drawing
        @return: True, if changes were applied correctly. False, if changes were
                 not applied.
        """
        if self.debugMode:
            print >>sys.stderr, "\t\tSlideAligner:"
            print >>sys.stderr, "\t\t\tStarting aligning"

        M  = self.getTransformationMatrix(svgdom)
        Mc = self.calculateAlignmentMatrix(M)

        # Check, if extracted transformation matrix is the same as reference
        # matrix. It if is, there is no sense to apply corrections and function
        # should exit and return false:
        if numpy.alltrue(numpy.around(Mc, decimals=4) - numpy.eye(3) == 0.):
            return False

        self._applyTransformCorrection(list(Mc), svgdom)
        
        if self.debugMode:
            print >>sys.stderr, "Initial transformation matrix M:"
            print >>sys.stderr, M
            print >>sys.stderr, "Matrix of correction coefficient Mcorr:"
            print >>sys.stderr, Mc
            print >>sys.stderr, "\t\t\tFinished aligning"

        return True

    def getTransformationMatrix(self, svgdom):
        """
        Extracts stereotaxic coordinate matrix from given SVG drawing metadata.
        It is assumed that in whole file there is only one tag named
        C{drba_transformationmatrix} and it has C{content} attribute in which
        matrix is stored as a tuple of four, float, comma-separated, values::

            \\mathbf{M}_c= \\begin{pmatrix}
            s_x   &  0    &  t_x \\\\ 
             0    &  s_y  &  t_y \\\\ 
             0    &  0    &  1
            \end{pmatrix}

            http://latex.codecogs.com/gif.latex?M=\\begin{pmatrix}&space;s_x&space;&&space;0&space;&&space;t_x&space;\\\\&space;0&space;&&space;s_y&space;&&space;t_y&space;\\\\&space;0&space;&&space;0&space;&&space;1&space;\\end{pmatrix}

        @type  svgdom: DOM object
        @param svgdom: DOM model of SVG drawing

        @return: Matrix C{M} as NumPy matrix
        """
        for element in svgdom.getElementsByTagName('bar:data'):
            print element.toxml()
            if element.getAttribute('name') == 'transformationmatrix':
                transfArr = element.getAttribute('content')
                self.InitialTransformationMatrix = map(float, split(transfArr,','))
                t = self.InitialTransformationMatrix # Just convinient alias
                return numpy.matrix([[ t[0], 0., t[1] ], [ 0., t[2], t[3] ], [ 0., 0., 1.]])

    def calculateAlignmentMatrix(self, M):
        """
        Calculates corretions for SVG drawing. Correction includes both: scaling
        and translation:
        
            1. C{cx, cy}: corrections in x and y directions.
            2. C{csx, csy}: scalings in x and y direction.
        
        And few remarks (just to remain clear):
        Multiplication vector x by matrix M means going from image coordinate
        system to stereotaxic coordinate system.
        
        Multiplication stereotaxic vector y by M^{-1} means switching from
        stereotaxic coordiante system to image coortdiante system.
        
        Calcucating M{-1}.(Mcorr.M) means:
            1. Transform matrix M by matrix Mcorr (we are still in stereotaxic
               coordinates).
            2. Transform result to image coordinates.
        We use multiplication by inverted M because image is still in
        untransformed coordinate system.
        
        Corrections are calculated in following way::
        
            \\begin{matrix}
            c_x     & = & t_x - t_{x_{ref}} \\\\
            c_y     & = & t_y - t_{y_{ref}} \\\\
            c_{s_x} & = & \\frac{s_{x_{ref}}}{s_x}\\\\
            c_{s_y} & = & \\frac{s_{y_{ref}}}{s_y}\\\\
            \\end{matrix}\\right.
        
        And then C{Mc} matrix is created::
        
            \\mathbf{M}_c=
            \\begin{pmatrix}
            \\frac{s_{x_{ref}}}{s_x} &           0               &  t_x - t_{x_{ref}} \\\\
            0                        &  \\frac{s_{y_{ref}}}{s_y} &  t_y - t_{y_{ref}} \\\\
            0                        &           0               &  1
            \\end{pmatrix}
        
        The final correction is calculated using following formula::
        
            \\begin{pmatrix}
            \\frac{s_{x_{ref}}}{s_x}       & 0                          &            \\frac{s_{x_{ref}} t_x - s_x t_{x_{ref}}}{{s_x}^{2}} \\\\
            0                              & \\frac{s_{y_{ref}}}{s_y}   &            \\frac{s_{y_{ref}}t_y - s_y t_{y_{ref}}}{{s_y}^{2}}\\\\
            0                              & 0                          & 1
            \end{pmatrix}
        
        @type  M: 3x3 numpy array
        @param M: Transformation matrix extracted from SVG drawing by
                  L{getTransformationMatrix<getTransformationMatrix>} method.
        @return: 3x3 numpy array C{C} defined below
        """
        
        cx= ( +M[0,2] - self.xref )
        cy= ( +M[1,2] - self.yref )

        csx = self.sxref / M[0,0]
        csy = self.syref / M[1,1]

        # Calculate corrections
        Mc=numpy.matrix([[ csx, 0., cx ], [ 0, csy, cy ],  [ 0., 0., 1.]])

        # Calculate alignment matrix
        # We need to round the numbers because otherwise they would be presented
        # in scientific notation.
        C=(M.I*Mc*M).round(15)

        if self.debugMode:
            print >>stderr, "\t\tApplying correction"
            print >>stderr, "Initial transformation matrix M (stereotaxic coords.):"
            print >>stderr, M
            print >>stderr, "Matrix of correction coefficients Mc (stereotaxic coords.):"
            print >>stderr, Mc
            print >>stderr, "Final alignment matrix C (image coords.):"
            print >>stderr, C

        return C

    def _applyTransformCorrection(self, TransformCorrection, svgdom):
        """
        Applies alignmetnt calculated by
        L{calculateAlignmentMatrix<calculateAlignmentMatrix>} function and
        updates SVG 3dBAR metedata element:

            1. Put reference scaling and offets as 3dBAR transformation matrix
            2. Transform topmost element by C{TransformCorrection} matrix.

        @type  svgdom: DOM object
        @param svgdom: DOM model of SVG drawing

        @type  TransformCorrection: 3x3 numpy array
        @param TransformCorrection: Matrix with alignment correction

        @return:None
        """
        tc=TransformCorrection # Alias

        # Get topmost (it is also assumed that is is the only g element in SVG
        # document)
        mainGroupElement=svgdom.getElementsByTagName('g')[0]

        # Correct praviously extracted group element by C{TransformCorrection}
        # Short fragment from SVG reference regarding matrix transformation:
        # [a b c d e f] = [sx, 0, 0, sy, tx, ty]
        correctedTransformation=\
                "matrix(%f, 0, 0, %f, %f, %f)" % (tc[0][0], tc[1][1], tc[0][2], tc[1][2] )
        mainGroupElement.setAttribute('transform', correctedTransformation)

        # Put reference scaling and offset as stereotaxic transformation matrix
        # (sx, tx), (sy, ty)
        correctedTranfromationArray=\
                "%5.10f, %5.10f, %5.10f, %5.10f" % (self.sxref, self.xref, self.syref, self.yref )
        
        for element in svgdom.getElementsByTagName('bar:data'):
            if element.getAttribute('name') == 'transformationmatrix':
                element.setAttribute('content', correctedTranfromationArray)

if __name__=='__main__':
    pass
