

import re, subprocess, json
import requests

#  ______________________________________________________________________________
# |         Classe responsável por tratar os dados enviados ao servidor          |
# |          via aplicação InspireFace rodando no dispositivo Android            |
# |______________________________________________________________________________|

class InspireFace:
    def __init__(self):
        super().__init__()

        #obtendo o ip do servidor do hotspot/roteador do smartphone
        self.ip = self.hotspot_ip()
        self.url = f"http://{self.ip}:8080"
        print(self.url)
        self.conteudo_page = self.ler_mensagem()
        self.processar_mensagem(self.conteudo_page)
        



    def hotspot_ip(self):
        out = subprocess.run(["ipconfig", "/all"], capture_output=True,
                            text=True, encoding="cp850", errors="ignore").stdout
        for bloco in re.split(r"\r?\n(?=\S)", out):          # um bloco por adaptador
            if re.search(r"Wi-?Fi|Wireless|Sem Fio", bloco.splitlines()[0], re.I):
                m = re.search(r"(?:Servidor DHCP|DHCP Server)[ .]*:\s*([\d.]+)", bloco)
                if m:
                    return m.group(1)
        return None


    def getIP(self):
        return self.ip


    def processar_mensagem(self, mensagem):
        try:
            dados = json.loads(mensagem)
            id = dados.get("id")
            image = dados.get("image")
            return id, image
        except (json.JSONDecodeError, AttributeError):
            print("Mensagem JSON inválida:", mensagem)
            return None, None


    def ler_mensagem(self):
        try:
            resposta = requests.get(self.url, timeout=5)
            resposta.raise_for_status()
            mensagem = resposta.text
            print("String recebida:", mensagem)
            return mensagem
        except requests.RequestException as erro:
            print(f"Erro ao consultar o servidor: {erro}")
            return None



