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

import pythonVerCheck
import pyDexcsSwakSubset
from dexcsCfdMesh import _CfdMesh
import dexcsCfdTools
App = FreeCAD

class Test(QDialog):
    def __init__(self,parent=None):
        super(Test, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        patchList = ['dexcs', 'inlet', 'outlet', 'wall']
        for patchName in patchList:
            print(patchName)
            newitem = QTableWidgetItem(patchName)
            self.ui._addrow(newitem)


class Model:
    """
    現在読み込んでいるfreeCADファイルの情報を格納する為のクラス
    """
    PATCH_STR        = "patch"
    LOCAL_STR        = "local"
    EMPTY_STR        = ""
    INF_STR          = "inf"

    def __init__(self, caseFilePath):
        """
        @type caseFilePath: string 
        @param caseFilePath:caseFilePath:freeCADの開いているfcstdファイルのpath
        """
        #print("Model")
        self.caseFilePath = caseFilePath
        
    def open(self):
        """
        コンストラクタで与えられたcaseFilePathのファイルを開いて戻す。
        @rtype: FreeCADで定義するdoc
        @return: 読み込んだFreeCADファイルオブジェクト
        """
        try:
            import sys
            sys.path.append("/usr/lib/freecad/lib")
            import FreeCAD
            import Part
        except ValueError:
            message = _(u'FreeCAD library not found. Check the FREECADPATH variable.')        
            answer = self.showMessageDialog(message)
        #self.doc = FreeCAD.open(self.caseFilePath)
        self.doc = App.ActiveDocument
        assert(self.doc != None), "None self.doc"
        return self.doc
                

class MainControl():
    """
    このアプリの全般的管理を行う為のクラス
    """
    F_1_2_STR         = "1.2"
    MAX_CELL_SIZE_STR = "maxCellSize"
    MIN_CELL_SIZE_STR = "minCellSize"
    FEATURE_ANGLE_STR = "feature<BR>Angle"
    UNTANGLE_LAYER = "untangle<BR>Layers"
    FEATURE_ANGLE     = 30
    configDict = pyDexcsSwakSubset.readConfigDexcs()
    PATH_4_OPENFOAM = configDict["cfMesh"]
    #PATH_4_OPENFOAM = "/opt/OpenFOAM/OpenFOAM-v1906"
    BASHRC_PATH_4_OPENFOAM = PATH_4_OPENFOAM + "/etc/bashrc"
    CFMESH_PATH_TEMPLATE = PATH_4_OPENFOAM + "/modules/cfmesh/tutorials/cartesianMesh/singleOrifice"
    SOLVER_PATH_TEMPLATE = os.path.expanduser(configDict["dexcs"] + "/template/dexcs")
    #SOLVER_PATH_TEMPLATE = "/opt/DEXCS/template/dexcs"
    SLASH_STR             = "/"
    DOT_STR               = "."
    DOT_SLASH             = "./"
    SURFACE_FEATURE_EDGES = "surfaceFeatureEdges -angle"
    SURFACE_FEATURE_TRANS = "surfaceTransformPoints -scale"
    CARTESIAN_MESH        = "cartesianMesh"
    DOT_FMS_STR           = ".fms"
    SPACE_STR             = " "
    MV_STR                = "mv"
    SED_STR               = "sed"
    REGION_STR            = "region"
    E_OPTION_STR          = "-e"
    S_EMPTY_STR           = "s/empty/"
    RM_F_STR              = "rm -f"
    MESH_DICT_STR         = "system/meshDict"
    OBJECT_STR            = "object"

    def __init__(self):
        """
        get mesh container of active analysis container
        """
        self.analysisObject = dexcsCfdTools.getActiveAnalysis()
       
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Proxy") and isinstance(obj.Proxy, _CfdMesh):              
               self.analysis = dexcsCfdTools.getParentAnalysisObject(obj)
               if self.analysis == self.analysisObject:
                 self.mesh_obj = obj     

        #print("DEXCS MainControl / " + self.mesh_obj.Label)

    def checkMeshPerform(self, CaseFilePath):
        """
        checkMeshボタン押下後の処理を全て行う。
        """
        #print ("MainControl::checkMeshPerform")
        os.chdir(CaseFilePath)
        caseName = os.path.basename(CaseFilePath)
        f=open(caseName+".OpenFOAM","w")
        f.close()
        #checkMeshの実行ファイル作成
        title =  "#!/bin/bash\n"
        configDict = pyDexcsSwakSubset.readConfigTreeFoam()
        env = configDict["bashrcFOAM"]
        configDict = pyDexcsSwakSubset.readConfigDexcs()
        envTreeFoam = configDict["TreeFoam"]
        env = env.replace('$TreeFoamUserPath',envTreeFoam)
        envSet = "source " + env + '\n'
        solverSet = "checkMesh " + "\n"
        cont = title + envSet + solverSet 
        f=open("./run","w")
        f.write(cont)
        f.close()
        #実行権付与
        os.system("chmod a+x run")
        #実行
        #comm = "xfce4-terminal --execute ./run &"
        comm = "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
        #subprocess.call(comm .strip().split(" "))
        os.system(comm)

    def viewMeshPerform(self, CaseFilePath):
        """
        viewMeshボタン押下後の処理を全て行う。
        """
        #print ("MainControl::viewMeshPerform")
        os.chdir(CaseFilePath)
        caseName = os.path.basename(CaseFilePath)
        f=open(caseName+".OpenFOAM","w")
        f.close()
        #paraviewの実行ファイル作成
        envSet0 = ". " + os.path.expanduser("~") + "/.FreeCAD/runTreefoamSubset\n"
        title =  "#!/bin/bash\n"
        configDict = pyDexcsSwakSubset.readConfigTreeFoam()
        paraFoamFix = configDict["paraFoam"]
        envSet = envSet0 + "source " + paraFoamFix + "\n"
        solverSet = "paraFoam " + "\n"
        #cont = title + envSet + solverSet 
        cont = title + envSet 
        f=open("./run","w")
        f.write(cont)
        f.close()
        #実行権付与
        os.system("chmod a+x run")
        #実行
        comm = "xfce4-terminal --execute ./run &"
        #comm = "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
        #subprocess.call(comm .strip().split(" "))
        os.system(comm)

    def editMeshDictPerform(self, CaseFilePath):
        """
        editMeshDictボタン押下後の処理を全て行う。
        """
        #print ("MainControl::editMeshDictPerform")
        os.chdir(CaseFilePath)
        #geditの実行ファイル作成
        caseName = CaseFilePath
        title =  "#!/bin/bash\n"
        envSet = ""
        solverSet = "gedit ./system/meshDict\n"
        libPath = ""
        sleep = ""
        cont = title + envSet + libPath + solverSet + sleep
        f=open("./run","w")
        f.write(cont)
        f.close()
        #実行権付与
        os.system("chmod a+x run")
        #実行
        comm = "xfce4-terminal --execute ./run &"
        #cmd = "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile /home/et/Desktop/test/run &"
        #subprocess.call(comm .strip().split(" "))
        os.system(comm)

    def makeCartesianMeshPerform(self, CaseFilePath):
        """
        makeCartesianMeshボタン押下後の処理を全て行う。
        """
        #print ("MainControl::makeCartesianMeshPerform")
        os.chdir(CaseFilePath)
        f=open("./cfmesh.log","w")
        f.close()
        #cfmeshの実行ファイル作成
        caseName = CaseFilePath
        title =  "#!/bin/bash\n"
        envSet = ". " + MainControl.BASHRC_PATH_4_OPENFOAM + ";\n"
        solverSet = "cartesianMesh | tee cfmesh.log\n"
        sleep = "sleep 2\n"
        cont = title + envSet + solverSet + sleep
        f=open("./run","w")
        f.write(cont)
        f.close()
        #実行権付与
        os.system("chmod a+x run")
        #実行
        #comm = "xfce4-terminal --execute ./run"
        comm = "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run &"
        process = (subprocess.Popen(comm, stdout=subprocess.PIPE, shell=True).communicate()[0]).decode('utf-8')
        #print('コマンドは\n'+process+'です')
        #os.system(comm)

        #command = '. ' + MainControl.BASHRC_PATH_4_OPENFOAM + ';'
        #command = command + 'cd ' + CaseFilePath + ';'
        #command = command + MainControl.CARTESIAN_MESH

        #print("command =" + command)
        #os.system(command)
        #path_to_output_file = CaseFilePath + '/log.cartesianMesh'
        #myoutput = open(path_to_output_file,'w')
        #try:
        #    res = subprocess.call(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            #output, errors = res.communicate()
            #res = subprocess.call(command, shell=True)
            #os.system(command)
        #except:
        #    print ("Error.")


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
            #print(command)
            os.system(command)
            command = "rm -rf " + constantFolder + "/polyMesh"
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
        self.makeMeshDict(CaseFilePath)

        os.chdir(CaseFilePath)
        #cfmeshの実行ファイル作成
        caseName = CaseFilePath
        title =  "#!/bin/bash\n"
        envSet = ". " + MainControl.BASHRC_PATH_4_OPENFOAM + ";\n"
        if self.mesh_obj.ElementDimension == '2D':
            solverSet = "cartesian2DMesh | tee cfmesh.log\n"
        else:
            solverSet = "cartesianMesh | tee cfmesh.log\n"
        sleep = "sleep 2\n"
        cont = title + envSet + solverSet + sleep
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


    def makeMeshDict(self, CaseFilePath):
    #def makeMeshDict(self, CaseFilePath, meshObj):
        """
        objSettingのGUIパネルにて指定した各種パラメタを読み取って、OpenFOAMに必要なmeshDictを作成する
        """
        from dexcsCfdMeshRefinement import _CfdMeshRefinement

        dictName = CaseFilePath + MainControl.SLASH_STR + MainControl.MESH_DICT_STR
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
        dexcsCfdDict_checkForGluedMeshCHKOption = self.mesh_obj.checkForGluedMesh

        if self.mesh_obj.workflowControls == 'none':
            stopAfterString = '\t//\tstopAfter\tedgeExtraction;\n'
        else:
            stopAfterString = '\t\tstopAfter\t' + self.mesh_obj.workflowControls +';\n'


        #if self.viewControl.get_refinementOption() == 1 :
        #if (dexcsCfdDict) :
        #    strings = ['//CellSize\n']
        #else:
        #    strings = ['//RefLevel\n']
        #meshDict.writelines(strings)        

        regionNumber = 0

        strings = [
               'FoamFile\n', 
               '{\n', 
               'version    2;\n', 
               'format    ascii;\n',
               'class    dictionary;\n',
               'location    "system";\n',
               'object    meshDict;\n',
               '}\n',
               '\n',
               '// maximum cell size in the mesh (mandatory)\n',
               #'maxCellSize\t' + str(self.viewControl.get_maxCellSizeValue()) + ';\n'
               'maxCellSize\t' + str(dexcsCfdDict_maxCellSize) + ';\n'
               '\n',
               '// minimum cell size allowed in the automatic refinement procedure (optional)\n',
               ]
        meshDict.writelines(strings)

        #minCellSizeValue = self.viewControl.get_minCellSizeValue()
        minCellSizeValue = dexcsCfdDict_minCellSize
        if str(minCellSizeValue) != Model.EMPTY_STR:
            meshDict.write('minCellSize\t' + str(minCellSizeValue) + ';\n')
        else:	
            meshDict.write('//minCellSize\t' + ';\n')

        FmsFileName = os.path.basename(self.fmsFileName)

        #if self.viewControl.get_untangleLayerCHKOption() == 1 :
        if dexcsCfdDict_untangleLayerCHKOption == 1 :
            untangleLayerString = '\tuntangleLayers    0; // \n'
        else :
            untangleLayerString = '\t// untangleLayers    0; // \n'

        #if self.viewControl.get_optimiseLayerCHKOption() == 1 :
        if dexcsCfdDict_optimiseLayerCHKOption == 1 :
            optimiseLayerString = '\toptimiseLayer    1; // \n'
        else :
            optimiseLayerString = '\t// optimiseLayer    1; // \n'

        strings2 = [
                    '\n',
                    '// path to the surface mesh\n',
                    '// relative from case or absolute\n',
                    'surfaceFile\t"' + FmsFileName + '";\n',
	                '\n',
     	            '// size of the cells at the boundary (optional)\n',
          	        '// boundaryCellSize		1.5; // [m]\n', 
               		'\n',
               		'// distance from the boundary at which\n',
               		'// boundary cell size shall be used (optional)\n',
               		'// boundaryCellSizeRefinementThickness		4.5; // [m]\n' 
                    '\n',
                    'boundaryLayers\n',
                    '{\n',
                    '\t// global number of layers (optional)\n',
					'\t// nLayers 3;\n',
                    '\t\n',
                    '\t// thickness ratio (optional)\n',
					'\t// thicknessRatio 1.2;\n',
                    '\t\n',
                    '\t// max thickness of the first layer (optional)\n',
					'\t// maxFirstLayerThickness 0.5;\n',
                    '\t\n',
               		'\t// deactivate smoothing of boundary layers \n' ,
               		'\t// (optional) activated by default \n' ,
               		#'\t// untangleLayers		0; // \n' 
               		untangleLayerString , 
                    '\t\n',
               		'\t// activates smoothing of boundary layers (optional)\n' , 
               		'\t// deactivated by default \n' ,
               		#'\t// optimiseLayer		1; // \n' 
               		optimiseLayerString , 
                    '\t\n',
               		'\toptimisationParameters \n' 
               		'\t{\n'
               		'  \t\t// number of iterations in the procedure\n'
               		'  \t\t// for reducing normal variation (optional)\n'
               		#'  \t\tnSmoothNormals\t3;\n'
               		'  \t\tnSmoothNormals\t' + dexcsCfdDict_opt_nSmoothNormals + ';\n'
               		'\t\n'
               		'  \t\t// maximum number of iterations\n'
               		'  \t\t// of the whole procedure (optional)\n'
               		#'  \t\tmaxNumIterations\t5;\n'
               		'  \t\tmaxNumIterations\t' + dexcsCfdDict_opt_maxNumIterations + ';\n'
               		'\t\n'
               		'  \t\t// ratio between the maximum layer thickness\n'
               		'  \t\t// and the estimated feature size (optional)\n'
               		#'  \t\tfeatureSizeFactor\t0.4;\n'
               		'  \t\tfeatureSizeFactor\t' + dexcsCfdDict_opt_featureSizeFactor + ';\n'
               		'\t\n'
               		'  \t\t// activale 1 or deactivate 0 calculation of normal\n'
               		'  \t\t// (optional)\n'
               		#'  \t\treCalculateNormals\t1;\n'
               		'  \t\treCalculateNormals\t' + dexcsCfdDict_opt_reCalculateNormalsCHKOption + ';\n'
               		'\t\n'
               		'  \t\t// maximum allowed thickness variation of thickness\n'
               		'  \t\t// between two neighbouring points, devided by\n'
               		'  \t\t// the distance between the points (optional)\n'
               		#'  \t\trelThicknessTol\t0.01;\n'
               		'  \t\trelThicknessTol\t' + dexcsCfdDict_opt_relThicknessTol + ';\n'
               		'\t}\n'
               		'\t\n'
                    '\tpatchBoundaryLayers\n',
                    '\t{\n'
                    ]
        meshDict.writelines(strings2)

        __patch__ = []
        __nLayer__ = []
        __expRatio__ = []
        __firstLayerHeight__ = []
        __allowDiscont__ = []
        __keepCells__ = []
        __removeCells__ = []
        doc = FreeCAD.activeDocument()
        for obj in doc.Objects:
            if obj.ViewObject.Visibility:
                if hasattr(obj, "Proxy") and isinstance(obj.Proxy, _CfdMeshRefinement):
                  if dexcsCfdTools.getParentAnalysisObject(obj) == self.analysisObject:
                    if obj.NumberLayers > 1 :                    
                        #for objList in(obj.LinkedObjects):
                        for ref in(obj.ShapeRefs):
                            #__patch__.append(objList.Label) 
                            __patch__.append(ref[0].Label) 
                            __nLayer__.append(obj.NumberLayers) 
                            __expRatio__.append(obj.ExpansionRatio) 
                            __firstLayerHeight__.append(obj.FirstLayerHeight) 
                            if obj.AllowDiscont == 1:
                                __allowDiscont__.append('1')
                            else: 
                                __allowDiscont__.append('0') 
                    if obj.KeepCell == 1:
                        for ref in(obj.ShapeRefs):
                            __keepCells__.append(ref[0].Label)
                    if obj.RemoveCell == 1:
                        for ref in(obj.ShapeRefs):
                            __removeCells__.append(ref[0].Label)
        print(__keepCells__)
        print(__removeCells__)

        keepCellsListString = ""
        if __keepCells__ :
            for objList in __keepCells__:
                #keepCellsListString = keepCellsListString + "\t" + "dexcs" + "\n\t{\n\t\tkeepCells 1; //1 active or 0 inactive \n\t}\n"
                keepCellsListString = keepCellsListString + "\t" + objList + "\n\t{\n\t\tkeepCells 1; //1 active or 0 inactive \n\t}\n"
        else:
            keepCellsListString = keepCellsListString + "//\t" + "patchName" + "\n//\t{\n//\t\tkeepCells 1; //1 active or 0 inactive \n//\t}\n"

        removeCellsListString = ""
        if __removeCells__ :
            for objList in __removeCells__:
                removeCellsListString = removeCellsListString + "\t" + objList + "\n\t{\n\t\tkeepCells 0; //0 remove or 1 keep \n\t}\n"
        else:
            removeCellsListString = removeCellsListString + "//\t" + "patchName" + "\n//\t{\n//\t\tkeepCells 1; //0 remove or 1 keep \n//\t}\n"


        # nLayers, thicknessRatio // BoundaryLayer チェックされたもの
        if __patch__ :
            patchNumber = 0
            for objList in __patch__ :
                for obj in doc.Objects:
                    if obj.Label == objList :

                        FirstLayerHeight = str(__firstLayerHeight__[patchNumber]).replace('m','') 
                        FirstLayerHeight = str(float(FirstLayerHeight)*self.mesh_obj.ScaleToMeter)

                        strings3 = [         
                        '\t\t'                 +  objList + '\n',
                        '\t\t{\n',
                        '\t\t\t// number of layers (optional)\n',
                        '\t\t\tnLayers    '    + str(__nLayer__[patchNumber])+ ';\n',
                        '\t\t\n',
                        '\t\t\t// thickness ratio (optional)\n',
                        '\t\t\tthicknessRatio ' + str(__expRatio__[patchNumber])  + ';\n',
                        '\t\t\n',
                        '\t\t\t// max thickness of the first layer (optional)\n',
                        '\t\t\tmaxFirstLayerThickness ' + FirstLayerHeight + '; // [m]\n',
                        '\t\t\n',
                        '\t\t\t// active 1 or inactive 0\n',
                        '\t\t\tallowDiscontinuity ' + __allowDiscont__[patchNumber] + ';\n',
                        '\t\t}\n'
                        ]
                        patchNumber = patchNumber + 1
                meshDict.writelines(strings3)

        # nLayers, thicknessRatio // BoundaryLayer チェックされたもの
        #iRow=0
        #while (self.viewControl.get_gridTableValue(iRow,0)):
        #    iRow = iRow + 1
        #    if self.viewControl.get_gridTableValue(iRow-1,3) == 2:
        #        strings3 = [         
        #        '\t\t'                 + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
        #        '\t\t{\n',
        #        '\t\t\t// number of layers (optional)\n',
        #        '\t\t\tnLayers    '    + str(self.viewControl.get_gridTableValue(iRow-1,4)) + ';\n',
        #        '\t\t\n',
        #        '\t\t\t// thickness ratio (optional)\n',
        #        '\t\t\tthicknessRatio ' + str(self.viewControl.get_gridTableValue(iRow-1,5)) + ';\n',
        #        '\t\t\n',
        #        '\t\t\t// max thickness of the first layer (optional)\n',
        #        '\t\t\t// maxFirstLayerThickness ' + '0.5; // [m]\n',
        #        '\t\t\n',
        #        '\t\t\t// active 1 or inactive 0\n',
        #        '\t\t\tallowDiscontinuity ' + '1;\n',
        #        '\t\t}\n'
        #        ]
        #        meshDict.writelines(strings3)

        # end of nLayers, thicknessRatio 
        #print ('get_keepCellsIntersectingBoundaryCHKOption')
        #print (self.viewControl.get_keepCellsIntersectingBoundaryCHKOption())
        #if self.viewControl.get_keepCellsIntersectingBoundaryCHKOption() == 1 :
        if dexcsCfdDict_keepCellsIntersectingBoundaryCHKOption == 1 :
            keepCellsIntersectingBoundaryString = 'keepCellsIntersectingBoundary    1; // 1 keep or 0 only internal cells are used\n'
        else :
            keepCellsIntersectingBoundaryString = '// keepCellsIntersectingBoundary    1; // 1 keep or 0 only internal cells are used\n'
        if dexcsCfdDict_checkForGluedMeshCHKOption == 1 :
            keepCellcheckForGluedMeshString = 'checkForGluedMesh    1; // 1 active or 0 inactive\n'
        else :
            keepCellcheckForGluedMeshString = 'checkForGluedMesh    0; // 1 active or 0 inactive\n'

        strings4 = [
        '\t}\n',
        '}\n',
        '\n',
        '// keep template cells intersecting boundary (optional)\n',
        #'// keepCellsIntersectingBoundary    1; // 1 keep or 0 only internal cells are used\n',
        keepCellsIntersectingBoundaryString ,
        '\n',
        '// keep cells in the mesh template\n',
        '// which intersect selected pathces/subsets (optional)\n',
        '// it is active when keepCellsIntersectingBoundary\n',
        '// is switched off\n',
        'keepCellsIntersectingPatches\n',
        '{\n',
        #'// patchName\n',
        #'//\t{\n',
        #'//\t\tkeepCells 1; // 1 active or 0 inactive\n',
        #'//\t}\n',
        keepCellsListString,
        '}\n',
        '\n',
        '// remove cells where distinct parts of the mesh are joined together (optional)\n',
        '// active only when keepCellsIntersectingBoundary is active\n',
        keepCellcheckForGluedMeshString,
        '\n',
        '// remove cells the cells intersected\n',
        '// by the selected patched/subsets\n',
        '// from the mesh template (optional)\n',
        '// it is active when keepCellsIntersectingBoundary\n',
        '// is switched on\n',
        'removeCellsIntersectingPatches\n',
        '{\n',
        #'// patchName\n',
        #'//\t{\n',
        #'//\t\tkeepCells 1; // 0 remove or 1 keep\n',
        #'//\t}\n',
        removeCellsListString,
        '}\n',
        '\n',
        '// refinement zones at the surface\n',
        '// of the mesh (optional)\n',
        'localRefinement\n',
        '{\n'
        ]
        meshDict.writelines(strings4)

        # local refinement // cellSize指定されており、region以外のもの
        # iRow=0

        __patch__ = []
        __reflevel__ = []
        __refThickness__ = []
        __patchType__ = []
        doc = FreeCAD.activeDocument()
        for obj in doc.Objects:
            if obj.ViewObject.Visibility:
                if hasattr(obj, "Proxy") and isinstance(obj.Proxy, _CfdMeshRefinement):
                  if dexcsCfdTools.getParentAnalysisObject(obj) == self.analysisObject:
                    if (not obj.Internal) and (obj.RefinementLevel > 0) :                    
                        #for objList in(obj.LinkedObjects):
                        for ref in(obj.ShapeRefs):
                            #__patch__.append(objList.Label) 
                            __patch__.append(ref[0].Label) 
                            __reflevel__.append(obj.RefinementLevel) 
                            __refThickness__.append(obj.RefinementThickness) 
                            __patchType__.append(obj.patchType) 

        if __patch__ :
            print('found patchRefinement')
            patchNumber = 0
            for objList in __patch__ :
                for obj in doc.Objects:
                    if obj.Label == objList :
                        print('patch '+objList)

                        #RefStr = str(int( 1.0 / __relativeLength__[patchNumber])-1)
                        RefStr = str(__reflevel__[patchNumber])
                        RefThickness = str(__refThickness__[patchNumber]).replace('m','')
                        #RefThickness = str(float(RefThickness)/1000)
                        RefThickness = str(float(RefThickness)*self.mesh_obj.ScaleToMeter)
                        print('RefLevel '+RefStr)

                        strings5 = [
                        '\t' + objList + '\n',
                        '\t{\n',
                        '\t\t// additional refinement levels\n',
                        '\t\t// to the maxCellSize\n',
                        '\t\t additionalRefinementLevels\t' + RefStr + ';\n',
                        '\t\n',
                        '\t\t// thickness of the refinement region;\n',
                        '\t\t// away from the patch;\n',
                        '\t\t refinementThickness\t' + RefThickness + ';\n',			
                        '\t}\n'
                                   ]
                        patchNumber = patchNumber + 1
                meshDict.writelines(strings5)


        # while (self.viewControl.get_gridTableValue(iRow,0)):
        #     iRow = iRow + 1
        #     #print ('### ', self.viewControl.get_gridTableValue(iRow-1,2) , self.viewControl.get_gridTableValue(iRow-1,1))
        #     if (self.viewControl.get_gridTableValue(iRow-1,2) != Model.EMPTY_STR and 
        #         self.viewControl.get_gridTableValue(iRow-1,1) != MainControl.REGION_STR):
        #         refThickness = float(self.viewControl.get_gridTableValue(iRow-1,2)) 
        #         if self.viewControl.get_refinementOption() == 1 :
        #             refLevel = 0
        #             refValue = float(self.viewControl.get_maxCellSizeValue())/float(self.viewControl.get_gridTableValue(iRow-1,2))
        #             while refValue>1:
        #              	refLevel = refLevel + 1
        #              	refValue = refValue/2                				
        #             strings5 = [
        #             '\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
        #             '\t{\n',
        #             '\t\tcellSize\t' + str(self.viewControl.get_gridTableValue(iRow-1,2)) + ';\n',
        #             '\t\n',
        #             '\t\t// additional refinement levels\n',
        #             '\t\t// to the maxCellSize\n',
        #             '\t\t// additionalRefinementLevels\t' + str(refLevel) + ';\n',
        #             '\t\n',
        #             '\t\t// thickness of the refinement region;\n',
        #             '\t\t// away from the patch;\n',
        #             '\t\t// refinementThickness\t'  + str(refThickness) + ';\n',			
        #             '\t}\n'
        #                        ]
        #         else :
        #             refSize = str(self.viewControl.get_maxCellSizeValue())
        #             refValue = float(self.viewControl.get_maxCellSizeValue())/float(self.viewControl.get_gridTableValue(iRow-1,2))
        #             while refValue>1:
        #              	refValue = refValue - 1
        #              	refSize = str(float(refSize)/2) 
        #             strings5 = [
        #             '\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
        #             '\t{\n',
        #             '\t\t// cellSize\t' + refSize + ';\n',
        #             '\t\n',
        #             '\t\t// additional refinement levels\n',
        #             '\t\t// to the maxCellSize\n',
        #             '\t\t additionalRefinementLevels\t' + str(self.viewControl.get_gridTableValue(iRow-1,2)) + ';\n',
        #             '\t\n',
        #             '\t\t// thickness of the refinement region;\n',
        #             '\t\t// away from the patch;\n',
        #             '\t\t// refinementThickness\t'  + str(refThickness) + ';\n',			
        #             '\t}\n'
        #                        ]
        #         meshDict.writelines(strings5)

        # end of local refinement // 

        strings6 = [
        '}\n',
        '\n',
        '// refinement zones inside the mesh\n',
        '// based on primitive geometric objects (optional)\n',
        'objectRefinements\n',
        '{\n'
        ]
        meshDict.writelines(strings6)

        # object refinement // cellSize指定されており、Refinement=object
        # // Box要素であることを前提
        # iRow=0
        # while (self.viewControl.get_gridTableValue(iRow,0)):
        #     for obj in self.doc.Objects:
        #         if obj.Label == self.viewControl.get_gridTableValue(iRow,0):    
        #             iRow = iRow + 1
        #             if self.viewControl.get_gridTableValue(iRow-1,1) == MainControl.REGION_STR:
        #                 boxNumber = boxNumber + 1
        #                 xmax = obj.Shape.BoundBox.XMax
        #                 xmin = obj.Shape.BoundBox.XMin
        #                 ymax = obj.Shape.BoundBox.YMax
        #                 ymin = obj.Shape.BoundBox.YMin
        #                 zmax = obj.Shape.BoundBox.ZMax
        #                 zmin = obj.Shape.BoundBox.ZMin
        #                 centerX = 0.5*(xmax+xmin)
        #                 centerY = 0.5*(ymax+ymin)
        #                 centerZ = 0.5*(zmax+zmin)
        #            	## 2019/7/15 分割レベルとセルサイズの不整合を調整するパラメタ（objRefPar）を導入
        #                 objRefPar = 1.1 
        #                 if self.viewControl.get_refinementOption() == 1 :
        #                     strings7 = [
        #                     '\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
        #                     '\t{\n',
        #                     #'\t\tcellSize\t' + str(self.viewControl.get_gridTableValue(iRow-1,2)) + ';\n',
        #                     '\t\tcellSize\t' + str(float(self.viewControl.get_gridTableValue(iRow-1,2))*objRefPar ) + ';\n',
        #                     '\t\tcentre (' + str(centerX) + MainControl.SPACE_STR + str(centerY) + MainControl.SPACE_STR + str(centerZ) + ');\n',
        #                     '\t\tlengthX\t' + str(xmax-xmin) + ';\n',
        #                     '\t\tlengthY\t' + str(ymax-ymin) + ';\n',
        #                     '\t\tlengthZ\t' + str(zmax-zmin) + ';\n',
        #                     '\t\ttype box;\n',
        #                     '\t}\n'
        #                                 ]
        #                 else :
        #                     strings7 = [
        #                     '\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
        #                     '\t{\n',
        #                     '\t\tadditionalRefinementLevels\t' + str(self.viewControl.get_gridTableValue(iRow-1,2)) + ';\n',
        #                     '\t\tcentre (' + str(centerX) + MainControl.SPACE_STR + str(centerY) + MainControl.SPACE_STR + str(centerZ) + ');\n',
        #                     '\t\tlengthX\t' + str(xmax-xmin) + ';\n',
        #                     '\t\tlengthY\t' + str(ymax-ymin) + ';\n',
        #                     '\t\tlengthZ\t' + str(zmax-zmin) + ';\n',
        #                     '\t\ttype box;\n',
        #                     '\t}\n'
        #                                 ]
        __region__=[]
        __reflevel__ = []
        doc = FreeCAD.activeDocument()
        for obj in doc.Objects:
            if obj.ViewObject.Visibility:
                if hasattr(obj, "Proxy") and isinstance(obj.Proxy, _CfdMeshRefinement):
                  if dexcsCfdTools.getParentAnalysisObject(obj) == self.analysisObject:
                    if obj.Internal :                    
                        #for objList in(obj.LinkedObjects):
                        for ref in(obj.ShapeRefs):
                            #__region__.append(objList.Label) 
                            __region__.append(ref[0].Label) 
                            __reflevel__.append(obj.RefinementLevel) 
        if __region__ :
            for objList in __region__ :
                for obj in doc.Objects:
                    if obj.Label == objList :
                         RefStr = str(__reflevel__[regionNumber])
                         print('found '+objList)
                         if obj.isDerivedFrom("Part::Box"):
                            print(' Box')
                            print('RefLevel '+RefStr)
                            centerX = ( obj.Placement.Base.x + obj.Length.Value * 0.5 ) * self.mesh_obj.ScaleToMeter
                            centerY = ( obj.Placement.Base.y + obj.Width.Value * 0.5 ) * self.mesh_obj.ScaleToMeter
                            centerZ = ( obj.Placement.Base.z + obj.Height.Value * 0.5 ) * self.mesh_obj.ScaleToMeter
                            strings7 = [
                            '\t' + objList + '\n',
                            '\t{\n',
                            '\t\ttype box;\n',
                            '\t\tadditionalRefinementLevels\t' + RefStr + ';\n',
                            '\t\tcentre (' + str(centerX) + MainControl.SPACE_STR + str(centerY) + MainControl.SPACE_STR + str(centerZ) + ');\n',
                            '\t\tlengthX\t' + str(obj.Length.Value * self.mesh_obj.ScaleToMeter) + ';\n',
                            '\t\tlengthY\t' + str(obj.Width.Value * self.mesh_obj.ScaleToMeter) + ';\n',
                            '\t\tlengthZ\t' + str(obj.Height.Value * self.mesh_obj.ScaleToMeter) + ';\n',
                            '\t}\n'
                                         ]
                         elif obj.isDerivedFrom("Part::Sphere"):
                            print(' Sphere')
                            print('RefLevel '+RefStr)
                            centerX = obj.Placement.Base.x  * self.mesh_obj.ScaleToMeter
                            centerY = obj.Placement.Base.y  * self.mesh_obj.ScaleToMeter
                            centerZ = obj.Placement.Base.z  * self.mesh_obj.ScaleToMeter
                            strings7 = [
                            '\t' + objList + '\n',
                            '\t{\n',
                            '\t\ttype sphere;\n',
                            '\t\tadditionalRefinementLevels\t' + RefStr + ';\n',
                            '\t\tcentre (' + str(centerX) + MainControl.SPACE_STR + str(centerY) + MainControl.SPACE_STR + str(centerZ) + ');\n',
                            '\t\tradius\t' + str(obj.Radius.Value * self.mesh_obj.ScaleToMeter) + ';\n',
                            '\t\trefinementThickness\t' + '0' + ';\n',
                            '\t}\n'
                                         ]
                         elif obj.isDerivedFrom("Part::Cone"):
                            print(' Cone')
                            print('RefLevel '+RefStr)
                            center = FreeCAD.Vector(0, 0, - obj.Height.Value * self.mesh_obj.ScaleToMeter)
                            pos = FreeCAD.Vector(obj.Placement.Base.x * self.mesh_obj.ScaleToMeter, obj.Placement.Base.y * self.mesh_obj.ScaleToMeter, obj.Placement.Base.z * self.mesh_obj.ScaleToMeter + obj.Height.Value * self.mesh_obj.ScaleToMeter)
                            rot = FreeCAD.Rotation(obj.Placement.Rotation)
                            cylinderHead = FreeCAD.Placement(pos, rot, center)
                            p0X = obj.Placement.Base.x  * self.mesh_obj.ScaleToMeter
                            p0Y = obj.Placement.Base.y  * self.mesh_obj.ScaleToMeter
                            p0Z = obj.Placement.Base.z  * self.mesh_obj.ScaleToMeter
                            p1X = cylinderHead.Base.x 
                            p1Y = cylinderHead.Base.y 
                            p1Z = cylinderHead.Base.z 
                            strings7 = [
                            '\t' + objList + '\n',
                            '\t{\n',
                            '\t\ttype cone;\n',
                            '\t\tadditionalRefinementLevels\t' + RefStr + ';\n',
                            '\t\tp0 (' + str(p0X) + MainControl.SPACE_STR + str(p0Y) + MainControl.SPACE_STR + str(p0Z) + ');\n',
                            '\t\tp1 (' + str(p1X) + MainControl.SPACE_STR + str(p1Y) + MainControl.SPACE_STR + str(p1Z) + ');\n',
                            '\t\tradius0\t' + str(obj.Radius1.Value * self.mesh_obj.ScaleToMeter) + ';\n',
                            '\t\tradius1\t' + str(obj.Radius2.Value * self.mesh_obj.ScaleToMeter) + ';\n',
                            '\t}\n'
                                         ]
                         elif obj.isDerivedFrom("Part::Cylinder"):
                            print(' Cylinder')
                            print('RefLevel '+RefStr)
                            center = FreeCAD.Vector(0, 0, - obj.Height.Value * self.mesh_obj.ScaleToMeter)
                            pos = FreeCAD.Vector(obj.Placement.Base.x * self.mesh_obj.ScaleToMeter, obj.Placement.Base.y * self.mesh_obj.ScaleToMeter, (obj.Placement.Base.z + obj.Height.Value) * self.mesh_obj.ScaleToMeter)
                            rot = FreeCAD.Rotation(obj.Placement.Rotation)
                            cylinderHead = FreeCAD.Placement(pos, rot, center)
                            p0X = obj.Placement.Base.x * self.mesh_obj.ScaleToMeter
                            p0Y = obj.Placement.Base.y * self.mesh_obj.ScaleToMeter
                            p0Z = obj.Placement.Base.z * self.mesh_obj.ScaleToMeter
                            p1X = cylinderHead.Base.x 
                            p1Y = cylinderHead.Base.y 
                            p1Z = cylinderHead.Base.z 
                            strings7 = [
                            '\t' + objList + '\n',
                            '\t{\n',
                            '\t\ttype cone;\n',
                            '\t\tadditionalRefinementLevels\t' + RefStr + ';\n',
                            '\t\tp0 (' + str(p0X) + MainControl.SPACE_STR + str(p0Y) + MainControl.SPACE_STR + str(p0Z) + ');\n',
                            '\t\tp1 (' + str(p1X) + MainControl.SPACE_STR + str(p1Y) + MainControl.SPACE_STR + str(p1Z) + ');\n',
                            '\t\tradius0\t' + str(obj.Radius.Value * self.mesh_obj.ScaleToMeter) + ';\n',
                            '\t\tradius1\t' + str(obj.Radius.Value * self.mesh_obj.ScaleToMeter) + ';\n',
                            '\t}\n'
                                         ]
                         else :
                            xmax = obj.Shape.BoundBox.XMax * self.mesh_obj.ScaleToMeter
                            xmin = obj.Shape.BoundBox.XMin * self.mesh_obj.ScaleToMeter
                            ymax = obj.Shape.BoundBox.YMax * self.mesh_obj.ScaleToMeter
                            ymin = obj.Shape.BoundBox.YMin * self.mesh_obj.ScaleToMeter
                            zmax = obj.Shape.BoundBox.ZMax * self.mesh_obj.ScaleToMeter
                            zmin = obj.Shape.BoundBox.ZMin * self.mesh_obj.ScaleToMeter
                            centerX = 0.5*(xmax+xmin)
                            centerY = 0.5*(ymax+ymin)
                            centerZ = 0.5*(zmax+zmin)

                            RefStr = str(__reflevel__[regionNumber])
                            print('RefLevel '+RefStr)

                            strings7 = [
                            '\t' + objList + '\n',
                            '\t{\n',
                            '\t\tadditionalRefinementLevels\t' + RefStr + ';\n',
                            '\t\tcentre (' + str(centerX) + MainControl.SPACE_STR + str(centerY) + MainControl.SPACE_STR + str(centerZ) + ');\n',
                            '\t\tlengthX\t' + str(xmax-xmin) + ';\n',
                            '\t\tlengthY\t' + str(ymax-ymin) + ';\n',
                            '\t\tlengthZ\t' + str(zmax-zmin) + ';\n',
                            '\t\ttype box;\n',
                            '\t}\n'
                                         ]
                         regionNumber = regionNumber + 1
                meshDict.writelines(strings7)

        strings71 = [
        '\t//coneExample\n',
        '\t//{\n',
        '\t//\ttype\t\tcone;\n',
        '\t//\tcellSize\t7.51;\n',
        '\t//\tp0\t\t\t(-100 1873 -320);\n',
        '\t//\tp1\t\t\t(-560 1400 0);\n',
        '\t//\tradius0\t\t200;\n',
        '\t//\tradius1\t\t300;\n',
        '\t//}\n',
        '\t//hollowConeExample\n',
        '\t//{\n',
        '\t//\ttype\t\t\t\thollowCone;\n',
        '\t//\tadditionalRefinementLevels\t2;\n',
        '\t//\tdditional refinement relative to maxCellSize\n',
        '\t//\tp0\t\t\t\t\t(-100 1873 -320);\n',
        '\t//\tp1\t\t\t\t\t(-560 1400 0);\n',
        '\t//\tradius0_Inner\t\t200;\n',
        '\t//\tradius0_Outer\t\t300;\n',
        '\t//\tradius1_Inner\t\t200;\n',
        '\t//\tradius1_Outer\t\t300;\n',
        '\t//}\n',
        '\t//sphereExample\n',
        '\t//{\n',
        '\t//\ttype\t\t\tsphere;\n',
        '\t//\tcellSize\t\t7.51;\n',
        '\t//\tcentre\t\t\t(0 700 0);\n',
        '\t//\tradius\t\t\t200;\n',
        '\t//\trefinementThickness\t40;\n',
        '\t//}\n',
        '\t//lineExample\n',
        '\t//{\n',
        '\t//\ttype\t\tline;\n',
        '\t//\tcellSize\t7.51;\n',
        '\t//\tp0\t\t\t(-750 1000 450);\n',
        '\t//\tp1\t\t\t(-750 1500 450);\n',
        '\t//\trefinementThickness\t40;\n',
        '\t//}\n',
        '}\n' 
        ]

        #end of object refinement // 
        meshDict.writelines(strings71)

        # renaming patche's type // BoundaryLayer チェックされたもの


        strings8 = [
		'\n',
		'// refine regions intersected by surface meshes (optional)\n',
        'surfaceMeshRefinement\n',
        '{\n',
        '\t//surface\n',
        '\t//{\n',
        '\t//\tsurfaceFile "surface.stl";\n',
        '\t//\tadditionalRefinementLevels 3;\n',
        '\t//\trefinementThickness 50;\n',
        '\t//}\n',
        '\t//surface\n',
        '\t//{\n',
        '\t//\tsurfaceFile "surface.stl";\n',
        '\t//\tcellSize 1.0; // [m];\n',
        '\t//}\n',
        '}\n',
		'\n',
		'// refine regions intersected by edges meshes (optional)\n',
        'edgeMeshRefinement\n',
        '{\n',
        '\t//edgeMeshExample\n',
        '\t//{\n',
        '\t//\tedgeFile "refEdges.eMesh";\n',
        '\t//\tadditionalRefinementLevels 3;\n',
        '\t//\trefinementThickness 50;\n',
        '\t//}\n',
        '\t//cellSizeExample\n',
        '\t//{\n',
        '\t//\tedgeFile "refEdges.vtk";\n',
        '\t//\tcellSize 1.0; // [m];\n',
        '\t//\tadditionalRefinementLevels 3;\n',
        '\t//}\n',
        '}\n',
        '\n',
        'anisotropicSources\n',
        '{\n',
        '\t//boxExample\n',
        '\t//{\n',
        '\t\t// box is determined by its center\n',
        '\t\t// and the size in x, y, and z directions\n',
        '\t\t//type box;\n',
        '\t\t//centre (0 0 0); // (x y z);\n',
        '\t\t//lengthX 1000; // DX;\n',
        '\t\t//lengthY 1000; // DY;\n',
        '\t\t//lengthZ 1000; // DZ;\n',
        '\n',
        '\t\t// scaling factor in each directions\n',
        '\t\t//scaleX 1;\n',
        '\t\t//scaleY 1;\n',
        '\t\t//scaleZ 0.3;\n',
        '\t//}\n',
        '\n',
        '\t//planeExample\n',
        '\t//{\n',
        '\t\t// plane is determined by ist origin\n',
        '\t\t// and the normal vector\n',
        '\t\t//type plane;\n',
        '\t\t//normal (0 0 1);\n',
        '\t\t//origin (x y z);\n',
        '\n',
        '\t\t// scaling is applied in the positive normal\n',
        '\t\t// direction within the distance specified below\n',
        '\t\t//scalingDistance 125;\n',
        '\n',
        '\t\t// scaling factor in the normal direction\n',
        '\t\t//scalingFactor 0.5;\n',
        '\t//}\n',
        '}\n',
        '\n',
        'workflowControls\n',
        '{\n',
        '\t//\t1.templateGeneration\n',
        '\t//\t2.surfaceTopology\n',
        '\t//\t3.surfaceProjection\n',
        '\t//\t4.patchAssignment\n',
        '\t//\t5.edgeExtraction\n',
        '\t//\t6.boundaryLayerGeneration\n',
        '\t//\t7.meshOptimisation\n',
        '\t//\t8.boundaryLayerRefinement\n',
        '\n',
        #'\t//\tstopAfter\tedgeExtraction;\n',
        stopAfterString ,
        '\n',
        '\t// reads the mesh from disk and\n',
        '\t// restarts the meshing process after the latest step\n',
        '\t// please use binary instead of ascii\n',
        '\t//\trestartFromLatestStep\t1;\n',
        '}\n',
        '\n',
		'// setting used for assigning new names\n'
		'// of patches in the surface mesh when\n'
		'// transferring them onto the volume mesh (optional)\n'
        'renameBoundary\n',
        '{\n',
        '\tnewPatchNames\n',
        '\t{\n'
        ]
        meshDict.writelines(strings8)

        patchNumber = 0
        __patch__ = []
        __patchType__ = []
        doc = FreeCAD.activeDocument()
        for obj in doc.Objects:
            if obj.ViewObject.Visibility:
                if hasattr(obj, "Proxy") and isinstance(obj.Proxy, _CfdMeshRefinement):
                  if dexcsCfdTools.getParentAnalysisObject(obj) == self.analysisObject:
                    if (not obj.Internal) :                    
                        #for objList in(obj.LinkedObjects):
                        for ref in(obj.ShapeRefs):
                            #__patch__.append(objList.Label) 
                            __patch__.append(ref[0].Label) 
                            __patchType__.append(obj.patchType) 
                            patchNumber = patchNumber + 1
        #print('renameBoundary ',patchNumber)

        for obj in doc.Objects:
            #print('search obj::',obj)
            if obj.ViewObject.Visibility:

              #print('selected obj::',obj.Label)
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
              if skipLabel == 0:
                #print('selected obj::',obj.Label)
                regionLabel = 0
                #print('regionNumber is ',regionNumber)
                if regionNumber >0:
                  for iregion in range(regionNumber):
                    if obj.Label == __region__[iregion]:
                        regionLabel = 1
                        #print(obj.Label , 'is region')
                if  regionLabel == 0:

                    changeType = 0
                    if patchNumber > 0 :
                        for i in range(patchNumber):
                            #print('obj',obj.Label)
                            #print('__patch__',__patch__[i])
                            #print('__patchType__',__patchType__[i])
                            if obj.Label == __patch__[i] :
                                changeType = 1
                                _patchType = __patchType__[i]
                        #print('changeType ',changeType)
                    if changeType == 1:
                        strings9 = [
                        '\t\t' + str(obj.Label) + '\n',
                        '\t\t{\n',
                        '\t\t\tnewName '+ str(obj.Label) + ';\n',
                        '\t\t\ttype ' + _patchType + ';\n',
                        '\t\t}\n',
                        ]
                    else:
                        strings9 = [
                        '\t\t' + str(obj.Label) + '\n',
                        '\t\t{\n',
                        '\t\t\tnewName '+ str(obj.Label) + ';\n',
                        '\t\t\ttype patch;\n',
                        '\t\t}\n',
                        ]
        
                    meshDict.writelines(strings9)

        # iRow=0
        # while (self.viewControl.get_gridTableValue(iRow,0)):
        #                 iRow = iRow + 1
        #                 strings9 = [
        #                 '\t\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
        #                 '\t\t{\n',
        #                 '\t\t\tnewName '+ str(self.viewControl.get_gridTableValue(iRow-1,0)) + ';\n',
        #                 '\t\t\ttype '+ str(self.viewControl.get_gridTableValue(iRow-1,1)) + ';\n',
        #                 '\t\t}\n',
        #                 ]
        #                 meshDict.writelines(strings9)
        strings10 = [
        '\t}\n'
        '}\n',
        ]
        meshDict.writelines(strings10)

        #end of renaming patch's type // 


        meshDict.close()
        #message = _(u'The configuration file system/meshDict for cfMesh has been created.')        
        #self.viewControl.showMessageDialog(message)
        
    def modifyFms(self, outputFmsTemp):
        """
        コマンドsurfaceFeatureEdgesを使ってstl->fms変換した場合、
        デフォルトのtype名はemptyになってしまうので、これを指定のtype名に変更する（sedを使用）
        @type outputFmsTemp: string
        @param outputFmsTemp: fmsの仮のファイル名
        """
        sedCmd = MainControl.SED_STR + MainControl.SPACE_STR
        iRow = 0    # テーブルの行番号（オブジェクトの並び順）
        jType = 0    # type=region以外(stl出力されるオブジェクト)の並び順
        while (self.viewControl.get_gridTableValue(iRow,0)):
            iRow = iRow + 1
            if self.viewControl.get_gridTableValue(iRow-1,1) != MainControl.REGION_STR:
                jType = jType + 1
                sedCmd = sedCmd + MainControl.E_OPTION_STR + MainControl.SPACE_STR + "'"
                sedCmd = sedCmd + str(2+3*jType)+","+str(3+3*jType)+ MainControl.S_EMPTY_STR
                sedCmd = sedCmd + self.viewControl.get_gridTableValue(iRow-1,1)+MainControl.SLASH_STR + "'" + MainControl.SPACE_STR

        sedCmd = sedCmd + outputFmsTemp + " > " + self.fmsFileName
        os.system(sedCmd)
        os.system(MainControl.RM_F_STR + MainControl.SPACE_STR + outputFmsTemp)
        
    def makeStlFile(self, CaseFilePath):
        """
        読み込んだCADファイルに格納されたデータのうち、Typeがregion以外のオブジェクトをstlファイルとして出力する。
        """
        from dexcsCfdMeshRefinement import _CfdMeshRefinement
        print("makeStlFile")
        ijk = 111
        print('CaseFilePath = ' + CaseFilePath)
        modelName = os.path.splitext(os.path.basename(FreeCAD.ActiveDocument.FileName))[0]
        self.stlFileName = CaseFilePath + modelName + '.stl'
        self.fileName = CaseFilePath 
        print('stlFileName = ' + self.stlFileName)

        outputStlFile = open(self.stlFileName, 'w')

        # refinementRegion として指定（obj.Internal）されたパーツのLabelリストを作成
        __region__=[]
        doc = FreeCAD.activeDocument()
        for obj in doc.Objects:
            if obj.ViewObject.Visibility:
                if hasattr(obj, "Proxy") and isinstance(obj.Proxy, _CfdMeshRefinement):
                  if dexcsCfdTools.getParentAnalysisObject(obj) == self.analysisObject:
                    if obj.Internal :                    
                        for ref in(obj.ShapeRefs):
                            __region__.append(ref[0].Label) 

        for obj in doc.Objects:
            if obj.ViewObject.Visibility:
                __objs__=[]
                try:
                    if obj.Shape:
                        # obj.Labelがregion指定パーツであるかどうか判定
                        checkRegion = False
                        for objRegion in __region__:
                            if obj.Label == objRegion :
                                print('pass ' + obj.Label)
                                checkRegion=True
                        # CfdSolver / Group Object / region指定Obj を除外
                        if obj.isDerivedFrom("Part::FeaturePython") or obj.isDerivedFrom("App::DocumentObjectGroupPython") or checkRegion:
                            pass
                        else:
                            print('append '+obj.Label)
                                
                            __objs__.append(obj)
                            file=self.fileName+obj.Label+'.ast'
                            Mesh.export(__objs__,file)
                            importFile = open(file,'r')
                            temp = importFile.readlines()
                            for line in temp:
                                if 'endsolid' in line:
                                    outputStlFile.write('endsolid ' + obj.Label + '\n')
                                elif 'solid' in line:
                                    outputStlFile.write('solid ' + obj.Label + '\n')
                                else:
                                    outputStlFile.write(line)
                            importFile.close
                            os.remove(file)
                except AttributeError:
                    pass
        outputStlFile.close
            
    def setupView_for_CUI(self):
        """
        実行時引数で与えられたfcstdファイルを読み込み、Viewの初期設定を行う
        """
        import sys
        argvs = sys.argv  # コマンドライン引数を格納したリストの取得
        argc = len(argvs)
        if (argc != 2):   # 引数が足りない場合は、その旨を表示
            print ('Usage: # python %s filename' % argvs[0])
            self.caseFilePath="/home/et/Desktop/Qt4/Test/cfMesh/test/dexcs4Mesh.fcstd"
            #quit()         # プログラムの終了
        else:
            self.caseFilePath = argvs[1]
        #print("import case file path = %s" % self.caseFilePath)
        model = Model(self.caseFilePath)
        self.doc = model.open()
        self.fcListData = model.get_fcListData()
        sumOf3Edges = model.get_sumOf3EdgesOfCadObjects()
        cellMax = Decimal(sumOf3Edges/60)#適切に数値を丸める
        #print ("cellMax = %6.2lf" % cellMax)
        self.viewControl = ViewControl(self)
        self.dirName = os.path.dirname(self.caseFilePath)
        self.viewControl.setLayout(self.fcListData, self.dirName, cellMax)
        #print ("dirName = ", self.dirName)

    def setupView(self):
        """
        #実行時引数で与えられたfcstdファイルを読み込み、Viewの初期設定を行う
        """
        try:
            import sys
            sys.path.append("/usr/lib/freecad/lib")
            import FreeCAD
            import Part
        except ValueError:
            message = _('FreeCAD library not found. Check the FREECADPATH variable. ')        
            wx.MessageBox(message,'Error')

        self.caseFilePath = App.ActiveDocument.FileName        
        model = Model(self.caseFilePath)
        self.doc = model.open()
        self.fcListData = model.get_fcListData()
        sumOf3Edges = model.get_sumOf3EdgesOfCadObjects()
        cellMax = Decimal(sumOf3Edges/60)#適切に数値を丸める
        #print ("cellMax = %6.2lf" % cellMax)
        self.viewControl = ViewControl(self)
        self.dirName = os.path.dirname(self.caseFilePath)

        optionOutputPath = dexcsCfdTools.getOptionOutputPath()
        if optionOutputPath :
            #モデルファイルがケースファイルの置き場所にない場合（.CaseFileDict）
            caseFileDict = self.dirName + "/.CaseFileDict"
            if os.path.isfile(caseFileDict) == True:
                f = open(caseFileDict)
                tempDirName = f.read()
                f.close()
                if os.path.isdir(tempDirName) == True:
                    self.dirName = tempDirName
                #print(self.dirName)

        self.viewControl.setLayout(self.fcListData, self.dirName, cellMax)
        #print ("dirName = ", self.dirName)
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    def searchVal(self,x,search_str):
        for i in range(len(x)):
            if search_str in x[i] and ( not x[i].strip().startswith("/")):
                foundList=x[i].split()
                return foundList[1].replace(";","")

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    def searchVal1(self,x,i_start,search_str):
        i = i_start
        while x[i]:
            i +=1
            if search_str in x[i] and ( not x[i].strip().startswith("/")):
                foundList=x[i].split()
                return foundList[1].replace(";","")

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    def searchLocationKakko(self,y,keyWord):
        is1=0; is2=0
        for i in range(len(y)):
            if ( y[i].strip() == keyWord ) : #キーワードが見つかった
                k_pop = 0                    #カッコの深さを示すカウンター
                k_found =0                   # 最初の左カッコが見つかったどうかのフラグ    
                while (k_found == 0 ): #最初の左カッコが見つかるまで行送りする
                    i = i + 1
                    if (y[i].strip() == "{") or (y[i].strip() == "(") : #最初の左カッコが見つかった
                        is1 = i                 # 最初の左カッコが見つかった位置 
                        k_pop = k_pop + 1; k_found =1
                        while ( k_pop != 0 ):#カッコの深さが元に戻るまで行送りする
                            i = i + 1
                            #print i,k_found,k_pop
                            if (y[i].strip() == "{") or (y[i].strip() == "(") :#左カッコが見つかった
                                k_pop = k_pop + 1 #カッコの深さを＋１
                            if (y[i].strip() == "}") or (y[i].strip() == ")") or (y[i].strip() == "};") or (y[i].strip() == ");") :#右カッコが見つかった
                                k_pop = k_pop - 1 #カッコの深さをー１
                            is2 = i         # 最後の右カッコが見つかった位置（になるはず）
        return is1,is2
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    def searchLocationKakko1(self,y,iss1):
        i = iss1
        while y[i]:
            k_pop = 0                    #カッコの深さを示すカウンター
            k_found =0                   # 最初の左カッコが見つかったどうかのフラグ    
            while (k_found == 0 ): #最初の左カッコが見つかるまで行送りする
                i = i + 1
                if (y[i].strip() == "{") or (y[i].strip() == "(") : #最初の左カッコが見つかった
                    #print "##", i,k_pop, k_found
                    is1 = i                 # 最初の左カッコが見つかった位置 
                    k_pop = k_pop + 1; k_found =1
                    while ( k_pop != 0 ):#カッコの深さが元に戻るまで行送りする
                        i = i + 1
                        #print "###", i,k_found,k_pop
                        if (y[i].strip() == "{") or (y[i].strip() == "(") :#左カッコが見つかった
                            k_pop = k_pop + 1 #カッコの深さを＋１
                        if (y[i].strip() == "}") or (y[i].strip() == ")") or (y[i].strip() == "};") or (y[i].strip() == ");") :#右カッコが見つかった
                            k_pop = k_pop - 1 #カッコの深さをー１
                        if (k_pop == 0):
                            is2 = i         # 最後の右カッコが見つかった位置（になるはず）
                            return is1,is2
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

def main():
    """
    mainメソッド
    """
    global refinementOption
    refinementOption = 1

    cfMeshSettingMainControl = MainControl()
    cfMeshSettingMainControl.setupView()
    
if __name__ == '__main__':
    """
     このアプリの開始点
    """
    main()
