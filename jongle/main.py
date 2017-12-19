#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys, inspect, pydoc, os.path, cv2, io, os, os.path, re

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtCore import Qt, QTranslator, QLocale, QLibraryInfo, QSize, \
    QXmlStreamReader
from PyQt5.QtGui import QPalette, QColor, QPixmap, QIcon, QImage, QPainter
from PyQt5.QtWidgets import QLabel, QTableWidgetItem, QSpinBox
from PyQt5.QtSvg import QSvgRenderer
from xml.dom import minidom
from collections import OrderedDict
from xml.dom.minidom import parseString

from .Ui_main import Ui_MainWindow
from .objetphysique import ObjetPhysique
from .matrix import matrix


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None,
                 delta_t=None,
                 ech=None,
                 videofile=None,
                 progfile="jongle/fonction_base.py",
    ):
        """
        le constructeur

        :param parent: un parent
        :type parent: QWidget
        :param delta_t: l'intervalle de temps entre deux images; la fonction
          de rappel self.runhooks est appelée entre deux images
        :type delta_t: float
        :param ech: l'échelle à appliquer à l'image
        :type ech: float
        :param videofile: un fichier video, à 25 images par secondes
        :type videofile: str
        :param progfile: un fichier Python qui contient des fonctions agissant sur un ObjetPhysique
        :type progfile: str
        """
        QtWidgets.QMainWindow.__init__(self,parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.connectUi()
        self.delta_t=delta_t if delta_t else 40e-3
        self.ech=ech if ech else 200
        self.progFileName=None
        self.ui.tabWidget.setCurrentWidget(self.ui.sceneTab)
        self.currentFrame=0
        self.stillFrame=0 # pointeur vers l'image gelée
        self.ui.progEdit.setText(open(progfile).read())
        self.hooks=[] # liste de fonctions pour la simulation
        self.trajectoires=[] # liste d'ensembles d'objets se déplaçant
        self.frames=videoToRgbFrameList(videofile)
        self.videoHeight, self.videoWidth, _ =  self.frames[0].shape
        self.count=len(self.frames)
        self.ui.progressBar.setRange(0,self.count)

        self.simulated = False
        self.ui.simulButton.setEnabled(True)
        
        self.paletteProgressSimul=self.ui.progressBar.palette()
        self.paletteProgressSimul.setColor(QPalette.Highlight, QColor("red"))
        self.paletteProgressVideo=self.ui.progressBar.palette()
        self.paletteProgressVideo.setColor(QPalette.Highlight, QColor("blue"))
        
        self.dragging  = False
        self.objIdents = set() # identifiants des objets sélectionnés
        # la boucle pour afficher les images
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.timeHook)
        self.timer.start(1000*self.delta_t)
        # compile et enregistre les fonctions de l'onglet d'édition
        self.enregistreFonctions()
        # peuple l'onglet des images
        self.stockObjetsPhysique=OrderedDict()
        self.getImages()
        # trouve les objets physiques et ajoute des widgets pour y accéder
        self.recenseObjets()
        # affiche la première image avec les objets SVG en haut à gauche
        doc=self.SVGObjets()
        self.ui.svgWidget.refresh(doc, self.frames[0])
        return

    def connectUi(self):
        """
        connecte les évènements de l'interface utilisateur avec
        les fonctions de rappel.
        """
        self.ui.playButton.clicked.connect(self.startStop)
        self.ui.backButton.clicked.connect(self.back)
        self.ui.simulButton.clicked.connect(self.enregistreFonctions)
        self.ui.minusButton.clicked.connect(self.oneBack)
        self.ui.plusButton.clicked.connect(self.oneForward)
        self.ui.saveAsButton.clicked.connect(self.saveAs)
        self.ui.compileButton.clicked.connect(self.tryCompile)
        self.ui.actionSave_standalone.triggered.connect(self.save)
        self.ui.actionOpen.triggered.connect(self.openFile)
        self.ui.actionCheck_Synta_x.triggered.connect(self.tryCompile)
        self.ui.progEdit.textChanged.connect(self.dirty)
        return

    def recenseBientot(self):
        """
        fonction de rappel pour self.recenseObjets, mais qui le 
        programme pour le prochain tour de la boucle principale
        """
        t=QtCore.QTimer.singleShot(0, self.recenseObjets)
        
    def recenseObjets(self):
        """
        parcourt le tableau des images et ramène au moins un objet
        en se basant sur les cases cochées. Met à jour
        self.ObjetsPhysiques
        """
        self.objetsPhysiques=OrderedDict()
        t=self.ui.tableWidget
        noms=list(self.stockObjetsPhysique.keys())
        for i in range(t.rowCount()):
            for j in range(t.cellWidget(i,0).value()):
                nom=noms[i]
                while nom in self.objetsPhysiques.keys():
                    # éviter les collisions d'entrées dans le dictionnaire
                    nom=self.incrementeNom(nom)
                op=self.stockObjetsPhysique[noms[i]].copy()
                op.id=nom
                self.objetsPhysiques[nom]=op
        # traite le cas où aucune case n'aurait été cochée
        # alors, ça coche autoritairement la première venue
        # du coup la fonction se rappelle elle-même à cause de
        # l'évènement valueChanged au tout de boucle suivant
        if not len(self.objetsPhysiques):
            t.cellWidget(0,0).setValue(1)
        # crée les contrôles des objets en bas de la fenêtre
        self.afficheListeObjets()
        return

    def incrementeNom(self, nom):
        """
        Change un nom compte tenu des entrées déjà présentes
        dans le dictionnaire self.objetsPhysiques
        :param nom: une base de nom
        :type  nom: str
        :return: une entrée nouvelle pour dico
        :rtype: str
        """
        pattern=r"(.*[^\d])(\d*)"
        m=re.match(pattern, nom)
        if not m.group(2):
            prefix=nom+"-"
            num=0
        else:
            prefix=m.group(1)
            num=int(m.group(2))
        result="{}{}".format(prefix,num)
        while result in self.objetsPhysiques.keys():
            num+=1
            result="{}{}".format(prefix,num)
        return result

    def getImages(self):
        self.stockObjetsPhysique=OrderedDict()
        size=70 # la taille des images 2D du répertoire image
        premiereCochee=False # booléen pour cocher la 1ère ligne par défaut
        t=self.ui.tableWidget
        t.horizontalHeader().setVisible(True)
        t.setRowCount(0) # vide la table des images
        top=os.path.join(os.path.dirname(os.path.dirname(__file__)),"images")
        for root, dirs, files in os.walk(top, topdown=False):
            for f in sorted(files): # met en tête 000-ballon.svg
                if f[-4:].lower()==".svg":
                    svgFile=os.path.join(root,f)
                    objetsPhysiques=self.trouveObjetsPhysiques(
                        minidom.parse(svgFile))
                    for opNom in objetsPhysiques:
                        nom=opNom
                        while nom in self.stockObjetsPhysique.keys():
                            # empêche deux noms identiques
                            nom+="_"
                        self.stockObjetsPhysique[nom]=objetsPhysiques[opNom]
                        svgCode="<svg>\n{}\n</svg>".format(
                            objetsPhysiques[opNom].g.toxml())
                        t.setRowCount(t.rowCount()+1)
                        t.setRowHeight(t.rowCount()-1, size)
                        # un compteur
                        sp=QSpinBox()
                        sp.setRange(0,9)
                        if not premiereCochee:
                            sp.setValue(1)
                            premiereCochee=True
                        sp.valueChanged.connect(self.recenseBientot)
                        t.setCellWidget(t.rowCount()-1,0,sp)
                        # le nom de fichier (sans le chemin)
                        t.setItem(t.rowCount()-1,1,QTableWidgetItem(f))
                        # le nom de l'image
                        t.setItem(t.rowCount()-1,2,QTableWidgetItem(opNom))
                        # la dimension native de l'image
                        t.setItem(t.rowCount()-1,3,QTableWidgetItem(
                            "{size}×{size} pixels".format(size=size)))
                        # une icône avec l'image
                        l=self.svgLabel(svgCode, size)
                        t.setCellWidget(t.rowCount()-1,4,l)
        t.setHorizontalHeaderLabels([
            self.tr('Use'), self.tr('File'), self.tr('Name'),
            self.tr('Size'), self.tr('Image')
        ])
        for i in range(4):
            t.resizeColumnToContents(i)
        return

    @staticmethod
    def svgLabel(svgCode, size):
        """
        transforme un code SVG en un label orné d'une image
        :param svgCode: un code SVG valide <svg>...</svg>
        :type  svgCode: bytes
        :param size: la taille du label carré (taille du rendu)
        :type  size: int
        """
        renderer=QSvgRenderer(QXmlStreamReader(svgCode))
        im=QImage(QSize(size,size),QImage.Format_ARGB32)
        painter=QPainter(im)
        renderer.render(painter)
        painter.end()
        pm=QPixmap.fromImage(im)
        l=QLabel()
        l.setPixmap(pm)
        return l
    
    def dirty(self):
        """
        invalide la source Python, il faudra recompiler
        """
        self.ui.simulButton.setEnabled(True)
        return

    def saveAs(self):
        if not self.progFileName:
            defaultDir=""
        else:
            defaultDir=os.path.dirname(self.progFileName)
        self.progFileName, ok=QtWidgets.QFileDialog.getSaveFileName(
            self,self.tr("File to save the programs"), defaultDir, "*.py"
        )
        if ok:
            if not self.progFileName.endswith(".py"):
                self.progFileName+=".py"
            self.nameTabProg()
            return self.save()
        else:
            return None

    def nameTabProg(self):
        """
        Met à jour le nom de l'onglet des programmes
        """
        self.ui.tabWidget.setTabText(
            self.ui.tabWidget.indexOf(self.ui.progTab),
            self.tr("Programs ({p})").format(p=os.path.basename(
                self.progFileName
            ))
        )
        return

    def save(self):
        self.back() # remise à zéro
        if self.timer.isActive():
            self.startStop()
        if not self.progFileName:
            return self.saveAs()
        with io.open(self.progFileName, mode="w", encoding="utf-8") as out:
            out.write(self.ui.progEdit.text())
        return
        
    def openFile(self):
        self.back() # remise à zéro
        if self.timer.isActive():
            self.startStop()
        if not self.progFileName:
            defaultDir=""
        else:
            defaultDir=os.path.dirname(self.progFileName)
        self.progFileName, ok=QtWidgets.QFileDialog.getOpenFileName(
            self, self.tr("Open a file"), defaultDir, "*.py"
        )
        if ok:
            self.ui.progEdit.setPlainText(io.open(
                self.progFileName, encoding="utf-8"
            ).read())
            self.nameTabProg()
            # recompilation forcée
            self.simulated = False
            self.ui.simulButton.setEnabled(True)
            self.startStop()
        return

    def SVGObjets(self, objDict=None):
        """
        Crée un document SVG à la taille du svgWidget, qui contient les objets
        de la liste à afficher

        :param objDict: dictionnaire d'objets SVG ; s'il est None, on prendra self.objetsPhysiques
        :type objDict: {nom: <instance de ObjetPhysique>, ...}
        :param w: largeur du document SVG
        :return: un document SVG
        :rtype: xml.dom.Document
        """
        if objDict is None:
            objDict=self.objetsPhysiques
        svgCode="""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"></svg>"""
        doc=parseString(svgCode.format(w=self.videoWidth, h=self.videoHeight))
        for ident in objDict:
            o=objDict[ident]
            doc.documentElement.appendChild(o.g)
        return doc

    def refresh(self, i):
        """
        rafraichit le svgWidget avec la position i

        :param i: index de l'image en cours
        :type  i: int
        """
        doc=self.SVGObjets(self.trajectoires[i])
        self.ui.svgWidget.refresh(doc, self.frames[i])
        self.animProgress()
        return
        
    def oneBack(self):
        """
        fonction de rappel pour revenir en arrière d'une image
        """
        if self.simulated:
            if self.currentFrame > 0:
                self.currentFrame -=1
                self.refresh(self.currentFrame)
        return

    def oneForward(self):
        """
        fonction de rappel pour avancer d'une image
        """
        if self.simulated:
            if self.currentFrame < self.count-1:
                self.currentFrame +=1
                self.refresh(self.currentFrame)
        return

        
    def mouseMoveEvent(self, event):
        """
        traite le mouvement de la souris quand un bouton est pressé.
        Les objets qui ont été cochés dans le cadre du bas se déplacent
        en même temps qu'on bouge la souris.
        """
        if not self.timer.isActive() and self.currentFrame < self.count:
            # pas d'animation en cours, on peut bouger les objets
            if not self.dragging: return # cette ligne est redondante
            mv=event.pos() - self.prevPos
            objetsPhysiques=self.trajectoires[self.stillFrame]
            for ident,o in objetsPhysiques.items():
                if not o.cb.isChecked(): continue
                self.dirty() # si on a bougé il faut re-simuler
                o.moveInSVG(mv, self.ech)
                self.setCbText(ident,o)
            self.refresh(self.stillFrame)
            self.prevPos=event.pos()
        return

    def setCbText(self,ident,op):
        """
        ajuste le texte d'une case à cocher
        
        :param ident: un nom
        :type  ident: str
        :param op: un objet physique
        :type  op: ObjetPhysique
        """
        op.cb.setText("%s (%6.2f, %6.2f)" %(ident, op.x, op.y))
        return

    def mousePressEvent(self, event):
        """
        Traite l'évènement de bouton de souris pressé. Débute le « tirer »
        en enregistrant la position courante
        """
        self.dragging=True
        self.prevPos=event.pos()
        return

    def mouseReleaseEvent(self, event):
        """
        Traite l'évènement de bouton de souris relâché. Fin du « tirer ».
        """
        self.dragging=False
        return

    def timeHook(self):
        """
        fonction de rappel (25 fois par seconde). Selon fait le choix entre
        faire avancer les calculs de simulation, et monter l'animation 
        (quand la simulation est terminée, on dispose de toutes les images
        de l'animation, prêtes à servir.
        """
        if self.currentFrame < self.count:
            if not self.simulated:
                # ne pas relancer en cours de simulation
                self.ui.simulButton.setEnabled(False)
                self.simule()
                self.simulProgress()
            else:
                self.refresh(self.currentFrame)
                self.animProgress()
            self.currentFrame +=1
        else: # self.currentFrame == self.count
            if not self.simulated:
                self.simulated=True
                self.ui.simulButton.setEnabled(False)
                self.currentFrame=0
                self.ui.label.setText(self.tr("The simulation is finished"))
            else:
                self.startStop()
        return
    
    def trouveObjetsPhysiques(self, doc):
        """
        met à jour la liste self.objetsPhysiques avec tous les
        elements <g> du DOM, qui ont un attribut
        transform="matrix(a,b,c,d,e,f)", puis crée des cases à cocher
        pour sélectionner les objets physiques.

        :param doc: un document SVG
        :type  doc: xml.dom
        :return: un dictionnaire ordonné identifiant => ObjetPhysique
        :rtype: OrderedDict((identifiant, <ObjetPhysique>), ...)
        """
        result=OrderedDict()
        for g in doc.getElementsByTagName("g"):
            try:
                m= eval(g.getAttribute("transform"))
                if isinstance(m, matrix):
                    ident=g.getAttribute("id")
                    o=ObjetPhysique(self,ident, g, m)
                    result[ident]=o
            except:
                pass
        return result

    def afficheListeObjets(self):
        """
        Affiche la liste des objets en bas du premier onglet, et ajoute
        pour chacun une case à cocher si on le veut déplaçable à la souris
        """
        poBox=self.ui.poBox
        layout = poBox.layout()
        # supprime les objets précédemment affichés
        for i in reversed(range(1,layout.count())): 
            layout.itemAt(i).widget().setParent(None)
            # selon la doc:
            # The new widget is deleted when its parent is deleted
        for ident,o in  self.objetsPhysiques.items():
            b=QtWidgets.QCheckBox("%s (%6.2f, %6.2f)" %(ident, o.x, o.y),poBox)
            o.cb=b
            layout.addWidget(b)
            b.stateChanged.connect(self.selectObject(o))
        self.dirty()
        return

    def selectObject(self,op):
        """
        Fabrique de fonction de rappel pour les cases à cocher des 
        objets physiques, qui conserve le contexte de l'objet op
        afin de maintenir l'ensemble self.objIdents
        
        :param op: un objet physique
        :type  op: ObjetPhysique
        """
        def cb(state):
            if state > 0:
                self.objIdents.add(op)
            else:
                self.objIdents.remove(op)
            return
        return cb

    def startStop(self):
        """arrête/relanche le timer"""
        if self.timer.isActive():
            self.timer.stop()
            self.stillFrame=self.currentFrame
            self.ui.playButton.setIcon(QtGui.QIcon.fromTheme("media-playback-pause-symbolic"))
        else:
            self.timer.start()
            self.ui.playButton.setIcon(QtGui.QIcon.fromTheme("media-playback-start-symbolic"))
        return

    def back(self):
        """
        remet le compteur de frames à zéro
        """
        self.currentFrame=0
        if self.simulated:
            self.refresh(self.currentFrame)
            self.animProgress()
        # dans tous les cas, réactive la boucle de temps
        if not self.timer.isActive():
            self.startStop()
        return

    def animProgress(self):
        """
        Montre dans la barre de progression et sous celle-ci où en est le
        temps de la vidéo.
        """
        self.ui.label.setText(self.tr("video t = ") +
                              "%6.3f / %6.3f s" % (
                                  self.currentFrame*self.delta_t,
                                  self.count*self.delta_t
                              ) + " " + self.tr("(# %d)") % self.currentFrame)
        self.ui.progressBar.setPalette(self.paletteProgressVideo)
        self.ui.progressBar.setValue(self.currentFrame)
        objetsPhysique=self.trajectoires[self.currentFrame]
        for ident,o in objetsPhysique.items():
            # met à jour les positions affichées des objets physiques
            self.setCbText(ident,o)
        # définit self.stillFrame au cas où l'animation est arretée
        if not self.timer.isActive():
            self.stillFrame=self.currentFrame
        return

    def simule(self):
        """
        Réalise la simulation de façon non-interactive, pour len(self.frames)
        images
        """
        self.stillFrame=0
        op=OrderedDict()
        for i, obj in self.objetsPhysiques.items():
            for h in self.hooks:
                h(obj)
            obj.move()
            op[i]=obj.copy()
        self.trajectoires.append(op)
        return

    def simulProgress(self):
        """
        met à jour la barre de progression durant la simulation
        """
        self.ui.label.setText("simultation, %d/%d" %
                              (self.currentFrame, self.count))
        self.ui.progressBar.setPalette(self.paletteProgressSimul)
        self.ui.progressBar.setValue(self.currentFrame)
        return

    def enregistreFonctions(self):
        """
        Enregistre les fonctions écrites dans l'onglet de programme,
        afin qu'elles soient invoquées lors de la simulation. Les anciennes
        fonctions enregistrées sont effacées.
        
        :return: un dictionnaire : nom de fonction -> tuple(exécutable, paramètres, aide)
        :rtype: dict
        """
        self.hooks=[] # efface les anciennes fonctions
        self.trajectoires=[] # idem pour les trajectoires des objets physiques
        self.simulated=False # va provoquer une nouvelle simulation
        self.ui.simulButton.setEnabled(True)
        self.currentFrame=0  # depuis le début
        funcs=self.functionsFrom()
        for f in funcs:
            self.hooks.append(funcs[f][0])
        # dans tous les cas, redémarre une compilation sans attendre
        if not self.timer.isActive():
            self.startStop()
        return funcs

    def functionsFrom(self):
        """
        Compile la source de l'onglet programmes en langage Python

        :return: un dictionnaire : nom de fonction -> (code compilé, spécification d'arguments, aide sur la fonction)
        :rtype: dict
        """
        source=self.ui.progEdit.text()
        d={}
        try:
            c=compile(source,"","exec")
            exec(c,d)
            return {f: (d[f], inspect.getargspec(d[f]), pydoc.render_doc(d[f], "aide sur %s")) for f in d if callable(d[f])}
        except IndentationError as err:
            t=err.text
            QtWidgets.QMessageBox.warning(
                self, self.tr("Indentation error"),
                self.tr("""\
line # {l} column # {c}
{t}
""").format(l=err.lineno, c=err.offset, t=t)
            )
            return dict()
        except SyntaxError as err:
            t=err.text
            QtWidgets.QMessageBox.warning(
                self, self.tr("Syntax error"),
                self.tr("""\
line # {l} column # {c}
{t}
""").format(l=err.lineno, c=err.offset, t=t)
            )
            return dict()
        except Exception as err:
            QtWidgets.QMessageBox.warning(
                self, self.tr("Error"), str(type(err))+" "+str(err)
            )
            return dict()
        
    def tryCompile(self):
        """
        essaie de compiler et renvoi juste un message d'accord si succès
        """
        result=self.functionsFrom()
        if len(result):
            QtWidgets.QMessageBox.information(
                self, self.tr("Compilation successful"),
                self.tr("Defined functions:\n") +
                ", ".join(result.keys())
            )
        return

