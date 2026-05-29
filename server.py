import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import re   # ← deze moet erbij

# ANSI codes verwijderen
def remove_ansi(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)



PORT = 8000

def ask_ollama(prompt):
    ollama_path = r"C:\Users\sandj\AppData\Local\Programs\Ollama\ollama.exe"

    result = subprocess.run(
        [ollama_path, "run", "llama3.1"],
        input=prompt,
        text=True,
        capture_output=True
    )

    clean_output = remove_ansi(result.stdout)
    return clean_output.strip()


class ChatHandler(BaseHTTPRequestHandler):

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self._set_cors_headers()
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"StudyBuddy backend is running. Use POST /ask to chat.")

    def do_POST(self):
        if self.path == "/ask":
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            user_question = data.get("question", "")

            answer = ask_ollama(f"Je bent StudyBuddy. Beantwoord: {user_question}")

            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {"answer": answer}
            self.wfile.write(json.dumps(response).encode())

server = HTTPServer(("localhost", PORT), ChatHandler)
print(f"Server running on http://localhost:{PORT}")
server.serve_forever()
