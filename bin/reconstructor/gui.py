#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    This file is part of 3d Brain Atlas Reconstructor                        #
#                                                                             #
#    Copyright (C) 2010-2011 Piotr Majka, Jakub M. Kowalski                   #
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

"""
Graphic user interface for 3dbar.

G{importgraph}
"""

from time import time
import random, sys, os, glob

#import wxversion        # Force using wxPython in version 2.6 
#wxversion.select('2.6') # as 2.8 causes blinking in rendering window
                         # while 2.6 in 10.04 causes segfault when accesing
                         # combo box - your choice.
# Be careful!
ENABLE_EXPERIMENTAL_FEATURES = False

import wx
import wx.gizmos
import wx.html

import vtk
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor

import bar.rec.structure_holder as structureHolder
from bar.rec.barreconstructor import barPipeline, barParam, barPipeElem, VTK_PIPELINE,\
                             DISPLAYABLE, barReconstructionModule,\
                             HTMLColorToRGB, BAR_DEFAULT_RECONSTRUCTION_DIR,\
                             BAR_ATLAS_INDEX_FILENAME, BAR_TEMPLATE,\
                             BAR_EXPORT_VOLUME_FORMATS,\
                             BAR_EXPORT_SCENE_FORMATS, BAR_CACHED_MODEL_MASK

random.seed(10000)

#TODO: Deprecated, needs to be removed in near future
#sys.path.append('../parsers/s')

BAR_VERSION = "ver. 0.1"

BAR_HELP_WEBSITE_URL = 'firefox -new-tab http://www.3dbar.org/'
BAR_HELP_ABOUT_URL   = 'firefox -new-tab http://www.3dbar.org/wiki/barSoftware3dbarTeaser'

BAR_GUI_MSGBOX_TITLE = '3d Brain Atlas Reconstructor'
BAR_GUI_NODEFEXPDIR  = "No default model directory selected. Please choose directory."
BAR_GUI_NOTEBOOK_MODEL_TITLE = "Model customization"
BAR_GUI_NOTEBOOK_STRC_SEL_TITLE = "Structure selection"
BAR_GUI_FRAME_TITLE = "3d Brain Atlas Reconstructor " + BAR_VERSION


class vtkParamCtrl(wx.TextCtrl):
    """
    Class defining text box used for providing data for vtk filters.
    This class allows to define integer or float values. Boolean values are
    handled by other class.
    """
    
    def __init__(self, parent, value, size, type):
        """
        @type  value: number (integer or float)
        @param value: initial value of given parameter
        
        @type  type: string
        @param type: type of value holded by given instance (usually int or
                     float). In other words: type of 'value' argument.
        """
        
        super(self.__class__, self).\
                __init__(parent,
                         value = value,
                         size = size,
                         style = wx.TE_PROCESS_ENTER)
        self.vtkParamType = type
    
    def GetValue(self):
        """
        Function extracts value from text box and returns string value converted
        to proper type.

        @return: TextCtrl value converted to proper type (either float or
        integer)
        """
        return self.vtkParamType(super(self.__class__, self).GetValue())


class vtkBoolParamCtrl(wx.CheckBox):
    """
    Class is an extension of wx.CheckBox handles booleaan values for vtk
    filters.
    """
    
    def __init__(self, parent, label, type):
        """
        @type  type: string
        @param type: type of value holded by given instance (usually int or
                     float). In other words: type of 'value' argument.
        """
        super(self.__class__, self).__init__(parent, -1, label)
        self.vtkParamType = type


class vtkHiddenParam(object):
    """
    Handles VTK pipeline element (filter) parametes that has hidden attribute
    set to True. Parameter cannont be modified using GUI as it has no representation
    by it can be still modified internally.
    """
    
    def __init__(self, type, value = None):
        self.vtkParamType = type
        if value: self.SetValue(value)
    
    def GetValue(self):
        return self.vtkParamType(self.value)
    
    def SetValue(self, newValue):
        self.value = newValue


class vtkPipelineElement(wx.Panel):
    """
    Class provides interface and behaviour of single vtk pipeline element
    (filter). Pipleline elements are represented by barPipeElem class.

    Final panel consists of various elements:
        1. Enable / Disable filter checkbox: Determines, if given filter may be
           used as a part of pipeline
        2. Settings for each defined filter parameter is represented by text box
           (for floats or integers) or by checkbox (for boolean parameters).
        3. Integers or floats paramers may constist of more than one (usually
           three) values. Textbox is created for each input value.
    
    Behaviour is provided by C{self.getPipelineElement}.
    """
    def __init__(self, parent, sourcePipelineElement):
        """
        Creates instance of wxPanel providing interface for given vtk filter
        represented by C{sourcePipelineElement} argument.
        
        It is possible to fix enabled/disabled state of the filter.
        
        @type  sourcePipelineElement: barPipeElem
        @param sourcePipelineElement: vtk pipeline element basing for which
                                      interface element will be provided.
                
        @todo: create properties: enabled, ...
        @todo: Extract main loop in this function into separate function
        
        @return: None
        """
        
        # Initialize wx panel class instance
        super(self.__class__, self).__init__(parent)
        
        # Make simple alias
        pelem = sourcePipelineElement
        
        # name of the instance is the same as vtk pipeline class element
        self.name = pelem.cls

        # Define sizer holding all widgets:
        self.sizer = wx.BoxSizer(wx.VERTICAL)
                
        # Create checkbox determining wheter filter is enabled or disabled.
        # Enabling filter means using it in pipeline, disabling filter means
        # excluding it from pipeline.
        # old method: self.filterEnabled = wx.CheckBox(self, -1, pelem.cls.__name__)
        self.filterEnabled = wx.CheckBox(self, -1, pelem.desc)
        self.filterEnabled.SetValue(pelem.on)
        # It is possible to fix enabled/disabled state of the filter.
        if pelem.disable: self.filterEnabled.Disable()
       
        # Append enabled/disabled checkbox to sizer
        self.sizer.Add(self.filterEnabled, proportion = 0, border = 0)
       
        # Initialize dictionary holding references for all filter's parameters
        # ie. self.paramCtrls['setStandardDaviation'] gives list of references to
        # textboxes defining parameters values.
        self.paramCtrls = {}
       
        #TODO: Put this loop into separate function
        # Iterate over all parameters and create appropriate widgets
        for param in pelem.params:
            newElemSizer= wx.BoxSizer(wx.VERTICAL)
            
            self.paramCtrls[param.name] = []

            # Handle parameters that do not have widget representation
            if param.hidden:
                newElemCtrl = vtkHiddenParam(param.type)
                newElemCtrl.SetValue(param.args[0])
                self.paramCtrls[param.name].append(newElemCtrl)
                continue

            # Each boolean filter parameters is represented by checkbox
            # while float/integer values are represented by textboxes.
            if param.type is bool:
                # Create widget, Initialize value, append to sizer and collect
                # reference
                newElemCtrl = vtkBoolParamCtrl(self,
                                               label = param.desc,
                                               type = param.type)
                newElemCtrl.SetValue(param.args[0])
                newElemSizer.Add(newElemCtrl)
                
                self.paramCtrls[param.name].append(newElemCtrl)
            else:
                # Create label for given parameter and append it to the sizer
                newElemLabel= wx.StaticText(self, label = param.desc, size=(-1,-1))
                newElemSizer.Add(newElemLabel)
                
                # For each parameter, text boxt is created and then initial
                # value is set, reference to the widget is stored and widget is
                # apended into sizer
                if hasattr(param.args, "__iter__"):
                     for pararg in param.args:
                         newElemCtrl = vtkParamCtrl(self,
                                                    value = str(pararg),
                                                    size=(40, -1),
                                                    type = param.type)
                         newElemSizer.Add(newElemCtrl, 0, border = 0)
                         self.paramCtrls[param.name].append(newElemCtrl)

            self.sizer.Add(newElemSizer, proportion = 0)
            # End of processing single parameter
        
        # Provide sizer for the panel.
        self.SetSizer(self.sizer)
    
    def getPipelineElement(self):
        """
        Creates PipeElem basing on state of the class instance
                
        @return: PipeElem corresponding to given class instance.
        """
        
        # Initialize empty array holding Param objects 
        params = []
        
        # Iterate over all parameter widgets and extract values
        for (paramName, paramValues) in self.paramCtrls.items():
            params.append(self.getParam((paramName, paramValues)))
        
        # Get value status for given filter
        status = self.filterEnabled.GetValue()
        
        # Return pipe element object
        return barPipeElem(self.name, on = status, params = params)
    
    def getParam(self, (paramName, paramValues) ):
        """
        @type  paramName: string
        @param paramName: Name of the parameter (as it is in vtk)
        
        @type  paramValues: wxWidget
        @param paramValues: Reference to wxWidget holding value or values for
                            particular parameter
        
        @return: Param object for given parameter name
        
        Method creates Param objects basing on values provided by user via GUI
        """
        # List of passed arguments
        varArr = []
        
        # Iterate over all widgets that holds values for given parameter
        for control in paramValues:
            # Get value from given widget
            varArr.append(control.GetValue())
        
        return barParam(paramName, varArr)


