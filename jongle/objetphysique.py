# -*- coding: utf-8 -*-
from __future__ import print_function

import Image, io, base64
from xml.dom.minidom import parseString
from copy import deepcopy
from .matrix import matrix

class ObjetPhysique():
    def __init__(self, parent, ident, group, matrice, vx=0, vy=0):
        """
        Définit un objet 2D par ses coordonnées dans l'espace de phase
        (position, vitesse)

        :param parent: un parent, qui connaît l'échelle pour dessiner
        :type parent: SVGWidget
        :param ident: nom de l'objet physique
        :type ident: str
        :param group: un groupe de l'image
        :type group: <DOM Element: g>
        :param matrice: l'attribut de transformation (matrice) du groupe
        :type matrice: jongle.matrix.matrix
        :param vx: abscisse de la vitesse
        :type vx: float
        :param vy: ordonnée de la vitesse
        :type vy: float
        """
        self.parent=parent
        self.id=ident
        self.g=group
        self.m=matrice
        self.x=matrice.e/self.parent.ech
        self.y=matrice.f/self.parent.ech
        self.vx=vx
        self.vy=vy
        self.cb=None # pointeur vers un checkBox
        return

    def copy(self):
        """
        revoie une copie de self, avec seulement la matrice copiées
        en profondeur. Le reste est plus simple (ce sont des scalaires).
        On évite de faire une copie en profondeur de self.cb, qui est
        un QCheckBox.
        
        :return: une copie "économique" de self
        :rtype: ObjetPhysique
        """
        result=ObjetPhysique(
            self.parent, self.id, self.g,
            deepcopy(self.m), self.vx, self.vy
        )
        result.cb=self.cb
        return result
    
    def __str__(self):
        return "Objet physique « {id} » : pos=({x}, {y}) vit=({vx}, {vy})".format(**self.__dict__)

    def moveInSVG(self, mv, ech):
        """
        Déplace un objet physique avec une transformation par matrice au sein
        d'une image SVG.

        :param mv: un déplacement en mètre
        :type  mv: QPoint
        :param ech: l'échelle globale
        :type ech: float
        """
        m=eval(self.g.getAttribute("transform"))
        m.e+=mv.x()
        m.f+=mv.y()
        self.g.setAttribute("transform", str(m))
        self.x=m.e/ech
        self.y=m.f/ech
        return

    def move(self):
        """
        Applique une étape de la méthode d'Euleur, change les coordonnées
        self.x et self.y, en y additionnant respectivement vx*delta_t et
        vy*delta_t. Comme self.g est un objet groupe SVG sous-jacent, on en
        modifie la matrice de transformation, en tenant compte de l'échelle
        du widget parent.
        """
        self.x+=self.vx*self.parent.delta_t
        self.y+=self.vy*self.parent.delta_t
        self.m.e=self.x*self.parent.ech
        self.m.f=self.y*self.parent.ech
        self.g.setAttribute("transform", str(self.m))
        return

    @property
    def t(self):
        """
        cette propriété permet d'interroger la date ; en fait celle-ci est
        héritée du parent, et elle est liée un nuvéro de l'image en cours
        de traitement. Comme dans la mécanique newtonnienne, le temps est
        universel.

        :return: la date en seconde
        :rtype: float
        """
        return self.parent.currentFrame * self.parent.delta_t

    def accelere(self, ax, ay):
        """
        Applique une étape de la méthode d'Euleur, change les vitesses
        self.vx et self.vy, en appliquant l'accélération (ax,ay) pendant
        une durée delta_t.

        :param ax: accélération horizontale
        :type  ax: float
        :param ay: accélération verticale
        :type  ay: float
        """
        self.vx+=ax*self.parent.delta_t
        self.vy+=ay*self.parent.delta_t
        return

def SVGImageAvecObjets(frame, objDict):
    """
    Crée un document SVG qui contient une image, et où l'on rajoute
    une liste d'objets à dessiner

    :param frame: une image
    :type  frame: Array numpy 2D
    :param objDict: dictionnaire d'objets SVG
    :type objDict: {nom: <instance de ObjetPhysique>, ...}
    :return: un document SVG
    :rtype: xml.dom.Document
    """
    im = Image.fromarray(frame)
    out = io.BytesIO()
    im.save(out, format='PNG')
    b64=base64.b64encode(out.getvalue())
    href="data:image/png;base64,"+b64
    doc=parseString("""\
<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"></svg>""".format(
    w=im.width, h=im.height
))
    # crée un objet image
    image=doc.createElement("image")
    # met des dimensions et une position
    image.setAttribute("x","0")
    image.setAttribute("y","0")
    image.setAttribute("width","%d" %im.width)
    image.setAttribute("height","%d" %im.height)
    image.setAttribute("preserveAspectRatio","none")
    # accroche l'image au format PNG
    image.setAttribute("xlink:href",href)
    doc.documentElement.appendChild(image)
    for obj in objDict:
        doc.documentElement.appendChild(deepcopy(objDict[obj].g))
    return doc

