# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/vchs/Sources/Repos/Relanotes/relanotes/qtdesign_ui/clear_history_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ClearHistoryDialog(object):
    def setupUi(self, ClearHistoryDialog):
        ClearHistoryDialog.setObjectName("ClearHistoryDialog")
        ClearHistoryDialog.resize(741, 540)
        self.verticalLayout = QtWidgets.QVBoxLayout(ClearHistoryDialog)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_2 = QtWidgets.QWidget(ClearHistoryDialog)
        self.widget_2.setMinimumSize(QtCore.QSize(0, 100))
        self.widget_2.setObjectName("widget_2")
        self.label = QtWidgets.QLabel(self.widget_2)
        self.label.setGeometry(QtCore.QRect(10, 40, 181, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pbutSelectAll = QtWidgets.QPushButton(self.widget_2)
        self.pbutSelectAll.setGeometry(QtCore.QRect(360, 10, 80, 23))
        self.pbutSelectAll.setObjectName("pbutSelectAll")
        self.pbutSelectOlderThanTwoWeeks = QtWidgets.QPushButton(self.widget_2)
        self.pbutSelectOlderThanTwoWeeks.setGeometry(QtCore.QRect(360, 40, 136, 23))
        self.pbutSelectOlderThanTwoWeeks.setObjectName("pbutSelectOlderThanTwoWeeks")
        self.pbutSelectNone = QtWidgets.QPushButton(self.widget_2)
        self.pbutSelectNone.setGeometry(QtCore.QRect(360, 70, 80, 23))
        self.pbutSelectNone.setObjectName("pbutSelectNone")
        self.verticalLayout.addWidget(self.widget_2)
        self.scrollArea = QtWidgets.QScrollArea(ClearHistoryDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 721, 385))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.buttonBox = QtWidgets.QDialogButtonBox(ClearHistoryDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ClearHistoryDialog)
        QtCore.QMetaObject.connectSlotsByName(ClearHistoryDialog)

    def retranslateUi(self, ClearHistoryDialog):
        _translate = QtCore.QCoreApplication.translate
        ClearHistoryDialog.setWindowTitle(_translate("ClearHistoryDialog", "Clear History"))
        self.label.setText(_translate("ClearHistoryDialog", "Select items for deleting:"))
        self.pbutSelectAll.setText(_translate("ClearHistoryDialog", "All"))
        self.pbutSelectOlderThanTwoWeeks.setText(_translate("ClearHistoryDialog", "Older then 2 weeks"))
        self.pbutSelectNone.setText(_translate("ClearHistoryDialog", "None"))

