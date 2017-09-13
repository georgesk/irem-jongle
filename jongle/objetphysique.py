
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
        :type matrice: matrix
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
        return

    def __str__(self):
        return "Objet physique « {id} » : pos=({x}, {y}) vit=({vx}, {vy})".format(**self.__dict__)

    def move(self):
        self.x+=self.vx*self.parent.delta_t
        self.y+=self.vy*self.parent.delta_t
        self.m.e=self.x*self.parent.ech
        self.m.f=self.y*self.parent.ech
        self.g.setAttribute("transform", str(self.m))
        return

    def accelere(self, ax, ay):
        self.vx+=ax*parent.delta_t
        self.vy+=ay*parent.delta_t
        return
