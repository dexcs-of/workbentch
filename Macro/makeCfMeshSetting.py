# -*- coding: utf-8 -*-
"""
Copyright (C) 2014 xxxx, xxxx all rights reserved.
2017/5/26 modified for cfMesh v-1.1.2
2018/9 modified for wx to QtGui
2019/4/21 some bug fix for import error
2019/4/30 some options , CellSize / RefLevel / ( MakeCartesianMesh )
"""
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


class FreeCadFileTable(QtGui.QTableWidget):
    """
    FreeCADファイルの情報を表示するTable
    """
    OBJECT_NAME_STR = "OjbectName"
    TYPE_STR        = "Type"
    REFINEMENT_STR  = "Refinement"
    CELL_SIZE_STR   = "CellSize"
    BOUNDARY_LAYER_STR = "Boundary\nLayer"
    N_LAYERS_STR     = "nLayers"
    RATIO_STR        = "Ratio"

    def __init__(self):
        """
        superクラスの__init__を呼ぶ
        """
        #print("FreeCadFileTable.__init__")
        QtGui.QTableWidget.__init__(self)
        
    def makeHeader(self):
        """
        このテーブルのヘッダーを作成する
        """
        #print("FreeCadFileTable.makeHeader")
        self.colLabels = [FreeCadFileTable.OBJECT_NAME_STR
                          , FreeCadFileTable.TYPE_STR
                          , FreeCadFileTable.CELL_SIZE_STR
                          , FreeCadFileTable.BOUNDARY_LAYER_STR
                          , FreeCadFileTable.N_LAYERS_STR
                          , FreeCadFileTable.RATIO_STR
                          ]
        """

        self.dataTypes = [grid.GRID_VALUE_STRING,
                          grid.GRID_VALUE_CHOICE + ':empty,patch,wall,symmetryPlane,region',
                          grid.GRID_VALUE_STRING,
                          grid.GRID_VALUE_BOOL,
                          grid.GRID_VALUE_NUMBER + ':0,99',
                          grid.GRID_VALUE_STRING        
                          ]

        """
    def GetColLabelValue(self, col):
        """
        明示的に呼ばれていなくても列のラベルを表示する時には呼ばれるので必要。
        @type col: number
        @param col: 列番号
        """
        return self.colLabels[col]

    def GetNumberRows(self):
        """
        Tableの行数を戻す。呼ばれていない。
        @rtype: number
        @return: Tableの行数
        """
        return len(self.data) + 1

    def GetNumberCols(self):
        """
        Tableの列数を戻す
        @rtype: number
        @return: Tableの列数
        """
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        """
        Tableのセルの値が空かどうかを戻す。呼ばれていない。
        @type row: number
        @param row:セルの行番号 
        @type col: number
        @param col: セルの列番号
        @rtype: boolean
        @return: Tableのセルの値が空ならTrue
        """
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    def GetValue(self, row, col):
        """
        テーブルの表のiRow行、jCol列のデータを戻す
        @type row:number
        @param row:テーブルの行番号
        @type col:number
        @param col:テーブルの列番号   
        @rtype: any data type
        @return: テーブルの表のrow行、col列のデータ
        """
        try:
        #    if col==1:
        #        comboBox=FreeCadFileGrid.tablewidget,cellWidget(row,col)
        #        index = comboBox.currentIndex()
        #        print index
        #        return FreeCadFileGrid.tablewidget.QComboBox.value()
        #    else:
                #print self.data[row][col]
                return self.data[row][col]
        except IndexError:
            return ''
        
    def SetValue(self, row, col, value):
        """
        テーブルの表のrow行、col列のセルにデータをセットする
        @type row:number
        @param row:テーブルの行番号
        @type col:number
        @param col:テーブルの列番号   
        @rtype: string
        @return: テーブルの表のrow行、col列のデータ
        """
        try:
            self.data[row][col] = value
        except IndexError:
            # add a new row
            self.data.append([''] * self.GetNumberCols())
            self.SetValue(row, col, value)
            # tell the grid we've added a row
            msg = grid.GridTableMessage(self,            # The table
                    grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                    1                                       # how many
                    )
            self.GetView().ProcessTableMessage(msg)
            
    def set_listData(self, listData):
        """
        FreeCADで読み込んだモデルのすべてのobjのLabel等のリストをセットする。
        @type listData: list
        @param listData: FreeCADで読み込んだモデルのすべてのobjのLabel等のリスト
        """
        #print("FreeCadFileTable.set_listData")
        self.data = listData

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]
    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False
    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)


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
    
    def get_sumOf3EdgesOfCadObjects(self):
        """
        CADファイルに含まれる全オブジェクトのバウンディングボックスの3辺の和を戻す
        FreeCAD上で表示されているすべてのobjのBoundBox情報から、領域全体のBoundBox情報(DX,DY,DZ)を算出して、
        概略セルサイズを決定する cellMax = ( DX + DY + DZ ) / 60
        ここでは60では割らない。
        @rtype: number
        @return: CADファイルに含まれる全オブジェクトのバウンディングボックスの3辺の和
        """
        assert(self.doc != None), "None self.doc in getBoundingBoxOfCadObjects"
        xmax = -float(Model.INF_STR)
        xmin = float(Model.INF_STR)
        ymax = -float(Model.INF_STR)
        ymin = float(Model.INF_STR)
        zmax = -float(Model.INF_STR)
        zmin = float(Model.INF_STR)
        # for obj in self.doc.Objects:
        #         print('obj = ',obj)
        for obj in self.doc.Objects:
            assert(obj != None), "None obj in getBoundingBoxOfCadObjects"
            #assert(obj.ViewObject != None), "None ViewObject in getBoundingBoxOfCadObjects"
            try:
                if obj.Shape:
                    if obj.Shape.BoundBox.XMax > xmax:
                        xmax = obj.Shape.BoundBox.XMax
                    if obj.Shape.BoundBox.XMin < xmin:
                        xmin = obj.Shape.BoundBox.XMin
                    if obj.Shape.BoundBox.YMax > ymax:
                        ymax = obj.Shape.BoundBox.YMax
                    if obj.Shape.BoundBox.YMin < ymin:
                        ymin = obj.Shape.BoundBox.YMin
                    if obj.Shape.BoundBox.ZMax > zmax:
                        zmax = obj.Shape.BoundBox.ZMax
                    if obj.Shape.BoundBox.ZMin < zmin:
                        zmin = obj.Shape.BoundBox.ZMin
            except AttributeError:
                pass
        boundingBox = BoundingBox(xmin,ymin,zmin,xmax,ymax,zmax)
        #print("boundingBox = %s" % boundingBox.toString())
        sumOf3Edges = (xmax-xmin+ymax-ymin+zmax-zmin)
        #print("Sum of 3 edges = %f" % sumOf3Edges)

        return sumOf3Edges

    def get_fcListData(self):
        """
        @rtype: list
        @return: FreeCADで読み込んだモデルのすべてのobjの[Label, "patch" "local" "" 0 2 1.2]を連結したリスト
        """
        #print("Model.get_fcListData")
        fcListData = []
        """
        # FreeCAD上で表示されているすべてのobjについて、とりあえずデフォルト値を設定        
        """
        for obj in self.doc.Objects:    
            if obj.ViewObject.Visibility:    
                if obj.isDerivedFrom("Part::FeaturePython") or obj.isDerivedFrom("App::DocumentObjectGroupPython"):
                    pass
                else:
            #if obj.Label:    # FreeCADで読み込んだモデルのすべてのobj
                    fcListData = fcListData + [[ obj.Label, Model.PATCH_STR, Model.EMPTY_STR, 0, 3, "1.2"]]
        #print(fcListData)
        return fcListData
 
class BoundingBox:
    """
    立体をぴったり囲む直方体
    """
    def __init__(self,xmin,ymin,zmin,xmax,ymax,zmax):
        """
        バウンディングボックスの値をセットする。
        @type xmin: number
        @param xmin: x最小値
        @type ymin: number
        @param ymin: y最小値
        @type zmin: number
        @param zmin: z最小値
        """
        self.xmin = xmin
        self.ymin = ymin
        self.zmin = zmin
        self.xmax = xmax
        self.ymax = ymax
        self.zmax = zmax
        
    def toString(self):
        """
        @rtype: string
        @return: このBoundingBoxの値を文字列で表現した者
        """
        return str("(" + str(self.xmin) + "," + str(self.ymin) + "," + str(self.zmin) + ")-(" + str(self.xmax) + "," + str(self.ymax) + "," + str(self.zmax) + ")")

