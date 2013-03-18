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
                text = reapTEXT(node).strip()
                if text not in ('', '+', '-', 'vBrain'):
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
                    if x1 == x2 and x1 > 360 and dy > 100 and dy < 103:
                        root.removeChild(node)
                        node.unlink()
                        continue

                visible = True

            elif node.hasAttribute('fill'):
                fill = node.getAttribute('fill').lower()
                if fill == 'none':
                    root.removeChild(node)
                    node.unlink()
                    continue

                col = barColor.fromHTML(fill)

                if .13 < col.r and col.r < .14 and .12 < col.g\
                   and col.g < .125 and .12 < col.b and col.b < .129\
                   or col.hsv[2] > 0.9:
                    root.removeChild(node)
                    node.unlink()
                    continue

                visible = True

            elif gVisible: #there is something left that can be visible if group is visible
                visible = True

            if node.hasAttribute('opacity'):
                node.removeAttribute('opacity')

            if node.hasAttribute('stroke-dasharray'):
                node.removeAttribute('stroke-dasharray')

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


def cleanSlide(slide, doc):
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
    xX_ = -x1X
    yX_ = -x1X
    xY_ = -x1X
    yY_ = -x1X
    xTics = []
    yTics = []
    grid = []
    top = None
    topR = x1X
    left = None
    leftR = x1X
    bottom = None
    bottomR = x1X
    right = None
    rightR = x1X
    for line in slide.getElementsByTagName('line'):
        if all(line.hasAttribute(a) for a in ['stroke', 'x1', 'x2',
                                              'y1', 'y2']):
            col = barColor.fromHTML(line.getAttribute('stroke'))
            x1 = float(line.getAttribute('x1'))
            x2 = float(line.getAttribute('x2'))
            y1 = float(line.getAttribute('y1'))
            y2 = float(line.getAttribute('y2'))
            dy = y2 - y1
            dx = x2 - x1
            if all(.39 < x and x < .404 for x in col()):
                grid.append(line)

                if dx == 0 and dy > 400: # Y grid
                    xTics.append(x1)
                    if x1 < xY: # find the lefttest line
                        y1Y = y1
                        y2Y = y2
                        xY = x1

                    if x1 > xY_: # find the rightest line
                        xY_ = x1
                        yY_ = y1


                elif dy == 0 and dx > 500: # X grid
                    yTics.append(y1)
                    if y1 < yX: # find the toppest line
                        yX = y1
                        x1X = x1
                        x2X = x2

                    if y1 > yX_: # find the bottomest line
                        yX_ = y1
                        xX_ = x1

    # filter grid line tics (OMG... why there are unnumbered grid lines???)
    xTics = [x for x in xTics if x1X < x and x < x2X]
    yTics = [y for y in yTics if y1Y < y and y < y2Y]
    xY = min(xTics)
    xY_ = max(xTics)
    yX = min(yTics)
    yX_ = max(yTics)


    for text in slide.getElementsByTagName('text'):
        if text.hasAttribute('x') and text.hasAttribute('y'):
            x = float(text.getAttribute('x'))
            y = float(text.getAttribute('y'))
            
            r = None

            if y < y1Y + 6:
                #find text closest to the begining of the lefttest Y grid line
                r = (x - xY) ** 2 + (y - y1Y) ** 2
                if r < leftR:
                    leftR = r
                    left = u''.join(t.data for t in text.childNodes\
                                    if t.nodeType == t.TEXT_NODE)

                #find text closest to the begining of the righttest Y grid line
                r = (x - xY_) ** 2 + (y - yY_) ** 2
                if r < rightR:
                    rightR = r
                    right = u''.join(t.data for t in text.childNodes\
                                     if t.nodeType == t.TEXT_NODE)

            if x < x1X:
                #find text closest to the begining of the toppest X grid line
                r = (x - x1X) ** 2 + (y - yX) ** 2
                if r < topR:
                    topR = r
                    top = u''.join(t.data for t in text.childNodes\
                                   if t.nodeType == t.TEXT_NODE)

                #find text closest to the begining of the bottomest X grid line
                r = (x - xX_) ** 2 + (y - yX_) ** 2
                if r < bottomR:
                    bottomR = r
                    bottom = u''.join(t.data for t in text.childNodes\
                                      if t.nodeType == t.TEXT_NODE)

            #if x < x1X or x > x2X - 11 or y < y1Y + 6 or y > y2Y and y < y2Y + 12:
            if r != None or x > x2X - 11 or y > y2Y and y < y2Y + 12:
                grid.append(text)

    # remove grid
    for node in grid:
        parent = node.parentNode
        parent.removeChild(node)
        node.unlink()

    left = float(left)
    right = float(right)
    top = float(top)
    bottom = float(bottom)
    # left = a * xY + b; right = a * xY_ + b
    a = (left - right) / (xY - xY_)
    b = left - a * xY
    # top = c * yX + d; bottom = c * yX_ + d
    c = (top - bottom) / (yX - yX_)
    d = top - c * yX
    ## xY = a * left + b; xY_ = a * right + b
    #a = (xY - xY_) / (left - right)
    #b = xY - a * left
    ## yX = c * top + d; yX_ = c * bottom + d
    #c = (yX - yX_) / (top - bottom)
    #d = yX - c * top
    #print left, right, top, left
    #print xY, xY_, yX, yX_
    return a, b, c, d
                

