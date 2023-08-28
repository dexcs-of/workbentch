#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import glob
import sys
from PySide import QtGui
from PySide2 import QtCore
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
   
os.chdir(modelDir)

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder):

    envSet = ". " + os.path.expanduser("~") + "/.FreeCAD/Mod/dexcsCfdOF/Macro/runTreefoamSubset;"
    wdir = modelDir + "/system"
    title = _("edit Dict File")
    img = "oneFile"
    mess = _("select edit Dict file.\n\nDict file is in system folder.")
    editDir = wdir
    job = "editDictFile"
    # properties File の選択と編集
    #self.showSelectFolderFilesDialog(job, title, img, mess, editDir)
    if TreeFoamVersion.startswith('3') :
        cont  =  envSet + "selectFolderFilesDialog.py " + job +  " " + modelDir +  " system"
    else :
        cont  =  envSet + "selectFolderFilesDialog.py " + job + " '" + title + "' " + img
        cont += " '" + mess + "' " + editDir

    if sys.version_info.major == 2 : 
        cont = cont.encode('utf-8') 

    f=open("./run","w")
    f.write(cont)
    f.close()
    #実行権付与
    os.system("chmod a+x run")
    #実行

    env = QtCore.QProcessEnvironment.systemEnvironment()
    if env.contains("APPIMAGE"):
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
        comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
        os.system(comm.encode("utf-8"))

else:
    message = (_("there is no system folder.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass
