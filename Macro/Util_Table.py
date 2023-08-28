#!/usr/bin/python3
#  coding: utf-8
#


"""
Qt4Parts.py
Copyright (C) 2020 Shigeki Fujii, Tsunehiro Watanabe all rights reserved.

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
"""


""" Qt4のGuiPartの操作関連をまとめたもの。

Parts:
    QTreeWidget:
    QListView:
    QTableWidget:
"""

#from PyQt4 import QtCore, QtGui
#from PySide import QtCore, QtGui
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


#------------------------- QTreeWidget関連 ----------------------------
#  treeWidget class
#-------------------
class treeWidget:
    """ 
    QTreeWidgetの設定、操作関連
    使い方
        ・辞書を準備
        ・createTree(headers)でtreeのformatを作成
        ・createTreeData(dataDict)でtreeDataを作成
        ・setItems()でtreeDataと辞書からtreeWidgetが完成
    """
    def __init__(self, treeWidget):
        self.treeWidget = treeWidget
        self.dataDict = {}              #辞書
        self.treeData = []              #dirを変換

    #
    #  createTree
    def createTree(self, headers):
        """ treeのcol数を設定し、各colのheaderを設定する。
        
        Args:
            headers (list(str)) :各列のheader名をlist形式で与える"""
        nCols = len(headers)
        self.treeWidget.setColumnCount(nCols)
        for col in range(nCols):
            header = headers[col]
            self.treeWidget.headerItem().setText(col, header)
    
    #
    #  createTreeData
    def createTreeData(self, dataDict):
        """ dataDictからtreeDataを作成する。
        ここで、クラス属性のdataDict, treeDataを作成する。
        辞書データには、treeで表示するdirectoryのiconを含む。
        
        Args:
            dataDict (dict) :tree作成用の辞書
                            :{<dir>: [icon, [0, 1]]} 
                            : dir名   icon   col内容のlist"""
        folderDirs = list(dataDict.keys())
        folderDirs.sort()
        rootDir = folderDirs[0]
        treeData = [rootDir, []]
        folders = []
        for folder in folderDirs[1:]:
            words = [rootDir] + folder[len(rootDir)+1:].split("/")
            folders.append(words)
        for folderWords in folders:
            treeData = self.setTreeDataFolder(0, treeData, folderWords)
        self.dataDict = dataDict
        self.treeData = treeData

    def setTreeDataFolder(self, nest, tree, folder):
        """ folderをtree状に作成する"""
        nest += 1
        if nest > 50:
            print("error: folder nesting is too deep!")
            return
        #親folderまでskipする
        parentDir = folder[nest]
        ii = 0
        while ii < len(tree[1]):
            if type(tree[1][ii]) == list:
                if tree[1][ii][0] == parentDir:
                    self.setTreeDataFolder(nest, tree[1][ii], folder)
                    break
            else:
                if tree[1][ii] == parentDir:
                    tree[1][ii] = [parentDir, []]
                    self.setTreeDataFolder(nest, tree[1][ii], folder)
                    break
            ii += 1
        #親folderの位置ならchildを追加する
        if nest == len(folder) - 1:
            child = folder[-1]
            tree[1].append(child)
        return tree

    #
    #  setItems
    def setItems(self):
        """ treeDataを使ってtreeWidgetのitemをセットする
        
        Args:
            None"""
        treeData = self.treeData
        dataDict = self.dataDict
        rootName = treeData[0]
        items = treeData[1]
        [icon, colConts] = dataDict[rootName]
        parentItem = QTreeWidgetItem(self.treeWidget)
        parentItem.setText(0, rootName)
        parentItem.setIcon(0, icon)
        self.setColConts(parentItem, colConts)
        self.addTreeNodes(parentItem, [rootName], items)

    #
    #  setItemCont
    def setItemCont(self, item, colConts):
        """ 指定したitemにcolContsを設定する。
        
        Args:
            item (QTreeWidgetItem)  :colContsをセットするitem
            colConts (list(str))    :セットする内容"""
        self.setColConts(item, colConts)

    #
    #  addTreeNodes
    def addTreeNodes(self, parentItem, parentDir, items):
        """ parentItem以下のTreeItemをitems（treeData）から作成する。
        
        Args:
            parentItem (QTreeWidgetItem)    :親item
            parentDir (str)                 :親のdir
            items (list(treeData))          :dirをtreeDataに変換したitem"""
        for item in items:
            if type(item) == str:
                itemDir = parentDir + [item]
                [icon, colConts] = self.dataDict["/".join(itemDir)]
                child = QTreeWidgetItem(parentItem)
                child.setIcon(0, icon)
                child.setText(0, item)
                self.setColConts(child, colConts)
            else:
                itemDir = parentDir + [item[0]]
                [icon, colConts] = self.dataDict["/".join(itemDir)]
                child = QTreeWidgetItem(parentItem)
                child.setText(0, item[0])
                child.setIcon(0, icon)
                self.setColConts(child, colConts)
                self.addTreeNodes(child, itemDir, item[1])

    def setColConts(self, item, colConts):
        """ item中にcol内容をセットする"""
        col = 1
        for i in range(len(colConts)):
            value = colConts[i]
            if type(value) == str:
                item.setText(col, value)
                col += 1
            elif type(value) == int or type(value) == float:
                item.setText(col, str(value))
                col += 1
            else:
                item.setIcon(col, value)


    #
    #  selectDir
    def selectDir(self, selDir):
        """ selDirまで展開し、scrollして、selDirを選択表示する。
        
        Args:
            selDir (str)    :選択するdir"""
        #selDirのitemを取得
        selItem = self.getItemFromDir(selDir)
        #selItemまで展開
        self.expandToItem(selItem)
        #selItemを選択
        self.treeWidget.setItemSelected(selItem, True)
        #selItemまでscroll
        self.treeWidget.scrollToItem(selItem, QAbstractItemView.PositionAtCenter)

    #
    #  selectItem
    def selectItem(self, selItem):
        """ selItemまで展開し、scrollして、selItemを選択表示する。
        
        Args:
            selItem (QTreeWidgetItem)   :選択するitem"""
        #selItemまで展開
        self.expandToItem(selItem)
        #selItemを選択
        self.treeWidget.setItemSelected(selItem, True)
        #selItemまでscroll
        self.treeWidget.scrollToItem(selItem, QAbstractItemView.PositionAtCenter)

    #
    #  getItemCont
    def getItemCont(self, item):
        """ 指定したitemのcol内容を取得する
        
        Args:
            item (QTreeWidgetItem)  :col内容を取得するitem
        Returns:
            colConts (list(str))    :col内容"""

        def convQstringToText(string):
            """ python2, 3で動作が異なるので、ここで修正。"""
            try:
                #python2の場合、変換する。
                string = string.toUtf8().data()
            except:
                #python3の場合、エラー発生。変換せず。
                pass
            return string

        nCols = item.columnCount()
        colConts = []
        for i in range(nCols):
            text = item.text(i)
            text = convQstringToText(text)
            colConts.append(text)
        return colConts

    #
    #  getItemFromDir
    def getItemFromDir(self, selDir):
        """ dirからitemを取得して返す
        
        Args:
            selDir (str)            :取得するdir
        Returns:
            item (QTreeWidgetItem)  :dirに対応するitem"""
        rootDir = self.treeData[0]
        folders = selDir[len(rootDir)+1:].split("/")
        parentItem = self.treeWidget.topLevelItem(0)
        for folder in folders:
            for idx in range(parentItem.childCount()):
                childItem = parentItem.child(idx)
                text = childItem.text(0)
                if text == folder:
                    break
            parentItem = childItem
        return parentItem

    #
    #  getDirFromItem
    def getDirFromItem(self, selItem):
        """ itemからdirを取得する。
        
        Args:
            selItem (QTreeWidgetItem)   :dirを取得するitem
        Returns:
            selDir (str)                :取得したdir"""

        def convQstringToText(string):
            """ python2, 3で動作が異なるので、ここで修正。"""
            try:
                #python2の場合、変換する。
                string = string.toUtf8().data()
            except:
                #python3の場合、エラー発生。変換せず。
                pass
            #PySide, PyQt4で異なるので、修正
            try:
                if type(string) == unicode:
                    string = string.encode("utf-8")
            except:
                pass
            return string

        words = []
        rootItem = self.treeWidget.topLevelItem(0)
        while selItem is not rootItem:
            text = selItem.text(0)
            text = convQstringToText(text)
            words = [text] + words
            selItem = selItem.parent()
        rootText = rootItem.text(0)
        rootText = convQstringToText(rootText)
        words = [rootText] + words
        selDir = "/".join(words)
        return selDir

    #
    #  expandToItem
    def expandToItem(self, selItem):
        """ rootからselItemまで展開する
        
        Args:
            selItem (QTreeWidgetItem)   :item"""
        #展開するitemを取得
        items = []
        rootItem = self.treeWidget.topLevelItem(0)
        #while selItem != rootItem:
        while selItem is not rootItem:
            selItem = selItem.parent()
            items = [selItem] + items
        items = [rootItem] + items
        #itemを展開
        for item in items:
            self.treeWidget.expandItem(item)

    #
    #  adjustColWidth
    def adjustColWidth(self):
        """ column幅をadjustする
        
        Args:
            None"""
        nCols = self.treeWidget.columnCount()
        for col in range(nCols):
            self.treeWidget.resizeColumnToContents(col)
        
    #
    #  deleteChildren
    def deleteChldren(self, item):
        """ 指定したitemの子itemを全て削除する。辞書も該当部を削除する。
        
        Args:
            item (QTreeWidgetItem)  :指定するitem"""
        #辞書から削除
        itemDir = self.getDirFromItem(item)
        folders = list(self.dataDict.keys())
        for folderDir in folders:
            if folderDir[:len(itemDir)+1] == itemDir + "/":
                dummy = self.dataDict.pop(folderDir)
        #treeWidgetから削除
        for _i in range(item.childCount()):
            delItem = item.child(0)
            item.removeChild(delItem)

    #
    #  getItemsFromTreeData
    def getItemsFromTreeData(self, selDir):
        """ dirをたどって、TreeDataの該当するitemsを取得する
        
        Args:
            selDir (str)            :指定するdir
        Returns:
            items (list(treeData))  :取得したtreeData内のitems"""
        
        def getTreeNodes(items, name):
            """ treeData内のitems内からnameが持っているitemsを取得する"""
            for item in items:
                newItems = ""
                if type(item) == str:
                    newItems = name
                else:
                    if item[0] == name:
                        newItems = item[1]
                        break
            return newItems

        rootDir = self.treeData[0]
        items = self.treeData[1]
        words = selDir[len(rootDir)+1:].split("/")
        for name in words:
            items = getTreeNodes(items, name)
        return items


