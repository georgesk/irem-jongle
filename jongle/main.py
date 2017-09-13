#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

from .Ui_main import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, svg=None, delta_t=None, ech=None):
        QtWidgets.QMainWindow.__init__(self,parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.delta_t=delta_t if delta_t else 40e-3
        self.ech=ech if ech else 20
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

    def enregistreFonction(self, fonction):
        """
        ajoute une fonction à self.hooks
        :param fonction: une fonction de rappel
        :type fonction: une fonction qui a un seul argument, de type 
        ObjetPhysique.
        """
        self.hooks.append(fonction)
        return

def main():
    app = QtWidgets.QApplication(sys.argv)

    w=MainWindow(svg="ballon.svg", delta_t=40e-3, ech=10)
    w.show()

    ### mise en place de la gravité
    def fonction(obj):
        obj.accelere(0,9.8)
        return
    w.enregistreFonction(fonction)


    ### mise en place du rebond
    def rebond(obj):
        if obj.y > 50 and obj.vy > 0:
            obj.vy = -obj.vy
        return
    w.enregistreFonction(rebond)
    
    sys.exit(app.exec_())
    return

