# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2013-2015 - Juergen Riegel <FreeCAD@juergen-riegel.net> *
# *   Copyright (c) 2015 - Qingfeng Xia <qingfeng.xia()eng.ox.ac.uk>        *
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

import FreeCAD
import dexcsCfdTools
from dexcsCfdTools import addObjectProperty
import os
import os.path
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
import pythonVerCheck

class _CommandCfdExportSTL:
    def GetResources(self):
        icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "Tree_Dimension.svg")
        return {'Pixmap': icon_path,
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Cfd_ExportSTL", "export STL"),
                'Accel': "S, P",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Cfd_ExportSTL", _("export STL"))}

    #def IsActive(self):
    #    return dexcsCfdTools.getActiveAnalysis() is not None

    def Activated(self):
        dexcsCfdTools.hide_parts_show_meshes()
        isPresent = False
        members = dexcsCfdTools.getActiveAnalysis().Group
        for i in members:
            if isinstance(i.Proxy, _CommandCfdExportSTL):
                FreeCADGui.activeDocument().setEdit(i.Name)
                isPresent = True

        # Allowing user to re-create if CFDSolver was deleted.
        if not isPresent:
            #FreeCADGui.runCommand('Std_Macro_8',0)
            #import exportStl
            _macroPath = os.path.expanduser("~")+'/.local/share/FreeCAD/Mod/dexcsCfdOF/Macro'
            _prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").GetString('MacroPath')
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").SetString('MacroPath',_macroPath)
            FreeCADGui.runCommand('Std_Macro_8',0)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").SetString('MacroPath',_prefs)
if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Cfd_ExportSTL', _CommandCfdExportSTL())