def videoToRgbFrameList(videofile):
    """
    transforme une vidéo lisible par openCV en une liste d'images au
    format RGB.

    :param videofile: chemin d'un fichier vidéo
    :type  videofile: str
    :return: liste d'images RGB
    :rtype: numpy Array
    """
    frames=[]
    cap=cv2.VideoCapture(videofile)
    ok=True
    while ok:
        ok, frame = cap.read()
        if ok:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return frames

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p", "--prog",
                      action="store", type="string", dest="prog",
                      default=os.path.join(os.path.dirname(__file__),"fonctions_base.py")
    )
    parser.add_option("-v", "--video",
                      action="store", type="string", dest="video",
                      default=os.path.join(os.path.dirname(__file__),"../videos/ffa-cropped-cut001.avi")
    )
    parser.add_option("-s", "--scale",
                      action="store", type="int", dest="scale",
                      default=290)
    parser.add_option("-t", "--deltat",
                      action="store", type="float", dest="deltat",
                      default=40e-3
    )
    (options, args) = parser.parse_args(sys.argv)
    
    app = QtWidgets.QApplication(args)

    # traduction
    lang=QLocale.system().name()
    t=QTranslator()
    t.load("lang/"+lang, os.path.dirname(__file__))
    app.installTranslator(t)
    
    t1=QTranslator()
    t1.load("qt_"+lang,
            QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(t1)

    w=MainWindow(delta_t=options.deltat, ech=options.scale,
                 videofile=options.video, progfile=options.prog
    )

    w.show()
    w.ui.svgWidget.resize(720,576)
    sys.exit(app.exec_())
    return

