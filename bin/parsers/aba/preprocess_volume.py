#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2011 Piotr Majka, Jakub M. Kowalski                   #
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
import sys

from nifti import *
import numpy as npy
import vtk

from math import sqrt
import random


"""
Note! To use this script ANTS (Advanced Normalization ToolS) package has to be
installed. Path for ImageMath binary file must be defined in $PATH environmental
variable.
"""

OUTPUT_VOLUME_ORIGIN  = (-5.575,-1.025,-5.325-2.525)
OUTPUT_VOLUME_SPACING = (0.025,0.025,0.025)
VOLUME_URI = 'http://community.brain-map.org/confluence/download/attachments/525267/data.zip?version=1'
VOLUME_DIMENSIONS = (528,320,456)
POI_TRANSFORM_POINTS_FNAME = 'aba-voxel_aba-ref_points.txt'

class Converter:
    
    def __init__(self):
        self.comment = None
        self.data = None
        self.size = None
    
    def __parseHeader(self, inputFile):
        s = inputFile.readline()
        arr = s.split(':');
        self.comment = arr[1];
        
        s=inputFile.readline()
        arr=s.split(':')
        arr=arr[1].split(',')
        self.size = map(int, arr)
    
    def __parseContent(self, inputFile):
        self.data = npy.zeros(self.size)
        for line in inputFile:
            (x,y,z,v) = map(int, line.split(','))
            self.data[x, y, z] = v
    
    def parseSVA(self, inputFile):
        print >>sys.stderr, 'Parsing file: %s...' % inputFile
        inputFile = open(inputFile, 'r')
        self.__parseHeader(inputFile)
        self.__parseContent(inputFile)
        inputFile.close()
    
    def saveRawData(self, outFile):
        print >>sys.stderr,'Saving Nifti image...'
        
        nim = NiftiImage(self.data)
        outputFileName = outFile
        nim.save(outputFileName)
    
    def __normalizeMatrix(self, M):
        print >>sys.stderr,'Applying transform...'
        
        A=npy.matrix(
            [
                [   1/abs(M[0,0]),  0,              0,                  0           ],
                [   0,              1/abs(M[1,1]),  0,                  0           ],
                [   0,              0,              abs(1/M[2,2]),      0           ],
                [   0,              0,              0,                              1           ]
            ])
        print 'M=\n',M
        
        return M*A
        
    def transformVolume(self, inputVolume, outputVolume, transformationMatrix):
        # Normalize matrix so it preserve its scaling (diagonal elements are
        # equal to 1)
        M = self.__normalizeMatrix(transformationMatrix)
        
        reader = vtk.vtkStructuredPointsReader()
        reader.SetFileName(inputVolume)
        reader.Update()
        reader.GetOutput().UpdateInformation()
        
        matrix = vtk.vtkMatrix4x4()
        matrix.DeepCopy((
            M[0,0], M[0,1], M[0,2], M[0,3],
            M[1,0], M[1,1], M[1,2], M[1,3],
            M[2,0], M[2,1], M[2,2], M[2,3],
            M[3,0], M[3,1], M[3,2], M[3,3]
            ))
        
        # Extract a slice in the desired orientation
        reslice = vtk.vtkImageReslice()
        reslice.SetInputConnection(reader.GetOutputPort())
        reslice.SetResliceAxes(matrix)
        reslice.AutoCropOutputOff()
        reslice.SetInterpolationModeToNearestNeighbor()
        #reslice.SetInterpolationModeToLinear()
        
        print >>sys.stderr,'M=\n',M
        ch = vtk.vtkImageChangeInformation()
        ch.SetInput(reslice.GetOutput())
        ch.SetOutputOrigin(*OUTPUT_VOLUME_ORIGIN)
        ch.SetOutputSpacing(*OUTPUT_VOLUME_SPACING)
        ch.Update() 
        
        writer = vtk.vtkStructuredPointsWriter()
        writer.SetFileTypeToBinary()
        writer.SetInput(ch.GetOutput())
        writer.SetFileName(outputVolume)
        writer.Update()

