.. -*- rest -*-
.. vim:syntax=rest


========================================
3d Brain Atlas Reconstructor readme file
========================================

In this file you can find a brief description of the 3D Brain Atlas
Reconstructor software instalation and usage. Please visit
the http://www.3dbar.org website for more detailed description.

If you haven't done this already, please let us know that you are using
3D Brain Atlas Reconstructor by filling out short form available on
http://www.3dbars.org/register . Thanks a lot.

Installing required packages (Ubuntu)
=====================================


* Installation in Ubuntu/Kubuntu 12.04 LTS and 14.04 LTS (confirmed 7.04.2014)

  1. Install the Visualization Toolkit and other graphics libraries::

       sudo apt-get install \
       libvtk5.8 libvtk5-dev libvtk5.8-qt4 libvtk5-qt4-dev \
       tk8.5 tk8.5-dev \
       python-vtk libgtkgl2.0-1 libgtkgl2.0-dev libgtkglext1 librsvg2-2 python-nifti

  2. Install python related packages::

       sudo apt-get install \
       python-gtkglext1 python-rsvg python-opengl python-numpy python-scipy python-wxgtk2.8

  3. Other packages::

      sudo apt-get install imagemagick \
      potrace pstoedit python-setuptools python-epydoc

* Installation in Ubuntu/Kubuntu 11.10

  1. Install the Visualization Toolkit and other graphics libraries::

       sudo apt-get install libvtk5.6 libvtk5-dev libvtk5.6-qt4 \
       libvtk5-qt4-dev tk8.5 tk8.5-dev python-vtk libgtkgl2.0-1 \
       libgtkgl2.0-dev libgtkglext1 librsvg2-2 python-nifti

  2. Install python related packages::

       sudo apt-get install python-gtkglext1 python-rsvg python-opengl \
       python-numpy python-scipy python-wxgtk2.8
       
  3. Other packages::

       sudo apt-get install potrace pstoedit python-setuptools python-epydoc

  4. Install Sphinx::

       sudo easy_install -U Sphinx


* Installation in Ubuntu 10.10 and Ubuntu 11.04

  1. Install the Visualization Toolkit and other graphics libraries::

       sudo apt-get install libvtk5.4 libvtk5-dev libvtk5.4-qt4 \
       libvtk5-qt4-dev tk8.5 tk8.5-dev python-vtk libgtkgl2.0-1 \
       libgtkgl2.0-dev libgtkglext1 librsvg2-2 python-nifti

  2. Install python related packages::

       sudo apt-get install python-gtkglext1 python-rsvg python-opengl \
       python-numpy python-scipy python-wxgtk2.8

  3. Other packages::

       sudo apt-get install potrace pstoedit python-setuptools python-epydoc

  4. Install Sphinx::

       sudo easy_install -U Sphinx


* Installation in Ubuntu 10.04

  1. Install the Visualization Toolkit and other graphics libraries::

       sudo apt-get install libvtk5.2 libvtk5-dev libvtk5.2-qt4 \
       libvtk5-qt4-dev tk8.5 tk8.5-dev python-vtk libgtkgl2.0-1 \
       libgtkgl2.0-dev libgtkglext1 librsvg2-2 python-nifti

  2. Install python related packages::

       sudo apt-get install python-gtkglext1 python-rsvg python-opengl \
       python-numpy python-scipy python-wxgtk2.6

  3. Other packages::

       sudo apt-get install potrace pstoedit python-setuptools python-epydoc

  4. Install Sphinx::

       sudo easy_install -U Sphinx


* Installation in Ubuntu 9.10

  1. Install the Visualization Toolkit and other graphics libraries::

       sudo apt-get install libvtk5.2 libvtk5-dev libvtk5.2-qt4 \
       libvtk5-qt4-dev tk8.5 tk8.5-dev python-vtk libgtkgl2.0-1 \
       libgtkgl2.0-dev libgtkglext1 librsvg2-2 python-nifti

  2. Install python related packages::

       sudo apt-get install python-gtkglext1 python-rsvg python-opengl \
       python-numpy python-scipy python-wxgtk2.6

  3. Other packages::

       sudo apt-get install potrace pstoedit python-setuptools python-epydoc

  4. Install Sphinx::

       sudo easy_install -U Sphinx

* Installation like desktop application

  1. Copy 3dbar.desktop in the good system directory
     
     for ubuntu in /usr/share/applications (all user access) or $HOME/.local/share/applications (one user access).

  2. Edit 3dbar.desktop
     
     Édit 3dbar.desktop and replace {3DBARPATH} by the correct value.


Generating CAF datasets
=======================

Once the software is installed, you need to generate CAF representations
of data of interest. For this you need to use parsers. We provide here
the following parsers:

