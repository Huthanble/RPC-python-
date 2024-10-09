import json
import socket
import threading
import time


class serverstub(object):
    def __init__(self,register_host,register_port,beat_port,client_port):
        self.server={} # 存一个服务器中可用的函数
        self.effect={} # 存每个函数的作用（重名函数会被覆盖，只展示某个服务器中的同名函数的作用）
        self.server_alive={} # 存一个服务器是否存活的状态
        self.server_list={} # 存一个服务器的具体地址和端口
        self.server_order=[] # 进行服务器轮询的顺序
        self.server_funs=[] # 存储所有可用的函数，用于查询
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alive_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data = None
        self.register_host = register_host
        self.register_port = register_port
        self.beat_port = beat_port
        self.client_port = client_port

    def server_listen(self):
        self.server_sock.bind((self.register_host, self.register_port))
        self.server_sock.listen(15)

    def alive_listen(self):
        self.alive_sock.bind((self.register_host, self.beat_port))
        self.alive_sock.listen(15)

    def handel_reg(self,client_socket):
        try: # 注册中心注册异常处理
            msg = client_socket.recv(1024)
            print("注册数据接受成功")
        except socket.error as e:
            print(f"注册数据接受异常: {e}")
            client_socket.close()
        data = json.loads(msg.decode('utf-8'))
        self.server[data['server_name']] = data['data']
        for key,value in data['effect'].items():
            self.effect[key]=value
        for key in data['data']:
            if not key in self.server_funs:
                self.server_funs.append(key)
        self.server_alive[data['server_name']] = 1
        self.server_list[data['server_name']] = (data['server_host'], data['server_port'])
        if not data['server_name'] in self.server_order:
            self.server_order.append(data['server_name'])
        key = data['server_name']
        print(f'{key}已加入\n')
        print(f'{key}的具体地址：host:{self.server_list[key][0]},port:{self.server_list[key][1]}')
        print(f'{key}的函数:{self.server[key]}')
        print(f'服务器顺序是{self.server_order}')
        all_funs=self.server.values()
        funs_list=list(all_funs)
        print(f'所有注册的函数(含重复)：{funs_list}')
        print(f'所有注册的函数(不含重复)：{self.server_funs}')
        client_socket.close()
    def server_loop(self):
        # 循环监听 5001 端口
        self.server_listen()
        print('Server listen '+ str(self.register_port)+'\n')
        while True:
            (client_socket, address) = self.server_sock.accept()
            reg_handeler = threading.Thread(target=self.handel_reg, args=(client_socket,))
            reg_handeler.start()

    def handel_beat(self,client_socket):
        try: # 处理读取心跳数据异常
            data = client_socket.recv(1024).decode('utf-8')
            self.server_alive[data] = 1
            client_socket.close()
        except socket.error as e:
            print(f"心跳数据异常: {e}")
    def alive_loop(self):
        # 循环监听 5001 端口
        self.alive_listen()
        print('alive listen '+ str(self.beat_port)+'\n')
        while True:
            (client_socket, address) = self.alive_sock.accept()
            beat_handeler=threading.Thread(target=self.handel_beat, args=(client_socket,))
            beat_handeler.start()

    def monitor_beat(self):
        while True:
            for key in self.server_alive:
                self.server_alive[key]=0
            time.sleep(2)
            for key in list(self.server_alive.keys()):
                if self.server_alive[key]==0:
                    del self.server[key]
                    del self.server_alive[key]
                    del self.server_list[key]
                    self.server_order.remove(key)
                    self.server_funs.clear()
                    for s in self.server:
                        for f in self.server[s]:
                            if not f in self.server_funs:
                                self.server_funs.append(f)
                    print(f'{key}已失活\n')
                    continue
                print(f'{key}存活\n')
                # print(f'{key}的具体地址：host:{self.server_list[key][0]},port:{self.server_list[key][1]}')
                # print(f'{key}的函数:{self.server[key]}')
            print(f'服务器顺序是{self.server_order}')

    def client_listen(self):
        self.client_sock.bind((self.register_host, self.client_port))
        self.client_sock.listen(15)

    def handel_client(self,client_socket):
        try: # 处理从客户端读取请求异常
            data = client_socket.recv(1024).decode('utf-8')
            print("接收到数据:", data)
            self.data = json.loads(data)
            method_name = self.data['method_name']
            parts = method_name.split('_')
            if len(parts) >= 2 and parts[0] == "help":
                method_name = method_name[5:]
                effect=self.effect.get(method_name)
                if effect:
                    result = {'effect': effect}
                    result = json.dumps(result).encode('utf-8')
                    client_socket.sendall(result)
                    client_socket.close()
                else:
                    result = {"error1": 'function not found'}
                    result = json.dumps(result).encode('utf-8')
                    client_socket.sendall(result)
                    client_socket.close()
                return
            if method_name == 'help':
                result = {'help': self.server_funs}
                result = json.dumps(result).encode('utf-8')
                client_socket.sendall(result)
                client_socket.close()
            else:
                method_args = self.data['method_args']
                aim = self.inquire(method_name)
                if aim[0] == '':
                    result = {"error1": 'function not found'}
                    result = json.dumps(result).encode('utf-8')
                    client_socket.sendall(result)
                    client_socket.close()
                else:
                    result_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 向服务器发送调用函数请求的连接（C）
                    try:  # 处理向注册服务器发送调用请求的异常
                        result_sock.connect(aim)
                        d = {'method_name': method_name, 'method_args': method_args}
                        result_sock.send(json.dumps(d).encode('utf-8'))
                        data = result_sock.recv(1024)  # 接收方法执行后返回的结果
                        result_sock.close()
                        client_socket.sendall(data)
                        client_socket.close()
                    except socket.error as e:
                        print(f"Socket通信向现有注册服务器发送信息异常: {e}")
                        data = {"error2": '注册服务器状态异常'}
                        result_sock.close()
                        client_socket.sendall(data)
                        client_socket.close()
        except socket.error as e:
            print(f"接收数据异常: {e}")

    def client_loop(self):
        # 循环监听 5003 端口
        self.client_listen()
        print('client listen ' + str(self.client_port) + '\n')
        while True:
            (client_socket, address) = self.client_sock.accept()
            client_handeler = threading.Thread(target=self.handel_client, args=(client_socket,))
            client_handeler.start()

    def inquire(self, method_name):
        for key in self.server_order:
            for fun in self.server[key]:
                if fun==method_name:
                    self.server_order.remove(key)
                    self.server_order.append(key) # 查询的同时进行轮询
                    return self.server_list[key] # 查询到对应函数的服务器，返回地址与端口的元组
        return ('',)