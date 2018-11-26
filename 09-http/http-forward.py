import json
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from urllib import request


def prepare_output(status_code, headers=None, content=None):
    output = dict()
    output['code'] = status_code

    if headers:
        output['headers'] = dict()
        for hkey, hvalue in headers:
            output['headers'][hkey] = hvalue

    if content:
        try:
            output['json'] = json.loads(content)
        except ValueError:
            output['content'] = content

    return output


def main():
    if len(sys.argv) >= 2:
        input_port = int(sys.argv[1])
    else:
        print('You have to specify a port name as a first argument.')
        return

    if len(sys.argv) >= 3:
        input_target_url = sys.argv[2]
    else:
        print('You have to specify target URL as a second argument.')
        return

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            get_params = parse.urlparse(self.path).query

            get_url = input_target_url
            if get_params:
                get_url = '%s?%s' % (get_url, get_params)

            new_headers = dict(self.headers)
            if 'Host' in new_headers:
                del new_headers['Host']

            new_request = request.Request(url=get_url,
                                          data=None,
                                          headers=new_headers,
                                          method='GET')
            try:
                with request.urlopen(new_request, timeout=1) as response:
                    res_content = response.read().decode('UTF-8')
                    output = prepare_output(200, response.getheaders(), res_content)

                    self.send_result(200, output)
            except socket.timeout:
                return self.send_result(200, prepare_output('timeout', None, None))

        def do_POST(self):
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)

            try:
                json_body = json.loads(post_body)
                request_type = 'GET'

                if 'type' in json_body:
                    request_type = json_body['type']

                if 'url' not in json_body or (request_type == 'POST' and 'content' not in json_body):
                    self.send_result(200, prepare_output('invalid_json'))

                request_url = json_body['url']
                request_headers = json_body['headers'] if 'headers' in json_body else dict()
                request_content = json_body['content'] if request_type == 'POST' else None
                request_timeout = json_body['timeout'] if 'timeout' in json_body else 1

                request_headers = {k.lower(): v for k, v in request_headers.items()}
                if 'content-type' not in request_headers:
                    request_headers['content-type'] = 'text/plain'

                new_request = request.Request(url=request_url,
                                              data=bytes(request_content, 'UTF-8') if request_content else None,
                                              headers=request_headers,
                                              method=request_type)
                try:
                    with request.urlopen(new_request, timeout=request_timeout) as response:
                        res_content = response.read().decode('UTF-8')
                        output = prepare_output(200, response.getheaders(), res_content)

                        self.send_result(200, output)
                except socket.timeout:
                    return self.send_result(200, prepare_output('timeout', None, None))
            except ValueError:
                self.send_result(200, prepare_output('invalid_json'))

        def send_result(self, status_code, content):
            data = json.dumps(content, indent=4)

            self.send_response(status_code)

            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()

            self.wfile.write(bytes(data, 'UTF-8'))

    server = HTTPServer(('', input_port), Handler)
    server.serve_forever()


main()