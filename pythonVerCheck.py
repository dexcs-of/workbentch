#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import gettext

localedir = os.path.expanduser("~") + "/.FreeCAD/locale"
if sys.version_info.major == 3:
#	if os.environ["LANG"] == "ja:en":
#	    os.environ["LANG"] ="ja"
	gettext.install("CfMeshSetting", localedir)
else:
#	if os.environ["LANGUAGE"] == "ja:en":
#	    os.environ["LANGUAGE"] ="ja"
	gettext.install("CfMeshSetting", localedir, unicode=True)

