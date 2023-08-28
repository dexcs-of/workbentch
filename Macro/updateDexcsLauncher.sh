#!/bin/bash

echo "DEXCS Launcher update"
echo " Overwrite your FreeCAD SettingFile(user.cfg)? (Y/N)"
read answer

case $answer in
	Y)
		echo -e "Overwrite FreeCAD SettingFile(user.cfg)"
		WHO=`whoami`
		cp ~/.FreeCAD/user.cfg ~/.FreeCAD/user.cfg.$WHO.orig
		sed "s/home\/dexcs\//home\/$WHO\//g" user.cfg.dexcs > user.cfg
		cp -r * ~/.FreeCAD/
		;;
	N)
		echo -e "Your FreeCAD SettingFile(user.cfg) does not changed."
		cp -r * ~/.FreeCAD/
		;;
	*)
		echo -e "Answer is Y or N"
		;;
esac


