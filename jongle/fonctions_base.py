
### mise en place de la gravité
def gravite(obj):
    obj.accelere(0,9.8)
    return

### mise en place du rebond
def rebond(obj):
    if obj.y > 1.8 and obj.vy > 0:
        obj.vy = -obj.vy
    return

### placement initial de l'objet
def initial(obj):
    if obj.t==0 and obj.id=="ballon-1":
        # la vitesse initiale est (-0.57, -2.65) NB: l'axe y est vers le bas !
        obj.vx=-0.57
        obj.vy=-2.65
        # la position initiale est (1.25, 1.38)
        obj.x=1.25
        obj.y=1.38
        # mais ... on anticipe
        # une étape de la simulation qui va modifier cette position
        # pour un intervalle de temps de 0.04 secondes.
        obj.x = obj.x - obj.vx*0.04
        obj.y = obj.y - obj.vy*0.04
    return

