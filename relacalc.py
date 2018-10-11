#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtWidgets
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *

from relacalc import relacalc

if __name__ == "__main__":
    # app = QtGui.QApplication(sys.argv)
    app = QtWidgets.QApplication(sys.argv)

    calculator_win = relacalc.CalculatorWindow()
    calculator_win.show()

    sys.exit(app.exec_())
