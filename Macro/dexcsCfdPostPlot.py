# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>          *
# *   Copyright (c) 2017 Johan Heyns (CSIR) <jheyns@csir.co.za>             *
# *   Copyright (c) 2017 Alfred Bogaers (CSIR) <abogaers@csir.co.za>        *
# *   Copyright (c) 2019 Oliver Oxtoby <oliveroxtoby@gmail.com>             *
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

from PySide2 import QtCore
import FreeCAD
from freecad.plot import Plot

class PostPlot:
    def __init__(self):
        self.fig = Plot.figure(FreeCAD.ActiveDocument.Name + "PostProcessing")

        self.updated = False
        self.postX = []
        self.postY = {}

    def updatePosts(self, Title, labelY, labelX, postX, postY):
        self.updated = True
        self.title = Title
        self.labelY = labelY
        self.labelX = labelX
        self.postX = postX
        self.postY = postY

    def refresh(self):
        if self.updated:
            self.updated = False
            ax = self.fig.axes
            ax.cla()
            ax.set_title(self.title)
            ax.set_xlabel(self.labelX)
            ax.set_ylabel(self.labelY)

            for k in self.postY:
                if self.postY[k]:
                    x = self.postX
                    y = self.postY[k]
                    ax.plot(x, y, label=k, linewidth=1)

            ax.grid()
            ax.legend(loc='lower right')

            self.fig.canvas.draw()