class PanelHeader(wx.StaticText):
    """
    Header static text.
    """
    
    def __init__(self, parent, headerLabel):
        """
        Creates static text which serves as a panel header.
        It has special formatting such as larger font, etc.
        @return: None
        """
        wx.StaticText.__init__(self, parent, -1, headerLabel, style=wx.ALIGN_LEFT)
        
        f = self.GetFont()
        f.SetPointSize(16)
        self.SetFont(f)


class mainPanel(wx.Panel):
    """
    Class holding notebook tab allowing to review reconstruction parameters and
    structure info panel.
    
    This notebook tab consists of two panels. First panel (Structure detail
    panel) holds information about details of current structure. The second tab
    (Structure selection tab) allows to select reconstruction properties such as
    reconstruction resolution, level of reconstructed substructures or mirroring
    along y axis.
    """
    
    def __init__(self, parent):
        """
        Creates panel holding all two subpanels (Structure detail panel and
        Structure selection tab).
        """
        wx.Panel.__init__(self, parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.infoPanel = GeneralInfoPanel(self) 
        self.propsPanel= ReconstructionPropsPanel(self)
        
        sizer.Add(self.infoPanel, border = 200)
        sizer.Add(self.propsPanel, border = 200, flag = wx.EXPAND)
               
        self.SetSizer(sizer)
        self.Fit()
    
    def updateInfo(self, updateList):
        """
        @param updateList: List of detailed information about structures
                          (Abbrevation, fullName, span of slides, Assigned
                          colour)
        @type  updateList: list
        
        Sets detailed information about currently selected structure basing on
        passed list. Alias for self.infoPanel.updateInfo(updateList)
        """
        return self.infoPanel.updateInfo(updateList)
    
    def getReconstructionProperties(self):
        """
        Extracts reconstruction properties from GUI. Alias of
        C{self.propsPanel.getReconstructionProperties()}.
        
        @return: C{self.propsPanel.getReconstructionProperties()}
        """
        return self.propsPanel.getReconstructionProperties()
    
    def setReconstructionProperties(self, propsDict):
        """
        @type  propsDict: Dictionary
        @param propsDict: Dictionary of reconstruction properties that will be applied
                          to the GUI. Dict consists of following elements:
        
        @return: Value returned by
                 C{self.propsPanel.setReconstructionProperties(propsDict)}
        
        Sets reconstruction properties into the GUI basing on the provided
        dictionary. This function is alias of
        C{self.propsPanel.setReconstructionProperties(propsDict)}
        """
        return self.propsPanel.setReconstructionProperties(propsDict)
        
    def setReconstructionEnabled(self, value):
        """
        @type  value: boolean
        @param value: Boolean value that determines if 'perform reconstruction'
                      button is enabled.
        @return: Value returned by
                 C{self.propsPanel.setReconstructionEnabled(value)}

        Function is an alias of
        C{self.propsPanel.setReconstructionEnabled(value)}.
        """
        return self.propsPanel.setReconstructionEnabled(value)


class ReconstructionPropsPanel(wx.Panel):
    """
    Class holds panel containing all widgets related to defining reconstruction properties
    called 'Reconstruction properties panel'

    At the time being this panel contains following elements:

        1. Resolution in conronal plane. Defined via combo box with predefined
           values or with arbitrary values given by user 
        2. Resolution along anterior - posterior axis. Input method as above
        3. Generate substructures up to given level
        4. Mirror along y axis - checkbox.

    Predefined resolutions are calculated basing on reference resolution
    provided with CAF dataset.
    """
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        # Header label:
        strDetaisText = PanelHeader(self, "Reconstruction properties:")
        # Customize the header if You want
        #f = strDetaisText.GetFont()
        #f.SetPointSize(16)
        #strDetaisText.SetFont(f)
        
        # Define predefined resolution multipliers
        # The key of the dictionary will be visible as combo box caption
        # while the value will be used as a multiplier
        self.planarRes = {'Full': 1.0,
                'Half': 2.0,
                'Quatrer': 4.0,
                'One fifth': 5.0,
                'One tenth': 10.0}
        
        self.antPostRes = {'every 4 slides': 4.0,
                'every 2 slides': 2.0,
                '1 per slide': 1.0,
                '2 per slide': 0.5,
                '4 per slide': 0.25}
        
        sizer = wx.GridBagSizer(hgap=4, vgap=4)
        
        # Define combo boxes for selecting coronal and ant-pos resolutions
        # and bind events for those combo boxes.
        self.planarListBox  = wx.ComboBox(self,  style = wx.CB_DROPDOWN)
        self.coronalListBox = wx.ComboBox(self,  style = wx.CB_DROPDOWN)
        self.planarListBox.Bind(wx.EVT_COMBOBOX, self.__enterCoronalComboValue)
        self.coronalListBox.Bind(wx.EVT_COMBOBOX, self.__enterAntPostComboValue)
        
        # Substructure generation chceckbox
        self.substrChBox   = wx.CheckBox(self,
                label = "Generate substructures up to level: ",
                style = wx.CHK_2STATE)
        self.substrChBox.SetValue(False)
        
        self.hierDepth = wx.SpinCtrl(self, min=0, max=20, initial=0)
        
        # 'Perform reconstruction' button which launches reconstruction
        # process. By default (as no dataset is loaded) button is disabled.
        # Button becomes enabled when CAF dataset is loaded.
        self.butStart = wx.Button(self, label="Perform reconstruction")
        self.butStart.Bind(wx.EVT_BUTTON, self.__doReconstruction)
        self.butStart.Disable()
        
        # Do the layout
        gridElems = [
                (strDetaisText, (0,0), (1,2)),
                ("Coronal resolution (mm/voxel):" , (1,0), (1,1)),
                ("Anterior - posterior res. (mm/voxel):", (2,0), (1,1)),
                (self.planarListBox, (1,1), (1,1)),
                (self.coronalListBox, (2,1), (1,1)),
                (self.substrChBox, (3,0), (1,1)),
                (self.hierDepth, (3,1), (1,1)),
                (self.butStart, (4,0), (1,2))
                ]
        
        for (el, p, sp) in gridElems:
            if type(el) == type(''):
                sizer.Add(wx.StaticText(self, label = el), pos= p, span = sp)
            else:
                sizer.Add(el, pos= p, span = sp)

        self.SetSizer(sizer)
        self.Fit()
        
    def __enterCoronalComboValue(self, event):
        """
        Function handles changing value of coronal resolution combo box.
        When value (resolution preset) is changed, new resolution is calculated
        and put into combo box.
        """
        
        # Get new string value of combo box - it will be string describing
        # resolution preset. Then basing on reference resolution, new resolution
        # is calculated and put into combo box.
        #
        # Note that value considered as an resolution is the float value shown
        # in combo box
        selectedValue = event.GetString()
        newComboVal = str(self.planarRes[selectedValue]*self.xyres)
        self.planarListBox.SetValue(newComboVal)
    
    def __enterAntPostComboValue(self, event):
        """
        Function handles changing value of anterior-posterior combo box.
        When value (resolution preset) is changed, new resolution is calculated
        and put into combo box.
        """
        
        # Get new string value of combo box - it will be string describing
        # resolution preset. Then basing on reference resolution, new resolution
        # is calculated and put into combo box.
        #
        # Note that value considered as an resolution is the float value shown
        # in combo box
        selectedValue = event.GetString()
        newComboVal = str(self.antPostRes[selectedValue]*self.zres)
        self.coronalListBox.SetValue(newComboVal)
    
    def setReconstructionEnabled(self, value):
        """
        @type  value: boolean
        @param value: Determies if reconstruction may be performed.
        Enables / disables 'Perform reconstruction' button.
        """
        if value: self.butStart.Enable()
        else: self.butStart.Disable()
    
    def __doReconstruction(self, event):
        """
        Function invoked by 'Perform reconstruction button'. Launches
        reconstructino process and performs reconstruction basing on
        reconstruction properties provided bey user with the GUI.
        
        @todo: Do something with the frame reference!
        @return: None
        """
        start = time() 

        # TODO: do something better fith the frame reference
        # Grab the reference to the frame and to the ontology tree
        frame =  self.GetGrandParent().GetGrandParent()
        tree = frame.structureTree
        
        # Get reconstruction properties from values entered by user into GUI
        # Then take name of the structure from ontology tree
        # TODO: getting the name is the subject of changes
        recProps = self.getReconstructionProperties()
        name = tree.GetItemText(tree.GetSelection())
       
        # Depending on the substructure generation box launch substructure
        # generation or generate superior structure only.
        if not self.substrChBox.GetValue():
            # if generating single structure:
            frame.generateModel(name, recProps['xyres'], recProps['zres'])
        else:
            # when generating whole hierarchy:
            frame.generateSubstructures(name, self.hierDepth.GetValue())

        print >>sys.stderr, "Reconstruction successfully completed."
        print >>sys.stderr, "Reconstruction time: %.2fs" % (time() - start) 

    def __resetValues(self):
        """
        Clears all widgets providing reconstruction proeprties.
        @return: None
        """
        self.planarListBox.Clear()
        self.coronalListBox.Clear()
        #self.mirrorChBox.SetValue(False)
        self.substrChBox.SetValue(False)
        self.hierDepth.SetValue(0)

    def getReconstructionProperties(self):
        """
        Extracts reconstruction properties from GUI and return them in form of
        dictionary: {xres,zres,generateSubstuctuers,substructuresDepth,mirrorY}.
        
        Reslolution parameters are floats, Level of generated substructures is
        integer and generateSubstuctuers and mirrorY parameters are float.
        
        @return: (dict) Dictionary holding reconstruction parameters
        """
        # Extract parameters from GUI:
        xyres = float(self.planarListBox.GetValue())
        zres  = float(self.coronalListBox.GetValue())
        generateSubstuctuers = self.substrChBox.GetValue()
        substructuresDepth = self.hierDepth.GetValue()
        
        # Create dictionary from extracted values:
        retDict = {
                'xyres': xyres,
                'zres' : zres,
                'generateSubstuctuers': generateSubstuctuers,
                'substructuresDepth'  : substructuresDepth}
        
        # Return created distionary
        return retDict
    
    def setReconstructionProperties(self, propsDict):
        """
        Puts reconstruction setting provided in C{propsDict} into widgets.
        Dictionary contain fillowing elements:
        {xres,zres,generateSubstuctuers,substructuresDepth,mirrorY}.
        
        @type  propsDict: Dict
        @param propsDict: Dictionary holding list of reconstuction parameters.
        
        @return: None
        """
        
        # At first clear widgets containing reconstruction parameters:
        self.__resetValues()
        self.xyres = float(propsDict['xyres'])
        
        # Append labels of predefined values
        map(lambda x: self.planarListBox.Append(str(x)), self.planarRes.keys())
        # Set the default coronal plane resolution and make the default size of
        # the voxel 4 times larger than reference size:
        self.planarListBox.SetValue(str(4.*self.xyres))
        
        self.zres = float(propsDict['zres'])
        # Append labels of predefined values
        # Enter default value literaly. Make voxel size in this dimension equal
        # to distanice betwen consecutive slices.
        map(lambda x: self.coronalListBox.Append(str(x)), self.antPostRes.keys())
        self.coronalListBox.SetValue(str(1. * self.zres))


class GeneralInfoPanel(wx.Panel):
    """
    Class holding 'Structure details' panel. Vwry simple class.
    """
    def __init__(self, parent):
        """
        Creates and layous 'Structure details' panel
        @return: None
        """
        wx.Panel.__init__(self, parent)
        
        # Define labels
        labels = ('Abbreviated name:',
                  'Full name:',
                  'Slides:',
                  'Assigned colour:')
        
        # Define strings holding information strings that will be displayed in
        # GUI. Note that they are strings created from actual data
        answers = (' ',' ',' ',' ')
        
        # Define empty placeholder for detailed information about given
        # structure.
        self.ansCtrls = []
        
        # Create sizer
        sizer = wx.GridSizer(rows = len(labels)+1, cols=2, hgap=4, vgap=4)
        
        # Create panel header
        strDetaisText = PanelHeader(self, "Structure details:")
        sizer.Add(strDetaisText, border =30)
        sizer.Add(strDetaisText)
       
        # Iterate over all labels and put them into sizer
        for (i,label) in enumerate(labels):
            label = wx.StaticText(self, -1, label, style=wx.ALIGN_LEFT)
            f = label.GetFont()
            f.SetWeight(wx.BOLD)
            label.SetFont(f)
            
            answer= wx.StaticText(self, -1, answers[i], style=wx.ALIGN_LEFT)
            sizer.Add(label)
            sizer.Add(answer)
            self.ansCtrls.append(answer)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def updateInfo(self, updateList):
        """
        Updates GUI with the structure details information provided in
        C{updateList} list.
        
        @type  updateList: list
        @param updateList: List containing 'structure details' data. List
                           contains following element: (Abbrevation, fullName,
                           span of slides, Assigned colour).
        
        @return: None
        """
        # Abbrevation (string)
        # fullName (string)
        # span of slides (tuple)
        # Assigned colour (tuple)

        # Interate over all  
        for (i, infoText) in enumerate(updateList):
            self.ansCtrls[i].SetLabel(str(infoText))
        
        # Prepere colour which is the last element of the 
        # list, 
        c = updateList[-1]       
        self.ansCtrls[-1].SetForegroundColour(wx.Colour(c[0],c[1],c[2]))


class pipelineButtonPanel(wx.Panel):
    """
    Pipeline button panel is the panel holding Refresh, Clear and Save model
    button. 
    """
    def __init__(self, parent, frameRef):
        """
        Creates panel containing panel holding buttons controlling vtkProcessing
        @return: None
        """
        wx.Panel.__init__(self, parent)
        
        # Save referece to frame,
        self.frame = frameRef
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create buttons one by one and put them into sizer
        for eachLabel, eachHandler in self.buttonData():
            button = self.buildOneButton(self, eachLabel, eachHandler)
            self.sizer.Add(button)
        
        self.SetSizer(self.sizer)
    
    def buttonData(self):
        """
        @return: Tuple of tuples containing (label, eventHandler)
        """
        return (("Refresh", self.frame.OnRefreshModel),
                ("Clear", self.frame.OnClearScene),
                ("Save model", self.frame.OnSaveModelAsPolyMesh))
    
    def buildOneButton(self, parent, label, handler):
        """
        Creates wxButton object basing on provided label and event handler.
        
        @type  label: string
        @param label: label fo the button
        
        @type  handler: function
        @param handler: function binded to wx.EVT_BUTTON button event
        
        @return: Button object created basing on provided arguments.
        """
        
        button = wx.Button(self, -1, label)
        button.Bind(wx.EVT_BUTTON, handler)
        return button


class pipelineManipulationPanel(wx.Panel):
    """
    Pipeline manipulation panel holds all widgets related to shaping model via
    VTK pipeline, saving models and refreshing the scene. It is actually very
    simple panel.
    """
    def __init__(self, parent, frameRef):
        """
        @type  frameRef: wxFrame reference
        @param frameRef: Reference to the wxFrame element, the main frame of
                         wxApplication
        
        @return: None
        """
        wx.Panel.__init__(self, parent)
        
        # save referece to frame
        self.frame = frameRef
        # Create sizer
        self.sizer = wx.BoxSizer()
        
        # Create empty dictionary holding references to vtk pipeline panels
        self.pipeListDict = {}
        
        # Iterate over those VTK pipeline elements that are to be displayed in
        # GUI, omit those pipeline elements that are not to be displayed
        for sourcePipelineElement in DISPLAYABLE:
            # Create panel basing on given sourcePipelineElement
            # and add it to sizer
            filterControl = vtkPipelineElement(self, sourcePipelineElement)
            self.sizer.Add(filterControl)
            # Save reference to the panel related to the sourcePipelineElement
            self.pipeListDict[sourcePipelineElement.cls.__name__] = filterControl
        
        # Create panel button and place it as a last element of the panel.
        self.buttonPanel = pipelineButtonPanel(self, self.frame)
        self.sizer.Add(self.buttonPanel)
        
        self.SetSizer(self.sizer)


class structureTree(wx.gizmos.TreeListCtrl):
    """
    Class implementing ontology tree. Class allows to load display ontology tree
    stored in CAF dataset. Handles loading, browsing and displaying elements.
    """
    def __init__(self, parent, frame):
        """
        @type  frame: reference to wxFrame object
        @param frame: Reference to wxFrame is requested to bind some wxFrame
                      methods to widgets in this class.
        
        @return: None
        """
        wx.gizmos.TreeListCtrl.__init__(self, parent, style =
                                           wx.TR_DEFAULT_STYLE
                                           | wx.TR_FULL_ROW_HIGHLIGHT)
        # Save reference to the frame
        self.frame = frame
        
        # Add columts to the tree ans add them some properties as width
        # also, bind some functions
        self.AddColumn("Abbreviation")
        self.AddColumn("Full name of the structure")
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 200)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, frame.ActivateInfoPanel)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, frame.updateInfoPanel)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, frame.switchContexActorFromTree)
        
        # Initialize dictionary holding references to the tree elements
        # Such reference is important as we want to manipulate tree elements
        # during runtime and iterating and searching elements trought the tree
        # is inconviniente.
        self.treeItemsRefs = {}
    
    def __addTreeNodes(self, parentItem, items):
        """
        @type  parentItem: reference to wxTree element 
        @param parentItem: parent tree element that will hold appended items
        
        @type  items: Dictionary
        @param items: dictionary holding all hierarchy elements and their
                      properties.
        
        Recursively travels across the data structures adding tree nodes to the
        ontology tree. Dictionary of items has form of tree. Single element has
        following form:
        
            - item[0] - holds data about top structure
            - item[1] - holds data about substructures (list)
            - item[0][0] - name(abbreviation) of root element
            - item[0][1] - full name of root structure
        """
        # Iterate trough all elements on root level adding them to ontology tree
        # If root element has children, invoke this function recursively.
        for item in items:
            # When root element does not have children
            if len(item) == 1:
                newItem = self.AppendItem(parentItem, item[0][0])
                self.SetItemText(newItem, item[0][1], 1)
                self.treeItemsRefs[item[0][0]] = newItem
            # Otherwise:
            else:
                newItem = self.AppendItem(parentItem, item[0][0])
                self.SetItemText(newItem, item[0][1], 1)
                self.treeItemsRefs[item[0][0]] = newItem
                self.__addTreeNodes(newItem, item[1])
        
    def prepareStructureTree(self):
        """
        Performs all operation related to loading ontology tree from dataset
        into tree widget:
        
            1. Remove all item from tree widget (self)
            2. Add superior element (Brain)
            3. Add whole ontology tree
            4. Expand root element of the widget
        """
        
        # Read ontlogy tree from index holder submodule
        # Name of superior brain structure may have arbitrary name stored in
        # index holder submodule.
        treeDataRoot = self.frame.sh.ih.hierarchyRootElementName
        treeData     = self.frame.sh.ih.getHierarchyTree(treeDataRoot)
         
        # Erase all elements from the tree
        self.DeleteAllItems()
        
        # Create root element and store reference to the root element
        root = self.AddRoot(treeData[0][0])
        self.treeItemsRefs[treeData[0][0]] = root
        self.SetItemText(root, treeData[0][1], 1)
        
        # Take the childs of root element in CAF ontology tree and recursively
        # add them into tree widget - treeData[1] hold all direct childrens of
        # hierarchy root element
        self.__addTreeNodes(root, treeData[1])
        
        # Expand root element
        self.Expand(root)
    
    def refreshEabledModelList(self, modelsDirectory):
        """
        @type  modelsDirectory: String
        @param modelsDirectory: Path to export model directory - directory
                                holding exported models  
        
        Checks for cached reconstructions in provided modelsDirectory. Basing on
        found files, elements of the tree are changed to bold.
        """
        
        # Prepare mask for models
        globPath = os.path.join(modelsDirectory, BAR_CACHED_MODEL_MASK)
        # List all models found reconstruction directory
        modelsList = glob.glob(globPath)
        # Make all elements of the tree to default font 
        self.__clearContextModels()
        
        # Iterate trough all cached reconstructed 
        # models and enable each model in tree widget
        for model in modelsList:
            # Extract model name from the name of the file
            groupName = os.path.basename(model).split("_")[1].split('.')[0]
            # Enable context model
            self.enableContextModel(groupName)

    def resetContents(self):
        """
        Cleans entire tree by removing all elements and internal dictionary of
        references to those elements

        @return: None
        """
        self.DeleteAllItems()
        self.treeItemsRefs = {}
    
    def clearContextModels(self):
        """
        Alias for C{self.__clearContextModels()} just for separate public and
        privete method.
        """
        self.__clearContextModels()
    
    def __clearContextModels(self):
        """
        Handle erasing all context models from the tree by iterating trough all
        stored references and changes their status to regular.
        """
        # Iterate trough all references and make all elements displayed in
        # regular way
        for groupName in self.treeItemsRefs.keys():
            # Perform all operation related to removing contex model from the
            # scene - accesing vtkInteractor, etc...
            self.disableContextModel(groupName)
            # Forces given group name to be dispalyed using black font
            self.__setContextModelSelection(groupName, False)
    
    def enableContextModel(self, groupName):
        """
        @param groupName: string
        @type  groupName: Name of the grup (name tag of group element stored in
                          ontology tree)
        Set tree list widget element to available for loading as an context
        model.
        """
        # Set representation of contex model to loaded 
        self.__setContextModelMode(groupName)
    
    def disableContextModel(self, groupName):
        """
        @type  groupName: string 
        @param groupName: Name of the grup (name tag of group element stored in
                          ontology tree)
        Sets the representation of the tree element to not available to
        displaying as a context model.
        """
        self.__setContextModelMode(groupName, False)
    
    def __setContextModelMode(self, groupName, status = True):
        """
        @type  groupName: string
        @param groupName: Name of the grup (name tag of group element stored in
                          ontology tree)
        
        @type  status: boolean
        @param status: Desired state of given group element
        
        Sets / disabled context representation of the tree element to enabled or
        disabled. If representation of groupName may be loaded as context model
        it is displayed using bold font, otherwise is it displayed using
        reugular font.
        """
        self.SetItemBold(self.treeItemsRefs[str(groupName)], status)
        
    def __setContextModelSelection(self, groupName, status):
        """
        @type  groupName: string
        @param groupName: Name of the grup (name tag of group element stored in
                          ontology tree)
        @type  status: boolean
        @param status: Desired state of given group element

        Changes the status of group with given C{groupName} to loaded as context
        model (red font color) or not loaded as context model (black font
        color).
        
        One should not confuse loaded/not loaded as context model (red/black
        font) and available for loading as context model (black or regular
        font).
        """
        
        # Select font colour depending on the passed status
        if status: colour = wx.Colour(255, 0, 0)
        else: colour = wx.Colour(0, 0, 0)
        self.SetItemTextColour(self.treeItemsRefs[str(groupName)], colour)
    
    def setContextSelecttion(self, groupName, status):
        """
        Alias for C{self.__setContextModelSelection} user for separating private
        and public functions.
        """
        self.__setContextModelSelection(groupName, status)

    def deselectAllContextModels(self):
        """
        Changes state of all elements to 'not loaded as context models'.
        """
        for groupName in self.treeItemsRefs.keys():
            self.__setContextModelSelection(groupName, False)