#------------------------- QListView関連 ------------------------------
#  listView class
#------------------
class listView:
    """ ListViewの設定、操作関連"""

    def __init__(self, listView):
        self.listView = listView

    def setItems(self, items, multi=True):
        """ listViewを作成し、itemをセットする。
        
        Args:
            items (list(item))  :セットする項目
                                :itemがstrのみは、nameのみ表示。
                                :itemが[icon, str]の場合は、iconも表示。
            multi (bool)        :Trueは、multipleSelection"""
        if multi == True:
            self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        listModel = QStandardItemModel()
        self.listView.setModel(listModel)
        for itemCont in items:
            if (itemCont) == str:
                item = QStandardItem(itemCont)
            else:
                icon = itemCont[0]
                name = itemCont[1]
                item = QStandardItem(icon, name)
            listModel.appendRow(item)

    def getSelectedNames(self):
        """ listViewから選択行名（name）を取得する
        
        Returns:
            names (list(str))   :選択行名（name）"""
        idxes = self.listView.selectionModel().selectedRows()
        names = []
        for idx in idxes:
            row = idx.row()
            name = self.listView.model().item(row).text()
            names.append(name)
        return names

    def getSelectedIndexes(self):
        """ listViewから選択行のrowNoのlistを取得する。
        
        Returns:
            rows (list(int))    :選択行Noのlist"""
        idxes = self.listView.selectionModel().selectedRows()
        rows = []
        for idx in idxes:
            row = idx.row()
            rows.append(row)
        return rows
        
    def selectNames(self, selNames):
        """ listView内の指定されたitem名を選択する。
        
        Args:
            selNames (list(str))    :選択する項目名のlist"""
        listModel = self.listView.model()
        selection = self.listView.selectionModel()
        for row in range(listModel.rowCount()):
            text = listModel.item(row).text()
            if text in selNames:
                idx = listModel.item(row).index()
                selection.select(idx, QItemSelectionModel.Select)


