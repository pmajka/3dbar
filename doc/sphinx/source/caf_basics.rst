======================
Basics of CAF datasets
======================

Basics of CAF slide
===================

How to create *CAF slide*?


In order to use CAF API you need to import ``bar`` module:

   >>> import bar

Creating empty CAF slide
------------------------

   >>> slide=bar.barCafSlide(slideNumber=0)  #doctest: +ELLIPSIS

Creating delineations of brain regions
--------------------------------------

Note that, by definition, SVG paths representing brain regions are closed paths
in sense of `SVG closepath` command and they should be expressed using SVG
absolute coordinates. By default API believes that provided paths
are valid and does not check their syntax thus following invalid path definition will be accepted:

   >>> path=bar.barPath("structure_s1_AA","M 100,100 l 100 200 L 200 200", "#ff0000")

In order to force path validation of
path definition set ``clearPathDef`` to ``True``. If invalid path is provided an exception is raised.

   >>> path=bar.barPath("structure_s1_AA","M 100,100 L 100 200 L 200 200", "#ff0000", clearPathDef=True)
   Traceback (most recent call last):
   ValueError: Invalid path definition provided

.. important:: Providing invalid path definitions will surely lead to errors in
   further steps. If you are not sure about path definition - validate it.
   
   >>> path=bar.barPath("structure_s1_AA","M 100,100 L 100 200 L 200 200 Z", "#ff0000", clearPathDef=True)
   >>> print path
   <path bar:growlevel="0" d="M100.0,100.0 L100.0,200.0 L200.0,200.0 Z " fill="#ff0000" id="structure_s1_AA" positive="True" stroke="none"/>

Path id convention
++++++++++++++++++

Additional properties
+++++++++++++++++++++

Cusomizing paths
+++++++++++++++++++++++


Adding labels
-------------

Automatic label generation
++++++++++++++++++++++++++

   >>> slide.generateLabels()  #doctest: +ELLIPSIS
   <bar.base.barTracedSlideRenderer object at 0x...>

Adding information about spatial coordinate system
--------------------------------------------------

Manually
++++++++

Using markers
+++++++++++++

Putting pieces togeater
-----------------------


   >>> import bar
   >>> import datetime
   >>> from random import gauss

   >>> slideRange    = range(50)
   >>> coronalCoords = map(lambda x: 50 - x - gauss(1, 0.25), slideRange)

   >>> slides = []
   >>> indexer = bar.barIndexer()

   >>> for i in slideRange:
   >>>     pathId  = "structure_s%02d_AA" % i
   >>>     pathDef = "M %d,100 L %d,500 L 500,500 Z" % (100+2*i, 100+2*i)
   >>>     path=bar.barPath(pathId, pathDef ,"#ff0000", clearPathDef=True)
   >>>     
   >>>     structure = bar.barGenericStructure("AA", "#ff0000", [path])
   >>>     
   >>>     slide=bar.barCafSlide(slideNumber=i)
   >>>     slide.addStructures(structure)
   >>>     slide.metadata = bar.barTransfMatrixMetadataElement((1.0,0,1.0,0))
   >>>     slide.metadata = bar.barBregmaMetadataElement(coronalCoords[i])
   >>>     slide.writeXMLtoFile("%02d_traced_v0.svg" % i)
   >>>     
   >>>     indexer.indexSingleSlide(slide, i)

   >>> indexerProperties = {
   >>> 'ReferenceWidth'   : str(slide._rendererConf['imageSize'][0]),
   >>> 'ReferenceHeight'  : str(slide._rendererConf['imageSize'][1]),
   >>> 'FilenameTemplate' : '%02d_traced_v%d.svg',\
   >>> 'RefCords'  : "0,0,1.0,1.0",
   >>> 'CAFName'   : "caf_test",
   >>> 'CAFComment': 'Exemplary CAF dataset',
   >>> 'CAFCreator': 'Put your fullname here',
   >>> 'CAFCreatorEmail': 'your.email@here.org',
   >>> 'CAFCompilationTime': datetime.datetime.utcnow().strftime("%F %T"),
   >>> 'CAFSlideUnits':'mm'}

   >>> # Set indexer properties        
   >>> indexer.updateProperties(indexerProperties)
   >>> indexer.createFlatHierarchy()
   >>> indexer.fullNameMapping = {}
   >>> indexer.colorMapping = {}

   >>> indexer.writeXMLtoFile('index.xml')
