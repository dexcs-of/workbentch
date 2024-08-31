# -*- coding: utf-8 -*-
"""
Copyright (C) 2014 xxxx, xxxx all rights reserved.
2017/5/26 modified for cfMesh v-1.1.2
2018/9 modified for wx to QtGui
2019/4/21 some bug fix for import error
2019/4/30 some options , CellSize / RefLevel / ( MakeCartesianMesh )
"""
from re import T
import FreeCAD
import Mesh
from PySide import QtCore, QtGui
from PySide.QtGui import *
from functools import partial
from decimal import Decimal
import sys
import os.path
#import gettext
import tempfile
import math
import subprocess
from subprocess import Popen
from FreeCAD import Units
import pythonVerCheck
import pyDexcsSwakSubset
from dexcsCfdMesh import _CfdMesh
from dexcsMeshTools import MainControl, Model
import Part                

class SHMeshTools(MainControl):
    def __init__(self):
        super().__init__()
        self.BLK_MESH_DICT_STR = 'system/blockMeshDict'
        self.SH_MESH_DICT_STR = "system/snappyHexMeshDict"
        
    def makeBlockMeshDict(self, CaseFilePath):
        """
        objSettingのGUIパネルにて指定した各種パラメタを読み取って、OpenFOAMに必要なmeshDictを作成する
        """
        from dexcsCfdMeshRefinement import _CfdMeshRefinement

        dictName = CaseFilePath + MainControl.SLASH_STR + self.BLK_MESH_DICT_STR
        meshDict = open(dictName , 'w')
        #dexcsCfdDict = True
        dexcsCfdDict_maxCellSize = self.mesh_obj.BaseCellSize * self.mesh_obj.ScaleToMeter
        dexcsCfdDict_minCellSize = Model.EMPTY_STR
        dexcsCfdDict_untangleLayerCHKOption = 0
        dexcsCfdDict_optimiseLayerCHKOption = self.mesh_obj.optimiseLayer
        dexcsCfdDict_opt_nSmoothNormals= str(self.mesh_obj.opt_nSmoothNormals)
        dexcsCfdDict_opt_maxNumIterations= str(self.mesh_obj.opt_maxNumIterations)
        dexcsCfdDict_opt_featureSizeFactor= str(self.mesh_obj.opt_featureSizeFactor)
        if self.mesh_obj.opt_reCalculateNormals==1:
            dexcsCfdDict_opt_reCalculateNormalsCHKOption = "1"
        else:
            dexcsCfdDict_opt_reCalculateNormalsCHKOption = "0"
        dexcsCfdDict_opt_relThicknessTol= str(self.mesh_obj.opt_relThicknessTol)
        dexcsCfdDict_keepCellsIntersectingBoundaryCHKOption = self.mesh_obj.keepCellsIntersectingBoundary

        if self.mesh_obj.workflowControls == 'none':
            stopAfterString = '\t//\tstopAfter\tedgeExtraction;\n'
        else:
            stopAfterString = '\t\tstopAfter\t' + self.mesh_obj.workflowControls +';\n'
        regionNumber = 0
        strings = [
               'FoamFile\n', 
               '{\n', 
               '\tversion    4.0;\n', 
               '\tformat    ascii;\n',
               '\tclass    dictionary;\n',
               '\tlocation    "system";\n',
               '\tobject    blockMeshDict;\n',
               '}\n',
               '\n'
               ]
        meshDict.writelines(strings)
        bC = 5
        cell_size = Units.Quantity(self.mesh_obj.BaseCellSize).Value
        offset = bC * cell_size
        nx = int(math.ceil((self.mesh_obj.BoundingBoxMax.x-self.mesh_obj.BoundingBoxMin.x)/self.mesh_obj.BaseCellSize)+2*bC)
        ny = int(math.ceil((self.mesh_obj.BoundingBoxMax.y-self.mesh_obj.BoundingBoxMin.y)/self.mesh_obj.BaseCellSize)+2*bC)
        nz = int(math.ceil((self.mesh_obj.BoundingBoxMax.z-self.mesh_obj.BoundingBoxMin.z)/self.mesh_obj.BaseCellSize)+2*bC)
        strings = [
            f'xMin    {(self.mesh_obj.BoundingBoxMin.x-offset) * self.mesh_obj.ScaleToMeter};\n',
            f'xMax    {(self.mesh_obj.BoundingBoxMax.x+offset) * self.mesh_obj.ScaleToMeter};\n',
            f'yMin    {(self.mesh_obj.BoundingBoxMin.y-offset) * self.mesh_obj.ScaleToMeter};\n',
            f'yMax    {(self.mesh_obj.BoundingBoxMax.y+offset) * self.mesh_obj.ScaleToMeter};\n',
            f'zMin    {(self.mesh_obj.BoundingBoxMin.z-offset) * self.mesh_obj.ScaleToMeter};\n',
            f'zMax    {(self.mesh_obj.BoundingBoxMax.z+offset) * self.mesh_obj.ScaleToMeter};\n',
            f'cellsX  {nx};\n',
            f'cellsY  {ny};\n',
            f'cellsZ  {nz};\n',
            '\n'
            ]
        meshDict.writelines(strings)
        strings = [
            'vertices\n',
            '(\n',
            '\t( $xMin  $yMin  $zMin )\n',
            '\t( $xMax  $yMin  $zMin )\n',
            '\t( $xMax  $yMax  $zMin )\n',
            '\t( $xMin  $yMax  $zMin )\n',
            '\t( $xMin  $yMin  $zMax )\n',
            '\t( $xMax  $yMin  $zMax )\n',
            '\t( $xMax  $yMax  $zMax )\n',
            '\t( $xMin  $yMax  $zMax )\n',
            ');\n',
            '\n',
            'blocks\n',
            '(\n',
            '\thex (0 1 2 3 4 5 6 7) ($cellsX $cellsY $cellsZ) simpleGrading (1 1 1)\n',
            ');\n',
            '\n',
            'edges\n',
            '(\n',
            ');\n',
            '\n',
            'boundary\n',
            '(\n',
            '\txMin\n',
            '\t{\n',
            '\t\ttype patch;\n',
            '\t\tfaces\n',
            '\t\t(\n',
            '\t\t\t(0 4 7 3)\n',
            '\t\t);\n',
            '\t}\n',
            '\txMax\n',
            '\t{\n',
            '\t\ttype patch;\n',
            '\t\tfaces\n',
            '\t\t(\n',
            '\t\t\t(1 5 6 2)\n',
            '\t\t);\n',
            '\t}\n',
            '\tyMin\n',
            '\t{\n',
            '\t\ttype patch;\n',
            '\t\tfaces\n',
            '\t\t(\n',
            '\t\t\t(0 1 2 3)\n',
            '\t\t);\n',
            '\t}\n',
            '\tyMax\n',
            '\t{\n',
            '\t\ttype patch;\n',
            '\t\tfaces\n',
            '\t\t(\n',
            '\t\t\t(4 5 6 7)\n',
            '\t\t);\n',
            '\t}\n',
            '\tzMin\n',
            '\t{\n',
            '\t\ttype patch;\n',
            '\t\tfaces\n',
            '\t\t(\n',
            '\t\t\t(1 0 4 5)\n',
            '\t\t);\n',
            '\t}\n',
            '\tzMax\n',
            '\t{\n',
            '\t\ttype patch;\n',
            '\t\tfaces\n',
            '\t\t(\n',
            '\t\t\t(3 7 6 2)\n',
            '\t\t);\n',
            '\t}\n',
            ');\n'
        ]
        meshDict.writelines(strings)
        meshDict.close()
    
    def makeSurfaceFeatureExtractDict(self, CaseFilePath):
        dictName = CaseFilePath + MainControl.SLASH_STR + 'system/surfaceFeatureExtractDict'
        print('surf: ', dictName)
        meshDict = open(dictName , 'w')
        modelName = os.path.splitext(os.path.basename(FreeCAD.ActiveDocument.FileName))[0]
        strings = ['FoamFile\n','{\n','\tversion     4.0;\n', '\tformat      ascii;\n', 
                   '\tclass       dictionary;\n', '\tlocation    "system";\n',
                   '\tobject      surfaceFeatureExtractDict;\n', '}\n',
                   f'\t"{modelName}.stl"\n',
                   '{\n', '\textractionMethod    extractFromSurface;\n',
                   '\textractFromSurfaceCoeffs\n','\t{\n', 
                   '\t\tincludedAngle   150;\n','\t}\n','\twriteObj            yes;\n','}\n']
        meshDict.writelines(strings)
        meshDict.close()


    def makeSHMeshDict(self, CaseFilePath, feature_angle):
        from dexcsCfdMeshRefinement import _CfdMeshRefinement
        dictName = CaseFilePath + MainControl.SLASH_STR + self.SH_MESH_DICT_STR
        meshDict = open(dictName , 'w')
        #dexcsCfdDict = True
        dexcsCfdDict_maxCellSize = self.mesh_obj.BaseCellSize * self.mesh_obj.ScaleToMeter
        dexcsCfdDict_minCellSize = Model.EMPTY_STR
        dexcsCfdDict_untangleLayerCHKOption = 0
        dexcsCfdDict_optimiseLayerCHKOption = self.mesh_obj.optimiseLayer
        dexcsCfdDict_opt_nSmoothNormals= str(self.mesh_obj.opt_nSmoothNormals)
        dexcsCfdDict_opt_maxNumIterations= str(self.mesh_obj.opt_maxNumIterations)
        dexcsCfdDict_opt_featureSizeFactor= str(self.mesh_obj.opt_featureSizeFactor)
        strings = \
