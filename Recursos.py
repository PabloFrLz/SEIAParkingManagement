from PySide6.QtGui import QBrush, QColor, QFont
from reportlab.lib import colors
import os, sys


class Constantes:
    def __init__(self):
        self.LARGURA_FORMULARIO = 400 # largura dos formularios como o de leitura de nomes na etapa de registro de entrada de servidor e visitante
        self.LARGURA_FORMULARIO_BUTTON = self.LARGURA_FORMULARIO * 0.125

        self.MINIMUN_CHARACTER_TO_NAME = 10

        self.ICON_SIZE_X = 115   # tamanho dos icones dos botões da sidebar
        self.ICON_SIZE_Y = 129   # tamanho dos icones dos botões da sidebar




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
        self.text_insert_placa = "Digite a placa do carro:"
        self.text_insert_contato = "Digite o contato do visitante:"
        self.text_insert_modelo_carro = "Insira o modelo do carro:"
        self.text_insert_setor = "Insira o setor responsável pelo veículo:"
        self.text_select_vaga = "Selecione uma das vagas vinculadas ao orgão selecionado:"



class Fontes:
    def __init__(self):
        self.fonte_texto_desc_infoboxes = QFont("SF Pro Text", 13) # [v1.0.0.03]:  fonte para perguntas como por exemplo: "selecione a autarquia:"
        self.fonte_texto_infoboxes = "font-size: 18px" # [v1.0.0.03]: tamanho da fonte dos textos das boxes da sidebar, como "98, SESP, Carlos João Rodrigues, OCUPADO"
        self.fonte_texto_pergunta = QFont("SF Pro Text", 14) # [v1.0.0.03]:  fonte para perguntas como por exemplo: "selecione a autarquia:"
        self.fonte_tabela = "font-family: 'SF Pro Text'; font-size: 14px;" # [v1.0.0.03]: tamanho da fonte da tabela de registros da sidebar
        self.fonte_texto_buttons = "font-size: 18px" # [v1.0.0.03]: tamanho da fonte do texto dos botões da interface
        self.fonte_texto_buttons_2 = "font-size: 12px"
        #self.fonte_title_header = "<font size='6'>" # [v1.0.0.03]: tamanho da fonte do título das seções, como "REGISTRAR ENTRADA", ou "REMOVER SERVIDOR"
        self.fonte_title_header = QFont("SF Pro Text", 20) # [v1.0.0.03]: tamanho da fonte do título das seções, como "REGISTRAR ENTRADA", ou "REMOVER SERVIDOR"
        self.fonte_copyright = QFont("Segoe UI Condensed", 10) # [v1.0.0.03]: Fonte do texto de copyright
        self.fonte_family_geral = "font-family: 'SF Pro Text';"

        self.fonte_texto_desc_infoboxes_2 = QFont("SF Pro Text", 12)
        self.fonte_texto_placa = QFont("Consolas", 16, QFont.Bold)

        self.fonte_texto_toggle = "font-size: 14px"



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
            QLineEdit, QComboBox, QTextEdit {{
                background-color: #000000;     /* fundo que destoa */
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 8px;            /* bordas arredondadas */
                padding: 8px 12px;
                {self.FONTES.fonte_texto_buttons};
                {self.FONTES.fonte_family_geral};
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
                background-color: #008C43;   /* verde bandeira paraná */
                padding: 14px 24px;  /* maior que o padding normal (12px 20px) dando o aspecto de crescimento */
                border: 2px solid rgba(255, 165, 0, 150);
            }}
            
            QPushButton:pressed {{
                background-color: #2649A5; /* azul bandeira paraná */
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
                background-color: #008C43;   /* verde bandeira paraná */
            }}
            
            QPushButton:pressed {{
                background-color: #2649A5; /* azul bandeira paraná */
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

        self.button_style_5 = f"""
            QPushButton {{
                background-color: transparent;
                border: 2px solid transparent;
                border-radius: 5px;
                min-width: 75px;
                min-height: 107px;
                margin: 0px;
                padding: 0px;
            }}

            QPushButton:hover {{
                background-color: rgba(38, 73, 165, 200);
                border: 2px solid #2649A5;
            }}

            QPushButton:pressed {{
                background-color: rgba(38, 73, 165, 200);
            }}
        """

        self.button_style_7 = f"""
            QPushButton{{

                background:qlineargradient(
                    x1:0,y1:0,
                    x2:0,y2:1,
                    stop:0 #802917,
                    stop:1 #571D10);

                border:1px solid #FF542E;
                color:white;
                font-weight:700;
                border-radius:6px;
                padding:5px 12px;
                {self.FONTES.fonte_family_geral};
            }}

            QPushButton:hover{{
                background-color:#852915;
            }}

            QPushButton:pressed{{
                background-color:#541C0D;
            }}
            
        """

        self.button_style_8 = f"""
            QPushButton{{

                background:qlineargradient(
                    x1:0,y1:0,
                    x2:0,y2:1,
                    stop:0 #177f62,
                    stop:1 #0f5c47);

                border:1px solid #2cffae;
                color:white;
                font-weight:700;
                border-radius:6px;
                padding:5px 12px;
                {self.FONTES.fonte_family_geral};
            }}

            QPushButton:hover{{
                background-color:#14855f;
            }}

            QPushButton:pressed{{
                background-color:#0b4d38;
            }}
            
        """

        self.estilo_toggle_switch = f"""
            QCheckBox {{
                background-color: transparent;
                border: none;
                {self.FONTES.fonte_family_geral};
                {self.FONTES.fonte_texto_toggle};
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

        self.qtextedit_estilo = f"""
            QTextEdit{{
                background-color: #000000;     /* fundo que destoa */
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 8px;            /* bordas arredondadas */
                padding: 8px 12px;
                {self.FONTES.fonte_texto_buttons};
                min-height: 24px;
            }}
            QTextEdit:focus {{
                border: 1px solid #ffaa00;     /* destaque laranja quando focado */
                background-color: #080808;     /* fundo mais escuro quando focado */
            }}
        """
        self.status_vaga_green = "color: green; font-weight: bold;"
        self.status_vaga_red = "color: red; font-weight: bold;"
        self.status_vaga_orange = "color: orange; font-weight: bold;"
        self.status_vaga_white_default = "color: white;"

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

        self.estilo_search_box = """
            background-color: rgba(0, 0, 0, 0.60);   /* fundo leve */
            border: 1px solid rgba(255, 165, 0, 80); 
            border-radius: 8px;
            padding: 6px 8px;
            color: white;
            font-size: 16px;
        """

        self.estilo_IP_banner = f"""
            QWidget {{
                background-color: transparent;
                border: none;
            }}
            QLineEdit:focus {{
                border: none;
                background-color: #080808;     /* fundo mais escuro quando focado */
            }}
            QPushButton {{
                color: #ffffff;
                background-color: #000000;
                border: 1px solid rgba(255, 165, 0, 80); /* borda laranja suave */
                text-align: center;
                {self.FONTES.fonte_texto_buttons};
                border-radius: 6px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(255, 165, 0, 80);   /* laranja suave */
            }}
            
            QPushButton:pressed {{
                background-color: rgba(0, 255, 155, 80);
                color: white;
            }}
        """

        self.text_admin = """
            background-color: transparent;
            font-weight: bold;
        """

        self.text_admin_OFF = """
            background-color: transparent;
            font-weight: bold;
            color: red;
        """

        self.text_admin_ON = """
            background-color: transparent;
            font-weight: bold;
            color: green;
        """



class Paths:
    def __init__(self):
        self.background_app = self.resource_path("imagens/background-3.png") # [v1.0.0.03]: imagem de background geral da aplicação
        self.logo_marca_dagua_parana = self.resource_path("imagens/SEIA3.png") # [v1.0.0.03]: imagem de marca d'agua do governo do estado do paraná que fica visivel na seção onde mostra os numeros das vagas e as legendas
        self.edificio_hauer = self.resource_path("imagens/edificacoes.png") # [v1.0.0.03]: imagem do edificio hauer onde a SEIA está situada
        self.togle_switch_off = self.resource_path("imagens/off2.png") # [v1.0.0.03]: imagem do switch off
        self.togle_switch_on = self.resource_path("imagens/on2.png") # [v1.0.0.03]: imagem do switch on

        self.img_logo_sidebar = self.resource_path("imagens/nas_logo_periodo_eleitoral.png") # [v1.0.0.03]: imagem da logo do NAS disposto na parte superior da sidebar

        self.img_carro_hatch = self.resource_path("imagens/hatch.png") # [v1.0.0.03]: imagem que representa o carro hatch da SEIA
        self.img_carro_sedan = self.resource_path("imagens/sedan.png") # [v1.0.0.03]: imagem que representa o carro sedan da SEIA
        self.img_carro_pickup = self.resource_path("imagens/pickup.png") # [v1.0.0.03]: imagem que representa o carro pickup da SEIA
        self.img_carro_pmpr = self.resource_path("imagens/pmpr-car.png") # [v1.0.0.03]: imagem que representa o carro da PMPR da SESP
        self.img_carro_deficiente = self.resource_path("imagens/deficiente.png") # [v1.0.0.03]: imagem que representa o carro de deficiente 

        self.img_placa = self.resource_path("imagens/placa.png") # [v1.0.0.03]: placa de instrução
        self.img_setas = [
            self.resource_path("imagens/1-arrow.png"),
            self.resource_path("imagens/2-arrows.png"),
            self.resource_path("imagens/3-arrows.png")
        ]

        self.img_banner_ip = self.resource_path("imagens/BANNER_LEITURA_IP_CAM_IP.png")

        self.icon_btn_entrada = self.resource_path("imagens/entrada.png") # [v1.0.0.03]: imagem do button de registrar entrada
        self.icon_btn_saida = self.resource_path("imagens/saida.png") # [v1.0.0.03]: imagem do button de registrar saida
        self.icon_btn_cadastrar_servidor = self.resource_path("imagens/cadastrar_servidor.png") # [v1.0.0.03]: imagem do button de cadastro de servidor
        self.icon_btn_cadastrar_veiculo = self.resource_path("imagens/cadastrar_veiculo.png") # [v1.0.0.03]: imagem do button de cadastro de veiculo
        self.icon_btn_remover_servidor = self.resource_path("imagens/remover_servidor.png") # [v1.0.0.03]: imagem do button de remover servidor
        self.icon_btn_remover_veiculo = self.resource_path("imagens/remover_veiculo.png") # [v1.0.0.03]: imagem do button de remover veiculo
        self.icon_btn_relatorio = self.resource_path("imagens/relatorio_vaga.png") # [v1.0.0.03]: imagem do button de relatorio por vaga
        self.icon_btn_relatorio_completo = self.resource_path("imagens/relatorio_completo.png") # [v1.0.0.03]: imagem do button relatorio completo

        #self.relatorio_pdf = self.resource_path("relatorio.pdf") # [v1.0.0.03]: caminho do arquivo de relatorio.pdf que é gerado quando o usuário clica no botão de gerar relatório
        #self.conteudo_pdf = self.resource_path("conteudo.pdf") # [v1.0.0.03]: caminho do arquivo de conteudo.pdf que é gerado quando o usuário clica no botão de gerar relatório
        #self.capa_pdf = self.resource_path("capa.pdf") # [v1.0.0.03]: caminho do arquivo de capa.pdf que é gerado quando o usuário clica no botão de gerar relatório

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
        #self.main_window = main_window 

        #    ___________________________________________________________________________
        #   |                                                                           |        
        #   |           VARIAVEIS AUXILIARES PARA OBTER CONTEXTO DOS PROXYS             |                      
        #   |___________________________________________________________________________|

        self.proxy_form_ref = None

    '''def getMainWindow(self):
        return self.main_window # [v1.0.0.03]: retorna a referencia pra janela principal da aplicação'''
    