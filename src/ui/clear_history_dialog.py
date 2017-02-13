# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/clear_history_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ClearHistoryDialog(object):
    def setupUi(self, ClearHistoryDialog):
        ClearHistoryDialog.setObjectName("ClearHistoryDialog")
        ClearHistoryDialog.resize(626, 540)
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
        self.chbAll = QtWidgets.QCheckBox(self.widget_2)
        self.chbAll.setGeometry(QtCore.QRect(290, 10, 70, 17))
        self.chbAll.setObjectName("chbAll")
        self.chbTwoWeeks = QtWidgets.QCheckBox(self.widget_2)
        self.chbTwoWeeks.setGeometry(QtCore.QRect(290, 40, 120, 17))
        self.chbTwoWeeks.setObjectName("chbTwoWeeks")
        self.chbNone = QtWidgets.QCheckBox(self.widget_2)
        self.chbNone.setGeometry(QtCore.QRect(290, 70, 70, 17))
        self.chbNone.setObjectName("chbNone")
        self.verticalLayout.addWidget(self.widget_2)
        self.scrollArea = QtWidgets.QScrollArea(ClearHistoryDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 606, 385))
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
        self.chbAll.setText(_translate("ClearHistoryDialog", "All"))
        self.chbTwoWeeks.setText(_translate("ClearHistoryDialog", "Older then 2 weeks"))
        self.chbNone.setText(_translate("ClearHistoryDialog", "None"))

