import json
import socket
import threading
import time

class TCPServer(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_name='server2'
        self.server_host='127.0.0.1'
        self.server_port=5004

    def bind_listen(self, port):
        self.sock.bind((self.server_host, port))
        self.sock.listen(15)

    def accept_receive_close(self):
        '''获取Client端信息'''
        (client_socket, address) = self.sock.accept()
        msg = client_socket.recv(1024)
        data = self.on_msg(msg)
        client_socket.sendall(data)  # 回传
        client_socket.close()
    # def handel_client(self,client_socket):
    #     msg = client_socket.recv(1024)
    #     data = self.on_msg(msg)
    #     client_socket.sendall(data)  # 回传
    #     client_socket.close()
    #
    # def accept_receive_close(self):
    #     '''获取Client端信息'''
    #     (client_socket, address) = self.sock.accept()
    #     client_handeler = threading.Thread(target=self.handel_client, args=(client_socket,))
    #     client_handeler.start()


class JSONRPC(object):
    def __init__(self):
        self.data = None

    def from_data(self, data):
        '''解析数据'''
        self.data = json.loads(data.decode('utf-8'))

    def call_method(self, data):
        '''解析数据，调用对应的方法变将该方法执行结果返回'''
        self.from_data(data)
        method_name = self.data['method_name']
        method_args = self.data['method_args']
        res = self.funs[method_name](*method_args)
        data = {"res": res}
        return json.dumps(data).encode('utf-8')


class RPCStub(object):
    def __init__(self):
        self.funs = {}
        self.fun_names=[]

    def register_function(self, function, name=None):
        '''Server端方法注册，Client端只可调用被注册的方法'''
        if name is None:
            name = function.__name__
        self.funs[name] = function
        self.fun_names.append(name)

        register_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        register_socket.connect(('127.0.0.1',5000)) # 向注册中心注册的连接（C）
        data = {'server_name': self.server_name, 'server_host': self.server_host,'server_port': self.server_port, 'data': self.fun_names}
        register_socket.send(json.dumps(data).encode('utf-8'))
        register_socket.close()

class RPCServer(TCPServer, JSONRPC, RPCStub):
    def __init__(self):
        TCPServer.__init__(self)
        JSONRPC.__init__(self)
        RPCStub.__init__(self)

    def loop(self, port):
        # 循环监听 5004 端口
        self.bind_listen(port)
        print('Server listen '+ str(port))
        while True:
            self.accept_receive_close()

    def on_msg(self, data):
        return self.call_method(data)

    def beat(self, port):
        while True:
            register_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 向注册中心发送心跳（C）
            try:
                register_socket.connect((self.server_host, port))
                register_socket.send(self.server_name.encode('utf-8'))
                print(f'{self.server_name}发送一次心跳')
            except Exception as e:
                print("Error occurred while trying to connect:", e)
            finally:
                register_socket.close()
            time.sleep(60)  # 60秒为间隔，可以根据需要调整
