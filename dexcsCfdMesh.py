# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2016 - Bernd Hahnebach <bernd@bimstatik.org>            *
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

from __future__ import print_function

import FreeCAD
import FreeCADGui
from PySide import QtCore
import dexcsCfdTools
from dexcsCfdTools import addObjectProperty
import os
import pythonVerCheck
# import sys
# import gettext

# localedir = os.path.expanduser("~") + "/.FreeCAD/Mod/dexcsCfdOF/locale"
# if sys.version_info.major == 3:
# 	gettext.install("dexcsCfMeshSetting", localedir)
# else:
# 	gettext.install("dexcsCfMeshSetting", localedir, unicode=True)


def makeCfdMesh(name="CFDMesh"):
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", name)
    _CfdMesh(obj)
    if FreeCAD.GuiUp:
        _ViewProviderCfdMesh(obj.ViewObject)
    return obj


class _CommandCfdMeshFromShape:
    def GetResources(self):
        icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "mesh.png")
        return {'Pixmap': icon_path,
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Cfd_MeshFromShape",
                                                     "CFD mesh"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Cfd_MeshFromShape",
                                                    _("Create a mesh using cfMesh, snappyHexMesh or gmsh"))}

    def IsActive(self):
        sel = FreeCADGui.Selection.getSelection()
        analysis = dexcsCfdTools.getActiveAnalysis()
        return analysis is not None and sel and len(sel) == 1 and sel[0].isDerivedFrom("Part::Feature")

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create CFD mesh")
        analysis_obj = dexcsCfdTools.getActiveAnalysis()
        if analysis_obj:
            meshObj = dexcsCfdTools.getMesh(analysis_obj)
            if not meshObj:
                sel = FreeCADGui.Selection.getSelection()
                if len(sel) == 1:
                    if sel[0].isDerivedFrom("Part::Feature"):
                        mesh_obj_name = sel[0].Name + "_Mesh"
                        FreeCADGui.doCommand("")
                        FreeCADGui.addModule("dexcsCfdMesh")
                        FreeCADGui.doCommand("dexcsCfdMesh.makeCfdMesh('" + mesh_obj_name + "')")
                        FreeCADGui.doCommand("App.ActiveDocument.ActiveObject.Part = App.ActiveDocument." + sel[0].Name)
                        if dexcsCfdTools.getActiveAnalysis():
                            FreeCADGui.addModule("dexcsCfdTools")
                            FreeCADGui.doCommand(
                                "dexcsCfdTools.getActiveAnalysis().addObject(App.ActiveDocument.ActiveObject)")
                        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        else:
            print("ERROR: You cannot have more than one mesh object")
        FreeCADGui.Selection.clearSelection()


