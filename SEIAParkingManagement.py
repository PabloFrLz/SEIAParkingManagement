"""
    Subject: Software de gerenciamento de vagas de estacionamento das dependências do SEIA, 
             desenvolvido para o Núcleo Administrativo Setorial (NAS) e para a Guarita do 
             edifício onde a secretaria está lotada. Projeto conduzido pelo núcleo de Diretoria
             em Inovação (DIN), vinculado à Secretaria da Inovação e Inteligência Artificial (SEIA), 
             do Estado do Paraná.
    Tools: Python3, PySide6, MySQL, PyQtDarkTheme, Photoshop CC 2015, Github  
    Department: Diretoria de Inovação (DIN)
    Author: Pablo Franco Luz (pablo-tr1@hotmail.com - https://github.com/PabloFrLz)
    Supervisor: André Luis Costa Batistela 
    Director: Thiago Rodrigo da Silva (Thiago Marcelino)
    Version: 1.0.0.03
    Start: 31/03/2026 - 08:16PM
    End: 21/06/2026 - 20:52PM
    Notas:
        1.   _________________________________________________________________________________________
            |      Dados para acesso ao banco de dados MySQL:                                         |                                                                                   |
            |      Comando: mysql -u "user" -p                                                        |             
            |      user: seia                                                                         |
            |      Senha: 5452                                                                        |                                                                                 |             
            |_________________________________________________________________________________________|



"""


import threading

from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QGraphicsOpacityEffect, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QGraphicsProxyWidget, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QPolygonF, QPen, QBrush, QColor, QPainter,QFont
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QPointF
import sys
import Vaga as vg
import Sidebar as sb
import Recursos
import qdarktheme
import pymysql
from colorama import init

init()
ver = "v1.0.0.03" # versão do software

#variaveis de autenticação do banco de dados
USER = 'root'
PASSWORD = '5452'

global WIDTH, HEIGHT, K, J
WIDTH = 1300
HEIGHT = 860
K = 400 #variavel de ajuste para expansão da propriedade na HORIZONTAL 
J = 530 ##variavel de ajuste para expansão da propriedade na VERTICAL 
D = 30 #variavel de deslocamento dos carros na horizontal

POS_X_SIDEBAR = 1550 #posição horizontal da sidebar (ajustável)

LARGURA_CIRCLE = 40
ALTURA_CIRCLE = 40

# Verde
PEN_VERDE = QPen(QColor("#00ff00"), 2)
BRUSH_VERDE = QBrush(QColor(0, 255, 0, 40))

# Rosa
PEN_ROSA = QPen(QColor("#ff69b4"), 2)
BRUSH_ROSA = QBrush(QColor(255, 105, 180, 40))

# Roxo
PEN_ROXO = QPen(QColor("#10006d"), 2)
BRUSH_ROXO = QBrush(QColor(0, 0, 255, 40))

# Azul
PEN_AZUL = QPen(QColor("#0062BE"), 2)
BRUSH_AZUL = QBrush(QColor(56, 109, 255, 40))

