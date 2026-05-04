from PySide6.QtCore import QObject, QPoint, QRegularExpression, Qt, QPropertyAnimation, Signal
from PySide6.QtWidgets import QFormLayout, QGraphicsProxyWidget, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PySide6.QtGui import QPixmap, QRegularExpressionValidator
from pymysql import Error
from shiboken6 import isValid

import Formulario


class Sidebar(QWidget, QObject):

    # Códigos de cores
    VERMELHO = '\033[91m'
    VERDE    = '\033[92m'
    AMARELO  = '\033[93m'
    AZUL     = '\033[94m'
    ROXO     = '\033[95m'
    CIANO    = '\033[96m'
    BRANCO   = '\033[97m'
    RESET    = '\033[0m'
    
    signal_insert = Signal(object)

    def __init__(self, janela_principal, WIDTH, HEIGHT, J, POS_X_SIDEBAR):

        super().__init__()
        self.POS_X_SIDEBAR = POS_X_SIDEBAR

        #======================================
        # Vars
        #======================================
        self.main_window = janela_principal
        self.conn = janela_principal.conn
        self.scene = janela_principal.scene
        self.check = [None, None, None, None]
        self.eixo_x_form = 30
        self.eixo_y_form = 150
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
        self.ctrl_forms = True
        self.coord_last_widget = []
        self.garbage_collector = []
        #self.conteiner = QVBoxLayout() # conteiner para agrupar elementos de outras paginas da sidebar que nao a de informações

        #======================================
        # Formularios
        #======================================
        self.form1 = None
        self.form2 = None
        self.form3 = None

        #======================================
        # Configurações iniciais
        #======================================
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        #main_layout.setSpacing(0)

        form = QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignRight)

        field_style = """
            QLineEdit, QComboBox {
                background-color: #000000;     /* fundo que destoa */
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 8px;            /* bordas arredondadas */
                padding: 8px 12px;
                font-size: 14px;
                min-height: 24px;
            }
            QLineEdit:focus {
                border: 1px solid #ffaa00;     /* destaque laranja quando focado */
                background-color: #2e2e2e;     /* fundo mais escuro quando focado */
            }
            QPushButton {
                color: #ffffff;
                background-color: transparent;
                border: 1px solid rgba(255, 165, 0, 80); /* borda laranja suave */
                padding: 12px 20px;
                text-align: left;
                font-size: 14px;
                border-radius: 6px;
                margin: 4px 8px;
            }
            
            QPushButton:hover {
                background-color: rgba(255, 165, 0, 80);   /* laranja suave */
            }
            
            QPushButton:pressed, QPushButton:checked {
                background-color: rgba(255, 140, 0, 160);
                color: white;
            }  
        """

        #======================================
        # infos da sidebar
        #======================================
        self.num_vaga = QLineEdit("-")
        self.orgao_vinculado = QLineEdit("-")
        self.orgao_vinculado.setStyleSheet("color: #A6E9FF;") #definindo cor pro nome do orgao
        self.modelo_carro = QLineEdit("-")
        self.placa_carro = QLineEdit("-")
        self.nome_servidor = QLineEdit("-")
        self.status_vaga = QLineEdit("-")
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
        self.lista_registro.setColumnCount(4)
        
        
        #======================================
        # formatação das informações da sidebar
        #======================================
        form.addRow("Nº vaga:", self.num_vaga)
        form.addRow("Órgão:", self.orgao_vinculado)
        form.addRow("Veículo:", self.modelo_carro)
        form.addRow("Placa:", self.placa_carro)
        form.addRow("Servidor:", self.nome_servidor)
        form.addRow("Status:", self.status_vaga)
        form.addRow("Registro:", None)
        form.addRow(self.lista_registro)

        self.setStyleSheet(field_style)

        #======================================
        # Sidebar
        #======================================
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(WIDTH - 890)           # largura da sidebar
        self.sidebar.setFixedHeight(HEIGHT + J - 100)          # altura da sidebar

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(20, 20, 20, 20)

        #======================================
        # Logomarca da SEIA na sidebar
        #====================================== 
        self.img = QPixmap("imagens/logo_seia_form_sidebar.png") #imagem de plano de fundo
        self.seia_logo = QLabel()
        self.seia_logo.setPixmap(self.img.scaled(
            260, 145,  # ajuste conforme necessário
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        self.sidebar_layout.addWidget(self.seia_logo) # insere na sidebar de infos de estacionamento
        
        self.stack = QStackedWidget()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)
        self.sidebar_layout.addLayout(form)

        #======================================
        # Botões de ação da sidebar
        #======================================
        # criação e estética dos botoes
        self.btn_registrar_saida = QPushButton("                    SAIDA") # cria
        self.btn_registrar_saida.setCheckable(True)
        self.sidebar_layout.addWidget(self.btn_registrar_saida) # insere na GUI
        self.btn_registrar_saida.clicked.connect(self.acaoButtonSaida)
        
        self.btn_registrar_entrada = QPushButton("                 ENTRADA")
        self.btn_registrar_entrada.setCheckable(True) # destaca o botão selecionado
        self.sidebar_layout.addWidget(self.btn_registrar_entrada)
        self.btn_registrar_entrada.clicked.connect(self.acaoButtonEntrada)

        self.btn_cadastro = QPushButton("                 CADASTRO")
        self.btn_cadastro.setCheckable(True) # destaca o botão selecionado
        self.sidebar_layout.addWidget(self.btn_cadastro)
        self.btn_cadastro.clicked.connect(self.acaoButtonCadastro)

        #======================================
        # configurando restrições de entrada - para etapa de cadastro de servidor
        #======================================
        self.regex_cpf = QRegularExpression("^[0-9]*$") # para o CPF
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
    

    def atualizar_info(self, info): 
        #atualizando a cor do campo "Status da vaga"
        if info.status == 0: # disponivel
            self.status_vaga.setStyleSheet("color: green; font-weight: bold;")
        elif info.status == 1: # ocupada
            self.status_vaga.setStyleSheet("color: red; font-weight: bold;")
        elif info.status == 2: # reservada
            self.status_vaga.setStyleSheet("color: orange; font-weight: bold;")

        self.sentinel = info

        #consulta pra pegar a ultima entrada registrada na tabela registro para o numero de vaga atual
        ultimo_registro_da_vaga = self.getSaidaOnRegistro(info.id) # pega a ultima saida registrada pra uma vaga especifica
        self.lista_registro.clear() # limpa entradas de outra vagas na tabela de registros da vaga especifica
        self.lista_registro.setRowCount(0) # reseta o contador de linhas da tabela

        if len(ultimo_registro_da_vaga) != 0:
            #consulta pra pegar dados da vaga/carro
            cursor = self.conn.cursor()
            cursor.execute(f"select * from carro where placa='{ultimo_registro_da_vaga[0][1]}'")
            dados_carro = cursor.fetchall()

            #consulta pra pegar o nome do servidor
            cursor.execute(f"select * from servidor where cpf_cnpj='{ultimo_registro_da_vaga[0][2]}'")
            dados_servidor = cursor.fetchall()

            # atualizando os valores dos campos
            self.num_vaga.setText(str(info.id))
            self.orgao_vinculado.setText(dados_carro[0][2])
            self.modelo_carro.setText(dados_carro[0][3])
            self.placa_carro.setText(dados_carro[0][0])
            self.nome_servidor.setText(dados_servidor[0][1])
            self.status_vaga.setText(info.status_name)

            #atualizando a lista de registros            
            self.updateHistoricoRegistro(ultimo_registro_da_vaga[0][3]) 

        else:
            self.num_vaga.setText(str(info.id))
            self.orgao_vinculado.setText(" - ")
            self.modelo_carro.setText(" - ")
            self.placa_carro.setText(" - ")
            self.nome_servidor.setText(" - ")
            self.status_vaga.setText(info.status_name)


        #historico de reservas no formato de lista (exemplo)
    
    def acaoButtonSaida(self):
        if self.num_vaga.displayText() != "-" and (self.status_vaga.displayText() != "OCUPADA" and self.status_vaga.displayText() != "RESERVADA"):
            self.transitToFormulario() # animação que empurra pro lado direito as infos
            self.titulo = self.insertHeader("REGISTRAR HORÁRIO")#gera logo no topo e titulo da seção 
            self.ctrl_forms = True # habilita formularios de registro de ENTRADA/SAIDA 
            self.controlForms() # gerando o 1º form
        else:
            QMessageBox.warning(self.main_window, "Atenção", "Vaga selecionada é inválida ou a vaga está OCUPADA/RESERVADA.")


    def acaoButtonEntrada(self):
        dados = None
        if self.num_vaga.displayText() != "-" and (self.status_vaga.displayText() == "OCUPADA" or self.status_vaga.displayText() == "RESERVADA"):
            dados = self.getSaidaOnRegistro(self.num_vaga.displayText()) #obtem a ultima saida registrada pra uma vaga especifica
            self.insertRegistro(dados=dados)
        else:
            QMessageBox.warning(self.main_window, "Atenção", "Vaga selecionada é inválida ou a vaga ainda está DISPONÍVEL.")

    def acaoButtonCadastro(self):
        self.transitToFormulario() # animação que empurra pro lado direito as infos
        self.titulo = self.insertHeader("CADASTRAR SERVIDOR")#gera logo no topo e titulo da seção 
        self.ctrl_forms = False # habilita formularios de cadastro de servidor;
        self.controlForms() 



    # transiciona para o formulario de registro e posteriomente de volta para a tela de informações da vaga
    def transitToFormulario(self):
        if self.turnRound: # empurra os elementos da sidebar pra direita (ocultando-os)
            self.animation.setStartValue(QPoint(0, 0))
            self.animation.setEndValue(QPoint(self.largura + 400, 0))
            self.animation.start() #inicia a animação

        else: # puxa os elementos da sidebar pra esquerda (mostrando-os de volta)
            self.animation.setStartValue(QPoint(self.largura + 400, 0))
            self.animation.setEndValue(QPoint(0, 0))  
            self.animation.start() #inicia a animação

        self.turnRound = not self.turnRound # inverte o estado para a próxima vez que o botão for clicado
    
    def geraFormulario(self, consulta, texto):
        #consulta ao banco de dados para obter os dados cadastrados
        cursor = self.conn.cursor()
        cursor.execute(consulta)
        resultado_pesquisa = cursor.fetchall()

        form = Formulario.Formulario(texto, resultado_pesquisa, self.categoria, onComplete=self.controlForms) 
        self.insertOnGUI(form, 0)#inserção na GUI
        return form
    
    def controlForms(self):


        if self.ctrl_forms: # REGISTRO
            if (self.check[0] is None): 
                texto = "Selecione a autarquia:"
                consulta = "select * from autarquia"
                self.categoria = 0
                self.form1 = self.geraFormulario(consulta, texto) # gera o primeiro formulario
                self.check[0] = True #desabilita esse bloco condicional na proxima iteração
            
            elif (self.check[1] is None): 
                #consulta se tem carros disponiveis pra eivtar ficar travado em etapas futuras
                situacao = self.consultaDisponibilidadeFrota(self.form1.getResult())
                if situacao:
                    texto = "Selecione o servidor responsável:"
                    consulta = "select * from servidor where autarquia='{}'".format(self.form1.getResult())
                    self.categoria = 1
                    self.form2 = self.geraFormulario(consulta, texto)
                    self.check[1] = True
                    self.form1.setDisabled(True)
                else:
                    QMessageBox.warning(self.main_window, "Atenção", "Não há carros disponíveis para o orgão {}.".format(self.form1.getResult()))
                    self.cancel()

            elif (self.check[2] is None):
                texto = "Selecione o carro:"
                #consulta = "select * from carro where autarquia='{}' and placa not in (select placa from registro)".format(self.form1.getResult()) # seleciona todos os veiculos que são do orgão público e que nao estão no registro. 
                consulta = f"SELECT * FROM carro c WHERE c.autarquia = '{self.form1.getResult()}' AND c.placa NOT IN (SELECT r.placa FROM registro r WHERE r.tipo = 'SAIDA')"
                self.categoria = 2
                self.form3 = self.geraFormulario(consulta, texto)
                self.coord_last_widget.append(self.form3.getCoordX()) # para poder posicionar os botoes corretamente - se tivesse usando conteiner nao precisaria
                self.coord_last_widget.append(self.form3.getCoordY())
                self.check[2] = True
                self.form2.setDisabled(True)
            
            elif(self.check[3] is None):
                self.check[3] = True
                # Button pra confirmar entrada no banco de dados
                self.btn_commit = self.insertButton("CONFIRMAR", self.insertRegistro) #insere na tabela registro
                self.btn_cancel = self.insertButton("CANCELAR", self.cancel)
        else: # CADASTRO
            if (self.check[0] is None): 
                texto = "Selecione a autarquia:"
                consulta = "select * from autarquia"
                self.categoria = 0
                self.form1 = self.geraFormulario(consulta, texto) # gera o primeiro formulario
                self.check[0] = True #desabilita esse bloco condicional na proxima iteração

            elif (self.check[1] is None): 
                container = QWidget()
                label = QLabel("Digite o nome do servidor:")
                line_edit = QLineEdit()
                line_edit.setValidator(self.validator_nome) # cria restrição para a entrada ser apenas letras maiusculas, minusculas e espaços
                line_edit.setPlaceholderText("Digite o nome aqui...")
                btn_confirmar = QPushButton("PRÓXIMO")
                btn_confirmar.clicked.connect(lambda: self.capturar_nome(line_edit))
                layout = QVBoxLayout(container) 
                layout.addWidget(label)
                layout.addWidget(line_edit)
                layout.addWidget(btn_confirmar)
                self.setLayout(layout)
                self.insertOnGUI(container, 25)
                self.check[1] = True
                # para destruir os itens posteriormente em cancel()
                self.garbage_collector.append(container)
                self.garbage_collector.append(label)
                self.garbage_collector.append(line_edit)
                self.garbage_collector.append(btn_confirmar)
                self.garbage_collector.append(layout)

            elif (self.check[2] is None): 
                container = QWidget()
                label = QLabel("Digite o CPF ou CNPJ do servidor:")
                line_edit = QLineEdit()
                line_edit.setValidator(self.validator_cpf) # cria restrição para a entrada ser apenas numeros sem pontos, hifens ou letras.
                line_edit.setMaxLength(11) # limita pra inserir apenas 11 digitos e nao mais que isso
                line_edit.setPlaceholderText("ex.: 50545642300...")
                btn_confirmar = QPushButton("PRÓXIMO")
                btn_confirmar.clicked.connect(lambda: self.capturar_cpf(line_edit))
                layout = QVBoxLayout(container)
                layout.addWidget(label)
                layout.addWidget(line_edit)
                layout.addWidget(btn_confirmar)
                self.setLayout(layout)
                self.insertOnGUI(container, 35)
                self.check[2] = True
                # para destruir os itens posteriormente em cancel()
                self.garbage_collector.append(container)
                self.garbage_collector.append(label)
                self.garbage_collector.append(line_edit)
                self.garbage_collector.append(btn_confirmar)
                self.garbage_collector.append(layout)
                #necessario pra posicionar os botoes
                self.coord_last_widget.append(container.x()) 
                self.coord_last_widget.append(container.y()+20)

            
            elif(self.check[3] is None):
                self.check[3] = True
                # Button pra confirmar entrada no banco de dados
                self.btn_commit = self.insertButton("CONFIRMAR", self.insertServidor) # Insere na tabela servidor
                self.btn_cancel = self.insertButton("CANCELAR", self.cancel)
            

    def capturar_nome(self, line_edit):
        self.nome = line_edit.text().strip()
        self.controlForms()

    def capturar_cpf(self, line_edit):
        self.cpf = line_edit.text().strip()
        self.controlForms()

    def insertRegistro(self, dados=None):
        print(f"\n\n {self.AMARELO}***************** ( DATABASE INSERT) *****************{self.RESET}\n")

        num_vaga = self.num_vaga.displayText()
        if dados is not None:
            #obtem os dados direto do banco
            placa = dados[0][1]
            cpf_cnpj = dados[0][2]
            tipo = "ENTRADA"
            sql = f"UPDATE registro SET data_entrada = NOW(), tipo = '{tipo}' WHERE placa = '{placa}' AND cpf_cnpj = '{cpf_cnpj}' AND data_entrada IS NULL AND tipo = 'SAIDA'"
        else:
            #obtem os dados apartir dos formularios de saida
            servidor = self.form2.getResult() 
            carro = self.form3.getResult()
            tipo = "SAIDA"
            sql = "INSERT INTO registro (placa, cpf_cnpj, num_vaga, data_saida, tipo) VALUES (%s, %s, %s, NOW(), %s)"
            #tratamento dos dados
            cpf_cnpj, nome_servidor = servidor.split(" - ")
            placa, modelo = carro.split(" - ")
            print("Nº vaga:", num_vaga)
            print("CPF/CNPJ:", cpf_cnpj)
            print("Nome:", nome_servidor)
            print("Placa:", placa)
            print("Modelo:", modelo)
            
        
        print(f"\n{self.AMARELO}================================{self.RESET}")
        print(f"{self.AMARELO}Dados extraídos! {self.RESET}")
        print(f"{self.AMARELO}================================{self.RESET}\n")
            
        #inserção no banco
        try:
            cursor = self.conn.cursor()
            #data e hora serão calculados automaticamente pelo banco de dados MySQL com a clausula NOW()
            if tipo == "SAIDA":
                cursor.execute(sql, (placa, cpf_cnpj, num_vaga, tipo))
            else:
                cursor.execute(sql)
            
            self.conn.commit() # commit - pra persistir no banco
            print(f"\n{self.VERDE}================================{self.RESET}")
            print(f"{self.VERDE}Dados inseridos no Registro com sucesso!{self.RESET}")
            print(f"{self.VERDE}================================{self.RESET}\n")
            

            self.signal_insert.emit(self) # emite o sinal pra atualizar o estado visual das vagas na interface
            QMessageBox.information(self.main_window, "Sucesso", "Registro efetuado com sucesso!")
            self.cancel(self.sentinel) # reseta informações e retrocede sidebar

        except Error as e:
            #text_screen = QLabel("<font color='red'> O Registro não foi salvo! Verifique o console para mais informações.</font>")
            #self.insertOnGUI(text_screen, 440)
            print(f"\n{self.VERMELHO}*******************************{self.RESET}")
            print(f"{self.VERMELHO}Ocorreu um erro! {self.RESET}")
            print(f"{self.VERMELHO}*******************************{self.RESET}\n")
            print("Detalhes: ",e,"\n*******************************")
            QMessageBox.warning(self.main_window, "Atenção", "Ocorreu um erro no tratamento dos dados. Verifique o console.")
            

    def insertServidor(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"insert into Servidor values('{self.cpf}', '{self.nome}', '{self.form1.getResult()}')")
            self.conn.commit()
            print(f"\n{self.VERDE}================================{self.RESET}")
            print(f"{self.VERDE}Servidor registrado com sucesso!{self.RESET}")
            print(f"{self.VERDE}================================{self.RESET}\n")

            QMessageBox.information(self.main_window, "Sucesso", "Servidor cadastrado com sucesso!")
            self.cancel(self.sentinel) # reseta informações e retrocede sidebar

        except Error as e:
            print(f"\n{self.VERMELHO}*******************************{self.RESET}")
            print(f"{self.VERMELHO}Ocorreu um erro! {self.RESET}")
            print(f"{self.VERMELHO}*******************************{self.RESET}\n")
            print("Detalhes: ",e,"\n*******************************")
            QMessageBox.warning(self.main_window, "Atenção", "Ocorreu um erro no tratamento dos dados. Verifique o console.")
            

    def insertOnGUI(self, object, deslocamento_mais_profundo):
        #inserção na GUI
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(object)
        self.eixo_y_form += 70 + deslocamento_mais_profundo
        proxy.setPos(self.POS_X_SIDEBAR + self.eixo_x_form, self.eixo_y_form)
        self.scene.addItem(proxy)
        return proxy # retorna o proxy pra caso precise destruir

    
    def insertHeader(self, msg):
        #Conteiner
        conteiner = QWidget()
        layout = QVBoxLayout(conteiner)

        # Logomarca SEIA 2
        seia_logo_2 = QLabel()
        seia_logo_2.setPixmap(self.img.scaled(
            260, 145,  # ajuste conforme necessário
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        #texto
        text = QLabel("<font size='6'>"+msg+"</font")

        #inserindo no conteiner
        layout.addWidget(seia_logo_2)
        layout.addWidget(text)

        #inserindo conteiner no proxy grafico
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(conteiner)
        pos_x = 20
        proxy.setPos(self.POS_X_SIDEBAR + pos_x, 0)

        #inserindo o proxy no cenário
        self.scene.addItem(proxy) 
        return proxy


    def insertButton(self, msg, action=None):
        button = QPushButton(msg)
        button.setCheckable(True)
        button.clicked.connect(lambda: action()) # chama o metodo para inserção na tabela registro do banco de dados
        proxyBtn = QGraphicsProxyWidget()
        proxyBtn.setWidget(button)
        x = self.coord_last_widget[0] + self.pos_button_x
        y = self.coord_last_widget[1] + self.pos_button_y
        proxyBtn.setPos(x, y)
        self.scene.addItem(proxyBtn)
        if self.pos_button_x == 0:
            self.pos_button_x = 140 # coloca o prox. button do lado direito do button anterior
        else:
            self.pos_button_x = 0
            #self.pos_button_y += 90 # coloca o prox. button abaixo dos dois buttons já gerados
        
        style_f = """
            QPushButton {
                color: #ffffff;
                background-color: transparent;
                border: 1px solid rgba(255, 165, 0, 80); /* borda laranja suave */
                padding: 12px 20px;
                text-align: left;
                font-size: 14px;
                border-radius: 6px;
                margin: 4px 8px;
            }
            
            QPushButton:hover {
                background-color: rgba(255, 165, 0, 80);   /* laranja suave */
            }
            
            QPushButton:pressed, QPushButton:checked {
                background-color: rgba(255, 140, 0, 160);
                color: white;
            }  
        """

        button.setStyleSheet(style_f)
        return button
        
    def reset(self):
        self.eixo_y_form = 150
        self.check = [None, None, None, None] # habilitando os forms
        # destruir os self.forms


    def cancel(self, param1=None):
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
        if self.titulo is not None and isValid(self.titulo):
            self.titulo.deleteLater()
            self.titulo = None
        
        # destruindo os formularios de leitura pra cadastro de servidor
        if self.garbage_collector is not None:
            for item in self.garbage_collector:
                if isValid(item):
                    item.deleteLater()
                    item = None

        self.reset() # reseta demais variaveis auxiliares
        if not self.turnRound:
            self.transitToFormulario() #animação que transiciona de volta para a interface padrão.
        
        if param1 is not None:
            self.atualizar_info(self.sentinel)

    def consultaDisponibilidadeFrota(self, valor):
        cursor = self.conn.cursor()
        cursor.execute("select * from carro where autarquia='{}' and placa not in (select placa from registro)".format(valor))
        result = cursor.fetchall()

        if len(result) == 0:
            return False # não há frota disponível
        else:
            return True
        
    
    def getInstance(self):
        return self
    
    def getSaidaOnRegistro(self, num_vaga):
        cursor = self.conn.cursor()
        cursor.execute(f"select * from registro where num_vaga='{num_vaga}' order by id desc limit 1")
        return cursor.fetchall() # retorna uma unica tupla e nao uma lista de tuplas

    def updateHistoricoRegistro(self, num_vaga):
        cursor = self.conn.cursor()
        cursor.execute(f"select * from registro where num_vaga='{num_vaga}'")
        entradas_tabela = cursor.fetchall()

        linha = 0
        self.lista_registro.setHorizontalHeaderLabels(["Placa", "Data/Hora", "Tipo", "CPF/CNPJ"])
        for tupla in entradas_tabela:
            self.lista_registro.insertRow(linha) # insere uma nova linha
            self.lista_registro.setItem(linha, 0, QTableWidgetItem(tupla[1])) # coluna Placa
            self.lista_registro.setItem(linha, 1, QTableWidgetItem(str(tupla[4]))) # coluna Data/Hora
            self.lista_registro.setItem(linha, 2, QTableWidgetItem(tupla[6])) # coluna Tipo
            self.lista_registro.setItem(linha, 3, QTableWidgetItem(tupla[2])) # coluna CPF/CNPJ
            linha += 1


        self.lista_registro.resizeColumnsToContents()        # Ajusta cada coluna ao conteúdo
        self.lista_registro.horizontalHeader().setStretchLastSection(True)

    
