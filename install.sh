#!/bin/sh

majorversion=$(gedit --version | sed -n 's/gedit.*\s\([0-9]\).*/\1/p')
minorversion=$(gedit --version | sed -n 's/gedit.*\s[0-9]\.\([0-9]*\).*/\1/p')
installfiles="editorconfig_plugin/"
editorconfigcore="editorconfig-core-py/"

if [ "$majorversion" -eq "3" ] ; then
    localinstalldir=~/.local/share/gedit/plugins
    rootinstalldir=/usr/lib/gedit/plugins
    installfiles="$installfiles $editorconfigcore editorconfig_gedit3.py editorconfig.plugin"
else
    localinstalldir=~/.gnome2/gedit/plugins
    rootinstalldir=/usr/lib/gedit-2/plugins
    installfiles="$installfiles $editorconfigcore editorconfig_gedit2.py editorconfig.gedit-plugin"
fi

if [ "$(id -u)" -ne "0" ] ; then
    installdir=$localinstalldir
else
    installdir=$rootinstalldir
fi

echo "Copying $installfiles to $installdir..."
mkdir -p $installdir &&
cp -rfL $installfiles $installdir &&
echo "Done."

if [ "$majorversion" -eq "3" -a "$minorversion" -ge "8" ] ; then
    echo "Patching $installdir/editorconfig.plugin for Python 3 support..."
    sed -i 's/python/python3/' "$installdir/editorconfig.plugin" &&
    echo "Done."
fi
