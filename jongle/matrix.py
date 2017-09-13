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
    
