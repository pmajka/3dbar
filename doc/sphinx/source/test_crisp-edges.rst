.. -*- rest -*-
.. vim:syntax=rest

========================================================
CAF tests: ``crisp-edges`` property
========================================================

Crisp edges property determines the rendering settings of the SVG drawing.
Note: By now (and probably also by the future) the 'shape-rendering' property
is run-time property only and is not stored or loaded from SVG files.

Tests
=========================================================

.. doctest:: 

    >>> import bar

Create empty slide and check its 'crispEdges' property

.. doctest:: 
    
    >>> testSlide = bar.barCafSlide()
    >>> print testSlide.crispEdges
    True

Let's set ``crispEdges`` to ``False``

.. doctest::
    
    >>> testSlide.crispEdges = False

Now, lets validate 'crispEdges' property on the ``path`` object.
Path element has assigned corresponding attribute defined

.. doctest::
    
    >>> testPath = bar.barPath("structure_test_test", "M 100 100 L 100 200 L 200 200 Z", "#ff0000")
    >>> testPath.crispEdges = True
    >>> print testPath
    <path bar:growlevel="0" d="M 100 100 L 100 200 L 200 200 Z" fill="#ff0000" id="structure_test_test" positive="True" shape-rendering="crisp-edges" stroke="none"/>
    
    >>> testPath.crispEdges = False
    >>> print testPath
    <path bar:growlevel="0" d="M 100 100 L 100 200 L 200 200 Z" fill="#ff0000" id="structure_test_test" positive="True" shape-rendering="geometric-precision" stroke="none"/>

Note that ``crispEdges`` property accepts only boolean values. Providing type
other than boolean will cause exception.

.. doctest::
    
    >>> testPath.crispEdges = 'string is invalid'
    Traceback (most recent call last):
    AssertionError: Boolean value expected
    
    >>> testSlide.crispEdges = 'string is invalid'
    Traceback (most recent call last):
    AssertionError: Boolean value expected

``crispEdgest`` should also always return boolean value:

.. doctest::

    >>> type(testPath.crispEdges) == type(True)
    True
    
    >>> type(testSlide.crispEdges) == type(True)
    True
