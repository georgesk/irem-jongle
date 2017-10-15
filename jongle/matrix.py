# -*- coding: utf-8 -*-
class matrix:
    r"""
    classe qui mime l'attribut matrix d'un <DOM Element: g>

    :math:`\left(\begin{array}{ccc} a & b & e \\ c & d & f \\ 0 & 0 & 1\end{array}\right) \times \left(\begin{array}{c} x \\ y \\ 1 \end{array}\right) = \left(\begin{array}{c} ax+by+e \\ cx+dy+f \\ 1 \end{array}\right)`

    """
    def __init__(self, a,b,c,d,e,f):
        r"""
        le constructeur ; on évoque ci-dessous :

          * un rapport d'homotétie :math:`r`, 
          * un angle de rotation :math:`\theta`,
          * et les coordonnées :math:`(\delta x, \delta y)`, horizontale et verticale d'une translation.

        :param a: :math:`= r \cos(\theta)`, élément de matrice de rotation/homotétie
        :type  a: float
        :param b: :math:`= r \sin(\theta)`, élément de matrice de rotation/homotétie
        :type  b: float
        :param c: :math:`= -r \sin(\theta)`, élément de matrice de rotation/homotétie
        :type  c: float
        :param d: :math:`= r \cos(\theta)`, élément de matrice de rotation/homotétie
        :type  d: float
        :param e: :math:`= \delta x`, translation horizontale
        :type  e: float
        :param f: :math:`= \delta y`, translation verticale
        :type  f: float
        """
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
        """
        Implémente un déplacement, en modifiant les deux derniers éléments
        de la matrice.

        :param x: translation horizontale
        :type  x: float
        :param y: translation verticale
        :type  y: float
        """
        self.e+=x
        self.f+=y
        return
    
