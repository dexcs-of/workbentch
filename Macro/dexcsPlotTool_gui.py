#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tempfile
import gettext
from PySide import QtGui
from PySide2 import QtCore, QtWidgets
import dexcsPlotPost
import pythonVerCheck
import sys
from dexcsPlotTool_ui import Ui_DexcsPlotTool
import dexcsCfdTools


class gui(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(gui, self).__init__(parent)
        self.ui = Ui_DexcsPlotTool()
        self.ui.setupUi(self)
        #doc = App.ActiveDocument
        #modelDir = os.path.dirname(doc.FileName)
        import dexcsFunctions
        modelDir = dexcsFunctions.getCaseFileName()
        if modelDir == 'model_dir' :
            modelDir = '.'
        #modelDir = '.'
        
        optionOutputPath = dexcsCfdTools.getOptionOutputPath()
        if optionOutputPath :
            #モデルファイル置き場がケースファイルの場所（.CaseFileDictで指定）と異なる場合
            caseFileDict = modelDir + "/.CaseFileDict"
            if os.path.isfile(caseFileDict) == True:
                f = open(caseFileDict)
                modelDir = f.read()
                f.close()
        else :
            modelDir = '.'


        systemFolder = modelDir + "/system"
        constantFolder = modelDir + "/constant"
        #systemFolder = "./system"
        #constantFolder =  "./constant"

        if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

            self.modelDir = modelDir
            dpltList=[]
            #for list in os.listdir(modelDir+"/system/"):
            for list in os.listdir("./system/"):
                ext = os.path.splitext(list)
                if ext[1] == ".dplt":
                    dpltList.append(list)

            self.model = QtCore.QStringListModel()
            self.model.setStringList(dpltList)
            self.ui.listView.setModel(self.model)
            self.ui.listView.clicked.connect(self.listClicked)
            self.ui.listView.doubleClicked.connect(self.listDoubleClicked)
        else:
            message = (_("this folder is not case folder of OpenFOAM.\n  check current directory.")) + modelDir
            ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)


    def listClicked(self, index):
        print("listClicked",index.data())
        self.dpltFile = index.data()

    def listDoubleClicked(self, index):
        print("listDoubleClicked",index.data())
        self.dpltFile = index.data()
        self.run_plot()

    def run_cancel(self):
        print("cancel")
        self.close()

    def run_new(self):
        #os.chdir(self.modelDir)
        #print("new1 at ", self.modelDir)
        import FreeCAD
        #FreeCAD.Gui.runCommand('Std_Macro_16',0)
        _macroPath = os.path.expanduser("~")+'/.local/share/FreeCAD/Mod/dexcsCfdOF/Macro'
        _prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").GetString('MacroPath')
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").SetString('MacroPath',_macroPath)
        FreeCADGui.runCommand('Std_Macro_16',0)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").SetString('MacroPath',_prefs)


    def run_edit(self):
        #dexcsCfMeshPATH = "~/.FreeCAD/Mod/dexcsCfMesh"
        #import sys
        #sys.path.append(dexcsCfMeshPATH)
        import dexcsCfdTools
        if self.dpltFile :
            fileName = self.modelDir + '/system/' + self.dpltFile
            #dexcsCfdTools.openFileManager(self.modelDir+'/system/' + self.dpltFile)
            proc = QtCore.QProcess()
            proc.setProgram("gnome-text-editor") 
            proc.setArguments([fileName])
            #proc.start()
            proc.startDetached()
            #proc.start("gedit " + fileName)
            #env = QtCore.QProcessEnvironment.systemEnvironment()
            #removeAppimageEnvironment(env)
            #proc.setWorkingDirectory(self.modelDir)
            #proc.setProcessEnvironment(env)
            #if proc.waitForStarted():
            #    consoleMessageFn("gedit started")
            #    return
            #else:
            #    consoleMessageFn("Error starting gedit")
            #    return

    def run_plot(self):
        print("plot")
        if self.dpltFile :
            fileName = self.modelDir + '/system/' + self.dpltFile
            f = open(fileName,"r")
            lines = f.readlines()
            f.close()
            print("postProcessing=",f.name)

            dexcsPlotPost.dexcsPlotPost(self.modelDir,lines)


if __name__ == '__main__':
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
        #print("debug1")
    else:
        #print("debug2")
        app = QtWidgets.QApplication.instance()
        #print("debug3")
    window = gui()
    window.show()
