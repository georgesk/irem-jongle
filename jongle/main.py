#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys, inspect, pydoc, os.path, cv2, io

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo, QSize
from xml.dom import minidom
from collections import OrderedDict
from copy import deepcopy

from .Ui_main import Ui_MainWindow
from .objetphysique import ObjetPhysique, SVGImageAvecObjets
from .matrix import matrix
from .pythonSyntax import PythonHighlighter


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None,
                 svg=None,
                 delta_t=None,
                 ech=None,
                 videofile=None,
                 progfile="jongle/fonction_base.py",
    ):
        """
        le constructeur

        :param parent: un parent
        :type parent: QWidget
        :param svg: un nom de fichier au format SVG
        :type svg: str
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
        self.highlight = PythonHighlighter(self.ui.progEdit.document())
        self.delta_t=delta_t if delta_t else 40e-3
        self.ech=ech if ech else 20
        self.doc=None
        self.svg=svg
        self.progFileName=None
        self.loadfile()
        self.ui.tabWidget.setCurrentWidget(self.ui.sceneTab)
        self.currentFrame=0
        self.stillFrame=0 # pointeur vers l'image gelée
        self.ui.progEdit.setPlainText(open(progfile).read())
        self.hooks=[] # liste de fonctions pour la simulation
        self.docs=[]  # liste d'images SVG
        self.trajectoires=[] # liste d'ensembles d'objets se déplaçant
        self.enregistreFonctions()
        self.frames=videoToRgbFrameList(videofile)
        self.videoWidth, self.videoHeight, _ =  self.frames[0].shape
        self.ui.svgWidget.resize(QSize(self.videoWidth, self.videoHeight))
        self.count=len(self.frames)
        self.ui.progressBar.setRange(0,self.count)
        self.doc=SVGImageAvecObjets(self.frames[0], self.objetsPhysiques)
        self.ui.svgWidget.refresh(self.doc)

        self.simulated = False
        self.dragging  = False
        self.objIdents = set() # identifiants des objets sélectionnés
        # la boucle pour afficher les images
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.timeHook)
        self.timer.start(1000*self.delta_t)
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
        return

    def saveAs(self):
        if self.timer.isActive():
            self.startStop()
        self.back() # remise à zéro
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
        if self.timer.isActive():
            self.startStop()
        self.back() # remise à zéro
        if not self.progFileName:
            return self.saveAs()
        with io.open(self.progFileName, mode="w", encoding="utf-8") as out:
            out.write(self.ui.progEdit.toPlainText())
        return
        
    def openFile(self):
        if self.timer.isActive():
            self.startStop()
        self.back() # remise à zéro
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
        return
        
    def oneBack(self):
        """
        fonction de rappel pour revenir en arrière d'une image
        """
        if self.simulated:
            if self.currentFrame > 0:
                self.currentFrame -=1
                self.ui.svgWidget.refresh(self.docs[self.currentFrame])
                self.animProgress()
        return

    def oneForward(self):
        """
        fonction de rappel pour avancer d'une image
        """
        if self.simulated:
            if self.currentFrame < self.count-1:
                self.currentFrame +=1
                self.ui.svgWidget.refresh(self.docs[self.currentFrame])
                self.animProgress()
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
            doc=self.docs[self.stillFrame]
            for o in self.objIdents:
               o.moveInSVG(doc, mv, self.ech)
               self.setCbText(o)
            self.ui.svgWidget.refresh(doc)
            self.prevPos=event.pos()
        return

    def setCbText(self,op):
        """
        ajuste le texte d'une case à cocher
        
        :param op: un objet physique
        :type  op: ObjetPhysique
        """
        op.cb.setText("%s (%6.2f, %6.2f)" %(op.id, op.x, op.y))
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
        if not self.simulated:
            self.simule()
        else:
            self.showDoc()
            if self.currentFrame < self.count:
                self.currentFrame +=1
        return
    
    def loadfile(self):
        """
        Récupère un fichier SVG, l'analyse et l'affiche.
        """
        self.doc=minidom.parse(self.svg)
        self.objetsPhysiques=OrderedDict()
        self.trouveObjetsPhysiques()
        return

    def trouveObjetsPhysiques(self):
        """
        met à jour la liste self.objetsPhysiques avec tous les
        elements <g> du DOM, qui ont un attribut
        transform="matrix(a,b,c,d,e,f)", puis crée des cases à cocher
        pour sélectionner les objets physiques.
        """
        for g in self.doc.getElementsByTagName("g"):
            try:
                m= eval(g.getAttribute("transform"))
                if isinstance(m, matrix):
                    ident=g.getAttribute("id")
                    o=ObjetPhysique(self,ident, g, m)
                    self.objetsPhysiques[ident]=o
            except:
                pass
        poBox=self.ui.poBox
        layout = poBox.layout()
        for ident,o in  self.objetsPhysiques.items():
            b=QtWidgets.QCheckBox("%s (%6.2f, %6.2f)" %(o.id, o.x, o.y),poBox)
            o.cb=b
            layout.addWidget(b)
            b.stateChanged.connect(self.selectObject(o))
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
            self.showDoc()
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
                              ))
        self.ui.progressBar.setValue(self.currentFrame)
        for o in self.trajectoires[self.currentFrame]:
            # met à jour les positions affichées des objets physiques
            self.setCbText(o)
        # définit self.stillFrame au cas où l'animation est arretée
        if not self.timer.isActive():
            self.stillFrame=self.currentFrame
        return

    def showDoc(self):
        """
        Fonction rappelée par le timer, toutes les 40 millisecondes.

        Elle provoque l'affichage d'une nouvelle image
        """
        if self.currentFrame < self.count:
            self.ui.svgWidget.refresh(self.docs[self.currentFrame])
            self.animProgress()
        else:
            pass
        return
    
    def simule(self):
        """
        Réalise la simulation de façon non-interactive, pour len(self.frames)
        images
        """
        self.stillFrame=0
        frame=self.frames[self.currentFrame]
        objSet=set()
        for i, obj in self.objetsPhysiques.items():
            for h in self.hooks:
                h(obj)
            obj.move()
            objSet.add(obj.copy())
        doc=SVGImageAvecObjets(frame, self.objetsPhysiques)
        self.docs.append(doc)
        self.trajectoires.append(objSet)
        self.ui.label.setText("simultation, %d/%d : %s" %
                              (self.currentFrame, self.count, i))
        self.currentFrame+=1
        self.ui.progressBar.setValue(self.currentFrame)
        if self.currentFrame == self.count:
            self.currentFrame=0
            self.simulated=True
            self.ui.label.setText(self.tr("The simulation is finished"))
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
        self.docs=[]  # efface les images de la précédente simulation
        self.trajectoires=[] # idem pour les trajectoires des objets physiques
        self.simulated=False # va provoquer une nouvelle simulation
        self.currentFrame=0  # depuis le début
        funcs=self.functionsFrom()
        for f in funcs:
            self.hooks.append(funcs[f][0])
        return funcs

    def functionsFrom(self):
        """
        Compile la source de l'onglet programmes en langage Python

        :return: un dictionnaire : nom de fonction -> (code compilé, spécification d'arguments, aide sur la fonction)
        :rtype: dict
        """
        source=self.ui.progEdit.toPlainText()
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
    parser.add_option("-g", "--svg",
                      action="store", type="string", dest="svg",
                      default=os.path.join(os.path.dirname(__file__),"../ballon.svg")
    )
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

    w=MainWindow(svg=options.svg, delta_t=options.deltat, ech=options.scale,
                 videofile=options.video, progfile=options.prog
    )

    w.show()
    sys.exit(app.exec_())
    return

