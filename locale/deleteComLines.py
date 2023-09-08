#!/usr/bin/env python
# -*- coding: utf-8 -*-

fileName = "ja.po"
f=open(fileName)
lines = f.readlines()
f.close()

newLines = []

i = 0
while i < len(lines):
    if i < 15:
        newLines.append(lines[i])
    else:
        if lines[i][0] != "#":
            newLines.append(lines[i])
    i += 1

fileName = "ja.po"
f=open(fileName, "w")
for line in newLines:
    f.write(line)
f.close()

