import socket

def http_get(host='localhost', port=12138, path='/test.txt'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        ## 建立tcp连接，3次握手
        sock.connect((host, port))

        ## 构造http请求消息，然后拼装
        req_line = f"GET {path} HTTP/1.1\r\n"
        host_header = f"Host:{host}:{port}\r\n"
        conn_header = f"Connection: keep-alive\r\n"
        blank = f"\r\n"
        msg = req_line + host_header + conn_header + blank

        ## 发送请求
        sock.sendall(msg.encode('utf-8'))
        
        ## 等待接收消息 并解析
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk ##因为response消息块可能比较大，多块

        ## 解码
        content = response.decode('utf-8', errors='ignore')
        headers, body = content.split('\r\n\r\n')

        print(f"headers:\n")
        print(headers)
        print(f"body:\n")
        print(body)
        # print(content)

    # except Exception as e:
    #     print(f"errors:{e}")
    finally:
        sock.close()

if __name__ == "__main__":
    http_get(path='/')
    print("\n" + '='*30 + "\n")
    http_get(path='/file/test.txt') ## 记得从项目根目录运行server