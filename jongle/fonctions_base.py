
### placement initial de l'objet
def initial(obj):
    if obj.t==0:
        obj.x=0
        obj.y=5
        obj.vx=0
        obj.vy=0
    return

### mise en place de la gravité
def gravite(obj):
    obj.accelere(0,9.8)
    return

### mise en place du rebond
def rebond(obj):
    if obj.y > 20 and obj.vy > 0:
        obj.vy = -obj.vy
    return
