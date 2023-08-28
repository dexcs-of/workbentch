# -*- coding: utf-8 -*-
 
# Qt for Python のクラスを使えるようにする
import FreeCAD
from FreeCAD import Gui
import Mesh
import os
import PySide
from PySide import QtGui
import pythonVerCheck

import tempfile
import dexcsFunctions


# 自作ダイアログクラス
class MyFirstDialog(QtGui.QDialog):
        # ウィンドウの初期化処理
        def __init__(self, parent=None):
                # ベース・クラスの初期化
                super(MyFirstDialog, self).__init__(parent)
               
                # ウィンドウタイトルを設定
                self.setWindowTitle(_("Get FSI parameter Diaog"))

                # 
                [young, poison] = dexcsFunctions.get_model(caseDir,modelName,solverInp)
               
                # レイアウトを使ってラベル、エディットボックス、ボタンを配置
                myLabel1 = QtGui.QLabel(_("patch name"))
                self.myLineEdit1 = QtGui.QLineEdit("flap")
                myLabel2 = QtGui.QLabel(_("scalingFactor to meter"))
                self.myLineEdit2 = QtGui.QLineEdit("0.001")
                myLabel3 = QtGui.QLabel(_("Young's Modulus (MPa)"))
                #self.myLineEdit3 = QtGui.QLineEdit("1")
                self.myLineEdit3 = QtGui.QLineEdit(young)
                myLabel4 = QtGui.QLabel(_("Poison ratio"))
                #self.myLineEdit4 = QtGui.QLineEdit("0.3")
                self.myLineEdit4 = QtGui.QLineEdit(poison)
                myLabel5 = QtGui.QLabel(_("Density (kg/m3)"))
                self.myLineEdit5 = QtGui.QLineEdit("3000")
                myLabel6 = QtGui.QLabel(_("deltaTime"))
                self.myLineEdit6 = QtGui.QLineEdit("0.01")
                myLabel7 = QtGui.QLabel(_("output Frequency"))
                self.myLineEdit7 = QtGui.QLineEdit("10")
                myLabel8 = QtGui.QLabel(_("finalTime"))
                self.myLineEdit8 = QtGui.QLineEdit("20")
                myButton = QtGui.QPushButton(_("make inpFile for FSI"))
               
                # ボタンが押された時の処理を設定
                myButton.clicked.connect(self.myButtonClicked)
               
                # 縦方向レイアウトを使ってラベル、エディットボックス、ボタンを配置
                layout = QtGui.QVBoxLayout()
                layout.addWidget(myLabel1)
                layout.addWidget(self.myLineEdit1)
                layout.addWidget(myLabel2)
                layout.addWidget(self.myLineEdit2)
                layout.addWidget(myLabel3)
                layout.addWidget(self.myLineEdit3)
                layout.addWidget(myLabel4)
                layout.addWidget(self.myLineEdit4)
                layout.addWidget(myLabel5)
                layout.addWidget(self.myLineEdit5)
                layout.addWidget(myLabel6)
                layout.addWidget(self.myLineEdit6)
                layout.addWidget(myLabel7)
                layout.addWidget(self.myLineEdit7)
                layout.addWidget(myLabel8)
                layout.addWidget(self.myLineEdit8)
                layout.addWidget(myButton)
                self.setLayout(layout)
       
        # ボタンが押された時の処理
        def myButtonClicked(self):
                # メッセージボックスを表示
                solidName = self.myLineEdit1.text()
                scale_factor = self.myLineEdit2.text()
                young = self.myLineEdit3.text()
                poison = self.myLineEdit4.text()
                density = self.myLineEdit5.text()
                dT = self.myLineEdit6.text()
                prt_frq = self.myLineEdit7.text()
                finalTime = self.myLineEdit8.text()
                dexcsFunctions.convertInpFile(caseDir,modelName,solverInp,scale_factor,solidName,young,poison,density,dT,prt_frq,finalTime)
                mes = solidName+".inp has been created."
                QtGui.QMessageBox.information(self, "Message", mes)
                ui.close()

