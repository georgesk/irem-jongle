# -*- coding: utf-8 -*-
from __future__ import print_function

from PyQt5 import QtSvg, QtCore

class SVGWidget(QtSvg.QSvgWidget):
    """
    Un widget SVG amélioré, qui permet de s'occuper de la dynamique de
    plusieurs objets graphiques
    """
    def __init__(self, parent=None):
        """
        Le constructeur.
        :param parent: un widget parent
        :type parent: QtWidgets.QWidget
        """
        QtSvg.QSvgWidget.__init__(self, parent)
        return

    def refresh(self, doc):
        """
        Remet à jour l'affichage en réinterprétant le DOM
        :param doc: un objet SVG
        :type doc: xml.dom
        """
        # le forçage au type QtCore.QByteArray est nécessaire pour Python2
        # qui fait mal la différence entre str et bytes
        self.load(QtCore.QByteArray(doc.toxml(encoding="utf-8")))
        return
