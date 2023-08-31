# -*- coding: utf-8 -*-

import os
import PySide
from PySide import QtGui

import pythonVerCheck
import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

	message = _("the case file is ") + modelDir + _(".")
	message = message + _("\n To change the analysis case file, set the OutputPath property of Analysis container and then write meshCase on the dexcsTaskPanelCfdMesh,\n or click the Case button in the cfMesh setting macro and specify the change destination.")
	QtGui.QMessageBox.information(None, _("Confirmation of analysis case file"), message)

else:
    message = _("the case file is ") + modelDir + _(".")
    message = message + "\n\n" + _("But, ")
    message = message + (_("this folder is not case folder of OpenFOAM.\n   check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

