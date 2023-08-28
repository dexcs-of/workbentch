# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2016 - Bernd Hahnebach <bernd@bimstatik.org>            *
# *   Copyright (c) 2017 Alfred Bogaers (CSIR) <abogaers@csir.co.za>        *
# *   Copyright (c) 2017 Johan Heyns (CSIR) <jheyns@csir.co.za>             *
# *   Copyright (c) 2017 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>          *
# *   Copyright (c) 2019-2021 Oliver Oxtoby <oliveroxtoby@gmail.com>        *
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

from __future__ import print_function
import FreeCAD
import os
import os.path
from dexcsCfdMesh import _CfdMesh
import time
from datetime import timedelta
import dexcsCfdTools
from dexcsCfdTools import setQuantity, getQuantity
import dexcsCfdMeshTools
import dexcsCfMeshTools
from dexcsCfdConsoleProcess import CfdConsoleProcess
import TemplateBuilder
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    from PySide import QtCore
    from PySide import QtGui
    from PySide.QtCore import Qt
    from PySide.QtGui import QApplication

import pythonVerCheck

# import sys
# import gettext

# localedir = os.path.expanduser("~") + "/.FreeCAD/Mod/dexcsCfdOF/locale"
# if sys.version_info.major == 3:
# 	gettext.install("dexcsCfMeshSetting", localedir)
# else:
# 	gettext.install("dexcsCfMeshSetting", localedir, unicode=True)


