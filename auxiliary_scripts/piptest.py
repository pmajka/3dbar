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

import subprocess
import sys,os
from bar.rec import pipeline

GRAPH_HEAD="""digraph G {
    fontname = "Bitstream Vera Sans"
    fontsize = 8
    
    node [
        fontname = "Bitstream Vera Sans"
        fontsize = 8
        shape = "record"
    ]
    
    edge [
        fontname = "Bitstream Vera Sans"
        fontsize = 8
    ]
"""
GRAPH_FOOT="""}"""

NODE_HEAD=""
NODE_FOOT="]\n\n"

class graph(object):
    def  __init__(self, pipe):
        self.pipeline = pipe
        
        self.connections = []
        self.nodes = filter(lambda x: x.on, self.pipeline.elements)
        
        self.addEdges()
    
    def __str__(self):
        retval = GRAPH_HEAD+\
                 self.__processPipeline()+\
                 "".join(map(str, self.connections))+\
                 GRAPH_FOOT
        return retval
    
    def __processPipeline(self):
        retval = ""
        for el in self.nodes:
            retval += str(node(el))
        return retval
    
    def addEdges(self):
        for i in range(len(self.nodes)-1):
            conn = edge(self.nodes[i], self.nodes[i+1])
            self.connections.append(conn)

class node(object):
    def __init__(self, filter):
        self.filter = filter
    
    def __processFilter(self):
        retval = self.filter.vtkclass + ' [\n'
        retval+= 'label = "{ '
        retval+= self.filter.vtkclass+'| '
        if self.filter.desc:
            desc = self.filter.desc.replace("\n"," ")
            retval+= '('+desc+')|'
        for p in self.filter.params:
            retval+= p.name+':'
            if p.args:
                retval+= ",".join(map(str,p.args))+'\l'
        retval +='}"'
        return retval
    
    def __str__(self):
        return NODE_HEAD + self.__processFilter() + NODE_FOOT

class edge(object):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
    
    def __str__(self):
        return self.src.vtkclass + " -> " + self.dst.vtkclass+'\n'

def plotGraph(pipeline, output_filename):
    gr = graph(pipeline)
    popen = subprocess.Popen(['dot', '-T', 'png', '-o', output_filename],
                             stdin=subprocess.PIPE)
    popen.communicate(str(gr))
    popen.stdin.close()
    popen.wait()
    

if __name__ == '__main__':
    plotGraph(pipeline.barPipeline.fromXML(sys.argv[1]),
              sys.argv[2])
