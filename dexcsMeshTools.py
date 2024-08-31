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
from abc import ABCMeta, abstractmethod


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
                

class MainControl(metaclass=ABCMeta):
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
        特に何もしない。
        """
        print('meshtools __init__')
        for obj in FreeCAD.ActiveDocument.Objects:
            print(obj)
            if hasattr(obj, "Proxy") and isinstance(obj.Proxy, _CfdMesh):
               self.mesh_obj = obj
        print("DEXCS MainControl / " + self.mesh_obj.Label)
        self.title =  "#!/bin/bash\n"        

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
        configDict = pyDexcsSwakSubset.readConfigTreeFoam()
        env = configDict["bashrcFOAM"]
        configDict = pyDexcsSwakSubset.readConfigDexcs()
        envTreeFoam = configDict["TreeFoam"]
        env = env.replace('$TreeFoamUserPath',envTreeFoam)
        envSet = "source " + env + '\n'
        solverSet = "checkMesh " + "\n"
        cont = self.title + envSet + solverSet 
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
        configDict = pyDexcsSwakSubset.readConfigTreeFoam()
        paraFoamFix = configDict["paraFoam"]
        envSet = envSet0 + "source " + paraFoamFix + "\n"
        solverSet = "paraFoam " + "\n"
        #cont = title + envSet + solverSet 
        cont = self.title + envSet 
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
        envSet = ""
        solverSet = "gedit ./system/meshDict\n"
        libPath = ""
        sleep = ""
        cont = self.title + envSet + libPath + solverSet + sleep
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
        envSet = ". " + MainControl.BASHRC_PATH_4_OPENFOAM + ";\n"
        solverSet = "cartesianMesh | tee cfmesh.log\n"
        sleep = "sleep 2\n"
        cont = self.title + envSet + solverSet + sleep
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

    @abstractmethod
    def perform(self, CaseFilePath, TemplateCase):
        pass

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
