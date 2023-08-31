#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import subprocess
import glob
import PySide
from PySide import QtGui
import re
from PySide import QtCore
import dexcsCfdTools

import pythonVerCheck
import pyDexcsSwakSubset
import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()


def getSolver():
    solver = ""
    fileName = "./system/controlDict"
    if glob.glob(fileName) != "":
        f=open("./system/controlDict")
        for line in f.readlines():
            item = line.split()
            if len(item)>0:
                if item[0] == "application":
                    solver = line.split()[1]
                    break
    return solver


os.chdir(modelDir)

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):


    solver = getSolver().replace(';','')

    if solver == "":
        message = (_("can't recognize solver name.\n  check current directory."))
        ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)
    else:
        #os.system(solver)
        caseName = modelDir
        title =  "#!/bin/bash\n"
        #envSet = ". /opt/OpenFOAM/OpenFOAM-v1906/etc/bashrc\n"
        #envSet = "source " + os.environ["HOME"] + "/.TreeFoamUser/app/bashrc-FOAM-DEXCS\n"
        configDict = pyDexcsSwakSubset.readConfigTreeFoam()
        envOpenFOAMFix = configDict["bashrcFOAM"]
        configDict = pyDexcsSwakSubset.readConfigDexcs()
        envTreeFoam = configDict["TreeFoam"]
        envOpenFOAMFix = envOpenFOAMFix.replace('$TreeFoamUserPath',envTreeFoam)
        envOpenFOAMFix = os.path.expanduser(envOpenFOAMFix)
        #envOpenFOAMFix = envOpenFOAMFix.replace('$TreeFoamUserPath',os.getenv("HOME")+'/.TreeFoamUser')
        envSet = "source " + envOpenFOAMFix + '\n'
        solverSet = solver + " | tee solve.log"
        cont = title + envSet + solverSet
        f=open("./run","w")
        f.write(cont)
        f.close()
        os.system("chmod a+x run")
        #実行
        env = QtCore.QProcessEnvironment.systemEnvironment()
        if env.contains("APPIMAGE"):
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
        else:
            comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
            #subprocess.call(comm.strip().split(" "))
            os.system(comm)

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass


