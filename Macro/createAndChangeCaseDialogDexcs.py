#!/usr/bin/python3
#  coding:  utf-8
#


import os
import sys
import pyTreeFoam

def showDialog():
    treeFoamPath = os.getenv("TreeFoamPath")
    path = treeFoamPath + os.sep + "python"
    comm = "./createAndChangeCaseDialog.py "  + caseDir + " &"
    pyTreeFoam.run(path).command(comm)


if __name__ == "__main__":
    caseDir = sys.argv[1]           #caseDir
    caseDir = os.path.abspath(caseDir)
    showDialog()
