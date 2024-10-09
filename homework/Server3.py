import threading
import argparse
import socket
import rpcserver

def add_3(a, b, c):
    sum = a + b + c
    return sum

def mul(a,b):
    result=a*b
    return result

def sub(a,b):
    result=a-b
    return result

def div(a,b):
    if b:
        result=a/b
        return result
    else:
        return 0


# 启动命令：python Server.py -i ip -sn server3 -ri register_ip -p 5005 -bp 5002 -rp 5001

def parse_args():
    parser = argparse.ArgumentParser(description="服务器启动程序",add_help=False)

    # 添加参数
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='显示帮助信息')
    parser.add_argument("-i", "--ip", required=True, help="服务器IP地址，支持 IPv4 和 IPv6")
    parser.add_argument("-sn", "--server_name", required=True, help="服务器名称")
    parser.add_argument("-ri", "--register_ip", required=True, help="注册中心ip")
    parser.add_argument("-p", "--server_port", required=True, type=int, help="服务器监听服务请求端口")
    parser.add_argument("-bp", "--beat_port", required=True, type=int, help="注册中心心跳监听端口")
    parser.add_argument("-rp", "--register_port", required=True, type=int, help="注册中心注册端口")

    return parser.parse_args()
def validate_ip(ip):
    try:
        # 尝试解析 IP 地址
        socket.inet_pton(socket.AF_INET, ip)  # IPv4
        return True
    except socket.error:
        pass

    try:
        socket.inet_pton(socket.AF_INET6, ip)  # IPv6
        return True
    except socket.error:
        pass

    return False
def main():
    args = parse_args()

    host = args.ip
    name = args.server_name
    ri = args.register_ip
    port = args.server_port
    bp = args.beat_port
    rp = args.register_port

    # 验证 IP 地址格式
    if not validate_ip(host):
        print("错误：服务器IP 地址格式无效！")
        return
    if not validate_ip(ri):
        print("错误：注册中心IP 地址格式无效！")
        return

    s = rpcserver.RPCServer(name, host, port, ri, bp, rp)
    s.register_function(add_3, '可输入三个数字相加')  # 注册方法
    s.register_function(div, '输入两个数字，进行除法')  # 注册方法
    s.register_function(sub, '输入两个数字，进行减法')  # 注册方法
    s.register_function(mul, '输入两个数字，进行乘法')  # 注册方法

    thread1 = threading.Thread(target=s.loop)  # 服务器监听调用函数的连接（S）
    thread2 = threading.Thread(target=s.beat)  # 服务器向注册中心发送心跳（C）

    # 启动线程
    thread1.start()
    thread2.start()

    # 等待线程结束
    thread1.join()
    thread2.join()


if __name__ == "__main__":
    main()