#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import re
import tempfile
import gettext
import PySide
from PySide import QtGui

import pythonVerCheck

doc = App.ActiveDocument
name = os.path.splitext(doc.FileName)[0]
modelDir = os.path.dirname(doc.FileName)

#モデルファイル置き場がケースファイルの場所（.CaseFileDictで指定）と異なる場合
caseFileDict = modelDir + "/.CaseFileDict"
if os.path.isfile(caseFileDict) == True:
    f = open(caseFileDict)
    modelDir = f.read()
    f.close()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):


	(fileName, selectedFilter) = QtGui.QFileDialog.getOpenFileName( None, _("Select a JGP project file"),modelDir + "/system")


	name = os.path.splitext(fileName)[0]

	if name != "":

	    f = open(fileName,"r")
	    lines = f.readlines()
	    f.close()

	    outputFile=open(name+'.org','w')

	    outputFile.writelines(lines)
	    outputFile.close()

	    outputFile=open(fileName,'w')

	    for line in lines:
	    	lineConv = line
	    	f1 = line.find('<filename>')
	    	f2 = line.find('/postProcessing/')
	    	if f1 > -1 and f2 > -1 :
	    	    lineConv = line[0:f1+10] + modelDir + line[f2:-1]
	    	    #print(line)
	    	    #print(f1, f2, lineConv)
	    	outputFile.write(lineConv)
	    outputFile.close()

	    f = open("/opt/jgp/.JGP", "r")
	    lines = f.readlines()
	    f.close()

	    outputFile = open("/opt/jgp/.JGP", 'w')
	    for i in range(len(lines)):
	    	line = lines[i]
	    	outputFile.write(line)
	    	if i == 3 :
	    	    outputFile.write('        <project>\n')
	    	    outputFile.write('            <filename>' + fileName + '</filename>\n')
	    	    outputFile.write('        </project>\n')
	    outputFile.close()

	    message = fileName + _(" has been adjusted for the included caseName.")
	    QtGui.QMessageBox.information(None, _("Adjust a JGP project file"), message)

	cont = "/opt/jgp/startupJgp"
	f=open("./run","w")
	f.write(cont)
	f.close()
	#実行権付与
	os.system("chmod a+x run")
	#実行
	comm = "xfce4-terminal --execute ./run"
	#comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
	#subprocess.call(comm .strip().split(" "))
	os.system(comm)
else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

