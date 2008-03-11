#!/usr/bin/env python
# Loosely based on:
#   Original C++ Tutorial 2 by Tim Sutton, ported to Python by Martin Dobias
#   with modifications and enhancements by Gary Sherman for FOSS4G2007
# Licensed under the terms of GNU GPL 2
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from qgis.core import *
#from qgis.gui import *
import sys
import os
# Import our GUI tree->setRootIndex(model->index(QDir::currentPath()));
from droptarget_ui import Ui_MainWindow
# Import our resources (icons)
import resources

# Environment variable QGISHOME must be set to the 0.9 install directory
# before running this application
qgis_prefix = os.getenv("QGISHOME")

class DropTarget(QMainWindow, Ui_MainWindow):

  def __init__(self):
    
    QMainWindow.__init__(self)

    # Required by Qt4 to initialize the UI
    self.setupUi(self)

    # Set the title for the app
    self.setWindowTitle("Drop Target")

    # enable drop
    self.setAcceptDrops(True)

  def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
      fmts = event.mimeData().formats()
      for f in fmts:
        print f
      urls = event.mimeData().urls()
      for u in urls:
        print u.toString()
      event.acceptProposedAction()
    

  def dropEvent(self, event):
    urls = event.mimeData().urls()
    for u in urls:
      print u.toString()
      self.textEdit.setPlainText(u.path())
    event.acceptProposedAction();
 

def main(argv):
  # create Qt application
  app = QApplication(argv)

  # Initialize qgis libraries
  #QgsApplication.setPrefixPath(qgis_prefix, True)
  #QgsApplication.initQgis()

  # create main window
  wnd = DropTarget()
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

