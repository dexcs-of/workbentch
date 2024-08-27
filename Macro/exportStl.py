import FreeCAD

import os
#import codecs
#import ntpath
import tempfile
from PySide2.QtWidgets import *
import pythonVerCheck
import Mesh
#import MeshPart

import draftutils

maxDeviation = draftutils.params.get_param( "MaxDeviationExport", "Mod/Mesh")
str_maxDeviation = str(maxDeviation)
doc = App.ActiveDocument
name = os.path.splitext(doc.FileName)[0]
modelDir = os.path.dirname(doc.FileName)
QI_Title = _("Maximum STL mesh deviation")
QI_Message = _("set Maximum STL mesh deviation \n ")
QI_Message += _("(You can make it smaller as many times as you like\n")
QI_Message += _(" but, change it to a larger value the first time only)")
double, ok = QInputDialog().getDouble(None, QI_Title, QI_Message,maxDeviation, 0, 10000, 3 )

if ok and double:
   print(str(double))
   draftutils.params.set_param( "MaxDeviationExport",double, "Mod/Mesh")

if maxDeviation < double:
	#print("warning")
	QTitle = _("set Maximum mesh deviation")
	QMessage = _("You can only change it to a larger value the first time after starting FreeCAD.\n")
	QMessage += _("If you want to reflect the changes after the second time, please restart FreeCAD.")
	QMessageBox.information(None, QTitle, QMessage)

#mesh = Mesh.Mesh()

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
	    #mesh.export(__objs__,file)
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

