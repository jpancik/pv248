import json
import socket
import ssl
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from urllib import request

from OpenSSL.SSL import TLSv1_2_METHOD, Context, Connection


def prepare_output(status_code, headers=None, content=None, certificate_is_valid=None, certificate_common_names=None):
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

    if certificate_is_valid is not None:
        output['certificate valid'] = certificate_is_valid
    if certificate_common_names:
        output['certificate for'] = certificate_common_names

    return output


def get_certificate_san(x509cert):
    san = ''
    ext_count = x509cert.get_extension_count()
    for i in range(0, ext_count):
        ext = x509cert.get_extension(i)
        if 'subjectAltName' in str(ext.get_short_name()):
            san = ext.__str__()
    san = san.split(', ')
    san = [x[4:] if x.startswith('DNS:') else x for x in san]
    return san


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

            # TU ZACINA GRCKA SORRY.
            certificate_common_names = None
            certificate_is_valid = None
            if get_url.startswith('https://'):
                client = None
                try:
                    client = socket.socket()
                    # print('Connecting...')
                    client.connect((parse.urlparse(get_url).netloc, 443))
                    client_ssl = Connection(Context(TLSv1_2_METHOD), client)
                    client_ssl.set_connect_state()
                    client_ssl.set_tlsext_host_name(parse.urlparse(get_url).netloc.encode('UTF-8'))
                    client_ssl.do_handshake()
                    # print('Server subject is', dict(client_ssl.get_peer_certificate().get_subject().get_components()))
                    certificate_common_names = get_certificate_san(client_ssl.get_peer_certificate())
                except:
                    pass
                finally:
                    if client:
                        client.close()


                try:
                    with request.urlopen(new_request, timeout=1) as response:
                        certificate_is_valid = True
                except:
                    certificate_is_valid = False
            # TU KONCI GRCKA.

            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                with request.urlopen(new_request, timeout=1, context=ctx) as response:
                    res_content = response.read().decode('UTF-8')
                    output = prepare_output(200, response.getheaders(), res_content, certificate_is_valid, certificate_common_names)

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
                    self.send_result(200, prepare_output('invalid json'))

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

                # TU ZACINA GRCKA SORRY.
                # cert_raw = ssl.get_server_certificate(('google.com', 443))
                # cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_raw)
                # print(dict(cert.get_subject().get_components()))

                certificate_common_names = None
                certificate_is_valid = None
                if request_url.startswith('https://'):
                    client = None
                    try:
                        client = socket.socket()
                        # print('Connecting...')
                        client.connect((parse.urlparse(request_url).netloc, 443))
                        client_ssl = Connection(Context(TLSv1_2_METHOD), client)
                        client_ssl.set_connect_state()
                        client_ssl.set_tlsext_host_name(parse.urlparse(request_url).netloc.encode('UTF-8'))
                        client_ssl.do_handshake()
                        # print('Server subject is', dict(client_ssl.get_peer_certificate().get_subject().get_components()))
                        certificate_common_names = get_certificate_san(client_ssl.get_peer_certificate())
                    except:
                        pass
                    finally:
                        if client:
                            client.close()

                    try:
                        with request.urlopen(new_request, timeout=request_timeout) as response:
                            certificate_is_valid = True
                    except:
                        certificate_is_valid = False
                # TU KONCI GRCKA.

                try:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE

                    with request.urlopen(new_request, timeout=request_timeout, context=ctx) as response:
                        res_content = response.read().decode('UTF-8')
                        output = prepare_output(200, response.getheaders(), res_content, certificate_is_valid, certificate_common_names)

                        self.send_result(200, output)
                except socket.timeout:
                    return self.send_result(200, prepare_output('timeout', None, None))

            except ValueError:
                # import traceback
                # traceback.print_exc()
                self.send_result(200, prepare_output('invalid json'))

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