import os
import sys
import json
import base64
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from datetime import datetime


SAVE_IMAGES = True
DIR = "capturas"
NAME_IMAGE = "captura.jpg"

if SAVE_IMAGES and not os.path.exists(DIR): # cria o diretorio das imagens
    os.makedirs(DIR)

class AI520FaceServer:
    """
    Servidor mínimo para o terminal AI520F-EM.

    Recebe eventos de reconhecimento facial (/note/insertNoteFace),
    confirma com o ACK correto ({"success":0} — descoberto por
    engenharia reversa do protocolo) e repassa ID + imagem pra
    quem estiver escutando via callback.

    Uso:
        def meu_callback(employee_id, employee_name, passed, confidence, note_time, image_bytes):
            ...  # sua aplicação (SEIA) usa os dados aqui

        server = AI520FaceServer(host="10.0.0.111", port=8001, on_recognition=meu_callback)
        server.start()
    """
    

    ACK_BODY = b'{"success":0}'
    MAX_SEEN = 5000


    def __init__(self, host: str, port: int, recursos, on_recognition=None):
        self.host = host
        self.port = port
        self.recursos = recursos
        self.on_recognition = on_recognition
        self._seen = set()
        self._lock = threading.Lock()
        self._server = None

    @staticmethod
    def _event_key(data: dict) -> str:
        return f"{data.get('employeeNumberId', '-')}|{data.get('noteTime', '-')}|{data.get('notePity', '-')}"


    def decode_and_save_image(self, data: dict):
        img_b64 = data.get("noteImg") # pega a imagem em base64 (rosto detectado)
        if SAVE_IMAGES and data.get("noteImg"):
            try:
                img_b64 = data["noteImg"]
                if img_b64.startswith("data:image"):
                    img_b64 = img_b64.split(",")[1]
                img_data = base64.b64decode(img_b64)
                filename = f"{DIR}/{NAME_IMAGE}"
                with open(filename, "wb") as f:
                    f.write(img_data) # salva a imagem no disco
                print(f"[{self.recursos.CORES.AMARELO}AI520FaceServer.py{self.recursos.CORES.RESET}]:   → Foto salva: {filename}")
            except Exception as e:
                print(f"[{self.recursos.CORES.AMARELO}AI520FaceServer.py{self.recursos.CORES.RESET}]:   → Erro ao salvar foto: {e}")

    def _handle_event(self, data: dict):
        key = self._event_key(data)
        with self._lock:
            if key in self._seen:
                return  # já processado (double-send do próprio aparelho)
            self._seen.add(key)
            if len(self._seen) > self.MAX_SEEN:
                self._seen.pop()

        employee_id = data.get("employeeNumberId", "-")
        employee_name = data.get("employeeName", "Desconhecido")
        passed = data.get("notePass") == 1
        confidence = data.get("notePity", 0)
        note_time = data.get("noteTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.decode_and_save_image(data) # pega a imagem e a salva no diretorio especificado


        status = "PASSOU" if passed else "NEGADO"
        print(f"[{self.recursos.CORES.AMARELO}AI520FaceServer.py{self.recursos.CORES.RESET}]: [{note_time}] {status} | {employee_name} (ID: {employee_id}) | Confiança: {confidence:.2f}")

        if self.on_recognition:
            self.on_recognition(
                employee_id=employee_id,
                employee_name=employee_name,
                passed=passed,
                confidence=confidence,
                note_time=note_time
            )

    def _build_handler(self):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'  # keep-alive: evita rajadas de reenvio do terminal

            def do_POST(self):
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)

                if self.path == "/note/insertNoteFace":
                    try:
                        data = json.loads(body.decode('utf-8'))
                        outer._handle_event(data)
                    except Exception:
                        pass
                # Outras rotas (polling/config do próprio protocolo) só
                # recebem o ACK genérico e são ignoradas — são leves e
                # não fazem parte do que você precisa capturar.

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(outer.ACK_BODY)))
                self.send_header('Connection', 'keep-alive')
                self.end_headers()
                self.wfile.write(outer.ACK_BODY)

            def do_GET(self):
                self.send_response(404)
                self.end_headers()

            def log_message(self, format, *args):
                return

        return Handler

    def start(self):
        class QuietServer(ThreadingHTTPServer):
            daemon_threads = True

            def handle_error(self_inner, request, client_address):
                exc_type = sys.exc_info()[0]
                if exc_type not in (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    super().handle_error(request, client_address)

        self._server = QuietServer((self.host, self.port), self._build_handler())
        print(f"[{self.recursos.CORES.AMARELO}AI520FaceServer.py{self.recursos.CORES.RESET}]: Servidor rodando em http://{self.host}:{self.port} — aguardando eventos...\n")
        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        if self._server:
            print(f"[{self.recursos.CORES.AMARELO}AI520FaceServer.py{self.recursos.CORES.RESET}]: Encerrando servidor...")
            self._server.shutdown()
            self._server.server_close()

'''
if __name__ == '__main__':
    def minha_aplicacao(employee_id, employee_name, passed, confidence, note_time, image_bytes):
        # Ponto de integração com o SEIA: aqui você recebe ID e imagem
        # (bytes crus do JPEG, ou None se o aparelho não mandou foto)
        # e faz o que precisar — salvar, mandar pro backend, etc.
        pass

    server = AI520FaceServer(host="10.0.0.111", port=8001, on_recognition=minha_aplicacao)
    server.start()
'''