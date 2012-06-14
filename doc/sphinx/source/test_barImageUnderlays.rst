.. -*- rest -*-
.. vim:syntax=rest

========================================================
CAF API  tests: ``barSlideBackgorundElement`` class
========================================================

Obviously, we need to import bar module and the proper extension

.. doctest:: 
    
    >>> import bar
    >>> from bar.barImageUnderlays import barSlideBackgorundElement

Checking default parameters of the barSlideBackgorundElement class:

.. doctest:: 
    
    >>> bck = barSlideBackgorundElement()
    Traceback (most recent call last):
    TypeError: __init__() takes at least 2 arguments (1 given)
    
The only required parameter is a imageLink which has to be string.

.. doctest:: 

    >>> bck = barSlideBackgorundElement('anyimage.tiff')
    >>> print bck #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <image height="100.0" id="..." style="opacity:1.0" width="100.0" x="0.0" xlink:href="anyimage.tiff" y="0.0"/>
    
The size and the position attributes are optional arguments and they are required to be tuples of two floats or integers:

.. doctest:: 

    >>> bck = barSlideBackgorundElement('anyimage.tiff', size = (100,100))
    >>> print bck #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <image height="100.0" id="..." style="opacity:1.0" width="100.0" x="0.0" xlink:href="anyimage.tiff" y="0.0"/>
    
    >>> bck = barSlideBackgorundElement('anyimage.tiff', size = (10.5,10.5))
    >>> print bck #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <image height="10.5" id="..." style="opacity:1.0" width="10.5" x="0.0" xlink:href="anyimage.tiff" y="0.0"/>
    
Passing values other than integers or floats will raise an exception:

.. doctest:: 

    >>> bck = barSlideBackgorundElement('anyimage.tiff', size = (10.5,None)) #doctest: +ELLIPSIS  +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    TypeError: float() argument must be a string or a number
    
    >>> bck = barSlideBackgorundElement('anyimage.tiff', size = 'string') #doctest: +ELLIPSIS  +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: invalid literal for float(): s
    
The same for the position attribute:

.. doctest:: 

    >>> bck = barSlideBackgorundElement('anyimage.tiff', position = (100,100))
    >>> print bck #doctest: +ELLIPSIS
    <image height="100.0" id="..." style="opacity:1.0" width="100.0" x="100.0" xlink:href="anyimage.tiff" y="100.0"/>
    
    >>> bck = barSlideBackgorundElement('anyimage.tiff', position = (10.5,10.5))
    >>> print bck #doctest: +ELLIPSIS
    <image height="100.0" id="..." style="opacity:1.0" width="100.0" x="10.5" xlink:href="anyimage.tiff" y="10.5"/>
    
Passing values other than integers or floats will raise an exception:

.. doctest:: 

    >>> bck = barSlideBackgorundElement('anyimage.tiff', position = (None,10.5)) #doctest: +ELLIPSIS  +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    TypeError: float() argument must be a string or a number
    
    >>> bck = barSlideBackgorundElement('anyimage.tiff', position = 'other string') #doctest: +ELLIPSIS  +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: invalid literal for float(): o


The description, modality and preparation attributes have to be strings or None values:

.. doctest:: 
    
    >>> bck = barSlideBackgorundElement('anyimage.tiff', position = (10.5,10.5))
    >>> bck.description = 'A description of a background image'
    >>> bck.modality = 'Nissl'
    >>> bck.preparation = 'Microscope slices'
    >>> print bck #doctest: +ELLIPSIS
    <image bar:description="A description of a background image" bar:modality="Nissl" bar:preparation="Microscope slices" height="100.0" id="..." style="opacity:1.0" width="100.0" x="10.5" xlink:href="anyimage.tiff" y="10.5"/>


Other types sould not work:

.. doctest:: 
    
    >>> bck.modality = 3 #doctest: +ELLIPSIS  +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ... 
    AssertionError: Stain has to be string or None. Non-string and not None value provided. Please provide string value.
    
The opacity attribute has to be a float-compatibile value:

.. doctest:: 
    
    >>> bck.opacity = 0
    >>> bck.opacity = 0.4
    >>> print bck #doctest: +ELLIPSIS
    <image bar:description="A description of a background image" bar:modality="Nissl" bar:preparation="Microscope slices" height="100.0" id="..." style="opacity:0.4" width="100.0" x="10.5" xlink:href="anyimage.tiff" y="10.5"/>
    
    >>> bck.opacity = 'd' #doctest: +ELLIPSIS  +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...    
    AssertionError: Opacity has to be float between 0 and 1
    
    >>> bck.opacity = None #doctest: +ELLIPSIS  +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...    
    AssertionError: Opacity has to be float between 0 and 1    
    
Serialized and reproduced object has to be equal to original object:

.. doctest:: 
    
    >>> print str(bck.fromXML(bck.getXMLelement())) == str(bck)
    True
