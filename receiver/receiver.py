import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-report.json")


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, text):
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/report":
            return self._reply(404, "Not found")
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return self._reply(400, "Invalid JSON")
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Report received -> {OUT_FILE}  (status: {data.get('summary', {}).get('status')})")
        self._reply(200, "Saved")

    def do_GET(self):
        self._reply(200, "Receiver is running")


if __name__ == "__main__":
    print("Receiver listening on http://127.0.0.1:9000/report  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", 9000), Handler).serve_forever()