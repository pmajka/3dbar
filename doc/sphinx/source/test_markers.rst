.. -*- rest -*-
.. vim:syntax=rest

========================================================
CAF API  tests: ``barMarker`` class and its subclasses
========================================================

Locating slide in spatial reference system (SRS)

The last thing to make the CAF slide complete is to locate it in a spatial
coordinate system. CAF supports orthogonal, 3-D coordinate systems which seem to
cover the majority of SRS used in brain atlases (e.g. Stereotactic coordinate
system, the Waxholm Space, Talairach Space). In a CAF dataset infotmation about
used SRS and its units of measurements is stored in the CAF index file. Wherever
it is possible, link to the INCF DAI SRS is provided offering more precise
description of the given SRS.

Each slide contains information about its own location in th SRS. This
information is stored within the CAF slide. This information if expressed using
two sets of numbers:

    - Intra-plane transofrmation allpowith the software to express location of
      exery point of the slide using SRS coordinates
    - stack coordinate (coordinate perpendicular to the slide plane).
 
E.g. the first set consists of 4 numbers (a,b,c,d) while the second contains
only one number (z).  The formula to convert SVG coordinates into SRS
coordinates is following:
    
    x' = a * x + b
    y' = c * y + d 
    z' = z

Where (x,y,z) are SVG coordinates while (x',y',z') are related SRS coordinates.

In the opposite direction:

.. math::

    x = (x' - b)/a
    y = (y' - d)/c
    z = z'

Each CAF slide can carry different SVG to SRS coordinates transformation.
However, if the purpose of the given dataset is to serve as as source to 3-D
model generation this variability is limited and all slides has to carry the
same parameters.

Embedding SRS information into CAF slide:

Mentioned coefficients can be embedded into CAF slide in two ways:

1. By explicitly defining transformation,
2. By calculating transformation from provided data with the help of ``markers``

In order to calculate SRS <=> SVG transformation one have to establish three
markers. Two in-plane markers and single intra-plane marker.


Obviously, we need to import bar module

.. doctest:: 
    
    >>> import bar
    >>> m1 = bar.barCoordinateMarker((0,0),(10,10))
    >>> m2 = bar.barCoordinateMarker((5,5),(500,500))
    >>> bm = bar.barCoronalMarker(6.0, (800, 800))

Let's display the XML/SVG representation of the markers:    

.. doctest::

    >>> print m1
    <text fill="#000000" font-family="Helvetica,sans-serif" font-size="18px" stroke="none" x="10" y="10">(0.000000,0.000000)</text>
    >>> print m2
    <text fill="#000000" font-family="Helvetica,sans-serif" font-size="18px" stroke="none" x="500" y="500">(5.000000,5.000000)</text>
    >>> print bm
    <text fill="#000000" font-family="Helvetica,sans-serif" font-size="18px" stroke="none" x="800" y="800">Bregma:6.000000</text>

Create empty CAF slide and locate it in SRS using created markers. By default,
the slide does not contain any infotmation abou its location is spatial
coordinate system.

.. doctest::
    
    >>> slide = bar.barCafSlide()
    >>> slide.metadata
    {}

SVG to SRS transformation can be calucated and put into the slide using methods
available in CAF API:

.. doctest::

    >>> bar.base.processMarkers(m1,m2,bm) #doctest: +ELLIPSIS
    (<bar.base.barTransfMatrixMetadataElement object at 0x...>, <bar.base.barBregmaMetadataElement object at 0x...>)

Add indormation about SRS to the slide:

.. doctest::

    >>> slide.updateMetadata(bar.base.processMarkers(m1,m2,bm))

From this moment one can express location on the slide using both, SVG and SRS
coordinates. To convert between these coordinates use ``svg2srs((svgx,svgy),
ndims = 2)`` method. Where (svgx,svgy) are SVG coordinate system to be converted
into spatial coordinates. While  ``ndims`` is number of dimensions of returned
value (determines if output value will be 2 or 3 dimensional; when ``ndims ==
3`` inter-plane coordinate is also included):

.. doctest::

   >>> slide.svg2srs((0,0))
   (-0.1020408163265306, -0.1020408163265306)
   >>> slide.svg2srs((30,20), ndims=3)
   (0.20408163265306117, 0.1020408163265306, 6.0)
  
Composition of ``svg2srs`` and ``srs2svg`` should result in initial coordinate.

.. doctest::

   >>> slide.srs2svg(slide.svg2srs((30,20)))
   (29.999999999999996, 20.0)
   >>> slide.svg2srs(slide.srs2svg((-1,2)))
   (-0.99999999999999989, 2.0)

Full functionality is preserved after loading and saving the slide:

.. doctest::

    >>> slide.writeXMLtoFile('test_markers.svg')
    >>> testSlide = bar.barCafSlide.fromXML('test_markers.svg')
    >>> testSlide.srs2svg(testSlide.svg2srs((30,20)))
    (30.0, 20.0)
    >>> testSlide.svg2srs(testSlide.srs2svg((-1,2)))
    (-0.99999999999999989, 2.0)

Just remove all the temporary files.

.. doctest::

    >>> import os
    >>> os.remove('test_markers.svg')
