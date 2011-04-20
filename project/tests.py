from serv import HTTPServer,  parse_http, encode_http, Request
from handlers import serve_static
from nose.tools import eq_, raises
from coverage import coverage
from cStringIO import StringIO
import os, time

class MockConnection:

    def __init__(self, data):
        self.sent_data = ''
        self.recv_data = data

    def recv(self, size):
        return self.recv_data

    def send(self, data):
        self.sent_data += data

    def sent_lines(self):
        self.sent_data.seek(0)
        return self.sent_data.readlines()

    def close(self):
        pass

class MockClient:
    def __init__(self, server):
        self.server = server
        

    def __call__ (self, method, url, body=None, **headers):
        conn = MockConnection(encode_http((method, url, "HTTP/1.0"), body, **headers))
        self.server.on_connect(conn, None)

        return parse_http(conn.sent_data)
 


class TestHTTPServer:
   
    def setup(self):
        self.server = HTTPServer(11112, debug=True)
        self.client = MockClient(self.server)

    def test_on_connect(self):
      
       
        
        handler = lambda request: request.reply('<H1>"Hello world!!!!"</H1>',content_type = 'text/html')
        pattern = lambda request: request.url =="/html/"
        self.server.register(pattern, handler)
	

        reply, headers, body = self.client('GET', '/html/')
        eq_(reply, ['HTTP/1.0', '200', 'OK'])
        eq_(headers['CONTENT-TYPE'], 'text/html')

    def test_change_handlers(self):
      
        
        def pattern(request):
             if request.url == '/html/':
                request.test = 'hell world'
                return True

        self.server.register(pattern, lambda request: request.reply(request.test, content_type='text/html'))



        reply, headers, body = self.client('GET', '/html/')

       
        eq_(body, 'hell world')


    def test_multihandlers(self):

 
        self.server.register(lambda request: request.method == "POST", lambda request: request.reply('post')) 
        self.server.register(lambda request: request.url == '/test/', lambda request: request.reply('other'))  

        reply, headers, body = self.client ('POST', '/test/')
        eq_('post', body)

        reply, headers, body = self.client('GET', '/test/')
        eq_('other', body)


    def test_multiline_body(self):

 
        self.server.register(
            lambda request: request.url == '/multiline',
            lambda request: request.reply('<strong>multi-\r\nline\r\nbody</strong>', content_type='text/html')
        )

        reply, headers, body = self.client('GET', '/multiline')
        eq_('<strong>multi-\r\nline\r\nbody</strong>', body)

    def test_handlers(self):

        self.server.register(lambda r: r.url == True, lambda r: None)
	request, headers, body = self.client('GET', '/')
	eq_(request[1], '404')
        eq_(body, '<h1>404 Not Found</h1>')

        self.server.register(lambda r: r.url == '/str', lambda r: 'This is a string reply')
	request, headers, body = self.client('GET', '/str')
	eq_(request[1], '200')
	eq_(body, 'This is a string reply')

	self.server.register(lambda r: r.url == 'utf', lambda r: 'This is a utf-8 reply'.decode('utf-8'))
	request, headers, body = self.client('GET', 'utf')
	eq_(request[1], '200')
	eq_(body, 'This is a utf-8 reply')

	self.server.register(lambda r: r.url == '/iter', lambda r: ['asd', 'fgh'])
	request, headers, body = self.client('GET', '/iter')
	eq_(request[1], '200')
	eq_(body, 'asdfgh')

	self.server.register(lambda r: r.url == '/file', lambda r: open('handlers.py').read(9))
	request, headers, body = self.client('GET', '/file')
	eq_(request[1], '200')
	eq_(body, 'import os')

        self.server.options["debug"] = False
	self.server.register(lambda r: r.url == '/crash/me/', lambda r: no_you)
        request, headers, body = self.client('GET', '/crash/me/')
        eq_(request[1], '500')  
        eq_(request[2], 'Internal Server Error')
    

class TestHandlers(object):
    def setup(self):

        self.server = HTTPServer(debug=True)
        self.client = MockClient(self.server)

    def test_static(self):
         
        self.server.register(*serve_static(address='/', root="."))
        reply, headers, body = self.client('GET', '/handlers.py')
        data = open('handlers.py').read()
        eq_(body, data)

    def test_parts_handlers(self):
        self.server.register(lambda r: True, lambda r: ["123", "456", "789"])
        request, header, body = self.client('GET', '/')
        eq_(body, "123456789")

    def test_autoindex(self): 
         self.server.register(*serve_static(address='/', root=".", autoindex=True))  
         reply, headers, body = self.client('GET', '/.')        
         eq_(body,''.join(["%s\t%s\t%s\n"%(file, str(os.stat(file).st_size), time.strftime('%a, %d %b %Y %H:%I:%S GMT', time.gmtime(os.stat(file).st_mtime))) for file in os.listdir('.')]))


class TestHTTPRequest:
    
    def test_constructor(self):pass

    

if __name__ == "__main__":
    import nose
    nose.run()

