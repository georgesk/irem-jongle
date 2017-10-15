
### mise en place de la gravité
def gravite(obj):
    obj.accelere(0,9.8)
    return

### mise en place du rebond
def rebond(obj):
    if obj.y > 50 and obj.vy > 0:
        obj.vy = -obj.vy
    return
