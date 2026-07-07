import socket
import os
import threading

host = 'localhost'
port = 12138
buffer_size = 4096

def handle(client_sock, client_addr): #绑定client的socket和addr
    print(f"new link from :{client_addr}")
    try:
        '''
        首先是解析请求
        '''
        raws = client_sock.recv(buffer_size) #看看这个连接都接受了些什么
        if not raws:
            return
        txt = raws.decode('utf-8', errors='ignore')
        line_0 = txt.split('\r\n')[0] if txt else '' 
        ## http请求的第一行，基本是GET <url> HTTP/1.1 这种
        parts = line_0.split(' ') ## convert to [GET, url, HTTP/1.1]
        if len(parts) < 2:
            raise ValueError("Invalid requests")
        method, path, _ = parts[0], parts[1], parts[2]

        '''
        简单地解析过请求了
        现在
        构造并返回响应
        '''
        if method == 'GET':
            if path == '/' or path == '/index.html':
                body = """
                    <html>
                        <head><title>欢迎</title></head>
                        <body>
                            <h1>Server Test</h1>
                            <p>pure server build from socket</p>
                        </body>
                    </html>
                    """
                status = "HTTP/1.1 200 OK"
                content_type = 'text/html;charset=utf-8'
            else:
                #如果不是上述欢迎界面，那认定可能是文件类请求吧
                #给他返回个文件吧
                #如果是根目录，记得访问：/servers/test.txt，或者把test.txt放在项目根目录下
                fpath = os.path.normpath('.' + path) #就在当前目录下寻找吧
                if os.path.isfile(fpath) and not fpath.startswith('..'): #避免路径穿越
                    with open(fpath, 'rb') as f:
                        body = f.read()
                    status = "HTTP/1.1 200 OK"
                    ## 然后根据fpath文件名后缀，决定返回的content_type是什么
                    if fpath.endswith('.html'):
                        content_type = 'text/html; charset=utf-8'
                    elif fpath.endswith('.css'):
                        content_type = 'text/css'
                    elif fpath.endswith('.js'):
                        content_type = 'application/javascript'
                    elif fpath.endswith('.png'):
                        content_type = 'image/png'
                    elif fpath.endswith('.jpg') or fpath.endswith('.jpeg'):
                        content_type = 'image/jpeg'
                    else:
                        content_type = 'application/octet-stream'

                else:
                    #他要的文件找不到
                    body = "<h1>404 not found<h1>"
                    status = "HTTP/1.1 405 Method Not Allowed"
                    content_type = 'text/html;charset=utf-8'
        else:
            ### 本服务器没写那么多请求方法
            ### 可以包含POST，PUT等请求方法，但这里懒了，先留个坑
            body = "<h1>405 Method Not Allowed</h1>"
            status_line = 'HTTP/1.1 405 Method Not Allowed'
            content_type = 'text/html; charset=utf-8'
        
        ### !!! 用上述信息构造response
        if isinstance(body, str): #额外处理body为str情况，因为也可能不是
            body = body.encode('utf-8')
        response = (
            f"{status}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: keep-alive\r\n"
        ).encode('utf-8') + body
        '''
        发送响应
        '''
        client_sock.sendall(response)
        print(f"[response] status code {status.split(' ')[1]}, length {len(body)} bytes")
    except Exception as e:
        print(f"processing client {client_addr} errors: {e}")
    # finally:
    #     client_sock.close()
    #     print(f"client {client_addr} disconnected.")

    
def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP连接
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #允许端口复用
    sock.bind((host, port)) #固定节目，bind ip和port
    sock.listen(10) #最大连接数，10个client，多了连不了
    print(f"server started at http://{host}:{port}")
    try:
        while True: #需加，否则接受一个连接即退出
            '''
                handle http 的各种请求，放外面进一步封装
            '''
            client_sock, client_addr = sock.accept() #accept函数，是server用的
            client_thread = threading.Thread(target=handle, args=(client_sock, client_addr)) #用threading库创建多线程
            client_thread.deamon = True
            client_thread.start() #好，虽然不懂多线程，但这样这个实例就拉起来了
    except Exception as e:
        print(f"Server Stopped.")
    finally:
        sock.close() #一定别忘了，最后加个finally，最后关掉这个不用的socket

if __name__ == "__main__":
    start_server()