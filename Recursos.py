from PySide6.QtCore import QObject, QPoint, QRegularExpression, Qt, QPropertyAnimation, Signal
from PySide6.QtWidgets import QFormLayout, QGraphicsProxyWidget, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PySide6.QtGui import QBrush, QColor, QFont, QPixmap, QRegularExpressionValidator
from pymysql import Error
from shiboken6 import isValid
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm


class Constantes:
    def __init__(self):
        self.LARGURA_FORMULARIO = 400 # largura dos formularios como o de leitura de nomes na etapa de registro de entrada de servidor e visitante
        self.LARGURA_FORMULARIO_BUTTON = self.LARGURA_FORMULARIO * 0.125
class Textos:
    def __init__(self):
        # [v1.0.0.03]: textos da interface - fica fácil de manipular e modificar centralizando nessa classe todos os textos
        self.text_interface = []
        self.text_interface.append("Nº vaga:")
        self.text_interface.append("Órgão:")
        self.text_interface.append("Veículo:")
        self.text_interface.append("Placa:")
        self.text_interface.append("Servidor:")
        self.text_interface.append("Status:")
        self.text_interface.append("Registro:")

        # [v1.0.0.03]: textos da interface - textos da seção de perguntas ao usuario, como "selecione a autarquia:"
        self.text_select_autarquia = "Selecione a autarquia:"
        self.text_select_servidor = "Selecione o servidor:"
        self.text_select_carro = "Selecione o carro:"
        self.text_insert_nome_servidor = "Digite o nome do servidor:"
        self.text_insert_nome_visitante = "Digite o nome do visitante:"
        self.text_insert_cpf_servidor = "Digite o CPF ou CNPJ do servidor:"



class Fontes:
    def __init__(self):
        self.fonte_texto_desc_infoboxes = QFont("Segoe UI", 12) # [v1.0.0.03]:  fonte para perguntas como por exemplo: "selecione a autarquia:"
        self.fonte_texto_infoboxes = "font-size: 18px" # [v1.0.0.03]: tamanho da fonte dos textos das boxes da sidebar, como "98, SESP, Carlos João Rodrigues, OCUPADO"
        self.fonte_texto_pergunta = QFont("Segoe UI", 14) # [v1.0.0.03]:  fonte para perguntas como por exemplo: "selecione a autarquia:"
        self.fonte_tabela = "font-size: 14px" # [v1.0.0.03]: tamanho da fonte da tabela de registros da sidebar
        self.fonte_texto_buttons = "font-size: 18px" # [v1.0.0.03]: tamanho da fonte do texto dos botões da interface
        #self.fonte_title_header = "<font size='6'>" # [v1.0.0.03]: tamanho da fonte do título das seções, como "REGISTRAR ENTRADA", ou "REMOVER SERVIDOR"
        self.fonte_title_header = QFont("Segoe UI", 20) # [v1.0.0.03]: tamanho da fonte do título das seções, como "REGISTRAR ENTRADA", ou "REMOVER SERVIDOR"



class Cores:
    def __init__(self):
        # Códigos de cores pro CONSOLE
        self.VERMELHO = '\033[91m'
        self.VERDE    = '\033[92m'
        self.AMARELO  = '\033[93m'
        self.AZUL     = '\033[94m'
        self.ROXO     = '\033[95m'
        self.CIANO    = '\033[96m'
        self.BRANCO   = '\033[97m'
        self.RESET    = '\033[0m'

        # Cores pra tabela do registro da sidebar
        self.BRUSH_ENTRADA = QBrush(QColor(0, 122, 204))        # azul médio
        self.BRUSH_ENTRADA_ALPHA = QBrush(QColor(0, 122, 204, 40))

        self.BRUSH_SAIDA = QBrush(QColor(255, 140, 0))          # laranja
        self.BRUSH_SAIDA_ALPHA = QBrush(QColor(255, 140, 0, 40))

        # cores
        self.cor_orgao_vinculado_box = "color: #A6E9FF;"



