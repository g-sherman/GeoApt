#!/usr/bin/env python
# Main window implementation for the data browser
# Copyright (C) 2008-2010 Gary Sherman
# Licensed under the terms of GNU GPL 2
# 2008-03-11 added to git
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import pdb
import sys
import os
import glob
import sqlite3
from add_theme_folder import *
from add_theme import *
from theme_tree import *
from about_geoapt import *
import geoapt_version 
# Environment variable QGISHOME must be set to the 1.0.x install directory
# before running this application
qgis_prefix = os.getenv("QGISHOME")

if qgis_prefix == None:
    print "QGISHOME environment variable not found, looking for QGIS on the PATH"
    # Try to locate the qgis directory
    if sys.platform == 'darwin':
        # look in the usual places
        candidates = glob.glob('/Applications/Q[Gg][Ii][Ss]*.app')
        if len(candidates) > 0:
            # use the first match to run with
            qgis_prefix = "%s/Contents/MacOS" % candidates[0]
        else:
            print """Please set the QGISHOME environment variable to the location of
                  your QGIS application (for example /Applications/Qgis-1.6.app)"""
            sys.exit(1)
    else:
        paths = os.environ['PATH'].split(os.pathsep)
        for path in paths:
            if os.path.exists(os.path.join(path, 'Qgis')) or os.path.exists(os.path.join(path, 'QGIS')):
                # pop the last part of the path (presumably 'bin')
                qgis_prefix = os.path.dirname(path)
                # if on OS X (darwin), pop the Contents part of the path too
                if sys.platform == 'darwin':
                    qgis_prefix = os.path.dirname(qgis_prefix)
                print "It looks like the path to QGIS is: %s\n" % qgis_prefix
                print "To start GeoApt, please use the run.sh script:\n"
                print "  ./run.sh %s\n" % qgis_prefix
    # exit after friendly message
    #sys.exit(1)

# qgis_prefix is set - finish imports
try:
    from qgis.core import *
    from qgis.gui import *
except ImportError as ie_error:
    print "Unable to import the QGIS libraries: %s" % ie_error
    print """Make sure LD_LIBRARY_PATH or DYLD_LIBRARY_PATH points 
to the location of the QGIS shared libraries"""
    sys.exit(1)

try:
    from osgeo import gdal
    have_osgeo = True
except ImportError:
    have_osgeo = False
from theme_database import *
# Import our GUI tree->setRootIndex(model->index(QDir::currentPath()));
from mainwindow_ui import Ui_MainWindow
#from qgstreeview import QgsTreeView
# Import our resources (icons)
import resources

