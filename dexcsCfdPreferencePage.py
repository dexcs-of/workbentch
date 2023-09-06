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
DEXCS_PATH = "/opt/DEXCS"
TREEFOAM_PATH = "/opt/TreeFoam"

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
        self.form.tb_choose_cfmesh_dir.clicked.connect(self.chooseCfmeshDir)
        self.form.le_cfmesh_dir.textChanged.connect(self.cfmeshDirChanged)
        self.form.tb_choose_treefoam_dir.clicked.connect(self.chooseTreefoamDir)
        self.form.le_treefoam_dir.textChanged.connect(self.treefoamDirChanged)
        self.form.tb_choose_dexcs_dir.clicked.connect(self.chooseDexcsDir)
        self.form.le_dexcs_dir.textChanged.connect(self.dexcsDirChanged)
        self.form.le_plot_maxnumber.textChanged.connect(self.plotMaxnumberChanged)

        self.form.tb_choose_output_dir.clicked.connect(self.chooseOutputDir)
        self.form.le_output_dir.textChanged.connect(self.outputDirChanged)
        self.form.tb_choose_template_case.clicked.connect(self.chooseTemplateCase)
        self.form.le_template_case.setText(DEXCS_TEMPLATE)
        self.form.le_template_case.textChanged.connect(self.templateCaseChanged)

        self.form.rb_deci.clicked.connect(self.plot_MethodChanged)
        self.form.rb_last.clicked.connect(self.plot_MethodChanged)

        self.form.label_7.setText(_("OpenFOAM install directory"))
        self.form.label_7b.setText(_("ParaView executable path"))
        self.form.label_outputdir.setText(_("Default output directory"))
        self.form.label.setText(_("cfMesh install directory"))
        self.form.label_3.setText(_("TreeFoam install directory"))
        self.form.label_8.setText(_("DEXCS install directory"))
        self.form.label_4.setText(_("Plot Limit"))
        self.form.label_6.setText(_("maxNumber"))
        self.form.label_2.setText(_("method"))
        tool_tip_mes = _("The OpenFOAM install folder (e.g. 'OpenFOAM-xxx').")
        self.form.le_foam_dir.setToolTip(tool_tip_mes)
        tool_tip_mes = _("The full path of the ParaView executable.")
        self.form.le_paraview_path.setToolTip(tool_tip_mes)
        tool_tip_mes = _("The default output directory ('model_dir' if the same of FreeCAD Model File).")
        self.form.le_output_dir.setToolTip(tool_tip_mes)
        tool_tip_mes = _("Template Case Folder")
        self.form.le_template_case.setToolTip(tool_tip_mes)
        tool_tip_mes = _("cfMesh install Folder (e.g. 'openfoam...').")
        self.form.le_cfmesh_dir.setToolTip(tool_tip_mes)
        tool_tip_mes = _("TreeFoam install Folder (default '/opt/Treefoam').")
        self.form.le_treefoam_dir.setToolTip(tool_tip_mes)
        tool_tip_mes = _("DEXCS install Folder (default '/opt/DEXCS').")
        self.form.le_dexcs_dir.setToolTip(tool_tip_mes)
        tool_tip_mes = _("MaxNumber of Plots series (default non-limit)")
        self.form.le_plot_maxnumber.setToolTip(tool_tip_mes)

        self.thread = None
        self.install_process = None

        self.console_message = ""

        self.foam_dir = ""
        self.initial_foam_dir = ""

        self.cfmesh_dir = ""
        self.initial_cfmesh_dir = ""

        self.treefoam_dir = ""
        self.initial_treefoam_dir = TREEFOAM_PATH

        self.dexcs_dir = ""
        self.initial_dexcs_dir = DEXCS_PATH

        self.paraview_path = ""
        self.initial_paraview_path = ""

        self.output_dir = ""
        self.template_case = DEXCS_TEMPLATE

        self.plot_Maxnumber = ""
        self.plot_Method = "last"


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
        dexcsCfdTools.setCfmeshDir(self.cfmesh_dir)
        dexcsCfdTools.setTreefoamDir(self.treefoam_dir)
        dexcsCfdTools.setDexcsDir(self.dexcs_dir)
        dexcsCfdTools.setPlot_Maxnumber(self.plot_Maxnumber)
        dexcsCfdTools.setPlot_Method(self.plot_Method)
        prefs = dexcsCfdTools.getPreferencesLocation()
        FreeCAD.ParamGet(prefs).SetString("DefaultOutputPath", self.output_dir)
        FreeCAD.ParamGet(prefs).SetString("DefaultTemplateCase", self.template_case)
        FreeCAD.ParamGet(prefs).SetString("DefaultPlotMaxnumber", self.plot_Maxnumber)
        FreeCAD.ParamGet(prefs).SetString("DefaultPlotMethodr", self.plot_Method)

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

    def cfmeshDirChanged(self, text):
        self.cfmesh_dir = text

    def treefoamDirChanged(self, text):
        self.treefoam_dir = text

    def dexcsDirChanged(self, text):
        self.dexcs_dir = text

    def plotMaxnumberChanged(self, text):
        self.plot_Maxnumber = text

    def plot_MethodChanged(self, text):
        if self.form.rb_last.isChecked() :
            self.plot_Method = "last"
        else:
            self.plot_Method = "deci"

    def chooseFoamDir(self):
        d = QtGui.QFileDialog().getExistingDirectory(None, _('Choose OpenFOAM directory'), self.foam_dir)
        if d and os.access(d, os.R_OK):
            self.foam_dir = d
        self.form.le_foam_dir.setText(self.foam_dir)

    def chooseCfmeshDir(self):
        d = QtGui.QFileDialog().getExistingDirectory(None, _('Choose cfMesh directory'), self.cfmesh_dir)
        if d and os.access(d, os.R_OK):
            self.cfmesh_dir = d
        self.form.le_foam_dir.setText(self.foam_dir)

    def chooseTreefoamDir(self):
        d = QtGui.QFileDialog().getExistingDirectory(None, _('Choose TreeFoam directory'), self.treefoam_dir)
        if d and os.access(d, os.R_OK):
            self.treefoam_dir = d
        self.form.le_foam_dir.setText(self.foam_dir)

    def chooseDexcsDir(self):
        d = QtGui.QFileDialog().getExistingDirectory(None, _('Choose DEXCS directory'), self.dexcs_dir)
        if d and os.access(d, os.R_OK):
            self.dexcs_dir = d
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
