"""
    Subject: Software de gerenciamento de vagas de estacionamento das dependências do SEIA, 
             desenvolvido para o núcleo Administrativo Setorial (NAS) e para a Guarita do 
             edifício onde a secretaria está lotada. Projeto conduzido pelo núcleo de Diretoria
             em Inovação (DIN), vinculado à Secretaria da Inovação e Inteligência Artificial (SEIA), 
             do Estado do Paraná.
    Tools: Python3, PySide6, MySQL, PyQtDarkTheme, Photoshop CC 2015, Github  
    Author: Pablo Franco Luz (pablo-tr1@hotmail.com - https://github.com/PabloFrLz)
    Supervisor: André Luis Costa Batistela 
    Sector: Diretoria de Inovação (DIN)
    Ver.: 1.0.0.01
    Start: 31/03/2026 - 08:16PM
    End: Em andamento...
    Notas:
        1.   _________________________________________________________________________________________
            |      Dados para acesso ao banco de dados MySQL:                                         |                                                                                   |
            |      Comando: mysql -u "user" -p                                                        |             
            |      user: seia                                                                         |
            |      Senha: 5452                                                                        |                                                                                 |             
            |_________________________________________________________________________________________|



"""


import threading

from PySide6.QtWidgets import (
    QApplication, QCheckBox, QGraphicsItem, QGraphicsOpacityEffect, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QGraphicsProxyWidget, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout
)
from PySide6.QtGui import QPixmap, QPolygonF, QPen, QBrush, QColor, QPainter,QFont
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QPointF
import sys
import Vaga as vg
import Sidebar as sb
import qdarktheme
import pymysql

ver = "v1.0.0.02" # versão do software

#variaveis de autenticação do banco de dados
USER = 'root'
PASSWORD = '5452'

