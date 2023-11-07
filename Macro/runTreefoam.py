#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import pyDexcsSwakSubset
import dexcsCfdTools
from PySide2 import QtCore
from PySide import QtGui
import pythonVerCheck

import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

workDir=modelDir

configDict = pyDexcsSwakSubset.readConfigDexcs()
envTreeFoam = "~/.TreeFoamUser"

configTreeFoamFile = os.path.expanduser(envTreeFoam) + "/configTreeFoam"
f = open(configTreeFoamFile)
x = f.read()
f.close()

configTreeFoamFileTemp = os.path.expanduser(envTreeFoam) + "/configTreeFoam"
g = open(configTreeFoamFileTemp,'w')
y = x.split('\n')
keyWord = "workDir"

for j in range(len(y)):
    s = y[j].find(keyWord)
    if s > -1:
        g.write("workDir\t"+workDir+"\n") 
    else :
        g.write(y[j]+"\n")
g.close()

trfCmd = "/opt/TreeFoam/treefoam"

env = QtCore.QProcessEnvironment.systemEnvironment()

if env.contains("APPIMAGE"):
    message = (_("this FreeCAD is AppImage version.\n  some function of TreeFoam doesen't work.\n if you want utilize the function, use normal TreeFoam clicked by dock-launcher button.")) 
    ans = QtGui.QMessageBox.critical(None, _("AppImage Warning"), message, QtGui.QMessageBox.Yes)
    dexcsCfdTools.removeAppimageEnvironment(env)
    process = QtCore.QProcess()
    process.setProcessEnvironment(env)
    working_dir = modelDir
    if working_dir:
        process.setWorkingDirectory(working_dir)
    process.start(trfCmd)

else:
    os.system(trfCmd)

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass
