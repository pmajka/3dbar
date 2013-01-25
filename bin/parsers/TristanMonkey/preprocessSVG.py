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
            tag = node.tagName.lower()
            if tag == 'g':
                if not cleanSVG(node, doc,
                                gVisible = gVisible or node.hasAttribute('stroke')):
                    root.removeChild(node)
                    node.unlink()
                    continue

                visible = True

            elif tag == 'text':
                text = reapTEXT(node)
                if text.strip() != '':
                    visible = True
                    node.appendChild(doc.createTextNode(text))

                else:
                    root.removeChild(node)
                    node.unlink()
                    continue

            elif node.hasAttribute('stroke'):
                h, s, v = barColor.fromHTML(node.getAttribute('stroke')).hsv
                # remove too dark elements - 0.4 shall be finne
                if v < .35 or v > .9 and s < 0.1\
                      or node.hasAttribute('fill')\
                      and node.getAttribute('fill').lower() != 'none':
                    root.removeChild(node)
                    node.unlink()
                    continue

                # remove bregma plane indicator
                elif tag == 'line' and .52 < h and h < .54\
                  and .82 < s and s < .84 and .83 < v and v < .84 and\
                  all(node.hasAttribute(a) for a in ['x1', 'x2', 'y1', 'y2']):
                    x1 = float(node.getAttribute('x1'))
                    x2 = float(node.getAttribute('x2'))
                    y1 = float(node.getAttribute('y1'))
                    y2 = float(node.getAttribute('y2'))
                    dy = y2 - y1
                    if x1 == x2 and x1 > 360 and dy > 100 and dy < 102:
                        root.removeChild(node)
                        node.unlink()
                        continue

                visible = True

            elif node.hasAttribute('fill'):
                if node.getAttribute('fill').lower() == 'none'\
                   or barColor.fromHTML(node.getAttribute('fill')).hsv[2] > 0.9:
                    root.removeChild(node)
                    node.unlink()
                    continue

                visible = True

            elif gVisible: #there is something left that can be visible if group is visible
                visible = True

            if node.hasAttribute('opacity'):
                node.removeAttribute('opacity')

            #if tag == 'line' and all(node.hasAttribute(a) for a in ['stroke',
            #                                                       'x1', 'x2',
            #                                                       'y1', 'y2',
            #                                                       'stroke-dasharray']):
            #    col = barColor.fromHTML(node.getAttribute('stroke'))
            #    x1 = float(node.getAttribute('x1'))
            #    x2 = float(node.getAttribute('x2'))
            #    y1 = float(node.getAttribute('y1'))
            #    y2 = float(node.getAttribute('y2'))
            #    dy = y2 - y1
            #    dx = x2 - x1

            #    # recognize grid line
            #    if (dx == 0 and dy > 400 or dy == 0 and dx > 500)\
            #       and all(.39 < x and x < .404 for x in col()):
            #        node.setAttribute('stroke', '#00FF00')
            #        node.setAttribute('stroke-width', '10')


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

    x1X = float('inf')
    x2X = x1X
    yX = x1X
    xY = x1X
    y1Y = x1X
    y2Y = x1X
#    xTics = []
#    yTics = []
    grid = []
    top = ''
    topR = x1X
    left = ''
    leftR = x1X
    for line in slide.getElementsByTagName('line'):
        if all(line.hasAttribute(a) for a in ['stroke', 'x1', 'x2',
                                              'y1', 'y2', 'stroke-dasharray']):
            col = barColor.fromHTML(line.getAttribute('stroke'))
            x1 = float(line.getAttribute('x1'))
            x2 = float(line.getAttribute('x2'))
            y1 = float(line.getAttribute('y1'))
            y2 = float(line.getAttribute('y2'))
            dy = y2 - y1
            dx = x2 - x1
            if all(.39 < x and x < .404 for x in col()):
                if dx == 0 and dy > 400: # Y grid
                    grid.append(line)
#                    xTics.append(x1)
                    if x1 < xY: # find the lefttest line
                         y1Y = y1
                         y2Y = y2
                         xY = x1


                elif dy == 0 and dx > 500: # X grid
                    grid.append(line)
#                    yTics.append(y1)
                    if y1 < yX: # find the toppest line
                        yX = y1
                        x1X = x1
                        x2X = x2

#                else:
#                    line.setAttribute('stroke', '#00FF00')
#                    line.setAttribute('stroke-width', '10')
#
#            else:
#                line.setAttribute('stroke', '#FF0000')
#                line.setAttribute('stroke-width', '10')

    # remove grid
    #for node in grid:
    #    parent = node.parentNode
    #    parent.removeChild(node)
    #    node.unlink()

    #grid = []

    for text in slide.getElementsByTagName('text'):
        if text.hasAttribute('x') and text.hasAttribute('y'):
            x = float(text.getAttribute('x'))
            y = float(text.getAttribute('y'))
            r = (x - xY) ** 2 + (y - y1Y) ** 2
            if r < leftR: #find text closest to begining of lefttest Y grid line
                leftR = r
                left = u''.join(t.data for t in text.childNodes if t.nodeType == t.TEXT_NODE) #XXX ???

            r = (x - x1X) ** 2 + (y - yX) ** 2
            if r < topR: #find text closest to begining of toppest X grid line
                topR = r
                top = u''.join(t.data for t in text.childNodes if t.nodeType == t.TEXT_NODE) #XXX ???

            if x < x1X or x > x2X - 11 or y < y1Y + 6 or y > y2Y and y < y2Y + 2:
                grid.append(text)

    # remove grid
    for node in grid:
    #    node.setAttribute('stroke', '#FF8800')
        parent = node.parentNode
        parent.removeChild(node)
        node.unlink()

    return ((xY, int(left)), (yX, int(top)))
                

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
            slideNodes.append(node)

        else:
            node.unlink()

    for i, node in enumerate(slideNodes):
        (left, labelLeft), (top, labelTop) = cleanSlide(node)
        nId = node.getAttribute('id').split('_')
        bregma = float(nId[2]) * (-1 if nId[1] == 'x2D' else 1)
        # id == '_x2D_' + bregma [+ '_' + ...]
        print "slide %d (bregma %f, Y axis labeled %d at %fpx, X axis labeled %d at%fpx)" % (i, bregma, labelTop, top, labelLeft, left)
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
