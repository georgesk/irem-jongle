#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

from .Ui_main import Ui_MainWindow

class ChampGravite:
    """
    Cette classe enregistre une méthode à activer toutes les
    40 millisecondes et qui peut toucher un objet du document
    SVG
    """

    def __init__(self, parent, acceleration):
        """
        :param parent: le widget parent qui contient les crochets (hooks)
        :type  parent: MainWindow
        :param acceleration: le vecteur accélération en 2D
        :type  acceleration: par exemple, tuple(float, float)
        """
        self.acc = acceleration
        def fonction(obj):
            obj.accelere(self.acc[0], self.acc[1])
            return
        parent.hooks.append(fonction)
        return

        

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, svg=None):
        QtWidgets.QMainWindow.__init__(self,parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.delta_t=40e-3
        self.ech=10 #(pixels pour 1 mètre)
        self.ui.svgWidget.delta_t=self.delta_t
        self.ui.svgWidget.ech=self.ech
        if svg:
            self.ui.svgWidget.loadfile(svg)
        self.ui.tabWidget.setCurrentWidget(self.ui.sceneTab)
        self.hooks=[]
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.runhooks)
        self.timer.start(1000*self.delta_t)

    def runhooks(self):
        """
        Fonction rappelée par le timer, toutes les 40 millisecondes.

        Elle provoque l'exécution de chaque fonction de la liste
        des hooks.
        """
        for i, obj in self.ui.svgWidget.objetsPhysiques.items():
            for h in self.hooks:
                h(obj)
            obj.move()
        self.ui.svgWidget.refresh()
        return

def main():
    app = QtWidgets.QApplication(sys.argv)

    w=MainWindow(svg="ballon.svg")
    w.show()
    #g=ChampGravite(w, (0, 9.8))
    ### mise en place de la gravité
    def fonction(obj):
        obj.accelere(self.acc[0], self.acc[1])
        return
    w.hooks.append(fonction)

    
    sys.exit(app.exec_())
    return

