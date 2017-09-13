from xml.dom import minidom
from collections import OrderedDict

from PyQt5 import QtSvg

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
        self.delta_t=getattr(parent, "delta_t", 40e-3)
        self.ech=getattr(parent, "ech", 0.01)
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

    def trouveObjetsPhysiques(self):
        """
        met à jour la liste self.objetsPhysiques avec tous les
        elements <g> du DOM, qui ont un attribut transform="matrix(a,b,c,d,e,f)"
        """
        for g in self.doc.getElementsByTagName("g"):
            #try:
            if 1:
                m= eval(g.getAttribute("transform"))
                if isinstance(m, matrix):
                    ident=g.getAttribute("id")
                    o=ObjetPhysique(self,ident, g, m)
                    self.objetsPhysiques[ident]=o
                    print("GRRRR",o)
            #except:
            #    pass
        return

    def refresh(self):
        """
        Remet à jour l'affichage en réinterprétant le DOM
        """
        # pas besoin de le faire si le tab parent
        # est caché
        self.load(self.doc.toxml(encoding="utf-8"))
        return
    
        
