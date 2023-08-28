#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os

doc = App.ActiveDocument
name = os.path.splitext(doc.FileName)[0]
modelDir = os.path.dirname(doc.FileName)

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
envSet = ". " + os.path.expanduser("~") + "/.FreeCAD/runTreefoamSubset;"
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
#comm = "xfce4-terminal --execute bash ./run"
comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
#subprocess.call(comm .strip().split(" "))
os.system(comm)
