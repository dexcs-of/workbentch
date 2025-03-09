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
import pyDexcsSwakSubset

import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

#TreeFoamVersionFile = os.getenv("TreeFoamPath") + "TreeFoamVersion"
TreeFoamVersionFile = "/opt/TreeFoam/TreeFoamVersion"
#print(TreeFoamVersionFile)
if os.path.isfile(TreeFoamVersionFile) == True:
    f = open(TreeFoamVersionFile)
    TreeFoamVersion = f.read()
    f.close()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

    CaseFilePath=modelDir
    #print(CaseFilePath)
    os.chdir(CaseFilePath)
    #geditの実行ファイル作成
    caseName = CaseFilePath
    title =  ""
    envSet = ". " + os.path.expanduser("~") + "/.local/share/FreeCAD/Mod/dexcsCfdOF/Macro/runTreefoamSubset;"
    configDict = pyDexcsSwakSubset.readConfigDexcs()
    envSwak = "export dexcsSwakPath=" + os.path.expanduser(configDict["dexcs"]) + "/SWAK\nexport PYTHONPATH=$dexcsSwakPath:$PYTHONPATH\n"
    envSwak = envSwak + "export GDK_BACKEND=x11\n"

    if TreeFoamVersion.startswith('3') :
        # solverSet = os.path.expanduser("~") + "/.FreeCAD/gridEditorDexcs.py " +caseName
        # timeFolder = " 0 constant/polyMesh\n"
        # sleep = ""
        # cont = title + envSet + envSwak + solverSet + timeFolder + sleep
        nTreeFoam = "-1"        #ここから起動するgridEditorのnTreeFoamは「-1」
        comm = "editSnappyHexMeshDialog.py " + caseName + " " + caseName + "/model &"
        cont = title + envSet + envSwak + comm

    else :
        solverSet = "editSnappyHexMeshDialog.py " +caseName + " " + caseName + "/model"
        timeFolder = " 0 constant/polyMesh\n"
        sleep = ""
        cont = title + envSet + envSwak + solverSet + timeFolder + sleep

    f=open("./run","w")
    f.write(cont)
    f.close()
    #実行権付与
    os.system("chmod a+x run")
    #実行

    env = QtCore.QProcessEnvironment.systemEnvironment()
    if env.contains("APPIMAGE"):
        cmd = dexcsCfdTools.makeRunCommand('./run', modelDir, source_env=False)
        #print('cmd = ', cmd)
        #FreeCAD.Console.PrintMessage("Solver run command: " + ' '.join(cmd) + "\n")
        env = QtCore.QProcessEnvironment.systemEnvironment()
        #print('env = ', env)
        dexcsCfdTools.removeAppimageEnvironment(env)
        process = QtCore.QProcess()
        process.setProcessEnvironment(env)
        working_dir = modelDir
        if working_dir:
            process.setWorkingDirectory(working_dir)
        process.start(cmd[0], cmd[1:])
    else:
        comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
        os.system(comm.encode("utf-8"))

else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass

