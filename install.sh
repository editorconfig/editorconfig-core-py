#!/bin/sh

geditversion=$(gedit --version | sed -n 's/gedit.*\s\([0-9]\).*/\1/p')

if [ "$geditversion" -eq "3" ] ; then
    localinstalldir=~/.local/share/gedit/plugins
    rootinstalldir=/usr/lib/gedit/plugins
    plugindir=gedit3
else
    localinstalldir=~/.gnome2/gedit/plugins
    rootinstalldir=/usr/lib/gedit-2/plugins
    plugindir=gedit2
fi

if [ "$(id -u)" -ne "0" ] ; then
    installdir=$localinstalldir
else
    installdir=$rootinstalldir
fi

echo "Copying $plugdir/* to $installdir..."
mkdir -p $installdir &&
cp -f $plugindir/* $installdir &&
echo "Done."
