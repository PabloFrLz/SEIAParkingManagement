
from PySide6.QtGui import QPixmap, QColor, QImage
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QObject
from shiboken6 import isValid


LARGURA = 70
ALTURA = 40


# Classe.atributo → compartilhado (global entre objetos)
# self.atributo → individual (cada objeto tem o seu)

preto = QColor(0, 0, 0, 160) # cor preto com transparência (alpha 160)
verde = QColor(0, 255, 0, 160) # verde
azul = QColor(0, 0, 255, 160) # azul 
amarelo = QColor(255, 255, 0, 160) # amarelo 
vermelho = QColor(255, 0, 0, 160) # vermelho
laranja = QColor(255, 168, 0, 160) # laranja

class Vaga(QGraphicsPixmapItem, QObject):
    habilitar_sidebar = Signal(object) # sinal para habilitar a sidebar e enviar as informações da vaga clicada (id, tipo_carro, status) para a sidebar exibir as informações correspondentes

    def __init__(self, id, tipo_carro, x, y, rotate):
        QObject.__init__(self)
        super().__init__()

        
        self.id = id #identificador do carro
        self.tipo_carro = tipo_carro #tipo de carro (ex: 1=hatch, 2=sedan, 3=pickup)
        self.status = 0 #status da vaga (ex: 0=disponível, 1=ocupada, 2=reserva)
        self.status_name = "" #variavel auxiliar com o nome do status para a GUI
        self.press_button_status = False #status do botão  (False=desativado, True=ativado)

        #variaveis extras com dados restritos ao banco de dados
        #carros
        self.modelo_carro = " - "
        self.nome_servidor = " - "
        self.placa_carro = " - "
        # servidores 
        self.cpf_cnpj = " - "
        self.nome = " - "
        self.autarquia = " - "
        #registros
        #self.id_registro = 0
        self.data_hora = " - "
        self.tipo = " - "


        #geração da imagem do carro
        if tipo_carro == 1:
            self.pixmap_original = QPixmap("imagens/hatch.png")
        elif tipo_carro == 2:
            self.pixmap_original = QPixmap("imagens/sedan.png")
        elif tipo_carro == 3:
            self.pixmap_original = QPixmap("imagens/pickup.png")
        elif tipo_carro == 4:
            self.pixmap_original = QPixmap("imagens/pmpr-car.png")

        # Redimensiona a imagem e demais ajustes
        self.pixmap_original = self.pixmap_original.scaled(LARGURA, ALTURA, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(self.pixmap_original)
        self.setTransformOriginPoint(self.pixmap_original.width() / 2, self.pixmap_original.height() / 2) # Define o ponto de rotação no centro da imagem (muito importante!)
        self.setRotation(rotate) # Aplica a rotação (em graus)
        self.setPos(x, y) # Posiciona o carro
        
        #cria uma versão monocromática (tonz de cinza) para a imagem do veículo
        #self.pixmap_gray = QPixmap.fromImage(self.pixmap_original.toImage().convertToFormat(QImage.Format_Grayscale8)) 
        self.pixmap_gray = self.pixmap_to_grayscale_keep_alpha(self.pixmap_original)

        #insere sombra no carro - mesma sombra que será usada posteriormente para efeitos de luz (LED pulsante)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)           # quanto mais blur, mais suave a sombra
        self.shadow.setOffset(0, 4)             # deslocamento da sombra (x, y)
        self.shadow.setColor(preto)  # cor preto com transparência (alpha 160)
        self.setGraphicsEffect(self.shadow)     # aplica no item

        # animação de LED pulsante
        self.animation = QPropertyAnimation(self.shadow, b"blurRadius") # anima o blurRadius da sombra para criar o efeito de LED pulsante
        self.animation.setDuration(900) # 900ms de animação
        self.animation.setStartValue(0) # valor inicial do blurRadius
        self.animation.setEndValue(30) # valor final do blurRadius
        self.animation.setEasingCurve(QEasingCurve.OutCubic) # curva de animação suave
        #self.animation.setLoopCount(-1) # loop infinito
        
        #configurações finais
        #habilitando hover
        self.setAcceptHoverEvents(True) # habilita eventos de hover para a vaga (importante para os efeitos de destaque e clique)

        #chamada ao banco de dados (MySQL/PostgreeSQL) - criar a vaga no banco de dados

    '''def getVagaInfo(self, id):
        if id == self.id:
            return self # retorna a instancia da vaga para acessar suas informações (id, tipo_carro, status) e atualizar a sidebar com as informações correspondentes
        else:
            return None
    '''

    #===========================================
    # EVENTO DE CLIQUE
    #===========================================
    def mousePressEvent(self, event):
        self.press_button_status = True #indica que o botão foi pressionado, para que o metodo "hoverLeaveEvent" não seja acionado automaticamente
        #print("Vaga clicada: ID = ", self.id, "Tipo de Carro = ", self.tipo_carro, "Status = ", self.status)
        # Debug - APAGAR - teste de LEDs 
        #self.status = random.randint(0, 2) # Gera um status aleatório (0, 1 ou 2)
        #self.ligar_led()
        self.checkStatus()
        self.habilitar_sidebar.emit(self) # emite o sinal para habilitar a sidebar e enviar as informações da vaga clicada (id, tipo_carro, status) para a sidebar exibir as informações correspondentes
        
        

    #===========================================
    # ANIMAÇÕES (LED PULSANTE)
    #===========================================

    def ativar_animacao(self, withLoop=False):
        if withLoop:
            self.animation.setLoopCount(-1) # loop infinito
        else:
            self.animation.setLoopCount(1) # loop único
            self.animation.setDirection(QPropertyAnimation.Forward) # define a direção da animação para frente
            
        self.animation.start() # inicia a animação

    def desativar_animacao(self):
        self.animation.setDirection(QPropertyAnimation.Backward) # define a direção da animação para trás
        self.animation.start() # inicia a animação
        if isValid(self.shadow):
            self.animation.finished.connect(lambda: self.shadow.setColor(preto)) # executa ao final da animação para atualizar a cor de animação devolta para o padrão preto de sombra


    # Evento especial ao passar o mouse sobre a vaga
    def hoverEnterEvent(self, event):
        #tooltip com informações básicas
        self.setToolTip(f"""
            <b>Vaga {self.id}</b><br>
            Status: {self.checkStatus()}<br>
            Tipo: {self.tipo_carro}
        """)

        if not self.press_button_status: #se o botão nao for pressionado -> execute
            self.setCursor(Qt.PointingHandCursor) # muda o cursor para mãozinha ao passar o mouse sobre a vaga
            if self.status == 0:
                self.ativar_animacao(withLoop=False) # ativa um destaque de sombra ao passar o mouse
            self.checkStatus() # verifica o status da vaga e atualiza a cor correspondente 
            #self.animation.finished.connect(self.desativar_animacao)
        
    # Evento especial ao sair com o mouse da vaga
    def hoverLeaveEvent(self, event):
        if not self.press_button_status: #se o botão nao for pressionado -> execute
            self.setCursor(Qt.ArrowCursor) # volta o cursor para o padrão ao sair da vaga
            self.desativar_animacao() # desativa o destaque de sombra ao sair com o mouse
    

    # Evento principal onde ativa os LEDs de acordo com o status da vaga (0=disponível, 1=ocupada, 2=reserva)
    def ligar_led(self):
        self.checkStatus() # verifica o status da vaga e atualiza a cor correspondente
        self.shadow = self.graphicsEffect() # obtém o efeito de sombra existente
        if self.shadow:
            self.shadow.setColor(self.color) # atualiza a cor da sombra para o LED pulsante

        #self.animation.start() # inicia a animação de LED pulsante
        self.ativar_animacao(withLoop=True) # ativa a animação de LED pulsante em loop infinito
    
    def checkStatus(self):
        if self.status == 0: #disponível - verde
            self.color = verde # verde com transparência (alpha 160)
            self.status_name = "LIVRE"
        elif self.status == 1: #ocupada - vermelho
            self.color = vermelho # vermelho com transparência (alpha 160)
            self.status_name = "OCUPADA"
        elif self.status == 2: #reserva - laranja
            self.color = laranja # laranja com transparência (alpha 160)
            self.status_name = "RESERVADA"
        
        self.shadow.setColor(self.color) # cor de seleção de acordo com o status da vaga
        return self.status_name # retorna o status em string já formatado HTML


    def getVagaID(self):
        return self.id
    
    def setStatus(self, newVal):
        self.status = newVal
        
    #===========================================
    # BANCO DE DADOS
    #===========================================
    def registrar(self, id, status):
        self.status = status
        #chamada ao banco de dados (MySQL/PostgreeSQL) - atualizar a coluna de status da vaga existente no banco de dados com o novo status (0=disponível, 1=ocupada, 2=reserva)

    def reservar_vaga(self, id, nome_servidor):
        #status da vaga (ex: 0=disponível, 1=ocupada, 2=reserva)
        self.status = 2
        #chamada ao banco de dados (MySQL/PostgreeSQL) 

    def active_monocromatico(self):
        if self.status != 0:
            self.setPixmap(self.pixmap_gray) # mostra imagem com efeito monocromatico
        else:
            self.setPixmap(self.pixmap_original) # mostra imagem original


    def pixmap_to_grayscale_keep_alpha(self, pixmap):
        image = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)

        for y in range(image.height()):
            for x in range(image.width()):
                color = QColor.fromRgba(image.pixel(x, y))

                gray = int(
                    color.red() * 0.299 +
                    color.green() * 0.587 +
                    color.blue() * 0.114
                )

                color.setRed(gray)
                color.setGreen(gray)
                color.setBlue(gray)
                # alpha fica intacto
                image.setPixelColor(x, y, color)

        return QPixmap.fromImage(image)