class treeAndSearchPanel(wx.Panel):
    """
    Class defining structure tree and and widget for searching structure in the
    tree.
    """
    def __init__(self, parent, frameRef):
        """
        @type  frameRef: wxFrame reference
        @param frameRef: Reference to the wxFrame element, the main frame of
                         wxApplication
        
        @return: None
        """
        # Just store reference to the parent frame
        self.frameRef = frameRef
        
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        self.structureTree = structureTree(self, self.frameRef)
        self.searchCtrl    = wx.TextCtrl(self,\
                                         value="Search here",\
                                         style=wx.TE_PROCESS_ENTER)
        self.searchCtrl.Bind(wx.EVT_TEXT, self.OnSearch)
        
        self.sizer.Add(self.structureTree, flag = wx.EXPAND|wx.ALL, proportion = 10)
        self.sizer.Add(self.searchCtrl, flag = wx.EXPAND|wx.ALL, proportion = 0)
    
    def OnSearch(self, event):
        """
        """
        searchStructureName = self.searchCtrl.GetValue()
        if self.structureTree.treeItemsRefs.has_key(searchStructureName):
            terrItemId = self.structureTree.treeItemsRefs[searchStructureName]
            self.structureTree.EnsureVisible(terrItemId)
            self.structureTree.SelectItem(terrItemId)


