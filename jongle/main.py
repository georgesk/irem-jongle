#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from xml.dom import minidom
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

class ChampGravite:
    """
    Cette classe enregistre une méthode à activer toutes les
    40 millisecondes et qui peut toucher un objet du document
    SVG
    """

    def __init__(self, svgObjet, identifiant, echelle, acceleration):
        """
        :param svgObjet:    un objet SVG
        :type  svgObjet:    xml.dom
        :param identifiant: désigne un des éléments de l'image
        :type  identifiant: str
        :param echelle:     l'échelle de l'accélération par rapport à l'image
        :type  echelle:     float
        :param acceleration: le vecteur accélération en 2D
        :type  acceleration: par exemple, tuple(float, float)
        """

def main():

    app = QtWidgets.QApplication(sys.argv)

    doc=minidom.parse("ballon.svg")
    w=QtSvg.QSvgWidget()
    w.load(doc.toxml(encoding="utf-8"))
    w.show()
    
    sys.exit(app.exec_())
