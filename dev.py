from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
from pathlib import Path

from build import reload_template, render_markdown


def get_mtime() -> float:
    return Path('template.html').stat().st_mtime
    

class BareboneHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        
        if get_mtime() != self.server.last_mtime:
            reload_template()
            print('[dev] reloaded template')
            self.server.last_mtime = get_mtime()
      
        path = self.path.strip('/')
        fileopts = [
            Path('site') / f'{path}.md',
            Path('site') / path / 'index.html.md',
            Path('site') / path,
            Path('site') / path / 'index.html',
        ]
        
        file_to_send = None
        for f in fileopts:
            if f.exists():
                file_to_send = f
                break
                
        if file_to_send:
            content_type, _ = mimetypes.guess_type(file_to_send)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            with open(file_to_send, 'rb') as tf:
                content = tf.read()
                
                if str(file_to_send).endswith('.md') and not self.path.endswith('.md'):
                    html_content = render_markdown(content.decode('utf-8'))
                    self.send_response(200)
                    self.send_header("Content-Type", 'text/html')
                    self.send_header("Content-Length", str(len(html_content)))
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))
                else: 
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
        else:
            self.serve_error(404, "Not Found")

    
    def serve_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))
        
        
def run_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, BareboneHTTPHandler)
    httpd.last_mtime = get_mtime()
    print(f"Server running on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()