class mainGuiFrame(wx.Frame):
    def __init__(self, vtkapp):
        """
        @type  vtkapp: vtkApplication obcject
        @param vktapp: Singleton handiling all operations related to displaying
                       rendering, adding and shaping recomstructions, loading and removing
                       context models, exporting models and many, many other
                       activities.
        """
        
        wx.Frame.__init__(self, None, -1, BAR_GUI_FRAME_TITLE, size=(800,600))
        self.SetName("3dBAR_main_frame")
        
        #Assing reference to vtkApplication instance
        self.vtkapp = vtkapp
        
        # Reset default export directory and atlas directory. Default exprt
        # directory is a directory in which reconstruction are cached or
        # exported. Atlas directory is the directory in which index.xml file of
        # particular dataset is stored. On order to separate reconstruction and
        # the CAF dataset those directories should not be the same direcories.
        # 
        # By default default export directory is parallel to the atlas
        # directory.
        # 
        # Of course, atlas directory and default export directory are defined in
        # moment of loading particular CAF dataset. However, default export
        # directory may be redefined by user by choosing another direcotry via
        # dialog box.
        self.__defaultExportDir = None
        self.__atlasDirectory = None
        
        # Create splitter window, notebook tabs and ontology tree        
        self.mainWindowSplitter = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.mainWindowNotebookTab = wx.Notebook(self.mainWindowSplitter, -1, style=0)
        self.modelCustomizationTab = wx.Panel(self.mainWindowNotebookTab, -1)
        self.structureSelectionTab = mainPanel(self.mainWindowNotebookTab)
        
        # Create panel containing tree of structures and search control.        
        self.treeSearchPanel = treeAndSearchPanel(self.mainWindowSplitter, self)
        self.structureTree = self.treeSearchPanel.structureTree
        self.searchCtrl    = self.treeSearchPanel.searchCtrl
        
        # Define sizers, customize notebook tabs...
        mainWindowSizer = wx.BoxSizer(wx.HORIZONTAL)
        recPrevWinSizer = wx.BoxSizer(wx.VERTICAL)
        self.modelCustomizationTab.SetSizer(recPrevWinSizer)
        self.mainWindowNotebookTab.AddPage(self.modelCustomizationTab,
                BAR_GUI_NOTEBOOK_MODEL_TITLE)
        self.mainWindowNotebookTab.AddPage(self.structureSelectionTab,
                BAR_GUI_NOTEBOOK_STRC_SEL_TITLE)
        self.mainWindowSplitter.SplitVertically(self.treeSearchPanel, self.mainWindowNotebookTab)
        mainWindowSizer.Add(self.mainWindowSplitter, 2, wx.EXPAND, 0)
        self.SetSizer(mainWindowSizer)
        
        # Create contents of notebook tabs, menu, etc.
        self.createMenuBar()
         
        # Create pipeline manipulation panel that allows to customize 
        # model shaping process, clear or refresh scene
        self.panel = pipelineManipulationPanel(self.modelCustomizationTab, self)
       
        # Render window interactor is the window in which scene is previewed
        # also set interaction style to more convinient
        self.rwi=wxVTKRenderWindowInteractor(self.modelCustomizationTab, -1)
        self.rwi.SetInteractorStyle(
                vtk.vtkInteractorStyleTrackballCamera())
        
        # Important thing is that wxVTKRenderWindowInteractor performs rendering
        # using renderer located in self.vtkapp!
        self.vtkapp.addRenderWindow(self.rwi.GetRenderWindow())

        # Finally enable render window interactor
        self.rwi.Enable(1)
        
        recPrevWinSizer.Add(self.rwi  , flag = wx.EXPAND, proportion = 1)
        recPrevWinSizer.Add(self.panel, flag = wx.EXPAND, proportion = 0)
        
        self.statusbar = self.CreateStatusBar()
        
        # Set currently reconstructed structure to None. This prevents from
        # ambigous situaltion during saving and exporting models. 
        self.currentStructureName = None
        
        # a backup list of arguments passed to vtkapp.setReconstructionSource
        self.__lastGeneratedModel = None