class FreeCadFileGrid(QtGui.QDialog):
    """
    FreeCADファイルの情報を表示するGrid
    """
    def __init__(self, parent):
        """
        @type parent: Panel
        @param parent: このGridを格納するPanel
        """
        #print("FreeCadFileGrid.__init__")
        #grid.Grid.__init__(self, parent, -1)
        
    def makeGrid(self, fcListData):
        """
        @type fcListData: list
        @param fcListData: FreeCADで読み込んだモデルのすべてのobjのLabel等のリスト
        """
        #print("FreeCadFileGrid.makeHeader")
        self.table = FreeCadFileTable()
        self.table.makeHeader()
        self.table.set_listData(fcListData)
        """
        The second parameter means that the grid is to take ownership of the
        table and will destroy it when done.  Otherwise you would need to keep
        a reference to it and call its Destroy method later.
        self.SetTable(self.table, True)
        self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.AutoSizeColumns(False)
        grid.EVT_GRID_CELL_LEFT_DCLICK(self, self.actionOnLeftDoubleClickOnCell)


        """
        OBJECT_NAME_STR = "OjbectName"
        TYPE_STR        = "Type"
        REFINEMENT_STR  = "Refinement"
        CELL_SIZE_STR   = "CellSize"
        REF_LEVEL_STR   = "RefLevel"
        BOUNDARY_LAYER_STR = "Boundary\nLayer"
        N_LAYERS_STR     = "nLayers"
        RATIO_STR        = "Ratio"
        #refinementOption = 1 // global
        global colLabelsCell
        colLabelsCell = [OBJECT_NAME_STR, TYPE_STR, CELL_SIZE_STR, BOUNDARY_LAYER_STR, N_LAYERS_STR, RATIO_STR]
        global colLabelsRef
        colLabelsRef = [OBJECT_NAME_STR, TYPE_STR, REF_LEVEL_STR, BOUNDARY_LAYER_STR, N_LAYERS_STR, RATIO_STR]
        
        if refinementOption == 1:
            colLabels = colLabelsCell
        else:
            colLabels = colLabelsRef
        
        colcnt = len(fcListData[0])
        rowcnt = len(fcListData)

        self.tablewidget = QtGui.QTableWidget(rowcnt, colcnt)
        vheader = QtGui.QHeaderView(QtCore.Qt.Orientation.Vertical)
        vheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tablewidget.setVerticalHeader(vheader)
        hheader = QtGui.QHeaderView(QtCore.Qt.Orientation.Horizontal)
        hheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tablewidget.setHorizontalHeader(hheader)
        self.tablewidget.setHorizontalHeaderLabels(colLabels)

#        section groupBox for the four radioButton

        #QTableWidgetItem *item;
        for i in range(rowcnt):
            for j in range(colcnt):
                item = QtGui.QTableWidgetItem(str(fcListData[i][j]))
                if j != 1:
                    self.tablewidget.setItem(i, j, item)
                    #self.tablewidget.setCellWidget(i, j, item)
        for i in range(rowcnt):
            self.checkBox= QtGui.QCheckBox()
            self.tablewidget.setCellWidget(i,3,self.checkBox)
            self.checkBox.stateChanged.connect(partial(self.actionOnStateChangeOnCheckBox,i))
            self.typeComboBox = QtGui.QComboBox()
            self.typeComboBox.addItem("patch")
            self.typeComboBox.addItem("wall")
            self.typeComboBox.addItem("symmetryPlane")
            self.typeComboBox.addItem("region")
            self.typeComboBox.addItem("overset")
            self.typeComboBox.addItem("empty")
            self.tablewidget.setCellWidget(i,1,self.typeComboBox)
            self.typeComboBox.currentIndexChanged.connect(partial(self.actionOnIndexChangeOnComboBox,i))
        self.tablewidget.cellChanged.connect(self.actionOnLeftDoubleClickOnCell)
        ####grid.EVT_GRID_CELL_LEFT_DCLICK(self, self.actionOnLeftDoubleClickOnCell)
        ### 上記相当をコネクトしてあげないと、編集結果が反映されない
        ## QtGui.QAction.
    def actionOnIndexChangeOnComboBox(self, rowIndex,index):
        iRow=rowIndex
        iCol=1
        #print('Cell ({0},{1}) is selected'.format(iRow+1,iCol+1))
        data = self.typeComboBox.itemText(index)
        dataF = self.table.GetValue(iRow,iCol)
        #print('data is' ,dataF,'->',data)
        self.table.SetValue(iRow,iCol,data)

    def actionOnStateChangeOnCheckBox(self, rowIndex,index):
        iRow=rowIndex
        iCol=3
        #print('Cell ({0},{1}) is selected'.format(iRow+1,iCol+1))
        dataF = self.table.GetValue(iRow,iCol)
        #data = self.checkBox.checkState()
        #print('check is' ,dataF, '->', index)
        self.table.SetValue(iRow,iCol,index)
    def actionOnLeftDoubleClickOnCell(self, index):
        """
        Tableの各セルにマウスポインターを置いて、左ダブルクリックでそのセルの値の編集を可能にする
        デフォールトの設定は、ダブルクリックでの編集起動ではない。
        @type event:Event
        @param event:ダブルクリックイベント  
        """
        #print("FreeCadFileGrid#actionOnLeftDoubleClickOnCell()")

        iRow=self.tablewidget.currentRow()
        iCol=self.tablewidget.currentColumn()
        #print('Cell ({0},{1}) is selected'.format(iRow,iCol))
        data = self.tablewidget.currentItem().text()
        dataF = self.table.GetValue(iRow,iCol)
        #print('data is' ,dataF, '->', data)
        self.table.SetValue(iRow,iCol,data)

    def get_tableValue(self, iRow, jCol):
        """
        テーブルの表のiRow行、jCol列のデータを戻す
        @type iRow:number
        @param iRow:テーブルの行番号
        @type jCol:number
        @param jCol:テーブルの列番号   
        @rtype: string
        @return: テーブルの表のiRow行、jCol列のデータ
        """
        return self.table.GetValue(iRow, jCol)

    def GetValue(self, row, col):
        """
        テーブルの表のiRow行、jCol列のデータを戻す
        @type row:number
        @param row:テーブルの行番号
        @type col:number
        @param col:テーブルの列番号   
        @rtype: any data type
        @return: テーブルの表のrow行、col列のデータ
        """
        try:
            if col==1:
                comboBox=self.tablewidget,cellWidget(row,col)
                index = comboBox.currentIndex()
                #print (index)
                return FreeCadFileGrid.tablewidget.QComboBox.value()
            else:
                data=self.tablewidget.cellWidget(row,col)
                #print (data)
                return data
        except IndexError:
            return ''
            

