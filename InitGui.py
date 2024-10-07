# **************************************************************************
# *  (c) bernd hahnebach (bernd@bimstatik.org) 2014                        *
# *  (c) qingfeng xia @ iesensor.com 2016                                  *
# *  Copyright (c) 2017 Andrew Gill (CSIR) <agill@csir.co.za>              *
# *  Copyright (c) 2019 Oliver Oxtoby <oliveroxtoby@gmail.com>             *
# *                                                                        *
# *  this file is part of the freecad cax development system.              *
# *                                                                        *
# *  this program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the gnu lesser general public license (lgpl)    *
# *  as published by the free software foundation; either version 2 of     *
# *  the license, or (at your option) any later version.                   *
# *  for detail see the licence text file.                                 *
# *                                                                        *
# *  freecad is distributed in the hope that it will be useful,            *
# *  but without any warranty; without even the implied warranty of        *
# *  merchantability or fitness for a particular purpose.  see the         *
# *  gnu lesser general public license for more details.                   *
# *                                                                        *
# *  you should have received a copy of the gnu library general public     *
# *  license along with freecad; if not, write to the free software        *
# *  foundation, inc., 59 temple place, suite 330, boston, ma  02111-1307  *
# *  usa                                                                   *
# *                                                                        *
# **************************************************************************/


class dexcsCfdOFWorkbench(Workbench):
    """ dexcsCfdOF workbench object """
    def __init__(self):
        import os
        import dexcsCfdTools
        import FreeCAD
        #icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "cfd.svg")
        icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "dexcs.svg")
        self.__class__.Icon = icon_path
        self.__class__.MenuText = "dexcsCfdOF"
        self.__class__.ToolTip = "dexcsCfdOF workbench"

        from PySide import QtCore
        from dexcsCfdPreferencePage import dexcsCfdPreferencePage
        ICONS_PATH = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons")
        QtCore.QDir.addSearchPath("icons", ICONS_PATH)
        FreeCADGui.addPreferencePage(dexcsCfdPreferencePage, "dexcsCfdOF")

        #print('debug CfdOfWB')
        #prefs = dexcsCfdTools.getPreferencesLocation()
        #FreeCAD.ParamGet(prefs).SetString("DefaultOutputPath", "")

    def Initialize(self):
        # must import QtCore in this function,
        # not at the beginning of this file for translation support
        from PySide import QtCore

        from dexcsCfdSolverSet import _CommandCfdSolverSet
        from dexcsCfdAnalysis import _CommandCfdAnalysis
        from dexcsCfdMesh import _CommandCfdMeshFromShape
        from dexcsCfdMeshRefinement import _CommandMeshRegion
        from dexcsCfdSolverFoam import _CommandCfdSolverFoam
        from dexcsCfdCheckCaseFileName import _CommandCfdCheckCaseFileName
        from dexcsCfdEditConstantFolder import _CommandCfdEditConstantFolder
        from dexcsCfdEditSystemFolder import _CommandCfdEditSystemFolder
        from dexcsCfdRunGridEditor import _CommandCfdRunGridEditor
        from dexcsCfdRunPlotWatcher import _CommandCfdRunPlotWatcher
        from dexcsCfdRunClearCase import _CommandCfdRunClearCase
        from dexcsCfdOpenOFTerminal import _CommandCfdOpenOFTerminal
        from dexcsCfdRunParaview import _CommandCfdRunParaview
        from dexcsCfdRunPlotTool import _CommandCfdRunPlotTool
        from dexcsCfdRunTreeFoam import _CommandCfdRunTreeFoam
        from dexcsCfdRunParallel import _CommandCfdRunParallel
        from dexcsCfdRundexcsPlotTable import _CommandCfdRundexcsPlotTable
        from dexcsCfdMakeCfMeshSetting import _CommandCfdMakeCfMeshSetting
        from dexcsCfdExportSTL import _CommandCfdExportSTL
        from dexcsCfdShowSolidInfo import _CommandCfdShowSolidInfo
        from dexcsCfdDowngrade import _CommandCfdDowngrade
        from dexcsCfdUpgrade import _CommandCfdUpgrade

        FreeCADGui.addCommand('Cfd_SolverSet', _CommandCfdSolverSet())
        FreeCADGui.addCommand('Cfd_Analysis', _CommandCfdAnalysis())
        FreeCADGui.addCommand('Cfd_MeshFromShape', _CommandCfdMeshFromShape())
        FreeCADGui.addCommand('Cfd_MeshRegion', _CommandMeshRegion())
        FreeCADGui.addCommand('Cfd_CheckCaseFileName', _CommandCfdCheckCaseFileName())
        FreeCADGui.addCommand('Cfd_RunGridEditor', _CommandCfdRunGridEditor())
        FreeCADGui.addCommand('Cfd_EditConstantFolder', _CommandCfdEditConstantFolder())
        FreeCADGui.addCommand('Cfd_EditSystemFolder', _CommandCfdEditSystemFolder())
        FreeCADGui.addCommand('Cfd_RunPlotWatcher', _CommandCfdRunPlotWatcher())
        FreeCADGui.addCommand('Cfd_RunClearCase', _CommandCfdRunClearCase())
        FreeCADGui.addCommand('Cfd_OpenOFTerminal', _CommandCfdOpenOFTerminal())
        FreeCADGui.addCommand('Cfd_RunParaview', _CommandCfdRunParaview())
        FreeCADGui.addCommand('Cfd_RunPlotTool', _CommandCfdRunPlotTool())
        FreeCADGui.addCommand('Cfd_RunTreeFoam', _CommandCfdRunTreeFoam())
        FreeCADGui.addCommand('Cfd_RunParallel', _CommandCfdRunParallel())
        FreeCADGui.addCommand('Cfd_RundexcsPlotTable', _CommandCfdRundexcsPlotTable())
        FreeCADGui.addCommand('Cfd_MakeCfMeshSetting', _CommandCfdMakeCfMeshSetting())
        FreeCADGui.addCommand('Cfd_ExportSTL', _CommandCfdExportSTL())
        FreeCADGui.addCommand('Cfd_ShowSolidInfo', _CommandCfdShowSolidInfo())
        FreeCADGui.addCommand('Cfd_Downgrade', _CommandCfdDowngrade())
        FreeCADGui.addCommand('Cfd_Upgrade', _CommandCfdUpgrade())

        cmdlst = ['Cfd_Analysis', 'Cfd_MeshFromShape', 
                  'Cfd_MeshRegion', 'Cfd_SolverControl', 'Cfd_SolverSet',
                  'Cfd_CheckCaseFileName', 'Cfd_RunGridEditor', 'Cfd_EditConstantFolder', 
                  'Cfd_EditSystemFolder', 'Cfd_RunPlotWatcher', 'Cfd_RunClearCase', 
                  'Cfd_OpenOFTerminal', 'Cfd_RunParaview', 'Cfd_RunPlotTool', 
                  'Cfd_RunTreeFoam', 'Cfd_RunParallel', 'Cfd_RundexcsPlotTable', 
                  'Cfd_MakeCfMeshSetting', 'Cfd_ExportSTL', 'Cfd_ShowSolidInfo', 
                  'Cfd_Downgrade', 'Cfd_Upgrade']

        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Cfd", "dexcsCfdOF")), cmdlst)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Cfd", "&dexcsCfdOF")), cmdlst)

        # enable QtCore translation here, todo


    def GetClassName(self):
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(dexcsCfdOFWorkbench())