class _TaskPanelCfdMesh:
    """ The TaskPanel for editing References property of dexcsCfdMesh objects and creation of new CFD mesh """
    def __init__(self, obj):
        self.mesh_obj = obj
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__), "dexcsTaskPanelCfdMesh.ui"))

        self.form.setWindowTitle(_("dexcsCFD Mesh"))
        self.form.pb_write_mesh.setText(_("Write mesh case"))
        self.form.l_meshTool.setText(_("Mesh Tool"))
        self.form.l_dimension.setText(_("dimension"))
        self.form.l_featureAngle.setText(_("Feature Angle(deg)"))
        self.form.pb_stop_mesh.setText(_("Stop"))
        self.form.l_scaleToMeter.setText(_("Scale to Meter:"))
        self.form.pb_edit_mesh.setText(_("Edit"))
        self.form.pb_run_mesh.setText(_("Run mesher"))
        self.form.label_3.setText(_("Mesh verification"))
        self.form.label_5.setText(_("Mesher"))
        self.form.label_6.setText(_("Mesh<"))
        self.form.pb_checkmesh.setText(_("CheckMesh"))
        self.form.label.setText(_("Mesh Parameters"))
        self.form.check_optimiseLayer.setText(_("optimiseLayer"))
        self.form.label_maxNumIterations.setText(_("maxNumIterations"))
        self.form.label_maxAllowedThickness.setText(_("maximum allowed thickness:"))
        self.form.label_featureSizeFactor.setText(_("featureSizeFactor"))
        self.form.label_reCalculateNormals.setText(_("reCalculateNormals"))
        self.form.label_nSmoothNormals.setText(_("Number of iterations:"))
        self.form.check_keepCells.setText(_("keepCellsIntersectingBoundary"))
        self.form.l_max.setText(_("Base element size:"))
        self.form.l_workflowControls.setText(_("workflowControls(stopAfter):"))
        self.form.label_2.setText(_("Status"))

        self.console_message_cart = ''
        self.error_message = ''
        self.cart_mesh = dexcsCfdMeshTools.CfdMeshTools(self.mesh_obj)
        self.paraviewScriptName = ""

        self.mesh_process = CfdConsoleProcess(finishedHook=self.meshFinished,
                                              stdoutHook=self.gotOutputLines,
                                              stderrHook=self.gotErrorLines)

        self.form.cb_meshTool.activated.connect(self.choose_utility)

        self.Timer = QtCore.QTimer()
        self.Timer.setInterval(1000)
        self.Timer.timeout.connect(self.update_timer_text)

        self.open_paraview = QtCore.QProcess()

        self.form.pb_write_mesh.clicked.connect(self.writeMesh)
        self.form.pb_edit_mesh.clicked.connect(self.editMesh)
        self.form.pb_run_mesh.clicked.connect(self.runMesh)
        self.form.pb_stop_mesh.clicked.connect(self.killMeshProcess)
        self.form.pb_paraview.clicked.connect(self.openParaview)
        self.form.pb_checkmesh.clicked.connect(self.runCheckMesh)
        #self.form.pb_load_mesh.clicked.connect(self.pbLoadMeshClicked)
        #self.form.pb_clear_mesh.clicked.connect(self.pbClearMeshClicked)
        #self.form.pb_searchPointInMesh.clicked.connect(self.searchPointInMesh)
        self.form.pb_stop_mesh.setEnabled(False)
        self.form.pb_paraview.setEnabled(False)
        self.form.pb_checkmesh.setEnabled(False)
        #self.form.snappySpecificProperties.setVisible(False)
        self.form.optimizer_frame.setVisible(False)
        self.form.check_reCalculateNormals.setChecked(True)

        self.form.cb_dimension.addItems(_CfdMesh.known_element_dimensions)
        self.form.cb_meshTool.addItems(_CfdMesh.known_mesh_utility)
        self.form.cb_workflowControls.addItems(_CfdMesh.known_workflowControls)

        self.form.if_max.setToolTip(_("Enter 0 to use default value"))
        #self.form.pb_searchPointInMesh.setToolTip("Specify below a point vector inside of the mesh or press 'Search' "
        #                                          "to try to automatically find a point")
        #self.form.if_cellsbetweenlevels.setToolTip("Number of cells between each of level of refinement")
        #self.form.if_edgerefine.setToolTip("Number of refinement levels for all edges")

        self.form.check_optimiseLayer.stateChanged.connect(self.updateUI)

        self.load()
        self.updateUI()

        self.Start = time.time()
        self.Timer.start()

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Close)
        # def reject() is called on close button
        # def accept() in no longer needed, since there is no OK button

    def reject(self):
        # There is no reject - only close
        self.store()
        self.mesh_process.terminate()
        self.mesh_process.waitForFinished()
        self.open_paraview.terminate()
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.recompute()
        return True

    def load(self):
        """ Fills the widgets """
        setQuantity(self.form.if_max, self.mesh_obj.BaseCellSize)

        ### <--addDexcs 
        self.form.if_featureAngle.setValue(self.mesh_obj.FeatureAngle) 
        self.form.if_scaleToMeter.setValue(self.mesh_obj.ScaleToMeter) 
        self.form.check_keepCells.setChecked(self.mesh_obj.keepCellsIntersectingBoundary) 
        self.form.check_optimiseLayer.setChecked(self.mesh_obj.optimiseLayer) 
        self.form.if_nSmoothNormals.setValue(self.mesh_obj.opt_nSmoothNormals) 
        self.form.if_maxNumIterations.setValue(self.mesh_obj.opt_maxNumIterations) 
        self.form.if_featureSizeFactor.setValue(self.mesh_obj.opt_featureSizeFactor) 
        self.form.check_reCalculateNormals.setChecked(self.mesh_obj.opt_reCalculateNormals) 
        self.form.if_relThicknessTol.setValue(self.mesh_obj.opt_relThicknessTol) 
        index_utility = self.form.cb_meshTool.findText(self.mesh_obj.MeshUtility)
        self.form.cb_meshTool.setCurrentIndex(index_utility)
        ### addDexcs -->

        #point_in_mesh = self.mesh_obj.PointInMesh.copy()
        #setQuantity(self.form.if_pointInMeshX, point_in_mesh.get('x'))
        #setQuantity(self.form.if_pointInMeshY, point_in_mesh.get('y'))
        #setQuantity(self.form.if_pointInMeshZ, point_in_mesh.get('z'))
        #self.form.if_cellsbetweenlevels.setValue(self.mesh_obj.CellsBetweenLevels)
        #self.form.if_edgerefine.setValue(self.mesh_obj.EdgeRefinement)

        index_dimension = self.form.cb_dimension.findText(self.mesh_obj.ElementDimension)
        self.form.cb_dimension.setCurrentIndex(index_dimension)
        index_workflowControls = self.form.cb_workflowControls.findText(self.mesh_obj.workflowControls)
        self.form.cb_workflowControls.setCurrentIndex(index_workflowControls)

    def updateUI(self):
        case_path = self.cart_mesh.meshCaseDir
        #print('case_path = ' + case_path)
        self.form.pb_edit_mesh.setEnabled(os.path.exists(case_path))
        self.form.pb_run_mesh.setEnabled(os.path.exists(os.path.join(case_path, "Allmesh")))
        self.form.pb_paraview.setEnabled(os.path.exists(os.path.join(case_path, "pv.foam")))
        self.form.pb_checkmesh.setEnabled(os.path.exists(os.path.join(case_path, "pv.foam")))
        #self.form.pb_load_mesh.setEnabled(os.path.exists(os.path.join(case_path, "mesh_outside.stl")))
        #utility = self.form.cb_utility.currentText()
        #if utility == "snappyHexMesh":
        #    self.form.snappySpecificProperties.setVisible(True)