# { Operation realted to searching across hierarchy tree


#}

#{ Operations related to loading and unloading context actores

    def __loadContextActor(self, groupName):
        """
        Loads cached model corresponding to given C{groupName} into model
        preview window.
        
        @type  groupName: C{string}
        @param groupName: name of the group (as in CAF hierarchy tree)
                          which reconstuction will be loaded as a context model
                          from cache.
        @return: (boolean) True when loading contex model was succesfull, False
                 otherwise.
        """
        
        # Generate filename for cached model
        filename = os.path.join(self.__defaultExportDir,\
                   BAR_TEMPLATE['exportToVTKPolydata'] % groupName)
        
        # When cached model corresponding to given groupName exists, it will be
        # loaded as context model. When cached model for given group does not
        # exists nothing will be done and False value will be loaded.
        if os.path.isfile(filename):
            ct = self.getStructureColor(groupName)
            self.vtkapp.appendContextActor(groupName, filename, ct)
            self.vtkapp.refreshRenderWindow() 
            return True
        else:
            return False
    
    def __removeContextActor(self, groupName):
        """
        @type  groupName: string
        @param groupName: name of the group (as in CAF hierarchy tree)
                          which reconstuction will be loaded as a context model
                          from cache.
        @return: None

        Removes context actor from model preview window (scene). After unloading
        context model, render window is updated.
        """
        # Simply remove actor from set of context actors
        self.vtkapp.removeContextActor(groupName)
        self.vtkapp.refreshRenderWindow()
    
    def __updateReconstructionProps(self, propsDict):
        """
        @type  propsDict: dictionary
        @param propsDict: Dictionary holding all properties regarding
                          reronstructions.
        @return: None
        
        Alias for C{self.structureSelectionTab.setReconstructionProperties}
        """
        self.structureSelectionTab.setReconstructionProperties(propsDict)

    def switchContexActorFromTree(self, event):
        """
        Switches displaying content model given by item clicked on ontology
        tree.
        """
        # Define name of the structure clicked on ontology tree
        tree = self.structureTree
        name = tree.GetItemText(event.GetItem())
        
        # If model is already loaded, unload the context model
        # and change way how the name of the model is dispalyed in the ontology
        # tree.
        # If model is not loaded, just load it.
        if self.vtkapp.hasContextActor(name):
            self.__removeContextActor(name)
            tree.setContextSelecttion(name, False)
        else:
            # When loading context model is successfull,
            # set selection in ontology tree
            if self.__loadContextActor(name):
                tree.setContextSelecttion(name, True)

