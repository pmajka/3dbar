.. -*- rest -*-
.. vim:syntax=rest

===========================================================
CAF tests: ``type`` property (barGenericStructure, barPath)
===========================================================

Attribute holding type of the feature delineated by given path. For example
it can be like `gray matter`, `white matter`, `single cell`, `ventricle`, and
other... This property tries to mimic INCF DAI `feature` attribute would be extended
after establishing the INCF DAI common metadata set.

Tests
=========================================================

.. doctest:: 
    
    >>> import bar

Let's create simple path:

.. doctest:: 
    
    >>> path = bar.barPath("structure_test00_test", "M 100 100 L 100 200 L 200 200 Z", "#00ff00")

By default, path has no `type` assigned:

.. doctest:: 
    
    >>> print path.type
    None

We can assingn any consistent string as feature type:

.. doctest:: 
    
    >>> path.type="white-matter"

But inconsistent string will not work:

.. doctest:: 
    
    >>> path.type="invalid:  hite-mat ter"
    Traceback (most recent call last):
    AssertionError: Invalid feature type name provided: invalid:  hite-mat ter

Also, any non-string value (except None) will raise an exception:

.. doctest:: 
    
    >>> path.type= []
    Traceback (most recent call last):
    AssertionError: String or 'None' value expected
    >>> path.type = None

Similarly as for single path, you can define the type attribute for the whole structure
Let's create exemplary structure and assign a type:

.. doctest:: 
    
    >>> structure = bar.barGenericStructure("test", "#00ff00")

By default, structure `type` property is also `None`:

.. doctest:: 
    
    >>> print structure.type
    None

You can assign any reasonable string or `None` value:

.. doctest:: 
    
    >>> structure.type = "test-type"
    >>> structure.type = None

But you cannot assign any other type than string or `None`:

.. doctest:: 
    
    >>> structure.type = ['dsf']
    Traceback (most recent call last):
    AssertionError: String or 'None' value expected
    
    >>> structure.type = True
    Traceback (most recent call last):
    AssertionError: String or 'None' value expected

You can assign a path to a structure:

.. doctest:: 
    
    >>> structure.addPaths(path)

After that, their types match. Type from structure is copied to the all paths belonging to this structure.

.. doctest:: 
    
    >>> path.type, structure.type
    (None, None)
    >>> path.type == structure.type
    True

After altering type of the structure, the type of its path is also altered:

.. doctest:: 
    
    >>> structure.type="test-type"
    
    >>> path.type, structure.type
    ('test-type', 'test-type')
    >>> path.type == structure.type
    True

But it doesn't work at the opposite direction:

.. doctest:: 
    
    >>> path.type = "other-type"
    
    >>> path.type, structure.type
    ('other-type', 'test-type')
    >>> path.type == structure.type
    False

Thus after adding given path to the structure it is recommended to define type
of the path indirectly - thought the structure. `Type` property is stored with CAF slide and can be loaded from XML.
