#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import re
import tempfile
import gettext
import PySide2
from PySide2 import QtGui
import math

import pythonVerCheck
from dexcsCfdPostPlot import PostPlot
from collections import OrderedDict

class dexcsPlotPost():
    def __init__(self,modelDir,Lines):
        #self.plotFile = plotFile
        #self.columnNumber = columnNumber
        #self.scaleFactor = scaleFactor
        #print('deb2',modelDir)
        #print('deb2',Lines)
        self.dexcs_plot(modelDir,Lines)

    def process_column_vector(self,plotFile,columnNumber,scaleFactor):
        f = open(plotFile,"r")
        text = f.readlines()
        f.close()
        postV = []
        for line in text:
            split = line.split()
            if split[0] != "#" :
                try:
                    pX = float((split[columnNumber].replace('(','')).replace(')','')) 
                    pY = float((split[columnNumber+1].replace('(','')).replace(')','')) 
                    pZ = float((split[columnNumber+2].replace('(','')).replace(')','')) 
                    pMag = math.sqrt( pX*pX + pY*pY + pZ*pZ )
                    postV.append( pMag * scaleFactor )
                except:
                    pass
        return postV


    def process_column(self,plotFile,columnNumber,scaleFactor):
    
        f = open(plotFile,"r")
        text = f.readlines()
        f.close()

        postV = []
        for line in text:
            split = line.split()
            if split[0] != "#" :
                try:
                    postV.append( float((split[columnNumber].replace('(','')).replace(')','')) * scaleFactor )
                except:
                    pass
        return postV

    def process_column_X(self,plotFile,columnNumber,scaleFactor):
    
        f = open(plotFile,"r")
        text = f.readlines()
        f.close()
        preX=100000
        epsX=1e-9

        postV = []
        for line in text:
            split = line.split()
            if split[0] != "#" :
                try:
                    tempX = float((split[columnNumber].replace('(','')).replace(')','')) * scaleFactor 
                    if preX == tempX :
                        postX = postX + epsX
                    else:
                        postX = float((split[columnNumber].replace('(','')).replace(')','')) * scaleFactor 
                        preX = postX
                    postV.append( postX )
                except:
                    pass
        return postV

    def dexcs_plot(self,modelDir,lines):
            X_Label='x'
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
                postX = self.process_column_X(X_File[k], X_column[k], X_scaleFactor[k])
                PostsX.append(postX)
                if Y_Vector[k] == "1":
                    PlotValue = self.process_column_vector(Y_File[k], Y_column[k], Y_scaleFactor[k])
                else:
                    PlotValue = self.process_column(Y_File[k], Y_column[k], Y_scaleFactor[k])
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
