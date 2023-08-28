#!/usr/bin/python3
#  coding:  utf-8
#
#   gridEditor.py
#
#       gridEditorを起動する
#
#       使い方
#       gridEditor.py <caseDir> <timeFolder> <polyMeshFolder>
#       例：gridEditor.py ~/cavity 0 constant/polyMesh
#
#   11/08/11    新規作成
#   12/01/21    バグ修正
#   12/03/25    起動時に読み込むfieldを設定
#   13/04/19    fieldが無い場合でも起動するように修正
#      05/24    timeFolder取得方法を変更
#      10/15    国際化のため、修正
#   20/06/12    python3用に書き換え
#

import os
import sys
import pyTreeFoam


nTreeFoam = "-1"        #ここから起動するgridEditorのnTreeFoamは「-1」

def showDialog():
    comm = "openGridEditorDialog.py " + nTreeFoam + " " + caseDir + " &"
    pyTreeFoam.run(caseDir).command(comm)


if __name__ == "__main__":
    caseDir = sys.argv[1]           #caseDir
    caseDir = os.path.abspath(caseDir)
    showDialog()
