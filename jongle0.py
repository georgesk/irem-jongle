#! /usr/bin/python3

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    svgData=open('ballon.svg','rb').read()
    w=QtSvg.QSvgWidget()
    w.load(svgData)
    w.show()
    
    sys.exit(app.exec_())