#}   
#{ Structure info panel

    def __updateStructureInfoPanel(self, groupName):
        """
        @type  groupName: string
        @param groupName: name of the group (as in CAF hierarchy tree)
                          information about will be displayed in
                          StructureSelectionTab
        @return: None
        
        Function extracts detailed information from StructureHolder.
        """
        # Get full name of the structures, span of the slides on which given
        # structure is defined and colour defined to this structure 
        fullName = self.sh.ih.fullNameMapping[groupName]
        slies    = self.sh.getSlidesSpan(groupName) 
        color    = self.getStructureColor(groupName, rgb = True)
        
        # Create list from the elements and put the list to the 
        # StructureSelectionTab
        retList = [groupName, fullName, slies, color]
        self.structureSelectionTab.updateInfo(retList)

    def updateInfoPanel(self, event):
        """
        @return: None
        @todo: Change way of getting name of the structure: do not take it from
        the tree - new variable currentStructureName has to be introduced.
        
        Extracts name of the structure from tree and basic on that name details
        of the structure are shown in structure info panel
        """
        # TODO: Code below should be replaced by code with currentStructureName
        tree = self.structureTree
        name = tree.GetItemText(tree.GetSelection())
        
        self.__updateStructureInfoPanel(name)
    
    def ActivateInfoPanel(self, event):
        """
        Activates StructureSelectionTab, updates detailed information about
        currently selsected structure and sets focus on the ontology tree.
        """
        self.mainWindowNotebookTab.SetSelection(1)
        self.updateInfoPanel(event)
        self.structureTree.SetFocus()

