# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2016 - Bernd Hahnebach <bernd@bimstatik.org>            *
# *   Copyright (c) 2017 Johan Heyns (CSIR) <jheyns@csir.co.za>             *
# *   Copyright (c) 2017 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>          *
# *   Copyright (c) 2017 Alfred Bogaers (CSIR) <abogaers@csir.co.za>        *
# *   Copyright (c) 2019-2020 Oliver Oxtoby <oliveroxtoby@gmail.com>        *
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
import FreeCADGui
from dexcsCfdMesh import _CfdMesh
from PySide import QtCore
import os
import dexcsCfdTools
from dexcsCfdTools import addObjectProperty
from pivy import coin
import Part
import _dexcsTaskPanelCfdMeshRefinement
import pythonVerCheck
# import sys
# import gettext

# localedir = os.path.expanduser("~") + "/.FreeCAD/Mod/dexcsCfdOF/locale"
# if sys.version_info.major == 3:
# 	gettext.install("dexcsCfMeshSetting", localedir)
# else:
# 	gettext.install("dexcsCfMeshSetting", localedir, unicode=True)


def makeCfdMeshRefinement(base_mesh, name="MeshRefinement"):
    """ makeCfdMeshRefinement([name]):
        Creates an object to define refinement properties for a surface or region of the mesh
    """
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _CfdMeshRefinement(obj)
    if FreeCAD.GuiUp:
        _ViewProviderCfdMeshRefinement(obj.ViewObject)
    base_mesh.addObject(obj)
    return obj


class _CommandMeshRegion:

    def GetResources(self):
        icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "meshRegion.png")
        return {'Pixmap': icon_path,
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Cfd_MeshRegion", "Mesh refinement"),
                'Accel': "M, R",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Cfd_MeshRegion", _("Creates a mesh refinement"))}

    def IsActive(self):
        sel = FreeCADGui.Selection.getSelection()
        return sel and len(sel) == 1 and hasattr(sel[0], "Proxy") and isinstance(sel[0].Proxy, _CfdMesh)

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) == 1:
            sobj = sel[0]
            if len(sel) == 1 and hasattr(sobj, "Proxy") and isinstance(sobj.Proxy, _CfdMesh):
                FreeCAD.ActiveDocument.openTransaction("Create MeshRegion")
                FreeCADGui.doCommand("")
                FreeCADGui.addModule("dexcsCfdMeshRefinement")
                FreeCADGui.doCommand(
                    "dexcsCfdMeshRefinement.makeCfdMeshRefinement(App.ActiveDocument.{})".format(sobj.Name))
                FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)

        FreeCADGui.Selection.clearSelection()


