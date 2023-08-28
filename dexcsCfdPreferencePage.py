# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2013-2015 - Juergen Riegel <FreeCAD@juergen-riegel.net> *
# *   Copyright (c) 2016 - Qingfeng Xia <qingfeng.xia()eng.ox.ac.uk>        *
# *   Copyright (c) 2017-2018 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>     *
# *   Copyright (c) 2017 Johan Heyns (CSIR) <jheyns@csir.co.za>             *
# *   Copyright (c) 2017 Alfred Bogaers (CSIR) <abogaers@csir.co.za>        *
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

import os
import os.path
import platform
import sys
if sys.version_info >= (3,):  # Python 3
    import urllib.request as urlrequest
    import urllib.parse as urlparse
else:
    import urllib as urlrequest
    import urlparse
import ssl
import ctypes

import FreeCAD
import dexcsCfdTools
import tempfile
from contextlib import closing

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    from PySide import QtGui
    from PySide.QtCore import Qt, QObject, QThread
    from PySide.QtGui import QApplication

import pythonVerCheck

DEXCS_TEMPLATE = "/opt/DEXCS/template/dexcs"

# Tasks for the worker thread
DOWNLOAD_OPENFOAM = 1
DOWNLOAD_PARAVIEW = 2
DOWNLOAD_CFMESH = 3
DOWNLOAD_HISA = 4


