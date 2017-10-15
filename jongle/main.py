#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from xml.dom import minidom
from collections import OrderedDict
from copy import deepcopy

from .Ui_main import Ui_MainWindow
from .objetphysique import ObjetPhysique
from .matrix import matrix
from .opencv import videoToRgbFrameList, insertImage

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
        self.ui.playButton.clicked.connect(self.startStop)
        self.ui.backButton.clicked.connect(self.back)
        self.delta_t=delta_t if delta_t else 40e-3
        self.ech=ech if ech else 20
        self.doc=None
        self.svg=svg
        self.loadfile()
        self.ui.tabWidget.setCurrentWidget(self.ui.sceneTab)
        self.frames=videoToRgbFrameList(videofile)
        self.currentFrame=0
        self.count=len(self.frames)
        self.ui.progressBar.setRange(0,self.count)
        self.doc=insertImage(self.frames[0], self.doc)
        self.ui.svgWidget.refresh(self.doc)

        self.hooks=[]
        self.docs=[]
        self.simulated=False
        # la boucle pour afficher les images
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.timeHook)
        self.timer.start(1000*self.delta_t)

    def timeHook(self):
        """
        fonction de rappel (25 fois par seconde)
        """
        if not self.simulated:
            self.simule()
        else:
            self.showDoc()
        return
    
    def loadfile(self):
        """
        Récupère un fichier SVG, l'analyse et l'affiche.
        """
        self.doc=minidom.parse(self.svg)
        self.objetsPhysiques=OrderedDict()
        self.trouveObjetsPhysiques()
        return

    def trouveObjetsPhysiques(self):
        """
        met à jour la liste self.objetsPhysiques avec tous les
        elements <g> du DOM, qui ont un attribut transform="matrix(a,b,c,d,e,f)"
        """
        for g in self.doc.getElementsByTagName("g"):
            try:
                m= eval(g.getAttribute("transform"))
                if isinstance(m, matrix):
                    ident=g.getAttribute("id")
                    o=ObjetPhysique(self,ident, g, m)
                    self.objetsPhysiques[ident]=o
            except:
                pass
        return

    def startStop(self):
        """arrête/relanche le timer"""
        if self.timer.isActive():
            self.timer.stop()
            self.ui.playButton.setIcon(QtGui.QIcon.fromTheme("media-playback-pause-symbolic"))
        else:
            self.timer.start()
            self.ui.playButton.setIcon(QtGui.QIcon.fromTheme("media-playback-start-symbolic"))
        return

    def back(self):
        """
        remet le compteur de frames à zéro
        """
        self.currentFrame=0
        if self.simulated:
            self.showDoc()
        return

    def showDoc(self):
        """
        Fonction rappelée par le timer, toutes les 40 millisecondes.

        Elle provoque l'affichage d'une nouvelle image
        """
        if self.currentFrame < self.count:
            self.ui.svgWidget.refresh(self.docs[self.currentFrame])
            self.ui.label.setText(self.tr("video t = ") +
                                  "%6.3f s" %(self.currentFrame*self.delta_t,))
            self.currentFrame +=1
            self.ui.progressBar.setValue(self.currentFrame)
        else:
            pass
        return
    
    def simule(self):
        """
        Réalise la simulation de façon non-interactive, pour len(self.frames)
        images
        """
        frame=self.frames[self.currentFrame]
        doc=minidom.parseString("<svg></svg>")
        for i, obj in self.objetsPhysiques.items():
            for h in self.hooks:
                h(obj)
            obj.move()
            doc.documentElement.appendChild(obj.g)
            self.ui.label.setText("simultation, %d/%d : %s" %
                                  (self.currentFrame, self.count, i))
        doc=insertImage(frame, doc)
        self.docs.append(deepcopy(doc))
        self.currentFrame+=1
        self.ui.progressBar.setValue(self.currentFrame)
        if self.currentFrame == self.count:
            self.currentFrame=0
            self.simulated=True
            self.ui.label.setText(self.tr("The simulation is finished"))
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
    w.show()
    sys.exit(app.exec_())
    return

