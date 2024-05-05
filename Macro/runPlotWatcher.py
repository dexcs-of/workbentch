#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import glob
#import wx
import PySide
from PySide import QtGui
from PySide import QtCore
from dexcsCfdResidualPlot import ResidualPlot
from collections import OrderedDict
from time import sleep

import pythonVerCheck
import pyDexcsSwakSubset
import dexcsFunctions

modelDir = dexcsFunctions.getCaseFileName()

os.chdir(modelDir)

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

def checkApp(directory, App):
    flag = "NG"
    names = glob.glob(directory + "/" + App)
    if len(names) == 1:
        flag = "OK"
    else:
        names = glob.glob(App)
        if len(names) == 1:
            flag = "OK"
        else:
            paths = os.environ["PATH"].split(":")
            for path in paths:
                names = glob.glob(path + "/" + App)
                if len(names) == 1:
                    flag = "OK"
                    break
    return flag

def process_output(text, niter):
        itimer = 0
        for line in text:
            #print(line),
            split = line.split()

            # Only store the first residual per timestep
            if line.startswith(u"Time = "):
                niter += 1

            # print split
            if "Ux," in split and niter-1 > len(UxResiduals):
                UxResiduals.append(float(split[7].split(',')[0]))
            if "Uy," in split and niter-1 > len(UyResiduals):
                UyResiduals.append(float(split[7].split(',')[0]))
            if "Uz," in split and niter-1 > len(UzResiduals):
                UzResiduals.append(float(split[7].split(',')[0]))
            if "p," in split and niter-1 > len(pResiduals):
                pResiduals.append(float(split[7].split(',')[0]))
            if "p_rgh," in split and niter-1 > len(pResiduals):
                pResiduals.append(float(split[7].split(',')[0]))
            if "h," in split and niter-1 > len(EResiduals):
                EResiduals.append(float(split[7].split(',')[0]))
            # HiSA coupled residuals
            if "Residual:" in split and niter-1 > len(rhoResiduals):
                rhoResiduals.append(float(split[4]))
                UxResiduals.append(float(split[5].lstrip('(')))
                UyResiduals.append(float(split[6]))
                UzResiduals.append(float(split[7].rstrip(')')))
                EResiduals.append(float(split[8]))
            if "k," in split and niter-1 > len(kResiduals):
                kResiduals.append(float(split[7].split(',')[0]))
            if "omega," in split and niter-1 > len(omegaResiduals):
                omegaResiduals.append(float(split[7].split(',')[0]))
        print("niter=",niter)
        if niter > 1:
            itimer=1
            #print(UxResiduals)
            residualPlot.updateResiduals(OrderedDict([
                ('$\\rho$', rhoResiduals),
                ('$U_x$', UxResiduals),
                ('$U_y$', UyResiduals),
                ('$U_z$', UzResiduals),
                ('$p$', pResiduals),
                ('$E$', EResiduals),
                ('$k$', kResiduals),
                ('$\\omega$', omegaResiduals)]))

def _plotResidual(logFile, niter):
        print("log=",logFile)
        f=open(modelDir+"/"+logFile)
        loglines = f.readlines()
        #f.close()
        process_output(loglines, niter)
        #residualPlot.updateResiduals
        residualPlot.updated = True
        residualPlot.refresh()

def errDialog(title, message):
  diag = QtGui.QMessageBox(\
    QtGui.QMessageBox.Information,\
    title,\
    message)
  diag.exec_()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

	solver = getSolver().replace(';','')

	configDict = pyDexcsSwakSubset.readConfigTreeFoam()
	envOpenFOAMFix = configDict["bashrcFOAM"]
	configDict = pyDexcsSwakSubset.readConfigDexcs()
	envTreeFoam = "~/.TreeFoamUser"
	envOpenFOAMFix = envOpenFOAMFix.replace('$TreeFoamUserPath',envTreeFoam)
	envOpenFOAMFix = os.path.expanduser(envOpenFOAMFix)
	solveCaseFix = modelDir
	if checkApp(solveCaseFix, envOpenFOAMFix) == "OK":
	    if solver != "":
	    	saveDir = os.getcwd()
	    	os.chdir(solveCaseFix)
	    	logFile = "solve.log"
	    	if len(glob.glob(logFile)) == 0:
	    	    logFile = "log." + solver
	    	    

	    	UxResiduals = []
	    	UyResiduals = []
	    	UzResiduals = []
	    	pResiduals = []
	    	rhoResiduals = []
	    	EResiduals = []
	    	kResiduals = []
	    	omegaResiduals = []
	    	niter = 0
	    	itimer=1

	    	residualPlot = ResidualPlot()
	    	
	    	_plotResidual(logFile, niter)


	    else:
	    	title = _("error")
	    	message = _("does not exist 'controlDict'.\n")
	    	message = message + _("wrong case directory.")
	    	errDialog(title, message)
	else:
	    title = _("error")
	    message = _("environ file 'bashrcFOAM' does not exist, FOAM terminal could not run.\n")
	    message = message + _("    check contents of configTreeFoam file.")
	    errDialog(title, message)

else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