1.  ScalableBrainAtlas DB08 template
    (http://scalablebrainatlas.incf.org/main/coronal3d.php?template=DB08)

2.  ScalableBrainAtlas PHT00 template
    (http://scalablebrainatlas.incf.org/main/coronal3d.php?template=PHT00)

3.  ScalableBrainAtlas WHS09 template
    (http://scalablebrainatlas.incf.org/main/coronal3d.php?template=WHS09)

4.  ScalableBrainAtlas WHS10 template
    (http://scalablebrainatlas.incf.org/main/coronal3d.php?template=WHS10)

5.  ScalableBrainAtlas LPBA40_on_SRI24 template
    (http://scalablebrainatlas.incf.org/main/coronal3d.php?template=LPBA40_on_SRI24)

6.  ScalableBrainAtlas RM_on_F99 template
    (http://scalablebrainatlas.incf.org/main/coronal3d.php?template=RM_on_F99)

7.  the Waxholm Space Atlas (the source mouse brain volumetric dataset)

8.  the Waxholm Space Atlas (the source mouse brain volumetric dataset), another
    delineation
    (http://software.incf.org/software/waxholm-space/waxholm-space/LabeledAtlas0.5.1/file_download?file_field=file)

9.  Symmetrical Waxholm Space Atlas (the source mouse brain volumetric dataset)

10. Paxinos and Watson "The Rat Brain in Stereotaxic Coordinates" atlas

11. Franklin and Paxinos "The Mouse Brain in Stereotaxic Coordinates" atlas

12. The Allen Mouse Brain Atlas
    (http://mouse.brain-map.org/atlas/index.html)

To generate CAF dataset for data from ScalableBrainAtlas DB08 template execute
the following commands in the root directory of the software:

::

  $ source setbarenv.sh
  $ make sba_DB08

The first line sets the path to the API and uses appropriate parser to download
the data from SBA and do the transformation into the CAF dataset.

You can also generate that way CAF dataset for any of following SBA templates:
``PHT00``, ``WHS09``, ``WHS10``, ``LPBA40_on_SRI24`` and ``RM_on_F99`` just by replacing
``DB08`` with the name of the source template.

In order to generate that way CAF dataset for the Waxholm Space Atlas replace
``sba_DB08`` with ``whs_0.5``, ``whs_0.51`` (for another WHS delineation)
or ```whs_0.5_symm`` (for symmetrical WHS).


To generate CAF dataset from Paxinos and Watson atlas (Paxinos, G. and Watson, C. (2007).
The Rat Brain In Stereotaxic Coordinates. Elsevier, 6th edition.) you have to supply
the parser with PDF file delivered with printed copy of the atlas.
Execute the following command in the root directory of the software:

::

$ bash bin/parsers/paxinos_watson_rbisc/make_svg_from_pdf_rat.sh <PDF path>

You have to replace *<PDF path>* with a valid path to the file mantioned above.
The CAF dataset will be stored in the ``atlases/paxinos_watson_rbisc/caf-src``
directory.

If the result of parsing does not satisfy you, you can edit slides derived
from the PDF atlass manually with your favourite SVG editor.

The slides are located in ``atlases/paxinos_watson_rbisc/caf-src`` directory
and named ``N_pretrace_v1.svg`` where N is the slide number.
Once you have your slides edited execute in the root directory of the software:

::

$ make -f make_pw_rbisc.mk

to reparse the edited slides.


Similarly for Paxinos and Frnklin atlas (Paxinos, G. and Franklin, K. B. J. (2008).
The Mouse Brain In Stereotaxic Coordinates. Elsevier, 3rd edition.) you have to execute:

::

$ bash bin/parsers/paxinos_franklin_mbisc/make_svg_from_pdf_mouse.sh <PDF path>

in the root directory of the software. The CAF dataset will be stored in
the ``atlases/paxinos_franklin_mbisc/caf-src`` directory.

To reparse the edited slides execute:

::

$ make -f make_pf_mbisc.mk

in the root directory of the software.


Generation of CAF dataset for The Allen Mouse Brain Atlas requires the Advanced Normalization Tools
(ANTS; http://picsl.upenn.edu/ANTS/) installed. ANTS have to be availiable as shell
commands (for an example by adding ANTS ``bin`` directory to environment value
``PATH``).

To generate CAF dataset from The Allen Mouse Brain Atlas execute:

::

$ source setbarenv.sh
$ make aba

in the root directory of the software.



Generating 3-D models
=====================

Once you have a CAF
of any dataset you can test the GUI for structure creation. To do it, in
the main directory run:

::

$ ./3dbar.sh

and choose in the menu Atlas/Open and select *index.xml* file of chosen CAF
dataset.

To test, click the topmost label on the tree in the left panel and press
*Perform reconstruction* button in the right panel. The reconstruction process
will start. When it is finished, chose in the menu *Edit/Save Model*. It allows
you to put it later in context by right click on the ontology tree.



Generating documentation
========================

In order to generate documentation execute:

::

$ source setbarenv.sh
$ make doc

The documentation for API can be viewed by opening *doc/api/html/index.html*
and the documentation for 3dBAR graphic interface can be viewed by opening
*doc/gui/html/index.html*.


Troubleshooting
=====================================

* Segmentation fault in Ubuntu 11.10

  If the reconstructor crashes like that (numbers can vary):

  ::

  $ ./3dbar.sh
  ./3dbar.sh: line 17:  2296 Segmentation fault      python bin/reconstructor/gui.py
  
  the reason can be a bug in the 'python-vtk' package installed
  in your system. Unfortunately there is no automated way to fix it - you have
  to do it manually:

  1. Find a file named 'wxVTKRenderWindowInteractor.py'. It can be located
     in '/usr/share/pyshared/vtk/wx/' directory or in similar location:
 
     ::

     $ find / -name 'wxVTKRenderWindowInteractor.py'


  2. Edit the file with your favourite ASCII editor. In the example editor 'vim'
     is used and it is assumed that the path to the file is
     '/usr/share/pyshared/vtk/wx/wxVTKRenderWindowInteractor.py':
 
     ::

     $ sudo vim /usr/share/pyshared/vtk/wx/wxVTKRenderWindowInteractor.py


  3. Near 350th line of the file find a following line:
 
     ::

                     d = '_%s_%s' % (d[2:], 'void_p')


  4. Add '\0' characters to the line to make it like below:

     ::

                     d = '_%s_%s\0' % (d[2:], 'void_p')


  5. Save the modified file.


  6. The bug should be fixed for now. Try running 3dBAR again. If this solution
     doesn't work - let us know.
