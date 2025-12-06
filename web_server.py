
import http.server
import socketserver
import json
import subprocess
import sys

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/call-agent':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Assuming agent.py can be called as a script
                result = subprocess.run(
                    [sys.executable, 'agent.py', 'console'], 
                    input=post_data, 
                    capture_output=True, 
                    text=True,
                    check=True
                )
                response = {"reply": result.stdout}
            except subprocess.CalledProcessError as e:
                response = {"reply": f"Error calling agent: {e.stderr}"}
            except FileNotFoundError:
                response = {"reply": "Error: agent.py not found."}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", 8000), Handler) as httpd:
    print("serving at port", 8000)
    httpd.serve_forever()
