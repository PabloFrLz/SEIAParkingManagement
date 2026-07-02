from PySide6.QtCore import QObject, QPoint, QRegularExpression, QSize, QVariantAnimation, Qt, QPropertyAnimation, Signal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QFormLayout, QGraphicsProxyWidget, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PySide6.QtGui import QIcon, QPixmap, QRegularExpressionValidator, QColor

from pymysql import Error
from shiboken6 import isValid
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm

import Formulario, Recursos # classes próprias da aplicação

class Sidebar(QWidget, QObject):
    
    signal_insert = Signal(object)

    def __init__(self, janela_principal, WIDTH, HEIGHT, J, POS_X_SIDEBAR):

        super().__init__()
        self.POS_X_SIDEBAR = POS_X_SIDEBAR
        self.CONST_DESLOCAMENTO = 220

        #======================================
        # Vars
        #======================================
        self.recursos = Recursos.Recursos()
        self.main_window = janela_principal
        self.conn = janela_principal.conn
        self.scene = janela_principal.scene
        self.check = [None, None, None, None, None]
        self.vaga_processada = True # [v1.0.0.03]: variavel pra identificar quando há um fluxo de formulario (ENTRADA, CADASTRO, REMOVER) em andamento
        #self.eixo_x_form = 30
        #self.eixo_y_form = self.CONST_DESLOCAMENTO
        self.categoria = 0 
        self.tipo_form = ""
        self.btn_commit = QPushButton("")
        self.btn_cancel = QPushButton("")
        self.pos_button_x = 0
        self.pos_button_y = 90
        self.warning_text = None
        self.turnRound = True
        self.titulo = None
        self.sentinel = None
        self.lista_carros_disponiveis = None # lista de carros disponíveis - nao possui tupla no registro do tipo ENTRADA
        #self.ctrl_forms_visitante = False 
        self.coord_last_widget = [None, None]
        self.garbage_collector = []
        self.textos_interface = []

        self.coord_last_widget[0] = self.POS_X_SIDEBAR + 30
        self.coord_last_widget[1] =  self.CONST_DESLOCAMENTO

        #======================================
        # Formularios
        #======================================
        self.form1 = None
        self.form2 = None
        self.form3 = None
        #self.formularios = [self.form1, self.form2, self.form3] # inserindo em um vetor/lista pra facilitar a manipulação e evitar futuros erros de escalamento


        #======================================
        # Configurações iniciais
        #======================================
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        #main_layout.setSpacing(0)


        #======================================
        # infos da sidebar
        #======================================
        self.num_vaga = QLineEdit("-")
        self.orgao_vinculado = QLineEdit("-")
        self.orgao_vinculado.setStyleSheet(self.recursos.CORES.cor_orgao_vinculado_box) #definindo cor pro nome do orgao
        self.modelo_carro = QLineEdit("-")
        self.placa_carro = QLineEdit("-")
        self.nome_servidor = QLineEdit("-")
        self.status_vaga = QLineEdit("-")
        # [v1.0.0.03]: inserindo todos os objetos numa lista pra melhor manipulação posterior
        self.lista_info_fields_interface = [self.num_vaga, self.orgao_vinculado, self.modelo_carro, self.placa_carro, self.nome_servidor, self.status_vaga, None]
        #especifica pra não permitir edição
        self.num_vaga.setReadOnly(True)
        self.orgao_vinculado.setReadOnly(True)
        self.modelo_carro.setReadOnly(True)
        self.placa_carro.setReadOnly(True)
        self.nome_servidor.setReadOnly(True)
        self.status_vaga.setReadOnly(True)

        #======================================
        # tabela de registro da sidebar
        #======================================
        self.lista_registro = QTableWidget()
        self.lista_registro.setColumnCount(5)
        
        
        #======================================
        # formatação das informações da sidebar
        #======================================
        form = QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignRight)

        for i, text in enumerate(self.recursos.TEXTOS.text_interface):
            qlabel = QLabel(text) # [v1.0.0.03]: instancia o texto
            qlabel.setFont(self.recursos.FONTES.fonte_texto_desc_infoboxes) # define a fonte
            self.textos_interface.append(qlabel) # [v1.0.0.03]: joga na lista de textos - opcional - bom pra manipular os textos no codigo
            form.addRow(qlabel, self.lista_info_fields_interface[i]) # [v1.0.0.03]: insere as infos no formulário descritivo das vagas

        form.addRow(self.lista_registro) # [v1.0.0.03]: insere a lista no formulário descritivo das vagas 
        

        #======================================
        # Sidebar
        #======================================
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(WIDTH - 890)           # largura da sidebar
        self.sidebar.setFixedHeight(HEIGHT + J - 10)          # altura da sidebar 

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(20, 0, 20, 20)

        #======================================
        # Logomarca da SEIA na sidebar
        #====================================== 
        self.header = QWidget() # [v1.0.0.03]: criando um widget próprio pra logomarca e título pra evitar da logo entrar na animação de transição 
        self.header_conteiner = QVBoxLayout(self.header) # [v1.0.0.03]: conteiner vertical que vai agrupar a logomarca superior e título
        self.img = QPixmap(self.recursos.PATH.img_logo_sidebar) #imagem de plano de fundo
        self.seia_logo = QLabel()
        
        self.seia_logo.setPixmap(self.img.scaled(
            320, 180,  # ajuste conforme necessário
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        #self.seia_logo.setPixmap(self.img)
        #self.seia_logo.setFixedSize(QSize(370, 150))
        self.seia_logo.setStyleSheet(self.recursos.ESTILOS.toolbar_estilo)
        self.titulo = QLabel("DESCRIÇÃO") # [v1.0.0.03]: Cria um titulo para descrever a seção atual da sidebar
        self.titulo.setFont(self.recursos.FONTES.fonte_title_header) # [v1.0.0.03]: define a fonte do texto do titulo
        self.header_conteiner.addWidget(self.seia_logo) # [v1.0.0.03]: adiciona a logomarca superior no conteiner
        self.header_conteiner.addSpacing(30) # [v1.0.0.03]: adicionando espaço entre a logomarca e o titulo da seção
        self.header_conteiner.addWidget(self.titulo) # [v1.0.0.03]: insere o título abaixo
        self.header_conteiner.setAlignment(Qt.AlignmentFlag.AlignCenter) # [v1.0.0.03]: alinhamento ao centro
        self.header_conteiner.setContentsMargins(0,30,0,0)

        #======================================
        # Inserção dos objetos na sidebar
        #====================================== 
        main_layout.addWidget(self.header) # [v1.0.0.03]: insere o widget do header primeiro pra fazer com que os formularios ficam logo abaixo
        main_layout.addWidget(self.sidebar)
        self.sidebar_layout.addSpacing(30) # adicionando um espaço de 30 pixels entre a logo do NAS e os formularios descritivos
        self.sidebar_layout.addLayout(form) # insere os formulários descritivos das vagas no layout da interface gráfica
        

        #======================================
        # Botões de ação da sidebar
        #======================================

        self.setStyleSheet(self.recursos.ESTILOS.button_style) # [v1.0.0.03]: se não definir um setStyleSheet() pra cada button, eles vão herdar esse estilo padrão de Button

        # criação e estética dos botoes
        self.btn_registrar_entrada = QPushButton("ENTRADA")
        self.btn_registrar_entrada.setCheckable(True) # destaca o botão selecionado
        self.sidebar_layout.addWidget(self.btn_registrar_entrada)
        self.btn_registrar_entrada.clicked.connect(lambda: self.acaoButtonEntrada(False))

        self.btn_registrar_saida = QPushButton("SAIDA") # cria
        self.btn_registrar_saida.setCheckable(True)
        self.sidebar_layout.addWidget(self.btn_registrar_saida) # insere na GUI
        self.btn_registrar_saida.clicked.connect(self.acaoButtonSaida)
        
        self.btn_cadastro = QPushButton("CADASTRAR SERVIDOR")
        self.btn_cadastro.setCheckable(True) # destaca o botão selecionado
        self.sidebar_layout.addWidget(self.btn_cadastro)
        self.btn_cadastro.clicked.connect(self.acaoButtonCadastro)
        #self.btn_cadastro.setStyleSheet(self.recursos.ESTILOS.button_style_2)

        self.btn_remove = QPushButton("REMOVER SERVIDOR")
        self.btn_remove.setCheckable(True) # destaca o botão selecionado
        self.sidebar_layout.addWidget(self.btn_remove)
        self.btn_remove.clicked.connect(self.acaoButtonRemoverServidor)
        self.btn_remove.setStyleSheet(self.recursos.ESTILOS.button_style_4)

        self.btn_relatorio = QPushButton() # Button RELATÓRIO
        self.btn_relatorio.setIcon(QIcon(self.recursos.PATH.icon_btn_relatorio)) # carrega icone para o botão de relatorio
        self.btn_relatorio.setIconSize(QSize(64, 64)) # define e fixa o tamanho (width, height) do icone
        self.btn_relatorio.setCheckable(True) # destaca o botão selecionado
        self.btn_relatorio.clicked.connect(lambda: self.acaoButtonRelatorio(False)) # função que será chamada ao detectar click no botão
        #self.btn_relatorio.setStyleSheet(self.recursos.ESTILOS.button_style_2) # estilo CSS do botão
        self.btn_relatorio.setFixedHeight(100) # definindo apenas a altura pra 100px pra fazer o botão ficar maior na vertical
        self.btn_relatorio.setToolTip("Emitir relatório dessa vaga.")

        self.btn_relatorio_completo = QPushButton() # Button RELATÓRIO COMPLETO
        self.btn_relatorio_completo.setIcon(QIcon(self.recursos.PATH.icon_btn_relatorio_completo)) # carrega icone para o botão de relatorio completo
        self.btn_relatorio_completo.setIconSize(QSize(64, 64)) # define e fixa o tamanho (width, height) do icone
        self.btn_relatorio_completo.setCheckable(True) # destaca o botão selecionado
        self.btn_relatorio_completo.clicked.connect(lambda: self.acaoButtonRelatorio(True)) # função que será chamada ao detectar click no botão
        #self.btn_relatorio_completo.setStyleSheet(self.recursos.ESTILOS.button_style_2)
        self.btn_relatorio_completo.setFixedHeight(100)
        self.btn_relatorio_completo.setToolTip("Emitir relatório de todas as vagas.")

        grupo_buttons_relatorio = QHBoxLayout()
        grupo_buttons_relatorio.addWidget(self.btn_relatorio)
        grupo_buttons_relatorio.addWidget(self.btn_relatorio_completo)
        self.sidebar_layout.addLayout(grupo_buttons_relatorio)

        self.list_buttons = [self.btn_registrar_entrada, self.btn_registrar_saida, self.btn_cadastro, self.btn_remove, self.btn_relatorio, self.btn_relatorio_completo]

        #======================================
        # configurando restrições de entrada - para etapa de cadastro de servidor
        #======================================
        self.regex_cpf = QRegularExpression(r"^\d{0,11}$") # para o CPF
        self.validator_cpf = QRegularExpressionValidator(self.regex_cpf)

        self.regex_nome = QRegularExpression("^[A-Za-z ]*$") # Para o nome
        self.validator_nome = QRegularExpressionValidator(self.regex_nome)
        
        #======================================
        # Configurações finais
        #======================================
        self.sidebar_layout.addStretch() # empurra os elementos para o topo
        
        #_________________________________________________________________________________________
        #animação da largura para rolar a sidebar para a direita
        self.largura = WIDTH
        self.animation = QPropertyAnimation(self.sidebar, b"pos")
        self.animation.setDuration(1200)



    def controlActions(self, vaga):
        self.cancel() # destroi formularios caso esteja em andamento - isso permite interagir com outras vagas na interface enquanto em outras etapas do fluxo dos formularios de ENTRADA, CADASTRO, etc.
        self.atualizar_info(vaga) 
    


    def atualizar_info(self, vaga): # variavel info contem os dados definidos em Vaga.py, como self.id, self.tipo_carro, self.status, self.status_name, self.press_button_status
        ultimo_registro_da_vaga = self.getUltimaEntradaRegistroDaVaga(vaga.id) # pega a ultima entrada registrada para esse numero de vaga em vaga.id
        self.lista_registro.setRowCount(0) # reseta o contador de linhas da tabela

        #atualizando informações principais
        self.orgao_vinculado.setText(str(vaga.autarquia))
        self.num_vaga.setText(str(vaga.id))
        self.status_vaga.setText(vaga.status_name)


        #atualizando informações secundárias
        if len(ultimo_registro_da_vaga) != 0:
            cpf = ultimo_registro_da_vaga[0][2] # [v1.0.0.03]: cpf será null/none quando for VISITANTE
            if(cpf is None): # [v1.0.0.03]: para quando for atualizar visualmente as informações da vaga registrada para um VISITANTE
                self.modelo_carro.setText("CARRO PRIVADO (VISITANTE)")
                self.placa_carro.setText("RESTRITO")
                self.nome_servidor.setText(ultimo_registro_da_vaga[0][7]) # o nome do servidor nesse momento de execução vai estar salvo em self.nome
            else: 
                #consulta pra pegar dados da vaga/carro
                cursor = self.conn.cursor()
                cursor.execute(f"select * from carro where placa='{ultimo_registro_da_vaga[0][1]}'")
                dados_carro = cursor.fetchall()
                #consulta pra pegar o nome do servidor
                cursor.execute(f"select * from servidor where cpf_cnpj='{ultimo_registro_da_vaga[0][2]}'")
                dados_servidor = cursor.fetchall()
                # atualizando as infos
                self.modelo_carro.setText(dados_carro[0][3])
                self.placa_carro.setText(dados_carro[0][0])
                self.nome_servidor.setText(dados_servidor[0][1])
            #atualizando a lista de registros com as infos do registro para essa vaga específica
            self.updateHistoricoRegistro() 

        else:
            self.modelo_carro.setText(" - ")
            self.placa_carro.setText(" - ")
            self.nome_servidor.setText(" - ")
        
         # [v1.0.0.03]: aplica animações de destaque pra atrair atenção do usuario
        self.destacar_campo(self.orgao_vinculado)
        self.destacar_campo(self.num_vaga)
        self.destacar_campo(self.modelo_carro)
        self.destacar_campo(self.placa_carro)
        self.destacar_campo(self.nome_servidor)

        #atualizando a cor do campo "Status da vaga"
        if vaga.status == 0: # disponivel
            self.destacar_campo(self.status_vaga, self.recursos.ESTILOS.status_vaga_green) 
        elif vaga.status == 1: # ocupada
            self.destacar_campo(self.status_vaga, self.recursos.ESTILOS.status_vaga_red)
        elif vaga.status == 2: # reservada
            self.destacar_campo(self.status_vaga, self.recursos.ESTILOS.status_vaga_orange)
        self.sentinel = vaga


    
    def acaoButtonEntrada(self, ignoredMessageBox=False): 
        if self.status_vaga.displayText() != "OCUPADA":
            self.transitToFormulario() # animação que empurra pro lado direito as infos
            self.titulo.setText("REGISTRO DE ENTRADA") # [v1.0.0.03]: Altera o titulo da seção para retratar a nova seção de registro de entrada
            
            if (ignoredMessageBox):
                resposta = QMessageBox.StandardButton.No # [v1.0.0.03]: Define manualmente "Não" ao invés de solicitar ao usuario - necessário pra direcionar o fluxo automaticamente sem solicitar nada ao usuário
                #verificaEntradaServidor() # [v1.0.0.03]: verifica se tem registro de 'ENTRADA' em andamento pra esse servidor - se tiver, questiona-o se ele quer registrar 'SAIDA'
            else:
                resposta = QMessageBox.question(self.main_window, "Questão", "Registro de VISITANTE ?") # [v1.0.0.03]: questiona o usuário se será um registro de um visitante ou de um servidor.
            
            if (resposta == QMessageBox.StandardButton.Yes): # [v1.0.0.03]: verifica se usuario clicou no botao Sim
                self.registroEntradaVisitante() # inicializa os formularios pra registro da ENTRADA de VISITANTES
                #self.ctrl_forms_visitante = True # diz a aplicação que se trata de um registro de visitante - necessário pra informar a funções secundárias como atualizar_info() - que fazem parte do fluxo de vários registros e consultas - como se portar quando for atualizar as infos de um VISITANTE
            else:
                self.registroEntrada() # inicializa os formularios pra registro da ENTRADA de servidores
                
        else:
            resposta = QMessageBox.question(self.main_window, "Atenção", "A vaga selecionada está OCUPADA! \nDeseja registrar a SAÍDA do servidor ?")
            if resposta == QMessageBox.StandardButton.Yes:
                self.acaoButtonSaida()
                return False # [v1.0.0.03]: define retorno falso pra evitar continuidade do fluxo de registro de ENTRADA para quando o fluxo vier do buscador global de placas (self.search_box)
            return False
        
        return True # [v1.0.0.03]: definindo retorno só pra verificar erros e evitar executar metodos especificos em SEIAParkingManagement.py -> processarVagaBuscada() 



    def acaoButtonSaida(self):
        dados = None
        if self.status_vaga.displayText() == "OCUPADA":
            '''if self.vaga_processada:
                dados = self.getUltimaEntradaRegistroDaVaga(self.num_vaga.displayText()) #obtem a ultima entrada registrada pra uma vaga especifica
            else:
                dados = self.getUltimaEntradaRegistroDaVagaByPlaca(self.placa_carro.displayText()) #obtem a ultima entrada registrada pra uma vaga especifica
            '''
            dados = self.getUltimaEntradaRegistroDaVaga(self.num_vaga.displayText()) #obtem a ultima entrada no registro para esse numero de vaga
            self.insertRegistro(dados=dados)
            print(f"[{self.recursos.CORES.AMARELO}Sidebar.py{self.recursos.CORES.RESET}]:  Iniciando registro de SAIDA para a vaga de nº {dados[0][3]}")

        else:
            QMessageBox.warning(self.main_window, "Atenção", "Vaga selecionada é inválida ou a vaga ainda está DISPONÍVEL.")



    def acaoButtonCadastro(self):
        self.transitToFormulario() # animação que empurra pro lado direito as infos
        #self.titulo = self.insertHeader("CADASTRAR SERVIDOR") # gera logo no topo e titulo da seção
        self.titulo.setText("CADASTRAR SERVIDOR") # [v1.0.0.03]: Altera o titulo da seção para retratar a nova seção de registro de entrada
        self.cadastroServidor() # inicializa os formularios pra cadastro de servidor



    def acaoButtonRemoverServidor(self): # [v1.0.0.03]: método que terá a ação que dará inicio ao processo de remoção de servidor 
        self.transitToFormulario() # animação que empurra pro lado direito as infos
        #self.titulo = self.insertHeader("REMOVER SERVIDOR") 
        self.titulo.setText("REMOVER SERVIDOR") # [v1.0.0.03]: Altera o titulo da seção para retratar a nova seção de registro de entrada
        self.removeServidor() # inicializa os formulários para remoção de servidor



    # transiciona para o formulario de registro e posteriomente de volta para a tela de informações da vaga
    def transitToFormulario(self):
        if self.turnRound: # empurra os elementos da sidebar pra direita (ocultando-os)
            self.animation.setStartValue(QPoint(0, self.sidebar.pos().y()))
            self.animation.setEndValue(QPoint(self.largura + 400, self.sidebar.pos().y()))
            self.animation.start() #inicia a animação

        else: # puxa os elementos da sidebar pra esquerda (mostrando-os de volta)
            self.animation.setStartValue(QPoint(self.largura + 400, self.sidebar.pos().y()))
            self.animation.setEndValue(QPoint(0, self.sidebar.pos().y()))  
            self.animation.start() #inicia a animação

        self.turnRound = not self.turnRound # inverte o estado para a próxima vez que o botão for clicado
    


    def geraFormulario(self, consulta, texto, func):
        try:
            #consulta ao banco de dados para obter os dados cadastrados
            cursor = self.conn.cursor()
            cursor.execute(consulta)
            resultado_pesquisa = cursor.fetchall()
            form = Formulario.Formulario(texto, resultado_pesquisa, self.categoria, onComplete=func) 
            object_proxy = self.insertOnGUI(form, 25)#inserção na GUI
            self.garbage_collector.append(object_proxy)
            return form
        except Error as e:
            self.error_message(e)  
    


    def registroEntrada(self):
        if (self.check[0] is None): 
            # [v1.0.0.03]: Em conversas com guardas da guarita, fui informado que a abordagem melhor seria o fluxo começar com a placa do veiculo
            #consulta = f"SELECT * FROM carro WHERE autarquia = '{self.orgao_vinculado.displayText()}' AND proprietario_cpf IS NOT NULL" # [v1.0.0.03]: selecione todos os carros que sejam vinculados ao orgão da vaga e que tenha um cpf de proprietario válido

            # [DESCRIÇÃO DA CONSULTA]: 
            #       Selecione todos os carros da tabela carro onde a autarquia seja igual ao valor informado,
            #       e onde o CPF do proprietario nao esteja vazio, e cuja placa não apareça em nenhum registro 
            #       da tabela Registro que tenha tipo = 'ENTRADA' (considerando apenas registros onde a placa não é nula)."
            consulta = f"SELECT * FROM carro c WHERE c.autarquia = '{self.orgao_vinculado.displayText()}' AND c.proprietario_cpf IS NOT NULL AND c.placa NOT IN (SELECT r.placa FROM registro r WHERE r.placa IS NOT NULL AND r.tipo = 'ENTRADA')"
            self.categoria = 2 # [v1.0.0.03]: informa a classe Formulario() que se trata de um carro
            self.form2 = self.geraFormulario(consulta, self.recursos.TEXTOS.text_select_carro, self.registroEntrada)
            self.check[0] = True

        elif (self.check[1] is None):
            self.form2.setDisabled(True)
            placa, modelo = self.form2.getResult().split(" - ") # [v1.0.0.03]: obtendo a PLACA e MODELO do carro
            self.placa_carro.setText(placa) # [v1.0.0.03]: gambiarra pra pdoer pegar dados de placa e carro no insert
            self.modelo_carro.setText(modelo)
            cpf = self.getCPFbyPlaca(placa)
            self.showInformacoesServidor("INFORMAÇÕES DO SERVIDOR: ", cpf)
            self.check[1] = True
            self.registroEntrada() # [v1.0.0.03]: chamada recursiva
        
        elif(self.check[2] is None):
            self.check[2] = True
            # Button pra confirmar inserção no banco de dados
            self.btn_commit = self.insertButton("CONFIRMAR", self.recursos.ESTILOS.button_style_3, self.insertRegistro) # linka com a função para inserir na tabela de registros do banco
            self.btn_cancel = self.insertButton("CANCELAR", self.recursos.ESTILOS.button_style_3, self.cancel)



    def registroEntradaVisitante(self): # [v1.0.0.03]: função propria para o registro de visitantes
        if (self.check[0] is None): # [v1.0.0.03]: para o formulario de registro de visitante só será necessário coletar o nome do visitante.
            self.FormularioLeituraDados(self.recursos.TEXTOS.text_insert_nome_visitante, "Digite o nome aqui...", self.validator_nome, self.registroEntradaVisitante)
            self.check[0] = True

        elif(self.check[1] is None):
            self.check[1] = True
            # Button pra confirmar inserção no banco de dados - registro
            self.btn_commit = self.insertButton("CONFIRMAR", self.recursos.ESTILOS.button_style_3, self.insertVisitante) # linka com a função que insere no banco os dados do servidor
            self.btn_cancel = self.insertButton("CANCELAR", self.recursos.ESTILOS.button_style_3, self.cancel)
        


    def cadastroServidor(self):
        if (self.check[0] is None): 
            consulta = "select * from autarquia"
            self.categoria = 0
            self.form1 = self.geraFormulario(consulta, self.recursos.TEXTOS.text_select_autarquia, self.cadastroServidor) # gera o primeiro formulario
            self.check[0] = True #desabilita esse bloco condicional na proxima iteração

        elif (self.check[1] is None): 
            if (self.form1.getResult() == ""): # [v1.0.0.03]: Corrige o problema do usuario não selecionar orgão
                QMessageBox.warning(self.main_window, "Erro", "Opção selecionada é inválida.")
                self.cancel()
                return
            
            self.form1.setDisabled(True)
            self.FormularioLeituraDados(self.recursos.TEXTOS.text_insert_nome_servidor, "Digite o nome aqui...", self.validator_nome, self.cadastroServidor)
            self.check[1] = True

        elif (self.check[2] is None): 
            self.FormularioLeituraDados(self.recursos.TEXTOS.text_insert_cpf_servidor, "ex.: 50545642300...", self.validator_cpf, self.cadastroServidor)
            self.check[2] = True
            #self.coord_last_widget[1] = self.coord_last_widget[1] + 30 # [v1.0.0.03]: deslocando novamente pra corrigir diferença de espaço entre formularios
        
        elif (self.check[3] is None): 
            consulta = f"SELECT * FROM carro WHERE autarquia = '{self.form1.getResult()}' AND proprietario_cpf IS NULL" # [v1.0.0.03]: selecione todos os servidores onde a autarquia for igual a de interesse e nao tenha proprietarios (null)
            self.categoria = 2 # informa pra classe Formulario que se trata de um carro
            self.form2 = self.geraFormulario(consulta, self.recursos.TEXTOS.text_select_carro, self.cadastroServidor)
            #self.coord_last_widget[0] = self.form2.getCoordX() # para poder posicionar os botoes corretamente - se tivesse usando conteiner nao precisaria
            #self.coord_last_widget[1] = self.form2.getCoordY() + 30
            self.check[3] = True

        elif(self.check[4] is None):
            self.form2.setDisabled(True)
            self.check[4] = True
            # Button pra confirmar inserção no banco de dados
            self.btn_commit = self.insertButton("CONFIRMAR", self.recursos.ESTILOS.button_style_3, self.insertServidor) # linka com a função que insere no banco os dados do servidor
            self.btn_cancel = self.insertButton("CANCELAR", self.recursos.ESTILOS.button_style_3, self.cancel)



    def removeServidor(self): # [v1.0.0.03]: Gerando os formularios do processo de remoção de servidor
        if (self.check[0] is None): 
            consulta = "select * from autarquia"
            self.categoria = 0
            self.form1 = self.geraFormulario(consulta, self.recursos.TEXTOS.text_select_autarquia, self.removeServidor) # gera o primeiro formulario
            self.check[0] = True #desabilita esse bloco condicional na proxima iteração
        
        elif (self.check[1] is None): 
            self.form1.setDisabled(True)
            consulta = "select * from servidor where autarquia='{}'".format(self.form1.getResult())
            self.categoria = 1
            self.form2 = self.geraFormulario(consulta, self.recursos.TEXTOS.text_select_servidor, self.removeServidor)
            self.check[1] = True
            # para poder posicionar os botoes corretamente
            self.coord_last_widget[0] = self.form2.getCoordX() 
            self.coord_last_widget[1] = self.form2.getCoordY() + 20

        elif(self.check[2] is None):
            self.form2.setDisabled(True)
            servidor = self.form2.getResult().split(" - ") # [v1.0.0.03]: obtém o nome e cpf do servidor
            self.nome = servidor[1] # [v1.0.0.03]: usa apenas o nome capturado
            # [v1.0.0.03]: Buttons pra confirmar remoção de servidor
            self.btn_commit = self.insertButton("REMOVER", self.recursos.ESTILOS.button_style_3, self.deleteServidor) # [v1.0.0.03]: linka coma função que remove os dados do servidor do banco
            self.btn_cancel = self.insertButton("CANCELAR", self.recursos.ESTILOS.button_style_3, self.cancel)
            servidor_entrada = self.verificaEntradaServidor(servidor[0]) # [v1.0.0.03]: consulta secundária pra verificar se o servidor possui registro em andamento pra não permitir exclusão até que seja registrado uma saida pra esse servidor.
            self.check[2] = True
            if len(servidor_entrada) != 0: # [v1.0.0.03]: se for diferente de zero então significa que tem ocorrencia de entrada do servidor no registro.
                resposta = QMessageBox.question(self.main_window, "Erro", f"Servidor '{servidor[1]}' possui uma ENTRADA no registro. Favor registrar sua SAIDA para habilitar sua exclusão do banco.\nGostaria de registrar SAIDA para esse servidor e exclui-lo em seguida ?")
                if (resposta == QMessageBox.StandardButton.Yes):
                    self.acaoButtonSaida() # [v1.0.0.03]: registra a SAIDA
                    self.deleteServidor() # [v1.0.0.03]: chama direto a função que deleta do banco pra nao ter que começar a remoção do servidor do inicio chamando removeServidor()
                else:
                    self.cancel() # [v1.0.0.03]: cancela a operação
            else:
                QMessageBox.warning(self.main_window, "Atenção", "Remover servidor implica remover também todos os dados associados a ele no registro. Clique em REMOVER para concluir a operação!")
    


    def capturar_nome_cpf(self, line_edit, func_call_recursivamente):
        texto = line_edit.text().strip() 
        if(texto.isdigit()): # verifica se é digito pra direcionar o fluxo pra etapa de CPF
            self.cpf = texto
        else:
            if(len(texto) >= self.recursos.CONST.MINIMUN_CHARACTER_TO_NAME): # Evita não inserir nada no formulario
                self.nome = texto
            else:
                QMessageBox.warning(self.main_window, "Erro", "insira um nome válido.")
                self.cancel()
                return
        
        func_call_recursivamente()



    def insertRegistro(self, dados=None):
        print(f"\n\n ***************** ({self.recursos.CORES.AMARELO} DATABASE INSERT {self.recursos.CORES.RESET}) *****************\n")
        num_vaga = self.num_vaga.displayText()
        if dados is not None:
            #obtem os dados direto do banco
            placa = dados[0][1]
            cpf_cnpj = dados[0][2]
            nome_visitante = dados[0][7] # [v1.0.0.03]: os dados do nome do visitante será a 8ª coluna da tabela Registro
            tipo = "SAIDA"
            if placa is None or cpf_cnpj is None: # [v1.0.0.03]: para o caso de ser um visitante, a placa e o cpf_cnpj serão None/null
                sql = f"UPDATE registro SET data_saida = NOW(), tipo = '{tipo}' WHERE nome_visitante = '{nome_visitante}' AND data_saida IS NULL AND tipo = 'ENTRADA'"
                # sql = atualize a tabela Registro definindo a coluna 'data_saida' com a hora atual do banco (clausula NOW()), definindo o tipo para "SAIDA" onde o nome do visitante
                # bater com o que foi coletado da tabela Registro - por fim, onde 'data_saida' estiver NULL (vazio) e o tipo for ENTRADA.
            else:
                sql = f"UPDATE registro SET data_saida = NOW(), tipo = '{tipo}' WHERE placa = '{placa}' AND cpf_cnpj = '{cpf_cnpj}' AND data_saida IS NULL AND tipo = 'ENTRADA'"
                # sql = atualize a tabela Registro definindo a coluna 'data_saida' com a hora atual do banco (clausula NOW()), definindo o tipo para "SAIDA" onde a placa e cpf 
                # baterem com os coletados nesse bloco condicional - por fim, onde 'data_saida' estiver vazio e o tipo estiver definido como ENTRADA, pois assim voce tem a certeza 
                # de atualizar a tupla no banco com dados de saida em branco e que so tem uma ENTRADA registrada - pode ser que seja redundante, mas funciona!
        else:
            #obtem os dados apartir dos formularios de ENTRADA
            tipo = "ENTRADA"
            sql = "INSERT INTO registro (placa, cpf_cnpj, num_vaga, data_entrada, tipo) VALUES (%s, %s, %s, NOW(), %s)"
            placa, modelo = self.placa_carro.displayText(), self.modelo_carro.displayText()
            cpf_cnpj = self.getCPFbyPlaca(placa)
            #servidor = self.getServidorByCPF(cpf_cnpj)
            #nome_servidor = servidor[0][1]

            #tratamento dos dados
            print(f"[{self.recursos.CORES.AMARELO}Sidebar.py{self.recursos.CORES.RESET}]: Nº vaga: {num_vaga}")
            print(f"[{self.recursos.CORES.AMARELO}Sidebar.py{self.recursos.CORES.RESET}]: CPF/CNPJ: {cpf_cnpj}")
            #print("Nome:", nome_servidor)
            print(f"[{self.recursos.CORES.AMARELO}Sidebar.py{self.recursos.CORES.RESET}]: Placa: {placa}")
            print(f"[{self.recursos.CORES.AMARELO}Sidebar.py{self.recursos.CORES.RESET}]: Modelo: {modelo}")
            
        print(f"\n{self.recursos.CORES.AMARELO}================================{self.recursos.CORES.RESET}")
        print("Dados extraídos!")
        print(f"{self.recursos.CORES.AMARELO}================================{self.recursos.CORES.RESET}\n")
        #inserção no banco
        try:
            cursor = self.conn.cursor()
            #data e hora serão calculados automaticamente pelo banco de dados MySQL com a clausula NOW()
            if tipo == "ENTRADA":
                cursor.execute(sql, (placa, cpf_cnpj, num_vaga, tipo))
            else:
                cursor.execute(sql)
            self.conn.commit() # commit - pra persistir no banco
            print(f"\n{self.recursos.CORES.VERDE}================================{self.recursos.CORES.RESET}")
            print("Dados inseridos no Registro com sucesso!")
            print(f"{self.recursos.CORES.VERDE}================================{self.recursos.CORES.RESET}\n")
            QMessageBox.information(self.main_window, "Sucesso", "Registro efetuado com sucesso!")
            self.cancel(self.sentinel) # reseta informações e retrocede sidebar

        except Error as e:
            self.error_message(e)
    


    def insertVisitante(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"INSERT INTO Registro(num_vaga, data_entrada, tipo, nome_visitante) VALUES({self.num_vaga.displayText()}, NOW(), 'ENTRADA', '{self.nome}')")
            self.conn.commit()
            QMessageBox.information(self.main_window, "Sucesso", "Registro efetuado com sucesso!")
            self.cancel(self.sentinel) # reseta informações e retrocede sidebar

        except Error as e:
            self.error_message(e)
            


    def insertServidor(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"INSERT INTO Servidor VALUES('{self.cpf}', '{self.nome}', '{self.form1.getResult()}')")
            self.conn.commit()
            print(f"\n{self.recursos.CORES.VERDE}================================{self.recursos.CORES.RESET}")
            print(f"Servidor [{self.nome}] registrado com sucesso!")
            print(f"{self.recursos.CORES.VERDE}================================{self.recursos.CORES.RESET}\n")

            # [v1.0.0.03]: a partir dessa versão o servidor tem que selecionar o carro no cadastro para linkar o veiculo ao seu cpf
            placa, modelo = self.form2.getResult().split(" - ") # [v1.0.0.03]: obtem a placa
            cursor.execute(f"UPDATE Carro SET proprietario_cpf = '{self.cpf}' WHERE placa = '{placa}'") # [v1.0.0.03]: atualiza o campo proprietario_cpf da tabela carro com o CPF do servidor
            self.conn.commit()
            print(f"\n{self.recursos.CORES.VERDE}================================{self.recursos.CORES.RESET}")
            print(f"Carro [{modelo}] de placa [{placa}] atualizado com CPF [{self.cpf}] do Servidor [{self.nome}] com sucesso!")
            print(f"{self.recursos.CORES.VERDE}================================{self.recursos.CORES.RESET}\n")
            
            QMessageBox.information(self.main_window, "Sucesso", "Servidor cadastrado com sucesso!")
            self.cancel(self.sentinel) # reseta informações e retrocede sidebar

        except Error as e:
            self.error_message(e)
            


    def deleteServidor(self): # [v1.0.0.03]: remoção do servidor do banco de dados
        try:
            cursor = self.conn.cursor() 
            cursor.execute(f"delete from servidor where nome='{self.nome}'")
            self.conn.commit()
            print(f"\n{self.recursos.CORES.VERMELHO}================================{self.recursos.CORES.RESET}")
            print("Servidor [{self.nome}] deletado com sucesso!")
            print(f"{self.recursos.CORES.VERMELHO}================================{self.recursos.CORES.RESET}\n")

            QMessageBox.information(self.main_window, "Sucesso", "Servidor removido com sucesso!")
            self.cancel(self.sentinel) # reseta informações e retrocede sidebar

        except Error as e:
            self.error_message(e)


    def insertOnGUI(self, object, deslocamento_mais_profundo):
        #inserção na GUI
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(object)
        #self.eixo_y_form += 90 + deslocamento_mais_profundo
        #proxy.setPos(self.POS_X_SIDEBAR + self.eixo_x_form, self.eixo_y_form)
        self.coord_last_widget[1] += 75 + deslocamento_mais_profundo
        proxy.setPos(self.coord_last_widget[0], self.coord_last_widget[1])
        self.scene.addItem(proxy)
        return proxy # retorna o proxy pra caso precise destruir



    def insertButton(self, msg, style, action=None):
        button = QPushButton(msg)
        button.setCheckable(True)
        button.clicked.connect(lambda: action()) # chama o metodo para inserção na tabela registro do banco de dados
        proxyBtn = QGraphicsProxyWidget() # cria um proxy pra mostrar diretamente no objeto scene sem necessidade de empilhar em conteiners layouts
        proxyBtn.setWidget(button)
        x = self.coord_last_widget[0] + self.pos_button_x + 7 # +7 é pra corrigir um pequeno desalinhamento no eixo x que notei
        y = self.coord_last_widget[1] + self.pos_button_y + 15
        proxyBtn.setPos(x, y)
        self.scene.addItem(proxyBtn)
        if self.pos_button_x == 0:
            self.pos_button_x = 160 # coloca o prox. button do lado direito do button anterior
        else:
            self.pos_button_x = 0        
        
        button.setStyleSheet(style) # aplica estilo
        return button
        

    def cancel(self, param1=None):
        self.signal_insert.emit(self) # emite o sinal pra atualizar o estado visual das vagas na interface

        #deleta os formularios relacionados a inserção no registro 
        formularios = [self.form1, self.form2, self.form3] 
        for form in formularios:
            if form is not None and isValid(form):
                form.deleteLater()
                form = None

        #destruindo os buttons
        botoes = [self.btn_commit, self.btn_cancel]
        for btn in botoes:
            if btn is not None and isValid(btn):
                btn.deleteLater()
                btn = None

        #destruindo a logomarca e o texto titulo
        
        '''
        if self.titulo is not None and isValid(self.titulo):
            self.titulo.deleteLater()
            self.titulo = None
        '''
        
        # destruindo os formularios de leitura pra cadastro de servidor
        if self.garbage_collector is not None:
            for item in self.garbage_collector:
                if isValid(item):
                    item.deleteLater()
                    item = None

        if not self.turnRound:
            self.transitToFormulario() #animação que transiciona de volta para a interface padrão.
        
        if param1 is not None:
            self.atualizar_info(self.sentinel)

        #self.ctrl_forms_visitante = False # [v1.0.0.03]: reseta a variavel de controle do formulario de visitante

        '''
        for btn in self.list_buttons:
            btn.setCheckable(False) # desabilita o efeito de checked do CSS 
            btn.setCheckable(True) # habilita novamente pra habilitar o efeito pra futuras interações do usuário.
        '''

        self.titulo.setText("DESCRIÇÃO") # [v1.0.0.03]: Altera o nome de volta pro titulo inicial

        self.coord_last_widget[1] = self.CONST_DESLOCAMENTO # [v1.0.0.03]: variavel que desloca verticalmente os formularios

        for i in range(len(self.check)):
            self.check[i] = None # atribuindo None pra habilitar novamente os forms

        self.vaga_processada = True # [v1.0.0.03]: habilita novas chamadas ao processo de ENTRADA via campo de busca global de placas

        print(f"[{self.recursos.CORES.AMARELO}Sidebar.py{self.recursos.CORES.RESET}]:  Operação cancelada.")



    def consultaDisponibilidadeFrota(self, valor):
        cursor = self.conn.cursor()

        # [DESCRIÇÃO DA CONSULTA]: 
        #       Selecione todos os carros da tabela carro onde a autarquia seja igual ao valor informado,
        #       e onde o CPF do proprietario nao esteja vazio, e cuja placa não apareça em nenhum registro 
        #       da tabela Registro que tenha tipo = 'ENTRADA' (considerando apenas registros onde a placa não é nula)."

        cursor.execute(f"SELECT * FROM carro c WHERE c.autarquia = '{valor}' AND c.proprietario_cpf IS NOT NULL AND c.placa NOT IN (SELECT r.placa FROM registro r WHERE r.placa IS NOT NULL AND r.tipo = 'ENTRADA')")
        carros_disponiveis = cursor.fetchall()
        return carros_disponiveis

        '''if len(result) == 0:
            return [False, result] # não há frota disponível
        else:
            return [True, result]'''
        

    
    def getInstance(self):
        return self
    


    def getUltimaEntradaRegistroDaVaga(self, num_vaga):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM registro WHERE num_vaga='{num_vaga}' ORDER BY id DESC LIMIT 1")
        return cursor.fetchall()



    def getUltimaEntradaRegistroDaVagaByPlaca(self, placa): 
        # [v1.0.0.03]: foi identificado um problema quando selecionava placa via self.search_box, onde a ultima entrada do carro 
        #              no registro nem sempre era a mesma da vaga selecionada, então foi criado esse metodo que busca a ultima 
        #              entrada do registro a partir da placa do carro.
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM registro WHERE placa='{placa}' ORDER BY id DESC LIMIT 1")
        return cursor.fetchall() 



    def getRegistroByVaga(self, num_vaga): # retorna todas as tuplas do registro onde tenha dados do nº da vaga informada
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM registro WHERE num_vaga='{num_vaga}'")
        '''SELECT * FROM registro 
        WHERE num_vaga = '{num_vaga}'
        AND data_entrada >= CURDATE()          -- Hoje a partir de 00:00:00
        AND data_entrada < CURDATE() + INTERVAL 1 DAY  -- Até amanhã 00:00:00
        ORDER BY data_entrada DESC;   -- Recomendado (mais recentes primeiro)'''
        #    *************
        #      [CRITICO]
        #    *************
        # descomentar o trecho abaixo quando for testar na guarita.
        #cursor.execute(f"SELECT * FROM registro WHERE num_vaga = '{num_vaga}' AND data_entrada >= CURDATE() AND data_entrada < CURDATE() + INTERVAL 1 DAY ORDER BY data_entrada DESC")
        tuplas_tabela = cursor.fetchall()
        return tuplas_tabela
    


    def getAllFromRegistro(self): # retorna todas as tuplas do registro onde tenha dados do nº da vaga informada
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM registro")
        tuplas_tabela = cursor.fetchall()
        return tuplas_tabela



    def getServidorByCPF(self, cpf_cnpj): # busca o servidor a partir do seu CPF
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM servidor WHERE cpf_cnpj='{cpf_cnpj}'")
        servidor = cursor.fetchall()
        return servidor
    


    def getVisitantes(self): # [v1.0.0.03]: busca dados de visitantes
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM registro WHERE nome_visitante != NULL")
        servidor = cursor.fetchall()
        return servidor
    


    def verificaEntradaServidor(self, cpf_cnpj):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM registro WHERE cpf_cnpj='{cpf_cnpj}' AND tipo='ENTRADA'") # busca no registro se há uma tupla com o cpf do servidor e se ela só foi registrada ENTRADA e não SAIDA
        servidor_entrada = cursor.fetchall()
        return servidor_entrada
    


    def getCarroByCPF(self, cpf_cnpj):  # [v1.0.0.03]: função para obter os dados do carro vinculado ao CPF do servidor
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM Carro WHERE proprietario_cpf = '{cpf_cnpj}'")
        servidor = cursor.fetchall()
        return servidor
    


    def getCarroByPlaca(self, placa):  # [v1.0.0.03]: função para obter os dados do carro vinculado à placa
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM Carro WHERE placa = '{placa}'")
        carro = cursor.fetchall()
        return carro
    


    def getCPFbyPlaca(self, placa):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM Carro WHERE placa = '{placa}'")
        cpf = cursor.fetchall()
        return cpf[0][5] # retorna apenas o CPF e nao a tupla inteira
        

    def getIdVagaByPlaca(self, placa):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT num_vaga FROM Carro WHERE placa = '{placa}'")
        num_vaga = cursor.fetchall()
        return num_vaga[0][0] # retorna apenas o numero da vaga e nao a tupla inteira

    def updateHistoricoRegistro(self):
        tuplas_tabela = self.getRegistroByVaga(self.num_vaga.displayText())

        linha = 0
        self.lista_registro.setHorizontalHeaderLabels(["Placa", "Tipo", "Data/Hora(⤷)", "Data/Hora(⤶)", "CPF/CNPJ"])
        for tupla in tuplas_tabela:
            tipo = QTableWidgetItem(tupla[6])
            if tupla[6] == "ENTRADA":
                tipo.setForeground(self.recursos.CORES.BRUSH_ENTRADA)
                tipo.setBackground(self.recursos.CORES.BRUSH_ENTRADA_ALPHA)
            else:
                tipo.setForeground(self.recursos.CORES.BRUSH_SAIDA)
                tipo.setBackground(self.recursos.CORES.BRUSH_SAIDA_ALPHA)
            
            self.lista_registro.insertRow(linha) # insere uma nova linha
            self.lista_registro.setItem(linha, 0, QTableWidgetItem(tupla[1])) # coluna Placa
            self.lista_registro.setItem(linha, 1, tipo) # coluna Tipo
            self.lista_registro.setItem(linha, 2, QTableWidgetItem(str(tupla[4]))) # coluna Data/Hora (Entrada)
            self.lista_registro.setItem(linha, 3, QTableWidgetItem(str(tupla[5]))) # coluna Data/Hora (Saída)
            self.lista_registro.setItem(linha, 4, QTableWidgetItem(tupla[2])) # coluna CPF/CNPJ
            linha += 1

        self.lista_registro.setStyleSheet(self.recursos.FONTES.fonte_tabela)
        self.lista_registro.resizeColumnsToContents()        # Ajusta cada coluna ao conteúdo
        self.lista_registro.horizontalHeader().setStretchLastSection(True)



    def FormularioLeituraDados(self, pergunta, instrucao_in_box, regex_validacao, func): # [v1.0.0.03]: metodo pra ler nomes e etc
        container = QWidget()
        label = QLabel(pergunta)
        label.setFont(self.recursos.FONTES.fonte_texto_pergunta)
        line_edit = QLineEdit()
        line_edit.setFont(self.recursos.FONTES.fonte_texto_pergunta)
        line_edit.setValidator(regex_validacao) # cria restrição para a entrada ser apenas letras maiusculas, minusculas e espaços
        line_edit.setPlaceholderText(instrucao_in_box)
        line_edit.setContentsMargins(5,0,0,0) # remove margens adicionais
        btn_confirmar = QPushButton("OK")
        btn_confirmar.setFixedHeight(self.recursos.CONST.LARGURA_FORMULARIO_BUTTON)
        btn_confirmar.clicked.connect(lambda: self.capturar_nome_cpf(line_edit, func)) # [v1.0.0.03]: o endereço da função passada como parametro é apenas pra chamar essa função novamente de forma recursiva
        layout = QVBoxLayout(container) # conteiner vertical pro nome da pergunta ficar acima da caixa/box de leitura de nome
        layout_2 = QHBoxLayout() # conteiner horizontal pro button ficar de lado nesses tipos de formulario que requisitam entrada
        layout.addWidget(label) # insere a pergunta
        layout_2.addWidget(line_edit) # insere a caixa de leitura de texto à esquerda
        layout_2.addWidget(btn_confirmar, stretch=0.2) # insere o botão 'OK' comprimido ao lado da caixa de leitura de texto
        layout.addLayout(layout_2) # insere a box de leitura + botão
        
        object_proxy = self.insertOnGUI(container, 30)
        container.setStyleSheet(self.recursos.ESTILOS.button_style) # define o estilo 
        container.setFixedWidth(self.recursos.CONST.LARGURA_FORMULARIO) # define a largura na horizontal do formulário
        # para destruir os itens posteriormente em cancel()
        self.garbage_collector.append(container)
        self.garbage_collector.append(label)
        self.garbage_collector.append(line_edit)
        self.garbage_collector.append(btn_confirmar)
        self.garbage_collector.append(layout)
        self.garbage_collector.append(layout_2)
        self.garbage_collector.append(object_proxy)
        #necessario pra posicionar os botoes



    def showInformacoesServidor(self, titulo, cpf): # [v1.0.0.03]: metodo para mostrar informações do Servidor nos formularios
        servidor = self.getServidorByCPF(cpf)
        carro = self.getCarroByCPF(cpf)
        container = QWidget()
        texto = """
        <b>"""+titulo+"""</b><br>
        <br>
        <b>Nº VAGA:</b>&nbsp;"""+str(carro[0][1])+"""<br>
        <b>CPF:</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+servidor[0][0]+"""<br>
        <b>NOME:</b>&nbsp;&nbsp;&nbsp;&nbsp;"""+servidor[0][1]+"""<br>
        <b>ORGÃO:</b>&nbsp;&nbsp;&nbsp;"""+servidor[0][2]+"""<br>
        <b>CARRO:</b>&nbsp;&nbsp;&nbsp;"""+carro[0][3]+"""<br>
        <b>PLACA:</b>&nbsp;&nbsp;&nbsp;"""+carro[0][0]+"""<br>
        """
        label = QLabel(texto) #  [v1.0.0.03]: cria a label e define o titulo + informações
        label.setFont(self.recursos.FONTES.fonte_texto_desc_infoboxes_2)
        #label.setContentsMargins(0,0,0,0)
        #btn_confirmar = QPushButton("OK")
        #btn_confirmar.setFixedHeight(self.recursos.CONST.LARGURA_FORMULARIO_BUTTON)
        #btn_confirmar.clicked.connect(self.registroEntrada) # [v1.0.0.03]: o endereço da função passada como parametro é apenas pra chamar essa função novamente de forma recursiva
        layout = QVBoxLayout(container) # [v1.0.0.03]: conteiner vertical pro nome do titulo e as informações ficarem uma abaixo da outra
        layout.addWidget(label) # [v1.0.0.03]: insere o titulo + informações
        #layout.addWidget(btn_confirmar, stretch=0.2) # insere o botão 'OK' com tamanho comprimido 
        
        object_proxy = self.insertOnGUI(container, 30)
        container.setStyleSheet(self.recursos.ESTILOS.toolbar_estilo_2) # [v1.0.0.03]: altera o estilo para o mesmo estilo de planod e fundo do header (onde está a logomarca) da aplicação
        container.setFixedWidth(self.recursos.CONST.LARGURA_FORMULARIO) # define a largura na horizontal do formulário
        # para destruir os itens posteriormente em cancel()
        self.garbage_collector.append(container)
        self.garbage_collector.append(label)
        #self.garbage_collector.append(btn_confirmar)
        self.garbage_collector.append(layout)
        self.garbage_collector.append(object_proxy)
        #necessario pra posicionar os botoes
        self.coord_last_widget[1] =  container.y() + 100
        


    def acaoButtonRelatorio(self, enable_relatorio_completo):
        relatorio_pdf = "relatorio.pdf" # nome do arquivo a ser gerado
        titulo = f"<font size='16'>Relatório Completo</font>"
        
        # ETAPA 1: Consulta
        if(enable_relatorio_completo):
            relatorio_pdf = "relatorio_completo.pdf"
            tuplas_tabela = self.getAllFromRegistro() # [v1.0.0.03]: retorna todos os valores do registro
        else:
            if(self.num_vaga.displayText() != "-"): # [v1.0.0.03]: verifica se o usuario selecionou alguma vaga ou ainda esta o valor default
                relatorio_pdf = "relatorio_vaga_"+self.num_vaga.displayText()+".pdf" # [v1.0.0.03]: nome do arquivo concatenado com o numero da vaga
                tuplas_tabela = self.getRegistroByVaga(self.num_vaga.displayText()) # retorna todos os valores do registro onde tenha incidência do numero da vaga informado
                titulo = f"<font size='16'>Relatório da vaga nº: {self.num_vaga.displayText()}</font>"
            else:
                QMessageBox.warning(self.main_window, "Erro", "Selecione uma vaga para imprimir o relatório da vaga.")
                return # [v1.0.0.03]: sai da função sem nenhuma ação

        # ETAPA 2: Gerando o documento PDF com os dados
        doc = SimpleDocTemplate("conteudo.pdf")
        count = 0
        linhas = []
        linhas.append(["Placa", "Data/Hora (ENTRADA)", "Data/Hora (SAÍDA)", "CPF/CNPJ", "Servidor", "Orgão Vinculado"]) # define as colunas da tabela
        for tupla in tuplas_tabela:
            servidor = self.getServidorByCPF(tupla[2]) # pesquisa dados do servidor pra inserir na tabela em complemento
            if len(servidor) == 0:
                #visitante = self.getVisitante(tupla[7])
                tupla_formatada = [tupla[1], tupla[4], tupla[5], tupla[2], tupla[7].upper(), "[VISITANTE]: "+self.orgao_vinculado.displayText()]
            else:
                tupla_formatada = [tupla[1], tupla[4], tupla[5], tupla[2], servidor[0][1].upper(), servidor[0][2]]
            linhas.append(tupla_formatada) # insere uma linha no pdf
            #linhas.append(Spacer(1, 10))
            count+=1 # contador de linhas 

        tabela = Table(linhas) # cria a tabela
        tabela.setStyle(TableStyle(self.recursos.ESTILOS.estilo_tabela))

        elemento = []
        elemento.append(Paragraph(titulo))
        elemento.append(Spacer(1, 10 * mm))
        elemento.append(tabela)

        doc.build(elemento) # cria o pdf com os dados do registro
        
        # ETAPA 3: juntando PDF
        capa_pdf = PdfReader("capa.pdf")
        conteudo_pdf = PdfReader("conteudo.pdf")
        writer = PdfWriter()

        for page in capa_pdf.pages: # primeira página = capa
            writer.add_page(page)

        for page in conteudo_pdf.pages: # páginas geradas dinamicamente
            writer.add_page(page)

        with open(relatorio_pdf, "wb") as f: # salvar resultado
            writer.write(f)

        os.remove("conteudo.pdf") # deleta do diretorio o documento temporario "conteudo.pdf" 
        print(f"\n{self.recursos.CORES.ROXO}================================{self.recursos.CORES.RESET}")
        print(f"Relatório gerado com sucesso!\nVeja o arquivo {relatorio_pdf}.")
        print(f"{self.recursos.CORES.ROXO}================================{self.recursos.CORES.RESET}\n")
        QMessageBox.information(self.main_window, "Sucesso", f"Relatório gerado com sucesso!\nConsulte o arquivo '{relatorio_pdf}'.")

    def error_message(self, e):
        print(f"\n{self.recursos.CORES.VERMELHO}*******************************{self.recursos.CORES.RESET}")
        print("Ocorreu um erro!")
        print(f"{self.recursos.CORES.VERMELHO}*******************************{self.recursos.CORES.RESET}\n")
        print(f"[{self.recursos.CORES.AMARELO}Sidebar.py{self.recursos.CORES.RESET}]:Detalhes: ",e,"\n*******************************")
        QMessageBox.warning(self.main_window, "Atenção", "Ocorreu um erro no tratamento dos dados. Verifique o console.")


    #==============================================================================================
    # [v1.0.0.03]: animação para destaque de modificações de texto na interface 
    #==============================================================================================
    '''def destacar_campo(self, line_edit, cor=QColor(255, 165, 0, 200), pulsos=2):
        #Aplica um efeito de glow pulsante no QLineEdit para chamar atenção do usuário.
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(cor)
        shadow.setOffset(0, 0)
        shadow.setBlurRadius(0)
        line_edit.setGraphicsEffect(shadow)

        grupo = QSequentialAnimationGroup(line_edit)  # parent garante que não seja coletado pelo GC antes de terminar

        for _ in range(pulsos):
            sobe = QPropertyAnimation(shadow, b"blurRadius")
            sobe.setDuration(250)
            sobe.setStartValue(0)
            sobe.setEndValue(25)
            sobe.setEasingCurve(QEasingCurve.OutCubic)

            desce = QPropertyAnimation(shadow, b"blurRadius")
            desce.setDuration(250)
            desce.setStartValue(25)
            desce.setEndValue(0)
            desce.setEasingCurve(QEasingCurve.InCubic)

            grupo.addAnimation(sobe)
            grupo.addAnimation(desce)

        grupo.start()
    '''

    def destacar_campo(self, line_edit, extra_color=None):
        if(extra_color is None): extra_color = self.recursos.ESTILOS.status_vaga_white_default

        anim = QVariantAnimation(line_edit)
        anim.setDuration(600)
        anim.setStartValue(QColor(255, 165, 0, 180)) # [v1.0.0.03]: laranja
        anim.setEndValue(QColor(0, 0, 0)) # [v1.0.0.03]: preto
        anim.valueChanged.connect(lambda cor: line_edit.setStyleSheet(
            f"background-color: rgba({cor.red()}, {cor.green()}, {cor.blue()}, {cor.alpha()}); {extra_color}"
        ))
        anim.start()
        #anim.finished.connect(line_edit.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);")) # [v1.0.0.03]: corrige o problema do fundo nao voltar a ser preto
        line_edit._highlight_anim = anim  # [v1.0.0.03]: mantém referência viva