"""FoamFile
{
    version     4.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      snappyHexMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMesh true;
snap            true;
addLayers       true;
"""
        meshDict.write(strings)
        modelName = os.path.splitext(os.path.basename(FreeCAD.ActiveDocument.FileName))[0]
        strings = [
        'geometry\n',
        '{\n',
        f'\t"{modelName}.stl"\n',
        '\t{\n',
        '\t\ttype triSurfaceMesh;\n',
        f'\t\tname {modelName};\n',
        '\t}\n',
        '}\n']
        meshDict.writelines(strings)

        strings = [
        'castellatedMeshControls\n',
        '{\n',
        '\tmaxLocalCells 100000000;\n',
        '\tmaxGlobalCells 2000000000;\n',
        '\tminRefinementCells 0;\n',
        '\tmaxLoadUnbalance 0.10;\n',
        f'\tnCellsBetweenLevels {self.mesh_obj.CellsBetweenLevels};\n']
        meshDict.writelines(strings)
        strings = ['features\n', '(\n', '\t{\n', f'\t\tfile "{modelName}.eMesh";\n', '\t\tlevel 0;\n', '\t}\n', ');\n']
        meshDict.writelines(strings)
        strings = [
        '\trefinementSurfaces\n',
        '\t{\n',
        f'\t\t{modelName}\n',
        '\t\t{\n',
        '\t\t\tlevel (0 0);\n',
        ]
        doc = FreeCAD.activeDocument()
        strings += ['\t\t\tregions\n', '\t\t\t{\n']
        for obj in doc.Objects:
            #print('search obj::',obj)
            if obj.ViewObject.Visibility:
                lenObjLabel = len(obj.Label)
                skipLabel = 0
                if lenObjLabel>6:
                    if obj.Label[0:7] == 'CFDMesh':
                        skipLabel = 1
                    if obj.Label[0:7] == 'CfdSolv':
                        skipLabel = 1
                    if obj.Label[0:7] == 'MeshRef':
                        skipLabel = 1
                    if obj.Label[0:7] == 'dexcsCf':
                        skipLabel = 1
                if skipLabel != 0:
                    continue
                strings += [         
                        f'\t\t\t\t{obj.Label}\n',
                        '\t\t\t\t{\n',
                        '\t\t\t\t\tlevel (0 0);\n',
                        '\t\t\t\t\tpatchInfo\n',
                        '\t\t\t\t\t{\n',
                        '\t\t\t\t\t\ttype patch;\n',
                        '\t\t\t\t\t}\n',
                        '\t\t\t\t}\n'
                        ]
        strings += ['\t\t\t}\n', '\t\t}\n']
        strings += ['\t}\n']
        strings += [f'\tresolveFeatureAngle {feature_angle};\n']
        strings += [f'\tplanarAngle {feature_angle};\n']
        strings += ['\trefinementRegions\n', '\t{\n', '\t}\n']
        px = Units.Quantity(self.mesh_obj.PointInMesh.get('x')).Value
        py = Units.Quantity(self.mesh_obj.PointInMesh.get('y')).Value
        pz = Units.Quantity(self.mesh_obj.PointInMesh.get('z')).Value
        strings += [f'\tlocationInMesh ({px} {py} {pz});\n', '\tallowFreeStandingZoneFaces true;\n']
        strings += ['}\n']
        meshDict.writelines(strings)
        strings = ['snapControls\n', '{\n', 
            '\tnSmoothPatch 3;\n',
            '\ttolerance 1.0;\n'
            '\tnSolveIter 100;\n',
            '\tnRelaxIter 5;\n',
            '\tnFeatureSnapIter 10;\n',
            '\timplicitFeatureSnap false;\n'
            '\texplicitFeatureSnap true;\n',
            '\tmultiRegionFeatureSnap false;\n',
            '}\n']
        meshDict.writelines(strings)
        strings = ['addLayersControls\n',
            '{\n',
            '\trelativeSizes true;\n',
            '\tlayers\n',
            '\t{\n'
            f'\t\t"{modelName}_side"\n',
                '\t\t{\n',
                    '\t\t\tnSurfaceLayers 3;\n',
                    '\t\t\texpansionRatio 1.0;\n',
                '\t\t}\n',
            '\t}\n',
            '\texpansionRatio 1.2;\n'
            '\tfinalLayerThickness 0.3;\n'
            '\tminThickness 0.1;\n'
            '\tnGrow 0;\n'
            '\tfeatureAngle 120;\n'
            '\tnRelaxIter 3;\n'
            '\tnSmoothSurfaceNormals 1;\n'
            '\tnSmoothNormals 3;\n'
            '\tnSmoothThickness 10;\n'
            '\tmaxFaceThicknessRatio 0.5;\n'
            '\tmaxThicknessToMedialRatio 0.3;\n'
            '\tminMedialAxisAngle 90;\n'
            '\tminMedianAxisAngle 90;\n'
            '\tnBufferCellsNoExtrude 0;\n'
            '\tnLayerIter 50;\n'
        '}\n']
        meshDict.writelines(strings)
        strings = ['meshQualityControls\n',
            '{\n',
            '\tmaxNonOrtho 65;\n',
            '\tmaxBoundarySkewness 20;\n',
            '\tmaxInternalSkewness 4;\n',
            '\tmaxConcave 80;\n',
            '\tminVol 1e-13;\n',
            '\tminTetQuality -1;\n',
            '\tminArea -1;\n',
            '\tminTwist 0.01;\n',
            '\tminDeterminant 0.001;\n',
            '\tminFaceWeight 0.05;\n',
            '\tminVolRatio 0.01;\n',
            '\tminTriangleTwist -1;\n',
            '\tnSmoothScale 4;\n',
            '\terrorReduction 0.75;\n',
            '\trelaxed\n',
            '\t{\n',
                '\t\tmaxNonOrtho 75;\n',
            '\t}\n',
        '}\n',
        'mergeTolerance 1e-6;\n']
        meshDict.writelines(strings)
        """ if __patch__:
            patchNumber = 0
            strings += ['\t\tregions\n', '\t\t{\n']
            for objList in __patch__ :
                for obj in doc.Objects:
                    if obj.Label == objList :
                        strings += [         
                        f'\t\t\t{objList}\n',
                        '\t\t\t{\n',
                        '\t\t\t\tlevel (0 0);\n',
                        '\t\t\t\tpatchInfo\n',
                        '\t\t\t\t{\n',
                        '\t\t\t\t\ttype patch;\n',
                        '\t\t\t\t}\n',
                        '\t\t\t}\n'
                        ]
            strings += ['\t\t}\n']
        strings += ['\t}\n', '}\n']
        meshDict.writelines(strings)
        meshDict.write(f'resolveFeatureAngle {feature_angle};\n')
        meshDict.write(f'planarAngle {feature_angle};\n') """
        """
            locationInMesh (%(SnappySettings/PointInMesh/x%) %(SnappySettings/PointInMesh/y%) %(SnappySettings/PointInMesh/z%));
            allowFreeStandingZoneFaces true;
        }

        snapControls
        {
            nSmoothPatch 3;
            tolerance 1.0;
            nSolveIter 100;
            nRelaxIter 5;
            nFeatureSnapIter 10;

        %{%(SnappySettings/ImplicitEdgeDetection%)
        %:True
            implicitFeatureSnap true;
            explicitFeatureSnap false;

        %:False
            implicitFeatureSnap false;
            explicitFeatureSnap true;
        %}
        }

        addLayersControls
        {
            relativeSizes true;
            layers
            {
        %{%(SnappySettings/BoundaryLayerPresent%)
        %:True
        %{%(SnappySettings/BoundaryLayers%)
                "%(0%)"
                {
                    nSurfaceLayers %(SnappySettings/BoundaryLayers/%(0%)/NumberLayers%);
                    expansionRatio %(SnappySettings/BoundaryLayers/%(0%)/ExpansionRatio%);
                }
        %}
        %}
            }

            expansionRatio 1.2;
            finalLayerThickness 0.3;
            minThickness 0.1;
            nGrow 0;
            featureAngle 120;
            nRelaxIter 3;
            nSmoothSurfaceNormals 1;
            nSmoothNormals 3;
            nSmoothThickness 10;
            maxFaceThicknessRatio 0.5;
            maxThicknessToMedialRatio 0.3;
            minMedialAxisAngle 90;
            minMedianAxisAngle 90;
            nBufferCellsNoExtrude 0;
            nLayerIter 50;
        }

        meshQualityControls
        {
            maxNonOrtho 65;

            maxBoundarySkewness 20;
            maxInternalSkewness 4;

            maxConcave 80;
            minVol 1e-13;
            minTetQuality -1;
            minArea -1;
            minTwist 0.01;
            minDeterminant 0.001;
            minFaceWeight 0.05;
            minVolRatio 0.01;
            minTriangleTwist -1;
            nSmoothScale 4;
            errorReduction 0.75;
            relaxed
            {
                maxNonOrtho 75;
            }
        }

        mergeTolerance 1e-6;

        // ************************************************************************* //
        %}
        """
        meshDict.close()

    def perform(self, CaseFilePath, TemplateCase):
    #def perform(self, CaseFilePath, meshObj):
        """
        exportボタン押下後の処理を全て行う。
        """
        #print ("MainControl::perform")

        ijk = 99
        #print(_("hello %d") % ijk)
        modelName = os.path.splitext(os.path.basename(FreeCAD.ActiveDocument.FileName))[0]
        #print(CaseFilePath)
        self.makeStlFile(CaseFilePath)
        ### step2 ### convert stl to fms file ##############################
        self.fmsFileName = CaseFilePath +  modelName + ".fms"
        #print('outputFms=' + self.fmsFileName)
        _ScaleToMeter = MainControl.SPACE_STR + str(self.mesh_obj.ScaleToMeter)
        #print(_ScaleToMeter)
        _featureAngle = MainControl.SPACE_STR + str(self.mesh_obj.FeatureAngle)
        #print(_featureAngle)
        command = '. ' + MainControl.BASHRC_PATH_4_OPENFOAM + ";" + MainControl.SURFACE_FEATURE_TRANS
        command = command + MainControl.SPACE_STR + "'(" + _ScaleToMeter + _ScaleToMeter + _ScaleToMeter + ")'"
        command = command + MainControl.SPACE_STR + self.stlFileName + MainControl.SPACE_STR + self.stlFileName + ";"
        command = command + MainControl.SURFACE_FEATURE_EDGES
        command = command + _featureAngle              
        command = command + MainControl.SPACE_STR + self.stlFileName + MainControl.SPACE_STR
        command = command + self.fmsFileName
        #print("command =" + command)
        os.system(command)


        constantFolder = CaseFilePath + "constant" 

        # OpenFOAMのケースフォルダでない場合の処理を追加（2019/8/2）
        # if not os.path.isdir(constantFolder):
        #     command = "mkdir " + constantFolder
        #     os.system(command)

        # systemFolder = CaseFilePath + "/system" 
        # if not os.path.isdir(systemFolder):
        #     command = "mkdir " + systemFolder
        #     os.system(command)
        #     command = "cp " + self.CFMESH_PATH_TEMPLATE + "/system/fv* " + systemFolder + "/"
        #     os.system(command)
        #     command = "cp " + self.CFMESH_PATH_TEMPLATE + "/system/controlDict "  + systemFolder + "/"
        #     #print("command =" + command)
        #     os.system(command)
        # OpenFOAMのケースフォルダでない場合の処理を追加（2019/9/6）
        if TemplateCase:
            templateSolver =  TemplateCase
        else:   
            templateSolver = self.SOLVER_PATH_TEMPLATE
        #print('templateSolver',templateSolver)
        if not os.path.isdir(constantFolder):
            command = "cp -r " + templateSolver + "/constant " + CaseFilePath + "/"
            # print(command)
            os.system(command)
            command = "rm -rf " + constantFolder + "/polyMesh"
            os.system(command)

        if not os.path.isdir(constantFolder+'/triSurface'):
            command = 'mkdir ' + constantFolder + '/triSurface'
            os.system(command)

        command = 'cp ' + CaseFilePath + modelName + '.stl' + MainControl.SPACE_STR + constantFolder + '/triSurface'
        os.system(command)

        systemFolder = CaseFilePath + "system" 
        if not os.path.isdir(systemFolder):
            command = "cp -r " + templateSolver + "/system " + CaseFilePath + "/"
            os.system(command)

        zeroFolder = CaseFilePath + "0" 
        if not os.path.isdir(zeroFolder):
            tempZero = templateSolver + "/0"
            tempZeroOrig = templateSolver + "/0.orig"
            if os.path.isdir(tempZero):
                command = "cp -rf " + tempZero +  " " + CaseFilePath + "/"
            elif os.path.isdir(tempZeroOrig):
                command = "cp -rf " + tempZeroOrig +  " " + CaseFilePath + "/0"
            else :
                command = "mkdir 0"

            os.system(command)

        #copy All* script
        command = "cp -f " + templateSolver + "/All* " + CaseFilePath + "/"
        #print(command)
        os.system(command)

        if os.path.exists(CaseFilePath + "/Allrun"):
            command = "mv " + CaseFilePath + "/Allrun " + CaseFilePath + "/Allrun.orig"
            #print(command)
            os.system(command)

        #self.makeMeshDict(CaseFilePath, meshObj)
        self.makeBlockMeshDict(CaseFilePath)
        self.makeSurfaceFeatureExtractDict(CaseFilePath)
        self.makeSHMeshDict(CaseFilePath, float(self.mesh_obj.FeatureAngle))
        os.chdir(CaseFilePath)
        #cfmeshの実行ファイル作成
        caseName = CaseFilePath
        title =  "#!/bin/bash\n"
        envSet = ". " + MainControl.BASHRC_PATH_4_OPENFOAM + ";\n"
        solverSet = "blockMesh | tee blockmesh.log\n"
        sleep = "sleep 2\n"
        cont = title + envSet + solverSet + sleep
        cont += "surfaceFeatureExtract | tee surfaceFeatureExtract.log\n"
        cont += "sleep 2\n"
        cont += "snappyHexMesh | tee snappyHexMesh.log\n"
        cont += "sleep 2\n"
        f=open("./Allmesh","w")
        f.write(cont)
        f.close()
        #実行権付与
        os.system("chmod a+x Allmesh")

        solverSet = "checkMesh | tee checkMesh.log\n"
        sleep = "sleep 2\n"
        cont = title + envSet + solverSet + sleep
        f=open("./Allcheck","w")
        f.write(cont)
        f.close()
        #実行権付与
        os.system("chmod a+x Allcheck")