tags = {}

def getTags(root, slide):
    if root.nodeType == root.ELEMENT_NODE:
        tag = root.tagName.lower()
        slides = tags.get(tag, set())
        slides.add(slide)
        tags[tag] = slides
        for node in root.childNodes:
            getTags(node, slide)


def parseSVG(srcFilename, dstPattern):
    srcFh = open(srcFilename)
    slideTemplate = xml.dom.minidom.parse(srcFh)
    srcFh.close()

    for tag in ['rect', 'defs', 'use', 'polygon']:
        for node in slideTemplate.getElementsByTagName(tag):
            parent = node.parentNode
            parent.removeChild(node)
            node.unlink()

    for node in slideTemplate.getElementsByTagNameNS('http://www.w3.org/2000/svg',
                                                     'clipPath'):
        parent = node.parentNode
        parent.removeChild(node)
        node.unlink()

    svgNode = slideTemplate.getElementsByTagName('svg')[0]

    cleanSVG(svgNode, slideTemplate)
    fixSvgImage(slideTemplate, fixHeader=False)
    slideNodes = []
    for node in list(svgNode.childNodes):
        svgNode.removeChild(node)

        if node.nodeType == node.ELEMENT_NODE and node.tagName.lower() == 'g':
            slideNodes.append(node)

        else:
            node.unlink()

    slideNodes.reverse() # now in rostral-caudal order

    metadata = slideTemplate.createElement('defs')
    transformationNode = slideTemplate.createElement('bar:data')
    transformationNode.setAttribute('name', 'transformationmatrix')
    metadata.appendChild(transformationNode)

    bregmaNode = slideTemplate.createElement('bar:data')
    bregmaNode.setAttribute('name', 'coronalcoord')
    metadata.appendChild(bregmaNode)

    dataNode = slideTemplate.createElement('bar:data')
    dataNode.setAttribute('name', 'tracingConf')
    dataNode.setAttribute('content',
    """
    {
      'DumpEachStepSVG': True,
      'DumpEachStepPNG': True,
      'PoTraceConf': {'potrace_accuracy_parameter': '0.001',
                      'potrace_width_string': '842pt',
                      'potrace_svg_resolution_string': '300x300',
                      'potrace_height_string': '1191pt'},
      'CacheLevel': 0,
      'DetectUnlabelled': True,
      'DumpVBrain': False,
      'DumpWrongSeed': True,
      'NewPathIdTemplate': 'structure%d_%s_%s',
      'DumpDirectory': '.',
      'MinFiterTimesApplication': 3,
      'GrowDefaultBoundaryColor': 200,
      'RegionAlreadyTraced': 100,
      'UnlabelledTreshold': 10
    }
    """)
    metadata.appendChild(dataNode)

    dataNode = slideTemplate.createElement('bar:data')
    dataNode.setAttribute('name', 'rendererConf')
    dataNode.setAttribute('content',
    """
    {
      'ReferenceHeight': 1191,
      'ReferenceWidth': 842,
      'imageSize': (4210, 5955)
    }
    """)
    metadata.appendChild(dataNode)

    svgNode.appendChild(metadata)
    svgNode.removeAttribute("xml:space")
    svgNode.setAttribute('xmlns:bar',"http://www.3dbar.org")
    svgNode.setAttribute('viewBox', '0 0 842 1191')
    svgNode.setAttribute('width', '842')
    svgNode.setAttribute('height', '1191')

    for i, node in enumerate(slideNodes):
        a, b, c, d = cleanSlide(node, slideTemplate)
        transformationNode.setAttribute('content', ', '.join(str(x) for x in (a, b, c, d)))
        #getTags(node, i)

        nId = node.getAttribute('id').split('_')
        # id == '_x2D_' + bregma [+ '_' + ...]
        bregma = float(nId[2]) * (-1 if nId[1] == 'x2D' else 1)
        bregmaNode.setAttribute('content', str(bregma))
        print "slide %d (AP = %f, LR = %f*x + %f , DV = %f * y + %f)"\
               % (i, bregma, a, b, c, d)

        # fetch only text, path and line elements
        content = list(node.getElementsByTagName('path'))
        for path in content:
            if path.hasAttribute('clip-path'):
                path.removeAttribute('clip-path')

        paths = []

        for line in node.getElementsByTagName('line'):
            path = slideTemplate.createElement('path')
            d = 'M ' + line.getAttribute('x1') + ',' + line.getAttribute('y1')\
                + ' L ' + line.getAttribute('x2') + ',' + line.getAttribute('y2')\
                + ' Z'
            path.setAttribute('d', d)
            for a in ['stroke-width']:
                path.setAttribute(a, line.getAttribute(a))

            paths.append(path)

        for j, path in enumerate(content + paths):
            path.setAttribute('id', 'path%d' % j)
            path.setAttribute('fill', 'none')
            path.setAttribute('stroke', '#23b5d5')

        texts = list(node.getElementsByTagName('text'))

        for n in content + texts:
            parent = n.parentNode
            parent.removeChild(n)

        vBrainLabel = slideTemplate.createElement('text')
        vBrainLabel.appendChild(slideTemplate.createTextNode('vBrain'))
        vBrainLabel.setAttribute('x', '800')
        vBrainLabel.setAttribute('y', '800')
        texts = [vBrainLabel] + texts
        content.extend(texts)

        for j, text in enumerate(texts):
            text.setAttribute('id', 'label%d' % j)
            text.setAttribute('font-size', '9px')
            text.setAttribute('font-family', 'Helvetica,sans-serif')
            text.setAttribute('stroke', 'none')

        g = slideTemplate.createElement('g')
        g.setAttribute('id', 'content')
        for n in content + paths:
            g.appendChild(n)

        svgNode.appendChild(g)
        
        node.unlink()

        fName = dstPattern % (i + 1)
        fh = open(fName, 'w')
        #print 'writing %s' % fName
        # there is an unicode encoding bug in writexml -_-
        #slideTemplate.writexml(fh, addindent=' ', newl='\n', encoding='utf-8')
        # and there is problem with some older xml.dom libraries and indents
        # of text elements
        fh.write(slideTemplate.toprettyxml(indent="", newl="\n", encoding='utf-8'))
        fh.close()
        svgNode.removeChild(g)
        g.unlink()


if __name__=='__main__':
    if len(sys.argv) != 3:
        print "USAGE: %s <source filename> <output filename pattern>" % sys.argv[0]
        sys.exit(1)

    parseSVG(sys.argv[1], sys.argv[2])
    for tag in sorted(tags):
        print tag, sorted(tags[tag])
