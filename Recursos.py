from PySide6.QtGui import QBrush, QColor, QFont
from reportlab.lib import colors
import os, sys


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
        self.text_select_carro = "Selecione a placa e modelo do carro:"
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
        self.fonte_copyright = QFont("Segoe UI Condensed", 10) # [v1.0.0.03]: Fonte do texto de copyright

        self.fonte_texto_desc_infoboxes_2 = QFont("Consolas", 12)



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
    def __init__(self, fontes, path):
        self.FONTES = fontes
        self.PATH = path

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
        
        self.toolbar_estilo_2 =  """QLabel {
                background-color: #000000;     /* fundo que destoa */
                color: #828282;
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

        self.estilo_toggle_switch = f"""
            QCheckBox {{
                background-color: transparent;
                border: none;
            }}
            QCheckBox::indicator {{
                width: 30px;
                height: 30px;                 
            }}
            QCheckBox::indicator:unchecked {{
                /* image: url("{self.PATH.togle_switch_off}"); */
                
            }}
            QCheckBox::indicator:checked {{
                /* image: url("{self.PATH.togle_switch_on}"); */

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

        self.estilo_combo_box = """
            background-color: rgba(0, 0, 0, 0.30);   /* fundo leve */
            border: none;                                   /* remove borda */
            border-radius: 8px;
            padding: 6px 8px;
            color: white;
            font-size: 16px;
        """



class Paths:
    def __init__(self):
        self.background_app = self.resource_path("imagens/background-3.png") # [v1.0.0.03]: imagem de background geral da aplicação
        self.logo_marca_dagua_parana = self.resource_path("imagens/SEIA3.png") # [v1.0.0.03]: imagem de marca d'agua do governo do estado do paraná que fica visivel na seção onde mostra os numeros das vagas e as legendas
        self.edificio_hauer = self.resource_path("imagens/edificacoes.png") # [v1.0.0.03]: imagem do edificio hauer onde a SEIA está situada
        self.togle_switch_off = self.resource_path("imagens/off2.png") # [v1.0.0.03]: imagem do switch off
        self.togle_switch_on = self.resource_path("imagens/on2.png") # [v1.0.0.03]: imagem do switch on

        self.img_logo_sidebar = self.resource_path("imagens/nas_logo_3.png") # [v1.0.0.03]: imagem da logo do NAS disposto na parte superior da sidebar
        self.icon_btn_relatorio = self.resource_path("imagens/relatorio.png") # [v1.0.0.03]: imagem do button de relatorio por vaga
        self.icon_btn_relatorio_completo = self.resource_path("imagens/relatorio_completo.png") # [v1.0.0.03]: imagem do button relatorio completo

        self.img_carro_hatch = self.resource_path("imagens/hatch.png") # [v1.0.0.03]: imagem que representa o carro hatch da SEIA
        self.img_carro_sedan = self.resource_path("imagens/sedan.png") # [v1.0.0.03]: imagem que representa o carro sedan da SEIA
        self.img_carro_pickup = self.resource_path("imagens/pickup.png") # [v1.0.0.03]: imagem que representa o carro pickup da SEIA
        self.img_carro_pmpr = self.resource_path("imagens/pmpr-car.png") # [v1.0.0.03]: imagem que representa o carro da PMPR da SESP
        self.img_carro_deficiente = self.resource_path("imagens/deficiente.png") # [v1.0.0.03]: imagem que representa o carro de deficiente 
    
    def resource_path(self, relative_path): # [v1.0.0.03]: função para obter o caminho relativo 
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)



class Recursos:   # [v1.0.0.03]: classe principal que instancia as outras - criada pra centralizar as configurações graficas e de consulta da aplicação
    def __init__(self):
        self.FONTES = Fontes() # [v1.0.0.03]: instancia as fontes
        self.PATH = Paths() # [v1.0.0.03]: instancia os caminhos de diretorios de imagens e etc.
        self.ESTILOS = Estilos(self.FONTES, self.PATH) # [v1.0.0.03]: instancia os estilos
        self.CORES = Cores() # [v1.0.0.03]: instancia das cores
        self.TEXTOS = Textos() # [v1.0.0.03]: instancia os textos da interface
        self.CONST = Constantes() # [v1.0.0.03]: instancia as contantes da aplicação como dimensões em pixels dos objetos