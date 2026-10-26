
from PySide6.QtCore import QObject, Signal
import os, re, subprocess, json, requests, threading

#  ______________________________________________________________________________
# |         Classe responsável por tratar os dados enviados ao servidor          |
# |          via aplicação InspireFace rodando no dispositivo Android            |
# |______________________________________________________________________________|


DIR = "capturas"
NAME_IMAGE = "captura.jpg"
PATH_IMAGE = DIR+"/"+NAME_IMAGE

class InspireFace(QObject):

    rosto_detectado = Signal(object, object)   # (id, image)

    def __init__(self):
        super().__init__()

        if not os.path.exists(DIR): # cria o diretorio das imagens
            os.makedirs(DIR)
        

        #obtendo o ip do servidor do hotspot/roteador do smartphone
        self.ip = self.hotspot_ip()
        self.url = f"http://{self.ip}:8080"
        print(self.url)
        #self.conteudo_page = self.ler_mensagem()
        #self.processar_mensagem(self.conteudo_page)
        



    def hotspot_ip(self):
        '''Extrai o IP do servidor DHCP do windows. É preciso estar conectado no hotspot do smartphone ou do roteador, de preferência no hotspot do smartphone.'''
        resultado = subprocess.run(
            [
                "powershell",
                "-Command",
                "Get-CimInstance Win32_NetworkAdapterConfiguration "
                "| Where-Object {$_.DHCPEnabled} "
                "| Select-Object -ExpandProperty DHCPServer"
            ],
            capture_output=True,
            text=True
        )
        return resultado.stdout.rstrip('\n') # rstrip é pra remover um '\n' inesperado que é retornado na chamada do metodo do subprocess


    def getIP(self):
        return self.ip


    def processar_mensagem(self, mensagem):
        '''Extrai as informações do rosto validado, como {id} e {image}\n
            • O servidor normalmente replica a mensagem: {"id":null};\n
            • Quando um rosto é validado, a mensagem passa a conter informações do tipo: {"id":1,"image":"/face/image"};\n'''
        try:
            if mensagem is not None:
                dados = json.loads(mensagem)
                id = dados.get("id")
                image = dados.get("image")
                # salva a imagem no diretorio criado para esse fim 
                open(PATH_IMAGE, "wb").write(requests.get(self.url+"/face/image").content)
                return id, image
        except (json.JSONDecodeError, AttributeError):
            print("Mensagem JSON inválida:", mensagem)
            return None, None


    def ler_mensagem(self):
        '''lê a mensagem replicada no servidor'''
        try:
            resposta = requests.get(self.url, timeout=5)
            resposta.raise_for_status()
            mensagem = resposta.text
            print("String recebida:", mensagem)
            return mensagem
        except requests.RequestException as erro:
            print(f"Erro ao consultar o servidor: {erro}")
            return None



    def monitorar(self, intervalo=0.3):
        '''Consulta o servidor em segundo plano e chama callback(id, image) sempre que a mensagem mudar.'''
        self._parar = threading.Event()
        def loop():
            ultima = None
            while not self._parar.is_set():
                msg = self.ler_mensagem()
                if msg is not None and msg != ultima:
                    ultima = msg
                    self.rosto_detectado.emit(*self.processar_mensagem(msg))
                self._parar.wait(intervalo)   # dorme, mas acorda na hora se chamar parar()

        threading.Thread(target=loop, daemon=True).start()

    def parar(self):
        self._parar.set()

