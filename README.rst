===========================
GeoApt Spatial Data Browser
===========================
GeoApt is a spatial data browser and theme catalog written in Python
using the QGIS libraries.

Copyright (C) 2010-2011 Gary Sherman

All code is licensed under the GNU GPL version 2.

Features
--------

- Browse directories and preview raster and vector data
- Drag and drop raster or vector data files to QGIS or other applications
- View metadata about the data

NOTE - the Theme and Database functions are not implemented in this version

Requirements
------------

- Python 
- PyQt
- Qt
- A QGIS install

Depending on your platform, the QGIS install may include the needed PyQt and
Qt requirements.

Downloads
---------
There are binaries of version 1.3 available for Windows and Mac OS X.
This version was released in March 2010. See the Resources section for
the URL to download.

Running GeoApt Spatial Data Browser
-----------------------------------
The development version of GeoApt runs as a Python script. 

* On **Linux** or **Mac OS X** -
  Use the run.sh script and specify the path to your QGIS installation.
  Running the script with no arguments will give you a hint.

* On **Windows** you must have the OSGeo4w install of QGIS. To run the browser

  1. From the Start menu, open an OSGeo4w shell
  2. Set the environment by issuing the following commands::

       set PATH=%PATH%;c:\osgeo4w\apps\qgis-unstable\bin
       set PYTHONPATH=%PYTHONPATH%;c:\osgeo4w\apps\qgis-unstable\python
       set QGISHOME=c:\osgeo4w\apps\qgis-unstable        

  These settings assume your OSGeo4w install uses the default location. If
  not, adjust accordingly.

Contributing to GeoApt
----------------------
We welcome contributions to the project. If you want to contribute to
GeoApt follow these steps:

1. If you don't have one already, create a GitHub account
   (http://github.com)
2. Fork the GeoApt project (http://help.github.com/forking)
3. Clone a local working copy 
4. Make your changes and push to your forked repository
5. Send a pull request so your changes can be reviewed and committed into
   the project (http://help.github.com/pull-requests)


Resources
---------

* Mailing list: http://groups.google.com/group/geoapt-browser
* Download: http://geoapt.com/geoapt-data-browser
* Source code: http://github.com/g-sherman/GeoApt
