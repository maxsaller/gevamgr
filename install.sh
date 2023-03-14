#!/bin/bash

# Icon for geva manager
if [ -d "${HOME}/.icons" ]
then
	cp -v gevamgr.png ${HOME}/.icons/
else
	mkdir -v ${HOME}/.icons
	cp -v gevamgr.png ${HOME}/.icons/
fi

# Create desktop file
loc=`pwd`
echo "[Desktop Entry]" > gevamgr.desktop
echo "Type=Application" >> gevamgr.desktop
echo "Version=1.0" >> gevamgr.desktop
echo "Name=Geva Manager" >> gevamgr.desktop
echo "Comment=Monitoring tool for the Geva cluster of workstations" >> gevamgr.desktop
echo "Exec=${loc}/gevamgr.sh" >> gevamgr.desktop
echo "Icon=gevamgr" >> gevamgr.desktop
echo "Terminal=false" >> gevamgr.desktop
echo "Categories=Utility;" >> gevamgr.desktop

# Install desktop file and update database
desktop-file-install --dir=${HOME}/.local/share/applications gevamgr.desktop
sudo update-desktop-database -v ${HOME}/.local/share/applications

# Clean up
rm gevamgr.desktop