class MySecondDialog(QtGui.QDialog):
        # ウィンドウの初期化処理
        def __init__(self, parent=None):
                # ベース・クラスの初期化
                super(MySecondDialog, self).__init__(parent)
               
                # ウィンドウタイトルを設定
                self.setWindowTitle(_("Get FSI parameter Diaog"))

                # 
                [young, poison] = dexcsFunctions.get_model(caseDir,modelName,solverInp)
               
                # レイアウトを使ってラベル、エディットボックス、ボタンを配置
                myLabel1 = QtGui.QLabel(_("patch name"))
                self.myLineEdit1 = QtGui.QLineEdit("flap")
                myLabel2 = QtGui.QLabel(_("scalingFactor to meter"))
                self.myLineEdit2 = QtGui.QLineEdit("0.001")
                myLabel3 = QtGui.QLabel(_("Young's Modulus (MPa)"))
                #self.myLineEdit3 = QtGui.QLineEdit("1")
                self.myLineEdit3 = QtGui.QLineEdit(young)
                myLabel4 = QtGui.QLabel(_("Poison ratio"))
                #self.myLineEdit4 = QtGui.QLineEdit("0.3")
                self.myLineEdit4 = QtGui.QLineEdit(poison)
                myLabel5 = QtGui.QLabel(_("Density (kg/m3)"))
                self.myLineEdit5 = QtGui.QLineEdit("3000")
                myLabel6 = QtGui.QLabel(_("deltaTime"))
                self.myLineEdit6 = QtGui.QLineEdit("0.01")
                myLabel7 = QtGui.QLabel(_("output Frequency"))
                self.myLineEdit7 = QtGui.QLineEdit("10")
                myLabel8 = QtGui.QLabel(_("finalTime"))
                self.myLineEdit8 = QtGui.QLineEdit("20")
                myButton = QtGui.QPushButton(_("make inpFile for FSI"))
               
                # ボタンが押された時の処理を設定
                myButton.clicked.connect(self.myButtonClicked)
               
                # 縦方向レイアウトを使ってラベル、エディットボックス、ボタンを配置
                layout = QtGui.QVBoxLayout()
                layout.addWidget(myLabel1)
                layout.addWidget(self.myLineEdit1)
                layout.addWidget(myLabel2)
                layout.addWidget(self.myLineEdit2)
                layout.addWidget(myLabel3)
                layout.addWidget(self.myLineEdit3)
                layout.addWidget(myLabel4)
                layout.addWidget(self.myLineEdit4)
                layout.addWidget(myLabel5)
                layout.addWidget(self.myLineEdit5)
                layout.addWidget(myLabel6)
                layout.addWidget(self.myLineEdit6)
                layout.addWidget(myLabel7)
                layout.addWidget(self.myLineEdit7)
                layout.addWidget(myLabel8)
                layout.addWidget(self.myLineEdit8)
                layout.addWidget(myButton)
                self.setLayout(layout)
       
        # ボタンが押された時の処理
        def myButtonClicked(self):
                # メッセージボックスを表示
                solidName = self.myLineEdit1.text()
                scale_factor = self.myLineEdit2.text()
                young = self.myLineEdit3.text()
                poison = self.myLineEdit4.text()
                density = self.myLineEdit5.text()
                dT = self.myLineEdit6.text()
                prt_frq = self.myLineEdit7.text()
                finalTime = self.myLineEdit8.text()
                dexcsFunctions.convertPrPInpFile(caseDir,modelName,solverInp,scale_factor,solidName,young,poison,density,dT,prt_frq,finalTime)
                mes = solidName+".inp has been created."
                QtGui.QMessageBox.information(self, "Message", mes)
                ui.close()

if __name__ == '__main__':

        import sys

        if sys.version_info.major == 3:
        	import PySide2
        	if isinstance(PySide2.QtGui.qApp, type(None)):
        	    app = PySide2.QtWidgets.QApplication([])
        	else:
        	    app = PySide2.QtGui.qApp
        else:
        	import PySide
        	if isinstance(PySide.QtGui.qApp, type(None)):
        	    app = PySide.QtWidgets.QApplication([])
        	else:
        	    app = PySide.QtGui.qApp

        doc = App.ActiveDocument
        modelName = os.path.basename(doc.FileName)
        modelName = os.path.splitext(modelName)[0]
        caseDir = os.path.dirname(doc.FileName)
        #print(modelName)
        #print(caseDir)

        try:
        
            set = Gui.Selection.getSelection()[0]

            if "Solver" in set.Name:
                inpDir = os.path.join(caseDir,modelName,set.Name)

                #print(inpDir)

                if os.listdir(inpDir):
                    for inpFile in os.listdir(inpDir):
                        if ".inp" in inpFile:

                            solverInp = set.Name + '/' + inpFile
                            #print(solverInp)

                            ui = MyFirstDialog()
                            ui.show()
           
                            app.exec_()
                else:
                    mes = ".inp file dosen't exist"
                    QtGui.QMessageBox.information(None,"Message", mes)
             
            else:
                #mes = "Select SolverCCxTools...container." 
                ### PrePoMax でエクスポートした.inp を読み込む

                (fileName, selectedFilter) = QtGui.QFileDialog.getOpenFileName( None, _("Select a CalculiX .inp file"), caseDir )
                path1, solverInp = os.path.split(fileName)
                caseDir, modelName = os.path.split(path1)

        except IndexError:    
                (fileName, selectedFilter) = QtGui.QFileDialog.getOpenFileName( None, _("Select a CalculiX .inp file"), caseDir )
                path1, solverInp = os.path.split(fileName)
                caseDir, modelName = os.path.split(path1)

        ui = MySecondDialog()
        ui.show()           
        app.exec_()