#------------------------- QTableWidget関連 ---------------------------
#  tableWidget class
#---------------------
class tableWidget:
    """ tableWidgetの作成、操作関連"""

    def __init__(self, tableWidget):
        self.tableWidget = tableWidget

    #
    #  createTable
    #--------------
    def createTable(self, rowNames, colNames):
        """ row x col のtableを作成する。rowNames、colNamesをセット。"""
        self.tableWidget.setRowCount(len(rowNames))
        self.tableWidget.setColumnCount(len(colNames))
        #colラベル（title）を作成
        for col in range(len(colNames)):
            #label(name)を設定
            self.tableWidget.setHorizontalHeaderItem(col, QTableWidgetItem(colNames[col]))
            #水平,垂直方向のセンタリング
            self.tableWidget.horizontalHeaderItem(col).setTextAlignment(Qt.AlignCenter)
        #rowラベル（title）を作成
        for row in range(len(rowNames)):
            #label（name）を設定
            self.tableWidget.setVerticalHeaderItem(row, QTableWidgetItem(rowNames[row]))
            #水平垂直のセンタリング
            self.tableWidget.verticalHeaderItem(row).setTextAlignment(Qt.AlignCenter)
        #headerFontをboldに変更
        font = self.tableWidget.font()
        font.setBold(True)
        self.tableWidget.horizontalHeader().setFont(font)
        self.tableWidget.verticalHeader().setFont(font)
        #全cellに空白のQTableWidgetItemをセット
        for col in range(len(colNames)):
            for row in range(len(rowNames)):
                #空白をセット
                self.tableWidget.setItem(row, col, QTableWidgetItem(""))
                #cellの上詰めで配置（defaultは縦方向がセンタリング）
                self.tableWidget.item(row, col).setTextAlignment(Qt.AlignTop)
        #tableWidgetにtextEditorを設定
        #  引数としてtableWidgetを設定。
        #  editorがtableWidgetにアクセスできる様にする為
        delegate = Delegate(self.tableWidget)
        self.tableWidget.setItemDelegate(delegate)
        #cell幅をadjustする
        #self.tableWidget.resizeColumnsToContents()
        #self.tableWidget.resizeRowsToContents()
        # col = self.tableWidget.columnCount() - 1
        # for row in range(self.tableWidget.rowCount()):
        #     self.tableWidget.verticalHeader().setResizeMode(row, QHeaderView.ResizeToContents)


    #---------- label関係 --------------------
    #
    #  setLabelsFontColor_darkBlue
    def setLabelsFontColor_darkBlue(self):
        """ labelのfontColorをdarkBlue設定する"""
        for col in range(self.tableWidget.columnCount()):
            self.tableWidget.horizontalHeaderItem(col).setForeground(QColor(Qt.darkBlue))
        for row in range(self.tableWidget.rowCount()):
            self.tableWidget.verticalHeaderItem(row).setForeground(QColor(Qt.darkBlue))
    #
    #  getColLabelValue
    def getColLabelValue(self, col):
        """ columnのlabelの値を取得する"""
        return self.tableWidget.horizontalHeaderItem(col).text()
    #
    #  getColLabelValue
    def getRowLabelValue(self, row):
        """ rowのlabelの値を取得する"""
        return self.tableWidget.verticalHeaderItem(row).text()

    #-------- current select scrollCell copyPaste-------------
    #
    #  currentCell
    def currentCell(self):
        """ currentCellの（row, column）を返す。"""
        idx = self.tableWidget.currentIndex()
        return (idx.row(), idx.column())
    #
    #  scrollToCell
    def scrollToCell(self, row, col):
        """ cell(row, col)までscrollして表示する。"""
        item = self.tableWidget.item(row, col)
        self.tableWidget.scrollToItem(item,QAbstractItemView.PositionAtCenter)
    #
    #  selectedCells
    def selectedCells(self):
        """ 選択しているcellの(row, col)をtupleで戻す。"""
        items = self.tableWidget.selectedItems()
        rowCols = []
        for item in items:
            index = self.tableWidget.indexFromItem(item)
            rowCols.append((index.row(), index.column()))
        return rowCols

    #
    #  selectRow
    def selectRow(self, row):
        """ row行を選択する"""
        for col in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(row, col)
            self.tableWidget.setItemSelected(item, True)
    #
    #  selectCol
    def selectCol(self, col):
        """ col列を選択する"""
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, col)
            self.tableWidget.setItemSelected(item, True)
    #
    #  selectCell
    def selectCell(self, row, col):
        """ cell(row, col)を選択する"""
        item = self.tableWidget.item(row, col)
        self.tableWidget.setItemSelected(item, True)
    #
    #  unselectAll
    def unselectAll(self):
        """ 全cellを非選択状態に設定"""
        for row in range(self.tableWidget.rowCount()):
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, col)
                self.tableWidget.setItemSelected(item, False)

    #
    #  getCopyText
    def getCopyText(self):
        """ 選択項目をclipboardに渡す形式で取得し、戻す"""
        items = self.tableWidget.selectedIndexes()
        rowCols = []
        for item in items:
            row = item.row()
            col = item.column()
            rowCols.append([row, col])
        rowCols.sort()
        conts = []
        rowConts = []
        rowb = rowCols[0][0]
        for row, col in rowCols:
            cell = self.tableWidget.item(row, col).text()
            if row == rowb:
                rowConts.append('"' + cell + '"')
            else:
                conts.append(rowConts)
                rowConts = ['"' + cell + '"']
                rowb = row
        conts.append(rowConts)
        lines = []
        for rowConts in conts:
            lines.append("\t".join(rowConts))
        copyCont = "\n".join(lines)
        return copyCont
    #
    #  setPasteText
    def setPasteText(self, pasteText):
        """ pasteTextをtableに貼り付ける"""

        def getMultiLines(cont):
            """ pasteContを行listに変換する"""
            lines = []
            p = 0
            line = ""
            ps = 0
            while p < len(cont):
                chara = cont[p]
                if chara == '"':
                    p += 1
                    while p < len(cont) and cont[p] != '"':
                        p += 1
                    p += 1
                elif chara == "\n":
                    line = cont[ps:p]
                    lines.append(line)
                    while p < len(cont) and cont[p] == "\n":
                        p += 1
                    ps = p
                else:
                    p += 1
            if ps < len(cont):
                line = cont[ps:p]
                lines.append(line)
            return lines

        def pasteValsToCells(vals):
            """ 値をcellにセット"""
            #選択場所を取得
            firstSelection = []
            endSelection = []
            flag = 0
            row = 0
            while row < self.tableWidget.rowCount():
                col = 0
                while col < self.tableWidget.columnCount():
                    item = self.tableWidget.item(row, col)
                    if self.tableWidget.isItemSelected(item) == True:
                        if flag == 0:
                            firstSelection = [row, col]
                        endSelection = [row, col]
                        flag = 1
                    col += 1
                row += 1
            if len(firstSelection) == 0:
                (currRow, currCol) = self.tableWidget.currentIndex()
                endSelection = [currRow, currCol]
                firstSelection = [currRow, currCol]
            #paste開始
            #  1ヶ分をpaste
            selItems = []
            row = firstSelection[0]
            vRow = 0
            while vRow < len(vals):
                col = firstSelection[1]
                vCol = 0
                while vCol < len(vals[vRow]):
                    val = vals[vRow][vCol]
                    if row < self.tableWidget.rowCount() and col < self.tableWidget.columnCount():
                        item = self.tableWidget.item(row, col)
                        item.setText(val)
                        selItems.append(item)
                    col += 1
                    vCol += 1
                row += 1
                vRow += 1
            #  残りをpaste（row側）
            if row < endSelection[0] + 1:
                vRow = 0
                while row < endSelection[0] + 1:
                    col = firstSelection[1]
                    vCol = 0
                    while vCol < len(vals[vRow]):
                        if row < self.tableWidget.rowCount() and col < self.tableWidget.columnCount():
                            val = vals[vRow][vCol]
                            item = self.tableWidget.item(row, col)
                            item.setText(val)
                            selItems.append(item)
                        col += 1
                        vCol += 1
                    row += 1
                    vRow += 1
                    if vRow >= len(vals):
                        vRow = 0
                endPaste = [row, col]
            else:
                endPaste = [row, col]
            #  残りpaste（col側）
            if col < endSelection[1] + 1:
                vCol = 0
                col = endPaste[1]
                while col < endSelection[1] + 1:
                    row = firstSelection[0]
                    vRow = 0
                    while row < endPaste[0]:
                        if row < self.tableWidget.rowCount() and col < self.tableWidget.columnCount():
                            val = vals[vRow][vCol]
                            item = self.tableWidget.item(row, col)
                            item.setText(val)
                            selItems.append(item)
                        row += 1
                        vRow += 1
                        if vRow >= len(vals):
                            vRow = 0
                    col += 1
                    vCol += 1
                    if vCol >= len(vals[vRow]):
                        vCol = 0
            #pasteしたcellを選択表示
            for item in selItems:
                self.tableWidget.setItemSelected(item, True)

        #行を取得
        vals = getMultiLines(pasteText)
        if len(vals) == 0:
            return
        #1行毎に値を取得しlistを作成
        values = []
        for line in vals:
            row = line.split("\t")
            rows = []
            for val in row:
                #「"」マークの処理
                if len(val) == 0:
                    b = ""
                elif len(val) == 1:
                    b = val
                elif val[0] == '"':
                    b = val[1:-1]
                else:
                    b = val
                rows.append(b)
            values.append(rows)
        #値をgridにセット
        pasteValsToCells(values)

    #--------- cellの値を取得、設定 -----------------
    #
    #  getCellValue
    def getCellValue(self, row, col):
        """ 指定したcellの値を取得"""
        return self.tableWidget.item(row, col).text()
    #
    #  setCellValue
    def setCellValue(self, row, col, value):
        """ 指定したcellにvalue（text）をセットする"""
        #文字列をcellにセット
        self.tableWidget.item(row, col).setText(value)
    #
    #  adjustCells
    def adjustCells(self):
        """ 全cellの幅、高さを自動調整する。"""
        #textのwidth、heightを取得
        rowColWidth = []
        rowColHeight = []
        for row in range(self.tableWidget.rowCount()):
            colWidth = []; colHeight = []
            for col in range(self.tableWidget.columnCount()):
                text = self.tableWidget.item(row, col).text()
                width, height = self.getTextRect(text)
                colWidth.append(width)
                colHeight.append(height)
            rowColWidth.append(colWidth)
            rowColHeight.append(colHeight)
        #列幅を設定
        for col in range(self.tableWidget.columnCount()):
            rowWidth = list(map(lambda x: x[col], rowColWidth))
            maxWidth = max(rowWidth)
            #headerを確認
            header = self.tableWidget.horizontalHeaderItem(col).text()
            #  header幅は、余裕を持たせるため、空白2ヶをプラス
            width, height = self.getTextRect(header+"  ")
            #最大値を取得しセット
            maxWidth = max([maxWidth, width])
            self.tableWidget.setColumnWidth(col, maxWidth)
        #行高さを設定
        for row in range(self.tableWidget.rowCount()):
            colHeight = rowColHeight[row]
            maxHeight = max(colHeight)
            #headerを確認
            header = self.tableWidget.verticalHeaderItem(row).text()
            width, height = self.getTextRect(header)
            #最大値を取得しセット
            maxHeight = max([maxHeight, height])
            self.tableWidget.setRowHeight(row, maxHeight)
    #
    #  adjustCell
    def adjustCell(self, curRow, curCol):
        """ 特定cellの幅、高さを自動調整する。"""
        #curCol列の幅を確認、セット
        vals = []
        text = self.tableWidget.horizontalHeaderItem(curCol).text()
        width, height = self.getTextRect(text)
        vals.append(width)
        for row in range(self.tableWidget.rowCount()):
            text = self.tableWidget.item(row, curCol).text()
            #  header幅は、余裕を持たせるため、空白2ヶをプラス
            width, height = self.getTextRect(text+"  ")
            vals.append(width)
        self.tableWidget.setColumnWidth(curCol, max(vals))
        #curRow行の高さを確認、セット
        vals = []
        text = self.tableWidget.verticalHeaderItem(curRow).text()
        width, height = self.getTextRect(text)
        vals.append(height)
        for col in range(self.tableWidget.columnCount()):
            text = self.tableWidget.item(curRow, col).text()
            width, height = self.getTextRect(text)
            vals.append(height)
        self.tableWidget.setRowHeight(curRow, max(vals))
    #
    #  getTextRect
    def getTextRect(self, text):
        """ text（文字列）の幅、高さを計算し、戻す。"""
        #文字列のサイズ（whidth、height）を取得
        maxWidth, maxHeight = 1000, 1000                #最大サイズ
        #サイズを取得
        text += " "
        valRect = self.tableWidget.fontMetrics().boundingRect(
            QRect(0,0,maxWidth, maxHeight),      #maxRectSize
            Qt.AlignLeft | Qt.AlignTop,   #alignmentMethod
            text)                                       #text
        w = int(valRect.width() * 1.095 + 2)              #大きめの値をセット
        h = int(valRect.height() * 1.095 + 2)
        return w, h

    #-------- cellの背景色設定 ------
    #
    #  setCellColor_lightGreen
    def setCellColor_lightGreen(self, row, col):
        """ cell背景色をlightGreenに設定"""
        #self.tableWidget.item(row, col).setBackgroundColor(QColor(204, 255, 255))
        self.tableWidget.item(row, col).setBackground(QColor(230, 255, 255))
    #
    #  setCellColor_pink
    def setCellColor_pink(self, row, col):
        """ cell背景色をpinkに設定"""
        self.tableWidget.item(row, col).setBackground(QColor(247, 171, 166))
    #
    #  setCellColor_yellow
    def setCellColor_yellow(self, row, col):
        """ 指定したcellの背景色をyellowに設定する。"""
        self.tableWidget.item(row, col).setBackground(QColor(Qt.yellow))

    #------------ cellのfontColorを設定-------------------
    #
    #  setCellFontColor_blue
    def setCellFontColor_blue(self, row, col):
        """ 指定したcellのfonfColorをblueに設定する"""
        self.tableWidget.item(row, col).setForeground(QColor(Qt.blue))
    #
    #  setCellFontColor_brown
    def setCellFontColor_brown(self, row, col):
        """ 指定したcellのfonfColorをbrownに設定する"""
        self.tableWidget.item(row, col).setForeground(QColor(153, 76, 0))
    #
    #  setCellFontColor_darkGreen
    def setCellFontColor_darkGreen(self, row, col):
        """ 指定したcellのfonfColorをdarkGreenに設定する"""
        self.tableWidget.item(row, col).setForeground(QColor(Qt.darkGreen))
    #
    #  setCellFontColor_sysFontColor
    def setCellFontColor_sysFontColor(self, row, col):
        """ 指定したcellのfonfColorをsystemFontColor（黒）に設定する"""
        self.tableWidget.item(row, col).setForeground(QColor(Qt.black))


