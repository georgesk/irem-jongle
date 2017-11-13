# -*- coding: utf-8 -*-
from __future__ import print_function

from PyQt5 import QtSvg, QtCore, QtGui

class SVGWidget(QtSvg.QSvgWidget):
    """
    Un widget SVG amélioré, qui permet de s'occuper de la dynamique de
    plusieurs objets graphiques sur une image de fond
    """
    def __init__(self, parent=None):
        """
        Le constructeur.

        :param parent: un widget parent
        :type parent: QtWidgets.QWidget
        """
        QtSvg.QSvgWidget.__init__(self, parent)
        self.bg=None # image de fond
        return

    def refresh(self, doc, background):
        """
        Remet à jour l'affichage en réinterprétant le DOM

        :param doc: un objet SVG
        :type doc: xml.dom
        :param background: une image de fond
        :type  background: numpy Array 2D 8 bits non signés
        """
        self.bg=background
        self.load(QtCore.QByteArray(
            doc.documentElement.toxml(encoding="utf-8"))
        )
        return

    def paintEvent(self,event):
        """
        surcharge la méthode de peinture : représente d'abord l'image de fond
        puis interprète ensuite le SVG.
        """
        if self.bg is not None:
            h, w, channels = self.bg.shape
            qimage = QtGui.QImage(
                self.bg, w, h,
                QtGui.QImage.Format_RGB888
            )
            painter=QtGui.QPainter(self)
            rect=QtCore.QRect(0,0,2048,2048)
            painter.drawImage(rect,qimage,rect)
            painter.end()
        # trace le doc SVG
        QtSvg.QSvgWidget.paintEvent(self, event)
        return

    def resizeEvent(self, event):
        """
        cette fonction est surchargée pour forcer à une taille fixe
        dès lors que self.bg est défini
        """
        if self.bg is not None:
            h, w, channels = self.bg.shape
            self.resize(w,h)
        QtSvg.QSvgWidget.resizeEvent(self, event)
        
