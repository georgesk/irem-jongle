#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys, inspect, pydoc, os.path

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo
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
                 progfile="jongle/fonction_base.py",
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
        :param progfile: un fichier Python qui contient des fonctions agissant sur un ObjetPhysique
        :type progfile: str
        """
        QtWidgets.QMainWindow.__init__(self,parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.playButton.clicked.connect(self.startStop)
        self.ui.backButton.clicked.connect(self.back)
        self.ui.simulButton.clicked.connect(self.enregistreFonctions)
        self.delta_t=delta_t if delta_t else 40e-3
        self.ech=ech if ech else 20
        self.doc=None
        self.svg=svg
        self.loadfile()
        self.ui.tabWidget.setCurrentWidget(self.ui.sceneTab)
        self.currentFrame=0
        self.ui.progEdit.setPlainText(open(progfile).read())
        self.hooks=[]
        self.docs=[]
        self.enregistreFonctions()
        self.frames=videoToRgbFrameList(videofile)
        self.count=len(self.frames)
        self.ui.progressBar.setRange(0,self.count)
        self.doc=insertImage(self.frames[0], self.doc)
        self.ui.svgWidget.refresh(self.doc)

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
            self.currentFrame +=1
            self.ui.label.setText(self.tr("video t = ") +
                                  "%6.3f / %6.3f s" % (
                                      self.currentFrame*self.delta_t,
                                      self.count*self.delta_t
                                  ))
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

    def enregistreFonctions(self):
        """
        Enregistre les fonctions écrites dans l'onglet de programme,
        afin qu'elles soient invoquées lors de la simulation. Les anciennes
        fonctions enregistrées sont effacées.
        
        :return: un dictionnaire : nom de fonction -> tuple(exécutable, paramètres, aide)
        :rtype: dict
        """
        self.hooks=[] # efface les anciennes fonctions
        self.docs=[]  # efface les images de la précédente simulation
        self.simulated=False # va provoquer une nouvelle simulation
        self.currentFrame=0  # depuis le début
        funcs=functionsFrom(self.ui.progEdit.toPlainText())
        for f in funcs:
            self.hooks.append(funcs[f][0])
        return funcs

def functionsFrom(source):
    """
    Compile une source en langage Python

    :param source: la source du programme
    :type  source: str
    :return: un dictionnaire : nom de fonction -> (code compilé, spécification d'arguments, aide sur la fonction)
    :rtype: dict
    """
    d={}
    c=compile(source,"","exec")
    exec(c,d)
    return {f: (d[f], inspect.getargspec(d[f]), pydoc.render_doc(d[f], "aide sur %s")) for f in d if callable(d[f])}

def main():
    app = QtWidgets.QApplication(sys.argv)

    # traduction
    lang=QLocale.system().name()
    t=QTranslator()
    t.load("lang/"+lang, os.path.dirname(__file__))
    app.installTranslator(t)
    
    t1=QTranslator()
    t1.load("qt_"+lang,
            QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(t1)

    w=MainWindow(svg="ballon.svg", delta_t=40e-3, ech=20,
                 videofile="videos/ffa-cropped-cut001.avi",
                 progfile="jongle/fonctions_base.py"
    )

    w.show()
    sys.exit(app.exec_())
    return