#}    
#{ Loading, reloading and closing CAF datasets
    
    def __getAtlasFilename(self):
        """
        Displays filename selection dialog box allowing user to choose
        CAF index file and open given atlas.
        
        @rtype : C{str}
        @return: Full path to filename
        """
        
        wildcard = "CAF index files (*.xml)|*.xml|All files (*.*)|*.*"
        
        dlg = wx.FileDialog(self, "Select atlas filename...",
                os.getcwd(), style=wx.OPEN,
                wildcard=wildcard)
        
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            dlg.Destroy()
            return filename
    
    def __closeAtlas(self):
        """
        Closes currently loaded CAF dataset.
        @return: None
        """
        # Closing opened CAF dataset is related with multiple activities:
        # - Reseting contents of ontology tree
        # - Clearing model preview window (clearing scene)
        # - Rendering empty scene :)
        # - Setting current export directory to None
        # - Removing structure holder if such exists (removing reference to
        #   structure generation module)
        
        self.structureTree.resetContents()
        self.vtkapp.clearScene()
        self.__defaultExportDir = None
        self.__atlasDirectory   = None
        
        try:
            del self.sh
        except:
            pass
        
        # Disable 'about current dataset' menu item
        self.__setMenuAboutCAFEnables(False)
        
        # Set currently reconstructed structure to none
        # Name of the currently reconstructed sturcture is changed when
        # structure reconstruction was performed succesfully
        self.currentStructureName = None
    
    def __reloadAtlas(self):
        """
        Reloads currently loaded CAF dataset. Why is it useful?. Reloading atlas
        means closing it and opening again and this is how it is implemented.
        """
        # Close currenlty loaded dataset and load it again.
        # Name of the dataset is not erased when dataset is closed thus user
        # does not have to select define CAF dataset again.
        # Closing of current dataset is performed by __loadAtlas function
        self.__loadAtlas(self.__atlasDirectory)
    
    def __loadAtlas(self, indexDirectory):
        """
        @type  indexDirectory: C{str}
        @param indexDirectory: directory containing caf index file and caf
        slides. In other words CAF dataset directory.
        
        Loads CAF dataset defined by provided index directory.
        """
        # Before loading anything close opened dataset. Opening new dataset
        # without closing will cause errors :)
        self.__closeAtlas()
        
        indexFile = os.path.join(indexDirectory, BAR_ATLAS_INDEX_FILENAME)
        self.sh = structureHolder.structureHolder(\
                indexFile, indexDirectory, debugMode = True)
        self.__atlasDirectory   = indexDirectory
        
        # Try to create reconstruction directory, if directory cannot be created
        # leave default output directory undefined
        recDir =\
            os.path.abspath(os.path.join(self.__atlasDirectory,
                BAR_DEFAULT_RECONSTRUCTION_DIR))
        if not os.path.exists(recDir):
            try:
                os.mkdir(recDir)
                self.__defaultExportDir = recDir
            except:
                self.__defaultExportDir = self.__atlasDirectory
        else:
            self.__defaultExportDir = recDir
        
        # Load structure into the tree and update list of cached context model
        # basing on default reconstruction directory
        self.structureTree.prepareStructureTree()
        self.structureTree.refreshEabledModelList(self.__defaultExportDir)
        
        # Set focus on the stryctyre selection tree
        self.mainWindowNotebookTab.SetSelection(1)
        self.structureTree.SetFocus()
        
        # Getting and updating default reconstruction parameters:
        xyres = abs(self.sh.ih.refCords[-1])
        zres  = abs(float(self.sh.ih.getDefaultZres()))
        propsDict = {'xyres':xyres,'zres':zres}
        self.__updateReconstructionProps(propsDict)
        self.structureSelectionTab.setReconstructionEnabled(True)
        
        # Enable 'about current dataset' menu item
        self.__setMenuAboutCAFEnables(True)
         
        # -----------  Experimental features   -------------------------------
        # Assings colors for tree elements. Colors are taken from CAF index
        # file. This feature would not become regular but for testing purposes
        # is ok.
        if ENABLE_EXPERIMENTAL_FEATURES:
            for groupName in self.structureTree.treeItemsRefs:
                terrItemId = self.structureTree.treeItemsRefs[groupName]
                ct = self.getStructureColor(groupName, rgb = True)
                colour = wx.Colour(ct[0], ct[1], ct[2])
                self.structureTree.SetItemBackgroundColour(terrItemId, colour)
        # -------------------------------------------------------------------

    def __selectDefaultOutputDir(self):
        """
        Allows user to redefine directory where reconstructions will be stored.
        """
        # Don't do anything when atlas os not loaded
        if not self.__atlasDirectory: return
        
        # Ok, atlas is loaded, define initial path for directory selection
        # dialog box
        if self.__defaultExportDir:
            defPath = self.__defaultExportDir
        else:
            defPath = self.__atlasDirectory
        
        # Display dialog and get new name of directory
        dialog = wx.DirDialog(None, message = "Choose context directory:",
                defaultPath = self.__atlasDirectory,
                style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        
        if dialog.ShowModal() == wx.ID_OK:
            self.__defaultExportDir = dialog.GetPath()
        else:
            self.__defaultExportDir = defPath
            dialog.Destroy()
        
        # Clear scene
        self.vtkapp.clearScene()
        
        # Update context models
        self.structureTree.refreshEabledModelList(self.__defaultExportDir)
#}

    def __exportPipeline(self, name):
        filename = BAR_TEMPLATE['exportPipeline'] % name
        savePath = os.path.join(self.__defaultExportDir, filename)
        self.vtkapp.exportPipeline(savePath)

#{ Saving and exporting models

    @staticmethod
    def __getWildcard(formatInfo):
        pattern = "%(desc)s (*%(ext)s)|*%(ext)s"
        components = [pattern % info for info in formatInfo.itervalues()]
        return '|'.join(components) + '|All files (*.*)|*.*'
    
    def __exportVolumetricDataset(self):
        """
        Saves given reconstruction in one of choosen volumetric formats.
        Filename and export format are selected by user using dialog box.
        
        @return: None
        """
        wildcard = self.__getWildcard(BAR_EXPORT_VOLUME_FORMATS) 
        #wildcard  = "vtk structured grid files (*.vtk)|*.vtk|NIfTI (*.nii)|.nii|All files (*.*)|*.*"
        dialogMsg = "Save volume as..."
        
        # Define dialog
        dlg = wx.FileDialog(self,
                message = dialogMsg,
                style=wx.SAVE | wx.OVERWRITE_PROMPT,
                defaultFile = BAR_TEMPLATE['exportToVolume'] % self.currentStructureName,
                defaultDir = self.__defaultExportDir,
                wildcard=wildcard)
        
        # Invoke export function depending on 
        # selected file type
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.vtkapp.exportVolumeByExt[filename[-4:]](filename)
    
    def __savePolyDataModel(self, name = None):
        """
        @todo: Will be documented after implementing batch model generation
        which may change syntax of export functions.
        
        @return: None
        """
        tree = self.structureTree
        if not name:
            name = self.currentStructureName
        
        filename = BAR_TEMPLATE['exportToVTKPolydata'] % name
        savePath = os.path.join(self.__defaultExportDir, filename)
        self.vtkapp.exportToVTKPolydata(savePath)
        
        tree.enableContextModel(name)
        self.__exportPipeline(name)
   
    def __exportRenderWindow(self):
        """
        @todo: Will be documented after implementing batch model generation
        which may change syntax of export functions.
        
        @return: None
        """
        wildcard = self.__getWildcard(BAR_EXPORT_SCENE_FORMATS)
        
        dialogMsg = "Export whole scene as..."
        dlg = wx.FileDialog(self,
                message = dialogMsg,
                style=wx.SAVE | wx.OVERWRITE_PROMPT,
                defaultFile = BAR_TEMPLATE['exportToVRML'] % self.currentStructureName,
                defaultDir = self.__defaultExportDir,
                wildcard=wildcard)
        
        # Invoke export function depending on 
        # selected file type
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.vtkapp.exportSceneByExt[filename[-4:]](filename)
#}

#{ Model generation

    def generatePipeline(self):
        """
        @return: VTK pipeline based on current GUI settings.
        
        Function iterates over all GUI elements representing particular VTK
        filters and extracts properties of each set of widget. Basing on all
        those settings, VTK pipeline os created.
        
        The problem is that whole pipeline consists of two kinds of filters:
        Those which have representation in GUI and those that do not have such
        representation. Filters without representation are not customizable and
        are loaded with their default values.
        """
        
        # Initialize empty pipeline
        pipeline = barPipeline()
        
        # Enumerate ell elements from generic pipeline. If given filter is
        # marked as 'displayable', its configuration is loaded from GUI.
        # Otherwise, default filter is appended with its default properties.
        for (i, pipelineElement) in enumerate(VTK_PIPELINE):
            if pipelineElement in DISPLAYABLE:
                pipeline.append(self.panel.pipeListDict[pipelineElement.cls.__name__].getPipelineElement())
            else:
                pipeline.append(VTK_PIPELINE[i])
        return pipeline
    
    def __generateSubmodel(self, submodels):
        """
        Recursively generates models starting from C{parenModel}. Structure is
        reconstructed and becomes available on the hierarchy tree as contex
        model.
        
        @type  submodels: C{List}
        @param submodels: List of first-level descendants (first level
        children). In following form:
        C{((parName,parFullName,parId),((chN,chFN,chId),...))}
        
        @return: None
        """
        props = self.structureSelectionTab.getReconstructionProperties()
        for item in submodels:
            groupName = item[0][0]
            
            # Generate the parent itself
            if self.generateModel(groupName, props['xyres'], props['zres']):
                
                # Cache the reconstruciton
                self.__savePolyDataModel(groupName)
                
                # 'Turn on' contex model on the structures tree
                self.structureTree.setContextSelecttion(groupName, True)
                self.__loadContextActor(groupName)
                
                # If given model has children - reconstruct them also
                if len(item) > 1:
                    self.__generateSubmodel(item[1])
                else:
                    print item
    
    def generateSubstructures(self, rootGroupName, depth = 1):
        """
        Function performing all operations related to substructure generation.

            1. Clearing scene, removing reconstructed structure as well as all
               context actors.
            2. Extracting the structures tree from the index holder down to
               given depth
            3. Generating submodels basing on extracted structures tree
        
        @type  rootGroupName: C{str}
        @param rootGroupName: name of root structure
        
        @type  depth: C{int}
        @param depth: Level down to which reconstructions would be generated.
        
        @return: None
        """
        self.vtkapp.clearScene()
        self.structureTree.deselectAllContextModels()
        
        treeData = self.sh.ih.getHierarchyTree(rootGroupName, depth)
        if len(treeData) > 1:
            # has substructures
            self.__generateSubmodel(treeData[1])
     
    def generateModel(self, structureName, coronalPlaneRes, saggitalAxisRes):
        """
        Generate model of given, single structure. At first volume is
        reconstructed from slides then volume is processed using vtk pipeline.
        After succeful reconsrtuction, name of the structure is stored in
        C{self.currentStructureName}.
        
        @type  structureName: C{str}
        @param structureName: Name of structure to reconsruct
        
        @type  coronalPlaneRes: C{float}
        @param coronalPlaneRes: resolution in coronal plane [mm]
        
        @type  saggitalAxisRes: C{float}
        @param saggitalAxisRes: resolution along anterior-posterior axis [mm]
        
        @rtype: C{Bool}
        @return: True, if everything is ok.
        """
        # Handling not defined structures
        if not type(self.sh.getSlidesSpan(structureName)) == type(("",)):
            return False
        
        self.sh.handleAllModelGeneration(\
                structureName, coronalPlaneRes, saggitalAxisRes) 
        
        self.sh.StructVol.prepareVolume()

        # Get colour of the structure
        ct = self.getStructureColor(structureName)
        
        # create a backup of last created volume
        self.__lastGeneratedModel = [self.sh.StructVol, ct]
       
        self.vtkapp.pipeline = self.generatePipeline()
        self.vtkapp.setReconstructionSource(*self.__lastGeneratedModel)
        
        # Display ModelPrewiev window and refresh preview.
        self.mainWindowNotebookTab.SetSelection(0)
        self.vtkapp.updateRenderWindow()
        
        # Set current structure name which allows exporting, caching and saving
        self.currentStructureName = structureName
        
        # Just to be sure that everything went ok.
        return True
    
    def getStructureColor(self, structureName, rgb = False):
        ct = HTMLColorToRGB(self.sh.ih.colorMapping[structureName])
        
        if ct[0] == ct[1] == ct[2] == 119:
            ct = map(lambda x: random.randint(0, 255), [0,0,0])

        if not rgb:
            ct = map(lambda x: float(x)/255, ct)
        return ct

#}

#{ Menu bindings
    def __setMenuAboutCAFEnables(self, status):
        """
        @type  status: boolean
        @param status: Desired status of the menu.
        
        Method sets status of Atlas -> About current dataset menu to C{status}.
        """
        
        # Select menubar, find proper menu element using its label and set
        # status
        menuBar = self.GetMenuBar()
        aboutMenuItem = menuBar.FindMenuItem("Atlas", 'About current dataset')
        menuBar.Enable(aboutMenuItem, status)
    
    def menuData(self):
        """
        Provides data basing on which menubar is created.
        
        @return: (tuple) Nested tuple containing data for menubar creation.
        Single tuple contains (Name of the menu, Tooltip displayed in statusbar,
        and method binded to particular menu).
        """
        return (("&Atlas",
                    ("&Open\tctrl-o", "Open CAF dataset", self.OnAtlasOpen),
                    ("&Close\tctrl-d", "Close current dataset", self.OnAtlasClose),
                    ("&Reload\tctrl-r", "Reload currently loaded dataset", self.OnAtlasReload),
                    ("", "", ""),
                    ("&About current dataset",
                        "Displays information about currently loaded CAF dataset",
                        self.OnAtlasInfo),
                    ("", "", ""),
                    ("E&xit\talt-f4", "Exit", self.OnAtlasExit)),
                ("&Edit",
                    ("Save &Model\tctrl-s",
                        "Cache currently reconsturcted model",
                        self.OnSaveModelAsPolyMesh),
                    ("Export model as volumetric dataset",
                        "Export model as volumetric dataset (vtk structured grid)",
                        self.OnSetExportAsVolume),
                    ("Export whole scene\tctrl-alt-s",
                        "Export current scene into file",
                        self.OnSetExportRenderWindow),
                    ("", "", ""),
                    ("Set cache directory\tins",
                        "Set default export directory.",
                        self.OnSetDefaultDir)
                    ),
                ("&Help",
                    ("&User manual", "Displays help", self.OnHelpHelp),
                    ("&About", "Displays about widow", self.OnHelpAbout)))
    
    def createMenuBar(self):
        """
        Creates menu bar.
        """
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)
        
        # On startup 'about CAF dataset menu item has to be disabled:
        # So we need to find that item and disable it:
        self.__setMenuAboutCAFEnables(False)
    
    def createMenu(self, menuData):
        """
        Creates single menu item basing on provided C{menuData}.
        
        @type  menuData: [(str, str, function), ... ]
        @param menuData: tuple containing data for creatring menu
        
        @rtype: C{wx.Menu} obj.
        @return: menu item.
        """
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menuData:
            if not eachLabel:
                # If menu data has no label ot means that given menu item is
                # intended to be a separator.
                menu.AppendSeparator()
                continue
            if eachLabel[0:2] == "--":
                # Menus with label starting from '--' are radio button menus
                menu.AppendRadioItem(-1, eachLabel[2:], eachStatus)
            else:
                # Menu items with regular labels are regular menus.
                menuItem = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu
    
    def OnAtlasOpen(self, event):
        """
        Interface for opening CAF dataset.
        """
        atlasDir = os.path.dirname(self.__getAtlasFilename())
        self.__loadAtlas(atlasDir)
    
    def OnAtlasClose(self, event):
        """
        Interface for closing CAF dataset.
        """
        self.__closeAtlas()
    
    def OnAtlasReload(self, event):
        """
        Interface for reloading currently loaded CAF dataset.
        """
        self.__reloadAtlas()
    
    def OnAtlasExit(self, event):
        """
        Interface for closing the software.
        """
        self.Close()
    
    def OnHelpHelp(self, event):
        """
        Interface for launching web browser with 3dBAR website.
        """
        os.system(BAR_HELP_WEBSITE_URL);
    
    def OnHelpAbout(self, event):
        """
        Interface for launching web browser with 3bBAR website.
        """
        os.system(BAR_HELP_ABOUT_URL);
    
    def OnAtlasInfo(self, event):
        """
        Displays frame with information about currently loaded CAF dataset.
        If no CAF dataset is loaded info frame is not loaded.
        """
        
        if (not self.__atlasDirectory) or (not self.__defaultExportDir):
            print "Cannot display atlas info. No atlas loaded."
        else:
            aboutDatasetFrame = SketchAbout(self, self.sh)
            aboutDatasetFrame.ShowModal()
            aboutDatasetFrame.Destroy()
    
    def OnSaveModelAsPolyMesh(self, event):
        """
        Interface for exporting given reconstruction to vtkPolyDataMesh.
        """
        # Only when CAF dataset is loaded and reconstruction performed.
        if (not self.__atlasDirectory) or (not self.__defaultExportDir):
            dlg = wx.MessageDialog(None,
                    BAR_GUI_NODEFEXPDIR,
                    BAR_GUI_MSGBOX_TITLE, wx.OK | wx.ICON_QUESTION)
            retCode = dlg.ShowModal()
            return
        
        # If everything is ok, save the model.
        self.__savePolyDataModel()
    
    def OnRefreshModel(self, event):
        """
        Interface for refreshing the reconstruction.
        """
        self.vtkapp.pipeline = self.generatePipeline()
        
        # restore source volume
        self.vtkapp.setReconstructionSource(*self.__lastGeneratedModel)
        
        self.vtkapp.updateRenderWindow(resetCamera = False)
    
    def OnClearScene(self, event):
        """
        Interface for clearing the scene.
        """
        self.vtkapp.clearScene()
        self.structureTree.deselectAllContextModels()
        # clear also the source volume to prevent artefact appearance in exported scene
        self.vtkapp.clearVolume()
    
    def OnSetDefaultDir(self, event):
        """
        Interface for setting reconstruction directory
        """
        self.__selectDefaultOutputDir()
    
    def OnSetExportRenderWindow(self, event):
        """
        Interface for exporting render window
        """
        self.__exportRenderWindow()
    
    def OnSetExportAsVolume(self, event):
        """
        Interface for exporting currently reconstructed structure as volumetric
        dataset.
        """
        self.__exportVolumetricDataset()

