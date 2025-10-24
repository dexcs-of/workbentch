#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import re

import FreeCAD
import Mesh
#import os
import re
import tempfile
import PySide
from PySide import QtGui

import pythonVerCheck
import dexcsCfdTools
App = FreeCAD

def getCaseFileName():
	active_analysis = dexcsCfdTools.getActiveAnalysis()
	optionOutputPath = dexcsCfdTools.getOptionOutputPath()
	if optionOutputPath:
		if active_analysis:
			modelDir =  active_analysis.OutputPath
		else:
			if optionOutputPath :    
				doc = App.ActiveDocument
				name = os.path.splitext(doc.FileName)[0]
				modelDir = os.path.dirname(doc.FileName)
				caseFileDict = modelDir + "/.CaseFileDict"
				if os.path.isfile(caseFileDict) == True:
					f = open(caseFileDict)
					modelDir = f.read()
					f.close()
				else:
					output_dir = dexcsCfdTools.getDefaultOutputPath()
					if os.path.exists(output_dir) == True:
						modelDir = output_dir
					else:
						modelDir = os.path.dirname(doc.FileName)
			else:
					modelDir = os.path.dirname(doc.FileName)
	else:
				doc = App.ActiveDocument
				modelDir = os.path.dirname(doc.FileName)

	return modelDir

