import http
import os
import socketserver
import sys
from http.server import CGIHTTPRequestHandler
from urllib.parse import urlparse


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


def main():
    if len(sys.argv) >= 2:
        input_port = int(sys.argv[1])
    else:
        print('You have to specify a port name as a first argument.')
        return

    if len(sys.argv) >= 3:
        input_folder = sys.argv[2]
    else:
        print('You have to specify a folder name as a second argument.')
        return

    class Handler(CGIHTTPRequestHandler):
        def do_GET(self):
            self.do_task()

        def do_POST(self):
            self.do_task()

        def do_HEAD(self):
            self.do_task()

        def do_task(self):
            param_path = urlparse(self.path).path[1:]
            input_folder_fix = os.path.relpath(os.path.abspath(input_folder), os.getcwd())
            file_path = os.path.join(input_folder_fix, param_path)

            if os.path.isfile(file_path):
                if file_path.endswith('.cgi'):
                    input_folder_without_slash = input_folder_fix[:-1] if input_folder_fix.endswith('/') else input_folder_fix
                    self.cgi_info = input_folder_without_slash, param_path
                    self.run_cgi()
                else:
                    self.send_response(200)
                    self.send_header('Content-Length', os.path.getsize(file_path))
                    self.end_headers()

                    file = open(file_path, 'rb')
                    data = file.read(100)
                    while data:
                        self.wfile.write(data)
                        data = file.read(100)

            else:
                self.send_error(404, explain='File not found.')

    server = Server(('', input_port), Handler)
    server.serve_forever()


main()
