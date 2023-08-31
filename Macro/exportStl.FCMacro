import FreeCAD
import Mesh
import os
import tempfile
from PySide.QtCore import *
from PySide.QtGui import *

import pythonVerCheck

doc = App.ActiveDocument
name = os.path.splitext(doc.FileName)[0]
modelDir = os.path.dirname(doc.FileName)

(fileName, selectedFilter) = QFileDialog.getSaveFileName( None, _("save name as stl"),modelDir)

name = os.path.splitext(fileName)[0]

if name != "":

	outputFile=open(name+'.stl','w')
	for obj in doc.Objects:
	  if obj.ViewObject.Visibility:
	    __objs__=[]
	    if obj.ViewObject.Visibility:
	    	__objs__.append(obj)
	    file=name+obj.Label+'.ast'
	    Mesh.export(__objs__,file)
	    importFile = open(file,'r')
	    temp = importFile.readlines()
	    for line in temp:
	    	if 'endsolid' in line:
	    		outputFile.write('endsolid ' + obj.Label + '\n')
	    	elif 'solid' in line:
	    		outputFile.write('solid ' + obj.Label + '\n')
	    	else:
	    		outputFile.write(line)
	    importFile.close
	    os.remove(file)
	    #os.rename(name+'.ast', name+'.stl')
	outputFile.close
	QMessageBox.information(None, _("exportedStlFile"), name+'.stl')