class _CfdMesh:
    """ CFD mesh properties """

    # they will be used from the task panel too, thus they need to be outside of the __init__
    known_element_dimensions = ['2D', '3D']
    #known_mesh_utility = ['cfMesh', 'snappyHexMesh', 'gmsh']
    known_mesh_utility = ['cfMesh', 'snappyHexMesh']
    known_workflowControls = ['none', 'templateGeneration', 'surfaceTopology', 'surfaceProjection', 'patchAssignment', 'edgeExtraction', 'boundaryLayerGeneration', 'meshOptimisation', 'boundaryLayerRefinement']
    known_patchType = ['patch', 'wall', 'symmetry', 'overset', 'cyclic', 'wedge', 'empty', 'symmetryPlane']

    def __init__(self, obj):
        self.Type = "dexcsCfdMesh"
        self.Object = obj
        obj.Proxy = self
        self.initProperties(obj)

    def initProperties(self, obj):
        #__caseName__ = os.path.splitext(os.path.basename(FreeCAD.ActiveDocument.FileName))[0]
        __caseName__ = ""
        addObjectProperty(obj, 'CaseName', __caseName__, "App::PropertyString", "",
                          "Name of directory in which the mesh is created")

        #addObjectProperty(obj, 'STLLinearDeflection', 0.05, "App::PropertyFloat", "", "STL linear deflection")

        #addObjectProperty(obj, 'NumberOfProcesses', 1, "App::PropertyInteger", "", "Number of parallel processes")

        #addObjectProperty(obj, 'NumberOfThreads', 0, "App::PropertyInteger", "",
        #                  "Number of parallel threads per process (only applicable when using cfMesh) "
        #                  "0 means use all available (if NumberOfProcesses = 1) or use 1 (if NumberOfProcesses > 1)")

        addObjectProperty(obj, "Part", None, "App::PropertyLink", "Mesh Parameters", "Part object to mesh")

        #if addObjectProperty(obj, "MeshUtility", _CfdMesh.known_mesh_utility, "App::PropertyEnumeration",
        #                     "Mesh Parameters", "Meshing utilities"):
        #    obj.MeshUtility = 'cfMesh'
        addObjectProperty(obj, "MeshUtility", _CfdMesh.known_mesh_utility, "App::PropertyEnumeration",
                               "Mesh Parameters", "Meshing utilities")
        ### <--addDexcs 
        addObjectProperty(obj, "FeatureAngle", 30, "App::PropertyFloat", "Mesh Parameters",
                          "Feature Angle of STL parts")
        addObjectProperty(obj, "ScaleToMeter", 1, "App::PropertyFloat", "Mesh Parameters",
                          "Scale Factor to meter")
        addObjectProperty(obj, "keepCellsIntersectingBoundary", True, "App::PropertyBool", "Mesh Parameters",
                          "keep template cells intersecting boundary")
        addObjectProperty(obj, "checkForGluedMesh", True, "App::PropertyBool", "Mesh Parameters",
                          "check for glued mesh")
        addObjectProperty(obj, "optimiseLayer", False, "App::PropertyBool", "Mesh Parameters",
                          "activates smoothing of boundary layers")
        addObjectProperty(obj, "opt_nSmoothNormals", 3, "App::PropertyInteger", "Mesh Parameters",
                          "number of iterations in the procedure for reducing normal variation")
        addObjectProperty(obj, "opt_maxNumIterations", 5, "App::PropertyInteger", "Mesh Parameters",
                          "maximum number of iterations of the whole procedure")
        addObjectProperty(obj, "opt_featureSizeFactor", 0.4, "App::PropertyFloat", "Mesh Parameters",
                          "ratio between the maximum layer thickness and the estimated feature size")
        addObjectProperty(obj, "opt_reCalculateNormals", True, "App::PropertyBool", "Mesh Parameters",
                          "activale 1 or deactivate 0 calculation of normal")
        addObjectProperty(obj, "opt_relThicknessTol", 0.05, "App::PropertyFloat", "Mesh Parameters",
                          "maximum allowed thickness variation of thickness between two neighbouring points, devided by the distance between the points")
        addObjectProperty(obj, "workflowControls", _CfdMesh.known_workflowControls, "App::PropertyEnumeration",
                             "Mesh Parameters", "workflowControls")
        addObjectProperty(obj, "patchTypeSetting", False, "App::PropertyBool", "Patch Type Settings",
                          "activates setting of boundary type")
        # if addObjectProperty(obj, 'patchTypeLists', [], "App::PropertyLinkList", "Patch Type Settings", "List of non-patch type boundary"):
        #      # Backward compat
        #      if 'References' in obj.PropertiesList:
        #          doc = FreeCAD.getDocument(obj.Document.Name)
        #          for r in obj.References:
        #              if not r[1]:
        #                  obj.ShapeRefs += [doc.getObject(r[0])]
        #              else:
        #                  obj.ShapeRefs += [(doc.getObject(r[0]), r[1])]
        #          obj.removeProperty('References')
        #          obj.removeProperty('LinkedObjects')

        ### addDexcs -->


        addObjectProperty(obj, "BaseCellSize", "0 m", "App::PropertyLength", "Mesh Parameters",
                          "Max mesh element size (0.0 = infinity)")

        #addObjectProperty(obj, 'PointInMesh', {"x": '0 m', "y": '0 m', "z": '0 m'}, "App::PropertyMap",
        #                  "Mesh Parameters",
        #                  "Location vector inside the region to be meshed (must not coincide with a cell face)")

        #addObjectProperty(obj, 'CellsBetweenLevels', 3, "App::PropertyInteger", "Mesh Parameters",
        #                  "Number of cells between each level of refinement")

        #addObjectProperty(obj, 'EdgeRefinement', 1, "App::PropertyFloat", "Mesh Parameters",
        #                  "Relative edge (feature) refinement")

        if addObjectProperty(obj, 'ElementDimension', _CfdMesh.known_element_dimensions, "App::PropertyEnumeration",
                             "Mesh Parameters", "Dimension of mesh elements (Default 3D)"):
            obj.ElementDimension = '3D'

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state


class _ViewProviderCfdMesh:
    """ A View Provider for the CfdMesh object """
    def __init__(self, vobj):
        #print('debug0')
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(dexcsCfdTools.get_module_path(), "Gui", "Resources", "icons", "mesh.png")
        return icon_path

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def updateData(self, obj, prop):
        #print('debug1'+obj.Label)
        return

    def onChanged(self, vobj, prop):
        #print('debug5'+vobj.Object.Name)
        dexcsCfdTools.setCompSolid(vobj)
        return

    def setEdit(self, vobj, mode):
        #print('debug4 '+vobj.Object.Name)
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, _CfdMesh):
                obj.ViewObject.show()
        #print('debug6'+self.Object.Name)
        import _dexcsTaskPanelCfdMesh
        taskd = _dexcsTaskPanelCfdMesh._TaskPanelCfdMesh(self.Object)
        taskd.obj = vobj.Object
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    def doubleClicked(self, vobj):
        if FreeCADGui.activeWorkbench().name() != 'dexcsCfdOFWorkbench':
            FreeCADGui.activateWorkbench("dexcsCfdOFWorkbench")
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        # it should be possible to find the AnalysisObject although it is not a documentObjectGroup
        if not dexcsCfdTools.getActiveAnalysis():
            analysis_obj = dexcsCfdTools.getParentAnalysisObject(self.Object)
            if analysis_obj:
                dexcsCfdTools.setActiveAnalysis(analysis_obj)
            else:
                FreeCAD.Console.PrintError(
                    _("No Active Analysis is detected from solver object in the active Document!\n"))
        if not doc.getInEdit():
            if dexcsCfdTools.getActiveAnalysis().Document is FreeCAD.ActiveDocument:
                if self.Object in dexcsCfdTools.getActiveAnalysis().Group:
                    doc.setEdit(vobj.Object.Name)
                else:
                    FreeCAD.Console.PrintError(_("Activate the analysis this solver belongs to!\n"))
            else:
                FreeCAD.Console.PrintError(_("Active Analysis is not in active Document!\n"))
        else:
            FreeCAD.Console.PrintError(_("Task dialog already open\n"))
        return True

    def onDelete(self, feature, subelements):
        try:
            for obj in self.Object.Group:
                obj.ViewObject.show()
        except Exception as err:
            FreeCAD.Console.PrintError("Error in onDelete: " + str(err))
        return True

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
