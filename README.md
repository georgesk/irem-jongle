# IREM JONGLE #

Commande pour les tests (et pour les impatients) : `./jongle.py`

## But du projet ##

Georges Khaznadar fait partie des auteurs de l'application pymecavideo,
qui permet le suivi d'objets dans une séquence vidéo, pour traiter les données
dans le cadre de la mécanique du point, en deux dimensions.

Avec Pymecavideo, on ouvre un fichier vidéo, on pointe à la main ou
automatiquement les positions successives d'un ou de plusieurs objets
en déplacement. Ensuite on peut :

  * visualiser des trajectoires, des vecteurs vitesse,
  * synthétiser une vidéo en changeant de référentiel (un des objets suivis devient immobile),
  * exporter les données vers divers logiciels de traitement des données (LibreOffice Calc, Qtiplot, Regressi, etc.)
	
Avec IREM JONGLE, on pourra superposer aux vidéo étudiées des objets qui
résultent d'une simulation, obéissant éventuellement aux mêmes lois que
les objets réels filmés.

## Outils pour les simulations ##

avec IREM JONGLE, on ouvre un fichier vidéo, on choisit une icône représentant
un objet, on choisit un modèle de force que cet objet reçoit (par exemple
son poids, dans le cas d'un champ de gravité), puis on peut appliquer à
cet objet diverses *impulsions* :

  * une impulsion de départ (sa vitesse initiale)
  * un ou plusieurs *kicks* (ou frappes). Chaque *kick* est donné dans une zone spatio-temporelle assez précise (autour de coordonnées x, y, t). Quand l'objet pénètre dans cette *zone spatio-temporelle*, son vecteur vitesse est incrémenté d'un vecteur Δv.
	
On peut passer doucement la séquence vidéo et la simulation, image par image.
Une fois que le modèle est au point, on peut demander de générer une nouvelle
vidéo qui superpose la ou les icônes avec la vidéo de fond.

