#!/bin/bash
# copy the ogr provider
BASEDIR=/Users/gsherman/development/geoapt/dist/GeoApt.app
mkdir -p $BASEDIR/Contents/PlugIns/qgis
cp ~/QGIS_unstable/qgis1.5.0.app/Contents/MacOS/lib/qgis/libogrprovider.so $BASEDIR/Contents/PlugIns/qgis 
cd $BASEDIR/Contents/PlugIns/qgis 
install_name_tool -change QtXml.framework/Versions/4/QtXml @executable_path/../Frameworks/QtXml.framework/Versions/4/QtXml libogrprovider.so
install_name_tool -change QtCore.framework/Versions/4/QtCore @executable_path/../Frameworks/QtCore.framework/Versions/4/QtCore libogrprovider.so
install_name_tool -change QtGui.framework/Versions/4/QtGui @executable_path/../Frameworks/QtGui.framework/Versions/4/QtGui libogrprovider.so
install_name_tool -change QtNetwork.framework/Versions/4/QtNetwork @executable_path/../Frameworks/QtNetwork.framework/Versions/4/QtNetwork libogrprovider.so
install_name_tool -change QtSvg.framework/Versions/4/QtSvg @executable_path/../Frameworks/QtSvg.framework/Versions/4/QtSvg libogrprovider.so
cd $BASEDIR
mkdir -p $BASEDIR/Contents/MacOS/lib
cd $BASEDIR/Contents/MacOS/lib
cp ~/QGIS_unstable/qgis1.5.0.app/Contents/MacOS/lib/libqgis_core.1.5.0.dylib .
cp ~/QGIS_unstable/qgis1.5.0.app/Contents/MacOS/lib/libqgis_gui.1.5.0.dylib .
install_name_tool -change QtXml.framework/Versions/4/QtXml @executable_path/../Frameworks/QtXml.framework/Versions/4/QtXml libqgis_core.1.5.0.dylib 
install_name_tool -change QtCore.framework/Versions/4/QtCore @executable_path/../Frameworks/QtCore.framework/Versions/4/QtCore libqgis_core.1.5.0.dylib 
install_name_tool -change QtGui.framework/Versions/4/QtGui @executable_path/../Frameworks/QtGui.framework/Versions/4/QtGui libqgis_core.1.5.0.dylib 
install_name_tool -change QtNetwork.framework/Versions/4/QtNetwork @executable_path/../Frameworks/QtNetwork.framework/Versions/4/QtNetwork libqgis_core.1.5.0.dylib 
install_name_tool -change QtSvg.framework/Versions/4/QtSvg @executable_path/../Frameworks/QtSvg.framework/Versions/4/QtSvg libqgis_core.1.5.0.dylib 

install_name_tool -change QtXml.framework/Versions/4/QtXml @executable_path/../Frameworks/QtXml.framework/Versions/4/QtXml libqgis_gui.1.5.0.dylib 
install_name_tool -change QtCore.framework/Versions/4/QtCore @executable_path/../Frameworks/QtCore.framework/Versions/4/QtCore libqgis_gui.1.5.0.dylib 
install_name_tool -change QtGui.framework/Versions/4/QtGui @executable_path/../Frameworks/QtGui.framework/Versions/4/QtGui libqgis_gui.1.5.0.dylib 
install_name_tool -change QtNetwork.framework/Versions/4/QtNetwork @executable_path/../Frameworks/QtNetwork.framework/Versions/4/QtNetwork libqgis_gui.1.5.0.dylib 
install_name_tool -change QtSvg.framework/Versions/4/QtSvg @executable_path/../Frameworks/QtSvg.framework/Versions/4/QtSvg libqgis_gui.1.5.0.dylib 

# fix up the python shared libs
install_name_tool -change @executable_path/lib/libqgis_core.1.5.0.dylib @executable_path/lib/libqgis_core.1.5.0.dylib /Users/gsherman/development/geoapt/dist/GeoApt.app/Contents/Resources/lib/python2.6/lib-dynload/qgis/core.so
install_name_tool -change @executable_path/lib/libqgis_gui.1.5.0.dylib @executable_path/lib/libqgis_gui.1.5.0.dylib /Users/gsherman/development/geoapt/dist/GeoApt.app/Contents/Resources/lib/python2.6/lib-dynload/qgis/gui.so

