# -*- coding: utf-8 -*-
from __future__ import print_function

import Image, io, base64
from xml.dom import minidom
from collections import OrderedDict

from PyQt5 import QtSvg, QtCore

from .matrix import matrix
from .objetphysique import ObjetPhysique

class SVGWidget(QtSvg.QSvgWidget):
    """
    Un widget SVG amélioré, qui permet de s'occuper de la dynamique de
    plusieurs objets graphiques
    """
    def __init__(self, parent=None, svg=None):
        """
        Le constructeur.
        :param parent: un widget parent
        :type parent: QtWidgets.QWidget
        :param svg: nom du fichier SVG
        :type svg: str
        """
        QtSvg.QSvgWidget.__init__(self, parent)
        self.svg=svg
        self.delta_t=None
        self.ech=None
        self.doc=None
        if self.svg:
            self.loadfile()
        return

    def loadfile(self, fname=None):
        """
        Récupère un fichier SVG, l'analyse et l'affiche.
        :param fname: nom du fichier SVG (si None, on garde self.svg)
        :type fname: str
        """
        if fname:
            self.svg=fname
        self.doc=minidom.parse(self.svg)
        self.objetsPhysiques=OrderedDict()
        self.trouveObjetsPhysiques()
        self.refresh()
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

    def refresh(self):
        """
        Remet à jour l'affichage en réinterprétant le DOM
        """
        # pas besoin de le faire si le tab parent
        # est caché
        # le forçage au type QtCore.QByteArray est nécessaire pour Python2
        # qui fait mal la différence entre str et bytes
        self.load(QtCore.QByteArray(self.doc.toxml(encoding="utf-8")))
        return
