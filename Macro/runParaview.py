#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import PySide
from PySide import QtGui
from PySide import QtCore
import dexcsCfdTools

import pythonVerCheck
import pyDexcsSwakSubset
import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

    CaseFilePath=modelDir
    os.chdir(CaseFilePath)
    caseName = CaseFilePath
    prefs = dexcsCfdTools.getPreferencesLocation()
    ParaviewPath = FreeCAD.ParamGet(prefs).GetString("ParaviewPath", "")
    title =  "#!/bin/bash\n"
    cont = title + "export LD_LIBRARY_PATH=''\n"
    cont = cont + "a=`pwd`\n"
    cont = cont + "openName=`basename $a`.foam\n"
    cont = cont + "touch $openName\n"
    cont = cont + ParaviewPath + " $openName\n"
    cont = cont + "rm $openName\n"
    f=open("./run","w")
    f.write(cont)
    f.close()
    #実行権付与
    os.system("chmod a+x run")
    #実行
    cmd = dexcsCfdTools.makeRunCommand('./run', modelDir, source_env=False)
    FreeCAD.Console.PrintMessage("Solver run command: " + ' '.join(cmd) + "\n")
    env = QtCore.QProcessEnvironment.systemEnvironment()
    dexcsCfdTools.removeAppimageEnvironment(env)
    process = QtCore.QProcess()
    process.setProcessEnvironment(env)
    working_dir = modelDir
    if working_dir:
        process.setWorkingDirectory(working_dir)
    process.start(cmd[0], cmd[1:])

else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass
