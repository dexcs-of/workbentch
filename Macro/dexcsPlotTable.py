#!/usr/bin/python3
#  coding: utf-8
#
"""
dexcsPlotTable.py
"""

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.disable(logging.CRITICAL)


FREECADPATH = "/usr/lib/freecad-daily/lib"
import sys
sys.path.append(FREECADPATH)

#import sys
#import FreeCAD

import os
import csv
import math

import copy

import numpy as np
import re

import shutil
import glob
import multiprocessing
import threading
import time
import pathlib

#from PyQt4 import QtCore, QtGui
#from PySide import QtCore, QtGui
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import Util_Table
import dexcsFunctions
from PySide2 import QtCore
import dexcsCfdTools



#プロットツール連携状況に合わせてセットすること
#from dexcsCfdPostPlot import PostPlot
#from collections import OrderedDict
#import runPlotPost as plotter
import dexcsPlotPost

fontName = "Monospace"


#左列挙欄の各ファイルのマトリックスデータとラベル名を辞書式として管理
Use_checkedfile_Matrixes = {}
Use_checkedfile_rowLabels  = {}
Use_checkedfile_Matrixes_other = {}
Use_checkedfile_rowLabels_other  = {}

other_flag = False


#テーブルのカラム表示は一定なのでグローバル変数とした
column_header = ["id","name","s/f","X","Y", "abs","length"]

#各ファイルのデータ登録を辞書型にしたため省略できるが、今後チェックボックス状態でbplt出力有無の切替に活用できる可能性あり
checked_postProcessisng_files = []
useindex_checked_postProcessisng_files = []

#各ファイルのデータ登録を辞書型にしたため省略できるが、作業的に後回しとしている。
table_contents = []
data_columns = []

def diy_is_num(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True
    
#---------------------
#  inputTextDialog class
#---------------------
class inputTextDialog:

    def __init__(self, title, mess):
        self.title = title
        self.mess = mess
        self.status = "CANCEL"
        self.inputText = ""
        self.Dialog = QDialog()

    def setupDialog(self):
        Dialog = QDialog()
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle(self.title)           #titleが表示されていなかったので追加
        self.verticalLayout = QVBoxLayout(Dialog)
        #label
        self.label = QLabel(Dialog)
        self.label.setText(self.mess)
        self.verticalLayout.addWidget(self.label)
        #lineEdit配置
        #一時的にただのOK,NGダイアログとするため、下記一行コメントアウト
        #self.lineEdit = QLineEdit(Dialog)

        #self.verticalLayout.addWidget(self.lineEdit)
        #cancel, ok button 配置
        #  spacer配置
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        #  calcelButton
        self.pushButtonCancel = QPushButton(Dialog)
        self.pushButtonCancel.setText(u"Cancel")
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        #  okButton
        self.pushButtonOk = QPushButton(Dialog)
        self.pushButtonOk.setText(u"OK")
        self.horizontalLayout.addWidget(self.pushButtonOk)
        #  button配置
        self.verticalLayout.addLayout(self.horizontalLayout)
        #event
        QMetaObject.connectSlotsByName(Dialog)
        self.pushButtonCancel.clicked.connect(self.onCancel)
        self.pushButtonOk.clicked.connect(self.onOk)
        self.Dialog = Dialog

    def show(self):
        self.setupDialog()
        self.Dialog.exec_()
        return (self.status, self.inputText)

    def close(self, *args):
        self.Dialog.close()

    def onCancel(self):
        self.status = "CANCEL"
        self.inputText = ""
        self.close()

    def onOk(self):
        self.status = "OK"
        #self.inputText = self.lineEdit.text()
        self.inputText = ""
        self.close()


#------------------------
#  getFileNamesDialog class
#------------------------
class getFileNamesDialog(QWidget):

    def __init__(self, currDir):
        super().__init__()
        self.currDir = currDir
        self.files = []
        self.Dialog = QFileDialog()

    def openFileNamesDialog(self):
        title = "select file"
        patterns = "All Files (*);;Python Files (*.py)"
        fileNames, _selectedFilter = self.Dialog.getOpenFileNames(self, title, self.currDir, patterns)
        self.files = fileNames

    def show(self):
        self.openFileNamesDialog()
        return self.files


#class elements_Tree(QWidget):
#    def __init__(self, parent=None):
#        super().__init__(parent)

class elements_Tree(QWidget):
    def __init__(self,ins_filenamegroup, parent=None):
        super().__init__(parent)


        tree_widget = QTreeWidget()
        self.tree_widget = tree_widget

        tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        tree_widget.customContextMenuRequested.connect(self.contextMenu)


        def addItem(branch, name, num, num2):
            item = QTreeWidgetItem(branch)
            item.setData(0, Qt.CheckStateRole, Qt.checked)
            item.setText(0, name)
            item.setText(1, str(num))
            item.setText(2, str(num2))


        #branch1 = QTreeWidgetItem()
        #branch1.setData(0, Qt.CheckStateRole, Qt.Checked)
        #branch1.setText(0, "branch1")

        #branch2 = QTreeWidgetItem()
        #branch2.setData(0, Qt.CheckStateRole, Qt.Checked)
        #branch2.setText(0,"branch2")

        if ins_filenamegroup == None:
            pass
            #temp_item = QTreeWidgetItem()
            #temp_item.setData(0, Qt.CheckStateRole, Qt.Unchecked)
            #temp_item.setText(0, "Dummy")     
            #self.tree_widget.addTopLevelItem(temp_item)
            #temp_item.setExpanded(True)

        else:
            for item in ins_filenamegroup:
            #for item in namegroup:
                temp_item = QTreeWidgetItem()
            
                #temp_item.setData(0, Qt.CheckStateRole, Qt.Checked)
                #temp_item.setData(0, Qt.CheckStateRole, False )
                temp_item.setData(0, Qt.CheckStateRole, Qt.Unchecked)
            
                temp_item.setText(0, item)
                       
                self.tree_widget.addTopLevelItem(temp_item)
                temp_item.setExpanded(True)

        #addItem(branch1, "item1-1", 1, 100)
        #addItem(branch1, "item1-2", 2, 200)
        #addItem(branch2, "item2-1", 3, 300)
        #addItem(branch2, "item2-2", 4, 400)


        tree_widget.setColumnCount(1)
        tree_widget.setHeaderLabels(["files"])

        tree_widget.itemClicked.connect(self.selectItem)
        tree_widget.itemChanged.connect(self.changeItem)

        #branch1.setExpanded(True)
        #branch2.setExpanded(True)

        layout = QVBoxLayout()
        layout.addWidget(tree_widget)

        self.setLayout(layout)

        self.setWindowTitle("check_tree")
        self.show()

    def selectItem(self):
        if self.tree_widget.selectedItems() == []:
            return
        item = self.tree_widget.selectedItems()[0]
        logging.debug(item.text(0))

    def changeItem(self, item, column):

        global checked_postProcessisng_files 
        checked_postProcessisng_files = []
    
        for i in range(self.tree_widget.topLevelItemCount()):
            branch = self.tree_widget.topLevelItem(i)
            if branch.checkState(0):
                logging.debug(branch.text(0))
                
                checked_postProcessisng_files.append(branch.text(0))                


    def checkBranch(self, branch, check=2):
        for i in range(branch.childCount()):
            item = branch.child(i)
            item.setCheckState(0, check)

    def checkAll(self, check=2):
        for i in range(self.tree_widget.topLevelItemCount()):
            branch = self.tree_widget.topLevelItem(i)
            branch.setCheckState(0, check)
            self.checkBranch(branch, check)

    def contextMenu(self, point):
        menu = QMenu(self)
        check_all = menu.addAction("Check all")
        uncheck_all = menu.addAction("Uncheck all")

        action = menu.exec_(self.mapToGlobal(point))

        if action == check_all:
            self.checkAll()
        elif action == uncheck_all:
            self.checkAll(0)


    def addcheckedItem(self):
        #eventMask
        self.maskEvent = True
            
        for item in filenamegroup:
        #for item in namegroup:
            temp_item = QTreeWidgetItem()
            
            #temp_item.setData(0, Qt.CheckStateRole, Qt.Checked)
            #temp_item.setData(0, Qt.CheckStateRole, False )
            temp_item.setData(0, Qt.CheckStateRole, Qt.Checked)
            
            temp_item.setText(0, item)
           
            
            self.tree_widget.addTopLevelItem(temp_item)
            temp_item.setExpanded(True)
            
        #mask解除
        self.maskEvent = False

    def setoneItem(self):
        #eventMask
        self.maskEvent = True
                        
        temp_item = QTreeWidgetItem()

        temp_item.setData(0, Qt.CheckStateRole, Qt.Checked)
            
        temp_item.setText(0, "test")
           
            
        self.tree_widget.addTopLevelItem(temp_item)
        temp_item.setExpanded(True)


            
        #mask解除
        self.maskEvent = False



#-------------------
#  textEdit class
#-------------------
class textEdit(QTextEdit):
    try:
        reloadSignal =  pyqtSignal(str)
    except:
        reloadSignal =  Signal(str)


#----------------------
#  Ui_MainWindow class
#----------------------
class Ui_MainWindow(object):
    """ gridTableのGUIを作成する"""

    def __init__(self):
        self.showSelectDir = ""
        self.loadDir = ""

    def setupUi(self, MainWindow, Table, default_tree, other_tree, showSelectDir, loadDir,typeComboBox ):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(509, 270)

        #MainwindowをcentralWidgetにセット
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        #全体のlayout
        self.verticalLayout_top = QVBoxLayout(self.centralwidget)
        self.verticalLayout_top.setObjectName("verticalLayout_top")

        #frameを定義(splitter上側)
        self.frameUp = QFrame()
        self.frameUp.setFrameShape(QFrame.StyledPanel)
        self.frameUp.setFrameShadow(QFrame.Raised)

        #このlayout内に各partsを配置し、verticalLayout_topにセット
        self.verticalLayout = QVBoxLayout(self.frameUp)
        self.verticalLayout.setObjectName("verticalLayout")

        #hLayoutに(buttons)をセット
        self.hLayout_buttons = QHBoxLayout()
        self.hLayout_buttons.setObjectName("hLayout_buttons")

        #
        self.verticalLayout.addLayout(self.hLayout_buttons)



        self.main_hLayout = QHBoxLayout()
        self.hLayout_buttons.setObjectName("main_layout")


        self.Left_verticalLayout = QVBoxLayout()



        self.defalut_tree = default_tree
        self.defalut_tree.setObjectName("treewidget")
                
        self.Left_verticalLayout.addWidget(self.defalut_tree)


        self.horizontalLayout_2a = QHBoxLayout()

        self.ConfirmFileButton = QPushButton()#self.frame2を削除
        #multi_lang
        self.ConfirmFileButton.setObjectName("ConfirmFileButton")
        self.ConfirmFileButton.setText(_("Confirm on gedit"))
        self.horizontalLayout_2a.addWidget(self.ConfirmFileButton)

        #self.Left_verticalLayout.addWidget(self.horizontalLayout_2a)

        self.min_horizontalGroupBox = QGroupBox('')
        self.min_horizontalGroupBox.setLayout(self.horizontalLayout_2a)

        self.Left_verticalLayout.addWidget(self.min_horizontalGroupBox)


        self.other_tree = other_tree
        self.other_tree.setObjectName("treewidget2")

        self.Left_verticalLayout.addWidget(self.other_tree)


        self.horizontalLayout_3 = QHBoxLayout()

        self.AddFileButton = QPushButton()#self.frame2を削除
        #multi_lang
        self.AddFileButton.setObjectName("AddFileButton")
        self.AddFileButton.setText(_("Add File"))
        self.horizontalLayout_3.addWidget(self.AddFileButton)

        #button load2
        self.DeleteFileButton = QPushButton()#self.frame2を削除
        self.DeleteFileButton.setObjectName("DeleteFileButton")
        self.DeleteFileButton.setText(_("Delete File"))
        #20240928 temporaly change to unvisible
        #self.horizontalLayout_3.addWidget(self.DeleteFileButton)


        self.mini_horizontalGroupBox = QGroupBox('')
        self.mini_horizontalGroupBox.setLayout(self.horizontalLayout_3)

        self.Left_verticalLayout.addWidget(self.mini_horizontalGroupBox)

        #group action2
        self.horizontalGroupBox1 = QGroupBox('')
        self.horizontalGroupBox1.setLayout(self.Left_verticalLayout)
        
        self.main_hLayout.addWidget(self.horizontalGroupBox1,1)
        
        
        
        self.fortooltip = QLabel()
        #multi_lang
        self.fortooltip.setText("")
        self.fortooltip.setToolTip(_("Index, ColumnName, Scale_factor, Used_as_x , Used_as_y(multi), Vectorize_flag, Data_length"))

        self.main_hLayout.addWidget(self.fortooltip,0.05)
        

        self.Right_verticalLayout = QVBoxLayout()
        
        #tableをセット
        self.tableWidget = Table                #置き換え
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setObjectName("tableWidget")
        #self.tableWidget.setToolTip(_("Test"))

        #self.main_hLayout.addWidget(self.tableWidget,2)
        
        #self.verticalLayout.addWidget(self.tableWidget)
        self.Right_verticalLayout.addWidget(self.tableWidget,8)

        self.showSelectDir = showSelectDir
        self.loadDir = loadDir



        #self.vLayout_6 = QVBoxLayout()

        #button export2
        self.horizontalLayout_6 = QHBoxLayout()
               
                #タイトル名
        #  label_depth
        self.label_title = QLabel()
        #multi_lang
        self.label_title.setText(_("Title"))
        #self.label_title.setSizePolicy(sizePolicy)
        self.horizontalLayout_6.addWidget(self.label_title)
        #  lineEdit
        self.lineEdit_title = QLineEdit()#self.frame2を削除
        self.lineEdit_title.setFixedWidth(200)
        self.lineEdit_title.setObjectName("")
        self.lineEdit_title.setText("Title")
        #self.lineEdit_title.setSizePolicy(sizePolicy)
        self.horizontalLayout_6.addWidget(self.lineEdit_title)

        spacerItemTop = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItemTop)

        #self.vLayout_6.addLayout(self.horizontalLayout_6)
        self.Right_verticalLayout.addLayout(self.horizontalLayout_6,1)


        self.horizontalLayout_6a = QHBoxLayout()


        #Yラベル名
        #  label_depth
        self.label_Ylabel = QLabel()
        #multi_lang
        self.label_Ylabel.setText(_("Y-Label"))
        #self.label_Ylabel.setSizePolicy(sizePolicy)
        self.horizontalLayout_6a.addWidget(self.label_Ylabel)
        #  lineEdit
        self.lineEdit_Ylabel = QLineEdit()#self.frame2を削除
        self.lineEdit_Ylabel.setFixedWidth(200)
        self.lineEdit_Ylabel.setObjectName("")
        self.lineEdit_Ylabel.setText("YLabel")
        #self.lineEdit_Ylabel.setSizePolicy(sizePolicy)
        self.horizontalLayout_6a.addWidget(self.lineEdit_Ylabel)
        
        
        self.PlotButton = QPushButton()#self.frame2を削除
        self.PlotButton.setObjectName("PlotButton")
        #multi_lang
        self.PlotButton.setText(_("plot"))
        self.horizontalLayout_6a.addWidget(self.PlotButton)

        spacerItem6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_6a.addItem(spacerItem6)

        #self.vLayout_6.addLayout(self.horizontalLayout_6)
        self.Right_verticalLayout.addLayout(self.horizontalLayout_6a,1)


        self.horizontalLayout_7 = QHBoxLayout()

        #ファイル名
        #  label_depth
        self.label_filename = QLabel()
        #multi_lang
        self.label_filename.setText(_("Save FileName"))
        #self.label_filename.setSizePolicy(sizePolicy)
        self.horizontalLayout_7.addWidget(self.label_filename)
        #  lineEdit
        self.lineEdit_filename = QLineEdit()#self.frame2を削除
        self.lineEdit_filename.setFixedWidth(200)
        self.lineEdit_filename.setObjectName("")
        self.lineEdit_filename.setText("FileName")
        #self.lineEdit_filename.setSizePolicy(sizePolicy)
        self.horizontalLayout_7.addWidget(self.lineEdit_filename)



        self.SaveButton = QPushButton()#self.frame2を削除
        #multi_lang
        self.SaveButton.setObjectName("SaveButton")
        self.SaveButton.setText(_("save dplt"))
        self.horizontalLayout_7.addWidget(self.SaveButton)







        #button load2
        self.Load2Button = QPushButton()#self.frame2を削除
        self.Load2Button.setObjectName("Load2Button")
        self.Load2Button.setText(_("(not yet) load2"))
        #self.horizontalLayout_7.addWidget(self.Load2Button)

        #spacer
        spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem2)
                
        #button Edit2
        self.reserveButton = QPushButton()#self.frame2を削除
        self.reserveButton.setObjectName("reserveButton")
        self.reserveButton.setText(_("reserve"))
        #self.horizontalLayout_7.addWidget(self.reserveButton)

        spacerItem_button = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem_button)

        #button exit2
        self.exitButton = QPushButton()#self.frame2を削除
        self.exitButton.setObjectName("exitButton")
        self.exitButton.setText("Exit")
        #self.horizontalLayout_7.addWidget(self.exitButton)



        #self.vLayout_6.addLayout(self.horizontalLayout_7)
        self.Right_verticalLayout.addLayout(self.horizontalLayout_7,1)



        self.horizontalLayout_8 = QHBoxLayout()
        
        self.load_name = QLabel()
        #multi_lang
        self.load_name.setText(_("Existing file"))
        self.horizontalLayout_8.addWidget(self.load_name)        
        
        self.typeComboBox = typeComboBox#self.frame2を削除
        self.typeComboBox.addItems(dplt_system)
        
        self.horizontalLayout_8.addWidget(self.typeComboBox)

        #button load
        self.LoadButton = QPushButton()#self.frame2を削除
        self.LoadButton.setObjectName("LoadButton")
        #multi_lang
        self.LoadButton.setText(_("load left-file"))
        self.horizontalLayout_8.addWidget(self.LoadButton)

        self.LookAsTextButton = QPushButton()#self.frame2を削除
        #multi_lang
        self.LookAsTextButton.setObjectName("ConfirmTextButton")
        self.LookAsTextButton.setText(_("LookAsText"))
        self.horizontalLayout_8.addWidget(self.LookAsTextButton)

        spacerItem6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem6)

        #self.vLayout_6.addLayout(self.horizontalLayout_8)
        self.Right_verticalLayout.addLayout(self.horizontalLayout_8,1)

        #group action2
        self.horizontalGroupBox6 = QGroupBox('')
        #self.horizontalGroupBox6.setLayout(self.horizontalLayout_6)
        self.horizontalGroupBox6.setLayout(self.Right_verticalLayout)


        self.main_hLayout.addWidget(self.horizontalGroupBox6,2)

        self.horizontalGroupBox8 = QGroupBox('')
        self.horizontalGroupBox8.setLayout(self.main_hLayout)

        self.verticalLayout.addWidget(self.horizontalGroupBox8)



        #frameを定義（splitterの下側）
        self.frameDown = QFrame()
        self.frameDown.setFrameShape(QFrame.StyledPanel)
        self.frameDown.setFrameShadow(QFrame.Raised)
        #verticalLayout_logを定義
        self.verticalLayout_log = QVBoxLayout(self.frameDown)
        self.verticalLayout_log.setObjectName("verticalLayout_log")
        #labelを定義、セット

        #textEditを定義、セット
        self.textEdit_log = textEdit()
        self.textEdit_log.setObjectName("textEdit_log")
        #self.verticalLayout_log.addWidget(self.textEdit_log)

        #spltterの定義、設定
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.frameUp)
        self.splitter.addWidget(self.frameDown)
        #splitterを埋め込む
        self.verticalLayout_top.addWidget(self.splitter)
        #spliterの位置を設定（8:2に設定）
        spSize = self.splitter.size().height()
        self.splitter.setSizes([spSize * 1.0, spSize * 0.0])

        MainWindow.setCentralWidget(self.centralwidget)

        #label, lineEditをhLayout_buttonsに追加
        #  reloadButton
        self.button_open = QPushButton()
        self.button_open.setObjectName("button_open")
        self.button_open.setText("")
        self.button_open.setIcon(QPixmap("calculator32ML.png"))
        self.button_open.setIconSize(QSize(24,24))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button_open.setSizePolicy(sizePolicy)
        #self.hLayout_buttons.addWidget(self.button_open)

        #  reloadButton
        self.button_open3 = QPushButton()
        self.button_open3.setObjectName("button_open3")
        self.button_open3.setText("")
        #self.button_open3.setIcon(QPixmap("reload3.png"))
        self.button_open3.setIcon(QPixmap("reloadSetLoad.png"))
        self.button_open3.setIconSize(QSize(24,24))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button_open3.setSizePolicy(sizePolicy)
        #self.hLayout_buttons.addWidget(self.button_open3)

        #  showSelectDirを挿入
        self.label_loadDir = QLabel()
        self.label_loadDir.setObjectName("label_loadDir")
        self.label_loadDir.setText("loadFile: " + self.loadDir)
        self.hLayout_buttons.addWidget(self.label_loadDir)

        #---------------------
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        #mainWindowのcolorを設定（lightGray）
        MainWindow.setAutoFillBackground(True)
        p = MainWindow.palette()
        p.setColor(MainWindow.backgroundRole(), Qt.lightGray)
        MainWindow.setPalette(p)

        QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        #MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        MainWindow.setWindowTitle("MainWindow")


#------------------
#  gridTable class
#------------------
class gridTable(Ui_MainWindow):
    """ simpleTableのUi_mainWindowクラスを継承"""

    #def __init__(self, rowLabels, colLabels, rowColVals):
    def __init__(self, rowLabels,  rowColVals):
        titleDir = learnDir
        if len(titleDir) > 80:
            titleDir = "..." + titleDir[-77:]
        self.showSelectDir = titleDir

        loadDir = rowLabels[0]
        
        
        if len(loadDir) > 80:
            loadDir = "..." + loadDir[-77:]
        self.loadDir = loadDir

        self.MainWindow = QMainWindow()           #redefine
        self.Table = Util_Table.Table()             #use original tablewidget
        
        
        
        self.default_tree = elements_Tree(filenamegroup)
        self.other_tree = elements_Tree(None)
        
        self.typeComboBox = QComboBox()
        self.setupUi(self.MainWindow, self.Table, self.default_tree, self.other_tree, self.showSelectDir, self.loadDir,self.typeComboBox)       #making GUI
        #font setting
        font = QFont()
        font.setFamily(fontName)
        self.MainWindow.setFont(font)
        #eventを作成
        self.createEvent()
        #attribute
        self.rowLabels = rowLabels
        #self.colLabels = colLabels
        self.rowColVals = rowColVals
        self.maskEvent = True                       #for masking event
        #titleを設定(multi-lang)
        title = (_("caseDir is :") ) + titleDir
        self.MainWindow.setWindowTitle(title)
        #selectDirの設定
        #self.showSelectDir = titleDir
        #widowSizeを取得
        
        #optDir = os.getenv("OptPlatform")
        optDir = learnDir


        fileName = optDir + "/gridTable_winSize"
        self.width = 500
        self.height = 300
        if os.path.exists(fileName):
            f = open(fileName); line = f.read(); f.close()
            words = line.split()
            if len(words) >= 2:
                self.width = int(words[0])
                self.height = int(words[1])
        #thread関連は不使用
        #self.flagThread = "run"     #thread停止flag
        #self.runLogThread()         #thread起動
        #starting()

    #
    #  main
    #---------------
    def main(self):
        self.createMatrix()     #row, colLabelをセット
        self.setMatrixData()    #cellにデータをセット
        self.MainWindow.resize(self.width, self.height)
        self.MainWindow.show()
    #
    #  close
    #----------
    def close2(self):
        self.flagThread = "stop"        #thread停止
        self.save_tableattr()
        qApp.quit()
        #ending処理
        #ending()

    def save_tableattr(self):
        """ windowSizeを保存する"""
        optDir = os.getenv("OptPlatform")
        fileName = optDir + "/gridTable_winSize"
        width = self.MainWindow.width()
        height = self.MainWindow.height()
        line = str(width) + " " + str(height)
        f = open(fileName, "w"); f.write(line); f.close()

        #selectDirの読み込み、表示
        fileName = optDir + "/selectDir"
        f = open(fileName)
        self.showSelectDir = f.read().split()[0]
        f.close() 


    def createEvent(self):
        """ event作成"""
        #toolBar
        # self.actionOpen.triggered.connect(self.onReloadTable)
        # self.actionSave.triggered.connect(self.onSaveTable)
        # self.actionClose.triggered.connect(self.onCloseTable)

        self.button_open.clicked.connect(self.onReloadTable)
        self.button_open3.clicked.connect(self.onReloadTable3)
       
        #tableWidget
        self.Table.itemClicked.connect(self.onItemClick)
        self.Table.enterSignal.connect(self.onEnterSignalFromEditor)
        
        self.default_tree.tree_widget.itemClicked.connect(self.onfile_enumClick)
        self.other_tree.tree_widget.itemClicked.connect(self.onfile_enumClick_other)




        ###########################################(20200611)追加ボタンと実装のconnect#####################################################################################

        QObject.connect(self.ConfirmFileButton, SIGNAL("clicked()"), self.actionOnConfirmFileButton)

        QObject.connect(self.AddFileButton, SIGNAL("clicked()"), self.actionOnAddFileButton)
        QObject.connect(self.DeleteFileButton, SIGNAL("clicked()"), self.actionOnDeleteFileButton)
        
        QObject.connect(self.PlotButton, SIGNAL("clicked()"), self.actionOnPlotButton)
        QObject.connect(self.SaveButton, SIGNAL("clicked()"), self.actionOnSaveButton)
        QObject.connect(self.LookAsTextButton, SIGNAL("clicked()"), self.actionOnLookAsTextButton)                
        QObject.connect(self.LoadButton, SIGNAL("clicked()"), self.actionOnLoadButton)        
        QObject.connect(self.Load2Button, SIGNAL("clicked()"), self.actionOnLoad2Button)        
        QObject.connect(self.reserveButton, SIGNAL("clicked()"), self.actionOnreserveButton)

        QObject.connect(self.exitButton, SIGNAL("clicked()"), self.actionOnExitButton)
        
        ###########################################(20200611)追加ボタンと実装のconnect#####################################################################################
        #self.textEdit_log.reloadSignal.connect(self.setLogText)

    #------- event handler ------------
    def onReloadTable(self):
        self.setDefaultMatrix(filenamegroup)
    def onReloadTable2(self):
        self.setDefaultMatrix(filenamegroup)
    def onReloadTable3(self):
        logging.debug("no func")

    def onSaveTable(self):
        selectDirName = os.getenv("OptPlatform") + "/selectDir"
        f = open(selectDirName); selectDir = f.read(); f.close()
        projDir, selectDir = learnDir,learnDir
        score_len=7
        table = Util_Table.tableWidget(self.tableWidget)
        for i in range(self.tableWidget.rowCount()):
            conts = []
            # importance.append(val)
            if i != 0:
                for j in range(score_len-1):
                    val = float(table.getCellValue(0, j+1)) * float(table.getCellValue(i, j+1))
                    conts.append(val)
                max_value = max(conts)
                if max_value> 0.00000001:
                    max_index = conts.index(max_value)
                    table.setCellValue(i, 2*score_len+4 , "sub" + str(max_index+1))
                else:
                    table.setCellValue(i, 2*score_len+4 , "score")
            else:
                pass


    def onEnterSignalFromEditor(self):
        self.enterSignalFromEditor()

    def onCloseTable(self):
        self.close2()
    def onUpTable(self):
        logging.debug("----up")
    def onDownTable(self):
        logging.debug("----down")
    def onItemClick(self, widgetItem):


        self.maskEvent = True
        
        table = Util_Table.tableWidget(self.tableWidget)

        for counter in range(self.tableWidget.rowCount()):
            table.setCellValue(counter,0,str(counter))
            
            
            if not diy_is_num(table.getCellValue(counter,2)):
               table.setCellValue(counter,2,"1") 
            if not(table.getCellValue(counter,3) == "Use" or table.getCellValue(counter,3) == "---"):
               table.setCellValue(counter,3,"---")
            if not(table.getCellValue(counter,4) == "Use" or table.getCellValue(counter,4) == "---"):
               table.setCellValue(counter,4,"---")
            #if (table.getCellValue(counter,5) == "X"):
               #table.setCellValue(counter,5,"---")            
            if not(table.getCellValue(counter,5) == "Use" or table.getCellValue(counter,5) == "---" or table.getCellValue(counter,5) == "X"):
               table.setCellValue(counter,5,"---")
            #else:
               #table.setCellValue(counter,5,"---")
            
        table.adjustCells()
        self.maskEvent = False        

        row = widgetItem.row()
        col = widgetItem.column()

        text = widgetItem.text()
        flag = 0


        if text == "Use":
            newText = "---"
        elif text == "---":
            newText = "Use"
        elif text == "X":
            newText = "X"

        else:
            flag = 1

        if flag == 0:

            table = Util_Table.tableWidget(self.tableWidget)
            table.setCellValue(row, col, newText)
            self.updateDictMatrixes() 

            checkbox_flag = False
            for row in range(self.tableWidget.rowCount()):
                if table.getCellValue(row,3) == "Use" or table.getCellValue(row,4) == "Use":
                    checkbox_flag = True
            logging.debug("checkbox_flag is")
            logging.debug(checkbox_flag)
            self.toggle_check(checkbox_flag)




    def toggle_check(self,checkbox_flag):

        if other_flag == False:        
            self.default_tree.maskEvent = True
        else:
            self.other_tree.maskEvent = True

        if other_flag == False:        
            select_item = self.default_tree.tree_widget.selectedItems()[0]
        else:
            select_item = self.other_tree.tree_widget.selectedItems()[0]

        if other_flag == False:        
            Index = self.default_tree.tree_widget.indexOfTopLevelItem(select_item)   
            item = self.default_tree.tree_widget.topLevelItem(Index)
        else:
            Index = self.other_tree.tree_widget.indexOfTopLevelItem(select_item)   
            item = self.other_tree.tree_widget.topLevelItem(Index)

        logging.debug("toggle2")
        logging.debug(item.checkState(0))
        
        if checkbox_flag == True:
            item.setCheckState(0,Qt.Checked)
            logging.debug("checked")
        else:
            item.setCheckState(0,Qt.Unchecked)
            logging.debug("unchecked") 
        #mask解除
        if other_flag == False:
            self.default_tree.maskEvent = False
        else:
            self.other_tree.maskEvent = False

    def enterSignalFromEditor(self):
        """ cellに組み込まれたtextEditorが終了した時の処理。
        編集後のtextをcellに挿入し、editorを閉じる"""
        #編集itemを取得
        item = self.Table.currentItem()
        self.Table.closePersistentEditor(item)
        index = self.Table.indexFromItem(item)
        #編集したtextを取得
        newText = self.Table.newText
        #textをitemに設定
        if newText != None:


            row = index.row()
            col = index.column()
            
            if (col==1) or (col==2 and (diy_is_num(newText))):
                Util_Table.tableWidget(self.tableWidget).setCellValue(row, col, newText)
                self.updateDictMatrixes()
            else:
                pass
            
        #newTextをクリア
        self.Table.newText = None


    def onfile_enumClick(self):
        logging.debug("file select")
        select_item = self.default_tree.tree_widget.selectedItems()[0]

        global other_flag
        other_flag = False

        logging.debug(select_item)
        #絶対パスと相対パスの切り替え箇所１
        #mapfile = postDir + "/" + filenamegroup[self.default_tree.tree_widget.indexOfTopLevelItem(select_item)]
        mapfile = filenamegroup[self.default_tree.tree_widget.indexOfTopLevelItem(select_item)]

        self.loadDir = mapfile        
        self.label_loadDir.setText("loadFile: " + self.loadDir)       


        pathname = mapfile.split("/")        
        use_pathname = pathname[-1]


        for i in range(len(pathname)-1):
            #The filename_maximum length defined by right value 
            if len(pathname[-i-2]) + len(use_pathname) < 30:
                use_pathname = pathname[-i-2] + "_" + use_pathname

        self.lineEdit_filename.setText(use_pathname)
        logging.debug(mapfile)

        print(mapfile)
        if mapfile in Use_checkedfile_Matrixes:
            logging.debug("mapfile exists")
            self.setEditedMatrixData(mapfile)
        else:
            self.setDefaultMatrix(mapfile )                
        #logging.debug( self.default_tree.tree_widget.indexOfTopLevelItem(select_item))


    def onfile_enumClick_other(self):
        #print("otherfile select")
        logging.debug("file select")
        select_item = self.other_tree.tree_widget.selectedItems()[0]

        global other_flag
        other_flag = True

        logging.debug(select_item)
        #絶対パスと相対パスの切り替え箇所１
        #mapfile = postDir + "/" + filenamegroup[self.default_tree.tree_widget.indexOfTopLevelItem(select_item)]
        #print("seconde")
        mapfile = filenamegroup_other[self.other_tree.tree_widget.indexOfTopLevelItem(select_item)]
        
        self.loadDir = mapfile        
        self.label_loadDir.setText("loadDir: " + self.loadDir)       


        pathname = mapfile.split("/")        
        use_pathname = pathname[-1]
        for i in range(len(pathname)-1):
            #The filename_maximum length defined by right value
            if len(pathname[-i-2]) + len(use_pathname) < 30:
                use_pathname = pathname[-i-2] + "_" + use_pathname

        self.lineEdit_filename.setText(use_pathname)
                
        logging.debug(mapfile)
        #print("third")

        if mapfile in Use_checkedfile_Matrixes_other:
            print("mapfile exists")
            self.setEditedMatrixData(mapfile)
        else:
            print("try opening other file")
            self.setDefaultMatrix(mapfile )                
        #logging.debug( self.default_tree.tree_widget.indexOfTopLevelItem(select_item))




    def actionOnExitButton(self):
        self.close()


    def combobox_update(self):
        global dplt_system
        dplt_system = []
        for postfolder, subpostfolders, postfiles in os.walk(learnDir + "/system"):
            for postfile in postfiles:
                if postfile[-4:] == "dplt" and postfile[0] != ".":
                    dplt_system.append(postfile)
        dplt_system.sort()

        self.typeComboBox.clear()
        self.typeComboBox.addItems(dplt_system)


    def actionOnConfirmFileButton(self):
        select_item = self.default_tree.tree_widget.selectedItems()[0]
        mapfile = filenamegroup[self.default_tree.tree_widget.indexOfTopLevelItem(select_item)]
        comm = "gedit " + learnDir +"/postProcessing/" + mapfile  + " &"

        env = QtCore.QProcessEnvironment.systemEnvironment()
        if env.contains("APPIMAGE"):
            dexcsCfdTools.removeAppimageEnvironment(env)
            process = QtCore.QProcess()
            process.setProcessEnvironment(env)
            process.setProgram("gnome-text-editor")
            process.setArguments({learnDir +"/postProcessing/" + mapfile})
            process.startDetached()

        else:
            os.system(comm)

    def actionOnAddFileButton(self):

        gettingDir = os.getcwd()
        filename = getFileNamesDialog(gettingDir).show()

        global filenamegroup_other

        if filename in filenamegroup_other:
            print("Select file already loaded")
            return
            
        p_abs = pathlib.Path(filename[0])
        #p_abs = pathlib.Path('/home/caeuser/projects/airplane_8param/div2_11111111/postProcessing/forces')
        #print(p_abs)

        startDir = pathlib.Path(postDir)
        #print(postDir)
        #print(startDir)
        #filenamegroup_other.append(p_abs.relative_to(startDir) )

        rel_filename = (os.path.relpath(filename[0],postDir) )
        filenamegroup_other.append(rel_filename )

        #logging.debug(filename)
        print(rel_filename)
        
        self.other_tree.maskEvent = True

        #filename = "Test"
        temp_item = QTreeWidgetItem()
            
        #temp_item.setData(0, Qt.CheckStateRole, Qt.Checked)
        #temp_item.setData(0, Qt.CheckStateRole, False )
        temp_item.setData(0, Qt.CheckStateRole, Qt.Unchecked)
            
        #temp_item.setText(0, str(filename[0]))
        temp_item.setText(0, rel_filename)
                       
        self.other_tree.tree_widget.addTopLevelItem(temp_item)
        temp_item.setExpanded(True)

        
        #select_item = self.default_tree.tree_widget.selectedItems()[0]
        #Index = self.default_tree.tree_widget.indexOfTopLevelItem(select_item)   
        #item = self.default_tree.tree_widget.topLevelItem(Index)
        
        #if checkbox_flag == True:
            #item.setCheckState(0,Qt.Checked)
            #logging.debug("checked")
        #else:
            #item.setCheckState(0,Qt.Unchecked)
            #logging.debug("unchecked") 
        #mask解除
        
        self.other_tree.maskEvent = False


    def actionOnDeleteFileButton(self):
        print("not yet impl")


    def actionOnPlotButton(self):
        #fileName = learnDir + '/system/' + "current.dplt"
        MAX_COUNT = 16
        
        for i in range(MAX_COUNT):
            tempname = ".temp" + str(i)
            tempname_extent = learnDir + "/system/" + tempname + ".dplt" 
            
            Entry_flag = False                
            try:
                if os.path.isfile(tempname_extent):
                    os.remove(tempname_extent)
                Entry_flag = True
            except:
                pass
            if Entry_flag == True:
                break

        
        rel_fileName = self.Save_dplt(tempname)
        
        #rel_fileName = self.Save_dplt("temp_")

        logging.debug("save success")
        logging.debug(rel_fileName)
        #fileName = learnDir + '/system/' + self.typeComboBox2.currentText()
        #abs_fileName = learnDir + '/system/' + rel_fileName

        if os.path.exists(rel_fileName):
            f = open(rel_fileName,"r")
            lines = f.readlines()
            f.close()
            logging.debug("postProcessing=",f.name)
            dexcsPlotPost.dexcsPlotPost(learnDir,lines)
            print("[dexcsPlotTable]: Plot excuted")

        #dexcs_plot(block)
        
    #################### Data type (1) X_Data : List of String (2) Y_Data : Double list of String ####################

    def dexcs_plot(lines):

        X_File=[]
        X_column=[]
        X_scaleFactor=[]
        Y_File=[]
        Y_column=[]
        Y_scaleFactor=[]
        Y_Legend=[]
        Y_Vector=[]

        for line in lines:
            split = line.split()
            try:
                if split[0] != "#" :
                    if split[0] == "Title":
                        Title = split[1]
                    if split[0] == "Y.Label":
                        Y_Label = split[1]
                    if split[0] == "X.File":
                        X_File.append( modelDir + "/postProcessing/" + split[1] )  
                    if split[0] == "X.column":
                        X_column.append(int(split[1])) 
                    if split[0] == "X.scaleFactor":
                        X_scaleFactor.append( float(split[1]))
                    if split[0] == "X.Label":
                        X_Label = split[1]
                    if split[0] == "Y.File":
                        Y_File.append( modelDir + "/postProcessing/" + split[1])
                    if split[0] == "Y.column":
                        Y_column.append(int(split[1]))
                    if split[0] == "Y.scaleFactor":
                        Y_scaleFactor.append(float(split[1]))
                    if split[0] == "Y.Legend":
                        Y_Legend.append(split[1])
                    if split[0] == "Y.Vector":
                        Y_Vector.append(split[1])
            except:
                pass

        postPlot = PostPlot()
        PostsX=[]
        PostsY={}

        for k in range(len(Y_File)) :
            postX = process_column_X(X_File[k], X_column[k], X_scaleFactor[k])
            PostsX.append(postX)
            if Y_Vector[k] == "1":
                PlotValue = process_column_vector(Y_File[k], Y_column[k], Y_scaleFactor[k])
            else:
                PlotValue = process_column(Y_File[k], Y_column[k], Y_scaleFactor[k])
            PostsY[Y_Legend[k]] = PlotValue
            k = k + 1

        NewPostX=[]
        for k in range(len(Y_File)) :
            for i in range(len(PostsX[k])):
                NewPostX.append(PostsX[k][i])
        NewPostX = list(set(NewPostX))
        NewPostX.sort()

        for k in range(len(Y_File)) :
            iIns = 0
            preFound = 0
            for j in range(len(NewPostX)):
                found = 0
                imin = -1
                for i in range(len(PostsX[k])):
                    if PostsX[k][i] == NewPostX[j]:
                        found = 1
                        preFound = 0
                        break
                    if PostsX[k][i] < NewPostX[j] :
                        imin = i
                if found == 0: 
                    iL = imin 
                    iH = iL + 1
                    try:
                        ratio = (NewPostX[j]-PostsX[k][iL])/(PostsX[k][iH]-PostsX[k][iL])
                    except:
                        ratio = 1
                    if iL < 0 :
                        insY = None
                    elif iH > len(PostsX[k])-1 :
                        insY = None
                    else:
                        insY = PostsY[Y_Legend[k]][iL+iIns-preFound] + (PostsY[Y_Legend[k]][iH+iIns]-PostsY[Y_Legend[k]][iL+iIns-preFound])*ratio

                    PostsY[Y_Legend[k]].insert(j,insY)
                    preFound = preFound + 1
                    iIns = iIns + 1

        postPlot.updatePosts(Title, Y_Label, X_Label, NewPostX, PostsY)
        postPlot.updated = True
        postPlot.refresh()


    def actionOnSaveButton(self):
        self.Save_dplt("")
        print("[dexcsPlotTable]: dplt file was saved")
        
    def Save_dplt(self, filename):
        MAX_COUNT=256
        X_name =""
        Y_names = []
        Y_keys = []
        
        X_Data = []
        Y_Datas = []
        X_index = ""
        Y_indexs = []

        X_mul = ""
        Y_muls = []
        Y_vectors = []

        X_file_index = 0
        Y_file_indexs = []

        File_X_rep_name = {}        
        #File_X_rep_column = {}
        X_rep_index = {}
        X_rep_mul = {}
        
        logging.debug("plot data output")

        #title = u"save filename"
        #mess = u"Please enter save-file name (without extension)"
        #(stat, inputText) = inputDialog(title, mess)
        #if stat == "OK":
            #filename = inputText
        #else:
            #filename = "blank"
        
        #sorted_Use_checkedfile_Matrixes = sorted(Use_checkedfile_Matrixes.items(), key=lambda x:x[0])
        #filename = self.lineEdit_filename.text()
        United_Use_checkedfile_Matrixes = Use_checkedfile_Matrixes
        United_Use_checkedfile_Matrixes.update(Use_checkedfile_Matrixes_other)


        #for file_key,file_cont in Use_checkedfile_Matrixes.items():
        for file_key,file_cont in United_Use_checkedfile_Matrixes.items():
            for row_count,row_data in enumerate(file_cont):


                #各特性値のテーブル各行データの抽出。column_headerの並びを変える際はこちらも変える必要あり
                index_f = row_data[0]
                name = row_data[1]
                mul =  row_data[2]
                X_Flag = row_data[3]
                Y_Flag =  row_data[4]
                Z_Flag =  row_data[5]
                vector = ""
                tempname = ""
                
                #vectorは---は"0"、Useは"1"に切替"
                if row_data[5]=="Use":
                    vector =  "1"
                else:
                    vector = "0"

                logging.debug("row_count is")
                logging.debug(len(file_cont))
                logging.debug("Use jud")
                logging.debug(row_data)
                 
                if X_Flag=="Use" or row_count==0:
                #if X_Flag=="Use":
                    #X_name=name
                    #X_mul = mul
                    #X_index = index_f
                    #File_X_rep_column = index_f
                    X_rep_index[file_key] = index_f
                    X_rep_mul[file_key] = mul
                    if X_Flag=="Use":
                        X_name = name

                if Z_Flag=="Use":
                    tempname = name
                    for i in range(MAX_COUNT):
                    
                        if not tempname in Y_names:
                            logging.debug("unique filename")
                            break
                        else:
                            tempname= name +"_" + str(i+1)
                    logging.debug("name decide")
                        
                    Y_names.append(name[:-2]+"_"+ "abs")
                    Y_keys.append(file_key)
                    #Y_Datas.append(data_columns[row_count])
                    Y_muls.append(mul)
                    Y_vectors.append("1")
                    Y_indexs.append(index_f)

                
                if Y_Flag=="Use":
                    tempname = name
                    for i in range(MAX_COUNT):
                    
                        if not tempname in Y_names:
                            logging.debug("unique filename")
                            break
                        else:
                            tempname= name +"_" + str(i+1)
                    logging.debug("name decide")
                        
                    Y_names.append(tempname)
                    Y_keys.append(file_key)
                    #Y_Datas.append(data_columns[row_count])
                    Y_muls.append(mul)
#                    Y_vectors.append(vector)
                    Y_vectors.append("0")
                    Y_indexs.append(index_f)
                    #Y_file_indexs.append(row)
 
            logging.debug("Use jud fin")
                
        logging.debug("X_name")
        logging.debug(X_name)
        #logging.debug("X_Data")
        #logging.debug(X_Data)
        logging.debug("Y_name")
        logging.debug(Y_names)
        #logging.debug("Y_Data")
        #logging.debug(Y_Datas)

        #for i in range(5):
            #if not os.path.exists(learnDir + "/current" + str(i) + ".dplt"):
                #f = open(learnDir + "/current" + str(i) + ".dplt","w")
                #break

        if filename=="":
            filename = self.lineEdit_filename.text()                
        
        Title_Chart = self.lineEdit_title.text()

        #X_Label_Chart =  self.lineEdit_label.text()

        Y_Label_Chart =  self.lineEdit_Ylabel.text()

        filename_extent = filename + ".dplt"

        if filename_extent in dplt_system:
            #multi_lang
            title = _(u"上書き許可")
            mess = _(u"既に同名のファイルがありますが上書きしますか？")
            (stat, inputText) = inputTextDialog(title, mess).show()
            if stat == "OK":
                pass
            else:
                return



        #f = open(learnDir + "/system/current.dplt","w")
        f = open(learnDir + "/system/" + filename + ".dplt","w")
        #f = open(filename + ".dplt","w")

        logging.debug("write process start")

        block=""

        block = block + "#header \n"
        block = block + "Title " + Title_Chart +"\n"
        block = block + "X.Label " + X_name + "\n"
        block = block + "Y.Label " + Y_Label_Chart  + "\n"
        block = block + "\n"

        #f.write(block)

        logging.debug("write XY process start")

        for i in range(len(Y_names)):
            #block = ""
            #block = block + "X.File " +  filenamegroup[useindex_checked_postProcessisng_files[X_file_index]]   +"\n"
            #block = block + "X.File " +  table.getRowLabelValue(X_file_index)   +"\n"
            #block = block + "X.File " + str( File_X_rep[table.getRowLabelValue(Y_file_indexs[i])] )   +"\n"
            #block = block + "X.File " +  table.getRowLabelValue(Y_file_indexs[i])   +"\n"
            block = block + "X.File " +  Y_keys[i]   +"\n"

            #block = block + "X.column " + X_index + "\n"
            #block = block + "X.column " + str( File_X_rep_column[table.getRowLabelValue(Y_file_indexs[i])] ) + "\n"
            #block = block + "X.column " + str( File_X_rep_column ) + "\n"
            
            #block = block + "X.column " + X_rep_index[Y_keys[i]] + "\n"
            block = block + "X.column " + X_rep_index.get(Y_keys[i]) + "\n"
            
            #block = block + "X.scaleFactor " + X_mul + "\n"
            block = block + "X.scaleFactor " + X_rep_mul.get(Y_keys[i]) + "\n"
            block = block + "\n"
            #f.write(block)

            #block = ""
            #block = block + "Y.File " +  filenamegroup[useindex_checked_postProcessisng_files[Y_file_indexs[i]]]  +"\n"
            block = block + "Y.File " +  Y_keys[i]   +"\n"
            block = block + "Y.column " + Y_indexs[i] + "\n"
            block = block + "Y.scaleFactor " + Y_muls[i] + "\n"
            block = block + "Y.Legend " + Y_names[i] + "\n"
            block = block + "Y.Vector " + Y_vectors[i] + "\n"

            block = block + "\n"
            #f.write(block)

        logging.debug("write complete")
             
        f.write(block)
        f.close()

        #plotボタンやsaveボタンでsystem下のdpltが増えたら下関数でコンボボックスの中身を更新
        self.combobox_update()


        return(learnDir + "/system/" + filename + ".dplt")

        #今後、各ファイルの辞書データを保存(ロードして再表示)させる際に下記を活用
        #with open(learnDir + "/system/" + filename + ".tbcfg","w") as f2:               
            #for row in range(self.tableWidget.rowCount()):
                #temp_row = table.getRowLabelValue(row)
                #for i in range(7):
                    #temp_row = temp_row + " " + table.getCellValue( row, i)
                #temp_row = temp_row + "\n"
                #f2.write(temp_row)


    def actionOnLookAsTextButton(self):
        fileName = learnDir + '/system/' + self.typeComboBox.currentText()

        if os.path.exists(fileName):
            comm = "gedit " + fileName + " &"
            env = QtCore.QProcessEnvironment.systemEnvironment()
            if env.contains("APPIMAGE"):
                dexcsCfdTools.removeAppimageEnvironment(env)
                process = QtCore.QProcess()
                process.setProcessEnvironment(env)
                process.setProgram("gnome-text-editor")
                process.setArguments({fileName})
                process.startDetached()

            else:
                os.system(comm)
            #os.system(comm)
            #f = open(fileName,"r")
            #lines = f.readlines()
            #f.close()
            #logging.debug("postProcessing=",f.name)
            #dexcsPlotPost.dexcsPlotPost(learnDir,lines)
            #print("[dexcsPlotTable]: Load dplt file excuted")
        else:
            print("file not exist")

    def actionOnLoadButton(self):
        fileName = learnDir + '/system/' + self.typeComboBox.currentText()

        if os.path.exists(fileName):
            f = open(fileName,"r")
            lines = f.readlines()
            f.close()
            logging.debug("postProcessing=",f.name)
            dexcsPlotPost.dexcsPlotPost(learnDir,lines)
            print("[dexcsPlotTable]: Load dplt file excuted")

    def actionOnLoad2Button(self):
        logging.debug("test")
        self.updateDictMatrixes()
        for item in Use_checkedfile_Matrixes.values():
            logging.debug("Cash of Matrixes")
            logging.debug(item)
        for item in Use_checkedfile_rowLabels.values():
            logging.debug("Cash of Matrixes")
            logging.debug(item)            
        
    def actionOnreserveButton(self):

        #dir_path = QFileDialog.getExistingDirectory(self.Ui_MainWindow,'select .tbcfg file', learnDir)
        #dir_path = QFileDialog.getExistingDirectory(self,'select .tbcfg file', learnDir)
       
        gettingDir = os.getcwd()
        files = getFileNamesDialog(gettingDir).show()
        logging.debug(files)
       
        
        (stat, inputText) = inputTextDialog("test","test").show()
        if stat == "OK":
            Title_Chart = inputText
        else:
            Title_Chart = "blank"
        logging.debug(Title_Chart)
        
        #filename = QFileDialog.getOpenFileName(self,"select .tbcfg file", learnDir)
        #logging.debug(filename)
        #logging.debug(dir_path)
        
        #dialog  = myFileDialog(self,"test","test")
        #if dialog().show():
            #logging.debug("dialog")
        #logging.debug("finish")
        #dialog = QFileDialog(self, "Select Directory")
        #dialog.setLabelText(QFileDialog.FileName, "Directory name:")
        #dialog.setLabelText(QFileDialog.Accept, "Open")
        #dialog.setFileMode(QFileDialog.Directory)
        #dialog.setAcceptMode(QFileDialog.AcceptOpen)
        #dialog.setOptions(QFileDialog.ShowDirsOnly)
        
        #path = ""
        
        #if dialog.exec_():
            #r = dialog.selectedFiles()
            #path = r[0]
            #logging.debug(path)






    def inherit_file(self,filename, startDir):
        words = startDir.split("/")
        for i in range(len(words)):
            #name = words[len(words)-i-1]
            # ancestorDir = "/".join(words[:len(words)-i-1])
            ancestorDir = "/".join(words[:len(words)-i])

            folderDirs = glob.glob(ancestorDir + "/*")

            for item in folderDirs:
                if item == ancestorDir +"/" + filename:
                    shutil.copy(ancestorDir + "/" + filename, startDir )
                    logging.debug("found inherit-file")
                    return
        logging.debug("not found inherit-file")
        return
        
            
    def setDefaultMatrix(self,mapfile ):
    

        rowLabels = []
        colData = []
        colData1 = []


        global table_contents
        global data_columns
        table_contents = []        
        data_columns = []
        useindex_checked_postProcessisng_files = []

        temp_data_columns = []

        datum = []

        mapfiles = []
        mapfiles.append(mapfile)

        #for h,name in enumerate(checked_postProcessisng_files):
        print(mapfile)
        for h,name in enumerate(mapfiles):        
            fileunit_data_columns = []
            #Dir__Name = postDir + "/" + name
            Dir__Name = name
            
            
            logging.debug(Dir__Name)
            #絶対パスと相対パスの切り替え箇所２
            tempf = open(os.path.normpath(postDir + "/" + name))
            #tempf = open(postDir + "/" + name)
            
            #tempf = open(name)
            cont_page = tempf.read().splitlines()            
            tempf.close()
            
            datum = []
            #rowLabels.append("")
            SingleCharFile_Flg=0                    
                                    
            logging.debug("read success")



                    #C/M for SingleCharFile



            if name[-3:] != ".xy":
                Probe_Flag = 0
                Read_Stage = 0
                for line in cont_page:
                #logging.debug(line)
                    if Read_Stage == 0:
                        if "Probe" in line:
                            Probe_Flag = 1
                        if 'Time' in line:
                            Read_Stage = 2
                            listlized = line.split()
                            for i,item in enumerate(listlized):
                                if i !=0:
                                    if item[0]=="(":
                                        item=item[1:]
                                    if item[-1]==")":
                                        if not '(' in item:
                                            item=item[:-1]
                                    if item[:8]!="location":
                                          
                                        datum.append(item)
                                    else:
                                        datum.append(item+"_x")
                                        datum.append(item+"_y")
                                        datum.append(item+"_z")                        
                                #rowLabels.append(name)                                
                                
                                #colData = []
                                #colData.append(item)
                                #colData.append("1.0")
                                #colData.append("---")
                                #colData.append("---")
                                
                                #colData1.append(colData)
                            logging.debug("datum")        
                            logging.debug(datum)

                    elif Read_Stage==2:
                        data_row =[]
                        listlized = line.split()
                        num_vector = 0
                        num_column = 0
                        for i,item in enumerate(listlized):
                            if item[0]=="(":
                                item=item[1:]
                                num_vector += 1
                            if item[-1]==")":
                                item=item[:-1]
                            data_row.append(item)
                            num_column += 1
                        fileunit_data_columns.append(data_row)
                        if Probe_Flag == 1:
                            if num_vector !=0:
                                if num_vector ==1:
                                    datum.append(os.path.basename(name)+"_x")
                                    datum.append(os.path.basename(name)+"_y")
                                    datum.append(os.path.basename(name)+"_z")
                                else:
                                    #print(num_vector)
                                    for ind in range(num_vector):
                                        datum.append(os.path.basename(name)+"_"+str(ind)+"_x")
                                        datum.append(os.path.basename(name)+"_"+str(ind)+"_y")
                                        datum.append(os.path.basename(name)+"_"+str(ind)+"_z")
                            else:
                                if num_column == 2:
                                    datum.append(os.path.basename(name))
                                else:
                                    for ind in range(num_column-1):
                                        datum.append(os.path.basename(name)+"_"+str(ind))                                                        
                            Probe_Flag =0
                    #elif Read_Stage==2 and Probe_Flag =0:
                                                
                    else:
                        pass

            else:
                #datum=[]

                for line in cont_page:
                    data_row=[]
                    listlized = line.split()
                    for i,item in enumerate(listlized):
                        if item[0]=="(":
                            item=item[1:]
                        if item[-1]==")":
                            item=item[:-1]
                        data_row.append(item)
                    fileunit_data_columns.append(data_row)

                    
            for i in range(len(data_row)):
                useindex_checked_postProcessisng_files.append(h)
                logging.debug("data_row length is")
                logging.debug(len(data_row))
                colData = []
                #idの番号付与
                colData.append(str(i))
                #デフォルトのname付与
                if i < len(datum):
                    colData.append(datum[i])
                else:
                    colData.append("unknown")
                    
                #行データについて、デフォルト値を与える。カラム番号以外は一定値。column_headerを変える場合はこちらも変える必要あり
                #colData.append("unknown")
                colData.append("1")    
                colData.append("---")
                colData.append("---")
                try:
                    if datum[i][-2:]=="_x":
                        colData.append("---")
                    else:
                        colData.append("X")
                except:
                    colData.append("X")

                #colData.append("")
                colData1.append(colData)

                #rowLabels.append(name)
                rowLabels.append(" ")
                                    
            fileunit_data_columns = ([list(x) for x in zip(*fileunit_data_columns)])

            for i in range(len(colData1)):
                colData1[i].append(str(len(fileunit_data_columns[0])))

            for elem in fileunit_data_columns:                                                       
                data_columns.append(elem)

            logging.debug("data_columns")
            logging.debug(data_columns)

         
        self.maskEvent = True
        table = Util_Table.tableWidget(self.tableWidget)

        table.createTable(rowLabels,column_header)
        

        for row in range(len(rowLabels)):
            for col in range(len(column_header)):
                table.setCellValue(row, col, colData1[row][col] )                
        table.adjustCells()
        self.maskEvent = False

    
    def createMatrix(self):
        """ 行、列名を設定"""
        self.maskEvent = True
        table = Util_Table.tableWidget(self.tableWidget)
        table.createTable(self.rowLabels, column_header)
        for col in range(table.tableWidget.columnCount()):
            table.setCellColor_yellow(0, col)
         
        #table.tableWidget.horizontalHeaderItem(0).setToolTip("column index in file")
        #table.tableWidget.horizontalHeaderItem(1).setToolTip("column name or your edit")
        #table.tableWidget.horizontalHeaderItem(2).setToolTip("scale factor")
        #table.tableWidget.horizontalHeaderItem(3).setToolTip("Used as X element")
        #table.tableWidget.horizontalHeaderItem(4).setToolTip("Used as Y element(multi-adaptable")
        #table.tableWidget.horizontalHeaderItem(5).setToolTip("apply vector(Y axis)")
        #table.tableWidget.horizontalHeaderItem(6).setToolTip("number of data length")
        
        self.maskEvent = False

    #
    #  setMatrixData
    #-----------------
    def setMatrixData(self):
        """ cellにデータを設定"""
        self.maskEvent = True
        table = Util_Table.tableWidget(self.tableWidget)
        for row in range(self.tableWidget.rowCount()):
            for col in range(self.tableWidget.columnCount()):
                value = str(self.rowColVals[row][col])
                table.setCellValue(row, col, value)
        table.adjustCells()
        self.maskEvent = False


    def setEditedMatrixData(self,mapfile):
        """ cellにデータを設定""" 

        if other_flag == False:
            EditedMatrix = Use_checkedfile_Matrixes[mapfile]
            rowLabels = Use_checkedfile_rowLabels[mapfile]
        else:
            EditedMatrix = Use_checkedfile_Matrixes_other[mapfile]
            rowLabels = Use_checkedfile_rowLabels_other[mapfile]
        
        
        logging.debug("call prev")
        logging.debug(EditedMatrix)

        self.maskEvent = True
        table = Util_Table.tableWidget(self.tableWidget)
        table.createTable(rowLabels,column_header)
        
        #for row in range(len(rowLabels)):
        for row in range(len(EditedMatrix)):
            for col in range(len(column_header)):
                value = EditedMatrix[row][col]
                table.setCellValue(row, col, value)                
        table.adjustCells()
        self.maskEvent = False



    def updateDictMatrixes(self):
        """ cellにデータを設定"""
        global Use_checkedfile_Matrixes
        global Use_checkedfile_rowLabels
        global Use_checkedfile_Matrixes_other
        global Use_checkedfile_rowLabels_other        
        
        temp_lists =[]
        rowLabels =[]        

        table = Util_Table.tableWidget(self.tableWidget)
        for row in range(self.tableWidget.rowCount()):
            #rowLabels.append(table.getRowLabelValue(row))
            rowLabels.append(" ")
            temp_row = []
            for col in range(self.tableWidget.columnCount()):
                value = str(table.getCellValue(row,col))
                temp_row.append(value)
            temp_lists.append(temp_row)    

        if other_flag == False:
            select_item = self.default_tree.tree_widget.selectedItems()[0]
        else:
            select_item = self.other_tree.tree_widget.selectedItems()[0]
        
        #絶対パスと相対パスの切り替え箇所３
        #filepath = postDir + "/" + filenamegroup[self.default_tree.tree_widget.indexOfTopLevelItem(select_item)] 
        if other_flag==False:
            filepath = filenamegroup[self.default_tree.tree_widget.indexOfTopLevelItem(select_item)]
        else:
            filepath = filenamegroup_other[self.other_tree.tree_widget.indexOfTopLevelItem(select_item)]

        print(filepath)        
        #filepath = postDir + "/" + filenamegroup[0]
        logging.debug("matrix for loop success") 
        if other_flag == False:
            Use_checkedfile_rowLabels[filepath] = rowLabels              
            Use_checkedfile_Matrixes[filepath] = temp_lists
        else:
            Use_checkedfile_rowLabels_other[filepath] = rowLabels              
            Use_checkedfile_Matrixes_other[filepath] = temp_lists
        
        
        logging.debug("get matrix finished")

    def setMatrixData2(self):
        logging.debug("no func")

    def setMatrixData3(self):
        logging.debug("no func")

    def setLogText(self, line):
        """ lineをtextEditに表示する"""
        self.textEdit_log.append(line)

    def okDialog(self, title, mess):
        msgBox = QMessageBox()
        msgBox.information(QDialog(), title, mess, msgBox.Ok)

    def errDialog(self, title, mess):
        msgBox = QMessageBox()
        msgBox.critical(QDialog(), title, mess, msgBox.Ok)


def showGui(learnDir,dpltDir):

    #rowLabels = ["blank"]
    rowLabels = []
    rowLabels.append("blank")
    
    
    #保存テーブルのロードとして実装したが現状未使用。ただ辞書データロードに際に活用できる
    #tbcfgDir = dpltDir[:-5] + ".tbcfg"
    #if os.path.exists(tbcfgDir):
        #logging.debug("dplt cfg exists")   
        #tempf = open(tbcfgDir)
        #cont_page = tempf.read().splitlines()            
        #tempf.close()

        #for line in cont_page:
            #listlized = line.split()
            #if len(listlized)==8:
                #rowLabels.append(listlized[0])
                #colData2.append(listlized[1:])
        #if rowLabels==[]:
            #logging.debug("failt to read tbcfg file")
            #rowLabels.append("empty")
            #colData2.append([""] * 7)
    #else:
        #rowLabels.append("blank")
        #colData2.append([""]*7)


    #if os.path.exists(dpltDir):
        #logging.debug("dplt exists")   
        #tempf = open(dpltDir)
        #cont_page = tempf.read().splitlines()            
        #tempf.close()
            
        #datum = []
        #Read_State =0

        #current_file = ""
        #file_change_flag = False
        #table_row = [""] * 7
                                                                    
        #logging.debug("read success")
            
        #Read_Stage = 0
        #table_row = [""] * 7
        #for line in cont_page:
            #listlized = line.split()            
            #if Read_Stage == 0 and len(listlized) >=2:
                
                #if listlized[0]=="X.Label":
                    #X_name = listlized[1]
                    #Read_Stage = 1

            #elif Read_Stage == 1 and len(listlized) >=2:                           
                #if listlized[0] == "X.File":
                    #temp_file = listlized[1]
                    #if current_file != temp_file:
                        #current_file = temp_file
                        #file_change_flag = True
                        
                #if file_change_flag == True:

                    #if listlized[0] == "X.column":
                        #table_row[5] = listlized[1]
                    #elif listlized[0] == "X.scaleFactor":
                        #table_row[0] = X_name
                        #table_row[1] = listlized[1]
                        #table_row[2] = "Use"
                        #table_row[3] = "---"                            
                        #table_row[4] = "0"
                        #table_row[6] = "-"
                        #colData2.append(table_row)
                        #table_row = [""] * 7
                        #rowLabels.append(current_file)
                        #file_change_flag =False
                        #logging.debug("one X block up")
                        
                    #else:
                        #pass

                #if listlized[0] == "Y.File":
                    #rowLabels.append(listlized[1])
                #elif listlized[0] == "Y.column":
                    #table_row[5] = listlized[1]
                #elif listlized[0] == "Y.scaleFactor":
                    #table_row[1] = listlized[1]
                #elif listlized[0] == "Y.Legend":
                    #table_row[0] = listlized[1]
                #elif listlized[0] == "Y.Vector":
                    #table_row[4] = listlized[1]
                    #table_row[2] = "---"
                    #table_row[3] = "Use"
                    #table_row[6] = "-"
                    #colData2.append(table_row)
                    #table_row = [""] * 7
                    #logging.debug("one X block up")
                #else:
                    #pass
            #else:
                #pass        
    #else:
        #rowLabels.append("blank")
        #colData2.append([""]*7)

    logging.debug(len(rowLabels),len(column_header))


    pre_rowColVals = []    
    pre_rowColVals.append(colData2)

    ui = gridTable(rowLabels, pre_rowColVals)
    ui.main()
    
    ui.MainWindow.show
    

    if not QApplication.instance():
        app = QApplication(sys.argv)
        logging.debug("with argument")
    else:
        app = QApplication.instance()
        logging.debug("no argument")
    

if __name__ == "__main__":
#    learnDir = sys.argv[1]
#    dpltDir = sys.argv[2]
#    platformDir = learnDir

#    if os.path.exists("case_pathinfo"):
    if 1==0:
        logging.debug("dplt cfg exists")   
        main_tempf = open("case_pathinfo")
        main_cont_page = main_tempf.read().splitlines()            
        main_tempf.close()

        for main_i,main_line in enumerate(main_cont_page):
            main_listlized = main_line.split()
            if main_i == 0 and main_listlized!=[]:
                learnDir = main_listlized[0]
            if main_i == 1 and main_listlized!=[]:
                dpltDir = main_listlized[0]

    else:

        optionOutputPath = dexcsCfdTools.getOptionOutputPath()

        if optionOutputPath:
            learnDir = dexcsFunctions.getCaseFileName()
        else:
            learnDir = '.'           

        dpltDir = learnDir + "/system/current.dplt"
        print('dpltDir = ',dpltDir)

        platformDir = learnDir    


    init_loadDir = learnDir
    logging.debug(learnDir)

    filenamegroup = []

    postDir = learnDir + "/postProcessing"
    
    for postfolder, subpostfolders, postfiles in os.walk(postDir):
        for postfile in postfiles:
            if postfile[-3:] != "vtk":
                temp_relative_path = os.path.relpath(postfolder, postDir )
                filenamegroup.append(temp_relative_path + "/" + postfile)
    filenamegroup.sort()  
    namegroup = []
    namegroup = os.listdir(postDir)
    namegroup.sort()    
    logging.debug(namegroup)

    dplt_system = []
    for postfolder, subpostfolders, postfiles in os.walk(learnDir + "/system"):
        for postfile in postfiles:
            if postfile[-4:] == "dplt" and postfile[0] != ".":
                dplt_system.append(postfile)
    dplt_system.sort()


    filenamegroup_other = []


    rowLabels = []
    rowLabels.append("blank")

    colData2 = []
    colData2.append([""]*7)

    logging.debug(len(rowLabels),len(column_header))


    pre_rowColVals = []    
    pre_rowColVals.append(colData2)

    #pre_rowColVals =[["0","unknown","1","---","---","---","unknown" ]]
    pre_rowColVals =[["0","unknown","1","---","---","X","unknown" ]]

    ui = gridTable(rowLabels, pre_rowColVals)
    ui.main()
    
   
    if not QApplication.instance():
        app = QApplication(sys.argv)
        logging.debug("with argument")
    else:
        app = QApplication.instance()
        logging.debug("no argument")
    
    # rowLabels = ["score", "param1", "param2", "param3", ""]
    # colLabels = ["score", "sub1", "sub2", "sub3", ""]
    # rowColVals = [[1, 2, 3, 4, ""],
    #               [11, 22, 33, 44, ""],
    #               [22, 23, 24, 25, ""],
    #               [33, 34, 35, 36, ""],
    #               [44, 45, 46, 47, ""]]
    # showGui(rowLabels, colLabels, rowColVals)
