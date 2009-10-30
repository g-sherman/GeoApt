#!/usr/bin/env python
# Main window implementation for the data browser
# Copyright (C) 2009 Gary Sherman
# Licensed under the terms of GNU GPL 2

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import sys
import os
# Import our GUI tree->setRootIndex(model->index(QDir::currentPath()));
from mainwindow_ui import Ui_MainWindow
#from qgstreeview import QgsTreeView
# Import our resources (icons)
import resources

# Environment variable QGISHOME must be set to the 1.0.x install directory
# before running this application
qgis_prefix = os.getenv("QGISHOME")

class MainWindow(QMainWindow, Ui_MainWindow):

  def __init__(self):
    self.supported_rasters = 'tif', 'jpg', 'png', 'vrt'
    self.supported_vectors = 'shp', 'tab'
    self.vector_geometry_types = ['Point', 'Line', 'Polygon']
    self.root = os.getenv("HOME")
    self.dockVisibility = False
    
    QMainWindow.__init__(self)

    # Required by Qt4 to initialize the UI
    self.setupUi(self)

    # Set the title for the app
    self.setWindowTitle("GeoNibble Data Browser")

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
    for filt in self.model.nameFilters():
      print filt

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

    self.tabWidget = QTabWidget()
    self.tabWidget.addTab(self.treeview, "Directories")
    self.dataFrame = QFrame()
    self.tabWidget.addTab(self.dataFrame, "Databases")

    self.splitter.addWidget(self.tabWidget)


    #self.splitter.addWidget(self.treeview)
    self.splitter.addWidget(self.canvas)
    #self.model.refresh
    #self.layout.addWidget(self.splitter)

    # make the connections for the treeview
    self.connect(self.treeview, SIGNAL("doubleClicked(const QModelIndex&)"), self.showData)
    self.connect(self.treeview, SIGNAL("clicked(const QModelIndex&)"), self.showData)

    # set up the actions
    self.actionZoomIn = QAction(QIcon(":/qgisbrowser/mActionZoomIn.png"), \
        "Zoom In", self.frame)
    self.connect(self.actionZoomIn, SIGNAL("activated()"), self.zoomIn)
    self.actionZoomOut = QAction(QIcon(":/qgisbrowser/mActionZoomOut.png"), \
        "Zoom Out", self.frame)
    self.connect(self.actionZoomOut, SIGNAL("activated()"), self.zoomOut)
    self.actionPan = QAction(QIcon(":/qgisbrowser/mActionPan.png"), \
        "Pan", self.frame)
    self.connect(self.actionPan, SIGNAL("activated()"), self.pan)
    self.actionZoomFull = QAction(QIcon(":/qgisbrowser/mActionZoomFullExtent.png"), \
        "Zoom Full Extent", self.frame)
    self.connect(self.actionZoomFull, SIGNAL("activated()"), self.zoomFull)

    self.actionMetadata = QAction(QIcon(":/qgisbrowser/mActionMetadata.png"), \
        "Properties", self.frame)
    self.connect(self.actionMetadata, SIGNAL("activated()"), self.metadata)

    self.actionOpenFolder = QAction(QIcon(":/qgisbrowser/mActionOpenFolder.png"), \
        "Open Folder", self.frame)
    self.connect(self.actionOpenFolder, SIGNAL("activated()"), self.openFolder)

    # Create the map toolbar
    self.toolbar = self.addToolBar("Map")
    # Add the map actions to the toolbar
    self.toolbar.addAction(self.actionZoomIn)
    self.toolbar.addAction(self.actionZoomOut)
    self.toolbar.addAction(self.actionPan)
    self.toolbar.addAction(self.actionZoomFull)
    self.toolbar.addAction(self.actionMetadata)

    # Create the map tools
    self.toolPan = QgsMapToolPan(self.canvas)
    self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
    self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out

    # Create the favorites/file management toolbar
    self.fileToolbar = self.addToolBar("File")
    self.historyCombo = QComboBox()
    self.connect(self.historyCombo, SIGNAL("currentIndexChanged(const QString&)"), self.setFolder)
    self.historyCombo.setMinimumWidth(180)
    # label for the combo
    self.historyLabel = QLabel()
    self.historyLabel.setText('Directories:')
    self.fileToolbar.addWidget(self.historyLabel)
    
    self.fileToolbar.addWidget(self.historyCombo)
    self.fileToolbar.addAction(self.actionOpenFolder)

    # Create the database management toolbar
    self.databaseToolbar = self.addToolBar("Database")
    self.databaseCombo = QComboBox()
    self.connect(self.databaseCombo, SIGNAL("currentIndexChanged(const QString&)"), self.setDatabase)
    self.databaseCombo.setMinimumWidth(180)
    # label for the combo
    self.databaseLabel = QLabel()
    self.databaseLabel.setText('Databases:')
    self.databaseToolbar.addWidget(self.databaseLabel)
    self.databaseToolbar.addWidget(self.databaseCombo)

    # set the default tree path
    self.treeview.setRootIndex(self.model.index(self.root));

    #TODO: restore the history list from settings file
    # add it to the drop down
    if self.historyCombo.findText(self.root) == -1:
      self.historyCombo.addItem(self.root)
    # resize the name column to contents
    self.treeview.resizeColumnToContents(0)

    # set up drag
    #self.treeview.__class__.dragEnterEvent = self.tvDragEnterEvent

    ## end __init__

  # Set the map tool to zoom in
  def zoomIn(self):
    self.canvas.setMapTool(self.toolZoomIn)

  # Set the map tool to zoom out
  def zoomOut(self):
    self.canvas.setMapTool(self.toolZoomOut)

  # Set the map tool to 
  def pan(self):
    self.canvas.setMapTool(self.toolPan)

  # Zoom to full extent of layer
  def zoomFull(self):
    self.canvas.zoomToFullExtent()


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

      print self.model.filePath(index),self.model.fileName(index)
      # get the extension
      file_info = QFileInfo(self.model.fileName(index))
      suffix = file_info.suffix()
      # determine layer type
      if str(suffix).lower() in self.supported_rasters:
        # add the raster layer
        self.layer = QgsRasterLayer(self.model.filePath(index), self.model.fileName(index))
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
          self.layer = QgsVectorLayer(self.model.filePath(index), self.model.fileName(index), "ogr")

          if not self.layer.isValid():
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
    if self.historyCombo.findText(folder) == -1:
      self.historyCombo.addItem(folder)

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
    myMetadataQString += "<table width=\"100%\">"
    myMetadataQString += "<tr><td bgcolor=\"lightgray\">"
    myMetadataQString += "<b>General:</b>"
    myMetadataQString += "</td></tr>"

    # data comment
    if not self.layer.dataComment().isEmpty():
      myMetadataQString += "<tr><td bgcolor=\"white\">"
      myMetadataQString += "<b> Layer comment:</b> " + self.layer.dataComment()
      myMetadataQString += "</td></tr>"

    # storage type
    myMetadataQString += "<tr><td bgcolor=\"white\">"
    myMetadataQString += "<b> Storage type:</b> " + self.layer.storageType()
    myMetadataQString += "</td></tr>"

    # data source
    myMetadataQString += "<tr><td bgcolor=\"white\">"
    myMetadataQString += "<b> Source:</b> " + self.layer.publicSource()
    myMetadataQString += "</td></tr>"

    #geom type

    vectorType = self.layer.type()

    if ( vectorType < 0 or vectorType > QGis.Polygon ):
      print "Invalid vector type" 
    else:
      vectorTypeString = self.vector_geometry_types[self.layer.type()] 
      myMetadataQString += "<tr><td bgcolor=\"white\">"
      myMetadataQString += "<b> Geometry type:</b> " + vectorTypeString
      myMetadataQString += "</td></tr>"


    # feature count
    myMetadataQString += "<tr><td bgcolor=\"white\">"
    myMetadataQString += "<b>Number of features:</b> " + str(self.layer.featureCount())
    myMetadataQString += "</td></tr>"
    #capabilities
    myMetadataQString += "<tr><td bgcolor=\"white\">"
    myMetadataQString += "<b>Editing capabilities:</b> " + self.layer.capabilitiesString()
    myMetadataQString += "</td></tr>"
    myExtent = self.layer.extent()  
    myMetadataQString += "<tr><td bgcolor=\"lightgray\">"
    myMetadataQString += "<b>Extents:</b>"
    myMetadataQString += "</td></tr>"
    # extents in layer cs  TODO...maybe make a little nested table to improve layout...
    myMetadataQString += "<tr><td bgcolor=\"white\">"
    myMetadataQString += "<b>In layer SRS units:</b><br>xMin,yMin :" 
    myMetadataQString += str(myExtent.xMinimum()) + ", " + str( myExtent.yMinimum()) + "<br>xMax,yMax :" 
    myMetadataQString += str(myExtent.xMaximum()) + ", " + str(myExtent.yMaximum())
    myMetadataQString += "</td></tr>"
    # Add the info about each field in the attribute table
    myMetadataQString += "<tr><td bgcolor=\"lightgray\">"
    myMetadataQString += "<b>Attribute field info:</b>"
    myMetadataQString += "</td></tr>"
    myMetadataQString += "<tr><td bgcolor=\"white\">"

    # Start a nested table in this trow
    myMetadataQString += "<table width=\"100%\">"
    myMetadataQString += "<tr><th bgcolor=\"black\">"
    myMetadataQString += "<font color=\"white\">" + "Field" + "</font>"
    myMetadataQString += "</th>"
    myMetadataQString += "<th bgcolor=\"black\">"
    myMetadataQString += "<font color=\"white\">" + "Type" + "</font>"
    myMetadataQString += "</th>"
    myMetadataQString += "<th bgcolor=\"black\">"
    myMetadataQString += "<font color=\"white\">" + "Length" + "</font>"
    myMetadataQString += "</th>"
    myMetadataQString += "<th bgcolor=\"black\">"
    myMetadataQString += "<font color=\"white\">" + "Precision" + "</font>"
    myMetadataQString += "</th>";      
    myMetadataQString += "<th bgcolor=\"black\">"
    myMetadataQString += "<font color=\"white\">" + "Comment" + "</font>"
    myMetadataQString += "</th>"
 
