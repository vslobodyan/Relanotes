from datetime import datetime, timedelta

from PyQt5 import QtWidgets

from relanotes.qtdesign_ui import clear_history_dialog


class ClearHistoryDialog(QtWidgets.QDialog, clear_history_dialog.Ui_ClearHistoryDialog):

    history_items = []

    history_rec = {}
    history_rec['checkbox'] = None
    history_rec['filename'] = None
    history_rec['last_open'] = None

    def select_all(self):
        for one_item in self.history_items:
            one_item['checkbox'].setChecked(True)

    def select_none(self):
        for one_item in self.history_items:
            one_item['checkbox'].setChecked(False)

    def select_older_than_two_weeks(self):
        today = datetime.now()
        two_weeks = timedelta(days=14)
        for one_item in self.history_items:
            last_open = datetime.strptime(one_item['last_open'], '%Y-%m-%d %H:%M:%S.%f')
            if last_open + two_weeks < today:
                one_item['checkbox'].setChecked(True)
            else:
                one_item['checkbox'].setChecked(False)

    def ok_pressed(self):
        pass
    def cancel_pressed(self):
        pass


    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self.pbutSelectAll.clicked.connect(self.select_all)
        self.pbutSelectOlderThanTwoWeeks.clicked.connect(self.select_older_than_two_weeks)
        self.pbutSelectNone.clicked.connect(self.select_none)