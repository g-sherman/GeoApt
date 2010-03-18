#!/bin/sh
# Run the GeoApt data browser. This script works on Mac OS X and
# Linux/Unix variants
# Copyright (C) 2008 Gary Sherman
# Licensed under the terms of GNU GPL 2
#
# If the full path to the QGIS install is specified the script sets 
# LD_LIBRARY_PATH (DYLD_LIBRARY_PATH on OS X), PYTHONPATH, and QGISHOME
# and then runs the main script GeoApt.py. If the full path is not 
# specified on the command line, the script looks for QGIS on the PATH 
# and sets the environment accordingly. 
# 
if [ -z "$1" ]
then
  # try to find the QGIS path and set the environment
  QGISPATH=`which qgis`
  if [ -z "$QGISPATH" ]
  then
      echo "Specify the full path to your QGIS 1.x install."
      echo "Hint: On a Mac this will be something like /Applications/Qgis.app"
      echo "      If you have built using CMake you will have to adjust this script"
      echo "Hint: On Linux specify the directory containing bin/qgis. e.g. /usr or /usr/local"
  else
      echo "Found QGIS at: $QGISPATH"
      # strip uneeded parts from the path
      if echo "$OSTYPE" | grep -q "darwin"
      then
          STRIP=/Contents/MacOS/qgis
          QGISPATH=${QGISPATH%$STRIP}
          echo "OS X path to QGIS binary: $QGISPATH"
      else
          STRIP=/bin/qgis
          QGISPATH=${QGISPATH%$STRIP}
      fi
  fi
fi
    if [ -z "$QGISPATH" ]
    then
      QGISBASE=$1
    else
      QGISBASE=$QGISPATH
    fi

    if echo "$OSTYPE" | grep -q "darwin"
    then
      # setup for a Mac
      echo "Setting DYLD_LIBRARY_PATH to $QGISBASE/Contents/MacOS/lib"
      export DYLD_LIBRARY_PATH=$QGISBASE/Contents/MacOS/lib
      echo "Setting PYTHONPATH to $QGISBASE/Contents/Resources/python:$QGISBASE/Contents/MacOS/share/qgis/python"
      export PYTHONPATH=$QGISBASE/Contents/Resources/python:$QGISBASE/Contents/MacOS/share/qgis/python
      echo "Setting QGISHOME to $QGISBASE/Contents/MacOS"
      export QGISHOME=$QGISBASE/Contents/MacOS
     else
      # setup for a Linux/Unix variant
      echo "Setting LD_LIBRARY_PATH to $QGISBASE/lib"
      export LD_LIBRARY_PATH=$QGISBASE/lib
      echo "Setting PYTHONPATH to $PYTHONPATH:$QGISBASE/share/qgis/python"
      export PYTHONPATH=$QGISBASE/share/qgis/python 
      echo "Setting QGISHOME to $QGISBASE"
      export QGISHOME=$QGISBASE
    fi

   ./GeoApt.py

