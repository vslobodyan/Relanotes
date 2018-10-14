from PyQt5 import QtWidgets

from relanotes.qtdesign_ui import preferences_window


class PreferencesWindow(QtWidgets.QDialog, preferences_window.Ui_DialogPreferences):
    """ Окно общих настроек программы. """

    rn_app = None

    def __init__(self, rn_app, parent=None):
        self.rn_app = rn_app

        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        # self.connect(self.lineEdit, SIGNAL("textEdited ( const QString& )"), self.updateUi)
        # self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.addToHistory)
        # self.connect(self.labelClearHistory, SIGNAL("	linkActivated( const QString& )"), self.clearHistory)
        # self.labelResult.setText('-')
        # self.lineEdit.setFocus()