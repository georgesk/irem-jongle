# -*- coding: utf-8 -*-
from __future__ import print_function

import Image, io, base64
from PyQt5 import QtSvg, QtCore

def insertImage(frame, doc):
    """
    insère une image (frame) avant les objets SVG de type "g" dans
    un document SVG.
    :param frame: une image issue d'un cv2.VideoCapture, par read()
    :type frame: numpy Array (encodage BRG comme fait OpenCV)
    :param doc: un document SVG
    :type doc: xml.dom
    :return: le document modifié par insertion de l'image
    :rtype: xml.dom
    """
    im = Image.fromarray(frame)
    out = io.BytesIO()
    im.save(out, format='PNG')
    b64=base64.b64encode(out.getvalue())
    href="data:image/png;base64,"+b64
    premierObjet=doc.getElementsByTagName("g")[0]
    images=doc.getElementsByTagName("image")
    if not images:
        image=doc.createElement("image")
        image.setAttribute("x","0")
        image.setAttribute("y","0")
        image.setAttribute("width","%d" %im.width)
        image.setAttribute("height","%d" %im.height)
        image.setAttribute("preserveAspectRatio","none")
        image.setAttribute("xlink:href",href)
        doc.documentElement.insertBefore(image, premierObjet)
    else:
        images[0].setAttribute("xlink:href",href)
    return doc

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
