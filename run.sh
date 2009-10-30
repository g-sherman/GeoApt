#!/bin/sh
# Run the geonibble data browser
if [ -z "$1" ]
then
  echo "Specify the full path to your QGIS 1.0.x install"
else
  QGISBASE=$1
  export LD_LIBRARY_PATH=$QGISBASE/lib
  export PYTHONPATH=$PYTHONPATH:$QGISBASE/share/qgis/python 
  export QGISHOME=$QGISBASE
  ./GeoNibble.py
fi

