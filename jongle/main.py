#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

import cv2
import numpy as np

from .Ui_main import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None,
                 svg=None,
                 delta_t=None,
                 ech=None,
                 videofile=None,
    ):
        """
        le constructeur
        :param parent: un parent
        :type parent: QWidget
        :param svg: un nom de fichier au format SVG
        :type svg: str
        :param delta_t: l'intervalle de temps entre deux images; la fonction
          de rappel self.runhooks est appelée entre deux images
        :type delta_t: float
        :param ech: l'échelle à appliquer à l'image
        :type ech: float
        :param videofile: un fichier video, à 25 images par secondes
        :type videofile: str
        """
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
        self.frames=[]
        self.currentFrame=0
        if videofile:
            self.cap=cv2.VideoCapture(videofile)
            ok=True
            while ok:
                ok, frame = self.cap.read()
                if ok:
                    self.frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
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
        if self.frames:
            self.ui.svgWidget.insertImage(self.frames[self.currentFrame])
            if self.currentFrame < len(self.frames)-1:
                self.currentFrame = self.currentFrame+1
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

    w=MainWindow(svg="ballon.svg", delta_t=40e-3, ech=20,
                 videofile="videos/ffa-cropped-cut001.avi",
    )
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

