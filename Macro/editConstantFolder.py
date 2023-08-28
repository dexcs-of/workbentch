#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import glob
import sys
import PySide
from PySide import QtGui
from PySide import QtCore
import dexcsCfdTools
# if FreeCAD.GuiUp:
#     import FreeCADGui
#     from PySide import QtCore
#     from PySide import QtGui
#     from PySide.QtCore import Qt
#     from PySide.QtGui import QApplication

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
#print(TreeFoamVersion)
   
os.chdir(modelDir)

def getFoldersFiles(wdir):      #wdirは、絶対path
    folders = []
    files = []
    dirFiles = glob.glob(wdir + "/*")
    for name in dirFiles:
        if os.path.isdir(name) == True:
            folders.append(name.split("/")[-1])
        elif os.path.isfile(name) == True:
            files.append(name.split("/")[-1])
    folders.sort()
    files.sort()
    return [folders, files]

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(constantFolder):

    envSet = ". " + os.path.expanduser("~") + "/.FreeCAD/Mod/dexcsCfdOF/Macro/runTreefoamSubset;"
    wdir = modelDir + "/constant"
    [folders, files] = getFoldersFiles(wdir)
    if len(folders) >= 1:
        title = _("edit properties File.")
        img = "oneFile"
        mess = _("select to edit Properties file.\n\nProperties files are in ./constant folder.")
        editDir = wdir
        job = "editProperties"
        # properties File の選択と編集
        #self.showSelectFolderFilesDialog(job, title, img, mess, editDir)
        if TreeFoamVersion.startswith('3') :
            cont  =  envSet + "selectFolderFilesDialog.py " + job +  " " + modelDir +  " constant"
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

        env = QtCore.QProcessEnvironment.systemEnvironment()
        if env.contains("APPIMAGE"):
            cmd = dexcsCfdTools.makeRunCommand('./run', modelDir, source_env=False)
            env = QtCore.QProcessEnvironment.systemEnvironment()
            dexcsCfdTools.removeAppimageEnvironment(env)
            process = QtCore.QProcess()
            process.setProcessEnvironment(env)
            process.start(cmd[0], cmd[1:])
        else:
            #実行
            #comm = "xfce4-terminal --execute bash ./run"
            comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
            os.system(comm.encode("utf-8"))
    
    else:
        message = (_("there is no polyMesh folder in constant.\n  check current directory.")) 
        ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

else:
    message = (_("there is no constant folder.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