#  //get info for each field by looping through them
    myDataProvider = self.layer.dataProvider()
    myFields = myDataProvider.fields()
    for fld in myFields:
      print "fld is: " , fld
      myMetadataQString += "<tr><td bgcolor=\"white\">"
      myMetadataQString += myFields[fld].name()
      myMetadataQString += "</td>"
      myMetadataQString += "<td bgcolor=\"white\">"
      myMetadataQString += myFields[fld].typeName()
      myMetadataQString += "</td>"
      myMetadataQString += "<td bgcolor=\"white\">"
      myMetadataQString += str(myFields[fld].length())
      myMetadataQString += "</td>"
      myMetadataQString += "<td bgcolor=\"white\">"
      myMetadataQString += str(myFields[fld].precision())
      myMetadataQString += "</td>"
      myMetadataQString += "<td bgcolor=\"white\">"
      myMetadataQString += str(myFields[fld].comment())
      myMetadataQString += "</td></tr>"
#  } 
#
    # close field list
    myMetadataQString += "</table>"; #end of nested table


    # Display layer spatial ref system
    myMetadataQString += "<tr><td bgcolor=\"lightgray\">"
    myMetadataQString += "<b>Spatial Reference System:</b>"
    myMetadataQString += "</td></tr>";  
    myMetadataQString += "<tr><td bgcolor=\"white\">"
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



def main(argv):
  # create Qt application
  app = QApplication(argv)

  # Initialize qgis libraries
  QgsApplication.setPrefixPath(qgis_prefix, True)
  #QgsApplication.setPrefixPath(app.applicationDirPath(), True)
  QgsApplication.initQgis()

  # create main window
  wnd = MainWindow()
  # Move the app window to upper left
  wnd.move(100,100)
  wnd.show()

  # run!
  retval = app.exec_()

  # exit
  #QgsApplication.exitQgis()
  sys.exit(retval)


if __name__ == "__main__":
  main(sys.argv)

