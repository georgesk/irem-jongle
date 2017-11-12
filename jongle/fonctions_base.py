
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
    if obj.t==0:
        obj.x=1.26
        obj.y=1.64
        obj.vx=-0.68
        obj.vy=-2.4
    return

