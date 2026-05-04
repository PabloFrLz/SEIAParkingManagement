from PySide6.QtWidgets import QLabel, QComboBox, QWidget, QVBoxLayout

import Sidebar


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
        for tupla in items:
            if categoria == 1: # servidores
                item = tupla[0]+"  -  "+tupla[1] # (CPF + Nome)
                self.combo.addItem(item) 
            elif categoria == 2: # carros
                item = f'{tupla[0]}  -  {tupla[3]}' # (placa/modelo)
                self.combo.addItem(item)
            else: # autarquias/data/horas
                self.combo.addItems(tupla)
        self.select.addWidget(self.combo)
        self.combo.currentTextChanged.connect(self.opcaoSelecionada) # conecta signal pra capturar escolha do usuario 

        self.setLayout(self.select)


    def opcaoSelecionada(self, text):
        # metodo para lidar com a opção selecionada
        print(f"Opção selecionada: {text}") # debug
        self.result_to_return = text # armazena a opção selecionada para ser retornada posteriormente
        if self.onComplete:
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
    
    

