#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import PySide
#from PySide import QtGui

import os
import pythonVerCheck
import FreeCAD

def ErrorDialog1(message):
    print (message)

def checkOpenFoamFileSystem(location):
        
        print (location)
        systemFolder = location + "/system"
        
        if not os.path.isdir(systemFolder):
            ErrorDialog1(_(u"systemフォルダが見つからないので、\nOpenFOAMのケースフォルダとして認識できません"))   
            return False
        elif not os.path.isdir(location + "/constant"):
            ErrorDialog1(_(u"constantフォルダが見つからないので、\nOpenFOAMのケースフォルダとして認識できません"))   
            return False
        elif not os.path.isfile(location + "/system/controlDict"):
            ErrorDialog1(_(u"system/controlDict が見つからないので、\nOpenFOAMのケースフォルダとして認識できません"))    
            return False
        else :
            return True

def readConfigTreeFoam():
    """ configTreeFoamの内容を読み取り、結果を辞書形式で返す。
    appの内容をconfigTreeFoamに合わせる
    辞書keys: language, logFile, OFversion, rootDir, workDir, bashrcFOAM,
    paraFoam, salomeMeca, CAD, editor, fileManager, Terminal, foamTerminal"""
    configDict = {
        "language": "",
        "logFile": "",
        "OFversion": "",
        "rootDir": "",
        "workDir": "",
        "bashrcFOAM": "",
        "paraFoam": "",
        "salomeMeca": "",
        "CAD": "",
        "editor": "",
        "fileManager": "",
        "Terminal": "",
        "TerminalRun": "",
        "foamTerminal": "",
        "foamTerminalRun": "",
        "office": ""
        }
    #fileName = os.getenv("TreeFoamUserPath") + os.sep + "configTreeFoam"
    fileName = os.getenv("HOME") + "/.TreeFoamUser/configTreeFoam"
    f = open(fileName); lines = f.readlines(); f.close()
    for line in lines:
        words = line.split()
        if len(words) > 1 and words[0][0] != "#":
            if words[0] in configDict.keys():
                configDict[words[0]] = " ".join(words[1:])
    
    return configDict

def readConfigDexcs():
    """ configDexcsの内容を読み取り、結果を辞書形式で返す。
    appの内容をconfigTreeFoamに合わせる
    辞書keys: CfmeshPath, TreefoamPath, DexcsPath"""

    prefs = "User parameter:BaseApp/Preferences/Mod/dexcsCfdOF"
    cfmesh_dir = FreeCAD.ParamGet(prefs).GetString("CfmeshPath", "")
    treefoam_dir = FreeCAD.ParamGet(prefs).GetString("TreefoamPath", "")
    dexcs_dir = FreeCAD.ParamGet(prefs).GetString("DexcsPath", "")
    configDict = {
        "cfMesh": cfmesh_dir,
        "TreeFoam": treefoam_dir,
        "dexcs": dexcs_dir
        }
    
    return configDict

