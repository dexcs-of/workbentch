# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dexcsPlotTool.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

import pythonVerCheck

class Ui_DexcsPlotTool(object):
    def setupUi(self, DexcsPlotTool):
        DexcsPlotTool.setObjectName("DexcsPlotTool")
        DexcsPlotTool.resize(400, 287)
        self.plot_Button = QtWidgets.QPushButton(DexcsPlotTool)
        self.plot_Button.setGeometry(QtCore.QRect(300, 40, 89, 25))
        self.plot_Button.setObjectName("plot_Button")
        self.edit_Button = QtWidgets.QPushButton(DexcsPlotTool)
        self.edit_Button.setGeometry(QtCore.QRect(300, 70, 89, 25))
        self.edit_Button.setObjectName("edit_Button")
        self.listView = QtWidgets.QListView(DexcsPlotTool)
        self.listView.setGeometry(QtCore.QRect(30, 40, 261, 201))
        self.listView.setObjectName("listView")
        self.label = QtWidgets.QLabel(DexcsPlotTool)
        self.label.setGeometry(QtCore.QRect(40, 10, 161, 16))
        self.label.setObjectName("label")
        self.cancel_Button = QtWidgets.QPushButton(DexcsPlotTool)
        self.cancel_Button.setGeometry(QtCore.QRect(300, 250, 89, 25))
        self.cancel_Button.setObjectName("cancel_Button")
        self.new_Button = QtWidgets.QPushButton(DexcsPlotTool)
        self.new_Button.setGeometry(QtCore.QRect(30, 250, 89, 25))
        self.new_Button.setObjectName("new_Button")

        self.retranslateUi(DexcsPlotTool)
        self.plot_Button.clicked.connect(DexcsPlotTool.run_plot)
        self.cancel_Button.clicked.connect(DexcsPlotTool.run_cancel)
        self.edit_Button.clicked.connect(DexcsPlotTool.run_edit)
        self.new_Button.clicked.connect(DexcsPlotTool.run_new)
        QtCore.QMetaObject.connectSlotsByName(DexcsPlotTool)

    def retranslateUi(self, DexcsPlotTool):
        _translate = QtCore.QCoreApplication.translate
        DexcsPlotTool.setWindowTitle(_translate("DexcsPlotTool", _("Dexcs Plot Tool")))
        self.plot_Button.setText(_translate("DexcsPlotTool", _("Plot")))
        self.edit_Button.setText(_translate("DexcsPlotTool", _("Edit")))
        self.label.setText(_translate("DexcsPlotTool", _("Select .dplt File")))
        self.cancel_Button.setText(_translate("DexcsPlotTool", _("Cancel")))
        self.new_Button.setText(_translate("DexcsPlotTool", _("New")))
