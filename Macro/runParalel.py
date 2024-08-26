#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import subprocess
import PySide
from PySide import QtGui
from PySide import QtCore
import dexcsCfdTools

import pythonVerCheck
import pyDexcsSwakSubset
import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()


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
    #title =  "#!/bin/sh\n"
    title =  ""

    configDict = pyDexcsSwakSubset.readConfigTreeFoam()
    envOpenFOAMFix = configDict["bashrcFOAM"]
    configDict = pyDexcsSwakSubset.readConfigDexcs()
    envTreeFoam = "~/.TreeFoamUser"
    envOpenFOAMFix = envOpenFOAMFix.replace('$TreeFoamUserPath',envTreeFoam)
    envOpenFOAMFix = os.path.expanduser(envOpenFOAMFix)
    #envOpenFOAMFix = envOpenFOAMFix.replace('$TreeFoamUserPath',os.getenv("HOME")+'/.TreeFoamUser')
    #envSet = "source " + envOpenFOAMFix + '\n'
    envSet = ". " + envOpenFOAMFix + '\n'

    envSet = envSet + ". ~/.local/share/FreeCAD/Mod/dexcsCfdOF/Macro/runTreefoamSubset\n"
    configDict = pyDexcsSwakSubset.readConfigDexcs()
    envSwak = "export dexcsSwakPath=" + os.path.expanduser(configDict["dexcs"]) + "/SWAK\nexport PYTHONPATH=$dexcsSwakPath:$PYTHONPATH\n"
    if TreeFoamVersion.startswith('3') :
        solverSet = os.path.expanduser("~") + "/.local/share/FreeCAD/Mod/dexcsCfdOF/Macro/runParallelDexcs.py " + caseName
    else :
        solverSet = "runParallelDialog.py " + caseName
    sleep = ""
    cont = title + envSet + envSwak + solverSet  + sleep
    f=open("./run","w")
    f.write(cont)
    f.close()
    #実行権付与
    os.system("chmod a+x run")

    env = QtCore.QProcessEnvironment.systemEnvironment()

    if env.contains("APPIMAGE"):
        #message = (_("this FreeCAD is AppImage version.\n  some function of runParallelDialog doesen't work.\n if you want utilize the function, use normal TreeFoam menu.")) 
        #ans = QtGui.QMessageBox.critical(None, _("AppImage Warning"), message, QtGui.QMessageBox.Yes)
        dexcsCfdTools.removeAppimageEnvironment(env)

        cmd = dexcsCfdTools.makeRunCommand('./run', modelDir, source_env=False)
        FreeCAD.Console.PrintMessage("Solver run command: " + ' '.join(cmd) + "\n")
        env = QtCore.QProcessEnvironment.systemEnvironment()
        dexcsCfdTools.removeAppimageEnvironment(env)
        process = QtCore.QProcess()
        process.setProcessEnvironment(env)
        working_dir = modelDir
        if working_dir:
            process.setWorkingDirectory(working_dir)
        # if platform.system() == "Windows":
        #     # Run through a wrapper process to allow clean termination
        #     cmd = [os.path.join(FreeCAD.getHomePath(), "bin", "python.exe"),
        #            '-u',  # Prevent python from buffering stdout
        #            os.path.join(os.path.dirname(__file__), "WindowsRunWrapper.py")] + cmd
        # print("Raw command: ", cmd)
        process.start(cmd[0], cmd[1:])

    else:

        #実行
        #comm = "xfce4-terminal --execute ./run"
        comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
        #subprocess.call(comm .strip().split(" "))
        os.system(comm)

else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass
