# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import re
import tempfile
import PySide
from PySide import QtGui

import pythonVerCheck
import dexcsCfdTools

active_analysis = dexcsCfdTools.getActiveAnalysis()
if active_analysis:
    modelDir =  active_analysis.OutputPath
else:    
    doc = App.ActiveDocument
    name = os.path.splitext(doc.FileName)[0]
    modelDir = os.path.dirname(doc.FileName)
    caseFileDict = modelDir + "/.CaseFileDict"
    if os.path.isfile(caseFileDict) == True:
        f = open(caseFileDict)
        modelDir = f.read()
        f.close()
    else:
        output_dir = dexcsCfdTools.getDefaultOutputPath()
        if os.path.exists(output_dir) == True:
            modelDir = output_dir
        else:
            modelDir = os.path.dirname(doc.FileName)
return modelDir