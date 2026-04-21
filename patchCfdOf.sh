#!/bin/bash

# FileManager の代わりに、TreeFoamを起動
ln -s ../../dexcsCfdOF/Macro ../CfdOF/CfdOF/Macro
patch -u ../CfdOF/CfdOF/CfdTools.py < CfdTools.patch

#対流項スキームのデフォルトを1次風上に
patch -u ../CfdOF/Data/Templates/case/system/fvSchemes < fvSchemes.patch
#Paraview起動時のWarning回避
patch -u ../CfdOF/Data/Templates/case/pvScript.py < pvScript.patch
#featureAngleを 120 → 85 に変更
patch -u ../CfdOF/Data/Templates/mesh/system/snappyHexMeshDict < snappyHexMeshDict.patch