class MainWindow(QMainWindow, Ui_MainWindow):

  def __init__(self):
    # get the list of supported rasters from GDAL
    if have_osgeo:
        self.supported_rasters = self.raster_extensions() 
    else:
        print "GDAL Python bindings not available, setting default raster support"
        self.supported_rasters = ['tif', 'tiff', 'png', 'jpg', 'gif']
    # the list of supported vectors - these are normally supported by OGR
    self.supported_vectors = ['shp', 'tab', 'mif', 'vrt', 'dgn', 'csv', 'kml', 'gmt', 'e00']
    # sort the raster and vector extension lists
    self.supported_rasters.sort()
    self.supported_vectors.sort()
    # Basic geometry types
    self.vector_geometry_types = ['Point', 'Line', 'Polygon']
    self.root = os.getenv("HOME")
    self.dockVisibility = False
    
    QMainWindow.__init__(self)

    # Required by Qt4 to initialize the UI
    self.setupUi(self)

    # Some debug stuff used when sorting out the Mac application bundle
    #QMessageBox.information(self, "GeoApt","Run path is: %s" % sys.argv[0])
    #QMessageBox.information(self, "GeoApt","qgis_prefix is: %s" % qgis_prefix)
    #QMessageBox.information(self, "GeoApt","qgis db path is: %s" % QgsApplication.qgisUserDbFilePath())

    # Set the title for the app
    self.setWindowTitle(QCoreApplication.translate("GeoApt","GeoApt Data Browser"))

    # create the widgets
    self.layout = QHBoxLayout(self.frame)

    self.splitter = QSplitter(self.frame)

    # set the sizes for the splitter
    split_size = [550, 250]
    self.splitter.setSizes(split_size)
    
    self.layout.addWidget(self.splitter)
    self.treeview = QTreeView()
    #self.treeview.__class__.dragObject = self.tvDragObject
    filter = QStringList()
    # build filter list from the supported raster and vector lists
    for vector in self.supported_vectors:
      filter.append("*.%s" % vector)
    for raster in self.supported_rasters:
      filter.append("*.%s" % raster)

    self.model = QDirModel(filter, QDir.Files|QDir.AllDirs|QDir.NoDotAndDotDot, QDir.Name)
    #model.setFilter(QDir.AllDirs)
    # FIXME - add the list to an about dialog so the user can see what file types are supported
    #         rather than printing to shell at startup
    #for filt in self.model.nameFilters():
    #  print filt

    self.treeview.setModel(self.model)
    #treeview.show()

    # hide the columns we don't want
    #self.treeview.hideColumn(1)
    self.treeview.hideColumn(2)
    self.treeview.hideColumn(3)

    # enable drag
    self.treeview.setDragEnabled(True)

    # add a map canvas
    # Create the map canvas
    self.canvas = QgsMapCanvas()
    self.canvas.enableAntiAliasing(True)
    # Set the canvas background color to white 
    self.canvas.setCanvasColor(QColor(255,255,255))
    self.canvas.enableAntiAliasing(True)
    self.canvas.useImageToRender(True)
    self.canvas.setMinimumSize(400,400)
    #self.canvas.show()

    self.tab_widget = QTabWidget()
    self.tab_widget.addTab(self.treeview, QCoreApplication.translate("GeoApt", "Directories"))

    # create the tab and frame for the themes
    self.themes_frame = QFrame()
    self.tab_widget.addTab(self.themes_frame, QCoreApplication.translate("GeoApt", "Themes"))
    # enable drop
    self.themes_frame.setAcceptDrops(True)
    # setup the model for displaying themes
    self.theme_model = QStandardItemModel()

    # setup the view
    theme_grid_layout = QGridLayout(self.themes_frame)
    # setup the toolbar for the theme tab
    self.theme_toolbar = QToolBar(QCoreApplication.translate("GeoApt", "Theme Tools"))
    # Add the map actions to the toolbar
    self.themeAdd = QAction(QIcon(":/qgisbrowser/mActionAddTheme.png"), \
        "Add a new theme folder", self.theme_toolbar)
    self.theme_toolbar.addAction(self.themeAdd)
    self.connect(self.themeAdd, SIGNAL("activated()"), self.new_theme_folder)
    theme_grid_layout.addWidget(self.theme_toolbar)
    self.theme_tree = ThemeTree()
    self.theme_tree.setHeaderHidden(True)
    # using treewidget instead of model/view for themes
    theme_grid_layout.addWidget(self.theme_tree)
    theme_info = QLabel(QCoreApplication.translate("GeoApt", "Right-click on a folder to add themes"))
    theme_grid_layout.addWidget(theme_info)


    # enable drag
    self.theme_tree.setDragEnabled(True)
    self.theme_tree.setDropIndicatorShown(True)
    self.theme_tree.setDragDropMode(QAbstractItemView.DragOnly)
    # XXX Following two lines are for debug of drag from the theme tree
    for t in self.theme_tree.mimeTypes():
        print t
    
    self.dataFrame = QFrame()
    self.tab_widget.addTab(self.dataFrame, QCoreApplication.translate("GeoApt", "Databases"))
    # database feature is not implemented so put a label on it for now
    QLabel(QCoreApplication.translate("GeoApt", "Not Implemented"), self.dataFrame)


    self.splitter.addWidget(self.tab_widget)


    #self.splitter.addWidget(self.treeview)
    self.splitter.addWidget(self.canvas)
    #self.model.refresh
    #self.layout.addWidget(self.splitter)

    # make the connections for the directory/file treeview
    self.connect(self.treeview, SIGNAL("doubleClicked(const QModelIndex&)"), self.showData)
    self.connect(self.treeview, SIGNAL("clicked(const QModelIndex&)"), self.showData)

    # make the connections for the theme treeview
    self.theme_tree.setContextMenuPolicy(Qt.CustomContextMenu) 
    self.connect(self.theme_tree, SIGNAL("customContextMenuRequested(const QPoint &)"), self.theme_tree_popup) 
    self.connect(self.theme_tree, SIGNAL("itemClicked(QTreeWidgetItem*, int)"), self.show_theme)
    

    # set up the actions
    self.action_zoomin = QAction(QIcon(":/qgisbrowser/mActionZoomIn.png"), \
        QCoreApplication.translate("GeoApt", "Zoom In"), self.frame)
    self.connect(self.action_zoomin, SIGNAL("activated()"), self.zoomIn)
    self.action_zoomout = QAction(QIcon(":/qgisbrowser/mActionZoomOut.png"), \
        QCoreApplication.translate("GeoApt", "Zoom Out"), self.frame)
    self.connect(self.action_zoomout, SIGNAL("activated()"), self.zoomOut)
    self.action_pan = QAction(QIcon(":/qgisbrowser/mActionPan.png"), \
        QCoreApplication.translate("GeoApt", "Pan"), self.frame)
    self.connect(self.action_pan, SIGNAL("activated()"), self.pan)
    self.action_zoomfull = QAction(QIcon(":/qgisbrowser/mActionZoomFullExtent.png"), \
        QCoreApplication.translate("GeoApt", "Zoom Full Extent"), self.frame)
    self.connect(self.action_zoomfull, SIGNAL("activated()"), self.zoomFull)

    self.action_metadata = QAction(QIcon(":/qgisbrowser/mActionMetadata.png"), \
        QCoreApplication.translate("GeoApt", "Properties"), self.frame)
    self.connect(self.action_metadata, SIGNAL("activated()"), self.metadata)

    self.action_open_folder = QAction(QIcon(":/qgisbrowser/mActionOpenFolder.png"), \
        QCoreApplication.translate("GeoApt", "Open Folder"), self.frame)
    self.connect(self.action_open_folder, SIGNAL("activated()"), self.openFolder)

    menu_bar = QMenuBar()
    self.menu = self.setMenuBar(menu_bar)

    menu_file = menu_bar.addMenu(QCoreApplication.translate("GeoApt", "File"))
    exit_action = QAction(QCoreApplication.translate("GeoApt", "Exit"), self)
    self.connect(exit_action, SIGNAL("triggered()"), self.exit_gndb)
    menu_file.addAction(exit_action)

    menu_theme = menu_bar.addMenu(QCoreApplication.translate("GeoApt", "Theme"))
    theme_new_folder_action = QAction(QCoreApplication.translate("GeoApt", "Add new folder..."), self)
    self.connect(theme_new_folder_action, SIGNAL("triggered()"), self.new_theme_folder)
    menu_theme.addAction(theme_new_folder_action)
    # Don't implement add new theme menu just yet:
    #theme_new_action = QAction("Add theme...", self)
    #self.connect(theme_new_action, SIGNAL("triggered()"), self.new_theme)
    #menu_theme.addAction(theme_new_action)
    #menu_favorites = menu_bar.addMenu("Favorites")

    menu_help = menu_bar.addMenu(QCoreApplication.translate("GeoApt", "Help"))
    help_about_action = QAction(QCoreApplication.translate("GeoApt", "About GeoApt"), self)
    self.connect(help_about_action, SIGNAL("triggered()"), self.help_about)
    menu_help.addAction(help_about_action)
    # On OS X add another entry under the help menu (same content as Help|About)
    if sys.platform == 'darwin':
      help_info_action = QAction(QCoreApplication.translate("GeoApt", "About GeoApt"), self)
      self.connect(help_info_action, SIGNAL("triggered()"), self.help_about)
      menu_help.addAction(help_info_action)

    



    # Create the map toolbar
    self.toolbar = self.addToolBar(QCoreApplication.translate("GeoApt", "Map"))
    # Add the map actions to the toolbar
    self.toolbar.addAction(self.action_zoomin)
    self.toolbar.addAction(self.action_zoomout)
    self.toolbar.addAction(self.action_pan)
    self.toolbar.addAction(self.action_zoomfull)
    self.toolbar.addAction(self.action_metadata)

    # Create the map tools
    self.tool_pan = QgsMapToolPan(self.canvas)
    self.tool_zoomin = QgsMapToolZoom(self.canvas, False) # false = in
    self.tool_zoomout = QgsMapToolZoom(self.canvas, True) # true = out

    # Create the favorites/file management toolbar
    self.file_toolbar = self.addToolBar(QCoreApplication.translate("GeoApt", "File"))
    self.history_combobox = QComboBox()
    self.connect(self.history_combobox, SIGNAL("currentIndexChanged(const QString&)"), self.setFolder)
    self.history_combobox.setMinimumWidth(280)
    self.history_combobox.setEditable(True)
    # label for the combo
    self.history_label = QLabel()
    self.history_label.setText(QCoreApplication.translate("GeoApt", 'Directories:'))
    self.file_toolbar.addWidget(self.history_label)
    
    self.file_toolbar.addWidget(self.history_combobox)
    self.file_toolbar.addAction(self.action_open_folder)

    # Create the database management toolbar
    #self.databaseToolbar = self.addToolBar("Database")
    #self.databaseCombo = QComboBox()
    #self.connect(self.databaseCombo, SIGNAL("currentIndexChanged(const QString&)"), self.setDatabase)
    #self.databaseCombo.setMinimumWidth(180)
    ## label for the combo
    #self.databaseLabel = QLabel()
    #self.databaseLabel.setText('Databases:')
    #self.databaseToolbar.addWidget(self.databaseLabel)
    #self.databaseToolbar.addWidget(self.databaseCombo)

    # set the default tree path
    self.treeview.setRootIndex(self.model.index(self.root));

    #TODO: restore the history list from settings file
    # add it to the drop down
    QCoreApplication.setOrganizationName("MicroResources")
    QCoreApplication.setOrganizationDomain("geoapt.com")
    QCoreApplication.setApplicationName("GeoApt")
    settings = QSettings()
    history_list = settings.value('history/folders').toList()
    for folder in history_list:
        self.history_combobox.addItem(folder.toString())

    if self.history_combobox.findText(self.root) == -1:
      self.history_combobox.addItem(self.root)
    # resize the name column to contents
    self.treeview.resizeColumnToContents(0)

    self.move(100,100)
    self.show()
    self.init_database()
    self.restore_themes()

    # set up drag
    #self.treeview.__class__.dragEnterEvent = self.tvDragEnterEvent



    ## end __init__
  def init_database(self):
    # Init the sqlite database for theme management
    self.db_base_path = os.path.join(os.environ['HOME'],'.geoapt')
    self.dbname = os.path.join(self.db_base_path,"geoapt.db")
    #print QCoreApplication.translate("GeoApt", "Opening sqlite3 database %s\n") % self.dbname
    if not os.path.exists(self.dbname):
        # create the storage directory
        if not os.path.exists(self.db_base_path):
            os.mkdir(self.db_base_path)
        self.db = sqlite3.connect(self.dbname)
        # create the database schema
        #print QCoreApplication.translate("GeoApt", "Initializing database schema for theme storage")
        ThemeDatabase.create_schema(self.db)
        QMessageBox.information(self, QCoreApplication.translate("GeoApt", "Theme Database"),QCoreApplication.translate("GeoApt", "A new theme database has been created.\nThis happens the first time you run the application or\nif your theme database has been moved or deleted.\n\nYour theme database can be found at:\n") + self.dbname)
    else: 
         self.db = sqlite3.connect(self.dbname)

        #self.db.close()
    # Check to see if we have a qgis.db (needed for displaying data or the qgis libs assert and crash
    # geoapt
    qgis_db_path = str(QgsApplication.qgisUserDbFilePath())
    qgis_db_base_path = os.path.dirname(qgis_db_path)
    if not os.path.exists(qgis_db_path):
        # create an empty database
        if not os.path.exists(qgis_db_base_path):
            os.mkdir(qgis_db_base_path)
        qgis_db = sqlite3.connect(qgis_db_path)
        QMessageBox.information(self, QCoreApplication.translate("GeoApt", "Spatial Reference Database"),QCoreApplication.translate("GeoApt", "A new spatial reference (SRS) database has been created.\nThis happens the first time you run the application if you don't have QGIS installed.\n\nThe SRS database can be found at:\n") + qgis_db_path)


  def restore_themes(self):
      # get the dict of theme folders and associated themes
      folders = ThemeDatabase.folder_list(self.db)
      themes = ThemeDatabase.theme_list(self.db)
      for folder in folders:
        string_list = QStringList()
        string_list << folder.name
        string_list << str(folder.id)
        new_folder = QTreeWidgetItem(self.theme_tree, string_list)
        # set folders to be non-draggable
        new_folder.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        # get the folders subitems
        child_themes = themes[folder.id]
        for theme in child_themes:
            theme_strings = QStringList()
            theme_strings << theme.name
            theme_strings << theme.path
            theme_strings << str(theme.id)
            new_item = QTreeWidgetItem(new_folder, theme_strings)
            #new_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
        #self.theme_tree.insertTopLevelItems(string_list)



  # Set the map tool to zoom in
  def zoomIn(self):
    self.canvas.setMapTool(self.tool_zoomin)

  # Set the map tool to zoom out
  def zoomOut(self):
    self.canvas.setMapTool(self.tool_zoomout)

  # Set the map tool to 
  def pan(self):
    self.canvas.setMapTool(self.tool_pan)

  # Zoom to full extent of layer
  def zoomFull(self):
    self.canvas.zoomToFullExtent()

  def show_theme(self, item, column):
      if item.parent() is None:
          print "Clicked folder---can't render it"
      else:
          print "Theme clicked is %s" % item.data(0, Qt.DisplayRole).toString()
          print "Theme path is %s" % item.data(1, Qt.DisplayRole).toString()
          self.statusBar().showMessage(item.data(1, Qt.DisplayRole).toString())
          self.render_layer(item.data(1, Qt.DisplayRole).toString(), item.data(0, Qt.DisplayRole).toString())
      
  def showData(self, index):
    #treeview.setPath(self.model.filePath(index))

    # show path in status bar
    self.statusBar().showMessage(self.model.filePath(index))

    # we need to determine what kind of data to determine
    # the provider to use
    if self.model.isDir(index):
        # set the name of the dir in the status bar
        print "user selected ", self.model.filePath(index)
    else:
        self.render_layer(self.model.filePath(index), self.model.fileName(index))

  def render_layer(self, path, layer_name):
      print "Rendering %s" % path
      # get the extension
      file_info = QFileInfo(path)
      suffix = file_info.suffix()
      # determine layer type
      if str(suffix).lower() in self.supported_rasters:
        # add the raster layer
        self.layer = QgsRasterLayer(path, layer_name)
        # Add layer to the registry
        QgsMapLayerRegistry.instance().addMapLayer(self.layer);

        # Set extent to the extent of our layer
        self.canvas.setExtent(self.layer.extent())

        # Set up the map canvas layer set
        cl = QgsMapCanvasLayer(self.layer)
        layers = [cl]
        self.canvas.setLayerSet(layers)
      else:
        if str(suffix).lower() in self.supported_vectors:
          # Add the layer
          self.layer = QgsVectorLayer(path, layer_name, "ogr")

          if not self.layer.isValid():
            QMessageBox.warning(self, "Themes","QGIS engine says %s is not valid" % layer_name)
            return

          # Change the color of the layer to gray
          symbols = self.layer.renderer().symbols()
          symbol = symbols[0]
          symbol.setFillColor(QColor.fromRgb(192,192,192))

          # Add layer to the registry
          QgsMapLayerRegistry.instance().addMapLayer(self.layer);

          # Set extent to the extent of our layer
          self.canvas.setExtent(self.layer.extent())

          # Set up the map canvas layer set
          cl = QgsMapCanvasLayer(self.layer)
          layers = [cl]
          self.canvas.setLayerSet(layers)
          print "setting qgis prefix to ", qgis_prefix
        else:
          print "unsupported file type"
      # update the metadata dock if it exists
      if self.dockVisibility:
        self.metadata() 

  def setTreeRoot(root):
    self.root = root

  #def tvDragEnterEvent(event):
    #event.accept(QTextDrag.canDecode(event))

  #def tvDragObject():
  #  drag = QxxxextDrag(self)
  #  mimeData = QMimeData()
  #  self.path = "foo"
  #  mimeData.setData("text/plain", self.path)
  #  drag.setMimeData(mimeData)
  #  booga
  #  #drag.exec_()
  #  return drag

  #def mousePressEvent(event):
  #  if (event.button() == Qt.LeftButton & self.treeview.geometry().contains(event.pos())): 
  #    self.tvDragObject()
  
  def openFolder(self):
    folder = QFileDialog.getExistingDirectory()
    self.setFolder(folder)
    
  def setFolder(self, folder):
    self.treeview.setRootIndex(self.model.index(folder))
    self.statusBar().showMessage(folder)
    # set the column width to contents for the name
    self.treeview.resizeColumnToContents(0)
    # add the folder to the drop-down list
    if self.history_combobox.findText(folder) == -1:
      self.history_combobox.addItem(folder)
      # store it to the preferences


  def setDatabase(self, database):
      pass

  def metadata(self):
    # show the metadata for the active layer
    print "Layer type is: ", self.layer.type()
    print "dock viz is: ", self.dockVisibility
    if(self.layer.type() == QgsMapLayer.RasterLayer): 
      metadata = self.layer.metadata()
    else:
      metadata = self.getVectorMetadata()
    #print metadata
    # create the metadata doc
    #if not self.dockVisibility:
    dock = QDockWidget("Metadata for " + self.layer.name(), self)
    # figure out where to put the floating dock
    geometry = self.geometry()
    dockLeft = geometry.left() + ((geometry.right() - geometry.left())/2 - 320/2)
    #dock.setMinimumSize(320,400)
    dock.setGeometry(dockLeft, geometry.top()+22, 320, 400)
    #dockVisibility = True
      # connect up the visibility slot
      #self.connect(dock, SIGNAL("visibilityChanged(bool)"), self.dockVisibilityChanged)
      #self.connect(dock, SIGNAL("destroyed()"), self.dockDestroyed)
    self.content = QTextEdit(metadata, dock)
    dock.setWidget(self.content)
    self.addDockWidget(Qt.RightDockWidgetArea, dock)
    dock.setFloating(True)

  def getVectorMetadata(self):
    myMetadataQString = "<html><body>"
    myMetadataQString += "<table width='100%'>"
    myMetadataQString += "<tr><td bgcolor='lightgray'>"
    myMetadataQString += "<b>General:</b>"
    myMetadataQString += "</td></tr>"

    # data comment
    if not self.layer.dataComment().isEmpty():
      myMetadataQString += "<tr><td bgcolor='white'>"
      myMetadataQString += "<b> Layer comment:</b> " + self.layer.dataComment()
      myMetadataQString += "</td></tr>"

    # storage type
    myMetadataQString += "<tr><td bgcolor='white'>"
    myMetadataQString += "<b> Storage type:</b> " + self.layer.storageType()
    myMetadataQString += "</td></tr>"

    # data source
    myMetadataQString += "<tr><td bgcolor='white'>"
    myMetadataQString += "<b> Source:</b> " + self.layer.publicSource()
    myMetadataQString += "</td></tr>"

    #geom type

    vectorType = self.layer.type()

    if ( vectorType < 0 or vectorType > QGis.Polygon ):
      print "Invalid vector type" 
    else:
      vectorTypeString = self.vector_geometry_types[self.layer.type()] 
      myMetadataQString += "<tr><td bgcolor='white'>"
      myMetadataQString += "<b> Geometry type:</b> " + vectorTypeString
      myMetadataQString += "</td></tr>"


    # feature count
    myMetadataQString += "<tr><td bgcolor='white'>"
    myMetadataQString += "<b>Number of features:</b> " + str(self.layer.featureCount())
    myMetadataQString += "</td></tr>"
    #capabilities
    myMetadataQString += "<tr><td bgcolor='white'>"
    myMetadataQString += "<b>Editing capabilities:</b> " + self.layer.capabilitiesString()
    myMetadataQString += "</td></tr>"
    myExtent = self.layer.extent()  
    myMetadataQString += "<tr><td bgcolor='lightgray'>"
    myMetadataQString += "<b>Extents:</b>"
    myMetadataQString += "</td></tr>"
    # extents in layer cs  TODO...maybe make a little nested table to improve layout...
    myMetadataQString += "<tr><td bgcolor='white'>"
    myMetadataQString += "<b>In layer SRS units:</b><br>xMin,yMin :" 
    myMetadataQString += str(myExtent.xMinimum()) + ", " + str( myExtent.yMinimum()) + "<br>xMax,yMax :" 
    myMetadataQString += str(myExtent.xMaximum()) + ", " + str(myExtent.yMaximum())
    myMetadataQString += "</td></tr>"
    # Add the info about each field in the attribute table
    myMetadataQString += "<tr><td bgcolor='lightgray'>"
    myMetadataQString += "<b>Attribute field info:</b>"
    myMetadataQString += "</td></tr>"
    myMetadataQString += "<tr><td bgcolor='white'>"

    # Start a nested table in this trow
    myMetadataQString += "<table width='100%'>"
    myMetadataQString += "<tr><th bgcolor='black'>"
    myMetadataQString += "<font color='white'>" + "Field" + "</font>"
    myMetadataQString += "</th>"
    myMetadataQString += "<th bgcolor='black'>"
    myMetadataQString += "<font color='white'>" + "Type" + "</font>"
    myMetadataQString += "</th>"
    myMetadataQString += "<th bgcolor='black'>"
    myMetadataQString += "<font color='white'>" + "Length" + "</font>"
    myMetadataQString += "</th>"
    myMetadataQString += "<th bgcolor='black'>"
    myMetadataQString += "<font color='white'>" + "Precision" + "</font>"
    myMetadataQString += "</th>";      
    myMetadataQString += "<th bgcolor='black'>"
    myMetadataQString += "<font color='white'>" + "Comment" + "</font>"
    myMetadataQString += "</th>"
 
