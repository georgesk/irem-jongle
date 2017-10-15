# -*- coding: utf-8 -*-
from __future__ import print_function

import cv2, Image, io, base64

def videoToRgbFrameList(videofile):
    """
    transforme une vidéo lisible par openCV en une liste d'images au
    format RGB.
    :param videofile: chemin d'un fichier vidéo
    :type  videofile: str
    :return: list(numpy Array pour une image RGB)
    """
    frames=[]
    cap=cv2.VideoCapture(videofile)
    ok=True
    while ok:
        ok, frame = cap.read()
        if ok:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return frames

def insertImage(frame, doc):
    """
    insère une image (frame) avant les objets SVG de type "g" dans
    un document SVG.
    :param frame: une image issue d'un cv2.VideoCapture, par read()
    :type frame: numpy Array (encodage BRG comme fait OpenCV)
    :param doc: un document SVG
    :type doc: xml.dom
    :return: le document modifié par insertion de l'image
    :rtype: xml.dom
    """
    im = Image.fromarray(frame)
    out = io.BytesIO()
    im.save(out, format='PNG')
    b64=base64.b64encode(out.getvalue())
    href="data:image/png;base64,"+b64
    premierObjet=doc.getElementsByTagName("g")[0]
    images=doc.getElementsByTagName("image")
    if not images:
        image=doc.createElement("image")
        image.setAttribute("x","0")
        image.setAttribute("y","0")
        image.setAttribute("width","%d" %im.width)
        image.setAttribute("height","%d" %im.height)
        image.setAttribute("preserveAspectRatio","none")
        image.setAttribute("xlink:href",href)
        doc.documentElement.insertBefore(image, premierObjet)
    else:
        images[0].setAttribute("xlink:href",href)
    return doc

