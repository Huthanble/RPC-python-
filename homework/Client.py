import threading

import rpcclient
import argparse
import socket
import sys

# 本地测试
# def thread_test():
#     c = rpcclient.RPCClient()
#     c2 = rpcclient.RPCClient()
#     c3 = rpcclient.RPCClient()
#     c4 = rpcclient.RPCClient()
#     c5 = rpcclient.RPCClient()
#     c.connect('127.0.0.1', 5003)  # 向注册中心发送信息的连接（C）
#     c2.connect('127.0.0.1', 5003)  # 向注册中心发送信息的连接（C）
#     c3.connect('127.0.0.1', 5003)  # 向注册中心发送信息的连接（C）
#     c4.connect('127.0.0.1', 5003)  # 向注册中心发送信息的连接（C）
#     c5.connect('127.0.0.1', 5003)  # 向注册中心发送信息的连接（C）
#     # for i in range(0,10):
#     #     c6 = rpcclient.RPCClient()
#     #     c6.connect('127.0.0.1', 5003)  # 向注册中心发送信息的连接（C）
#     #     res6=c6.add(1,2)
#     #     print(f'res6: [{res6}]')
#     res = c.add_normal(1, 2)
#     res2 = c2.mul(2, 3)
#     res3 = c3.div(3, 4)
#     res4 = c4.aaa(3, 4)
#     res5 = c5.add_10(3, 4)
#     print(f'res: [{res}]')
#     print(f'res2: [{res2}]')
#     print(f'res3: [{res3}]')
#
# thread1 = threading.Thread(target=thread_test)
# thread1.start()
# thread2 = threading.Thread(target=thread_test)
# thread2.start()
#
# thread1.join()
# thread2.join()

# 用户输入测试
# 所需要的注册服务器地址和端口
# host='127.0.0.1'
# port=5003
# while(True):
#     # 用户输入要调用的方法名
#     method_name = input("请输入要调用的方法名(输入help可进入查询模式，输入exit退出)：")
#     if method_name=='exit':
#         break
#     if method_name == 'help':
#         c = rpcclient.RPCClient()
#         c.connect(host, port)  # 向注册中心发送信息的连接（C）
#         # 将参数转换为对应的类型
#         converted_args = []
#         result = getattr(c, method_name)(*converted_args)
#         print("现在可用函数有：",result)
#         while(True):
#             method_name = input("请输入要查询的方法名(输入exit可退出查询模式)：")
#             if method_name == 'exit':
#                 break
#             inquire = 'help_'+method_name
#             c1 = rpcclient.RPCClient()
#             c1.connect(host, port)  # 向注册中心发送信息的连接（C）
#             # 将参数转换为对应的类型
#             converted_args = []
#             result = getattr(c1, inquire)(*converted_args)
#             print("该方法的使用方式：", result)
#         continue
#     # 用户输入参数字符串
#     args_str = input("请输入方法参数，以空格分隔：")
#     # 将参数字符串按空格分割成列表
#     args_list = args_str.split()
#     if args_list[0]=='_exit':
#         break
#     c = rpcclient.RPCClient()
#     c.connect(host, port)  # 向注册中心发送信息的连接（C）
#     # 将参数转换为对应的类型
#     converted_args = []
#     for arg in args_list:
#         if '.' in arg:
#             # 如果参数中包含小数点，则尝试转换为浮点数类型
#             try:
#                 converted_args.append(float(arg))
#             except ValueError:
#                 converted_args.append(arg)  # 转换失败则保持原样
#         else:
#             # 否则尝试转换为整数类型
#             try:
#                 converted_args.append(int(arg))
#             except ValueError:
#                 converted_args.append(arg)  # 转换失败则保持原样
#
#     # 调用方法
#     result = getattr(c, method_name)(*converted_args)
#     print("方法调用结果：", result)

# 启动命令：python Client.py -i ip -p 5000
def parse_args():
    parser = argparse.ArgumentParser(description="客户端启动程序",add_help=False)

    # 添加参数
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='显示帮助信息')
    parser.add_argument("-i", "--ip", required=True, help="注册中心服务端 IP 地址，支持 IPv4 和 IPv6")
    parser.add_argument("-p", "--port", required=True, type=int, help="注册中心服务端端口")

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
    port = args.port

    # 验证 IP 地址格式
    if not validate_ip(host):
        print("错误：IP 地址格式无效！")
        return

    # 执行你的程序逻辑，使用提供的 IP 和端口

    while(True):
        # 用户输入要调用的方法名
        method_name = input("请输入要调用的方法名(输入help可进入查询模式，输入exit退出)：")
        if method_name=='exit':
            break
        if method_name == 'help':
            c = rpcclient.RPCClient()
            c.connect(host, port)  # 向注册中心发送信息的连接（C）
            # 将参数转换为对应的类型
            converted_args = []
            result = getattr(c, method_name)(*converted_args)
            print("现在可用函数有：",result)
            while(True):
                method_name = input("请输入要查询的方法名(输入exit可退出查询模式)：")
                if method_name == 'exit':
                    break
                inquire = 'help_'+method_name
                c1 = rpcclient.RPCClient()
                c1.connect(host, port)  # 向注册中心发送信息的连接（C）
                # 将参数转换为对应的类型
                converted_args = []
                result = getattr(c1, inquire)(*converted_args)
                print("该方法的使用方式：", result)
            continue
        # 用户输入参数字符串
        args_str = input("请输入方法参数，以空格分隔：")
        # 将参数字符串按空格分割成列表
        args_list = args_str.split()
        if args_list[0]=='_exit':
            break
        c = rpcclient.RPCClient()
        c.connect(host, port)  # 向注册中心发送信息的连接（C）
        # 将参数转换为对应的类型
        converted_args = []
        for arg in args_list:
            if '.' in arg:
                # 如果参数中包含小数点，则尝试转换为浮点数类型
                try:
                    converted_args.append(float(arg))
                except ValueError:
                    converted_args.append(arg)  # 转换失败则保持原样
            else:
                # 否则尝试转换为整数类型
                try:
                    converted_args.append(int(arg))
                except ValueError:
                    converted_args.append(arg)  # 转换失败则保持原样

        # 调用方法
        result = getattr(c, method_name)(*converted_args)
        print("方法调用结果：", result)


if __name__ == "__main__":
    main()