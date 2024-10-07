# -*- coding: utf-8 -*-
# # ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2013-2015 - Juergen Riegel <FreeCAD@juergen-riegel.net> *
# *   Copyright (c) 2017 Johan Heyns (CSIR) <jheyns@csir.co.za>             *
# *   Copyright (c) 2017 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>          *
# *   Copyright (c) 2017 Alfred Bogaers (CSIR) <abogaers@csir.co.za>        *
# *   Copyright (c) 2019 Oliver Oxtoby <oliveroxtoby@gmail.com>             *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

from multiprocessing import parent_process
import FreeCAD
import dexcsCfdTools
from dexcsCfdTools import addObjectProperty
import os
import platform
if FreeCAD.GuiUp:
    import FreeCADGui
from PySide import QtCore, QtGui
from PySide.QtGui import *
import pythonVerCheck



def makeCfdAnalysis(name):
    """ Create a Cfd Analysis group object """
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", name)
    _CfdAnalysis(obj)

    if FreeCAD.GuiUp:
        _ViewProviderCfdAnalysis(obj.ViewObject)
    return obj


class _CfdAnalysis:
    """ The CFD analysis group """
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "dexcsCfdAnalysis"
        print("deb:__init__")
        self.initProperties(obj)

    def initProperties(self, obj):
        print("deb_CfdAnalysis-initProperties")
        print(obj.Label)
        model = FreeCAD.ActiveDocument.FileName
        prefs = dexcsCfdTools.getPreferencesLocation()
        model_Dir = FreeCAD.ParamGet(prefs).GetString("DefaultOutputPath", "")
        if os.path.exists(model_Dir):
            model_Dir = model_Dir
        else:
            model_Dir = os.path.dirname(model)
        templateCase = FreeCAD.ParamGet(prefs).GetString("DefaultTemplateCase", "")
 
        plot_maxnumber = FreeCAD.ParamGet(prefs).GetString("DefaultPlotMaxnumber", "")
        plot_method = FreeCAD.ParamGet(prefs).GetString("DefaultPlotMethod", "")
 
        addObjectProperty(obj, "OutputPath", model_Dir, "App::PropertyPath", "",
                           "Path to which cases are written (blank to use system default)")
        addObjectProperty(obj, "TemplateCase", templateCase, "App::PropertyPath", "",
                           "Path to Template case Dir (blank to use system default)")

        addObjectProperty(obj, "PlotMaxnumber", plot_maxnumber, "App::PropertyString", "",
                           "Max Plot number")

        if plot_method == 'last' :
            addObjectProperty(obj, 'PlotMethodLast', True, "App::PropertyBool", "", "Plot Method if over Maxnumber")
        else :
            addObjectProperty(obj, 'PlotMethodLast', False, "App::PropertyBool", "", "Plot Method if over Maxnumber")

        addObjectProperty(obj, "IsActiveAnalysis", False, "App::PropertyBool", "", "Active analysis object in document")
        obj.setEditorMode("IsActiveAnalysis", 1)  # Make read-only (2 = hidden)
        addObjectProperty(obj, 'NeedsMeshRewrite', True, "App::PropertyBool", "", "Mesh setup needs to be re-written")
        addObjectProperty(obj, 'NeedsCaseRewrite', True, "App::PropertyBool", "", "Case setup needs to be re-written")
        addObjectProperty(obj, 'NeedsMeshRerun', True, "App::PropertyBool", "", "Mesher needs to be re-run before running solver")

    def restoredProperties(self, obj):

        env = QtCore.QProcessEnvironment.systemEnvironment()

        model = FreeCAD.ActiveDocument.FileName
        prefs = dexcsCfdTools.getPreferencesLocation()
        model_Dir = FreeCAD.ParamGet(prefs).GetString("DefaultOutputPath", "")
        if os.path.exists(model_Dir):
            defaultModel_Dir = model_Dir
        else:
            defaultModel_Dir = os.path.dirname(model)

        setDictOutput_dir = ""
        dictName = os.path.dirname(FreeCAD.ActiveDocument.FileName)  + "/.CaseFileDict"
        if os.path.isfile(dictName) == True:
            f = open(dictName)
            tempDirName = f.read()
            f.close()
            if os.path.isdir(tempDirName) == True:
                 setDictOutput_dir = tempDirName

        if obj.IsActiveAnalysis:
            outputPath = obj.OutputPath
            # print("outputPath : " + outputPath)
            # print("defaultModel_Dir : " + defaultModel_Dir)
            # print("setDictOutput_dir : " + setDictOutput_dir)

            if ( defaultModel_Dir == outputPath ) or ( setDictOutput_dir == outputPath) :
                pass
            else:
                message = _("The OutputPath of Active Analysis Container is \n") + outputPath
                message = message + _("\n This is not the Default Setting Path.\n\n\t Do you change the OutputPath ?")
                # dialog = QtGui.QMessageBox.question(None,"Question",message, QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                msgBox = QtGui.QMessageBox()
                msgBox.setText(message)
                msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.RestoreDefaults | QMessageBox.No)
                msgBox.setDefaultButton(QMessageBox.RestoreDefaults)
                dialog = msgBox.exec_()
 
                if dialog == QtGui.QMessageBox.RestoreDefaults:

                    outputPath = defaultModel_Dir
 
                if dialog == QtGui.QMessageBox.Yes:

                    if env.contains("APPIMAGE"):
                        #message = _("This FreeCAD is AppImage version.\n ")
                        #message = message + _("AppImage cannot change the OutputPAth while loading process.\n\n") 
                        #message = message + _("so if you want change the OutputPAth of Analysis Container,\n") 
                        #message = message + _("change the property manually after lodaing process,\n") 
                        #ans = QtGui.QMessageBox.critical(None, _("AppImage Warning"), message, QtGui.QMessageBox.Yes)
                        dexcsCfdTools.removeAppimageEnvironment(env)
                    else:
                        d = QtGui.QFileDialog().getExistingDirectory(None, _('Choose output directory'), defaultModel_Dir)

                        #msgBox = QtGui.QFileDialog()
                        #msgBox.ShowDirsOnly
                        #msgBox.setDirectory(defaultModel_Dir)
                        #msgBox.setLabelText(_('Choose output directory'))
                        #d = msgBox.exec_()

                        if d and os.access(d, os.R_OK):
                            outputPath = d

                if outputPath != defaultModel_Dir:
                    writeDict = open(dictName , 'w')
                    writeDict.writelines(outputPath)
                    writeDict.close()

            obj.OutputPath = outputPath


        # active_analysis = dexcsCfdTools.getActiveAnalysis()
        # if active_analysis:
        #     print(active_analysis.OutputPath)
        #print(model_Dir)
        #templateCase = FreeCAD.ParamGet(prefs).GetString("DefaultTemplateCase", "")
        # addObjectProperty(obj, "OutputPath", model_Dir, "App::PropertyPath", "",
        #                    "Path to which cases are written (blank to use system default)")
        # #obj.OutputPath = model_Dir
        # addObjectProperty(obj, "TemplateCase", templateCase, "App::PropertyPath", "",
        #                    "Path to Template case Dir (blank to use system default)")
        # addObjectProperty(obj, "IsActiveAnalysis", False, "App::PropertyBool", "", "Active analysis object in document")
        # obj.setEditorMode("IsActiveAnalysis", 1)  # Make read-only (2 = hidden)
        # addObjectProperty(obj, 'NeedsMeshRewrite', True, "App::PropertyBool", "", "Mesh setup needs to be re-written")
        # addObjectProperty(obj, 'NeedsCaseRewrite', True, "App::PropertyBool", "", "Case setup needs to be re-written")
        # addObjectProperty(obj, 'NeedsMeshRerun', True, "App::PropertyBool", "", "Mesher needs to be re-run before running solver")

    def onDocumentRestored(self, obj):
        #print("deb:restored")
        self.restoredProperties(obj)