#------------------
#  Delegate class
#------------------
class Delegate(QStyledItemDelegate):
    """ QTableWidgetのeditorをにQTextEditに変更するために作成。
    親のQTableWidgetを引数として受け取り、editorに渡す。"""

    def __init__(self, parent=None):
        super(Delegate, self).__init__(parent)
        self.table = parent

    def createEditor(self, parent, option, index):
        """ editorをセットせずに戻る。"""
        #return
        #return QLineEdit(parent)
        #return QTextEdit(parent)
        value = self.table.item(index.row(), index.column()).text()
        if value[-3:] == "...":
            #signalを発信してeditorを起動しない
            self.table.largeTextSignal.emit()
            return
        return TextEditor(parent, self.table)
    
    def setEditorData(self, editor, index):
        #value = index.model().data(index, Qt.DisplayRole)
        #editor.setText(value)
        editor.setText(index.data())
        editor.selectAll() 
    
    def setModelData(self, editor, model, index):
        #model.setData(index, editor.text())
        model.setData(index, editor.toPlainText())


#---------------
#  Table class
#---------------
class Table(QTableWidget):
    """ eventを追加したQTableWidgetを作成。
    追加したeventは、keyPressEvent, keyReleaseEvent。"""

    CtrlFlag = 0                            #shiftKey pressing:1
    # copySignal = pyqtSignal()        #copyのsignal
    # pasteSignal = pyqtSignal()       #pasteのsignal
    # enterSignal = pyqtSignal()       #enterKeyのsignal
    # largeTextSignal = pyqtSignal()   #largetext(...)のsignal
    copySignal = Signal()        #copyのsignal
    pasteSignal = Signal()       #pasteのsignal
    enterSignal = Signal()       #enterKeyのsignal
    largeTextSignal = Signal()   #largetext(...)のsignal
    newText = None

    def mousePressEvent(self, event):
        #if event.type() == QEvent.MouseButtonPress:
        #    return
        return QTableWidget.mousePressEvent(self, event)
    
    #
    #  keyPressEvent
    #----------------
    def keyPressEvent(self, event):
        """ keyboardのevent取得と処理"""
        key = event.key()
        #enterKey?
        if self.CtrlFlag == 0 and (key == Qt.Key_Enter or key == Qt.Key_Return):
            #enterKeyの場合、eventを発生させない。
            self.enterSignal.emit()
            newEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
            return QTableWidget.keyPressEvent(self, newEvent)
        #deleteKey?
        elif self.CtrlFlag == 0 and key == Qt.Key_Delete:
            #deleteKeyの場合、cellをクリア
            #tableOperation(self).cellClear()
            indexes = self.selectedIndexes()
            for index in indexes:
                row = index.row()
                col = index.column()
                self.item(row, col).setText("")
        #controlKey?
        if key == Qt.Key_Control:
            #pressKey:ControlKeyの場合
            self.CtrlFlag = 1
        #pressing controlKey?
        elif self.CtrlFlag == 1:
            #Ctrl+C?
            if key == Qt.Key_C:
                #ctrl+Cの場合、signalを発信
                self.copySignal.emit()
            #Ctrl+V?
            elif key == Qt.Key_V:
                #ctrl+Vの場合、signalを発信
                self.pasteSignal.emit()
        #eventを返す
        return QTableWidget.keyPressEvent(self, event)

    #
    #  keyReleaseEvent
    #-----------------
    """ keyを離した時のevent。controlKeyをチェックする。"""
    def keyReleaseEvent(self, event):
        key = event.key()
        #controlKey?
        if key == Qt.Key_Control:
            #CtrlFlagをクリアする
            self.CtrlFlag = 0
        return QTableWidget.keyReleaseEvent(self, event)