global WIDTH, HEIGHT, K, J
WIDTH = 1190
HEIGHT = 840
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
        

        #==============================================================================================
        # construção do cenário da propriedade (fundo, contorno, blocos, recepção, torre, entradas/saídas)
        #==============================================================================================

        # 1. Imagem de satélite como fundo
        self.pixmap = QPixmap("imagens/background-3.png") #imagem de plano de fundo
        self.bg = QGraphicsPixmapItem(self.pixmap)
        self.bg.setOpacity(0.85) # um pouco transparente para destacar desenho
        self.scene.addItem(self.bg)
        
        self.pixmap2 = QPixmap("logos/SEIA3.png") #imagem da secretaria
        self.bg2 = QGraphicsPixmapItem(self.pixmap2)
        self.bg2.setOpacity(0.05)
        self.bg2.setPos(WIDTH/2-80, HEIGHT/2) 
        self.scene.addItem(self.bg2)

        self.pixmap_edificios = QPixmap("imagens/edificacoes.png") #imagem da secretaria
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
        self.vagas.append(vg.Vaga(1, 4, 120+D, 1100, 135))
        self.vagas.append(vg.Vaga(2, 4, 160+D, 1100, 135))
        self.vagas.append(vg.Vaga(3, 4, 200+D, 1100, 135))
        self.vagas.append(vg.Vaga(4, 4, 240+D, 1100, 135))
        self.vagas.append(vg.Vaga(5, 4, 280+D, 1100, 135))
        self.vagas.append(vg.Vaga(6, 4, 320+D, 1100, 135))
        self.vagas.append(vg.Vaga(7, 4, 360+D, 1100, 135))
        self.vagas.append(vg.Vaga(8, 4, 400+D, 1100, 135))
        self.vagas.append(vg.Vaga(9, 4, 440+D, 1100, 135))
        self.vagas.append(vg.Vaga(10, 4, 480+D, 1100, 135))
        self.vagas.append(vg.Vaga(11, 4, 520+D, 1100, 135))
        self.vagas.append(vg.Vaga(12, 4, 560+D, 1100, 135))
        #Especial p/ deficiente
        self.vagas.append(vg.Vaga(13, 5, 600+D, 1100, 135))
        self.vagas.append(vg.Vaga(14, 5, 640+D, 1100, 135))
        self.vagas.append(vg.Vaga(15, 5, 680+D, 1100, 135))
        #SESP
        self.vagas.append(vg.Vaga(33, 4, 280+D, 1290, 225))
        self.vagas.append(vg.Vaga(34, 4, 320+D, 1290, 225))
        self.vagas.append(vg.Vaga(35, 4, 360+D, 1290, 225))
        self.vagas.append(vg.Vaga(36, 4, 400+D, 1290, 225))
        self.vagas.append(vg.Vaga(37, 4, 440+D, 1290, 225))
        #COHAPAR
        self.vagas.append(vg.Vaga(38, 3, 480+D, 1290, 225))
        self.vagas.append(vg.Vaga(39, 3, 520+D, 1290, 225))
        self.vagas.append(vg.Vaga(40, 3, 560+D, 1290, 225))
        self.vagas.append(vg.Vaga(41, 3, 600+D, 1290, 225))
        self.vagas.append(vg.Vaga(42, 3, 640+D, 1290, 225))
        self.vagas.append(vg.Vaga(43, 3, 680+D, 1290, 225))

        #______________________
        #Vagas INFERIOR DIREITO
        #SEIA
        self.vagas.append(vg.Vaga(16, 1, 780+D, 1095, 135))
        self.vagas.append(vg.Vaga(17, 1, 820+D, 1095, 135))
        self.vagas.append(vg.Vaga(18, 1, 860+D, 1095, 135))
        self.vagas.append(vg.Vaga(19, 1, 900+D, 1095, 135))
        self.vagas.append(vg.Vaga(20, 1, 940+D, 1095, 135))
        self.vagas.append(vg.Vaga(21, 1, 980+D, 1095, 135))
        self.vagas.append(vg.Vaga(22, 1, 1020+D, 1095, 135))
        self.vagas.append(vg.Vaga(23, 1, 1060+D, 1095, 135))
        self.vagas.append(vg.Vaga(24, 1, 1100+D, 1095, 135))
        self.vagas.append(vg.Vaga(25, 1, 1140+D, 1095, 135))
        self.vagas.append(vg.Vaga(26, 1, 1180+D, 1095, 135))
        self.vagas.append(vg.Vaga(27, 1, 1220+D, 1095, 135))
        self.vagas.append(vg.Vaga(28, 1, 1260+D, 1095, 135))
        self.vagas.append(vg.Vaga(29, 1, 1300+D, 1095, 135))
        # Especial p/ deficiente
        self.vagas.append(vg.Vaga(142, 5, 780+D, 1285, 225))
        #SEIA
        self.vagas.append(vg.Vaga(143, 1, 820+D, 1285, 225))
        self.vagas.append(vg.Vaga(44, 1, 860+D, 1285, 225))
        self.vagas.append(vg.Vaga(45, 1, 900+D, 1285, 225))
        self.vagas.append(vg.Vaga(46, 1, 940+D, 1285, 225))
        self.vagas.append(vg.Vaga(47, 1, 980+D, 1285, 225))
        self.vagas.append(vg.Vaga(48, 1, 1020+D, 1285, 225))
        self.vagas.append(vg.Vaga(49, 1, 1060+D, 1285, 225))
        self.vagas.append(vg.Vaga(50, 1, 1100+D, 1285, 225))
        self.vagas.append(vg.Vaga(51, 1, 1140+D, 1285, 225))
        self.vagas.append(vg.Vaga(52, 1, 1180+D, 1285, 225))
        self.vagas.append(vg.Vaga(53, 1, 1220+D, 1285, 225)) 
        self.vagas.append(vg.Vaga(54, 1, 1260+D, 1285, 225))
        self.vagas.append(vg.Vaga(55, 1, 1300+D, 1285, 225)) 
        self.vagas.append(vg.Vaga(56, 1, 1340+D, 1285, 225))
        self.vagas.append(vg.Vaga(57, 1, 1380+D, 1285, 225))  

        #______________________
        # Vagas LATERAL DIREITA
        #COHAPAR
        self.vagas.append(vg.Vaga(58, 3, 1420+D, 1230, 135))  
        self.vagas.append(vg.Vaga(59, 3, 1420+D, 1190, 135))
        self.vagas.append(vg.Vaga(60, 3, 1420+D, 1150, 135))
        self.vagas.append(vg.Vaga(61, 3, 1420+D, 1110, 135))
        self.vagas.append(vg.Vaga(62, 3, 1420+D, 1070, 135))
        self.vagas.append(vg.Vaga(63, 3, 1420+D, 1030, 135))
        self.vagas.append(vg.Vaga(64, 3, 1420+D, 990, 135))
        self.vagas.append(vg.Vaga(65, 3, 1420+D, 950, 135))
        self.vagas.append(vg.Vaga(66, 3, 1420+D, 910, 135))
        self.vagas.append(vg.Vaga(67, 3, 1420+D, 870, 135))
        self.vagas.append(vg.Vaga(68, 3, 1420+D, 830, 135))
        self.vagas.append(vg.Vaga(69, 3, 1420+D, 790, 135))
        self.vagas.append(vg.Vaga(70, 3, 1420+D, 750, 135))
        self.vagas.append(vg.Vaga(71, 3, 1420+D, 710, 135))
        self.vagas.append(vg.Vaga(72, 3, 1420+D, 670, 135))
        self.vagas.append(vg.Vaga(73, 3, 1420+D, 630, 135))
        self.vagas.append(vg.Vaga(74, 3, 1420+D, 590, 135))
        self.vagas.append(vg.Vaga(75, 3, 1420+D, 550, 135))
        self.vagas.append(vg.Vaga(76, 3, 1420+D, 510, 135))
        self.vagas.append(vg.Vaga(77, 3, 1420+D, 470, 135))
        self.vagas.append(vg.Vaga(78, 3, 1420+D, 430, 135))
        self.vagas.append(vg.Vaga(79, 3, 1420+D, 390, 135))
        self.vagas.append(vg.Vaga(80, 3, 1420+D, 350, 135))
        #SESP
        self.vagas.append(vg.Vaga(81, 4, 1420+D, 310, 135))
        self.vagas.append(vg.Vaga(82, 4, 1420+D, 270, 135))
        self.vagas.append(vg.Vaga(83, 4, 1420+D, 230, 135))
        self.vagas.append(vg.Vaga(84, 4, 1420+D, 190, 135))
        self.vagas.append(vg.Vaga(85, 4, 1420+D, 150, 135))
        self.vagas.append(vg.Vaga(86, 4, 1420+D, 110, 135))
        self.vagas.append(vg.Vaga(87, 4, 1420+D, 70, 135))
            
        #______________________
        # Vagas SUPERIOR DIREITA
        #SESP
        self.vagas.append(vg.Vaga(88, 4, 1300+D, 70, 45))
        self.vagas.append(vg.Vaga(89, 4, 1260+D, 70, 45))
        self.vagas.append(vg.Vaga(90, 4, 1220+D, 70, 45))
        self.vagas.append(vg.Vaga(91, 4, 1180+D, 70, 45))
        self.vagas.append(vg.Vaga(92, 4, 1140+D, 70, 45))
        self.vagas.append(vg.Vaga(93, 4, 1100+D, 70, 45))
        self.vagas.append(vg.Vaga(94, 4, 1060+D, 70, 45))
        self.vagas.append(vg.Vaga(95, 4, 1020+D, 70, 45))
        self.vagas.append(vg.Vaga(96, 4, 980+D, 70, 45))


        #________________________
        # Vagas SUPERIOR ESQUERDO
        #SEJU
        self.vagas.append(vg.Vaga(110, 2, 0+D, 70, 45)) # exemplo de vaga - id=1, tipo hatch, posicao x=60 y=60, sem rotacao
        self.vagas.append(vg.Vaga(109, 2, 40+D, 70, 45)) 
        self.vagas.append(vg.Vaga(108, 2, 80+D, 70, 45)) 
        self.vagas.append(vg.Vaga(107, 2, 120+D, 70, 45))
        self.vagas.append(vg.Vaga(106, 2, 160+D, 70, 45)) 
        self.vagas.append(vg.Vaga(105, 2, 200+D, 70, 45))
        self.vagas.append(vg.Vaga(104, 2, 240+D, 70, 45)) 
        self.vagas.append(vg.Vaga(103, 2, 280+D, 70, 45))
        self.vagas.append(vg.Vaga(102, 2, 320+D, 70, 45)) 
        self.vagas.append(vg.Vaga(101, 2, 360+D, 70, 45))
        self.vagas.append(vg.Vaga(100, 2, 400+D, 70, 45)) 
        self.vagas.append(vg.Vaga(99, 2, 440+D, 70, 45))
        self.vagas.append(vg.Vaga(98, 2, 480+D, 70, 45)) 
        self.vagas.append(vg.Vaga(97, 2, 520+D, 70, 45))
        #SESP
        self.vagas.append(vg.Vaga(196, 2, 560+D, 70, 45)) 
        self.vagas.append(vg.Vaga(197, 2, 600+D, 70, 45)) 
        self.vagas.append(vg.Vaga(198, 4, 640+D, 70, 45)) 
        self.vagas.append(vg.Vaga(199, 4, 680+D, 70, 45)) 


        #_______________________
        # Vagas LATERAL ESQUERDA
        #SEJU
        self.vagas.append(vg.Vaga(111, 2, 0+D, 130, 315))
        self.vagas.append(vg.Vaga(112, 2, 0+D, 170, 315))
        self.vagas.append(vg.Vaga(113, 2, 0+D, 210, 315))
        self.vagas.append(vg.Vaga(114, 2, 0+D, 250, 315))
        self.vagas.append(vg.Vaga(115, 2, 0+D, 290, 315))
        self.vagas.append(vg.Vaga(116, 2, 0+D, 330, 315))
        self.vagas.append(vg.Vaga(117, 2, 0+D, 370, 315))
        self.vagas.append(vg.Vaga(118, 2, 0+D, 410, 315))
        self.vagas.append(vg.Vaga(119, 2, 0+D, 450, 315))
        self.vagas.append(vg.Vaga(120, 2, 0+D, 490, 315))
        self.vagas.append(vg.Vaga(121, 2, 0+D, 530, 315))
        self.vagas.append(vg.Vaga(122, 2, 0+D, 570, 315))
        self.vagas.append(vg.Vaga(123, 2, 0+D, 610, 315))
        #COHAPAR
        self.vagas.append(vg.Vaga(124, 3, 0+D, 650, 315))
        self.vagas.append(vg.Vaga(125, 3, 0+D, 690, 315))
        self.vagas.append(vg.Vaga(126, 3, 0+D, 730, 315))
        self.vagas.append(vg.Vaga(127, 3, 0+D, 770, 315))
        self.vagas.append(vg.Vaga(128, 3, 0+D, 810, 315))
        self.vagas.append(vg.Vaga(129, 3, 0+D, 850, 315))
        self.vagas.append(vg.Vaga(130, 3, 0+D, 890, 315))
        self.vagas.append(vg.Vaga(131, 3, 0+D, 930, 315))
        self.vagas.append(vg.Vaga(132, 3, 0+D, 970, 315))
        self.vagas.append(vg.Vaga(133, 3, 0+D, 1010, 315))
        self.vagas.append(vg.Vaga(134, 3, 0+D, 1050, 315))
        self.vagas.append(vg.Vaga(135, 3, 0+D, 1090, 315))
        self.vagas.append(vg.Vaga(136, 3, 0+D, 1130, 315))
        self.vagas.append(vg.Vaga(137, 3, 0+D, 1170, 315))
        self.vagas.append(vg.Vaga(138, 3, 0+D, 1210, 315))

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
            vaga.habilitar_sidebar.connect(sidebar.atualizar_info) # conecta o sinal da vaga para atualizar a sidebar automaticamente quando o valor da variavel habilitar_sidebar for alterado
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

        #==============================================================================================
        # Inserindo toggle switch pra alternar entre formas geometricas e imagens (views)
        #==============================================================================================

        # Toggle Switch customizado via stylesheet
        self.toggle = QCheckBox()
        self.toggle.setCheckable(True)
        self.toggle.setStyleSheet("""
            QCheckBox {
                spacing: 20px;
            }
            QCheckBox::indicator {
                width: 55px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                image: url(imagens/off2.png);  /* ou usar border-radius + background */
                border: 5px solid gray;
                border-radius: 15px;
                background-color: #ccc;
            }
            QCheckBox::indicator:checked {
                image: url(imagens/on2.png);
                border: 5px solid #2196F3;
                border-radius: 15px;
                background-color: #2196F3;
            }
        """)

        proxy_toggle = QGraphicsProxyWidget()
        proxy_toggle.setWidget(self.toggle)
        proxy_toggle.setPos(WIDTH+570, HEIGHT+350)
        proxy_toggle.setZValue(1000) # força a ficar no topo da pilha de renderização
        self.scene.addItem(proxy_toggle)
        
        self.toggle.toggled.connect(self.alternar_view)

        
        #==============================================================================================
        # Copyright
        #==============================================================================================

        copyright = QGraphicsTextItem("© 2026 SEIA Parking Management "+ver+".\n         Todos os direitos reservados.")
        copyright.setFont(QFont("Arial", 8))
        copyright.setDefaultTextColor(QColor("white"))
        copyright.setPos(WIDTH+K, HEIGHT+J-60)
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
        #self.fitInView(bg, Qt.KeepAspectRatio)
    
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

        #self.show_message("bla bla bla", "python e pytgqt são grandes porcarias")
        
        cursor = self.conn.cursor()
        cursor.execute("select * from registro")
        registro = cursor.fetchall()

        for vaga in self.vagas:
            for tupla in registro:
                if vaga.getVagaID() == tupla[3]: #identifica se esta inserido no registro
                    if tupla[6] == "ENTRADA":
                        vaga.setStatus(0) # disponivel
                        vaga.active_monocromatico() # volta a cor original da imagem caso tenha aplicado monocromatico
                    elif tupla[6] == "SAIDA":
                        vaga.setStatus(1) # ocupado
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



'''app.setStyleSheet("""
    QToolTip {
        background-color: #404033;
        color: black;
        border: 1px solid black;
        padding: 4px;
        font-size: 12px;
    }
""")'''
app = QApplication(sys.argv)
app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
viewer = SEIAParkingManagement()
viewer.setWindowTitle("Car Management - v1.0.0.01")
viewer.resize(WIDTH+K, HEIGHT)
viewer.show()
sys.exit(app.exec())


'''
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
apply_stylesheet(app, theme='dark_teal.xml') # aplica o thema exemplo do qt-material
window.resize(WIDTH+k, HEIGHT) # define o tamanho da janela
window.show() # mostra a janela
app.exec()'''

