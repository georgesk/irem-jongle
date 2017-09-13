#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from xml.dom import minidom
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

hooks=[]
"""
:var  hooks: une liste de procédures qu'on accrocher et décrocher
:type hooks: [function, ...]
"""
class matrix:
    """
    classe qui mime l'attribut matrix d'un <DOM Element: g>
    """
    def __init__(self, a,b,c,d,e,f):
        self.a=a
        self.b=b
        self.c=c
        self.d=d
        self.e=e
        self.f=f
        return

    def __str__(self):
        return "matrix({a},{b},{c},{d},{e},{f})".format(**self.__dict__)

    def move(self,x,y):
        self.e+=x
        self.f+=y
        return
    
class ChampGravite:
    """
    Cette classe enregistre une méthode à activer toutes les
    40 millisecondes et qui peut toucher un objet du document
    SVG
    """

    def __init__(self,
                 svgObjet, group, echelle, acceleration):
        """
        :param svgObjet:    un objet SVG
        :type  svgObjet:    xml.dom
        :param group: désigne un des groupes <g> de l'image
        :type  group: <DOM Element: g>
        :param echelle:     l'échelle de l'accélération par rapport à l'image
        :type  echelle:     float
        :param acceleration: le vecteur accélération en 2D
        :type  acceleration: par exemple, tuple(float, float)
        """
        self.svg = svgObjet
        self.g  = group
        self.ech = echelle
        self.acc = acceleration

        def fonction():
            mat=eval(self.g.getAttribute("transform"))
            mat.move(self.ech*self.acc[0], self.ech*self.acc[1])
            self.g.setAttribute("transform", str(mat))
            return

        hooks.append(fonction)
        return

    def __str__(self):
        return "ChampGravite(cible : {g}, echelle: {ech}, accélération: {acc})".format(**self.__dict__)
        
w=None
doc=None

def runhooks():
    """
    Fonction rappelée toutes les 40 millisecondes.

    Elle provoque l'exécution de chaque fonction de la liste
    globale hooks.
    """
    for h in hooks:
        h()
    w.load(doc.toxml(encoding="utf-8"))
    return

def main():
    global w
    global doc
    app = QtWidgets.QApplication(sys.argv)

    doc=minidom.parse("ballon.svg")
    w=QtSvg.QSvgWidget()
    w.load(doc.toxml(encoding="utf-8"))
    w.show()
    g=ChampGravite(doc, doc.getElementsByTagName("g")[0], 0.2, (0, 9.8))
    timer=QtCore.QTimer()
    timer.timeout.connect(runhooks)
    timer.start(40)
    
    sys.exit(app.exec_())