class _CfdMeshRefinement:

    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "dexcsCfdMeshRefinement"
        self.initProperties(obj)

    def initProperties(self, obj):
        # Common to all
        addObjectProperty(obj, 'ShapeRefs', [], "App::PropertyLinkSubList", "", "List of mesh refinement objects")
        # if addObjectProperty(obj, 'ShapeRefs', [], "App::PropertyLinkSubList", "", "List of mesh refinement objects"):
        #     # Backward compat
        #     if 'References' in obj.PropertiesList:
        #         doc = FreeCAD.getDocument(obj.Document.Name)
        #         for r in obj.References:
        #             if not r[1]:
        #                 obj.ShapeRefs += [doc.getObject(r[0])]
        #             else:
        #                 obj.ShapeRefs += [(doc.getObject(r[0]), r[1])]
        #         obj.removeProperty('References')
        #         obj.removeProperty('LinkedObjects')

        #addObjectProperty(obj, "RelativeLength", 0.75, "App::PropertyFloat", "",
        #                  "Set relative length of the elements for this region")
        addObjectProperty(obj, "CellSize", "0 m", "App::PropertyLength", "",
                          "Set cell size for selected object(s)")
        addObjectProperty(obj, "RefinementLevel", 1, "App::PropertyInteger", "",
                          "Set refinement level for for selected object(s)")
        addObjectProperty(obj, "patchType", _CfdMesh.known_patchType, "App::PropertyEnumeration", "",
                          "Set patch boundary type for for selected object(s)")
        addObjectProperty(obj, "KeepCell", False, "App::PropertyBool", "cfMeshOption",
                          "Keep cells in the mesh template which intersect selected objects")
        addObjectProperty(obj, "RemoveCell", False, "App::PropertyBool", "cfMeshOption",
                          "Remove cells the cells intersecte by the selected objects")
        addObjectProperty(obj, "AllowDiscont", True, "App::PropertyBool", "BoundaryLayers",
                          "Allow discontinuity of boundary layers")

        addObjectProperty(obj, 'LinkedObjects', [], "App::PropertyLinkList", "", "Linked objects")

        addObjectProperty(obj, "References", [], "App::PropertyPythonObject", "",
                          "List of mesh refinement objects")

        addObjectProperty(obj, "Internal", False, "App::PropertyBool", "",
                          "Whether the refinement region is a volume rather than surface")

        #cfMesh:
        addObjectProperty(obj, "RefinementThickness", "0 m", "App::PropertyLength", "cfMeshOption",
                          "Set refinement region thickness")

        addObjectProperty(obj, "NumberLayers", 0, "App::PropertyInteger", "BoundaryLayers",
                          "Set number of boundary layers")

        addObjectProperty(obj, "ExpansionRatio", 1.2, "App::PropertyFloat", "BoundaryLayers",
                          "Set expansion ratio within boundary layers")

        addObjectProperty(obj, "FirstLayerHeight", "0 m", "App::PropertyLength", "BoundaryLayers",
                          "Set the maximum first layer height")

        # snappy:
        #addObjectProperty(obj, "RegionEdgeRefinement", 1, "App::PropertyFloat", "snappyHexMesh",
        #                  "Relative edge (feature) refinement")

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create compound part at recompute. """
        docName = str(obj.Document.Name)
        doc = FreeCAD.getDocument(docName)
        obj.LinkedObjects = []
        for ref in obj.References:
            selection_object = doc.getObject(ref[0])
            if selection_object is not None:  # May have been deleted
                if selection_object not in obj.LinkedObjects:
                    obj.LinkedObjects += [selection_object]
        shape = dexcsCfdTools.makeShapeFromReferences(obj.References, False)
        if shape is None:
            obj.Shape = Part.Shape()
        else:
            obj.Shape = shape
        if FreeCAD.GuiUp:
            vobj = obj.ViewObject
            vobj.Transparency = 20
            vobj.ShapeColor = (1.0, 0.4, 0.0)  # Orange


class _ViewProviderCfdMeshRefinement:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "meshRegion.png")
        return icon_path

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.standard = coin.SoGroup()
        vobj.addDisplayMode(self.standard, "Standard")

    def getDisplayModes(self, obj):
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        return "Shaded"

    def setDisplayMode(self, mode):
        return mode

    def updateData(self, obj, prop):
        return

    def onChanged(self, vobj, prop):
        return

    def setEdit(self, vobj, mode=0):
        for obj in FreeCAD.ActiveDocument.Objects:
           if hasattr(obj, "Proxy") and isinstance(obj.Proxy, _CfdMesh) and (self.Object in obj.Group):
               #obj.Part.ViewObject.show()
               pass
        taskd = _dexcsTaskPanelCfdMeshRefinement._TaskPanelCfdMeshRefinement(self.Object)
        taskd.obj = vobj.Object
        FreeCADGui.Control.showDialog(taskd)
        # import importlib
        # importlib.reload(_dexcsTaskPanelCfdMeshRefinement)
        # self.taskd = _dexcsTaskPanelCfdMeshRefinement._TaskPanelCfdMeshRefinement(self.Object)
        # self.taskd.obj = vobj.Object
        # FreeCADGui.Control.showDialog(self.taskd)
        return True

    def unsetEdit(self, vobj, mode=0):
        FreeCADGui.Control.closeDialog()
        return

    def doubleClicked(self, vobj):
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError('Task dialog already open\n')
        return True

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
