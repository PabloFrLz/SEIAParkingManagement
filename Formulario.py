from PySide6.QtWidgets import QLabel, QComboBox, QWidget, QVBoxLayout


class Formulario(QWidget):

    def __init__(self, texto, items, categoria, onComplete=None):
        super().__init__()
        self.onComplete = onComplete
        self.result_to_return = None # variável para armazenar o resultado a ser retornado
        self.select = QVBoxLayout()
        self.label = QLabel(texto) # texto a ser mostrado, como por exemplo: "selecione a autarquia:"
        self.select.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.addItem("...")
        # lista de itens vindas do banco de dados
        self.combo.addItem("VISITANTE") # [v1.0.0.03]: colocando a opção de visitante para a etapa de permitir que visitantes usem vagas da secretaria
        for tupla in items:
            if categoria == 1: # servidores
                item = tupla[0]+" - "+tupla[1] # (CPF + Nome)
                self.combo.addItem(item) 
            elif categoria == 2: # carros
                item = f'{tupla[0]}  -  {tupla[3]}' # (placa/modelo)
                self.combo.addItem(item)
            else: # autarquias/data/horas/vagas
                self.combo.addItems(tupla)
        self.select.addWidget(self.combo)
        self.combo.currentTextChanged.connect(self.opcaoSelecionada) # conecta signal pra capturar escolha do usuario 
        # estilo dos formulários
        self.combo.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.30);   /* fundo leve */
            border: none;                                   /* remove borda */
            border-radius: 8px;
            padding: 6px 8px;
            color: white;
            font-size: 16px;
        """)
        self.setLayout(self.select)


    def opcaoSelecionada(self, text):
        # metodo para lidar com a opção selecionada
        print(f"Opção selecionada: {text}") # debug
        self.result_to_return = text # armazena a opção selecionada para ser retornada posteriormente
        if self.onComplete: # executa a função fornecida via parâmetro
            self.onComplete()

    def getResult(self):
        # método para retornar a opção selecionada
        return self.result_to_return

    def setResult(self, valor):
        self.result_to_return = valor 

    def getCoordX(self):
        return self.x()
    
    def getCoordY(self):
        return self.y()
    
    