class CfMeshFrame(QtGui.QDialog):
    """
    Frameを継承したクラス。読み込んだfreeCADファイルの情報を表形式で表示する。
    対話処理も可能。
    以下は、GUIコンポーネントの構成
    Frame > Panel > boxS_V 
    boxS_V > boxS_H1 > caseButton
                     > caseFileST
           > boxS_H2 > maxCellSizeST
                     > maxCellSizeCRL
                     > minCellSizeST
                     > minCellSizeCRL
                     > featureAngleST
                     > featureAngleCRL
           > grid
           > boxS_H3 > exportButton
                     > exitButton
    """
    CASE_STR         = "Case"
    EXPORT_STR       = "Export..."
    EXIT_STR         = "Exit"
    LOAD_STR         = "LoadDict"

    def __init__(self, parent=None):
        message = _(u'cfMesh parameter settings from FreeCAD Model(.fcstd)')        
        QtGui.QDialog.__init__(self)  

    def get_gridTableValue(self, iRow, jCol):
        """
        テーブルの表のiRow行、jCol列のデータを戻す
        @type iRow:number
        @param iRow:テーブルの行番号
        @type jCol:number
        @param jCol:テーブルの列番号   
        @rtype: string
        @return: テーブルの表のiRow行、jCol列のデータ
        """
        #print("get_gridTableValue")
        #print (iRow, jCol, self.grid.get_tableValue(iRow, jCol))
        return self.grid.get_tableValue(iRow, jCol)
    
    def get_minCellSizeValue(self):
        """
        最小のセルサイズを戻す
        @rtype: number
        @return: 最小のセルサイズ
        """
        return self.minCellSizeCRL.text()
    
    def get_maxCellSizeValue(self):
        """
        最大のセルサイズを戻す
        @rtype: number
        @return: 最大のセルサイズ
        """
        return self.maxCellSizeCRL.text()

    def set_maxCellSizeValue(self,value):
        """
        最大のセルサイズをセットする。
        @rtype: number
        @param: 最大のセルサイズ
        """
        self.maxCellSizeCRL.Value = value   
 
    def set_minCellSizeValue(self,value):
        """
        最小のセルサイズをセットする。
        @rtype: number
        @param: 最小のセルサイズ
        """
        self.minCellSizeCRL.Value = value   

    def get_featureAngleValue(self):
        """
        フィーチャーの角度を戻す
        @rtype: number
        @return: フィーチャーの角度        
        """
        return self.featureAngleCRL.text()
        
    def set_caseDirectory(self, caseDirectory):
        """
        ケースファイルのディレクトリをラベルにセットする。
        @type caseDirectory: string
        @param caseDirectory: ケースファイルのディレクトリ
        """
        #print("selected case directory=" + caseDirectory)
        self.caseFileST.Label = caseDirectory
        
    def get_caseDirectory(self):
        """
        ケースファイルのディレクトリを戻す
        @type caseDirectory: string
        @param caseDirectory: ケースファイルのディレクトリ
        """
        #print ( "get_caseDirectory: ", self.pathLabel.text())
        return self.pathLabel.text()

    def get_refinementOption(self):
        """
        チェックボタンの値を戻す
        """
        return self.radioButton_c.isChecked()

    def get_keepCellsIntersectingBoundaryCHKOption(self):
        """
        チェックボタンの値を戻す
        """
        return self.keepCellsIntersectingBoundaryCHK.isChecked()

    def get_untangleLayerCHKOption(self):
        """
        チェックボタンの値を戻す
        """
        return self.untangleLayerCHK.isChecked()

    def get_optimiseLayerCHKOption(self):
        """
        チェックボタンの値を戻す
        """
        return self.optimiseLayerCHK.isChecked()

    def get_stopAfterEdgeExtractionCHKOption(self):
        """
        チェックボタンの値を戻す
        """
        return self.stopAfterEdgeExtractionCHK.isChecked()

    def setLayout1(self, fcListData, caseDirectory, maxCellSize):
        """
        このFrameのレイアウトをセットする。
        @type fcListData:list
        @param fcListData:FreeCADで読み込んだモデルのすべてのobjのLabel等のリスト
        @type caseDirectory:string
        @param caseDirectory: ケースファイルのディレクトリ
        @type maxCellSize: number
        @param maxCellSize: 最大のセルサイズ
        """

        self.fcListData = fcListData
        panel = QtGui.QVBoxLayout()
       
        self.dirName = caseDirectory
        self.maxCellSize = '{0:8.3}'.format(maxCellSize)
        
        self.grid = FreeCadFileGrid(panel)
        self.grid.makeGrid(fcListData)

        self.widget = QtGui.QWidget()
        self.widget.setGeometry(QtCore.QRect(11, 11, 571, 471))
        self.widget.setObjectName("widget")	


        self.horizontalGroupBox1 = QtGui.QGroupBox(_('location of CaseFile'))

        self.horizontalLayout_1 = QtGui.QHBoxLayout()
        self.horizontalLayout_1.setObjectName("horizontalLayout_1")
        self.caseButton = QtGui.QPushButton(self.widget)
        self.caseButton.setObjectName("caseButton")
        self.horizontalLayout_1.addWidget(self.caseButton)
        self.pathLabel = QtGui.QLabel(self.widget)
        self.pathLabel.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pathLabel.sizePolicy().hasHeightForWidth())
        self.pathLabel.setSizePolicy(sizePolicy)

        self.pathLabel.setText(self.dirName)

        self.pathLabel.setObjectName("pathLabel")
        self.horizontalLayout_1.addWidget(self.pathLabel)
        self.horizontalGroupBox1.setLayout(self.horizontalLayout_1)
        #self.caseButton.setText(QtGui.QApplication.translate("cfMeshSetting", "Case", None, QtGui.QApplication.UnicodeUTF8))
        self.caseButton.setText(QtGui.QApplication.translate("cfMeshSetting", "Case", None))

        panel.addWidget(self.horizontalGroupBox1)
        #panel.addWidget(self.horizontalLayout_1)
        #print("set_gridTableValue1")

        self.horizontalGroupBox2 = QtGui.QGroupBox(_('primary parameters'))

        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.maxCellSizeST = QtGui.QLabel(self.widget)
        self.maxCellSizeST.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.maxCellSizeST)
        self.maxCellSizeCRL = QtGui.QLineEdit(self.widget)
        self.maxCellSizeCRL.setObjectName("maxCellSizeCRL")

        self.maxCellSizeCRL.setText(self.maxCellSize)
        self.maxCellSizeCRL.update()

        self.horizontalLayout_2.addWidget(self.maxCellSizeCRL)
        self.minCellSizeST = QtGui.QLabel(self.widget)
        self.minCellSizeST.setObjectName("minCellSizeST")
        #self.horizontalLayout_2.addWidget(self.minCellSizeST)
        self.minCellSizeCRL = QtGui.QLineEdit(self.widget)
        self.minCellSizeCRL.setObjectName("minCellSizeCRL")
        #self.horizontalLayout_2.addWidget(self.minCellSizeCRL)
        self.featureAngleST = QtGui.QLabel(self.widget)
        self.featureAngleST.setObjectName("featureAngleST")
        self.horizontalLayout_2.addWidget(self.featureAngleST)
        self.featureAngleCRL = QtGui.QLineEdit(self.widget)
        self.featureAngleCRL.setObjectName("featureAngleCRL")
        self.horizontalLayout_2.addWidget(self.featureAngleCRL)
        self.horizontalLayout_2.update()

        #self.maxCellSizeST.setText(QtGui.QApplication.translate("cfMeshSetting", MainControl.MAX_CELL_SIZE_STR, None, QtGui.QApplication.UnicodeUTF8))
        #self.minCellSizeST.setText(QtGui.QApplication.translate("cfMeshSetting", MainControl.MIN_CELL_SIZE_STR, None, QtGui.QApplication.UnicodeUTF8))
        #self.featureAngleST.setText(QtGui.QApplication.translate("cfMeshSetting", MainControl.FEATURE_ANGLE_STR, None, QtGui.QApplication.UnicodeUTF8))
        self.maxCellSizeST.setText(QtGui.QApplication.translate("cfMeshSetting", MainControl.MAX_CELL_SIZE_STR, None))
        self.minCellSizeST.setText(QtGui.QApplication.translate("cfMeshSetting", MainControl.MIN_CELL_SIZE_STR, None))
        self.featureAngleST.setText(QtGui.QApplication.translate("cfMeshSetting", MainControl.FEATURE_ANGLE_STR, None))

        self.featureAngleCRL.setText(str(MainControl.FEATURE_ANGLE))



        self.horizontalGroupBox2.setLayout(self.horizontalLayout_2)
        self.horizontalGroupBox2.update()
        #self.caseButton.setText(QtGui.QApplication.translate("cfMeshSetting", "Case", None, QtGui.QApplication.UnicodeUTF8))
        self.caseButton.setText(QtGui.QApplication.translate("cfMeshSetting", "Case", None))

        panel.addWidget(self.horizontalGroupBox2)
        #panel.addWidget(self.horizontalLayout_2)

        self.horizontalGroupBox3 = QtGui.QGroupBox(_('options'))

        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.untangleLayerST = QtGui.QLabel(self.widget)
        self.untangleLayerST.setObjectName("untangleLayerST")
        #self.horizontalLayout_3.addWidget(self.untangleLayerST)
        self.untangleLayerCHK = QtGui.QCheckBox(self.widget)
        self.untangleLayerCHK.setObjectName("untangleLayer")
        #self.horizontalLayout_3.addWidget(self.untangleLayerCHK)

        self.optimiseLayerST = QtGui.QLabel(self.widget)
        self.optimiseLayerST.setObjectName("optimiseLayerST")
        self.horizontalLayout_3.addWidget(self.optimiseLayerST)
        self.optimiseLayerCHK = QtGui.QCheckBox(self.widget)
        self.optimiseLayerCHK.setObjectName("optimiseLayer")
        self.horizontalLayout_3.addWidget(self.optimiseLayerCHK)

        self.optionsButton = QtGui.QPushButton(self.widget)
        self.optionsButton.setObjectName("options")
        #self.horizontalLayout_3.addWidget(self.optionsButton)

        self.keepCellsIntersectingBoundaryST = QtGui.QLabel(self.widget)
        self.keepCellsIntersectingBoundaryST.setObjectName("keepCellsIntersectingBoundaryST")
        self.horizontalLayout_3.addWidget(self.keepCellsIntersectingBoundaryST)
        self.keepCellsIntersectingBoundaryCHK = QtGui.QCheckBox(self.widget)
        self.keepCellsIntersectingBoundaryCHK.setObjectName("keepCellsIntersectingBoundary")
        self.horizontalLayout_3.addWidget(self.keepCellsIntersectingBoundaryCHK)

        self.stopAfterEdgeExtractionST = QtGui.QLabel(self.widget)
        self.stopAfterEdgeExtractionST.setObjectName("stopAfterEdgeExtractionST")
        self.horizontalLayout_3.addWidget(self.stopAfterEdgeExtractionST)
        self.stopAfterEdgeExtractionCHK = QtGui.QCheckBox(self.widget)
        self.stopAfterEdgeExtractionCHK.setObjectName("stopAfterEdgeExtraction")
        self.horizontalLayout_3.addWidget(self.stopAfterEdgeExtractionCHK)

        self.untangleLayerST.setText("untangle<BR>_Layer")        
        self.optimiseLayerST.setText("optimise<BR>_Layer")        
        #self.optionsButton.setText(QtGui.QApplication.translate("cfMeshSetting", "options", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsButton.setText(QtGui.QApplication.translate("cfMeshSetting", "options", None))
        self.stopAfterEdgeExtractionST.setText("stopAfter<BR>EdgeExtraction")        
        self.keepCellsIntersectingBoundaryST.setText("keepCells<BR>Intersecting<BR>_Boundary")        


        self.horizontalLayout_3.update()

        self.horizontalGroupBox3.setLayout(self.horizontalLayout_3)
        self.horizontalGroupBox3.update()
        panel.addWidget(self.horizontalGroupBox3)

        #print("set_gridTableValue1")



        self.horizontalGroupBox4 = QtGui.QGroupBox(_('individual parameters'))
       # panel.addWidget(self.horizontalGroupBox4)

        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.radioButton_c = QtGui.QRadioButton(self.widget)
        self.radioButton_c.setObjectName("radioButton_c")
        self.radioButton_c.setText("CellSize")
        self.radioButton_c.setChecked(1)
        self.radioButton_r = QtGui.QRadioButton(self.widget)
        self.radioButton_r.setObjectName("radioButton_r")
        self.radioButton_r.setText("RefLevel")
        self.radioButton = QtGui.QButtonGroup(self.widget)
        self.radioButton.addButton(self.radioButton_c,1)
        self.radioButton.addButton(self.radioButton_r,2)
        self.horizontalLayout_4.addWidget(self.radioButton_c)
        self.horizontalLayout_4.addWidget(self.radioButton_r)

        self.horizontalGroupBox4.setLayout(self.horizontalLayout_4)
        self.horizontalGroupBox4.update()
        panel.addWidget(self.horizontalGroupBox4)


        panel.addWidget(self.grid.tablewidget)
        #print("set_gridTableValue2")

        self.horizontalGroupBox5 = QtGui.QGroupBox(_('action'))

        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.exportButton = QtGui.QPushButton(self.widget)
        self.exportButton.setObjectName("exportButton")
        self.horizontalLayout_5.addWidget(self.exportButton)
        self.loadButton = QtGui.QPushButton(self.widget)
        self.loadButton.setObjectName("loadButton")
        self.horizontalLayout_5.addWidget(self.loadButton)
        self.editMeshDictButton = QtGui.QPushButton(self.widget)
        self.editMeshDictButton.setObjectName("editMeshButton")
        self.horizontalLayout_5.addWidget(self.editMeshDictButton)
        self.makeCartesianMeshButton = QtGui.QPushButton(self.widget)
        self.makeCartesianMeshButton.setObjectName("makeCartesianMeshButton")
        self.horizontalLayout_5.addWidget(self.makeCartesianMeshButton)
        self.checkMeshButton = QtGui.QPushButton(self.widget)
        self.checkMeshButton.setObjectName("checkMeshButton")
        self.horizontalLayout_5.addWidget(self.checkMeshButton)
        self.viewMeshButton = QtGui.QPushButton(self.widget)
        self.viewMeshButton.setObjectName("viewMeshButton")
        self.horizontalLayout_5.addWidget(self.viewMeshButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.exitButton = QtGui.QPushButton(self.widget)
        self.exitButton.setObjectName("exitButton")
        self.horizontalLayout_5.addWidget(self.exitButton)

        #self.exportButton.setText(QtGui.QApplication.translate("cfMeshSetting", "ExportDict", None, QtGui.QApplication.UnicodeUTF8))
        #self.loadButton.setText(QtGui.QApplication.translate("cfMeshSetting", "LoadDict", None, QtGui.QApplication.UnicodeUTF8))
        #self.makeCartesianMesh.setText(QtGui.QApplication.translate("cfMeshSetting", "makeCartesianMesh", None, QtGui.QApplication.UnicodeUTF8))
        #self.exitButton.setText(QtGui.QApplication.translate("cfMeshSetting", "exit", None, QtGui.QApplication.UnicodeUTF8))
        self.exportButton.setText(QtGui.QApplication.translate("cfMeshSetting", "ExportDict", None))
        self.loadButton.setText(QtGui.QApplication.translate("cfMeshSetting", "LoadDict", None))
        self.editMeshDictButton.setText(QtGui.QApplication.translate("cfMeshSetting", "EditDict", None))
        self.makeCartesianMeshButton.setText(QtGui.QApplication.translate("cfMeshSetting", "MakeMesh", None))
        self.checkMeshButton.setText(QtGui.QApplication.translate("cfMeshSetting", "CheckMesh", None))
        self.viewMeshButton.setText(QtGui.QApplication.translate("cfMeshSetting", "ViewMesh", None))
        self.exitButton.setText(QtGui.QApplication.translate("cfMeshSetting", "Exit", None))

        self.horizontalGroupBox5.setLayout(self.horizontalLayout_5) 
        self.horizontalGroupBox5.update()

        panel.addWidget(self.horizontalGroupBox5)
        panel.update()
        self.setLayout(panel)

        self.setWindowTitle(_('cfMesh parameter settings from FreeCAD Model(.fcstd)'))
        self.setGeometry(QtCore.QRect(220, 100, 500, 500))
        #print("set_gridTableValue3")
        self.update()

    def get_loadButton(self):
        """
        Loadボタンを戻す
        @rtype: Button
        @return: Loadボタン
        """
        return self.loadButton
    
    def get_exportButton(self):
        """
        Exportボタンを戻す
        @rtype: Button
        @return: Exportボタン
        """
        #print("get_exportButton")
        return self.exportButton

    def get_exitButton(self):
        """
        Exitボタンを戻す
        @rtype: Button
        @return: Exitボタン
        """
        return self.exitButton
    
    def get_caseButton(self):
        """
        Caseボタンを戻す
        @rtype: Button
        @return: Caseボタン
        """
        return self.caseButton

                
class ViewControl():
###class ViewControl(QtGui.QMainWindow):
    """
    表示全般を管理するクラス
    """
    MESSAGE_STR = "message"
    
    def __init__(self, mainControl):
        """
        初期設定
        @type mainControl: MainControl
        @param mainControl: 全般管理クラス
        """
        self.mainControl = mainControl
        
    def showMessageDialog(self, message):
        """
        メッセージを表示し、OKをクリックしてもらうダイアログを表示する
        @type message: string 
        @param message: 表示するメッセージ
        """
        QMessageBox.information(self.cfMeshFrame, "Message", message)
        
    def get_minCellSizeValue(self):
        """
        最小Cell寸法を戻す
        @rtype: number 
        @return: 最小Cell寸法 
        """
        return self.cfMeshFrame.get_minCellSizeValue()
        
    def get_maxCellSizeValue(self):
        """
        最大Cell寸法を戻す
        @rtype: number
        @return: 最大Cell寸法
        """
        return self.cfMeshFrame.get_maxCellSizeValue()
    
    def get_featureAngleValue(self):
        """
        フィーチャーの角度を戻す
        @rtype: number
        @return: フィーチャーの角度
        """
        return self.cfMeshFrame.get_featureAngleValue()
    
    def get_caseDirectory(self):
        """
        ケースファイルのディレクトリを戻す
        @type caseDirectory: string
        @param caseDirectory: ケースファイルのディレクトリ
        """
        return self.cfMeshFrame.get_caseDirectory()

    def get_refinementOption(self):
        """
        細分化指定方法
        @type caseDirectory: string
        @param caseDirectory: ケースファイルのディレクトリ
        """
        return self.cfMeshFrame.get_refinementOption()

    def get_keepCellsIntersectingBoundaryCHKOption(self):
        """
        keepCellsIntersectingBoundary Option
        """
        return self.cfMeshFrame.get_keepCellsIntersectingBoundaryCHKOption()

    def get_untangleLayerCHKOption(self):
        """
        keepCellsIntersectingBoundary Option
        """
        return self.cfMeshFrame.get_untangleLayerCHKOption()

    def get_optimiseLayerCHKOption(self):
        """
        keepCellsIntersectingBoundary Option
        """
        return self.cfMeshFrame.get_optimiseLayerCHKOption()

    def get_stopAfterEdgeExtractionCHKOption(self):
        """
        keepCellsIntersectingBoundary Option
        """
        return self.cfMeshFrame.get_stopAfterEdgeExtractionCHKOption()

    def setLayout(self, fcListData, dirName, cellMax):
        """
        Frameを表示して、読み込んだfreeCADファイルの情報をテーブルで表示する
        @type fcListData: list
        @param fcListData: 読み込んだfreeCADファイルの情報
        @type dirName: string
        @param dirName: 読み込んだfreeCADファイルのディレクトリ名
        @type cellMax:number
        @param cellMax:最大Cell寸法
        """

        self.dirName = dirName
        self.cfMeshFrame = CfMeshFrame()
        self.cfMeshFrame.setLayout1(fcListData, dirName, cellMax)
        QtCore.QObject.connect(self.cfMeshFrame.caseButton, QtCore.SIGNAL("clicked()"), self.actionOnCaseButton)
        QtCore.QObject.connect(self.cfMeshFrame.exitButton, QtCore.SIGNAL("clicked()"), self.actionOnExitButton)
        QtCore.QObject.connect(self.cfMeshFrame.exportButton, QtCore.SIGNAL("clicked()"), self.actionOnExportButton)
        QtCore.QObject.connect(self.cfMeshFrame.editMeshDictButton, QtCore.SIGNAL("clicked()"), self.actionOnEditMeshDictButton)
        QtCore.QObject.connect(self.cfMeshFrame.makeCartesianMeshButton, QtCore.SIGNAL("clicked()"), self.actionOnMakeCartesianMeshButton)
        QtCore.QObject.connect(self.cfMeshFrame.checkMeshButton, QtCore.SIGNAL("clicked()"), self.actionOnCheckMeshButton)
        QtCore.QObject.connect(self.cfMeshFrame.viewMeshButton, QtCore.SIGNAL("clicked()"), self.actionOnViewMeshButton)
        QtCore.QObject.connect(self.cfMeshFrame.loadButton, QtCore.SIGNAL("clicked()"), self.actionOnLoadButton)
        QtCore.QObject.connect(self.cfMeshFrame.radioButton_c, QtCore.SIGNAL("clicked()"), self.actionOnRadioButton)
        QtCore.QObject.connect(self.cfMeshFrame.radioButton_r, QtCore.SIGNAL("clicked()"), self.actionOnRadioButton)
        self.cfMeshFrame.exec_()
        #print ("cfMeshFrame.setLayout1")      

    def get_gridTableValue(self, iRow, jCol):
        """
        テーブルの表のiRow行、jCol列のデータを戻す
        @type iRow:number
        @param iRow:テーブルの行番号
        @type jCol:number
        @param jCol:テーブルの列番号   
        @rtype: number?
        @return: テーブルの表のiRow行、jCol列のデータ
        """
        #print("ViewControl#get_gridTableValue:i,j=%d,%d" % (i, j))
        return self.cfMeshFrame.get_gridTableValue(iRow, jCol)
        
    def actionOnExitButton(self):
        """
        Exitボタンが押された場合の処理。
        @type event:Event 
        @param event: マウスクリックイベント 
        """
        #print("actionOnExitButton()")
        message = _('Will you exit?')
        ret = QMessageBox.question(None, "My message", message, QMessageBox.Yes, QMessageBox.No)      
        if ret == QMessageBox.Yes:
                self.cfMeshFrame.close()
        elif ret == QMessageBox.No:
                return
        
    def actionOnCaseButton(self):
        """    
        Case ボタンが押された場合の処理
        @type event:Event 
        @param event: マウスクリックイベント         
        """
        #print("actionOnCaseButton()")

        dirName = QFileDialog.getExistingDirectory(self.cfMeshFrame, 'Select Directory', os.path.expanduser('~') + '/Desktop')

        if dirName != "":
                QMessageBox.information(self.cfMeshFrame, "Directory", dirName)
        text = dirName
        self.cfMeshFrame.pathLabel.setText(text)
        
        from dexcsCfdAnalysis import _CfdAnalysis
        for obj in FreeCAD.ActiveDocument.Objects:
            #print(obj)
            if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, _CfdAnalysis):
                if obj.IsActiveAnalysis:
                    #print("deb:"+dirName)
                    obj.OutputPath = dirName

        dictName = os.path.dirname(App.ActiveDocument.FileName) + MainControl.SLASH_STR + ".CaseFileDict"
        #print(dictName)
        writeDict = open(dictName , 'w')
        writeDict.writelines(text)
        writeDict.close()



    def actionOnButtonFocused(self):
        """
        特に何もしない。
        """
        pass

    def actionOnRadioButton(self):
        """
        radioButton
        """
        #print("actionOnRadioButton()")
        if self.cfMeshFrame.radioButton_c.isChecked() == True :
            #print ('CellSize')
            colLabels = colLabelsCell
        else :
            #print ('RefLevel')
            colLabels = colLabelsRef
        self.cfMeshFrame.grid.tablewidget.setHorizontalHeaderLabels(colLabels)
        NR = self.cfMeshFrame.grid.table.GetNumberRows()
        maxCellSize = float(self.cfMeshFrame.get_maxCellSizeValue())
        for j in range(NR):
            if self.cfMeshFrame.grid.table.GetValue(j,2) :
                if self.cfMeshFrame.radioButton_c.isChecked() == True :
                    refLevel = float(self.cfMeshFrame.grid.table.GetValue(j,2))
                    cellSize = maxCellSize
                    while refLevel>0:
                        refLevel = refLevel - 1
                        cellSize = cellSize / 2
                    self.cfMeshFrame.grid.table.SetValue(j, 2, str(cellSize))
                    self.item = QtGui.QTableWidgetItem(str(cellSize))
                    self.cfMeshFrame.grid.tablewidget.setCurrentCell( j, 2)
                    self.cfMeshFrame.grid.tablewidget.setItem( j, 2, self.item)
                    #print ('CellSize='+str(cellSize))
                else:
                    cellSize = float(self.cfMeshFrame.grid.table.GetValue(j,2))
                    refLevel = 0
                    while cellSize < maxCellSize:
                        refLevel = refLevel + 1
                        cellSize = cellSize * 2
                    self.cfMeshFrame.grid.table.SetValue(j, 2, str(refLevel))
                    self.item = QtGui.QTableWidgetItem(str(refLevel))
                    self.cfMeshFrame.grid.tablewidget.setCurrentCell( j, 2)
                    self.cfMeshFrame.grid.tablewidget.setItem( j, 2, self.item)
                    #print ('RefLevel='+str(refLevel))
                    



    def actionOnLoadButtonEx(self):
        """    
        Case ボタンが押された場合の処理(example)
        """    
        MaxCellSize = "0.5"
        self.cfMeshFrame.maxCellSizeCRL.setText(MaxCellSize)

        i=0
        j=3
        self.checkBox=QtGui.QCheckBox()
        self.checkBox.setChecked(1)
        self.cfMeshFrame.grid.tablewidget.setCellWidget( i, j, self.checkBox)
        j=1
        self.typeComboBox = QtGui.QComboBox()
        self.typeComboBox.addItem("patch")
        self.typeComboBox.addItem("wall")
        self.typeComboBox.addItem("symmetryPlane")
        self.typeComboBox.addItem("region")
        self.typeComboBox.addItem("overset")
        self.typeComboBox.addItem("empty")
        index=2
        self.typeComboBox.setCurrentIndex(index)
        self.cfMeshFrame.grid.tablewidget.setCellWidget( i, j, self.typeComboBox)

        j=2
        CellSize= "0.05"
        self.item = QtGui.QTableWidgetItem(CellSize)
        self.cfMeshFrame.grid.tablewidget.setCurrentCell( i, j)
        self.cfMeshFrame.grid.tablewidget.setItem( i, j, self.item)

        j=4
        i=1
        nLayer = "5"
        self.item = QtGui.QTableWidgetItem(nLayer)
        self.cfMeshFrame.grid.tablewidget.setCurrentCell( i, j)
        self.cfMeshFrame.grid.tablewidget.setItem( i, j, self.item)

        return
        
    def actionOnLoadButton(self):
        """
        Load ボタンが押された場合の処理
        """
        #print("onLoad1")
        #print(self.dirName)
 
        if(os.path.exists(self.dirName)):
            caseFolder = self.dirName + "/system"
            (meshDict, dialog) = QFileDialog.getOpenFileName(self.cfMeshFrame, 'Choose the meshDict file', caseFolder)
            #print (dialog)
            #print (meshDict)
            if meshDict == "":
                answer = self.showMessageDialog(_("You Canceled."))
                return     # the user changed idea...

            if str(meshDict)[-8:] == "meshDict":
                message = str(meshDict) + _(' has been found, do you choose it? ')
                dialog = QMessageBox.question(None,"Question",message, QMessageBox.No, QMessageBox.Yes)
                if dialog == QMessageBox.Yes:
                    #print ("ID_YES")
                    self.loadMeshDict(meshDict)
            else:
                message = str(meshDict) + _(' is not a meshDict file.')
                answer = self.showMessageDialog(message)

            return

    def loadMeshDict(self,meshDict):
        """
        Loadボタン押下後の処理を全て行う。
        """
        f = open(meshDict)
        x = f.read()
        f.close()
        y = x.split('\n')

        message = str(meshDict) + _(" has been read.")
        #print (message)

        """
        CellSize or RefLevel
        """
        if y[0] == "//RefLevel" :
            refinementOption = 0
            colLabels = colLabelsRef
            self.cfMeshFrame.radioButton_r.setChecked(1)
            searchText = "additionalRefinementLevels"
        else :
            colLabels = colLabelsCell
            refinementOption = 1
            self.cfMeshFrame.radioButton_c.setChecked(1)
            searchText = "cellSize"

        #print (refinementOption)    
        #print (colLabels)    
        self.cfMeshFrame.grid.tablewidget.setHorizontalHeaderLabels(colLabels)

        MaxCellSize = ""
        MaxCellSize = self.mainControl.searchVal( y, "maxCellSize")
        answerMsg = 'maxCellSize ='+ str(MaxCellSize)
        #print (answerMsg)
        self.cfMeshFrame.set_maxCellSizeValue(str(MaxCellSize))
        self.cfMeshFrame.maxCellSizeCRL.setText(MaxCellSize)

        MinCellSize = ""
        MinCellSize = self.mainControl.searchVal( y, "minCellSize")
        answerMsg = 'minCellSize ='+ str(MinCellSize)
        #print (answerMsg)
        if MinCellSize:
            self.cfMeshFrame.set_minCellSizeValue(str(MinCellSize))
            self.cfMeshFrame.minCellSizeCRL.setText(MinCellSize)

        keepCellsIntersectingBoundary = ""
        keepCellsIntersectingBoundary = self.mainControl.searchVal( y, "keepCellsIntersectingBoundary")
        answerMsg = 'keepCellsIntersectingBoundary ='+ str(keepCellsIntersectingBoundary)
        #print (answerMsg)
        self.cfMeshFrame.keepCellsIntersectingBoundaryCHK.setChecked(bool(keepCellsIntersectingBoundary))

        checkForGluedMesh = ""
        checkForGluedMesh = self.mainControl.searchVal( y, "checkForGluedMesh")
        answerMsg = 'checkForGluedMesh ='+ str(checkForGluedMesh)
        #print (answerMsg)

        untangleLayer = ""
        untangleLayer = self.mainControl.searchVal( y, "untangleLayer")
        answerMsg = 'untangleLayer ='+ str(untangleLayer)
        #print (answerMsg)
        self.cfMeshFrame.untangleLayerCHK.setChecked(bool(untangleLayer))

        optimiseLayer = ""
        optimiseLayer = self.mainControl.searchVal( y, "optimiseLayer")
        answerMsg = 'optimiseLayer ='+ str(optimiseLayer)
        #print (answerMsg)
        self.cfMeshFrame.optimiseLayerCHK.setChecked(bool(optimiseLayer))

        stopAfter = ""
        stopAfter = self.mainControl.searchVal( y, "stopAfter")
        answerMsg = 'stopAfter ='+ str(stopAfter)
        #print (answerMsg)
        self.cfMeshFrame.stopAfterEdgeExtractionCHK.setChecked(bool(stopAfter))

        NR=self.cfMeshFrame.grid.table.GetNumberRows()
        #print ("NR = ", NR)

        search_str = "newPatchNames"
        is1, is2 = self.mainControl.searchLocationKakko(y,search_str)
        #print (search_str, " between ", is1, " - ", is2)
        typeDefLabelList=[]
        typeBoundaryList=[]
        counter = is1
        while counter<is2-1:
                counter += 1
                myList = y[counter].strip()
                if myList and ( not y[counter].strip().startswith("/")):
                    if myList[0:7] == "newName":
                        #print ("    found", y[counter])
                        typeDefLabel = self.mainControl.searchVal1( y, counter-2, "newName") 
                        #print ("    ---label ", typeDefLabel)
                        typeDefLabelList.append( typeDefLabel )
                    if myList[0:4] == "type":
                        typeBoundaryList.append( self.mainControl.searchVal1( y, counter-2, "type") )
                        #print ("    ---apend BoundaryList ")
        #print (search_str, "=", typeDefLabelList)
        #print ("type = ", typeBoundaryList)

        
        for i in range(len(typeDefLabelList)):
            	for j in range(NR):
                    #print (i, j, str(typeDefLabelList[i]), str(self.cfMeshFrame.grid.table.GetValue(j,0)))
                    if str(typeDefLabelList[i]) ==  str(self.cfMeshFrame.grid.table.GetValue(j,0)):
                        self.cfMeshFrame.grid.table.SetValue(j, 1, typeBoundaryList[i])        
                        text=typeBoundaryList[i]
                        if text == "wall" : 
                            index = 1
                        elif text == "symmetryPlane" : 
                            index = 2
                        elif text == "region" : 
                            index = 3
                        elif text == "overset" : 
                            index = 4
                        elif text == "empty" : 
                            index = 5
                        else:
                            index = 0
                        self.comboBox = self.cfMeshFrame.grid.tablewidget.cellWidget(j,1)
                        self.comboBox.setCurrentIndex(index)
         
        search_str = "localRefinement"
        is1, is2 = self.mainControl.searchLocationKakko(y,search_str)
        localRefLabelList=[]
        cellSize=[]
        counter = is1
        while counter<is2-1:
                counter += 1
                myList = y[counter].strip()
                if myList and ( not x[counter].strip().startswith("/")):
                    localRefLabelList.append(myList)
                    cellSize.append( self.mainControl.searchVal1( y, counter, searchText) )
                    iss1, iss2 = self.mainControl.searchLocationKakko1(y,counter)
                    counter = iss2
        #print (search_str, "=", localRefLabelList)
        #print ("cellSize = ", cellSize)


        for i in range(len(localRefLabelList)):
            	for j in range(NR):
                    #print (str(localRefLabelList[i]), str(self.cfMeshFrame.grid.table.GetValue(j,0)))
                    if str(localRefLabelList[i]) ==  str(self.cfMeshFrame.grid.table.GetValue(j,0)):
                        self.cfMeshFrame.grid.table.SetValue(j, 2, cellSize[i])
                        self.item = QtGui.QTableWidgetItem(cellSize[i])
                        self.cfMeshFrame.grid.tablewidget.setCurrentCell( j, 2)
                        self.cfMeshFrame.grid.tablewidget.setItem( j, 2, self.item)

        search_str = "patchBoundaryLayers"
        is1, is2 = self.mainControl.searchLocationKakko(y,search_str)
        boundaryLayerList=[]
        nLayerList=[]
        RatioList=[]
        counter = is1
        while counter<is2-1:
            counter += 1
            myList = y[counter].strip()
            if myList and ( not x[counter].strip().startswith("/")):
                boundaryLayerList.append(myList)
                nLayerList.append( self.mainControl.searchVal1( y, counter, "nLayers") )
                RatioList.append( self.mainControl.searchVal1( y, counter, "thicknessRatio") )
                iss1, iss2 = self.mainControl.searchLocationKakko1(y,counter)
                counter = iss2
        #print (search_str, "=", boundaryLayerList)
        #print ("nLayer = ", nLayerList)
        #print ("Ratio = ", RatioList)

        for i in range(len(boundaryLayerList)):
                for j in range(NR):
                    if str(boundaryLayerList[i]) ==  str(self.cfMeshFrame.grid.table.GetValue(j,0)):
                        self.checkBox=QtGui.QCheckBox()
                        self.checkBox.stateChanged.connect(partial(self.cfMeshFrame.grid.actionOnStateChangeOnCheckBox,j))
                        self.checkBox.setCheckState(QtCore.Qt.Checked)
                        self.cfMeshFrame.grid.tablewidget.setCellWidget( j, 3, self.checkBox)
                        self.cfMeshFrame.grid.table.SetValue(j,4,int(nLayerList[i]))
                        self.item = QtGui.QTableWidgetItem(nLayerList[i])
                        self.cfMeshFrame.grid.tablewidget.setCurrentCell( j, 4)
                        self.cfMeshFrame.grid.tablewidget.setItem( j, 4, self.item)
                        self.cfMeshFrame.grid.table.SetValue(j, 5, RatioList[i])
                        self.item = QtGui.QTableWidgetItem(RatioList[i])
                        self.cfMeshFrame.grid.tablewidget.setCurrentCell( j, 5)
                        self.cfMeshFrame.grid.tablewidget.setItem( j, 5, self.item)

        search_str = "objectRefinements"
        is1, is2 = self.mainControl.searchLocationKakko(y,search_str)
        objectRefList=[]
        cellSizeList=[]
        counter = is1
        while counter<is2-1:
                counter += 1
                myList = y[counter].strip()
                if myList and ( not x[counter].strip().startswith("/")):
                    objectRefList.append(myList)
                    #cellSizeList.append( self.mainControl.searchVal1( y, counter, "cellSize") )
                    ## 2019/7/15 分割レベルとセルサイズの不整合を調整するパラメタ（objRefPar）を導入
                    objRefPar = 1.1
                    if searchText == 'cellSize' and self.mainControl.searchVal1( y, counter, searchText) != None:
                   	    #print ( self.mainControl.searchVal1( y, counter, searchText))
                        cellSizeList.append( str(float(self.mainControl.searchVal1( y, counter, searchText)) / objRefPar ) )
                    else :
                        cellSizeList.append( self.mainControl.searchVal1( y, counter, searchText) )
                    iss1, iss2 = self.mainControl.searchLocationKakko1(y,counter)
                    counter = iss2

        for i in range(len(objectRefList)):
            	for j in range(NR):
                    if str(objectRefList[i]) ==  str(self.cfMeshFrame.grid.table.GetValue(j,0)):
                        self.cfMeshFrame.grid.table.SetValue(j, 1, 'region')
                        self.cfMeshFrame.grid.table.SetValue(j, 2, cellSizeList[i])
                        self.item = QtGui.QTableWidgetItem(cellSizeList[i])
                        self.cfMeshFrame.grid.tablewidget.setCurrentCell( j, 2)
                        self.cfMeshFrame.grid.tablewidget.setItem( j, 2, self.item)

    def actionOnExportButton(self):
        """
        Export ボタンが押された場合の処理
        @type event:Event 
        @param event: マウスクリックイベント
        """
        self.caseFilePath = self.get_caseDirectory()
        if(os.path.exists(self.caseFilePath)):
            message = _('Will you create a setting file for cfMesh?')
            answer = QMessageBox.question(None, "My message", message, QMessageBox.Yes, QMessageBox.No)
            if answer == QMessageBox.Yes:
                #print ("ID_YES")
                self.mainControl.perform(self.caseFilePath)
                
    def actionOnMakeCartesianMeshButton(self):
        """
        MakeCartesianMesh ボタンが押された場合の処理
        @type event:Event 
        @param event: マウスクリックイベント
        """
        #print("MakeCartesianMesh")

        self.caseFilePath = self.get_caseDirectory()
        if(os.path.exists(self.caseFilePath)):
            message = _('Will you create a cartesianMesh?')
            answer = QMessageBox.question(None, "My message", message, QMessageBox.Yes, QMessageBox.No)
            if answer == QMessageBox.Yes:
                #print ("ID_YES")
                self.mainControl.makeCartesianMeshPerform(self.caseFilePath)

    def actionOnCheckMeshButton(self):
        """
        CheckMesh ボタンが押された場合の処理
        @type event:Event 
        @param event: マウスクリックイベント
        """
        #print("CheckMesh")

        self.caseFilePath = self.get_caseDirectory()
        if(os.path.exists(self.caseFilePath)):
            message = _('Will you check a Mesh?')
            answer = QMessageBox.question(None, "My message", message, QMessageBox.Yes, QMessageBox.No)
            if answer == QMessageBox.Yes:
                #print ("ID_YES")
                self.mainControl.checkMeshPerform(self.caseFilePath)

    def actionOnViewMeshButton(self):
        """
        ViewMesh ボタンが押された場合の処理
        @type event:Event 
        @param event: マウスクリックイベント
        """
        #print("ViewMesh")

        self.caseFilePath = self.get_caseDirectory()
        if(os.path.exists(self.caseFilePath)):
            message = _('Will you view a Mesh?')
            answer = QMessageBox.question(None, "My message", message, QMessageBox.Yes, QMessageBox.No)
            if answer == QMessageBox.Yes:
                #print ("ID_YES")
                self.mainControl.viewMeshPerform(self.caseFilePath)

    def actionOnEditMeshDictButton(self):
        """
        EditDict ボタンが押された場合の処理
        @type event:Event 
        @param event: マウスクリックイベント
        """
        #print("EditMeshDict")

        self.caseFilePath = self.get_caseDirectory()
        if(os.path.exists(self.caseFilePath)):
            message = _('Will you edit the meshDict?')
            answer = QMessageBox.question(None, "My message", message, QMessageBox.Yes, QMessageBox.No)
            if answer == QMessageBox.Yes:
                #print ("ID_YES")
                self.mainControl.editMeshDictPerform(self.caseFilePath)

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
    #PATH_4_OPENFOAM = "/opt/OpenFOAM/OpenFOAM-v2006"
    BASHRC_PATH_4_OPENFOAM = PATH_4_OPENFOAM + "/etc/bashrc"
    CFMESH_PATH_TEMPLATE = PATH_4_OPENFOAM + "/modules/cfmesh/tutorials/cartesianMesh/singleOrifice"
    SOLVER_PATH_TEMPLATE = os.path.expanduser(configDict["dexcs"] + "/template/dexcs")
    #SOLVER_PATH_TEMPLATE = "/opt/DEXCS/template/dexcs"
    SLASH_STR             = "/"
    DOT_STR               = "."
    DOT_SLASH             = "./"
    SURFACE_FEATURE_EDGES = "surfaceFeatureEdges -angle"
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

    def perform(self, CaseFilePath):
        """
        exportボタン押下後の処理を全て行う。
        """
        #print ("MainControl::perform")

        ijk = 99
        #print(_("hello %d") % ijk)

        #print(CaseFilePath)
        self.makeStlFile(CaseFilePath)
        ### step2 ### convert stl to fms file ##############################
        #        using surfaceFeatureEdges command
        #self.fmsFileName = self.dirName + MainControl.SLASH_STR + self.fileStem + MainControl.DOT_FMS_STR
        self.fmsFileName = CaseFilePath + MainControl.SLASH_STR + self.fileStem + MainControl.DOT_FMS_STR
        #print('outputFms=' + self.fmsFileName)
        command = '. ' + MainControl.BASHRC_PATH_4_OPENFOAM + ";" + MainControl.SURFACE_FEATURE_EDGES
        command = command + MainControl.SPACE_STR + self.viewControl.get_featureAngleValue()
        command = command + MainControl.SPACE_STR + self.stlFileName + MainControl.SPACE_STR
        command = command + self.fmsFileName
        #print("command =" + command)
        os.system(command)


        constantFolder = CaseFilePath + "/constant" 

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
        templateSolver = self.SOLVER_PATH_TEMPLATE
        if not os.path.isdir(constantFolder):
            command = "cp -r " + templateSolver + "/constant " + CaseFilePath + "/"
            #print(command)
            os.system(command)
            command = "rm -rf " + constantFolder + "/polyMesh"
            os.system(command)

        systemFolder = CaseFilePath + "/system" 
        if not os.path.isdir(systemFolder):
            command = "cp -r " + templateSolver + "/system " + CaseFilePath + "/"
            os.system(command)

        zeroFolder = CaseFilePath + "/0" 
        if not os.path.isdir(zeroFolder):
            command = "cp -rf " + templateSolver + "/0 " + CaseFilePath + "/"
            os.system(command)

        self.makeMeshDict(CaseFilePath)

    def makeMeshDict(self, CaseFilePath):
        """
        objSettingのGUIパネルにて指定した各種パラメタを読み取って、OpenFOAMに必要なmeshDictを作成する
        """
        dictName = CaseFilePath + MainControl.SLASH_STR + MainControl.MESH_DICT_STR
        meshDict = open(dictName , 'w')

        if self.viewControl.get_refinementOption() == 1 :
            strings = ['//CellSize\n']
        else:
            strings = ['//RefLevel\n']
        meshDict.writelines(strings)        

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
               'maxCellSize\t' + str(self.viewControl.get_maxCellSizeValue()) + ';\n'
               '\n',
               '// minimum cell size allowed in the automatic refinement procedure (optional)\n',
               ]
        meshDict.writelines(strings)


        minCellSizeValue = self.viewControl.get_minCellSizeValue()
        if str(minCellSizeValue) != Model.EMPTY_STR:
            meshDict.write('minCellSize\t' + str(minCellSizeValue) + ';\n')
        else:	
            meshDict.write('//minCellSize\t' + ';\n')

        FmsFileName = os.path.basename(self.fmsFileName)

        if self.viewControl.get_untangleLayerCHKOption() == 1 :
            untangleLayerString = '\tuntangleLayers    0; // \n'
        else :
            untangleLayerString = '\t// untangleLayers    0; // \n'

        if self.viewControl.get_optimiseLayerCHKOption() == 1 :
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
               		'  \t\tnSmoothNormals\t3;\n'
               		'\t\n'
               		'  \t\t// maximum number of iterations\n'
               		'  \t\t// of the whole procedure (optional)\n'
               		'  \t\tmaxNumIterations\t5;\n'
               		'\t\n'
               		'  \t\t// ratio between the maximum layer thickness\n'
               		'  \t\t// and the estimated feature size (optional)\n'
               		'  \t\tfeatureSizeFactor\t0.4;\n'
               		'\t\n'
               		'  \t\t// activale 1 or deactivate 0 calculation of normal\n'
               		'  \t\t// (optional)\n'
               		'  \t\treCalculateNormals\t1;\n'
               		'\t\n'
               		'  \t\t// maximum allowed thickness variation of thickness\n'
               		'  \t\t// between two neighbouring points, devided by\n'
               		'  \t\t// the distance between the points (optional)\n'
               		'  \t\trelThicknessTol\t0.01;\n'
               		'\t}\n'
               		'\t\n'
                    '\tpatchBoundaryLayers\n',
                    '\t{\n'
                    ]
        meshDict.writelines(strings2)

        # nLayers, thicknessRatio // BoundaryLayer チェックされたもの
        iRow=0
        while (self.viewControl.get_gridTableValue(iRow,0)):
            iRow = iRow + 1
            if self.viewControl.get_gridTableValue(iRow-1,3) == 2:
                strings3 = [         
                '\t\t'                 + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
                '\t\t{\n',
                '\t\t\t// number of layers (optional)\n',
                '\t\t\tnLayers    '    + str(self.viewControl.get_gridTableValue(iRow-1,4)) + ';\n',
                '\t\t\n',
                '\t\t\t// thickness ratio (optional)\n',
                '\t\t\tthicknessRatio ' + str(self.viewControl.get_gridTableValue(iRow-1,5)) + ';\n',
                '\t\t\n',
                '\t\t\t// max thickness of the first layer (optional)\n',
                '\t\t\t// maxFirstLayerThickness ' + '0.5; // [m]\n',
                '\t\t\n',
                '\t\t\t// active 1 or inactive 0\n',
                '\t\t\tallowDiscontinuity ' + '1;\n',
                '\t\t}\n'
                ]
                meshDict.writelines(strings3)
        # end of nLayers, thicknessRatio 
        #print ('get_keepCellsIntersectingBoundaryCHKOption')
        #print (self.viewControl.get_keepCellsIntersectingBoundaryCHKOption())
        if self.viewControl.get_keepCellsIntersectingBoundaryCHKOption() == 1 :
            keepCellsIntersectingBoundaryString = 'keepCellsIntersectingBoundary    1; // 1 keep or 0 only internal cells are used\n'
        else :
            keepCellsIntersectingBoundaryString = '// keepCellsIntersectingBoundary    1; // 1 keep or 0 only internal cells are used\n'

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
        '// patchName\n',
        '//\t{\n',
        '//\t\tkeepCells 1; // 1 active or 0 inactive\n',
        '//\t}\n',
        '}\n',
        '\n',
        '// remove cells where distinct parts of the mesh are joined together (optional)\n',
        '// active only when keepCellsIntersectingBoundary is active\n',
        '// checkForGluedMesh    0; // 1 active or 0 inactive\n',
        '\n',
        '// remove cells the cells intersected\n',
        '// by the selected patched/subsets\n',
        '// from the mesh template (optional)\n',
        '// it is active when keepCellsIntersectingBoundary\n',
        '// is switched on\n',
        'removeCellsIntersectingPatches\n',
        '{\n',
        '// patchName\n',
        '//\t{\n',
        '//\t\tkeepCells 1; // 0 remove or 1 keep\n',
        '//\t}\n',
        '}\n',
        '\n',
        '// refinement zones at the surface\n',
        '// of the mesh (optional)\n',
        'localRefinement\n',
        '{\n'
        ]
        meshDict.writelines(strings4)

        # local refinement // cellSize指定されており、region以外のもの
        iRow=0

        while (self.viewControl.get_gridTableValue(iRow,0)):
            iRow = iRow + 1
            #print ('### ', self.viewControl.get_gridTableValue(iRow-1,2) , self.viewControl.get_gridTableValue(iRow-1,1))
            if (self.viewControl.get_gridTableValue(iRow-1,2) != Model.EMPTY_STR and 
                self.viewControl.get_gridTableValue(iRow-1,1) != MainControl.REGION_STR):
                refThickness = float(self.viewControl.get_gridTableValue(iRow-1,2)) 
                if self.viewControl.get_refinementOption() == 1 :
                    refLevel = 0
                    refValue = float(self.viewControl.get_maxCellSizeValue())/float(self.viewControl.get_gridTableValue(iRow-1,2))
                    while refValue>1:
                        refLevel = refLevel + 1
                        refValue = refValue/2                				
                    strings5 = [
                    '\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
                    '\t{\n',
                    '\t\tcellSize\t' + str(self.viewControl.get_gridTableValue(iRow-1,2)) + ';\n',
                    '\t\n',
                    '\t\t// additional refinement levels\n',
                    '\t\t// to the maxCellSize\n',
                    '\t\t// additionalRefinementLevels\t' + str(refLevel) + ';\n',
                    '\t\n',
                    '\t\t// thickness of the refinement region;\n',
                    '\t\t// away from the patch;\n',
                    '\t\t// refinementThickness\t'  + str(refThickness) + ';\n',			
                    '\t}\n'
                               ]
                else :
                    refSize = str(self.viewControl.get_maxCellSizeValue())
                    refValue = float(self.viewControl.get_maxCellSizeValue())/float(self.viewControl.get_gridTableValue(iRow-1,2))
                    while refValue>1:
                        refValue = refValue - 1
                        refSize = str(float(refSize)/2) 
                    strings5 = [
                    '\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
                    '\t{\n',
                    '\t\t// cellSize\t' + refSize + ';\n',
                    '\t\n',
                    '\t\t// additional refinement levels\n',
                    '\t\t// to the maxCellSize\n',
                    '\t\t additionalRefinementLevels\t' + str(self.viewControl.get_gridTableValue(iRow-1,2)) + ';\n',
                    '\t\n',
                    '\t\t// thickness of the refinement region;\n',
                    '\t\t// away from the patch;\n',
                    '\t\t// refinementThickness\t'  + str(refThickness) + ';\n',			
                    '\t}\n'
                               ]
                meshDict.writelines(strings5)

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
        iRow=0
        boxNumber=0    
        while (self.viewControl.get_gridTableValue(iRow,0)):
            for obj in self.doc.Objects:
                if obj.Label == self.viewControl.get_gridTableValue(iRow,0):    
                    iRow = iRow + 1
                    if self.viewControl.get_gridTableValue(iRow-1,1) == MainControl.REGION_STR:
                        boxNumber = boxNumber + 1
                        xmax = obj.Shape.BoundBox.XMax
                        xmin = obj.Shape.BoundBox.XMin
                        ymax = obj.Shape.BoundBox.YMax
                        ymin = obj.Shape.BoundBox.YMin
                        zmax = obj.Shape.BoundBox.ZMax
                        zmin = obj.Shape.BoundBox.ZMin
                        centerX = 0.5*(xmax+xmin)
                        centerY = 0.5*(ymax+ymin)
                        centerZ = 0.5*(zmax+zmin)
                   	## 2019/7/15 分割レベルとセルサイズの不整合を調整するパラメタ（objRefPar）を導入
                        objRefPar = 1.1 
                        if self.viewControl.get_refinementOption() == 1 :
                            strings7 = [
                            '\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
                            '\t{\n',
                            #'\t\tcellSize\t' + str(self.viewControl.get_gridTableValue(iRow-1,2)) + ';\n',
                            '\t\tcellSize\t' + str(float(self.viewControl.get_gridTableValue(iRow-1,2))*objRefPar ) + ';\n',
                            '\t\tcentre (' + str(centerX) + MainControl.SPACE_STR + str(centerY) + MainControl.SPACE_STR + str(centerZ) + ');\n',
                            '\t\tlengthX\t' + str(xmax-xmin) + ';\n',
                            '\t\tlengthY\t' + str(ymax-ymin) + ';\n',
                            '\t\tlengthZ\t' + str(zmax-zmin) + ';\n',
                            '\t\ttype box;\n',
                            '\t}\n'
                                        ]
                        else :
                            strings7 = [
                            '\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
                            '\t{\n',
                            '\t\tadditionalRefinementLevels\t' + str(self.viewControl.get_gridTableValue(iRow-1,2)) + ';\n',
                            '\t\tcentre (' + str(centerX) + MainControl.SPACE_STR + str(centerY) + MainControl.SPACE_STR + str(centerZ) + ');\n',
                            '\t\tlengthX\t' + str(xmax-xmin) + ';\n',
                            '\t\tlengthY\t' + str(ymax-ymin) + ';\n',
                            '\t\tlengthZ\t' + str(zmax-zmin) + ';\n',
                            '\t\ttype box;\n',
                            '\t}\n'
                                        ]

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

        if self.viewControl.get_stopAfterEdgeExtractionCHKOption() == 1 :
            stopAfterEdgeExtractionString = '\t\tstopAfter\tedgeExtraction;\n'
        else :
            stopAfterEdgeExtractionString = '\t//\tstopAfter\tedgeExtraction;\n'

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
        stopAfterEdgeExtractionString ,
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

        iRow=0
        while (self.viewControl.get_gridTableValue(iRow,0)):
                        iRow = iRow + 1
                        strings9 = [
                        '\t\t' + str(self.viewControl.get_gridTableValue(iRow-1,0)) + '\n',
                        '\t\t{\n',
                        '\t\t\tnewName '+ str(self.viewControl.get_gridTableValue(iRow-1,0)) + ';\n',
                        '\t\t\ttype '+ str(self.viewControl.get_gridTableValue(iRow-1,1)) + ';\n',
                        '\t\t}\n',
                        ]
                        meshDict.writelines(strings9)
        strings10 = [
        '\t}\n'
        '}\n',
        ]
        meshDict.writelines(strings10)

        #end of renaming patch's type // 


        meshDict.close()
        message = _(u'The configuration file system/meshDict for cfMesh has been created.')        
        self.viewControl.showMessageDialog(message)
        
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
        #print("makeStlFile")
        ijk = 111
        #print(_("hello %d") % ijk)

        self.fileStem = os.path.splitext(self.caseFilePath)[0]
        self.fileStem = self.fileStem.split(MainControl.SLASH_STR)[-1]
        self.stlFileName = CaseFilePath + MainControl.SLASH_STR + self.fileStem + '.stl'
        self.fileName = CaseFilePath + MainControl.SLASH_STR + self.fileStem

        outputStlFile = open(self.stlFileName, 'w')

        i = 0
        while(True):
            #print("i = %d" % i)
            tableValue = self.viewControl.get_gridTableValue(i, 0)
            if tableValue == "":
                #print ("empty string break")
                break
            #print("i=%d :tableValue= [%s]" % (i, tableValue))
            k = 0
            for obj in self.doc.Objects:
                __objs__=[]
                #print("-k=%d obj.Label= %s" % (k, obj.Label))
                if obj.Label == tableValue:#表中のobjectNameがobj.Labelに一致したobj
                    #print("--obj.Label()==" + obj.Label)
                    if self.viewControl.get_gridTableValue(i,1) != "region":#Typeがregion以外のものについてstl出力
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
                k = k + 1
            i = i + 1
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
        import dexcsCfdTools

        from dexcsCfdAnalysis import _CfdAnalysis


        self.caseFilePath = App.ActiveDocument.FileName        
        model = Model(self.caseFilePath)
        self.doc = model.open()
        self.fcListData = model.get_fcListData()
        sumOf3Edges = model.get_sumOf3EdgesOfCadObjects()
        cellMax = Decimal(sumOf3Edges/60)#適切に数値を丸める
        #print ("cellMax = %6.2lf" % cellMax)


        outputPath1 = ""
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, _CfdAnalysis):
                if obj.IsActiveAnalysis:
                    outputPath1 = obj.OutputPath

        if outputPath1:
            self.dirName = outputPath1
        else:
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
        print(self.dirName)
        self.viewControl = ViewControl(self)
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