class Estilos:
    def __init__(self, fontes):
        self.FONTES = fontes

        # estilo toolbars de fundo
        self.toolbar_estilo =  """QLabel {
                background-color: #000000;     /* fundo que destoa */
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 8px;            /* bordas arredondadas */
                padding: 8px 12px;
                opacity: 0.5;
                }
            """

        # estilos de botões 
        self.button_style = f"""
            QLineEdit, QComboBox {{
                background-color: #000000;     /* fundo que destoa */
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 8px;            /* bordas arredondadas */
                padding: 8px 12px;
                {self.FONTES.fonte_texto_buttons};
                min-height: 24px;
            }}
            QLineEdit:focus {{
                border: 1px solid #ffaa00;     /* destaque laranja quando focado */
                background-color: #080808;     /* fundo mais escuro quando focado */
            }}
            QPushButton {{
                color: #ffffff;
                background-color: transparent;
                border: 1px solid rgba(255, 165, 0, 80); /* borda laranja suave */
                padding: 12px 20px;
                text-align: center;
                {self.FONTES.fonte_texto_buttons};
                border-radius: 6px;
                margin: 4px 8px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(255, 165, 0, 80);   /* laranja suave */
            }}
            
            QPushButton:pressed {{
                background-color: rgba(0, 255, 155, 80);
                color: white;
            }}
        """

        self.button_style_2 = f"""
            QPushButton {{
                color: #ffffff;
                background-color: transparent;
                border: 1px solid rgba(255, 165, 0, 80); /* borda laranja suave */
                padding: 12px 20px;
                text-align: center;
                {self.FONTES.fonte_texto_buttons};
                border-radius: 6px;
                margin: 4px 8px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(0, 255, 155, 80); 
            }}
            
            QPushButton:pressed {{
                background-color: rgba(0, 255, 0, 160);
                color: white;
            }}
        """

        self.button_style_3 = f"""
            QPushButton {{
                color: #ffffff;
                background-color: transparent;
                border: 1px solid rgba(255, 165, 0, 80); /* borda laranja suave */
                padding: 12px 20px;
                text-align: center;
                {self.FONTES.fonte_texto_buttons};
                border-radius: 6px;
                margin: 4px 8px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(255, 165, 0, 80);   /* laranja suave */
            }}
            
            QPushButton:pressed {{
                background-color: rgba(255, 140, 0, 160);
                color: white;
            }}
        """

        self.button_style_4 = f"""
            QPushButton {{
                color: #FFFFFF;
                background-color: transparent;
                border: 1px solid rgba(255, 165, 0, 80); /* borda laranja suave */
                padding: 12px 20px;
                text-align: center;
                {self.FONTES.fonte_texto_buttons};
                border-radius: 6px;
                margin: 4px 8px;
            }}

            QPushButton:hover {{
                background-color: rgba(255, 0, 55, 80);   /* laranja suave */
            }}
            
            QPushButton:pressed {{
                background-color: rgba(255, 18, 70, 160);
                color: white;
            }} 
        """
        self.status_vaga_green = "color: green; font-weight: bold;"
        self.status_vaga_red = "color: red; font-weight: bold;"
        self.status_vaga_orange = "color: orange; font-weight: bold;"

        # estilo da tabela com os dados da vaga no arquivo de relatorio.pdf
        self.estilo_tabela = [
            # fundo cabeçalho
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            # cor do texto cabeçalho
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            # alinhamento
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            # fonte cabeçalho
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            # tamanho fonte
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            # padding cabeçalho
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            # cor linhas internas
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]



class Paths:
    def __init__(self):
        self.img_logo_sidebar = "imagens/nas_logo.png"
        self.icon_btn_relatorio = "imagens/relatorio.png"
        self.icon_btn_relatorio_completo = "imagens/relatorio_completo.png"



class Recursos:   # [v1.0.0.03]: classe principal que instancia as outras - criada pra centralizar as configurações graficas e de consulta da aplicação
    def __init__(self):
        self.FONTES = Fontes() # [v1.0.0.03]: instancia as fontes
        self.ESTILOS = Estilos(self.FONTES) # [v1.0.0.03]: instancia os estilos
        self.CORES = Cores() # [v1.0.0.03]: instancia das cores
        self.PATH = Paths() # [v1.0.0.03]: instancia os caminhos de diretorios de imagens e etc.
        self.TEXTOS = Textos() # [v1.0.0.03]: instancia os textos da interface
        self.CONST = Constantes() # [v1.0.0.03]: instancia as contantes da aplicação como dimensões em pixels dos objetos