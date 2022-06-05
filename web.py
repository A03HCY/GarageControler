import socket

class Req:
    def __init__(self, head, addr, url, conn):
        self.head = head
        self.addr = addr
        self.url = url
        self.conn = conn
    
    def response(self, data, cont_type='text'):
        try:
            self.conn.send('HTTP/1.1 200 OK\n')
            self.conn.send('Content-Type: text/html\n')
            self.conn.send('Access-Control-Allow-Origin: *\n')
            self.conn.send('Connection: close\n\n')
            self.conn.sendall(data)
        except:pass

class Web:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('', 80))
        self.regs = {}
    
    def active(self):
        self.server.listen(50)
        while True:
            self.handle(self.request())
            self.conn.close()
    
    def request(self):
        self.conn, addr = self.server.accept()
        self.conn.setblocking(False)
        try:
            head = self.conn.recv(1024)
            head = str(head)
            url = head.split('HTTP')[0].split(' ')[1]
            req = Req(head, str(addr), url, self.conn)
            return req, True
        except:
            return None, False
    
    def handle(self, req):
        if req[1] == False:return
        req = req[0]
        
        print('requested at', req.url)
        if req.url in self.regs:
            self.regs[req.url](req)
        else:
            req.response('Not Found')
    
    def route(self, url, func):
        self.regs[url] = func
        
    def apply(self, regs):
        self.regs.update(regs)