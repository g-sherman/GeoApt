# Copyright (C) 2008-2011 Gary Sherman
# Licensed under the terms of GNU GPL 2
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dlgAboutGeoApt_ui import Ui_dlgAboutGeoApt
class AboutGeoApt(QDialog, Ui_dlgAboutGeoApt):
    """ UI driver for the about box"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
