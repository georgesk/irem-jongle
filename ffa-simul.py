
### mise en place de la gravité
def gravite(obj):
    obj.accelere(0,9.8)
    return

### mise en place d'un rebond automatique en bas de l'image
def rebond(obj):
    if obj.y > 1.8 and obj.vy > 0:
        obj.vy = -obj.vy
    return

### placement initial de l'objet
def initial(obj):
    if obj.numero==0 and obj.id=="ballon-1":
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

### premier coup de pied
def coup1(obj):
  if obj.numero==14 and obj.id=="ballon-1":
    ### ajoute delta V = (0.85, 5.37) N.B. : l'axe y est vers le bas
    obj.vx = obj.vx + 0.85
    obj.vy = obj.vy - 5.37
  return

### deuxième coup de pied
def coup2(obj):
  if obj.numero==28 and obj.id=="ballon-1":
    ### ajoute delta V = (-0.58, 5.3) N.B. : l'axe y est vers le bas
    obj.vx = obj.vx - 0.58
    obj.vy = obj.vy - 5.3
  return

### troisième coup de pied
def coup3(obj):
  if obj.numero==39 and obj.id=="ballon-1":
    ### ajoute delta V = (0.74, 4.2) N.B. : l'axe y est vers le bas
    obj.vx = obj.vx + 0.74
    obj.vy = obj.vy - 4.2
  return

### quatrième coup de pied
def coup4(obj):
  if obj.numero==51 and obj.id=="ballon-1":
    ### ajoute delta V = (-0.31, 4.7) N.B. : l'axe y est vers le bas
    obj.vx = obj.vx - 0.31
    obj.vy = obj.vy - 4.7
  return

### cinquième coup de pied
def coup5(obj):
  if obj.numero==63 and obj.id=="ballon-1":
    ### ajoute delta V = (0.24, 5.2) N.B. : l'axe y est vers le bas
    obj.vx = obj.vx + 0.24
    obj.vy = obj.vy - 5.2
  return


### sixième coup de pied
def coup6(obj):
  if obj.numero==77 and obj.id=="ballon-1":
    ### ajoute delta V = (-0.54, 5.4) N.B. : l'axe y est vers le bas
    obj.vx = obj.vx - 0.54
    obj.vy = obj.vy - 5.4
  return

### septième coup de pied
def coup7(obj):
  if obj.numero==90 and obj.id=="ballon-1":
    ### ajoute delta V = (-0.1, 5.3) N.B. : l'axe y est vers le bas
    obj.vx = obj.vx - 0.1
    obj.vy = obj.vy - 5.3
  return

### huitième coup de pied
def coup8(obj):
  if obj.numero==104 and obj.id=="ballon-1":
    ### ajoute delta V = (0, 4.5) N.B. : l'axe y est vers le bas
    obj.vx = obj.vx + 0.0
    obj.vy = obj.vy - 4.5
  return
