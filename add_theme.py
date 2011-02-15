# Copyright (C) 2008-2011 Gary Sherman
# Licensed under the terms of GNU GPL 2
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dlgAddTheme_ui import Ui_dlgAddTheme
class AddTheme(QDialog, Ui_dlgAddTheme):
    """UI driver for the AddTheme dialog."""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.connect(self.pushButton, SIGNAL("clicked()"), self.get_path)

    def get_path(self):
        path = QFileDialog.getOpenFileName(self, "Choose Spatial Layer")
        self.led_path_name.setText(path)
