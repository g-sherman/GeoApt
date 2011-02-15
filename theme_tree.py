# Copyright (C) 2008-2011 Gary Sherman
# Licensed under the terms of GNU GPL 2
from PyQt4.QtGui import *
from PyQt4.QtCore import *
class ThemeTree(QTreeWidget):
    """Subclassed QTreeWidget to provide drag and drop."""
    def __init__(self):
        QTreeWidget.__init__(self)

    def mousePressEvent(self, event):
        """Process mouse event, looking for a left button click."""
        if event.button() == Qt.LeftButton:
            self.startPos = event.pos()
        QTreeWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """Process mouse move event (left button)."""
        if event.buttons() & Qt.LeftButton:
            distance = (event.pos() - self.startPos).manhattanLength()
            if distance >= QApplication.startDragDistance():
                self.startDrag()
        QTreeWidget.mouseMoveEvent(self,event)

    def startDrag(self):
        """Start dragging a tree item."""
        if self.currentItem().parent() != None:
            mimedata = QMimeData()
            path = self.currentItem().data(1, Qt.DisplayRole).toString()
            mimedata.setText(path)
            url = QUrl("file:///%s" % path)
            urls = list()
            urls.append(url)
            mimedata.setUrls(urls)
            drag = QDrag(self)
            drag.setMimeData(mimedata)
            drag.start()

    def mimeTypes(self):
        """Return mime types supported by the tree widget."""
        mime_types = QStringList()
        mime_types << "text/uri-list"
        mime_types << "text/x-moz-url"
        return mime_types
