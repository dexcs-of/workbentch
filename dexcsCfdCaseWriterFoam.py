# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2013-2015 - Juergen Riegel <FreeCAD@juergen-riegel.net> *
# *   Copyright (c) 2017 Alfred Bogaers (CSIR) <abogaers@csir.co.za>        *
# *   Copyright (c) 2017 Johan Heyns (CSIR) <jheyns@csir.co.za>             *
# *   Copyright (c) 2017 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>          *
# *   Copyright (c) 2019-2020 Oliver Oxtoby <oliveroxtoby@gmail.com>        *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD
import dexcsCfdTools
from dexcsCfdTools import cfdMessage
import os
import os.path
import shutil
from FreeCAD import Units
import TemplateBuilder
import dexcsCfdMeshRefinement
import glob
import pythonVerCheck
import pyDexcsSwakSubset

class dexcsCfdCaseWriterFoam:
    def __init__(self, analysis_obj):
        self.analysis_obj = analysis_obj
        self.solver_obj = dexcsCfdTools.getSolver(analysis_obj)
        self.physics_model = dexcsCfdTools.getPhysicsModel(analysis_obj)
        self.mesh_obj = dexcsCfdTools.getMesh(analysis_obj)
        #self.material_objs = dexcsCfdTools.getMaterials(analysis_obj)
        #self.bc_group = dexcsCfdTools.getCfdBoundaryGroup(analysis_obj)
        #self.initial_conditions = dexcsCfdTools.getInitialConditions(analysis_obj)
        #self.porousZone_objs = dexcsCfdTools.getPorousZoneObjects(analysis_obj)
        #self.initialisationZone_objs = dexcsCfdTools.getInitialisationZoneObjects(analysis_obj)
        #self.zone_objs = dexcsCfdTools.getZoneObjects(analysis_obj)
        self.mesh_generated = False
        self.working_dir = dexcsCfdTools.getOutputPath(self.analysis_obj)

    def writeAllrun(self, progressCallback=None):
        """ writeCase() will collect case settings, and finally build a runnable case. """
        cfdMessage("Writing AllrunDexcs to folder {}\n".format(self.working_dir))
        if not os.path.exists(self.working_dir):
            raise IOError("Path " + self.working_dir + " does not exist.")

        # Perform initialisation here rather than __init__ in case of path changes
        self.case_folder = os.path.join(self.working_dir, self.solver_obj.InputCaseName)
        self.case_folder = os.path.expanduser(os.path.abspath(self.case_folder))
        
        os.chdir(self.case_folder)
        solver = self.getSolver().replace(';','')

        import pathlib
        fname = os.path.join(self.case_folder, "Allrun")
        p_new = pathlib.Path(fname)
        
        title =  "#!/bin/bash\n"
        prefs = dexcsCfdTools.getPreferencesLocation()
        installation_path = FreeCAD.ParamGet(prefs).GetString("InstallationPath", "")
        envOpenFOAMFix = os.path.expanduser(installation_path)
        envSet = "source " + envOpenFOAMFix + '/etc/bashrc\n'

        self.ParallelCores = self.solver_obj.ParallelCores
        #print(self.ParallelCores)
        if self.ParallelCores == 1:
            solverSet = solver + " | tee solve.log"
        else:
            solverSet = "decomposePar | tee decomposePar.log\n"
            solverSet = solverSet + "mpirun -np " + str(self.ParallelCores) + " " + solver + " -parallel | tee solve.log"
        cont = title + envSet + solverSet

        with p_new.open(mode='w') as f:
            f.write(cont)
        
        # Update Allrun permission - will fail silently on Windows
        fname = os.path.join(self.case_folder, "Allrun")
        import stat
        s = os.stat(fname)
        os.chmod(fname, s.st_mode | stat.S_IEXEC)

        fname = os.path.join(self.case_folder, "Allreconst")
        p_new = pathlib.Path(fname)
        solverSet = "reconstructPar -latestTime | tee reconstructPar.log"
        cont = title + envSet + solverSet
        with p_new.open(mode='w') as f:
            f.write(cont)
        s = os.stat(fname)
        os.chmod(fname, s.st_mode | stat.S_IEXEC)

        cfdMessage("Successfully wrote case to folder {}\n".format(self.working_dir))
        
        self.template_path = os.path.join(dexcsCfdTools.get_module_path(), "data", "dexcs")
        settings={}
        settings['system']={}
        settings['solver']={}
        settings['system']['CasePath'] = self.case_folder
        settings['solver']['ParallelCores'] = self.solver_obj.ParallelCores
        settings['solver']['ParallelMethod'] = self.solver_obj.ParallelMethod
        TemplateBuilder.TemplateBuilder(self.case_folder, self.template_path, settings)
        
        return True

    def getSolver(self):
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