def convertPrPInpFile(caseDir,modelName,solverInp,scale_factor,solidName,young,poison,density,dT,prt_frq,finalTime):
	inpFile = caseDir + '/' + modelName + '/' + solverInp
	s_f = float(scale_factor)
	f = open(inpFile)
	x = f.read()
	f.close()
	y = x.split('\n')
	# *英大文字で始まる
	deckCommand = r'^\*[A-Z]'
	# 数値で始まる
	deckNumData = r'^\d+'
	# *で始まる
	deckAstariskData = r'^\d+'
	message = str(inpFile) + _(" has been read.")
	print (message)

	inpFileName = caseDir + '/' + modelName + '/' + solidName + '.inp'
	namFileName = caseDir + '/' + modelName + '/interface.nam'
	nodeFileName = caseDir + '/' + modelName + '/allnodes.nam'

	is1=0; is2=0
	nodeList = []
	px = [] ; py = [] ; pz = []
	for i in range(len(y)):
		i = i + 1
		#if ( y[i].strip() == '** Nodes +++++++++++++++++++++++++++++++++++++++++++++++++++'):
		if ( y[i] == '** Nodes +++++++++++++++++++++++++++++++++++++++++++++++++++'):
			i = i + 2
			match = None
			while (match is None):
			#while (i < 100): ## for debug
				# 数値で始まる（データ）カードを探す
				matchData = re.search(deckNumData, y[i]) 
				#print ('i'+str(i)+': '+y[i])## for debug
				if matchData :
					pData = y[i].split(',')
					#print(pData)## for debug
					# 見つかった数値をリスト（nodeList）に加える
					is1 = is1 + 1 
					nodeList.append(pData[0])
					px.append(pData[1])			
					py.append(pData[2])			
					pz.append(pData[3])
					y[i] = str(pData[0])		
					y[i] = y[i] + ", {:.6E}".format(float(pData[1])*s_f)
					y[i] = y[i] + ", {:.6E}".format(float(pData[2])*s_f)
					y[i] = y[i] + ", {:.6E}".format(float(pData[3])*s_f)			
				i = i + 1
				match = re.search( deckCommand, y[i] )
			break

	nodeFile = open(nodeFileName , 'w')
	nodeFile.writelines('** Nodes\n')        
	nodeFile.writelines('*Node, NSET=Nall\n')        

	for i in range(len(nodeList)):
		nodeFile.writelines(nodeList[i])
		nodeFile.writelines(', %E' %(float(px[i])*s_f))
		nodeFile.writelines(', %E' %(float(py[i])*s_f))
		nodeFile.writelines(', %E' %(float(pz[i])*s_f) + '\n')
	nodeFile.close()
	
	is1=0; is2=0
	nodeList = []
	for i in range(len(y)):
		i = i + 1
		if ( y[i].strip() == '*Cload'):
			iCload = i
			i = i + 1
			match = None
			while (match is None):
				# 数値で始まる（データ）カードを探す
				matchData = re.search(deckNumData, y[i]) 
				if matchData :
					# 見つかった数値をリスト（nodeList）に加える
					is1 = is1 + 1 ; nodeList.append(matchData.group(0))			
				i = i + 1
				# *英大文字で始まる（コマンド）カードを探す
				match = re.search( deckCommand, y[i] )
			break
	inpFile = open(inpFileName , 'w')

	if len(nodeList) > 0:
		# 重複ノードを削除して順番に並び替える
		cNodeList = sorted(list(set(nodeList)), key=int )
	
		namFile = open(namFileName , 'w')
		namFile.writelines('*NSET,NSET=Nsurface\n')        

		for i in range(len(cNodeList)):
			namFile.writelines(cNodeList[i])
			namFile.writelines(',\n')
		namFile.close()

		inpFile.writelines('*INCLUDE, INPUT=interface.nam\n')
	else:
		Concentrated_force = y[iCload+1].split(",")[0]
		print("patch Name is " + Concentrated_force)

	for i in range(len(y)):
		if Concentrated_force in y[i]:
			y[i] = y[i].replace(Concentrated_force, 'Nsurface')	
	
	inpFile.writelines('*INCLUDE, INPUT=allnodes.nam\n')


	if ( int(prt_frq) > 0 ):
		for i in range(len(y)):
			if ( y[i].strip() == '*Node file'):
				#*NODE FILEカードは書き換える
				y[i] = '*NODE FILE' + ", FREQUENCY=" + str(prt_frq)
			if ( y[i].strip() == '*El file'):
				#*EL FILEカードは書き換える
				y[i] = '*EL FILE' + ", FREQUENCY=" + str(prt_frq)
	for i in range(len(y)):
		if ( y[i].strip()[0:6] == '*Shell'):
			# *Shellの寸法をスケール変更
			y[i+1] = str( float(y[i+1]) * s_f )
	for i in range(len(y)):
		if ( y[i].strip() == '*Elastic'):
			# dataカードは書き換える
			y[i+1] = str(float(young)*1000000.0) + ", " + str(poison)
			# 追加行ナンバー(iDensity)を登録(*ELASTICカードの2行下)
			iDensity = i + 1
	for i in range(len(y)):
		if ( y[i].strip() == '*Step'):
			# *STEPカードは書き換える
			y[i] = '*STEP, NLGEOM, INC=1000000'

	for i in range(len(y)):
			# *STATICカードは書き換える
		if ( y[i].strip() == '*Static'):
			y[i] = '*DYNAMIC, DIRECT'
			# 追加行ナンバー(iDynamic)を登録(*STATICカードの1行下)
			iDynamic = i

	for i in range(len(y)):
		#if ( y[i].strip() == '* Nodes +++++++++++++++++++++++++++++++++++++++++++++++++++'):
		if ( y[i] == '** Nodes +++++++++++++++++++++++++++++++++++++++++++++++++++'):
			# Nodeのデータカードから、
			# 次のコマンドカードが見つかるまでの
			# 位置（iNode〜iNode+jN）を探す
			jN = 2 ; iNode = i
			match = None
			while (match is None):
				#print(jN,y[i+jN])
				jN = jN + 1
				# *英大文字で始まる（コマンド）カードを探す
				match = re.search( deckCommand, y[i+jN] )
			break

	for i in range(len(y)):
		if ( y[i].strip() == '*Cload'):
			# CLOADのデータカードから、
			# 次のコマンドカードが見つかるまでの
			# 位置（iCload〜iCload+j）を探す
			j = 1 ; iCload = i
			match = None
			while (match is None):
				j = j + 1
				# *英大文字で始まる（コマンド）カードを探す
				match = re.search( deckCommand, y[i+j] )
			break

	for i in range(len(y)):
		if( i >= iNode and i < iNode+jN-1 ):
			pass
		elif( i <= iCload or i > iCload+j-4 ) :
		#if( i <= iCload or i > iCload+j-4 ) :
			inpFile.writelines(y[i]+'\n')
			if ( i == iCload ):
				inpFile.writelines('Nsurface, 1, 0.0\n')
				inpFile.writelines('Nsurface, 2, 0.0\n')
				inpFile.writelines('Nsurface, 3, 0.0\n')
			if ( i == iDensity ):
				inpFile.writelines('*DENSITY\n')
				# 密度の値
				inpFile.writelines(str(density) + '\n')
			if ( i == iDynamic ):
				# 時間刻み、最終時刻の値
				inpFile.writelines(str(dT) + ', '+ str(finalTime) + '\n')

	inpFile.close()