class dexcsCfdPreferencePage:
    def __init__(self):
        ui_path = os.path.join(os.path.dirname(__file__), "dexcsCfdPreferencePage.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.form.setWindowTitle(_("DEXCS Setting"))

        self.form.tb_choose_foam_dir.clicked.connect(self.chooseFoamDir)
        self.form.le_foam_dir.textChanged.connect(self.foamDirChanged)
        self.form.tb_choose_paraview_path.clicked.connect(self.chooseParaviewPath)
        self.form.le_paraview_path.textChanged.connect(self.paraviewPathChanged)

        self.form.tb_choose_output_dir.clicked.connect(self.chooseOutputDir)
        self.form.le_output_dir.textChanged.connect(self.outputDirChanged)
        self.form.tb_choose_template_case.clicked.connect(self.chooseTemplateCase)
        self.form.le_template_case.setText(DEXCS_TEMPLATE)
        self.form.le_template_case.textChanged.connect(self.templateCaseChanged)

        self.form.label_7.setText(_("OpenFOAM install directory"))
        self.form.label_7b.setText(_("ParaView executable path"))
        self.form.label_outputdir.setText(_("Default output directory"))
        self.form.label_5.setText(_("Template Case"))
        tool_tip_mes = _("The OpenFOAM install folder (e.g. 'OpenFOAM-xxx').")
        self.form.le_foam_dir.setToolTip(tool_tip_mes)
        tool_tip_mes = _("The full path of the ParaView executable.")
        self.form.le_paraview_path.setToolTip(tool_tip_mes)
        tool_tip_mes = _("The default output directory ('model_dir' if the same of FreeCAD Model File).")
        self.form.le_output_dir.setToolTip(tool_tip_mes)
        tool_tip_mes = _("Template Case Folder")
        self.form.le_template_case.setToolTip(tool_tip_mes)

        self.thread = None
        self.install_process = None

        self.console_message = ""

        self.foam_dir = ""
        self.initial_foam_dir = ""

        self.paraview_path = ""
        self.initial_paraview_path = ""

        self.output_dir = ""
        self.template_case = DEXCS_TEMPLATE


    def __del__(self):
        if self.thread and self.thread.isRunning():
            FreeCAD.Console.PrintMessage(_("Terminating a pending install task"))
            self.thread.terminate()
        if self.install_process and self.install_process.state() == QtCore.QProcess.Running:
            FreeCAD.Console.PrintMessage(_("Terminating a pending install task"))
            self.install_process.terminate()
        QApplication.restoreOverrideCursor()

    def saveSettings(self):
        # print("deb:saveSettings")
        # print(self.output_dir)
        # print(self.template_case)
        if os.path.isdir(self.output_dir) != True:
            self.output_dir = "model_dir"
        dexcsCfdTools.setFoamDir(self.foam_dir)
        dexcsCfdTools.setParaviewPath(self.paraview_path)
        prefs = dexcsCfdTools.getPreferencesLocation()
        FreeCAD.ParamGet(prefs).SetString("DefaultOutputPath", self.output_dir)
        FreeCAD.ParamGet(prefs).SetString("DefaultTemplateCase", self.template_case)

    def loadSettings(self):
        # Don't set the autodetected location, since the user might want to allow that to vary according
        # to WM_PROJECT_DIR setting
        prefs = dexcsCfdTools.getPreferencesLocation()
        self.foam_dir = FreeCAD.ParamGet(prefs).GetString("InstallationPath", "")
        self.initial_foam_dir = str(self.foam_dir)
        self.form.le_foam_dir.setText(self.foam_dir)

        self.paraview_path = dexcsCfdTools.getParaviewPath()
        self.initial_paraview_path = str(self.paraview_path)
        self.form.le_paraview_path.setText(self.paraview_path)

        self.output_dir = dexcsCfdTools.getDefaultOutputPath()
        self.template_case = dexcsCfdTools.getDefaultTemplateCase()
        self.form.le_output_dir.setText(self.output_dir)
        self.form.le_template_case.setText(self.template_case)

    def consoleMessage(self, message="", color="#000000"):
        message = message.replace('\n', '<br>')
        self.console_message = self.console_message + \
            '<font color="{0}">{1}</font><br>'.format(color, message)
        self.form.textEdit_Output.setText(self.console_message)
        self.form.textEdit_Output.moveCursor(QtGui.QTextCursor.End)

    def foamDirChanged(self, text):
        self.foam_dir = text
        # if self.foam_dir and os.access(self.foam_dir, os.R_OK):
        #     self.setDownloadURLs()

    def testGetRuntime(self, disable_exception=True):
        """ Set the foam dir temporarily and see if we can detect the runtime """
        prefs = dexcsCfdTools.getPreferencesLocation()
        prev_foam_dir = FreeCAD.ParamGet(prefs).GetString("InstallationPath", "")
        dexcsCfdTools.setFoamDir(self.foam_dir)
        try:
            runtime = dexcsCfdTools.getFoamRuntime()
        except IOError as e:
            runtime = None
            if not disable_exception:
                raise
        dexcsCfdTools.setFoamDir(prev_foam_dir)
        return runtime

    def paraviewPathChanged(self, text):
        self.paraview_path = text

    def chooseFoamDir(self):
        d = QtGui.QFileDialog().getExistingDirectory(None, _('Choose OpenFOAM directory'), self.foam_dir)
        if d and os.access(d, os.R_OK):
            self.foam_dir = d
        self.form.le_foam_dir.setText(self.foam_dir)

    def chooseParaviewPath(self):
        p, filter = QtGui.QFileDialog().getOpenFileName(None, _('Choose ParaView executable'), self.paraview_path,
                                                        filter="*.exe"  if platform.system() == 'Windows' else None)
        if p and os.access(p, os.R_OK):
            self.paraview_path = p
        self.form.le_paraview_path.setText(self.paraview_path)

    def outputDirChanged(self, text):
        self.output_dir = text

    def templateCaseChanged(self, text):
        self.template_case = text

    def chooseOutputDir(self):
        d = QtGui.QFileDialog().getExistingDirectory(None, _('Choose output directory'), self.output_dir)
        if d and os.access(d, os.W_OK):
            self.output_dir = os.path.abspath(d)
        self.form.le_output_dir.setText(self.output_dir)

    def chooseTemplateCase(self):
        d = QtGui.QFileDialog().getExistingDirectory(None, _('Choose template case'), self.template_case)
        if d and os.access(d, os.W_OK):
            self.template_case = os.path.abspath(d)
        self.form.le_template_case.setText(self.template_case)
