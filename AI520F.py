import sys
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import base64
import os
from datetime import datetime

IP = '10.0.0.111'
PORT = 8001
EVENTS = []
MAX_EVENTS = 50
SAVE_IMAGES = True
state_lock = threading.Lock()  # protege EVENTS/SEEN_EVENTS entre threads

# ACK correto, descoberto a partir do vocabulário nativo do próprio
# protocolo (visto em uploadPerson e PeriodCallback, que o aparelho
# manda com {"success":-1} quando pendente). Confirmado por teste real:
# {"success":0} faz o insertNoteFace parar de repetir a cada ciclo.
ACK_BODY = b'{"success":0}'

# Dedup: o aparelho pode mandar o mesmo evento 2x quase simultaneamente
# dentro do mesmo lote de sincronização (comportamento normal, não é bug).
SEEN_EVENTS = set()
MAX_SEEN = 5000

if SAVE_IMAGES and not os.path.exists("fotos"):
    os.makedirs("fotos")


def event_key(data: dict) -> str:
    return f"{data.get('employeeNumberId','-')}|{data.get('noteTime','-')}|{data.get('notePity','-')}"


class QuietHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        exc_type = sys.exc_info()[0]
        if exc_type in (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass  # normal: o terminal derruba a conexão keep-alive de vez em quando
        else:
            super().handle_error(request, client_address)


class AI520Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'  # keep-alive: necessário pro aparelho não reenviar em rajada

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        path = self.path

        data = None
        try:
            data = json.loads(body.decode('utf-8'))
        except Exception:
            pass

        if path == "/note/insertNoteFace" and data:
            key = event_key(data)

            with state_lock:
                already_seen = key in SEEN_EVENTS
                if not already_seen:
                    SEEN_EVENTS.add(key)
                    if len(SEEN_EVENTS) > MAX_SEEN:
                        SEEN_EVENTS.pop()

            if already_seen:
                pass  # já processado (provável double-send do próprio aparelho), ignora silenciosamente
            else:
                employee = data.get("employeeName", "Desconhecido")
                emp_id = data.get("employeeNumberId", "-")
                note_time = data.get("noteTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                passed = "PASSOU" if data.get("notePass") == 1 else "NEGADO"
                pity = data.get("notePity", 0)

                print(f"\n[{note_time}] {passed} | {employee} (ID: {emp_id}) | Confiança: {pity:.2f}")

                if SAVE_IMAGES and data.get("noteImg"):
                    try:
                        img_b64 = data["noteImg"]
                        if img_b64.startswith("data:image"):
                            img_b64 = img_b64.split(",")[1]
                        img_data = base64.b64decode(img_b64)
                        filename = f"fotos/{note_time.replace(':','-').replace(' ','_')}_{employee}.jpg"
                        with open(filename, "wb") as f:
                            f.write(img_data)
                        print(f"   → Foto salva: {filename}")
                    except Exception as e:
                        print(f"   → Erro ao salvar foto: {e}")

                with state_lock:
                    EVENTS.insert(0, {
                        "time": note_time,
                        "name": employee,
                        "id": emp_id,
                        "pass": passed,
                        "pity": round(pity, 3),
                    })
                    if len(EVENTS) > MAX_EVENTS:
                        EVENTS.pop()

        # Todas as rotas (inclusive as de polling/config como selectDayPeriod,
        # updateStateDevice etc.) recebem o mesmo ACK no vocabulário nativo
        # do aparelho. Essas rotas de polling vão continuar batendo a cada
        # ~10s por design (Poll Time(s)) — isso é esperado e leve, não é o
        # flood que a gente resolveu aqui.
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(ACK_BODY)))
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        self.wfile.write(ACK_BODY)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>AI520 - Eventos</title>
                <meta http-equiv="refresh" content="3">
                <style>
                    body { font-family: Arial; background: #111; color: #eee; padding: 20px; }
                    h1 { color: #0f0; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #444; padding: 8px; text-align: left; }
                    th { background: #222; }
                    .pass { color: #0f0; }
                    .deny { color: #f55; }
                </style>
            </head>
            <body>
                <h1>AI520 - Últimos Eventos</h1>
                <p>Atualiza a cada 3 segundos</p>
                <table>
                    <tr><th>Horário</th><th>Nome</th><th>ID</th><th>Status</th><th>Confiança</th></tr>
            """
            with state_lock:
                events_snapshot = list(EVENTS)
            for e in events_snapshot:
                cls = "pass" if e["pass"] == "PASSOU" else "deny"
                html += f"""
                    <tr>
                        <td>{e['time']}</td><td>{e['name']}</td><td>{e['id']}</td>
                        <td class="{cls}">{e['pass']}</td><td>{e['pity']}</td>
                    </tr>
                """
            html += "</table></body></html>"
            body = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    server = QuietHTTPServer((IP, PORT), AI520Handler)
    print(f"Servidor AI520 (produção) rodando em http://{IP}:{PORT}")
    print(f"Abra no navegador: http://{IP}:8001")
    print("Fotos serão salvas na pasta 'fotos/' (se Save Face estiver ligado no aparelho)")
    print("ACK: {\"success\":0} | keep-alive ativo | dedup ativo | threaded")
    print("Aguardando eventos...\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        server.server_close()
