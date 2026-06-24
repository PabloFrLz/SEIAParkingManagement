import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap


class ArrowAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Caminhos das imagens (ajuste se necessário)
        self.arrow_images = [
            "1-arrow.png",
            "2-arrows.png",
            "3-arrows.png"
        ]
        
        self.current_index = 0
        
        # Label que vai mostrar as imagens
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: transparent;")  # ou a cor que precisar
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Timer para animação
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(180)  # Ajuste esse valor (ms) para controlar a velocidade
        
        self.next_frame()  # Mostra a primeira imagem

    def next_frame(self):
        pixmap = QPixmap(self.arrow_images[self.current_index])
        self.label.setPixmap(pixmap.scaledToWidth(120, Qt.SmoothTransformation))  # Ajuste o tamanho
        
        self.current_index = (self.current_index + 1) % len(self.arrow_images)


# ====================== Exemplo de uso ======================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = ArrowAnimation()
    window.setWindowTitle("Animação Setas")
    window.resize(300, 150)
    window.show()
    
    sys.exit(app.exec())