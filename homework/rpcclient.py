import json
import socket
import time


class EmptyResponseError(Exception):
    """自定义异常，表示空响应"""
    pass

class TimeoutError(Exception):
    """自定义异常，表示超时"""
    pass
class TCPClient(object):
    def __init__(self,timeout=5):
        self.timeout = timeout  # 设置超时的默认值
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        '''链接Server端'''
        try:# 连接服务器异常时的处理
            self.sock.settimeout(self.timeout)  # 设置套接字超时
            self.sock.connect((host, port))
            # print("连接成功")
        except socket.error as e:
            print(f"连接服务器异常: {e}")
            self.sock.close()

    def send(self, data):
        '''将数据发送到Server端'''
        try: # 发送数据异常处理
            self.sock.send(data)
            # print("数据发送成功")
        except socket.error as e:
            print(f"发送数据异常: {e}")
            self.sock.close()

    def recv(self, length):
        '''接受Server端回传的数据'''
        try:# 接收数据时异常处理
            received_data = self.sock.recv(length)
            # print("数据接收成功:", received_data)
            return received_data
        except socket.error as e:
            print(f"接收数据异常: {e}")
            self.sock.close()


class RPCStub(object):
    def __getattr__(self, function):
        def _func(*args):
            d = {'method_name': function, 'method_args': args}

            try:
                self.send(json.dumps(d).encode('utf-8'))  # 发送数据

                data = self.recv(1024)  # 接收方法执行后返回的结果
                data = json.loads(data.decode('utf-8'))
                if 'error1' in data:
                    raise EmptyResponseError("没有查找到相关函数")
                if 'error2' in data:
                    raise EmptyResponseError("注册服务器状态异常")
                if 'error3' in data:
                    raise EmptyResponseError(data["error3"])
                if 'help' in data:
                    return data['help']
                if 'effect' in data:
                    return data['effect']
                return data['res']

            except socket.timeout:# 等待数据时发生超时
                raise TimeoutError(f"Operation timed out after {self.timeout} seconds")
            except Exception as e:
                print(f"无法与注册中心建立连接： {e}")
            finally:
                self.sock.close()

        setattr(self, function, _func)
        return _func

class RPCClient(TCPClient, RPCStub):
    pass