class SEIAParkingManagement(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)  # arrastar com botão esquerdo
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.turnRound = True
        self.anim = None
        self.recursos = Recursos.Recursos()

        #==============================================================================================
        # Caixa de busca de placas (v1.0.0.03)
        #==============================================================================================

        self.search_box = QComboBox()
        self.search_box.setEditable(True)
        self.search_box.setPlaceholderText("Digite os dados da placa no formato ABC-XXXX")
        self.search_box.editTextChanged.connect(self.processarVagaBuscada)

        self.completer = self.search_box.completer()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)   # busca em qualquer parte
        self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        #self.scene.addWidget(self.search_box)

        self.conteiner_search = QHBoxLayout()
        self.conteiner_search.addWidget(self.search_box)
        self.scene.addLayout(self.conteiner_search)


        

        #==============================================================================================
        # construção do cenário da propriedade (fundo, contorno, blocos, recepção, torre, entradas/saídas)
        #==============================================================================================

        self.pixmap = QPixmap(self.recursos.PATH.background_app) #imagem de plano de fundo
        self.bg = QGraphicsPixmapItem(self.pixmap)
        self.bg.setOpacity(0.85) # um pouco transparente para destacar o desenho
        self.scene.addItem(self.bg)
        
        self.pixmap2 = QPixmap(self.recursos.PATH.logo_marca_dagua_parana) #imagem marca d'agua do gov. do paraná
        self.bg2 = QGraphicsPixmapItem(self.pixmap2)
        self.bg2.setOpacity(0.05)
        self.bg2.setPos(WIDTH/2-80, HEIGHT/2) 
        self.scene.addItem(self.bg2)

        self.pixmap_edificios = QPixmap(self.recursos.PATH.edificio_hauer) # imagem do edificio do prédio Hauer da SEIA
        self.bg3 = QGraphicsPixmapItem(self.pixmap_edificios)
        self.bg3.setOpacity(0.01) 
        self.bg3.setPos(WIDTH/11, HEIGHT/5.5) 
        self.bg3.setZValue(999) # coloca proximo do topo da pilha de renderização
        self.scene.addItem(self.bg3)
    
        
        # 2. Contorno da propriedade (polígono irregular do quarteirão)
        self.polygon = QPolygonF([
            QPointF(30, 50),
            QPointF(555+(K/2),50),
            QPointF(570+(K/2), 75),
            QPointF(610+(K/2), 75),
            QPointF(625+(K/2), 50),
            QPointF(1120+(K), 50),
            QPointF(1120+(K), 760+J),
            QPointF(1070+(K), 810+J),
            QPointF(620+(K/2), 810+J),
            QPointF(605+(K/2), 795+J),
            QPointF(585+(K/2), 795+J),
            QPointF(570+(K/2), 810+J),
            QPointF(80, 810+J),
            QPointF(30, 760+J)
        ])

        self.prop_item = QGraphicsPolygonItem(self.polygon)
        self.prop_item.setPen(QPen(QColor("#292727"), 6, Qt.SolidLine))  # borda 
        self.prop_item.setBrush(QBrush(QColor(0, 255, 0, 30)))  # preenchimento semi-transparente
        self.scene.addItem(self.prop_item)

        # 3. Estacionamento interno 
        self.pen_bloco = QPen(QColor("#ffff00"), 2)
        self.brush_vaga = QBrush(QColor(255, 255, 0, 40))

        # bloco 1 
        self.bloco1 = QGraphicsRectItem(160, 180, 410+(K/2), 180+(K/2)) # desenha um bloco na area da propriedade
        self.bloco1.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.bloco1.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.bloco1) # insere o bloco no cenário
        # bloco 1 - nome do bloco
        self.bloco1_text = QGraphicsTextItem("Bloco 1") # texto do nome do bloco
        self.bloco1_text.setPos(215+(K/2), 170+(K/2))
        self.bloco1_text.setFont(QFont("Arial", 14)) # define a fonte do texto
        self.bloco1_text.setDefaultTextColor(QColor("white"))
        self.scene.addItem(self.bloco1_text) #insere o numero da vaga no cenario

        # bloco 2 
        self.bloco2 = QGraphicsRectItem(160, 700, 410+(K/2), 180+(K/2)) # desenha um bloco na area da propriedade
        self.bloco2.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.bloco2.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.bloco2) # insere o bloco no cenário
        # bloco 2 - nome do bloco
        self.bloco2_text = QGraphicsTextItem("Bloco 2") # texto do nome do bloco
        self.bloco2_text.setPos(215+(K/2), 690+(K/2))
        self.bloco2_text.setFont(QFont("Arial", 14)) # define a fonte do texto
        self.bloco2_text.setDefaultTextColor(QColor("white"))
        self.scene.addItem(self.bloco2_text) #insere o numero da vaga no cenario

        # bloco 3 
        self.bloco3 = QGraphicsRectItem(620+(K/2), 180, 410+(K/2), 180+(K/2)) # desenha um bloco na area da propriedade
        self.bloco3.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.bloco3.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.bloco3) # insere o bloco no cenário
        # bloco 3 - nome do bloco
        self.bloco3_text = QGraphicsTextItem("Bloco 3") # texto do nome do bloco
        self.bloco3_text.setPos(850+(K/2), 170+(K/2))
        self.bloco3_text.setFont(QFont("Arial", 14)) # define a fonte do texto
        self.bloco3_text.setDefaultTextColor(QColor("white"))
        self.scene.addItem(self.bloco3_text) #insere o numero da vaga no cenario

        # bloco 4 
        self.bloco4 = QGraphicsRectItem(620+(K/2), 700, 410+(K/2), 180+(K/2)) # desenha um bloco na area da propriedade
        self.bloco4.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.bloco4.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.bloco4) # insere o bloco no cenário
        # bloco 4 - nome do bloco
        self.bloco4_text = QGraphicsTextItem("Bloco 4") # texto do nome do bloco
        self.bloco4_text.setPos(850+(K/2), 690+(K/2))
        self.bloco4_text.setFont(QFont("Arial", 14)) # define a fonte do texto
        self.bloco4_text.setDefaultTextColor(QColor("white"))
        self.scene.addItem(self.bloco4_text) #insere o numero da vaga no cenario

        #recepção
        self.recepcao = QGraphicsPolygonItem(QPolygonF([
            QPointF(570+(K/2),535),
            QPointF(573+(K/2),525),
            QPointF(585+(K/2),515),
            QPointF(605+(K/2),515),
            QPointF(616+(K/2),525),
            QPointF(620+(K/2),535),
            QPointF(620+(K/2),725),
            QPointF(616+(K/2),735),
            QPointF(605+(K/2),745),
            QPointF(585+(K/2),745),
            QPointF(573+(K/2),735),
            QPointF(570+(K/2),725)
        ]))
        self.recepcao.setPen(self.pen_bloco)   # borda 
        self.recepcao.setBrush(self.brush_vaga) # preenchimento
        self.scene.addItem(self.recepcao)
        self.recepcao_text = QGraphicsTextItem("Recepção") # texto do nome do bloco
        self.recepcao_text.setPos(567+(K/2), 620)
        self.recepcao_text.setFont(QFont("Arial", 8)) # define a fonte do texto
        self.recepcao_text.setDefaultTextColor(QColor("white"))
        self.scene.addItem(self.recepcao_text) #insere o numero da vaga no c

        #torre
        self.torre = QGraphicsEllipseItem(650+(K/2), 340+(K/1.5), 60, 60)
        self.torre.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.torre.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.torre) # insere o bloco no cenário

        #bloco desconhecido
        self.bloco5 = QGraphicsRectItem(740+(K/2), 335+(K/1.5), 100, 70) # desenha um bloco na area da propriedade
        self.bloco5.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.bloco5.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.bloco5) # insere o bloco no cenário


        #Entrada/saída 1
        self.Entrada_saida_1 = QGraphicsPolygonItem(QPolygonF([
            QPointF(30, 760+J),
            QPointF(40, 760+J),
            QPointF(80, 800+J),
            QPointF(80, 810+J)
        ]))
        self.Entrada_saida_1.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.Entrada_saida_1.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.Entrada_saida_1) # insere o bloco no cenário

        #Entrada/saída 2
        self.Entrada_saida_2 = QGraphicsPolygonItem(QPolygonF([
            QPointF(1070+(K), 810+J),
            QPointF(1070+(K), 800+J),
            QPointF(1110+(K), 760+J),
            QPointF(1120+(K), 760+J)
        ]))
        self.Entrada_saida_2.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.Entrada_saida_2.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.Entrada_saida_2) # insere o bloco no cenário

        #Entrada/saída 3
        self.Entrada_saida_3 = QGraphicsPolygonItem(QPolygonF([
            QPointF(620+(K/2), 810+J),
            QPointF(605+(K/2), 795+J),
            QPointF(585+(K/2), 795+J),
            QPointF(570+(K/2), 810+J)
        ]))
        self.Entrada_saida_3.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.Entrada_saida_3.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.Entrada_saida_3) # insere o bloco no cenário

        #Entrada/saída 4
        self.Entrada_saida_4 = QGraphicsPolygonItem(QPolygonF([
            QPointF(555+(K/2),50),
            QPointF(570+(K/2), 75),
            QPointF(610+(K/2), 75),
            QPointF(625+(K/2), 50)
        ]))
        self.Entrada_saida_4.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.Entrada_saida_4.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.Entrada_saida_4) # insere o bloco no cenário

        #Lixeira
        self.lixeira = QGraphicsRectItem(-40+(K/2), 1290, 140, 40)
        self.lixeira.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.lixeira.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.lixeira) # insere o bloco no cenário
        self.lixeira_text = QGraphicsTextItem("Lixeira") # texto do nome do bloco
        self.lixeira_text.setPos(10+(K/2), 1300)
        self.lixeira_text.setFont(QFont("Arial", 8)) # define a fonte do texto
        self.lixeira_text.setDefaultTextColor(QColor("white"))
        self.scene.addItem(self.lixeira_text) #insere o numero da vaga no c

        # Guarita 1
        self.guarita = QGraphicsRectItem(635+(K/2), 60, 140, 40)
        self.guarita.setPen(self.pen_bloco) # define a cor da borda do bloco
        self.guarita.setBrush(self.brush_vaga) # define a cor de preenchimento interno do bloco
        self.scene.addItem(self.guarita) # insere o bloco no cenário
        self.guarita_text = QGraphicsTextItem("Guarita") # texto do nome do bloco
        self.guarita_text.setPos(685+(K/2), 70)
        self.guarita_text.setFont(QFont("Arial", 8)) # define a fonte do texto
        self.guarita_text.setDefaultTextColor(QColor("white"))
        self.scene.addItem(self.guarita_text) # insere o texto no cenário

        # Guarita 2
        self.guarita2 = QGraphicsRectItem()
        self.guarita2.setPen(self.pen_bloco)
        self.guarita2.setBrush(self.brush_vaga)
        self.scene.addItem(self.guarita2)


        #==============================================================================================
        # Inserção de self.vagas de estacionamento
        #==============================================================================================
        
        self.vagas = [] # lista com todas as self.vagas disponíveis

        #_______________________
        #Vagas INFERIOR ESQUERDO
        #SESP
        self.vagas.append(vg.Vaga(1, 4, "SESP", 120+D, 1100, 135))
        self.vagas.append(vg.Vaga(2, 4, "SESP", 160+D, 1100, 135))
        self.vagas.append(vg.Vaga(3, 4, "SESP", 200+D, 1100, 135))
        self.vagas.append(vg.Vaga(4, 4, "SESP", 240+D, 1100, 135))
        self.vagas.append(vg.Vaga(5, 4, "SESP", 280+D, 1100, 135))
        self.vagas.append(vg.Vaga(6, 4, "SESP", 320+D, 1100, 135))
        self.vagas.append(vg.Vaga(7, 4, "SESP", 360+D, 1100, 135))
        self.vagas.append(vg.Vaga(8, 4, "SESP", 400+D, 1100, 135))
        self.vagas.append(vg.Vaga(9, 4, "SESP", 440+D, 1100, 135))
        self.vagas.append(vg.Vaga(10, 4, "SESP", 480+D, 1100, 135))
        self.vagas.append(vg.Vaga(11, 4, "SESP", 520+D, 1100, 135))
        self.vagas.append(vg.Vaga(12, 4, "SESP", 560+D, 1100, 135))
        #Especial p/ deficiente
        self.vagas.append(vg.Vaga(13, 5, "Deficiente", 600+D, 1100, 135))
        self.vagas.append(vg.Vaga(14, 5, "Deficiente", 640+D, 1100, 135))
        self.vagas.append(vg.Vaga(15, 5, "Deficiente", 680+D, 1100, 135))
        #SESP
        self.vagas.append(vg.Vaga(33, 4, "SESP", 280+D, 1290, 225))
        self.vagas.append(vg.Vaga(34, 4, "SESP", 320+D, 1290, 225))
        self.vagas.append(vg.Vaga(35, 4, "SESP", 360+D, 1290, 225))
        self.vagas.append(vg.Vaga(36, 4, "SESP", 400+D, 1290, 225))
        self.vagas.append(vg.Vaga(37, 4, "SESP", 440+D, 1290, 225))
        #COHAPAR
        self.vagas.append(vg.Vaga(38, 3, "COHAPAR", 480+D, 1290, 225))
        self.vagas.append(vg.Vaga(39, 3, "COHAPAR", 520+D, 1290, 225))
        self.vagas.append(vg.Vaga(40, 3, "COHAPAR", 560+D, 1290, 225))
        self.vagas.append(vg.Vaga(41, 3, "COHAPAR", 600+D, 1290, 225))
        self.vagas.append(vg.Vaga(42, 3, "COHAPAR", 640+D, 1290, 225))
        self.vagas.append(vg.Vaga(43, 3, "COHAPAR", 680+D, 1290, 225))

        #______________________
        #Vagas INFERIOR DIREITO
        #SEIA
        self.vagas.append(vg.Vaga(16, 1, "SEIA", 800+D, 1095, 135))
        self.vagas.append(vg.Vaga(17, 1, "SEIA", 840+D, 1095, 135))
        self.vagas.append(vg.Vaga(18, 1, "SEIA", 880+D, 1095, 135))
        self.vagas.append(vg.Vaga(19, 1, "SEIA", 920+D, 1095, 135))
        self.vagas.append(vg.Vaga(20, 1, "SEIA", 960+D, 1095, 135))
        self.vagas.append(vg.Vaga(21, 1, "SEIA", 1000+D, 1095, 135))
        self.vagas.append(vg.Vaga(22, 1, "SEIA", 1040+D, 1095, 135))
        self.vagas.append(vg.Vaga(23, 1, "SEIA", 1080+D, 1095, 135))
        self.vagas.append(vg.Vaga(24, 1, "SEIA", 1120+D, 1095, 135))
        self.vagas.append(vg.Vaga(25, 1, "SEIA", 1160+D, 1095, 135))
        self.vagas.append(vg.Vaga(26, 1, "SEIA", 1200+D, 1095, 135))
        self.vagas.append(vg.Vaga(27, 1, "SEIA", 1240+D, 1095, 135))
        self.vagas.append(vg.Vaga(28, 1, "SEIA", 1280+D, 1095, 135))
        self.vagas.append(vg.Vaga(29, 1, "SEIA", 1320+D, 1095, 135))
        # Especial p/ deficiente
        self.vagas.append(vg.Vaga(142, 5, "Deficiente", 780+D, 1285, 225))
        #SEIA
        self.vagas.append(vg.Vaga(143, 1, "SEIA", 820+D, 1285, 225))
        self.vagas.append(vg.Vaga(44, 1, "SEIA", 860+D, 1285, 225))
        self.vagas.append(vg.Vaga(45, 1, "SEIA", 900+D, 1285, 225))
        self.vagas.append(vg.Vaga(46, 1, "SEIA", 940+D, 1285, 225))
        self.vagas.append(vg.Vaga(47, 1, "SEIA", 980+D, 1285, 225))
        self.vagas.append(vg.Vaga(48, 1, "SEIA", 1020+D, 1285, 225))
        self.vagas.append(vg.Vaga(49, 1, "SEIA", 1060+D, 1285, 225))
        self.vagas.append(vg.Vaga(50, 1, "SEIA", 1100+D, 1285, 225))
        self.vagas.append(vg.Vaga(51, 1, "SEIA", 1140+D, 1285, 225))
        self.vagas.append(vg.Vaga(52, 1, "SEIA", 1180+D, 1285, 225))
        self.vagas.append(vg.Vaga(53, 1, "SEIA", 1220+D, 1285, 225)) 
        self.vagas.append(vg.Vaga(54, 1, "SEIA", 1260+D, 1285, 225))
        self.vagas.append(vg.Vaga(55, 1, "SEIA", 1300+D, 1285, 225)) 
        self.vagas.append(vg.Vaga(56, 1, "SEIA", 1340+D, 1285, 225))
        self.vagas.append(vg.Vaga(57, 1, "SEIA", 1380+D, 1285, 225))  

        #______________________
        # Vagas LATERAL DIREITA
        #COHAPAR
        self.vagas.append(vg.Vaga(58, 3, "COHAPAR", 1420+D, 1230, 135))  
        self.vagas.append(vg.Vaga(59, 3, "COHAPAR", 1420+D, 1190, 135))
        self.vagas.append(vg.Vaga(60, 3, "COHAPAR", 1420+D, 1150, 135))
        self.vagas.append(vg.Vaga(61, 3, "COHAPAR", 1420+D, 1110, 135))
        self.vagas.append(vg.Vaga(62, 3, "COHAPAR", 1420+D, 1070, 135))
        self.vagas.append(vg.Vaga(63, 3, "COHAPAR", 1420+D, 1030, 135))
        self.vagas.append(vg.Vaga(64, 3, "COHAPAR", 1420+D, 990, 135))
        self.vagas.append(vg.Vaga(65, 3, "COHAPAR", 1420+D, 950, 135))
        self.vagas.append(vg.Vaga(66, 3, "COHAPAR", 1420+D, 910, 135))
        self.vagas.append(vg.Vaga(67, 3, "COHAPAR", 1420+D, 870, 135))
        self.vagas.append(vg.Vaga(68, 3, "COHAPAR", 1420+D, 830, 135))
        self.vagas.append(vg.Vaga(69, 3, "COHAPAR", 1420+D, 790, 135))
        self.vagas.append(vg.Vaga(70, 3, "COHAPAR", 1420+D, 750, 135))
        self.vagas.append(vg.Vaga(71, 3, "COHAPAR", 1420+D, 710, 135))
        self.vagas.append(vg.Vaga(72, 3, "COHAPAR", 1420+D, 670, 135))
        self.vagas.append(vg.Vaga(73, 3, "COHAPAR", 1420+D, 630, 135))
        self.vagas.append(vg.Vaga(74, 3, "COHAPAR", 1420+D, 590, 135))
        self.vagas.append(vg.Vaga(75, 3, "COHAPAR", 1420+D, 550, 135))
        self.vagas.append(vg.Vaga(76, 3, "COHAPAR", 1420+D, 510, 135))
        self.vagas.append(vg.Vaga(77, 3, "COHAPAR", 1420+D, 470, 135))
        self.vagas.append(vg.Vaga(78, 3, "COHAPAR", 1420+D, 430, 135))
        self.vagas.append(vg.Vaga(79, 3, "COHAPAR", 1420+D, 390, 135))
        self.vagas.append(vg.Vaga(80, 3, "COHAPAR", 1420+D, 350, 135))
        #SESP
        self.vagas.append(vg.Vaga(81, 4, "SESP", 1420+D, 310, 135))
        self.vagas.append(vg.Vaga(82, 4, "SESP", 1420+D, 270, 135))
        self.vagas.append(vg.Vaga(83, 4, "SESP", 1420+D, 230, 135))
        self.vagas.append(vg.Vaga(84, 4, "SESP", 1420+D, 190, 135))
        self.vagas.append(vg.Vaga(85, 4, "SESP", 1420+D, 150, 135))
        self.vagas.append(vg.Vaga(86, 4, "SESP", 1420+D, 110, 135))
        self.vagas.append(vg.Vaga(87, 4, "SESP", 1420+D, 70, 135))
            
        #______________________
        # Vagas SUPERIOR DIREITA
        #SESP
        self.vagas.append(vg.Vaga(88, 4, "SESP", 1300+D, 70, 45))
        self.vagas.append(vg.Vaga(89, 4, "SESP", 1260+D, 70, 45))
        self.vagas.append(vg.Vaga(90, 4, "SESP", 1220+D, 70, 45))
        self.vagas.append(vg.Vaga(91, 4, "SESP", 1180+D, 70, 45))
        self.vagas.append(vg.Vaga(92, 4, "SESP", 1140+D, 70, 45))
        self.vagas.append(vg.Vaga(93, 4, "SESP", 1100+D, 70, 45))
        self.vagas.append(vg.Vaga(94, 4, "SESP", 1060+D, 70, 45))
        self.vagas.append(vg.Vaga(95, 4, "SESP", 1020+D, 70, 45))
        self.vagas.append(vg.Vaga(96, 4, "SESP", 980+D, 70, 45))


        #________________________
        # Vagas SUPERIOR ESQUERDO
        #SEJU
        self.vagas.append(vg.Vaga(110, 2, "SEJU", 0+D, 70, 45)) # exemplo de vaga - id=1, tipo hatch, posicao x=60 y=60, sem rotacao
        self.vagas.append(vg.Vaga(109, 2, "SEJU", 40+D, 70, 45)) 
        self.vagas.append(vg.Vaga(108, 2, "SEJU", 80+D, 70, 45)) 
        self.vagas.append(vg.Vaga(107, 2, "SEJU", 120+D, 70, 45))
        self.vagas.append(vg.Vaga(106, 2, "SEJU", 160+D, 70, 45)) 
        self.vagas.append(vg.Vaga(105, 2, "SEJU", 200+D, 70, 45))
        self.vagas.append(vg.Vaga(104, 2, "SEJU", 240+D, 70, 45)) 
        self.vagas.append(vg.Vaga(103, 2, "SEJU", 280+D, 70, 45))
        self.vagas.append(vg.Vaga(102, 2, "SEJU", 320+D, 70, 45)) 
        self.vagas.append(vg.Vaga(101, 2, "SEJU", 360+D, 70, 45))
        self.vagas.append(vg.Vaga(100, 2, "SEJU", 400+D, 70, 45)) 
        self.vagas.append(vg.Vaga(99, 2, "SEJU", 440+D, 70, 45))
        self.vagas.append(vg.Vaga(98, 2, "SEJU", 480+D, 70, 45)) 
        self.vagas.append(vg.Vaga(97, 2, "SEJU", 520+D, 70, 45))
        #SESP
        self.vagas.append(vg.Vaga(196, 2, "SESP", 560+D, 70, 45)) 
        self.vagas.append(vg.Vaga(197, 2, "SESP", 600+D, 70, 45)) 
        self.vagas.append(vg.Vaga(198, 4, "SESP", 640+D, 70, 45)) 
        self.vagas.append(vg.Vaga(199, 4, "SESP", 680+D, 70, 45)) 


        #_______________________
        # Vagas LATERAL ESQUERDA
        #SEJU
        self.vagas.append(vg.Vaga(111, 2, "SEJU", 0+D, 130, 315))
        self.vagas.append(vg.Vaga(112, 2, "SEJU", 0+D, 170, 315))
        self.vagas.append(vg.Vaga(113, 2, "SEJU", 0+D, 210, 315))
        self.vagas.append(vg.Vaga(114, 2, "SEJU", 0+D, 250, 315))
        self.vagas.append(vg.Vaga(115, 2, "SEJU", 0+D, 290, 315))
        self.vagas.append(vg.Vaga(116, 2, "SEJU", 0+D, 330, 315))
        self.vagas.append(vg.Vaga(117, 2, "SEJU", 0+D, 370, 315))
        self.vagas.append(vg.Vaga(118, 2, "SEJU", 0+D, 410, 315))
        self.vagas.append(vg.Vaga(119, 2, "SEJU", 0+D, 450, 315))
        self.vagas.append(vg.Vaga(120, 2, "SEJU", 0+D, 490, 315))
        self.vagas.append(vg.Vaga(121, 2, "SEJU", 0+D, 530, 315))
        self.vagas.append(vg.Vaga(122, 2, "SEJU", 0+D, 570, 315))
        self.vagas.append(vg.Vaga(123, 2, "SEJU", 0+D, 610, 315))
        #COHAPAR
        self.vagas.append(vg.Vaga(124, 3, "COHAPAR", 0+D, 650, 315))
        self.vagas.append(vg.Vaga(125, 3, "COHAPAR", 0+D, 690, 315))
        self.vagas.append(vg.Vaga(126, 3, "COHAPAR", 0+D, 730, 315))
        self.vagas.append(vg.Vaga(127, 3, "COHAPAR", 0+D, 770, 315))
        self.vagas.append(vg.Vaga(128, 3, "COHAPAR", 0+D, 810, 315))
        self.vagas.append(vg.Vaga(129, 3, "COHAPAR", 0+D, 850, 315))
        self.vagas.append(vg.Vaga(130, 3, "COHAPAR", 0+D, 890, 315))
        self.vagas.append(vg.Vaga(131, 3, "COHAPAR", 0+D, 930, 315))
        self.vagas.append(vg.Vaga(132, 3, "COHAPAR", 0+D, 970, 315))
        self.vagas.append(vg.Vaga(133, 3, "COHAPAR", 0+D, 1010, 315))
        self.vagas.append(vg.Vaga(134, 3, "COHAPAR", 0+D, 1050, 315))
        self.vagas.append(vg.Vaga(135, 3, "COHAPAR", 0+D, 1090, 315))
        self.vagas.append(vg.Vaga(136, 3, "COHAPAR", 0+D, 1130, 315))
        self.vagas.append(vg.Vaga(137, 3, "COHAPAR", 0+D, 1170, 315))
        self.vagas.append(vg.Vaga(138, 3, "COHAPAR", 0+D, 1210, 315))

        #==============================================================================================
        # Criando a lista de circulos com o numero das vagas - view 2
        #==============================================================================================

        self.circulos = []    
        
        #==============================================================================================
        # Inicializando o banco de dados MySQL
        #==============================================================================================
        self.conn = self.initDatabaseMySQL()


        #==============================================================================================
        # Sidebar lateral direita para exibição das informações
        #==============================================================================================
        sidebar = sb.Sidebar(self, WIDTH, HEIGHT, J, POS_X_SIDEBAR) # cria a sidebar passando o tamanho da janela para ajustar o layout


        #==============================================================================================
        # Inserindo as vagas com imagens e circulos e inserindo 'ouvintes' pra atualizar informações 
        #==============================================================================================
        for vaga in self.vagas:
            vaga.habilitar_sidebar.connect(sidebar.controlActions) # conecta o sinal da vaga para atualizar a sidebar automaticamente quando o valor da variavel habilitar_sidebar for alterado
            if vaga.tipo_carro == 1: # SEIA
                circle = self.insertCircle(vaga.getVagaID(), vaga.getX(), vaga.getY(), PEN_VERDE, BRUSH_VERDE) # gerando os circulos com o numero das vagas
            elif vaga.tipo_carro == 2: # SEJU
                circle = self.insertCircle(vaga.getVagaID(), vaga.getX(), vaga.getY(), PEN_ROSA, BRUSH_ROSA)
            elif vaga.tipo_carro == 3: # COHAPAR
                circle = self.insertCircle(vaga.getVagaID(), vaga.getX(), vaga.getY(), PEN_ROXO, BRUSH_ROXO)
            elif vaga.tipo_carro == 4: # SESP
                circle = self.insertCircle(vaga.getVagaID(), vaga.getX(), vaga.getY(), PEN_AZUL, BRUSH_AZUL)
            else:
                circle = self.insertCircle(vaga.getVagaID(), vaga.getX(), vaga.getY(), self.pen_bloco, self.brush_vaga)

            self.circulos.append(circle) # inserindo na lista pra fácil manipulação posterior
            self.scene.addItem(vaga) # insere a vaga (imagem) no cenário
            #circle.setWindowOpacity(0.01)

        
        self.updateStatusVagas() # atualizando o status das vagas conforme dados do Registro do Banco de Dados
        sidebar.signal_insert.connect(self.updateStatusVagas) 

        self.generateLegenda() # gerando as legendas

        #==============================================================================================
        # Inserindo toggle switch pra alternar entre formas geometricas e imagens (views)
        #==============================================================================================

        # Toggle Switch customizado via stylesheet
        self.toggle = QCheckBox()
        self.toggle.setCheckable(True)
        self.toggle.setStyleSheet(self.recursos.ESTILOS.estilo_toggle_switch)
        self.toggle.setText("DISPOSIÇÃO DAS VAGAS")

        proxy_toggle = QGraphicsProxyWidget()
        proxy_toggle.setWidget(self.toggle)
        proxy_toggle.setPos(25, 10)
        proxy_toggle.setZValue(1000) # força a ficar no topo da pilha de renderização
        self.scene.addItem(proxy_toggle)
        
        self.toggle.toggled.connect(self.alternar_view)

        
        #==============================================================================================
        # Copyright
        #==============================================================================================

        #copyright = QGraphicsTextItem("                                                                                                                                                  © 2026 SEIA Parking Management "+ver+".\n Todos os direitos reservados ao Supervisor Especialista em Governança Digital & Transformação Digital André Luis Costa Batistela - um dos nomes mais proeminentes da Diretoria de Inovação e um dos pilares da Inovação no Estado do Paraná.")
        copyright = QGraphicsTextItem(
            "      © 2026 SEIA Parking Management " + ver + ". Todos os direitos reservados.\n"
            "               Secretaria de Inovação e Inteligência Artificial (SEIA)\n"
            "                             Diretoria de Inovação (DIN)\n"
            "               Desenvolvido por Pablo F. L. (github.com/PabloFrLz)" 
        )        
        copyright.setFont(self.recursos.FONTES.fonte_copyright)
        copyright.setDefaultTextColor(QColor("gray"))
        copyright.setPos(WIDTH+230, HEIGHT+J-120)
        copyright.setZValue(10)
        self.scene.addItem(copyright)

        #==============================================================================================
        # Configurações finais
        #==============================================================================================
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(sidebar)
        proxy.setPos(POS_X_SIDEBAR, 0)
        self.scene.addItem(proxy) # insere a sidebar no cenário
        self.scale(0.85, 0.85)
        self.delayApresentacao(10.0) # alterna a view de blocos geometricos para edificio com o delay especificado de 10 segundos

        # Ajusta a visão inicial
        #self.fitInView(self.bg, Qt.KeepAspectRatio)
    
    """
    def wheelEvent(self, event):
        # Zoom com roda do mouse
        factor = 1.15 if event.angleDelta().y() > 0 else 0.85
        self.scale(factor, factor)
    """

    def initDatabaseMySQL(self):
        # Configurações de conexão com o banco de dados MySQL
        self.conn = pymysql.connect(
            host='localhost',
            user=USER,
            password=PASSWORD,
            database='seia_parking'
        )

        return self.conn
    
    def updateStatusVagas(self):
        cursor = self.conn.cursor()
        cursor.execute("select * from registro")
        registro = cursor.fetchall()

        for vaga in self.vagas:
            for tupla in registro:
                if vaga.getVagaID() == tupla[3]: #identifica se esta inserido no registro
                    if tupla[6] == "ENTRADA":
                        vaga.setStatus(1) # ocupado
                        vaga.active_monocromatico() # volta a cor original da imagem caso tenha aplicado monocromatico
                    elif tupla[6] == "SAIDA":
                        vaga.setStatus(0) # disponível
                        vaga.active_monocromatico() #aplica efeito monocromatico
                    elif tupla[6] == "RESERVA":
                        vaga.setStatus(2) # reserva
                    
                    vaga.ligar_led() # liga o led pra refletir o estado atual davaga

    
    def show_message(self, titulo, texto):
        msg = QMessageBox(self)                    # importante passar o parent
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setIcon(QMessageBox.Icon.Warning)     # ou Information, Critical...
        # Força não usar diálogo nativo (deve ser antes do exec/show)
        msg.setOption(QMessageBox.Option.DontUseNativeDialog, True)
        msg.exec()   

    def alternar_view(self): # alterna entre view 1 (objetos geometricos) e view 2 (imagens 3D)
        if self.turnRound:
            #esconde os objetos geometricos
            self.bloco1.hide()
            self.bloco2.hide()
            self.bloco3.hide()
            self.bloco4.hide()
            self.bloco5.hide()
            self.recepcao.hide()
            self.torre.hide()
            for circle in self.circulos:
                circle[0].hide()
                circle[1].hide()
            for legenda in self.legendas:
                legenda[0].hide()
                legenda[1].hide()
            #aparece suavemente
            self.fade_in(self.bg3)
            for vaga in self.vagas:
                vaga.show()

        else:
            # Imagem desaparece suavemente
            self.fade_out(self.bg3)
            for vaga in self.vagas:
                vaga.hide()
            # mostra os objetos geometricos
            self.bloco1.show()
            self.bloco2.show()
            self.bloco3.show()
            self.bloco4.show()
            self.bloco5.show()
            self.recepcao.show()
            self.torre.show()
            for circle in self.circulos:
                circle[0].show()
                circle[1].show()
            for legenda in self.legendas:
                legenda[0].show()
                legenda[1].show()
            
        
        self.turnRound = not self.turnRound
    
    def fade_out(self, item): # metodo que decrementa opacidade até 0.01 - efeito de desaparecimento suave
        if not hasattr(item, 'opacity_effect'):
            effect = QGraphicsOpacityEffect()
            item.setGraphicsEffect(effect)
            item.opacity_effect = effect
        else:
            effect = item.opacity_effect

        self.anim = QPropertyAnimation(effect, b"opacity")
        self.anim.setDuration(1500)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.01) # não pode ser 0.0 se nao da bug
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()
        # Opcional: esconder de verdade no final
        self.anim.finished.connect(lambda: item.setOpacity(0.01))
    
    def fade_in(self, item): # metodo que incrementa a opacidade até 1.0 - efeito de reaparecimento suave
        if not hasattr(item, 'opacity_effect'):
            effect = QGraphicsOpacityEffect()
            item.setGraphicsEffect(effect)
            item.opacity_effect = effect
        else:
            effect = item.opacity_effect

        self.anim = QPropertyAnimation(effect, b"opacity")
        self.anim.setDuration(1500)
        self.anim.setStartValue(0.01)# não pode ser 0.0 se não da bug
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()
        # Opcional: esconder de verdade no final
        self.anim.finished.connect(lambda: item.setOpacity(1.0))

    def delayApresentacao(self, sec):
        # Cria um timer
        timer = threading.Timer(sec, self.alternar_view())
        timer.start()

    def insertCircle(self, numero, x, y, paint1, paint2):
        # Circulo
        circulo = QGraphicsEllipseItem(x, y, LARGURA_CIRCLE, ALTURA_CIRCLE)
        circulo.setPen(paint1)
        circulo.setBrush(paint2)
        self.scene.addItem(circulo) # insere no cenário

        # Texto
        texto = QGraphicsTextItem(str(numero))
        texto.setDefaultTextColor(Qt.GlobalColor.white)
        texto.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        if(numero >= 100): # centralizar corretamente numero com 3 digitos
            x_relativo = x + 3
        elif(numero <= 9):
            x_relativo = x + 13
        else:
            x_relativo = x + 8
        texto.setPos(x_relativo, y + 8)   # ajuste manual do posicionamento
        self.scene.addItem(texto) # insere no cenário

        return circulo, texto
    
    def generateLegenda(self): # gera a legenda das cores pra se orientar melhor
        #self.legendas = QVBoxLayout() # conteiner lateral pra agrupar um em baixo do outro
        self.legendas = []
        orgaos = ["Secretaria da Inovação e Inteligência Artificial (SEIA)", 
                  "Secretaria de Estado de Justiça e Cidadania (SEJU)", 
                  "Companhia de Habitação do Paraná (COHAPAR)", 
                  "Secretaria de Estado de Segurança Pública (SESP)"]
        pen = [PEN_VERDE, PEN_ROSA, PEN_ROXO, PEN_AZUL]
        brush = [BRUSH_VERDE, BRUSH_ROSA, BRUSH_ROXO, BRUSH_AZUL]
        x = 160
        y = 590
        desl_y = 0

        for i in range(4):
            item = QGraphicsRectItem(x, y + desl_y, 15, 10)
            item.setPen(pen[i])
            item.setBrush(brush[i]) 
            item_text = QGraphicsTextItem(orgaos[i]) # texto do nome do bloco
            item_text.setPos(x + 20, y + desl_y-6)
            item_text.setFont(QFont("Arial", 10)) # define a fonte do texto
            item_text.setDefaultTextColor(QColor("white"))
            self.scene.addItem(item) 
            self.scene.addItem(item_text) 
            desl_y += 20

            self.legendas.append([item, item_text]) # insere as legendas como tuplas (QUADRADO + TEXTO DESCRITIVO)
    
    def processarVagaBuscada(self):
        pass


app = QApplication(sys.argv)
app.setStyleSheet(
    qdarktheme.load_stylesheet("dark") + 
    """
    QToolTip {
        background-color: #000000;
        color: grey;
        border: 1px solid #5a5a5a;
        padding: 5px;
        font-size: 10pt;
        opacity: 0.75;
    }
    """
) # [v1.0.0.03]: adaptado pra estilizar a Qtooltip dos objetos Vaga()
viewer = SEIAParkingManagement()
viewer.setWindowTitle("SEIA Parking Management - "+ver)
viewer.setFixedSize(WIDTH+K-240, HEIGHT+150)
viewer.scale(0.85, 0.85)
viewer.show()
sys.exit(app.exec())



