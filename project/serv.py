# -*- coding: utf-8 -*-
import socket
import traceback

class HTTPError(Exception):
    pass


def parse_http(data):

    lines = data.split('\r\n')
    query = lines[0].split(' ', 2)

    headers = {}
    for pos, line in enumerate(lines[1:]):
        if not line.strip():
            break
        key, value = line.split(': ', 1)
        headers[key.upper()] = value

    body = '\r\n'.join(lines[pos+2:])
    return query, headers, body.lstrip('\r\n')


def encode_http(query, body='', **headers):
    request = " ".join(query)

    headers = "\r\n".join("%s: %s" %
        ("-".join(part.title() for part in key.split('_')), value)
        for key, value in sorted(headers.iteritems()))
    
    return "\r\n".join((request, headers, '', body) if body else (request, headers, '', ''))

class Request(object):
    def __init__(self, method, url, body, conn, **headers):
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
        self.conn = conn
        self.headers_sent = False
    
    def start_response(self, code = '200', status = 'OK', **headers):
        '''begin http reply, send status and headers'''
        self.conn.send(encode_http(("HTTP/1.0", code, status), data='', **headers))
        self.headers_sent = True
        return True

    def reply(self, data, code = '200', status = 'OK',  **headers):
        '''begin response, send data and close connection'''
        self.start_response(code, status, **headers)
        self.conn.send(data)
        self.conn.close()

class HTTPServer(object):
    def __init__(self, host="127.0.0.1", port=8000, **options):
        self.host = host
        self.port = port
        self.handlers = []
        self.options = options

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(50)
        
        while True:
            conn, addr = sock.accept()
            self.on_connect(conn, addr)

    def on_connect(self, conn, addr):
        (method, url, proto), headers, body = parse_http(conn.recv(1024))
        self.on_request(Request (method, url, body, conn, **headers))

    def on_request(self, request):
        try:
            for pattern, handler in self.handlers:
                if pattern(request): 
                    result = handler(request)
                    # нужно проверить результат, возвращаемый данной функцией:
                    # 1. ничего 
                    if result == None:
                        return

                    if not request.headers_sent:
                        request.start_response(content_type = 'text/plain')

                    # 2. строка (т.е хендлер не отправил ее в виде ответа)
                    if isinstance(result, unicode):
                       result = result.encode('utf-8')
                    
                    if isinstance(result, str):
                       request.conn.send(result)
                       return  

                    # 3. объект-файл
                    if isinstance(result, file):
                        def read_file(open_file):                           
    	                    while True:
    	                        data = open_file.read(1048576)
    	                        if not data:
    	                            break
                                yield data
                        result = read_file(result)

                    # 4. итерабельный ответ (генератор, последовательность строк)

                    if getattr(result, '__iter__', None):

                        for data in result:
                            request.conn.send(data)
                        return  

                    raise HTTPError(500)
            raise HTTPError(404)


        except HTTPError as err:

            code = err.args[0]
            status = {
                404: 'Not Found',
                403: 'Forbidden',
                500: 'Internal Server Error'}[code]
            
            request.reply('<h1>%s %s</h1>' % (code, status), str(code), status, content_type='text/html')

        except Exception:
	    if self.options.get("debug", False):
		raise
            request.reply(traceback.format_exc(), '500', 'Internal Server Error')
        

    def register(self, pattern, handler):
        self.handlers.append((pattern, handler))

