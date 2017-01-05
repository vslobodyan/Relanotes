#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *

from src import calculator


if __name__ == "__main__":
    # app = QtGui.QApplication(sys.argv)
    app = QtWidgets.QApplication(sys.argv)

    calculator_win = calculator.CalculatorWindow()
    calculator_win.show()

    sys.exit(app.exec_())
