#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
from PySide import QtGui
from PySide import QtCore
import dexcsCfdTools

import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

#モデルファイル置き場がケースファイルの場所（.CaseFileDictで指定）と異なる場合
caseFileDict = modelDir + "/.CaseFileDict"
if os.path.isfile(caseFileDict) == True:
    f = open(caseFileDict)
    modelDir = f.read()
    f.close()


CaseFilePath=modelDir
#print(CaseFilePath)
os.chdir(CaseFilePath)
#geditの実行ファイル作成
caseName = CaseFilePath
title =  ""
#envSet = ". ~/.FreeCAD/runTreefoamSubset\n"
envSet = ". " + os.path.expanduser("~") + "/.FreeCAD/Mod/DexcsCfdOF/Macro/runTreefoamSubset;"
solverSet = "gridEditor.py " +caseName
timeFolder = " 0 constant/polyMesh\n"
sleep = ""
cont = title + envSet + solverSet + timeFolder + sleep
f=open("./run","w")
f.write(cont)
f.close()
#実行権付与
os.system("chmod a+x run")
#実行
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
