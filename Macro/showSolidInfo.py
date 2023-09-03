# -*- coding: utf-8 -*-
#import FreeCADGui

import pythonVerCheck

def showSolidInfo():
  # 選択されている形状を取得
  selections = FreeCADGui.Selection.getSelection()
  if len(selections)==0:
    # 選択されている形状なし
    return
  if 1<len(selections):
    # 複数の形状が選択されている
    return

  object_label = selections[0].Label
  message = _("object name ") + object_label + "\n"

  shape = selections[0].Shape
  num_solids = len(shape.Solids)
  count = 0
  message += _("No. of solid ") + str(num_solids)+ "\n"
  for s in shape.Solids:
    message += _(" solid No.    : ") + str(count) + "\n"
    message += _(" surface area : ") + str(s.Area) + "\n"
    message += _(" volumes      : ") + str(s.Volume) + "\n"
    message += _("weight center : \n")
    message += _("            X : ") + str(s.CenterOfMass[0]) + "\n"
    message += _("            Y : ") + str(s.CenterOfMass[1]) + "\n"
    message += _("            Z : ") + str(s.CenterOfMass[2]) + "\n"
    count+=1

  import PySide
  from PySide import QtGui
  diag = QtGui.QMessageBox(\
    QtGui.QMessageBox.Information,\
    u"オブジェクト情報",\
    message)
  diag.exec_()

showSolidInfo()
