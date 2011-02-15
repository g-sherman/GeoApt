# Copyright (C) 2008-2011 Gary Sherman
# Licensed under the terms of GNU GPL 2
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dlgAddThemeFolder_ui import Ui_dlgAddThemeFolder
class AddThemeFolder(QDialog, Ui_dlgAddThemeFolder):
    """UI driver for the Add Theme FOlder dialog."""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
