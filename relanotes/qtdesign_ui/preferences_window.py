# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/vchs/Sources/Repos/Relanotes/relanotes/qtdesign_ui/preferences_window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogPreferences(object):
    def setupUi(self, DialogPreferences):
        DialogPreferences.setObjectName("DialogPreferences")
        DialogPreferences.resize(598, 510)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/newPrefix/icons/window_icons/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogPreferences.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogPreferences)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(DialogPreferences)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox.setGeometry(QtCore.QRect(430, 40, 60, 28))
        self.doubleSpinBox.setProperty("value", 0.4)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 40, 331, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(500, 40, 77, 20))
        self.label_2.setObjectName("label_2")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_3 = QtWidgets.QPushButton(DialogPreferences)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_2 = QtWidgets.QPushButton(DialogPreferences)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(DialogPreferences)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogPreferences)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DialogPreferences)

    def retranslateUi(self, DialogPreferences):
        _translate = QtCore.QCoreApplication.translate
        DialogPreferences.setWindowTitle(_translate("DialogPreferences", "Relanote Preferences"))
        self.label.setText(_translate("DialogPreferences", "Notelist update timeout"))
        self.label_2.setText(_translate("DialogPreferences", "sec"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("DialogPreferences", "Main"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("DialogPreferences", "History sidebar"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("DialogPreferences", "Themes and styles"))
        self.pushButton_3.setText(_translate("DialogPreferences", "Cancel"))
        self.pushButton_2.setText(_translate("DialogPreferences", "Apply"))
        self.pushButton.setText(_translate("DialogPreferences", "Ok"))

from resources import resources_rc
