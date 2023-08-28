#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2013-2015 - Juergen Riegel <FreeCAD@juergen-riegel.net> *
# *   Copyright (c) 2016 - Qingfeng Xia <qingfeng.xia()eng.ox.ac.uk>        *
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

import FreeCAD
import dexcsCfdTools
import os
import os.path
import time
from dexcsCfdConsoleProcess import CfdConsoleProcess
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    from PySide import QtGui
    from PySide.QtCore import Qt
    from PySide.QtGui import QApplication

import pythonVerCheck

class _dexcsTaskPanelCfdSolverControl:
    def __init__(self, solver_runner_obj):
        ui_path = os.path.join(os.path.dirname(__file__), "dexcsTaskPanelCfdSolverControl.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.analysis_object = dexcsCfdTools.getActiveAnalysis()

        self.form.setWindowTitle(_("Analysis control"))
        self.form.label.setText(_("Case"))
        self.form.label_2.setText(_("Solver"))
        self.form.label_3.setText(_("Results"))
        self.form.label_5.setText(_("Status"))
        self.form.terminateSolver.setText(_("Stop"))
        self.form.pb_run_solver.setText(_("Run"))
        self.form.pb_write_inp.setText(_("Write"))
        self.form.pb_edit_inp.setText(_("Edit"))
        self.form.pb_reconstruct.setText(_("reconstructPar"))
        self.form.check_parallel.setText(_("parallel"))

        self.solver_runner = solver_runner_obj
        self.solver_object = solver_runner_obj.solver

        self.form.if_ncpu.setValue(self.solver_object.ParallelCores) 
        #known_method = ['simple','hierachical','scotch','metis','manual']
        known_method = ['scotch']
        self.form.cb_method.addItems(known_method)
        index_method = self.form.cb_method.findText(self.solver_object.ParallelMethod)
        self.form.cb_method.setCurrentIndex(index_method)

        self.form.check_parallel.stateChanged.connect(self.updateUI)
        self.form.check_parallel.setChecked(self.solver_object.ParallelCores > 1)

        # update UI
        self.console_message = ''

        self.solver_run_process = CfdConsoleProcess(finishedHook=self.solverFinished,
                                                    stdoutHook=self.gotOutputLines,
                                                    stderrHook=self.gotErrorLines)
        self.Timer = QtCore.QTimer()
        self.Timer.setInterval(1000)
        self.Timer.timeout.connect(self.updateText)

        self.form.terminateSolver.clicked.connect(self.killSolverProcess)
        self.form.terminateSolver.setEnabled(False)

        self.open_paraview = QtCore.QProcess()

        self.working_dir = dexcsCfdTools.getOutputPath(self.analysis_object)

        self.updateUI()

        # Connect Signals and Slots
        #self.form.pb_write_inp.clicked.connect(self.write_input_file_handler)
        self.form.pb_write_inp.clicked.connect(self.write_input_file_handler_dexcs)
        self.form.pb_edit_inp.clicked.connect(self.editSolverInputFile)
        self.form.pb_run_solver.clicked.connect(self.runSolverProcess)
        self.form.pb_paraview.clicked.connect(self.openParaview)
        self.form.pb_reconstruct.clicked.connect(self.runReconstruct)

        self.Start = time.time()
        self.Timer.start()

    def updateUI(self):
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.ParallelMethod "
                             "= '{}'".format(self.solver_object.Name, self.form.cb_method.currentText()))
        solverDirectory = os.path.join(self.working_dir, self.solver_object.InputCaseName)
        #print('solverDirectory=', solverDirectory)
        self.form.pb_edit_inp.setEnabled(os.path.exists(solverDirectory))
        self.form.pb_paraview.setEnabled(os.path.exists(os.path.join(solverDirectory, "pv.foam")))
        self.form.pb_reconstruct.setEnabled(os.path.exists(os.path.join(solverDirectory, "Allreconst")))
        self.form.pb_run_solver.setEnabled(os.path.exists(os.path.join(solverDirectory, "Allrun")))
        self.form.parallel_frame.setVisible(self.form.check_parallel.isChecked())
        if self.form.check_parallel.isChecked():
            if self.form.if_ncpu.value()==1:
                self.form.if_ncpu.setValue(2)
        else:
            self.form.if_ncpu.setValue(1)
            FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.ParallelCores "
                             "= {}".format(self.solver_object.Name, 1))
            FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.Parallel"
                             "= {}".format(self.solver_object.Name, 0))



    def consoleMessage(self, message="", color="#000000"):
        self.console_message = self.console_message + \
                               '<font color="#0000FF">{0:4.1f}:</font> <font color="{1}">{2}</font><br>'.\
                               format(time.time() - self.Start, color, message)
        self.form.textEdit_Output.setText(self.console_message)
        self.form.textEdit_Output.moveCursor(QtGui.QTextCursor.End)

    def updateText(self):
        if self.solver_run_process.state() == QtCore.QProcess.ProcessState.Running:
            self.form.l_time.setText('Time: ' + dexcsCfdTools.formatTimer(time.time() - self.Start))

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Close)

    def accept(self):
        FreeCADGui.ActiveDocument.resetEdit()

    def reject(self):
        self.solver_run_process.terminate()
        self.solver_run_process.waitForFinished()
        self.open_paraview.terminate()
        FreeCADGui.ActiveDocument.resetEdit()

    def write_input_file_handler_dexcs(self):
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.ParallelMethod "
                             "= '{}'".format(self.solver_object.Name, self.form.cb_method.currentText()))
        FreeCADGui.doCommand("\nFreeCAD.ActiveDocument.{}.ParallelCores "
                             "= {}".format(self.solver_object.Name, self.form.if_ncpu.value()))
        self.Start = time.time()
        import dexcsCfdCaseWriterFoam
        import importlib
        importlib.reload(dexcsCfdCaseWriterFoam)
        if self.check_prerequisites_helper():
            self.consoleMessage(_("Writing dexcs Allrun ..."))
            self.form.pb_paraview.setEnabled(False)
            self.form.pb_reconstruct.setEnabled(False)
            self.form.pb_edit_inp.setEnabled(False)
            self.form.pb_run_solver.setEnabled(False)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                FreeCADGui.addModule("dexcsCfdCaseWriterFoam")
                FreeCADGui.doCommand("writer = dexcsCfdCaseWriterFoam.dexcsCfdCaseWriterFoam(FreeCAD.ActiveDocument." +
                                     self.solver_runner.analysis.Name + ")")
                FreeCADGui.doCommand("writer.writeAllrun()")
            except Exception as e:
                self.consoleMessage(_("Error writing case:", "#FF0000"))
                self.consoleMessage(type(e).__name__ + ": " + str(e), "#FF0000")
                self.consoleMessage(_("Write case setup file failed", "#FF0000"))
                raise
            finally:
                QApplication.restoreOverrideCursor()
            self.consoleMessage(_("Write dexcs Allrun is completed"))
            self.updateUI()
            self.form.pb_run_solver.setEnabled(True)
        else:
            self.consoleMessage(_("Case check failed"), "#FF0000")
        
    def check_prerequisites_helper(self):
        self.consoleMessage(_("Checking dependencies..."))

        message = self.solver_runner.check_prerequisites()
        if message != "":
            self.consoleMessage(message, "#FF0000")
            return False
        return True

    def editSolverInputFile(self):
        case_path = os.path.join(self.working_dir, self.solver_object.InputCaseName)
        self.consoleMessage(_("Please edit the case input files externally at: {}\n").format(case_path))
        dexcsCfdTools.openFileManager(case_path)

    def runSolverProcess(self):
        self.Start = time.time()

        solverDirectory = os.path.join(self.working_dir, self.solver_object.InputCaseName)
        solverDirectory = os.path.abspath(solverDirectory)
        cmd = self.solver_runner.get_solver_cmd(solverDirectory)
        FreeCAD.Console.PrintMessage(' '.join(cmd) + '\n')
        envVars = self.solver_runner.getRunEnvironment()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.solver_run_process.start(cmd, env_vars=envVars)
        if self.solver_run_process.waitForStarted():
            # Setting solve button to inactive to ensure that two instances of the same simulation aren't started
            # simultaneously
            self.form.pb_write_inp.setEnabled(False)
            self.form.pb_run_solver.setEnabled(False)
            self.form.terminateSolver.setEnabled(True)
            self.form.pb_paraview.setEnabled(True)
            self.form.pb_reconstruct.setEnabled(True)
            self.consoleMessage(_("Solver started"))
        else:
            self.consoleMessage(_("Error starting solver"))
        QApplication.restoreOverrideCursor()

    def killSolverProcess(self):
        self.consoleMessage(_("Solver manually stopped"))
        self.solver_run_process.terminate()
        # Note: solverFinished will still be called

    def solverFinished(self, exit_code):
        if exit_code == 0:
            self.consoleMessage(_("Simulation finished successfully"))
        else:
            self.consoleMessage(_("Simulation exited with error"), "#FF0000")
        self.form.pb_write_inp.setEnabled(True)
        self.form.pb_run_solver.setEnabled(True)
        self.form.terminateSolver.setEnabled(False)

    def gotOutputLines(self, lines):
        self.solver_runner.process_output(lines)

    def gotErrorLines(self, lines):
        print_err = self.solver_run_process.processErrorOutput(lines)
        if print_err is not None:
            self.consoleMessage(print_err, "#FF0000")

    def openParaview(self):
        self.Start = time.time()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        case_path = os.path.abspath(os.path.join(self.working_dir, self.solver_object.InputCaseName))
        script_name = "pvScript.py"
        try:
            self.open_paraview = dexcsCfdTools.startParaview(case_path, script_name, self.consoleMessage)
        finally:
            QApplication.restoreOverrideCursor()

    def runReconstruct(self):
        self.Start = time.time()

        solverDirectory = os.path.join(self.working_dir, self.solver_object.InputCaseName)
        solverDirectory = os.path.abspath(solverDirectory)
        cmd = self.solver_runner.get_reconst_cmd(solverDirectory)
        FreeCAD.Console.PrintMessage(' '.join(cmd) + '\n')
        envVars = self.solver_runner.getRunEnvironment()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.solver_run_process.start(cmd, env_vars=envVars)
        if self.solver_run_process.waitForStarted():
            # Setting solve button to inactive to ensure that two instances of the same simulation aren't started
            # simultaneously
            self.form.pb_write_inp.setEnabled(False)
            self.form.pb_run_solver.setEnabled(False)
            self.form.terminateSolver.setEnabled(True)
            self.form.pb_paraview.setEnabled(True)
            self.form.pb_reconstruct.setEnabled(True)
            self.consoleMessage(_("reconstruction started"))
        else:
            self.consoleMessage(_("Error starting reconstruct"))
        QApplication.restoreOverrideCursor()

