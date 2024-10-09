import threading
import argparse
import socket
import ServerStub

# 启动命令：python RegistCenter.py -i ip -rp 5001 -bp 5002 -cp 5000
def parse_args():
    parser = argparse.ArgumentParser(description="注册中心启动程序",add_help=False)

    # 添加参数
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='显示帮助信息')
    parser.add_argument("-i", "--ip", required=True, help="注册中心IP地址，支持 IPv4 和 IPv6")
    parser.add_argument("-rp", "--register_port", required=True, type=int, help="注册中心服务器注册端口")
    parser.add_argument("-bp", "--beat_port", required=True, type=int, help="注册中心监听心跳端口")
    parser.add_argument("-cp", "--client_port", required=True, type=int, help="注册中心客户端端口")

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
    rp = args.register_port
    bp = args.beat_port
    cp = args.client_port

    # 验证 IP 地址格式
    if not validate_ip(host):
        print("错误：IP 地址格式无效！")
        return

    reg = ServerStub.serverstub(host, rp, bp, cp)
    thread1 = threading.Thread(target=reg.server_loop)  # 服务器注册函数的连接（S）
    thread2 = threading.Thread(target=reg.alive_loop)  # 服务器发送心跳的连接（S）
    thread3 = threading.Thread(target=reg.client_loop)  # 监听客户端发来的请求（S）
    thread4 = threading.Thread(target=reg.monitor_beat)

    # 启动线程
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    # 等待线程结束
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

if __name__ == "__main__":
    main()