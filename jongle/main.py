#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys, Image, io, base64

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from xml.dom import minidom
from collections import OrderedDict
from copy import deepcopy

import cv2
import numpy as np

from .Ui_main import Ui_MainWindow
from .objetphysique import ObjetPhysique
from .matrix import matrix

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
        self.doc=None
        if svg:
            self.svg=svg
            self.loadfile()
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
            self.count=len(self.frames)
        else: # pas de fichier vidéo
            self.count=100 # (quatre secondes, à 25 images/seconde)
        self.hooks=[]
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.showDoc)
        self.timer.start(1000*self.delta_t)

    def loadfile(self):
        """
        Récupère un fichier SVG, l'analyse et l'affiche.
        """
        self.doc=minidom.parse(self.svg)
        self.objetsPhysiques=OrderedDict()
        self.trouveObjetsPhysiques()
        self.ui.svgWidget.refresh(self.doc)
        return

    def objets(self, doc):
        """
        trouve la liste d'elements <g> du DOM, qui ont un attribut
        transform="matrix(a,b,c,d,e,f)"
        :param doc: un objet SVG
        :type doc: xml.dom
        :return: une liste d'objets physiques
        :rtype: list(ObjetPhysique)
        """
        objs=OrderedDict()
        for g in self.doc.getElementsByTagName("g"):
            try:
                m= eval(g.getAttribute("transform"))
                if isinstance(m, matrix):
                    ident=g.getAttribute("id")
                    o=ObjetPhysique(self,ident, g, m)
                    objs[ident]=o
            except:
                pass
        return objs
        

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

    def showDoc(self):
        """
        Fonction rappelée par le timer, toutes les 40 millisecondes.

        Elle provoque l'affichage d'une nouvelle image
        """
        try:
            if self.currentFrame < self.count:
                print("GRRRR", self.docs[self.currentFrame])
                self.ui.svgWidget.refresh(self.docs[self.currentFrame])
                self.currentFrame +=1
        except:
            pass
        return
    
    def runhooks(self):
        """
        Fonction rappelée par le timer, toutes les 40 millisecondes.

        Elle provoque l'exécution de chaque fonction de la liste
        des hooks.
        """
        for i, obj in self.objetsPhysiques.items():
            for h in self.hooks:
                h(obj)
            obj.move()
        if self.frames:
            self.insertImage(self.frames[self.currentFrame])
            if self.currentFrame < len(self.frames)-1:
                self.currentFrame = self.currentFrame+1
        self.ui.svgWidget.refresh(self.doc)
        return

    def simule(self):
        """
        Réalise la simulation de façon non-interactive, pour len(self.frames)
        images
        """
        self.docs=[]
        count=0
        for frame in self.frames:
            doc=minidom.parseString("<svg></svg>")
            for i, obj in self.objetsPhysiques.items():
                print("GRRRR", i, obj)
                for h in self.hooks:
                    h(obj)
                obj.move()
                doc.documentElement.appendChild(obj.g)
            self.insertImage(frame, doc=doc)
            self.docs.append(doc)
            print("GRRRR", self.docs)
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

    def insertImage(self, frame):
        """
        insère une image juste devant le fond (de type rect)
        ou remplace l'image qui est juste devant le fond
        :param frame: une image issue d'un cv2.VideoCapture ... read()
        :type frame: numpy Array
        """
        im = Image.fromarray(frame)
        out = io.BytesIO()
        im.save(out, format='PNG')
        b64=base64.b64encode(out.getvalue())
        href="data:image/png;base64,"+b64
        premierObjet=self.doc.getElementsByTagName("g")[0]
        images=self.doc.getElementsByTagName("image")
        if not images:
            image=self.doc.createElement("image")
            image.setAttribute("x","0")
            image.setAttribute("y","0")
            image.setAttribute("width","%d" %im.width)
            image.setAttribute("height","%d" %im.height)
            image.setAttribute("preserveAspectRatio","none")
            image.setAttribute("xlink:href",href)
            self.doc.documentElement.insertBefore(image, premierObjet)
        else:
            images[0].setAttribute("xlink:href",href)
        return
            
    def insertImage(self, frame, doc=None):
        """
        insère une image juste devant le fond (de type rect)
        ou remplace l'image qui est juste devant le fond
        :param frame: une image issue d'un cv2.VideoCapture ... read()
        :type frame: numpy Array
        :param doc: a SVG document
        :type doc: xml.dom
        """
        if doc==None:
            doc=self.doc
        im = Image.fromarray(frame)
        out = io.BytesIO()
        im.save(out, format='PNG')
        b64=base64.b64encode(out.getvalue())
        href="data:image/png;base64,"+b64
        premierObjet=doc.getElementsByTagName("g")[0]
        images=doc.getElementsByTagName("image")
        if not images:
            image=self.doc.createElement("image")
            image.setAttribute("x","0")
            image.setAttribute("y","0")
            image.setAttribute("width","%d" %im.width)
            image.setAttribute("height","%d" %im.height)
            image.setAttribute("preserveAspectRatio","none")
            image.setAttribute("xlink:href",href)
            doc.documentElement.insertBefore(image, premierObjet)
        else:
            images[0].setAttribute("xlink:href",href)
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
    w.simule()
    
    sys.exit(app.exec_())
    return

