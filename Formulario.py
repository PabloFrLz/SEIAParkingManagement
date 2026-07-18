from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel, QComboBox, QWidget, QVBoxLayout
from PySide6.QtCore import Qt


class Formulario(QWidget):

    def __init__(self, janela_principal, texto, items, categoria, onComplete=None):
        super().__init__()
        self.main_window = janela_principal # [v1.0.0.03]: janela_principal faz referencia a SEIAParkingManagement, a classe de mais alto nivel
        self.recursos = self.main_window.recursos # [v1.0.0.03]: obtem a instancia da classe recursos
        self.onComplete = onComplete
        self.result_to_return = None # variável para armazenar o resultado a ser retornado
        self.select = QVBoxLayout()
        self.label = QLabel(texto) # texto a ser mostrado, como por exemplo: "selecione a autarquia:"
        self.label.setFont(self.recursos.FONTES.fonte_texto_pergunta)
        self.select.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.setEditable(True) # [v1.0.0.03]: importante definir como editável para permitir busca ao digitar
        self.combo.addItem("")
        # lista de itens vindas do banco de dados
        for tupla in items:
            if categoria == 1: # servidores
                item = tupla[0]+" - "+tupla[1] # (CPF + Nome)
                self.combo.addItem(item) 
            elif categoria == 2: # carros
                item = f'{tupla[0]} - {tupla[3]}' # (placa/modelo)
                self.combo.addItem(item)
            else: # autarquias/data/horas/vagas
                self.combo.addItems(tupla)

        # estilo dos formulários
        self.combo.setStyleSheet(self.recursos.ESTILOS.estilo_combo_box)
        # [v1.0.0.03]: adequando formulario pra permitir uma busca ao digitar 
        self.completer = self.combo.completer()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)   # busca em qualquer parte
        self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion) 
        #completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        
        
        popup = self.completer.popup()
        '''popup.setParent(self.combo.window())        # ← linha principal
        popup.setWindowFlags(Qt.Popup)'''
        
        

        self.combo.lineEdit().textEdited.connect(lambda: self.fix_pos_popup(popup))
        self.select.addWidget(self.combo)
        
        self.combo.activated.connect(lambda: self.opcaoSelecionada(self.combo.currentText())) # conecta signal pra capturar escolha do usuario 
        self.combo.setFixedWidth(350) # [v1.0.0.03]: fixa a largura dos formularios
        self.setLayout(self.select)


    def opcaoSelecionada(self, text):
        # metodo para lidar com a opção selecionada
        #self.combo.setCurrentIndex(int(text))
        print(f"[{self.recursos.CORES.AMARELO}Formulario.py{self.recursos.CORES.RESET}]: Opção selecionada: ({text})") # debug
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

    def fix_pos_popup(self, popup): # [v1.0.0.03]: metodo pra corrigir a posição xy da janela do QCompleter da self.search_box
        if not popup.isVisible():
            return  # nada pra reposicionar se a lista não esta aberta
        
        viewport_pos = self.main_window.mapFromScene(self.recursos.proxy_form_ref.pos())
        global_pos = self.main_window.viewport().mapToGlobal(viewport_pos) 
        popup.move(global_pos)
        self.combo.setFocus()
    
    

