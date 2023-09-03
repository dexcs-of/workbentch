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

#doc = App.ActiveDocument
#name = os.path.splitext(doc.FileName)[0]
#modelDir = os.path.dirname(doc.FileName)
import dexcsFunctions
modelDir = dexcsFunctions.getCaseFileName()

#TreeFoamVersionFile = os.getenv("TreeFoamPath") + "TreeFoamVersion"
TreeFoamVersionFile = "/opt/TreeFoam/TreeFoamVersion"
#print(TreeFoamVersionFile)
if os.path.isfile(TreeFoamVersionFile) == True:
    f = open(TreeFoamVersionFile)
    TreeFoamVersion = f.read()
    f.close()

#モデルファイル置き場がケースファイルの場所（.CaseFileDictで指定）と異なる場合
# caseFileDict = modelDir + "/.CaseFileDict"
# if os.path.isfile(caseFileDict) == True:
#     f = open(caseFileDict)
#     modelDir = f.read()
#     f.close()

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
#comm = "xfce4-terminal --execute ./run"
#comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
#subprocess.call(comm .strip().split(" "))

#実行
#if TreeFoamVersion.startswith('3') :
#    message = (_("sorry for TreeFoam Ver.3*, \n  this module cannnot activate correctly.\n You need to use this module from TreeFoam main window."))
#    ans = QtGui.QMessageBox.critical(None, _("check TreeFoam version"), message, QtGui.QMessageBox.Yes)
#    os.system(comm)
#else :
#    os.system(comm)
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
