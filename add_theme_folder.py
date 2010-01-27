from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dlgAddThemeFolder_ui import Ui_dlgAddThemeFolder
class AddThemeFolder(QDialog, Ui_dlgAddThemeFolder):

  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.setupUi(self)

