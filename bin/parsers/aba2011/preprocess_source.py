#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2011 Piotr Majka, Lukasz Walejko, Jakub M. Kowalski   #
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
Purpose of the script below is to prepare input data for the Allen Brain Atlas
2011 volumetric dataset. Two partial datasets are processed.  The first one is
the labelled volume containing volume element to structure's name assignment. This
volume is provided by Allen Institute in form of raw binary file and one needs
to figure out what are the voxel dimensions and volume origin.  Volume is
processed by L{preprocessVolume} function.

The second dataset is the ontology containing:
    1) Structure's abbreviated name
    2) Strucutre's parent abbreviated name
    3) Full name of the structure
    4) Ontlogy id (I don't know where the full ontology is provided)
    5) Structure's index as provided in the labelled volume
    6) RGB color arrigned to the particular structure (note the colour may be no uniqe)
"""

import os, sys, csv

import nifti
import numpy
from data import HIERARCHY_FILANEME, MAPPING_FILENAME, ATLAS_FILENAME

# Origin and spacing of the labelled volume.  Note that origin and spacing are
# not provided within the volume thus they have to be provided separately.
OUTPUT_VOLUME_ORIGIN  = (0, 0, 0)
OUTPUT_VOLUME_SPACING = (0.025, 0.025, 0.025)

# Provide the address from which the dataset can be obtained.
VOLUME_URI = 'http://www.brain-map.org/BrainExplorer2/Atlases/Mouse_Brain_2.zip'
ANNOTATION_PATH = 'Spaces/P56/Annotation'
ONTOLOGY_FILENAME = 'ontology.csv'
VOLUME_DIMENSIONS = (456,320,528)

def preprocessVolume(outputDirectory, outputFilename):
    """
    Process the raw input volume into niftii labelled volume with full
    information about coordinate system.
    
    @type  outputDirectory: str
    @param outputDirectory: Directory containing source dataset.
     
    @type  outputFilename: str
    @param outputFilename: Name of the output volume
    
    @return: None
    """
    
    # Load labelled volume from the raw binary file using numpy. The values are
    # stored as unsigned short integers one after another. After loading all
    # values, resulting array is reshaped to match the atlas volume shape.
    annotationVolumeFilename = os.path.join(outputDirectory, ANNOTATION_PATH) 
    fd = open(annotationVolumeFilename, 'rb')
    read_data = numpy.fromfile(file=fd, dtype=numpy.uint16).reshape(VOLUME_DIMENSIONS)
    
    # We are trying to reorient the volume into TODO: RAI orientation,
    # hope that's correct.
    read_data = numpy.transpose(read_data, (1,2,0))
    read_data = read_data[::-1,:,:]
    
    # Prepare nifti volume from numpy array. Create proper header and store all
    # of them into target volume file.
    annotatedVolume = nifti.NiftiImage(read_data)
    annotatedVolume.setVoxDims(OUTPUT_VOLUME_SPACING)
    annotatedVolumeHeader = annotatedVolume.header
    annotatedVolumeHeader['qoffset'] = OUTPUT_VOLUME_ORIGIN
    annotatedVolumeHeader['qform_code'] = 1
    annotatedVolume.header = annotatedVolumeHeader
    outputPath = os.path.join(outputDirectory, outputFilename)
    annotatedVolume.save(outputPath)

def _RGBToHTMLColor(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def cleanStructName(structName):
    """
    Provided acronyms are usually fine but sometimes they are not compatibile
    with 3dBar naming convention. Here we process them so they can pass 3dBAR
    name validataion.
    
    @type  structName: C{str}
    @param structName: initial sturcture name, potentially invalid
    
    @rtype: C{str}
    @return: structure name transformed in the way that passes 3dBAR name validation
    
    @todo: this function should be a part of the base.py module
    """
    # transform name into its valid form by replacing '(',')', '$', '/',
    # "'", '+', ' ' characters with their names and stripping hypens
    # from beginning and end of the string
    replaceMap = [('(', 'OpParen'),
                  (')', 'ClParen'),
                  (',', '-'),
                  ('$', 'Dollar'),
                  ('/', 'Slash'),
                  ('\\', 'Backslash'),
                  ('+', 'Plus'),
                  (' ', '-'),
                  ('\'', 'Prime')]
    
    return reduce(lambda x, (y, z): x.replace(y, z),
                  replaceMap,
                  structName).strip('- ')

def __processSingleOntologyFileLine(ontologyLine):
    """
    Helper function for processing sungle ontology file line. A single line with
    ontology records contains following elements:
        - Fullname, abbreviation, parent, assigned color, volume index,
          ontologyID
    
    @type  ontologyLine: str
    @param ontologyLine: tab separatd line containing data with single ontology
                         record.
    
    @rtype: (str, str)
    @return: Strings that could be appended to ontology and hierarchy string.
    """
    
    # Extract data from provided string.
    abbreviation = cleanStructName(ontologyLine[1])
    parent = cleanStructName(ontologyLine[2])
    fullname = ontologyLine[0]
    ontologyId = ontologyLine[7]
    structureIdx = ontologyLine[6]
    
    # Convert color components into html color string.
    rgbTuple = tuple(map(lambda x: int(ontologyLine[x]), [3,4,5]))
    htmlColour = _RGBToHTMLColor(rgbTuple)[1:]
    
    toOntStringData = [abbreviation, fullname, htmlColour, ontologyId, structureIdx]
    toParentsData = [abbreviation, parent]
    
    # From final string that will be returned.
    toOntStringData = "\t".join(map(str, toOntStringData)) + "\n"
    if parent == "":
        toParentsData=""
    else:
        toParentsData = "\t".join(map(str, toParentsData)) + "\n"
    
    return toOntStringData, toParentsData

def preprocessOntology(outputDirectory):
    """
    Extract and process structure ontology information from source dataset. 
    
    @type  outputDirectory: str
    @param outputDirectory: directory containig source dataset
    
    @return: None
    """
    
    # String that will hold contents of the ontology file.
    ontologyString = ""
    
    # String that will hold contents of the structure's hierarchy file.
    parentsString = ""
    
    # Load the ontology file using csv reader.
    ontologyFilename = os.path.join(outputDirectory, ONTOLOGY_FILENAME)
    csvReader = csv.reader(open(ontologyFilename, 'r'), delimiter=',', quotechar='"')
    
    # Read line by line from ontology file and extract information about
    # the structures.
    for ontologyLine in csvReader:
        toOntStringData, toParentsData =\
            hstr, ontstr = __processSingleOntologyFileLine(ontologyLine)
        ontologyString += hstr
        parentsString  += ontstr
    
    # Create files with processed ontology data as well as hierarchy data.
    hierarchyFile = os.path.join(outputDirectory, HIERARCHY_FILANEME)
    mappingFile   = os.path.join(outputDirectory, MAPPING_FILENAME)
    
    open(hierarchyFile,'w').write(parentsString)
    open(mappingFile,'w').write(ontologyString)


if __name__ == '__main__':
    try:
        outputDirectory = sys.argv[1]
        outputFilename  = sys.argv[2]
    except:
        outputDirectory = 'atlases/aba2011/src/'
        outputFilename  = ATLAS_FILENAME
    
    preprocessVolume(outputDirectory, outputFilename)
    preprocessOntology(outputDirectory)