def convertInpFile(caseDir,modelName,solverInp,scale_factor,solidName,young,poison,density,dT,prt_frq,finalTime):
	inpFile = caseDir + '/' + modelName + '/' + solverInp
	s_f = float(scale_factor)
	f = open(inpFile)
	x = f.read()
	f.close()
	y = x.split('\n')
	# *英大文字で始まる
	deckCommand = r'^\*[A-Z]'
	# 数値で始まる
	deckNumData = r'^\d+'
	# *で始まる
	deckAstariskData = r'^\d+'
	message = str(inpFile) + _(" has been read.")
	print (message)

	inpFileName = caseDir + '/' + solidName + '.inp'
	namFileName = caseDir + '/interface.nam'
	nodeFileName = caseDir + '/allnodes.nam'

	is1=0; is2=0
	nodeList = []
	px = [] ; py = [] ; pz = []
	for i in range(len(y)):
		i = i + 1
		if ( y[i].strip() == '** Nodes'):
			i = i + 2
			match = None
			while (match is None):
			#while (i < 100): ## for debug
				# 数値で始まる（データ）カードを探す
				matchData = re.search(deckNumData, y[i]) 
				#print ('i'+str(i)+': '+y[i])## for debug
				if matchData :
					pData = y[i].split(',')
					#print(pData)## for debug
					# 見つかった数値をリスト（nodeList）に加える
					is1 = is1 + 1 
					nodeList.append(pData[0])
					px.append(pData[1])			
					py.append(pData[2])			
					pz.append(pData[3])
					y[i] = str(pData[0])		
					y[i] = y[i] + ", {:.6E}".format(float(pData[1])*s_f)
					y[i] = y[i] + ", {:.6E}".format(float(pData[2])*s_f)
					y[i] = y[i] + ", {:.6E}".format(float(pData[3])*s_f)			
				i = i + 1
				match = re.search( deckCommand, y[i] )
			break

	nodeFile = open(nodeFileName , 'w')
	nodeFile.writelines('** Nodes\n')        
	nodeFile.writelines('*Node, NSET=Nall\n')        

	for i in range(len(nodeList)):
		nodeFile.writelines(nodeList[i])
		nodeFile.writelines(', %E' %(float(px[i])*s_f))
		nodeFile.writelines(', %E' %(float(py[i])*s_f))
		nodeFile.writelines(', %E' %(float(pz[i])*s_f) + '\n')
	nodeFile.close()
	
	is1=0; is2=0
	nodeList = []
	for i in range(len(y)):
		i = i + 1
		if ( y[i].strip() == '*CLOAD'):
			i = i + 1
			match = None
			while (match is None):
				# 数値で始まる（データ）カードを探す
				matchData = re.search(deckNumData, y[i]) 
				if matchData :
					# 見つかった数値をリスト（nodeList）に加える
					is1 = is1 + 1 ; nodeList.append(matchData.group(0))			
				i = i + 1
				# *英大文字で始まる（コマンド）カードを探す
				match = re.search( deckCommand, y[i] )
			break
	# 重複ノードを削除して順番に並び替える
	cNodeList = sorted(list(set(nodeList)), key=int )

	namFile = open(namFileName , 'w')
	namFile.writelines('*NSET,NSET=Nsurface\n')        

	for i in range(len(cNodeList)):
		namFile.writelines(cNodeList[i])
		namFile.writelines(',\n')
	namFile.close()


	inpFile = open(inpFileName , 'w')
	inpFile.writelines('*INCLUDE, INPUT=interface.nam\n')
	inpFile.writelines('*INCLUDE, INPUT=allnodes.nam\n')


	if ( int(prt_frq) > 0 ):
		for i in range(len(y)):
			if ( y[i].strip() == '*NODE FILE'):
				#*NODE FILEカードは書き換える
				y[i] = '*NODE FILE' + ", FREQUENCY=" + str(prt_frq)
			if ( y[i].strip() == '*EL FILE'):
				#*EL FILEカードは書き換える
				y[i] = '*EL FILE' + ", FREQUENCY=" + str(prt_frq)
	for i in range(len(y)):
		if ( y[i].strip() == '*ELASTIC'):
			# dataカードは書き換える
			y[i+1] = str(float(young)*1000000) + ", " + poison
			# 追加行ナンバー(iDensity)を登録(*ELASTICカードの2行下)
			iDensity = i + 1
	for i in range(len(y)):
		if ( y[i].strip() == '*STEP'):
			# *STEPカードは書き換える
			y[i] = '*STEP, NLGEOM, INC=1000000'

	for i in range(len(y)):
			# *STATICカードは書き換える
		if ( y[i].strip() == '*STATIC'):
			y[i] = '*DYNAMIC, DIRECT'
			# 追加行ナンバー(iDynamic)を登録(*STATICカードの1行下)
			iDynamic = i

	for i in range(len(y)):
		if ( y[i].strip() == '** Nodes'):
			# Nodeのデータカードから、
			# 次のコマンドカードが見つかるまでの
			# 位置（iNode〜iNode+jN）を探す
			jN = 1 ; iNode = i
			match = None
			while (match is None):
				#print(jN,y[i+jN])
				jN = jN + 1
				# *英大文字で始まる（コマンド）カードを探す
				match = re.search( deckCommand, y[i+jN] )
			break

	for i in range(len(y)):
		if ( y[i].strip() == '*CLOAD'):
			# CLOADのデータカードから、
			# 次のコマンドカードが見つかるまでの
			# 位置（iCload〜iCload+j）を探す
			j = 1 ; iCload = i
			match = None
			while (match is None):
				j = j + 1
				# *英大文字で始まる（コマンド）カードを探す
				match = re.search( deckCommand, y[i+j] )
			break

	for i in range(len(y)):
		if( i >= iNode and i < iNode+jN-1 ):
			pass
		elif( i <= iCload or i > iCload+j-4 ) :
		#if( i <= iCload or i > iCload+j-4 ) :
			inpFile.writelines(y[i]+'\n')
			if ( i == iCload ):
				inpFile.writelines('Nsurface, 1, 0.0\n')
				inpFile.writelines('Nsurface, 2, 0.0\n')
				inpFile.writelines('Nsurface, 3, 0.0\n')
			if ( i == iDensity ):
				inpFile.writelines('*DENSITY\n')
				# 密度の値
				inpFile.writelines(str(density) + '\n')
			if ( i == iDynamic ):
				# 時間刻み、最終時刻の値
				inpFile.writelines(str(dT) + ', '+ str(finalTime) + '\n')
	
	inpFile.close()

