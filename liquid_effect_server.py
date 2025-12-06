
import http.server
import socketserver
import json
import subprocess
import sys
import os

PORT = 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/liquid_effect.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/call-agent':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                agent_path = os.path.join(os.path.dirname(__file__), 'agent.py')
                if not os.path.exists(agent_path):
                     raise FileNotFoundError("agent.py not found")

                result = subprocess.run(
                    [sys.executable, agent_path, 'console'], 
                    input=post_data, 
                    capture_output=True, 
                    text=True,
                    check=True,
                    timeout=30 
                )
                response_data = {"reply": result.stdout if result.stdout else "Agent executed without output."}
            except FileNotFoundError:
                response_data = {"reply": "Error: agent.py not found."}
            except subprocess.CalledProcessError as e:
                response_data = {"reply": f"Error calling agent: {e.stderr}"}
            except subprocess.TimeoutExpired:
                response_data = {"reply": "Error: Agent script timed out."}
            except Exception as e:
                response_data = {"reply": f"An unexpected error occurred: {str(e)}"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

def run():
    with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