#}

class SketchAbout(wx.Dialog):
    """
    "About current dataset" frame.
    """
   
    text = '''
<html>
<body bgcolor="#bbbbbb">

<p><b>%s</b></p>
<p>%s</p>

<p>Corresponding author: %s (<a href="mailto:%s">%s</a>)</p>

<small>Compilation date: %s</small>
</body>
</html>
'''
    def __init__(self, parent, structureHolder):
            wx.Dialog.__init__(self, parent, -1,
                              'About CAF dataset',
                              size=(440, 400) )
           
            fields = ['CAFName','CAFComment','CAFCreator','CAFCreatorEmail',\
                    'CAFCreatorEmail','CAFCompilationTime']
            infoStrings =\
                    tuple(map(lambda x: structureHolder.ih.properties[x].value, fields))
            
            htmlText = self.text % infoStrings
            
            html = wx.html.HtmlWindow(self)
            html.SetPage(htmlText)
            button = wx.Button(self, wx.ID_OK, "Close")
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(html, 1, wx.EXPAND|wx.ALL, 5)
            sizer.Add(button, 0, wx.ALIGN_CENTER|wx.ALL, 5)
            
            self.SetSizer(sizer)
            self.Layout()

def flatten(x):
    """
    @type  x: iterable sequence
    @param x: sequence to flat
    
    @return: (list). Flattened list. Read description for firther information.
    
    flatten(sequence) -> list
    
    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    
    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    
    """
    
    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

    
class App(wx.App):
    def OnInit(self):
        self.vtkapp = barReconstructionModule()
        self.frame =  mainGuiFrame(self.vtkapp)
        self.frame.Maximize()
        self.SetTopWindow(self.frame)
        return True

if __name__=='__main__':
    app=App(redirect = False)
    app.MainLoop()