#-------------------
#  TextEditor class
#-------------------
class TextEditor(QTextEdit):
    """ eventを追加したQTextEditを作成。
    追加したeventは、keyPressEvent, keyReleaseEvent。
    editorから親のtableWidgetにアクセスできる様に、引数を追加。"""

    def __init__(self, parent, table):
        super(TextEditor, self).__init__(parent)
        self.table = table              #tableWidget（親）
        self.table.newText = None       #編集後のtext
        self.CtrlFlag = 0               #shiftKey pressing:1
        self.AltFlag = 0                #AltKey pressing:1

    def keyPressEvent(self, event):
        """ keyboardのevent取得と処理"""
        key = event.key()
        #ctrl(alt) + <enter> <Return> ?
        if self.CtrlFlag == 1 or self.AltFlag == 1:
            if key == Qt.Key_Enter or Qt.Key_Return:
                #eventの内容を変更して、再発行
                enterEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier)
                #QCoreApplication.postEvent(self, enterEvent)
                return QTextEdit.keyPressEvent(self, enterEvent)
        #<enter> or <return> ?
        elif self.CtrlFlag == 0 and self.AltFlag == 0:
            #editorの終了?
            if key == Qt.Key_Enter or key == Qt.Key_Return:
                #編集後のtextを取得
                self.table.newText = self.toPlainText()
                #tableのenterSignalを発行
                #  signalを発行して、main側に知らせる
                self.table.enterSignal.emit()
                return
        #ctrlKey?
        if key == Qt.Key_Control:
            #flagをセット
            self.CtrlFlag = 1
        #AltKey?
        elif key == Qt.Key_Alt:
            #flagをセット
            self.AltFlag = 1
        return QTextEdit.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        key = event.key()
        #CtrlKeyを離した？
        if key == Qt.Key_Control:
            #CtrlFlagをクリアする
            self.CtrlFlag = 0
        elif key == Qt.Key_Alt:
            #AltFlagをクリア
            self.AltFlag = 0
        return QTextEdit.keyReleaseEvent(self, event)
