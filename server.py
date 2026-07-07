import socket

# 服务器配置
HOST = '127.0.0.1'   # 监听所有网络接口（0.0.0.0）或本地回环（127.0.0.1）
PORT = 12138        # 端口号

# 创建一个 TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 允许端口重用（避免重启时 Address already in use）
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 绑定到地址和端口
server_socket.bind((HOST, PORT))
# 开始监听，最大等待连接数设为 5
server_socket.listen(5)
print(f"服务器已启动，访问 http://{HOST}:{PORT}")

while True:
    # 接受客户端连接
    client_socket, client_address = server_socket.accept()
    print(f"收到来自 {client_address} 的连接")

    # 接收 HTTP 请求数据（最多 1024 字节）
    request_data = client_socket.recv(1024).decode('utf-8')
    # 解析请求行（第一行）
    request_line = request_data.split('\r\n')[0] if request_data else ''
    print(f"请求行: {request_line}")

    # 构造 HTTP 响应
    # 响应体（HTML 内容）
    response_body = """
    <html>
        <head><title>我的服务器</title></head>
        <body>
            <h1>Hello, World!</h1>
            <p>这是一个通过 socket 搭建的 HTTP 服务器。</p>
        </body>
    </html>
    """
    # 响应头：状态行 + 头部字段
    response_headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        "Connection: close\r\n"
        "\r\n"   # 空行分隔头部和正文
    )
    # 拼接完整响应并发送
    response = response_headers + response_body
    client_socket.sendall(response.encode('utf-8'))

    # 关闭客户端连接
    client_socket.close()