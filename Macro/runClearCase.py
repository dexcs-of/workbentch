# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import sys
import glob
import re
#import gi
import PySide
from PySide import QtGui

import pythonVerCheck

import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

os.chdir(modelDir)

def isTime(name):
    try:
        a=float(name)
        flag = True
    except:
        flag = False
    return flag

#
#  getTimeFolders
#    caseDir内のtimeFolderを取得
def getTimeFolders(caseDir):
    dirs = glob.glob(caseDir + "/*")
    folders = []
    for folder in dirs:
        folders.append(folder.split("/")[-1])
    time=[]
    for name in folders:
        try:
            a=float(name)
            time.append([a, name])
        except:
            a=0
    time.sort()
    timeFolders=[]
    for name in time:
        timeFolders.append(name[1])
    return timeFolders

#
#  getFoldersFiles
#    dir内のfolder名とfile名を返す（名前のみ返す。pathではない）
#    戻り値：[[folders],[files]]
def getFoldersFiles(wdir):      #wdirは、絶対path
    folders = []
    files = []
    dirFiles = glob.glob(wdir + "/*")
    for name in dirFiles:
        if os.path.isdir(name) == True:
            folders.append(name.split("/")[-1])
        elif os.path.isfile(name) == True:
            files.append(name.split("/")[-1])
    folders.sort()
    files.sort()
    return [folders, files]

#
#  selectNeedFolders
#    folderを要・不要に分ける
#    timeFolderの場合は、minTimeのみ要、それ以外を不要
def selectNeedFolders(names):
    unneedFolders = ["processor.*", ".*\.log.*", "log\..*", "postPro*"]
    [unmatchNames, unneed] = selectNeedNames(unneedFolders, names)
    numFolders = []
    need = []
    for name in unmatchNames:
        try:
            a = float(name)
            numFolders.append([a, name])
        except:
            need.append(name)
    if len(numFolders) > 0:
        numFolders.sort()
        need.append(numFolders[0][1])
        i = 1
        while i<len(numFolders):
            [a, name] = numFolders[i]
            unneed.append(name)
            i += 1
    return [need, unneed]

#
#  selectNeedFiles
#    fileを要、不要に分ける
def selectNeedFiles(names):
    unneedFiles = ["log\..*|.*\.log", ".*~",
        ".*\.bak|.*\.png|.*\.obj|.*\.jpg|.*\.OpenFOAM|.*\.foam|.*\.blockMesh",
        #"test.*|.*test", "run|plotWatcher", "Allrun.*|Allclean.*|README.*",
        "test.*|.*test", "plotWatcher", "README.*",
        ".*\.ods|.*\.odt|.\*.odp|.*\.csv", "job*"]
    return selectNeedNames(unneedFiles, names)
#  selectNeedNames
def selectNeedNames(unneedNames, names):

    def isMatch(name):
        flag = False
        for pattern in unneedNames:
            if isMatchName(name, pattern) == True:
                flag = True
                break
        return flag

    need = []
    unneed = []
    for name in names:
        if isMatch(name) == True:
            unneed.append(name)
        else:
            need.append(name)
    return [need, unneed]

#
#  isMatchName
#    nameがpatternと一致するかどうかをチェック
#    一致：Trueが戻る
def isMatchName(name, pattern):
    if pattern[0] == '"':
        pattern = pattern[1:-1]
    ans = False
    obj = re.match(pattern, name)   #正規表現でチェック
    if obj != None:
        ans = True
    return ans

def okDialog(self, title, message):
#    dlg = wx.MessageDialog(self, message, title,
#                            style = wx.OK | wx.ICON_INFORMATION) 
#    dlg.ShowModal()
#    dlg.Destroy()
  diag = QtGui.QMessageBox(\
    QtGui.QMessageBox.Information,\
    title,\
    message,QtGui.QMessageBox.Yes)
  diag.exec_()

#  okCancelDialog
#
#def okCancelDialog(self, title, mess):
def okCancelDialog(parent, title, mess):
    """ okCancel dialog表示"""

    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(mess)
    msgBox.setStandardButtons(QtGui.QMessageBox.Ok  | QtGui.QMessageBox.Cancel)
    res = msgBox.exec_()

    if res == QtGui.QMessageBox.Ok:
        stat = "OK"
    else:
        stat = "CANCEL"
    return stat

def deleteFolder(delDir):
    mess = ""
    try:
        #ファイルをゴミ箱へ移動
        obj = gio.File(delDir.encode("utf-8"))
        obj.trash()
        #shutil.rmtree(delDir)
    except:
        mess = _("'") + delDir + _("' was not able to delete.  continue ?")
        #print mess
    return mess

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):


    solveCaseFix = modelDir
    #singleCore計算時の処理
    timeFolders = getTimeFolders(solveCaseFix)
    ans = ""
    ansFlag = 0
    [folders, files] = getFoldersFiles(solveCaseFix)
    [need, unneed] = selectNeedFiles(files)
    [needFolders, unneedFolders] = selectNeedFolders(folders)
    #削除対象のfileがあるか
    if len(timeFolders) > 1 or len(unneed) > 0 or len(unneedFolders) > 0:
        title = _("initialize of case")
        msg = _("result folders and unneeded files are deleted, case is initialized.")
        ans = okCancelDialog(None,title, msg)
        #print("ans="+ans)
        if ans == "OK":
            # if selCaseDirFix != solveCaseFix:
            #     msg = _(u"解析caseと選択しているcaseが異なっています。\n　解析caseを初期化しますか？")
            #     ans = okCancelDialog(None,title, msg)
            #     if ans == "OK":
            #         ansFlag = 1
            # else:
            ansFlag = 1
            if ansFlag == 1:
                #不要なfolderをゴミ箱へ（processor, timeFolderは削除）
                for name in unneedFolders:
                    #if name[:9] == "processor" or isTime(name) == True:
                        comm = "rm -rf " + solveCaseFix + "/" + name
                        os.system(comm)
                    #else:
                    #    delName = solveCaseFix + "/" + name
                    #    deleteFolder(delName)
                #不要なfileをゴミ箱へ（削除しない）
                for name in unneed:
                    delName = solveCaseFix + "/" + name
                    deleteFolder(delName)
                mess = _("case were initialized.")
                #print (mess)
                okDialog(None,title, mess)
else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.OK)

