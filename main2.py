from PySide6.QtWidgets import QApplication, QComboBox, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
import sys

app = QApplication(sys.argv)

janela = QWidget()
layout = QVBoxLayout(janela)

combo = QComboBox()
combo.setEditable(True)

itens = [
    "Curitiba",
    "São Paulo",
    "São Cristovão",
    "São Petersburgo",
    "Rio de Janeiro",
    "Rio de Fevereiro",
    "Rio de Março",
    "Porto Alegre",
    "Porto da Mancha Verde",
    "Porto de La Muerte"
    "Florianópolis",
    "Londrina",
    "Longarina"
]

combo.addItems(itens)

# pesquisa enquanto digita
completer = combo.completer()
completer.setCaseSensitivity(Qt.CaseInsensitive)
completer.setFilterMode(Qt.MatchContains)  # busca em qualquer parte do texto
combo.lineEdit().textEdited.connect(combo.showPopup)

layout.addWidget(combo)

janela.show()
sys.exit(app.exec())