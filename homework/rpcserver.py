import json
import socket
import threading
import time

class TCPServer(object):
    def __init__(self,server_name,server_host,server_port,register_host,beat_port,register_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_name = server_name
        self.server_host = server_host
        self.server_port = server_port
        self.register_host=register_host
        self.beat_port=beat_port
        self.register_port=register_port
    def bind_listen(self, port):
        self.sock.bind((self.server_host, port))
        self.sock.listen(15)

    def accept_receive_close(self,client_socket):
        '''获取Client端信息'''
        try:# 处理读数据异常
            msg = client_socket.recv(1024)
        except socket.error as e:
            print(f"接收数据异常: {e}")
            client_socket.close()
            return None
        data = self.on_msg(msg)
        try:
            client_socket.sendall(data) # 回传
            print("数据发送成功")
        except socket.error as e:
            print(f"发送数据异常: {e}")
            client_socket.close()
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
        method = self.funs[method_name]
        num_args_needed = method.__code__.co_argcount
        if len(method_args) != num_args_needed:
            data={"error3":f"参数数量不匹配，方法 {method_name} 需要 {num_args_needed} 个参数，但你提供了 {len(method_args)} 个参数。"}
            return json.dumps(data).encode('utf-8')
        else:
            res = self.funs[method_name](*method_args)
            data = {"res": res}
            return json.dumps(data).encode('utf-8')


class RPCStub(object):
    def __init__(self):
        self.funs = {}
        self.fun_names=[]
        self.funs_effect = {}

    def register_function(self, function, effect, name=None):
        '''Server端方法注册，Client端只可调用被注册的方法'''
        if name is None:
            name = function.__name__
        self.funs[name] = function
        self.funs_effect[name] = effect
        self.fun_names.append(name)

        register_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:# 注册异常处理
            register_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            register_socket.connect((self.register_host, self.register_port))  # 向注册中心注册的连接（C）
            data = {'server_name': self.server_name, 'server_host': self.server_host, 'server_port': self.server_port,
                    'data': self.fun_names,'effect': self.funs_effect}
            register_socket.send(json.dumps(data).encode('utf-8'))
            print("注册成功")
        except socket.error as e:
            print(f"注册函数时连接注册中心异常: {e}")
        finally:
            register_socket.close()

class RPCServer(TCPServer, JSONRPC, RPCStub):
    def __init__(self,server_name,server_host,server_port,register_host,beat_port,register_port):
        TCPServer.__init__(self,server_name,server_host,server_port,register_host,beat_port,register_port)
        JSONRPC.__init__(self)
        RPCStub.__init__(self)

    def loop(self):
        # 循环监听 服务请求 端口
        self.bind_listen(self.server_port)
        print('监听服务请求的端口是 '+ str(self.server_port))
        while True:
            (client_socket, address) = self.sock.accept()
            client_handeler = threading.Thread(target=self.accept_receive_close, args=(client_socket,))
            client_handeler.start()

    def on_msg(self, data):
        return self.call_method(data)

    def beat(self):
        while True:
            register_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 向注册中心发送心跳（C）
            try: # 心跳异常处理
                register_socket.connect((self.register_host, self.beat_port))
                register_socket.send(self.server_name.encode('utf-8'))
                print(f'{self.server_name}发送一次心跳')
            except Exception as e:
                print("发送心跳时无法连接到注册中心", e)
            finally:
                register_socket.close()
            time.sleep(1)  # 1秒为间隔，可以根据需要调整
