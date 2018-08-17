# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/vchs/Sources/Repos/Relanotes/src/ui/calculator_window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(718, 399)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/newPrefix/icons/window_icons/calculator.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.labelClearHistory = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setUnderline(False)
        self.labelClearHistory.setFont(font)
        self.labelClearHistory.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.labelClearHistory.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelClearHistory.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelClearHistory.setObjectName("labelClearHistory")
        self.horizontalLayout_2.addWidget(self.labelClearHistory)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setStyleSheet("background-color: rgb(220, 220, 220);")
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.lineEdit.setFont(font)
        self.lineEdit.setAutoFillBackground(True)
        self.lineEdit.setStyleSheet("")
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 25)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.labelResult = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.labelResult.setFont(font)
        self.labelResult.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.labelResult.setStyleSheet("")
        self.labelResult.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelResult.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelResult.setObjectName("labelResult")
        self.horizontalLayout.addWidget(self.labelResult)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 10, 10, 10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout_2.addWidget(self.lineEdit_2)
        self.labelComment = QtWidgets.QLabel(Dialog)
        self.labelComment.setObjectName("labelComment")
        self.verticalLayout_2.addWidget(self.labelComment)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_3.addWidget(self.pushButton)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_3.addWidget(self.label_6)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.buttonAdd_to_note = QtWidgets.QPushButton(Dialog)
        self.buttonAdd_to_note.setObjectName("buttonAdd_to_note")
        self.verticalLayout_4.addWidget(self.buttonAdd_to_note)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_4.addWidget(self.label_7)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "RelaCalc"))
        self.label_5.setText(_translate("Dialog", "History:"))
        self.labelClearHistory.setText(_translate("Dialog", "<html><head/><body><p><a href=\"clear_history\"><span style=\" text-decoration: underline; color:#004455;\">Clear History</span></a></p></body></html>"))
        self.label.setText(_translate("Dialog", "Type an expression:"))
        self.label_2.setText(_translate("Dialog", "="))
        self.labelResult.setText(_translate("Dialog", "<html><head/><body><p><span style=\" color:#000000;\">TextLabel</span></p></body></html>"))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p>Some things about format: <span style=\" font-size:12pt; font-weight:600; color:#008066;\">*</span> multiplication, <span style=\" font-size:12pt; font-weight:600; color:#008066;\">/</span> division. Any other operations avalaible too.</p></body></html>"))
        self.labelComment.setText(_translate("Dialog", "Your comment for history"))
        self.pushButton.setText(_translate("Dialog", "Add to history"))
        self.label_6.setText(_translate("Dialog", "Or press Enter"))
        self.buttonAdd_to_note.setText(_translate("Dialog", "Add to note"))
        self.label_7.setText(_translate("Dialog", "Ctrl+Enter"))

from resources import resources_rc
