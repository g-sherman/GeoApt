# Tree view class for the data browser
# Copyright (C) 2008 Gary Sherman
# Licensed under the terms of GNU GPL 2
from PyQt4.QtCore import *
from PyQt4.QtGui import *
class QgsTreeView(QTreeView):
    """TreeView class for GeoApt."""
    def __init__(self):
        """Setup the tree view and enable drag."""
        QTreeView.__init__(self)
        self.setDragEnabled(True)

    def mouseMoveEvent(self,event):
        """Process a mouse move event and drag/drop as appropriate."""
        print "event position:", event.pos().x(), event.pos().y()
        print "dragStartPosition:", self.dragStartPosition.x(), self.dragStartPosition.y()
        print "mouseMoveEvent"
        if (not(event.buttons() & Qt.LeftButton)):
            print "not(event.buttons() & Qt.LeftButton) - returned"
            return

        print "Creating drag object"

        drag = QDrag(self)
        mimeData = QMimeData()
        self.path = "foo"
        mimeData.setData("text/plain", self.path)
        drag.setMimeData(mimeData)

        dropAction = drag.exec_(self, Qt.CopyAction | Qt.MoveAction)

    def mousePressEvent(self,event):
        """Process a mouse press event on the tree view."""
        print "mousePressEvent"
        if event.button() == Qt.LeftButton:
            print "setting drag start position"
            self.dragStartPosition = event.pos()
        else:
            TreeView.mousePressEvent(self,event)

    def setPath(path):
        """Set the current path."""
        self.path = path
