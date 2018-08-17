# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/vchs/Sources/Repos/Relanotes/src/ui/note_multiaction.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogNoteMultiaction(object):
    def setupUi(self, DialogNoteMultiaction):
        DialogNoteMultiaction.setObjectName("DialogNoteMultiaction")
        DialogNoteMultiaction.resize(746, 269)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/newPrefix/icons/window_icons/multiaction.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogNoteMultiaction.setWindowIcon(icon)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DialogNoteMultiaction)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(DialogNoteMultiaction)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 21))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.labelNoteFileName = QtWidgets.QLabel(DialogNoteMultiaction)
        self.labelNoteFileName.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(11)
        self.labelNoteFileName.setFont(font)
        self.labelNoteFileName.setWordWrap(True)
        self.labelNoteFileName.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelNoteFileName.setObjectName("labelNoteFileName")
        self.verticalLayout_2.addWidget(self.labelNoteFileName)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtWidgets.QLabel(DialogNoteMultiaction)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(DialogNoteMultiaction)
        self.lineEdit.setAutoFillBackground(True)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(400, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButton = QtWidgets.QPushButton(DialogNoteMultiaction)
        self.pushButton.setEnabled(False)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_AddNoteNearly = QtWidgets.QPushButton(DialogNoteMultiaction)
        self.pushButton_AddNoteNearly.setObjectName("pushButton_AddNoteNearly")
        self.horizontalLayout.addWidget(self.pushButton_AddNoteNearly)
        self.pushButton_AddChildNote = QtWidgets.QPushButton(DialogNoteMultiaction)
        self.pushButton_AddChildNote.setObjectName("pushButton_AddChildNote")
        self.horizontalLayout.addWidget(self.pushButton_AddChildNote)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_2 = QtWidgets.QPushButton(DialogNoteMultiaction)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_6 = QtWidgets.QPushButton(DialogNoteMultiaction)
        self.pushButton_6.setEnabled(False)
        self.pushButton_6.setObjectName("pushButton_6")
        self.verticalLayout.addWidget(self.pushButton_6)
        self.pushButton_5 = QtWidgets.QPushButton(DialogNoteMultiaction)
        self.pushButton_5.setEnabled(False)
        self.pushButton_5.setObjectName("pushButton_5")
        self.verticalLayout.addWidget(self.pushButton_5)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        spacerItem2 = QtWidgets.QSpacerItem(40, 88, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.labelNoteFileName.raise_()
        self.label_2.raise_()

        self.retranslateUi(DialogNoteMultiaction)
        QtCore.QMetaObject.connectSlotsByName(DialogNoteMultiaction)

    def retranslateUi(self, DialogNoteMultiaction):
        _translate = QtCore.QCoreApplication.translate
        DialogNoteMultiaction.setWindowTitle(_translate("DialogNoteMultiaction", "Note Multiaction"))
        self.label_2.setText(_translate("DialogNoteMultiaction", "Multioperation for selected note file:"))
        self.labelNoteFileName.setText(_translate("DialogNoteMultiaction", "TextLabel"))
        self.label.setText(_translate("DialogNoteMultiaction", "New Note Name:"))
        self.pushButton.setText(_translate("DialogNoteMultiaction", "Rename"))
        self.pushButton_AddNoteNearly.setText(_translate("DialogNoteMultiaction", "Add note nearly"))
        self.pushButton_AddChildNote.setText(_translate("DialogNoteMultiaction", "Add child note"))
        self.pushButton_2.setText(_translate("DialogNoteMultiaction", "Delete"))
        self.pushButton_6.setText(_translate("DialogNoteMultiaction", "Export"))
        self.pushButton_5.setText(_translate("DialogNoteMultiaction", "Move note"))

from resources import resources_rc
