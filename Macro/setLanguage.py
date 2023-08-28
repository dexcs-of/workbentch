#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gettext


lang="Japanese"

treeFoamPath = os.environ["TreeFoamPath"]
if lang == "English":
    os.environ["LANG"] = "en_US.UTF-8"
    os.environ["LANGUAGE"] = "en_US.UTF-8"
    gettext.install("treefoam", treeFoamPath + "/data/locale")
else:
    os.environ["LANG"] = "ja_JP.UTF-8"
    os.environ["LANGUAGE"] = "ja_JP.UTF-8"
    gettext.install("", treeFoamPath + "/data/locale")

