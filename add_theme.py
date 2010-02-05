from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dlgAddTheme_ui import Ui_dlgAddTheme
class AddTheme(QDialog, Ui_dlgAddTheme):

  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.setupUi(self)

