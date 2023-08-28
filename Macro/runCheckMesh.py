#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import glob
import PySide
from PySide import QtGui

import pythonVerCheck
import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):


	solver = 'checkMesh'

	if solver == "":
	    message = (_("can't recognize solver name.\n  check current directory."))
	    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)
	else:
	    #os.system(solver)
	    caseName = modelDir
	    title =  "#!/bin/bash\n"
	    envSet = ". /opt/OpenFOAM/OpenFOAM-v1906/etc/bashrc\n"
	    solverSet = solver + " | tee solve.log"
	    cont = title + envSet + solverSet
	    f=open("./run","w")
	    f.write(cont)
	    f.close()
	    #実行権付与
	    os.system("chmod a+x run")
	    #実行
	    #comm = "xfce4-terminal --execute ./run"
	    comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
	    #subprocess.call(comm .strip().split(" "))
	    os.system(comm)

else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)



