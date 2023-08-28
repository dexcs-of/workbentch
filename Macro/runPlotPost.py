#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import re
import tempfile
import gettext
import PySide
from PySide import QtGui
import math

import pythonVerCheck
from dexcsCfdPostPlot import PostPlot
from collections import OrderedDict
import dexcsPlotPost
import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

    (fileName, selectedFilter) = QtGui.QFileDialog.getOpenFileName( None,
         _("Select a postProcess file"),modelDir + "/system" , filter="dexcs plot Files (*.dplt)")

    name = os.path.splitext(fileName)[0]

    if name != "":


        f = open(fileName,"r")
        lines = f.readlines()
        f.close()
        print("postProcessing=",f.name)

        dexcsPlotPost.dexcsPlotPost(modelDir,lines)
        #dexcsPlot.dexcs_plot(modelDir,lines)


    else:
        message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
        ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

