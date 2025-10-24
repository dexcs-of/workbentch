#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import gettext
import PySide
from PySide import QtGui
from PySide import QtCore
import dexcsCfdTools
import pythonVerCheck

import dexcsFunctions
modelDir = dexcsFunctions.getCaseFileName()

#TreeFoamVersionFile = os.getenv("TreeFoamPath") + "TreeFoamVersion"
TreeFoamVersionFile = "/opt/TreeFoam/TreeFoamVersion"
#print(TreeFoamVersionFile)
if os.path.isfile(TreeFoamVersionFile) == True:
    f = open(TreeFoamVersionFile)
    TreeFoamVersion = f.read()
    f.close()

CaseFilePath=modelDir
#print(CaseFilePath)
os.chdir(CaseFilePath)
#geditの実行ファイル作成
caseName = CaseFilePath
title =  "#!/bin/bash\n"
envSet = ". ~/.local/share/FreeCAD/Mod/dexcsCfdOF/Macro/runTreefoamSubset\n"
if TreeFoamVersion.startswith('3') :
    solverSet = os.path.expanduser("~") + "/.local/share/FreeCAD/Mod/dexcsCfdOF/Macro/createAndChangeCaseDialogDexcs.py "  + CaseFilePath
else :
    solverSet = "createAndChangeCaseDialog.py "  + CaseFilePath
sleep = ""
cont = title + envSet + solverSet + sleep
f=open("./run","w")
f.write(cont)
f.close()
#実行権付与
os.system("chmod a+x run")
cmd = dexcsCfdTools.makeRunCommand('./run', modelDir, source_env=False)
print('cmd = ', cmd)
FreeCAD.Console.PrintMessage("Solver run command: " + ' '.join(cmd) + "\n")
env = QtCore.QProcessEnvironment.systemEnvironment()
print('env = ', env)
dexcsCfdTools.removeAppimageEnvironment(env)
process = QtCore.QProcess()
process.setProcessEnvironment(env)
working_dir = modelDir
if working_dir:
    process.setWorkingDirectory(working_dir)
process.start(cmd[0], cmd[1:])

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass
