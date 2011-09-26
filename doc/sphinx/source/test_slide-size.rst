.. -*- rest -*-
.. vim:syntax=rest

========================================================
CAF API  tests: ``size`` and  ``bitmapSize`` property
========================================================

Obviously, we need to import bar module

.. doctest:: 
    
    >>> import bar

Let's create an exemplary CAF slide with default settings

.. doctest:: 
    
    >>> slide = bar.barCafSlide()

We can read the dimensions of the SVG drawing representing CAF slide

.. doctest:: 
    
    >>> slide.size  #doctest: +SKIP
    (1200, 900)

Size is provided as tuple of two Intergers

.. doctest:: 
    
    >>> map(type, slide.size) == map(type, (1,1))
    True

Also the rendering size of the slide (which is not the same property as dimensions of the CAF slide) can be set

.. doctest:: 
    
    >>> slide.bitmapSize #doctest: +SKIP
    (1200, 900)
    >>> map(type, slide.bitmapSize) == map(type, (1,1))
    True

Size, as well as bitmapsize can be altered. Only tuple of two integers is accepted as new value
Altering slide dimensions:

.. doctest:: 
    
    >>> slide.size = (1000, 500)
    >>> slide.size
    (1000, 500)

.. doctest:: 
    
    >>> slide.size = ("1000", 500)
    Traceback (most recent call last):
    AssertionError: (int,int) Tuple of two integers required
    
    >>> slide.bitmapSize = 'invalid slide dimensions'
    Traceback (most recent call last):
    AssertionError: (int,int) Tuple of two integers required

`Size` and `bitmap size` are related with some internal properies that can be edited by advanded user to better customize the slides.
Changing the slide size alters the slide template as well as tracing and rendering properties

.. doctest:: 
    
    >>> slide._rendererConf
    {'ReferenceHeight': 500, 'ReferenceWidth': 1000, 'imageSize': (1200, 900)}
    >>> slide._tracingConf #doctest: +SKIP

Changing the slide size alters the slide template as well as tracing and rendering properties

.. doctest:: 
    
    >>> slide.size = (1000,500)
    >>> slide.bitmapSize = (2000, 1000)
    >>> slide._rendererConf
    {'ReferenceHeight': 500, 'ReferenceWidth': 1000, 'imageSize': (2000, 1000)}