#======================================
class Gatherer:
    def __init__(self):
        self.data = npy.zeros(VOLUME_DIMENSIONS)
        self.points = {}
        
    def ext(self,f):
        arr=f.split('.')
        return arr[len(arr)-1]
    
    def setPoint(self, (x,y,z), val):
        self.data[x,y,z] = val
    
    def parseFile(self, fname):
        f = open(fname, 'r')
        print 'Collecting data from file %s...' % fname
        
        for line in f:
            arr = tuple(map(float, line.split('\t')))
            pointsCoords = tuple(map(lambda x: int(arr[x]),  (0,1,2)))
            voxelCoords  = tuple(map(lambda x: int(arr[x]),  (2,1,0)))
            spatialCoords= tuple(map(lambda x: float(arr[x]), (5,4,3)))
            self.setPoint(pointsCoords, 128)
            self.points[voxelCoords] = spatialCoords
        
        print '%d points found' % len(self.points)
    
    def gather(self, filename):
        self.parseFile(filename)
        print 'Done! Collected %d points' % len(self.points)
        
    def solve(self):
        k = self.points.keys()
        indices = tuple(range(4))
        P = tuple(map(lambda x: k[x], indices))
        PP= tuple(map(lambda x: self.points[x],P))
        V1=npy.ones((4,4))
        V1[0:3,0:4] = npy.array(P).transpose()
        V2=npy.ones((4,4))
        V2[0:3,0:4] = npy.array(PP).transpose()
        
        # Which is equal to:
        #A1=k[0]
        #B1=k[1]
        #C1=k[2]
        #D1=k[3]
        #A2=self.points[A1]
        #B2=self.points[B1]
        #C2=self.points[C1]
        #D2=self.points[D1]
        #V1=npy.array(
        #        [
        #            [   A1[0],  B1[0],  C1[0],  D1[0]   ],
        #            [   A1[1],  B1[1],  C1[1],  D1[1]   ],
        #            [   A1[2],  B1[2],  C1[2],  D1[2]   ],
        #            [   1,          1,          1,          1           ]
        #    ])
        #V2=npy.array(
        #        [
        #            [   A2[0],  B2[0],  C2[0],  D2[0]   ],
        #            [   A2[1],  B2[1],  C2[1],  D2[1]   ],
        #            [   A2[2],  B2[2],  C2[2],  D2[2]   ],
        #            [   1,          1,          1,          1           ]
        #        ])
        
        V1=npy.linalg.inv(npy.matrix(V1))
        V2=npy.matrix(V2)
        self.M=V2*V1
        print "M=\n",self.M
        #A = npy.matrix(V1[:,0].reshape((4,1)))
        #A=npy.matrix(
        #        [
        #            [   A1[0]   ],
        #            [   A1[1]   ],
        #            [   A1[2]   ],
        #            [   1           ]
        #        ])
        return self.M
    
    def diff(self, voxelCoords):
        try:
            A1=npy.ones((4,1))
            A1[0:3,:] = npy.array(voxelCoords).reshape((3,1))
            #A1=npy.matrix(
            #    [
            #        [   A[0]    ],
            #        [   A[1]    ],
            #        [   A[2]    ],
            #        [   1           ]
            #    ])
            spatialCoords = self.points[voxelCoords]
            B1=npy.ones((4,1))
            B1[0:3,:] = npy.array(spatialCoords).reshape((3,1))
            #B1=npy.matrix(
            #    [
            #        [   B[0]    ],
            #        [   B[1]    ],
            #        [   B[2]    ],
            #        [   1           ]
            #    ])
            B2=self.M*A1
            r = npy.linalg.norm(B2-B1)**2
            return r
        except:
            print 'Error'
            
    def sqsum(self):
        #k=self.points.keys()
        #l=len(k)
        #s=0.0
        #for point in self.points:
        #    s+=self.diff(point)
        s = sum(map(self.diff, self.points.iterkeys()))
        print >>sys.stderr, "Sum of differences", sqrt(s)
        return s

def preprocessVolume(outputDirectory, outputFilename):
    os.system('wget -O /tmp/data.zip %s'% VOLUME_URI)
    os.system('unzip -o  /tmp/data -d /tmp/') 
    abaPoiTransformPoints =\
       os.path.join(os.path.split(__file__)[0], POI_TRANSFORM_POINTS_FNAME)

    g=Gatherer()
    g.gather(abaPoiTransformPoints)
    g.solve()
    g.sqsum()
    conv = Converter()
    conv.parseSVA('/tmp/data/AtlasAnnotation25.sva')
    conv.saveRawData('/tmp/temp_AtlasAnnotation25.nii')
    os.system('ImageMath 3 /tmp/temp_AtlasAnnotation25.vtk + /tmp/temp_AtlasAnnotation25.nii 0')
    conv.transformVolume('/tmp/temp_AtlasAnnotation25.vtk', '/tmp/aba_atlas.vtk', g.M)
    os.system('rm -rfv /tmp/data.zip /tmp/data /tmp/temp_AtlasAnnotation25.vtk\
            /tmp/temp_AtlasAnnotation25.nii /tmp/temp_AtlasAnnotation25.vtk')
    os.system('ImageMath 3 %s + /tmp/aba_atlas.vtk 0'\
                % os.path.join(outputDirectory,outputFilename))
    print 'Done!'


if __name__ == '__main__':
    try:
        outputDirectory = sys.argv[1]
        outputFilename  = sys.argv[2]
    except:
        outputDirectory = 'atlases/aba/src/'
        outputFilename  = 'atlas.nii'
        
    preprocessVolume(outputDirectory, outputFilename)