#  //get info for each field by looping through them
    myDataProvider = self.layer.dataProvider()
    myFields = myDataProvider.fields()
    for fld in myFields:
      print "fld is: " , fld
      myMetadataQString += "<tr><td bgcolor='white'>"
      myMetadataQString += myFields[fld].name()
      myMetadataQString += "</td>"
      myMetadataQString += "<td bgcolor='white'>"
      myMetadataQString += myFields[fld].typeName()
      myMetadataQString += "</td>"
      myMetadataQString += "<td bgcolor='white'>"
      myMetadataQString += str(myFields[fld].length())
      myMetadataQString += "</td>"
      myMetadataQString += "<td bgcolor='white'>"
      myMetadataQString += str(myFields[fld].precision())
      myMetadataQString += "</td>"
      myMetadataQString += "<td bgcolor='white'>"
      myMetadataQString += str(myFields[fld].comment())
      myMetadataQString += "</td></tr>"
#  } 
#
    # close field list
    myMetadataQString += "</table>"; #end of nested table
    # Display layer spatial ref system
    myMetadataQString += "<tr><td bgcolor='lightgray'>"
    myMetadataQString += "<b>Spatial Reference System:</b>"
    myMetadataQString += "</td></tr>";  
    myMetadataQString += "<tr><td bgcolor='white'>"
    myMetadataQString += self.layer.srs().toProj4().replace(QRegExp("\"")," \"")
    myMetadataQString += "</td></tr>";

    myMetadataQString += "</td></tr>"; #end of stats container table row
  
    # Close the table
    myMetadataQString += "</table>"
    myMetadataQString += "</body></html>"
    return myMetadataQString

  def dockVisibilityChanged(self, viz):
    self.dockVisibility = viz
    print "changed dock visibility to", viz

  def dockDestroyed(self):
    self.dockVisibility = False
    print "dock destroyed"

  def theme_tree_popup(self, pos):
    print "parent of right-click item is %s" % self.theme_tree.currentItem().parent()
    if self.theme_tree.currentItem().parent() is None:
        index = self.theme_tree.indexAt(pos)
        if not index.isValid(): 
            return 
        print "Index type is %s" % type(index)
        print index.data().toString()
        name = index.data().toString()
        id = index.data(Qt.UserRole +1).toInt()
        print "Type of id is %s" % type(id)
        print "Caught mouse event for context menu for %s" % name
        print "Caught mouse event for context menu for id" , id[0]

        print "Pos type is %s" % type(pos)
        print "Pos is ", pos
        self.current_theme = Theme(id[0], name)
        self.current_index = index
        pop_menu = QMenu()
        pop_add = QAction("Add theme...",pop_menu)
        self.connect(pop_add, SIGNAL("triggered()"), self.add_new_theme)
        pop_menu.addAction(pop_add)
        pop_menu.exec_(self.theme_tree.mapToGlobal(pos), pop_add)



  def new_theme_folder(self):
    add_theme_folder = AddThemeFolder()
    if add_theme_folder.exec_() == QDialog.Accepted:
        #QMessageBox.information(self, "Themes","Will now add a theme folder: %s" % add_theme_folder.folder_name.text())    
        folder_name = add_theme_folder.folder_name.text()
        if len(folder_name) > 0:
            # add to the database
            id = ThemeDatabase.add_folder(self.db, folder_name)
            print "Setting id for new folder to %i" % id
            new_folder = QStringList()
            new_folder << folder_name
            new_folder << str(id)
            QTreeWidgetItem(self.theme_tree, new_folder)
            self.theme_tree.sortItems(0, Qt.AscendingOrder)

  def add_new_theme(self):
      print "adding new theme to folder %s with id %i\n" % (self.current_theme.name, self.current_theme.id)
      print type(self.current_theme)
      add_theme = AddTheme()
      add_theme.label_folder_name.setText(self.current_theme.name)
      if add_theme.exec_() == QDialog.Accepted:
          theme_name = add_theme.led_theme_name.text()
          theme_path = add_theme.led_path_name.text()
          if len(theme_name) > 0:
              # get the current item
              current_item = self.theme_tree.currentItem()
              parent_id = current_item.data(1, Qt.DisplayRole)
              print "ID for parent is %i" %  parent_id.toInt()[0]
              id = ThemeDatabase.add_theme(self.db, theme_name, theme_path, parent_id.toInt()[0])
              string_list = QStringList()
              string_list << theme_name
              string_list << theme_path
              string_list << str(id)
              new_theme = QTreeWidgetItem(self.theme_tree.currentItem(), string_list)





  def new_theme(self):
    QMessageBox.information(self, "Themes","Add new theme")    

  def last_window_closed(self):
      # Main window was closed by user click -- cleanup up
    print "Cleaning up...\n"
    self.db.close()
    # set the database connection to None so Qt cleans up the connection properly
    self.db = None
    # save the directory list
    QCoreApplication.setOrganizationName("MicroResources")
    QCoreApplication.setOrganizationDomain("geoapt.com")
    QCoreApplication.setApplicationName("GeoApt")
    settings = QSettings()
    history_list = list()
    for i in range(self.history_combobox.count()):
        print "adding %s to the history list" % self.history_combobox.itemText(i)
        history_list.append(self.history_combobox.itemText(i))

    settings.setValue('history/folders', history_list)
    #pyqtRemoveInputHook()
    #pdb.set_trace()
    
    #QSqlDatabase.removeDatabase(self.dbname) 
  def exit_gndb(self):
    QApplication.closeAllWindows()

  def raster_extensions(self):
    # get the list of supported raster types from the GDAL drivers
    self.driver_list = list()
    self.driver_list_description = list()
    # iterate through the GDAL drivers and get the supported extension list
    for d in range(0, gdal.GetDriverCount()):
      driver = gdal.GetDriver(d)
      metadata = driver.GetMetadata()
      if metadata.has_key('DMD_EXTENSION'):
          self.driver_list.append(metadata['DMD_EXTENSION'])
          self.driver_list_description.append(metadata['DMD_LONGNAME'])
    
    self.driver_list_description.sort()
    return self.driver_list

  def help_about(self):
    about = AboutGeoApt()
    # Set general info in the About tab
    about.textBrowser.setText("""<h2>GeoApt</h2>
                              Version %s""" % geoapt_version.VERSION)
    about.textBrowser.append("GeoApt is a geospatial data browser and theme catalog written in Python using the QGIS libraries.")
    about.textBrowser.append("<p>Copyright (C) 2010 Gary Sherman</p>")
    about.textBrowser.append("<p>All code is licensed under the GNU GPL version 2.</p>")
    about.textBrowser.append("Your theme database is located at: %s" % self.dbname)

    # Set raster info in the Raster tab
    about.textBrowser_raster.setText("""<h3>Supported Raster Formats</h3>
                             <ul>
                             <li>%s""" % "<li>".join(self.supported_rasters))
    if not have_osgeo: 
        about.textBrowser_raster.append("""**The GDAL Python bindings were not found.
        The list of supported rasters has been set to a minimum.""")

    # Set vector info in the Vector tab
    about.textBrowser_vector.setText("""<h3>Supported Vector Formats</h3>
                              <ul>
                              <li>%s""" % "<li>".join(self.supported_vectors))
    # list the data providers
    provider_instance = QgsProviderRegistry.instance()
    
    #about.textBrowser_vector.append("<b>Data Providers</b>: %s" % provider_instance.pluginList())
    #vector_filters = provider_instance.fileVectorFilters()
    #filter_array = vector_filters.split(';;')
    #about.textBrowser_vector.append(provider_instance.fileVectorFilters())
    #provider_list = provider_instance.providerList()
    #about.textBrowser_vector.append("PROVIDERS")
    #for p in provider_list:
        #about.textBrowser_vector.append(p)

    # show the about dialog
    about.exec_()

      #QMessageBox.information(self, QCoreApplication.translate("GeoApt", "About"), QCoreApplication.translate("GeoApt", "GeoApt Geospatial Data Browser") + geoapt_version.VERSION + "\n" + geoapt_version.COPYRIGHT + "\n" + geoapt_version.WEBSITE)




def main(argv):
  # create Qt application
  app = QApplication(argv)

  # Initialize qgis libraries
  QgsApplication.setPrefixPath(qgis_prefix, True)
  print "Set PrefixPath to %s" % qgis_prefix
  #QgsApplication.setPrefixPath(app.applicationDirPath(), True)
  QgsApplication.initQgis()

  provider_inst = QgsProviderRegistry.instance()
  print provider_inst.pluginList()
  print QgsApplication.showSettings()

  # create main window
  wnd = MainWindow()
  # Move the app window to upper left
  #wnd.move(100,100)
  #wnd.show()
  #wnd.init_database()

  # run!
  retval = app.exec_()

  # exit
  wnd.last_window_closed()

  #QgsApplication.exitQgis()
  sys.exit(retval)


if __name__ == "__main__":
  main(sys.argv)