#        elif utility == "cfMesh":
#            self.form.snappySpecificProperties.setVisible(False)
        if self.form.check_optimiseLayer.isChecked():
            self.form.optimizer_frame.setVisible(True)
        else:
            self.form.optimizer_frame.setVisible(False)



    def store(self):
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.MeshUtility "
                             "= '{}'".format(self.mesh_obj.Name, self.form.cb_meshTool.currentText()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.BaseCellSize "
                             "= '{}'".format(self.mesh_obj.Name, getQuantity(self.form.if_max)))

        ### <--addDexcs 
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.FeatureAngle "
                             "= {}".format(self.mesh_obj.Name, self.form.if_featureAngle.value()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.ScaleToMeter "
                             "= {}".format(self.mesh_obj.Name, self.form.if_scaleToMeter.value()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.keepCellsIntersectingBoundary "
                             "= {}".format(self.mesh_obj.Name, self.form.check_keepCells.isChecked()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.optimiseLayer "
                             "= {}".format(self.mesh_obj.Name, self.form.check_optimiseLayer.isChecked()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.opt_nSmoothNormals "
                             "= {}".format(self.mesh_obj.Name, self.form.if_nSmoothNormals.value()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.opt_maxNumIterations "
                             "= {}".format(self.mesh_obj.Name, self.form.if_maxNumIterations.value()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.opt_featureSizeFactor "
                             "= {}".format(self.mesh_obj.Name, self.form.if_featureSizeFactor.value()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.opt_reCalculateNormals "
                             "= {}".format(self.mesh_obj.Name, self.form.check_reCalculateNormals.isChecked()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.opt_relThicknessTol "
                             "= {}".format(self.mesh_obj.Name, self.form.if_relThicknessTol.value()))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.workflowControls "
                             "= '{}'".format(self.mesh_obj.Name, self.form.cb_workflowControls.currentText()))
        ### addDexcs -->

        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.ElementDimension "
                             "= '{}'".format(self.mesh_obj.Name, self.form.cb_dimension.currentText()))
        #FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.CellsBetweenLevels "
        #                     "= {}".format(self.mesh_obj.Name, self.form.if_cellsbetweenlevels.value()))
        #FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.EdgeRefinement "
        #                     "= {}".format(self.mesh_obj.Name, self.form.if_edgerefine.value()))
        #point_in_mesh = {'x': getQuantity(self.form.if_pointInMeshX),
        #                 'y': getQuantity(self.form.if_pointInMeshY),
        #                 'z': getQuantity(self.form.if_pointInMeshZ)}
        #FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.PointInMesh "
        #                     "= {}".format(self.mesh_obj.Name, point_in_mesh))
        self.cart_mesh = dexcsCfdMeshTools.CfdMeshTools(self.mesh_obj)

    def consoleMessage(self, message="", color="#000000", timed=True):
        if timed:
            self.console_message_cart = self.console_message_cart \
                                        + '<font color="#0000FF">{0:4.1f}:</font> <font color="{1}">{2}</font><br>'.\
                                        format(time.time() - self.Start, color, message)
        else:
            self.console_message_cart = self.console_message_cart \
                                        + '<font color="{0}">{1}</font><br>'.\
                                        format(color, message)
        self.form.te_output.setText(self.console_message_cart)
        self.form.te_output.moveCursor(QtGui.QTextCursor.End)
        if FreeCAD.GuiUp:
            FreeCAD.Gui.updateGui()

    def update_timer_text(self):
        if self.mesh_process.state() == QtCore.QProcess.ProcessState.Running:
            self.form.l_time.setText('Time: ' + dexcsCfdTools.formatTimer(time.time() - self.Start))

    def choose_utility(self, index):
        if index < 0:
            return
        utility = self.form.cb_utility.currentText()
        if utility == "snappyHexMesh":
            self.form.snappySpecificProperties.setVisible(True)
        else:
            self.form.snappySpecificProperties.setVisible(False)

    def writeMesh(self):
        import importlib
        importlib.reload(dexcsCfMeshTools)
        self.console_message_cart = ''
        self.Start = time.time()
        # Re-initialise dexcsCfdMeshTools with new parameters
        self.store()
        FreeCADGui.addModule("dexcsCfdMeshTools")
        FreeCADGui.addModule("dexcsCfMeshTools")
        self.consoleMessage("Preparing meshing ...")

        #cart_mesh = self.cart_mesh
        self.analysis = dexcsCfdTools.getParentAnalysisObject(self.mesh_obj)
        output_path = dexcsCfdTools.getOutputPath(self.analysis) + os.path.sep
        if output_path[-1] == os.path.sep:
            output_path1 = output_path[:-1] 
        else:
            output_path1 = output_path

        print("output dir = " + output_path1)
        current_model_path = os.path.dirname(FreeCAD.ActiveDocument.FileName)
        print("model dir = " + current_model_path)
        #if output_path1 != current_model_path:

        dictName = os.path.dirname(FreeCAD.ActiveDocument.FileName)  + "/.CaseFileDict"
        writeDict = open(dictName , 'w')
        writeDict.writelines(output_path1)
        writeDict.close()

        template_case = dexcsCfdTools.getTemplateCase(self.analysis)
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            FreeCADGui.doCommand("dexcsCfMesh = dexcsCfMeshTools.MainControl()")
            #FreeCADGui.doCommand("dexcsCfMesh.perform("+ "'" + cart_mesh.meshCaseDir + "'" + ")")
            FreeCADGui.doCommand("dexcsCfMesh.perform("+ "'" + output_path + "', '" + template_case + "'" + ")")       
            self.consoleMessage("Exporting the part surfaces ...")
        except Exception as ex:
            self.consoleMessage("Error " + type(ex).__name__ + ": " + str(ex), '#FF0000')
            raise
        finally:
            QApplication.restoreOverrideCursor()
        self.updateUI()

    def editMesh(self):
        case_path = self.cart_mesh.meshCaseDir
        self.consoleMessage(_("Please edit the case input files externally at: {}\n").format(case_path))
        dexcsCfdTools.openFileManager(case_path)

    def runMesh(self):
        self.Start = time.time()
        cart_mesh = self.cart_mesh
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.consoleMessage("Running {} ...".format(self.mesh_obj.MeshUtility))
            cart_mesh.error = False
            cmd = dexcsCfdTools.makeRunCommand('./Allmesh', cart_mesh.meshCaseDir, source_env=False)
            print("cmd = ", cmd)
            FreeCAD.Console.PrintMessage(_("Executing: ") + ' '.join(cmd) + "\n")
            env_vars = dexcsCfdTools.getRunEnvironment()
            self.mesh_process.start(cmd, env_vars=env_vars)
            if self.mesh_process.waitForStarted():
                self.form.pb_run_mesh.setEnabled(False)  # Prevent user running a second instance
                self.form.pb_stop_mesh.setEnabled(True)
                self.form.pb_paraview.setEnabled(False)
                self.form.pb_checkmesh.setEnabled(False)
                #self.form.pb_load_mesh.setEnabled(False)
                self.consoleMessage(_("Mesher started"))
            else:
                self.consoleMessage(_("Error starting meshing process"), "#FF0000")
                cart_mesh.error = True
        except Exception as ex:
            self.consoleMessage(_("Error ") + type(e).__name__ + ": " + str(ex), '#FF0000')
            raise
        finally:
            QApplication.restoreOverrideCursor()

    def killMeshProcess(self):
        self.consoleMessage(_("Meshing manually stopped"))
        self.error_message = _('Meshing interrupted')
        self.mesh_process.terminate()
        # Note: meshFinished will still be called

    def gotOutputLines(self, lines):
        pass

    def gotErrorLines(self, lines):
        print_err = self.mesh_process.processErrorOutput(lines)
        if print_err is not None:
            self.consoleMessage(print_err, "#FF0000")

    def meshFinished(self, exit_code):
        if exit_code == 0:
            self.consoleMessage(_('Meshing completed'))
            self.form.pb_run_mesh.setEnabled(True)
            self.form.pb_stop_mesh.setEnabled(False)
            self.form.pb_paraview.setEnabled(True)
            self.form.pb_checkmesh.setEnabled(True)
            #self.form.pb_load_mesh.setEnabled(True)
            
            self.template_path = os.path.join(dexcsCfdTools.get_module_path(), "data", "dexcsMesh")
            settings={}
            settings['MeshPath'] = self.cart_mesh.meshCaseDir
            TemplateBuilder.TemplateBuilder(self.cart_mesh.meshCaseDir, self.template_path, settings)

        else:
            self.consoleMessage(_("Meshing exited with error"), "#FF0000")
            self.form.pb_run_mesh.setEnabled(True)
            self.form.pb_stop_mesh.setEnabled(False)
            self.form.pb_paraview.setEnabled(False)
            self.form.pb_checkmesh.setEnabled(False)

        self.error_message = ''
        # Get rid of any existing loaded mesh
        self.pbClearMeshClicked()
        self.updateUI()

    def openParaview(self):
        self.Start = time.time()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        case_path = os.path.abspath(self.cart_mesh.meshCaseDir)
        script_name = "pvScriptMesh.py"
        try:
            self.open_paraview = dexcsCfdTools.startParaview(case_path, script_name, self.consoleMessage)
        finally:
            QApplication.restoreOverrideCursor()

    def pbLoadMeshClicked(self):
        self.consoleMessage(_("Reading mesh ..."), timed=False)
        self.cart_mesh.loadSurfMesh()
        self.consoleMessage(_('Triangulated representation of the surface mesh is shown - '), timed=False)
        self.consoleMessage(_("Please view in Paraview for accurate display.\n"), timed=False)

    def pbClearMeshClicked(self):
        for m in self.mesh_obj.Group:
            if m.isDerivedFrom("Fem::FemMeshObject"):
                FreeCAD.ActiveDocument.removeObject(m.Name)
        FreeCAD.ActiveDocument.recompute()

    def searchPointInMesh(self):
        print (_("Searching for an internal vector point ..."))
        # Apply latest mesh size
        self.store()
        pointCheck = self.cart_mesh.automaticInsidePointDetect()
        if pointCheck is not None:
            iMPx, iMPy, iMPz = pointCheck
            setQuantity(self.form.if_pointInMeshX, str(iMPx) + "mm")
            setQuantity(self.form.if_pointInMeshY, str(iMPy) + "mm")
            setQuantity(self.form.if_pointInMeshZ, str(iMPz) + "mm")

    def runCheckMesh(self):
        self.Start = time.time()
        cart_mesh = self.cart_mesh
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.consoleMessage(_("Running {} ...").format(self.mesh_obj.MeshUtility))
            cart_mesh.error = False
            cmd = dexcsCfdTools.makeRunCommand('./Allcheck', cart_mesh.meshCaseDir, source_env=False)
            FreeCAD.Console.PrintMessage(_("Executing: ") + ' '.join(cmd) + "\n")
            env_vars = dexcsCfdTools.getRunEnvironment()
            self.mesh_process.start(cmd, env_vars=env_vars)
            if self.mesh_process.waitForStarted():
                self.form.pb_run_mesh.setEnabled(False)  # Prevent user running a second instance
                self.form.pb_stop_mesh.setEnabled(True)
                self.form.pb_paraview.setEnabled(False)
                self.form.pb_checkmesh.setEnabled(False)
                #self.form.pb_load_mesh.setEnabled(False)
                self.consoleMessage(_("checkMesh started"))
            else:
                self.consoleMessage(_("Error starting checkMeshing process"), "#FF0000")
                cart_mesh.error = True
        except Exception as ex:
            self.consoleMessage(_("Error ") + type(e).__name__ + ": " + str(ex), '#FF0000')
            raise
        finally:
            QApplication.restoreOverrideCursor()
