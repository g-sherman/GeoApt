#!/usr/bin/env python
# Sample directory view 
# Copyright (C) 2008 Gary Sherman
# Licensed under the GNU GPL Version 2

# PyQt4 includes for python bindings to QT
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# General system includes
import sys


# Main entry to program.
def main(argv):

  # create Qt application
  app = QApplication(argv,True)
  
  # Set the app style
  app.setStyle(QString("plastique"))
  
  model = QDirModel()
  tree = QTreeView()
  tree.setModel(model);
  
  tree.setWindowTitle("Dir View");
  tree.resize(640, 480);
  tree.show();

  # Create signal for app finish
  app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))
  
  # Start the app up
  retval = app.exec_()
  
  sys.exit(retval)


if __name__ == "__main__":
  main(sys.argv)