def dummyFunction(): # 何故かこれがないとうまく動かない      
        pass

class _CommandCfdAnalysis:
    """ The Cfd_Analysis command definition """
    def __init__(self):
        pass

    def GetResources(self):
        icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "cfd_analysis.png")
        return {'Pixmap': icon_path,
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Cfd_Analysis", "Analysis container"),
                'Accel': "N, C",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Cfd_Analysis", _("Creates an analysis container with a CFD solver"))}

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create CFD Analysis")
        FreeCADGui.doCommand("")
        FreeCADGui.addModule("dexcsCfdAnalysis")
        FreeCADGui.addModule("dexcsCfdTools")
        FreeCADGui.doCommand("analysis = dexcsCfdAnalysis.makeCfdAnalysis('dexcsCfdAnalysis')")
        FreeCADGui.doCommand("dexcsCfdTools.setActiveAnalysis(analysis)")

        ''' Objects ordered according to expected workflow '''

        # Add mesh object when dexcsCfdAnalysis container is created
        FreeCADGui.addModule("dexcsCfdMesh")
        FreeCADGui.doCommand("analysis.addObject(dexcsCfdMesh.makeCfdMesh())")

        # Add solver object when dexcsCfdAnalysis container is created
        FreeCADGui.addModule("dexcsCfdSolverFoam")
        FreeCADGui.doCommand("analysis.addObject(dexcsCfdSolverFoam.makeCfdSolverFoam())")


class _ViewProviderCfdAnalysis:
    """ A View Provider for the dexcsCfdAnalysis container object. """
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "cfd_analysis.png")
        return icon_path

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.bubbles = None

    def updateData(self, obj, prop):
        return

    def onChanged(self, vobj, prop):
        self.makePartTransparent(vobj)
        dexcsCfdTools.setCompSolid(vobj)
        return

    def doubleClicked(self, vobj):
        #print("deb:AnalysisiContainerDoubleClicced")
        if dexcsCfdTools.getActiveAnalysis():
            outputPath1 = dexcsCfdTools.getActiveAnalysis().OutputPath
        else:
            dexcsCfdTools.setActiveAnalysis(self.Object)
            #outputPath1 = self.Object.OutputPath
            return True
        #print(outputPath1)
        if not dexcsCfdTools.getActiveAnalysis() == self.Object:
            if FreeCADGui.activeWorkbench().name() != 'dexcsCfdOFWorkbench':
                FreeCADGui.activateWorkbench("dexcsCfdOFWorkbench")
            dexcsCfdTools.setActiveAnalysis(self.Object)
            _CfdAnalysis.restoredProperties(self,self.Object)
        outputPath2 = self.Object.OutputPath
        #print(outputPath2)
        if outputPath1 == outputPath2 :
            message = _("The OutputPath of Active Analysis Container is not changed.\n") 
            message = message + _("\n Please note that the contents of the case file at this point are the previous AnalysisContainer.")
            message = message + _("\n You will need to recreate the case file to continue working.")
            dialog = QtGui.QMessageBox.critical(None,"Question",message, QtGui.QMessageBox.Yes)
        return True

    def makePartTransparent(self, vobj):
        """ Make parts transparent so that the boundary conditions and cell zones are clearly visible. """
        docName = str(vobj.Object.Document.Name)
        doc = FreeCAD.getDocument(docName)
        for obj in doc.Objects:
            if obj.isDerivedFrom("Part::Feature") and not("CfdFluidBoundary" in obj.Name):
                vobj2 = FreeCAD.getDocument(docName).getObject(obj.Name).ViewObject
                if hasattr(vobj2, 'Transparency'):
                    vobj2.Transparency = 70
                if obj.isDerivedFrom("PartDesign::Feature"):
                    doc.getObject(obj.Name).ViewObject.LineWidth = 1
                    doc.getObject(obj.Name).ViewObject.LineColor = (0.5, 0.5, 0.5)
                    doc.getObject(obj.Name).ViewObject.PointColor = (0.5, 0.5, 0.5)
            if obj.isDerivedFrom("Part::Feature") and obj.Name.startswith("Compound"):
                FreeCAD.getDocument(docName).getObject(obj.Name).ViewObject.Visibility = False

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