def get_model(caseDir,modelName,solverInp):
	inpFile = caseDir + '/' + modelName + '/' + solverInp
	f = open(inpFile)
	x = f.read()
	f.close()
	y = x.split('\n')
	# *英大文字で始まる
	deckCommand = r'^\*[A-Z]'
	# 数値で始まる
	deckNumData = r'^\d+'
	# *で始まる
	deckAstariskData = r'^\d+'
	modelData="1"
	for i in range(len(y)):
		if ( y[i].strip() == '*Elastic'):
			modelData = y[i+1]
	young=str(float(modelData.split(',')[0])/1000000)
	poison=modelData.split(',')[1]
	return [young,poison]

def getSolver():
    solver = ""
    fileName = "./system/controlDict"
    if glob.glob(fileName) != "":
        f=open("./system/controlDict")
        for line in f.readlines():
            item = line.split()
            if len(item)>0:
                if item[0] == "application":
                    solver = line.split()[1]
                    break
    return solver


def getFoldersFiles(wdir):

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


def caseFileDir(doc):

    name = os.path.splitext(doc.FileName)[0]
    modelDir = os.path.dirname(doc.FileName)

    optionOutputPath = dexcsCfdTools.getOptionOutputPath()
    if optionOutputPath :       
        #モデルファイル置き場がケースファイルの場所（.CaseFileDictで指定）と異なる場合
        caseFileDict = modelDir + "/.CaseFileDict"
        if os.path.isfile(caseFileDict) :
            f = open(caseFileDict)
            modelDir = f.read()
            f.close()

    return modelDir


