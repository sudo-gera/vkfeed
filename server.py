import http.server

class Server(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        # self.path='/'
        super().do_GET()


def run_server(host, port):
    with http.server.HTTPServer((host, port), Server) as httpd:
        httpd.serve_forever()
