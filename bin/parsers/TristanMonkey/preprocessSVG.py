#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2013 Piotr Majka, Jakub M. Kowalski                   #
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
import sys
import xml.dom as dom
import xml.dom.minidom

from bar.svgfix import fixSvgImage
from bar.color import barColor

def reapTEXT(root):
    result = u''
    for node in list(root.childNodes):
        if node.nodeType == node.TEXT_NODE:
            result += node.nodeValue # strip?

        elif node.nodeType == node.ELEMENT_NODE:
            result += reapTEXT(node)

        else:
            print node.nodeType

        root.removeChild(node)
        node.unlink()

    return result

def cleanSVG(root, doc, gVisible = False):
    visible = False
    for node in list(root.childNodes):
        if node.nodeType == node.ELEMENT_NODE:
            if node.tagName.lower() == 'g':
                if cleanSVG(node, doc, gVisible = gVisible or node.hasAttribute('stroke')):
                    visible = True

                else:
                    root.removeChild(node)
                    node.unlink()
                    

            elif node.tagName.lower() == 'text':
                text = reapTEXT(node)
                if text.strip() != '':
                    visible = True
                    node.appendChild(doc.createTextNode(text))

                else:
                    root.removeChild(node)
                    node.unlink()


            elif node.hasAttribute('stroke'):
                if barColor.fromHTML(node.getAttribute('stroke')).hsv[2] < .35\
                   or node.hasAttribute('fill')\
                      and node.getAttribute('fill').lower() != 'none':#0.4 shall be finne
                    root.removeChild(node)
                    node.unlink()

                else:
                    visible = True

            elif node.hasAttribute('fill'):
                if node.getAttribute('fill').lower() == 'none'\
                   or barColor.fromHTML(node.getAttribute('fill')).hsv[2] > 0.9:
                    root.removeChild(node)
                    node.unlink()

                else:
                    visible = True

            elif gVisible: #there is something left that can be visible if group is visible
                visible = True

        elif node.nodeType == node.TEXT_NODE: #remove empty text nodes
            if node.nodeValue.strip() == '':
                root.removeChild(node)
                node.unlink()

            else:
                visible = True

    return visible


def textOnlyGroup(root):
    for node in list(root.childNodes):
        if node.nodeType != node.ELEMENT_NODE:
            continue

        tag = node.tagName.lower()
        if tag == 'text':
            continue

        if tag == 'g' and textOnlyGroup(node):
            continue

        return False

    return True


def cleanSlide(slide):
    for node in list(slide.childNodes):
        if node.nodeType == node.ELEMENT_NODE \
           and node.tagName.lower() == 'g'\
           and textOnlyGroup(node):
            slide.removeChild(node)
            node.unlink()
            #node.setAttribute('stroke', '#FF0000')

    return slide
                

def parseSVG(srcFilename, dstPattern):
    srcFh = open(srcFilename)
    slideTemplate = xml.dom.minidom.parse(srcFh)
    srcFh.close()

    svgNode = slideTemplate.getElementsByTagName('svg')[0]
    cleanSVG(svgNode, slideTemplate)
    fixSvgImage(slideTemplate, fixHeader=False)
    slideNodes = []
    for node in list(svgNode.childNodes): # maybe make a copy of childNodes???
        svgNode.removeChild(node)

        if node.nodeType == node.ELEMENT_NODE and node.tagName.lower() == 'g':
            slideNodes.append(cleanSlide(node))

        else:
            node.unlink()

    for i, node in enumerate(slideNodes):
        fName = dstPattern % i
        fh = open(fName, 'w')
        print 'writing %s' % fName
        svgNode.appendChild(node)
        # there is an unicode encoding bug in writexml -_-
        #slideTemplate.writexml(fh, addindent=' ', newl='\n', encoding='utf-8')
        fh.write(slideTemplate.toprettyxml(indent=" ", newl="\n", encoding='utf-8'))
        fh.close()
        svgNode.removeChild(node)


if __name__=='__main__':
    if len(sys.argv) != 3:
        print "USAGE: %s <source filename> <output filename pattern>" % sys.argv[0]
        sys.exit(1)

    parseSVG(sys.argv[1], sys.argv[2])
