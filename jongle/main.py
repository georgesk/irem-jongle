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

    def __str__(self):
        return "ChampGravite(cible : {g}, echelle: {ech}, accélération: {acc})".format(**self.__dict__)
        

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, svg=None):
        QtWidgets.QMainWindow.__init__(self,parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        if svg:
            self.ui.svgWidget.loadfile(svg)
        self.ui.tabWidget.setCurrentWidget(self.ui.sceneTab)
        self.delta_t=40e-3
        self.ech=0.1
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
        print("GRRRR runhooks", self.ui.svgWidget.objetsPhysiques.items())
        for i, obj in self.ui.svgWidget.objetsPhysiques.items():
            for h in self.hooks:
                h(obj)
                print("GRRR", i)
            obj.move()     
        self.ui.svgWidget.refresh()
        return

def main():
    app = QtWidgets.QApplication(sys.argv)

    w=MainWindow(svg="ballon.svg")
    w.show()
    #g=ChampGravite(doc, doc.getElementsByTagName("g")[0], 0.2, (0, 9.8))
    
    sys.exit(app.exec_())
    return

