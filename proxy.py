import http.server
import urllib.request
import urllib.parse
import time
import re
import socket
import threading
import select
from datetime import datetime, timedelta

# ---------- 缓存配置 ----------
CACHE = {}
CACHE_LOCK = threading.Lock()
MAX_CACHE_SIZE = 50          # 限制缓存条目数，防止内存爆炸
DEFAULT_TTL = 120            # 默认缓存有效期（秒）

class CachingProxyHandler(http.server.BaseHTTPRequestHandler):
    """带缓存功能的HTTP/HTTPS代理"""

    # ---------- 核心：处理 HTTP 明文请求 ----------
    def do_GET(self):
        # 1. 解析请求URL（浏览器发来的代理请求通常是绝对路径，如 http://example.com/）
        full_url = self.path
        if not full_url.startswith(('http://', 'https://')):
            self.send_error(400, "Bad Request: Only HTTP/HTTPS URLs are supported.")
            return

        # 2. 检查缓存（使用URL作为Key）
        cache_key = full_url
        with CACHE_LOCK:
            cached_entry = CACHE.get(cache_key)
        
        if cached_entry:
            data, headers_dict, status, expires_at = cached_entry
            # 判断缓存是否有效
            if time.time() < expires_at:
                self._send_response(status, headers_dict, data)
                print(f"[Cache HIT] {full_url}")
                return
            else:
                # 缓存过期，移除
                with CACHE_LOCK:
                    CACHE.pop(cache_key, None)
                print(f"[Cache EXPIRED] {full_url}")

        # 3. 缓存未命中或已过期 -> 代理请求远端服务器
        print(f"[Cache MISS] {full_url}")
        try:
            # 构建请求（复制客户端发来的Header，剔除代理专用头）
            req = urllib.request.Request(full_url, method='GET')
            for key, value in self.headers.items():
                if key.lower() not in ['proxy-connection', 'keep-alive', 'connection']:
                    req.add_header(key, value)

            # 发起请求（设置超时）
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
                status = response.getcode()
                response_headers = dict(response.headers)

                # 4. 计算缓存有效期（基于响应头）
                expires_at = time.time() + DEFAULT_TTL
                cache_control = response_headers.get('Cache-Control', '')
                if 'max-age' in cache_control:
                    match = re.search(r'max-age\s*=\s*(\d+)', cache_control)
                    if match:
                        expires_at = time.time() + int(match.group(1))
                elif 'Expires' in response_headers:
                    # 简单处理Expires头（RFC 1123格式）
                    try:
                        exp_date = email.utils.parsedate_to_datetime(response_headers['Expires'])
                        if exp_date:
                            expires_at = exp_date.timestamp()
                    except:
                        pass

                # 5. 存入缓存（控制大小）
                with CACHE_LOCK:
                    if len(CACHE) >= MAX_CACHE_SIZE:
                        # 简单策略：移除最早的一个条目
                        CACHE.pop(next(iter(CACHE)), None)
                    CACHE[cache_key] = (data, response_headers, status, expires_at)

                # 6. 返回响应给客户端
                self._send_response(status, response_headers, data)

        except Exception as e:
            self.send_error(502, f"Proxy Error: {str(e)}")

    # ---------- 核心：处理 HTTPS 隧道 (CONNECT) ----------
    def do_CONNECT(self):
        """处理HTTPS请求（浏览器通过CONNECT建立隧道）"""
        # self.path 格式为 "host:port"
        host, port = self.path.split(':')
        port = int(port)
        print(f"[CONNECT] 建立隧道到 {host}:{port}")

        try:
            # 1. 代理连接到目标服务器
            remote_sock = socket.create_connection((host, port), timeout=30)
        except Exception as e:
            self.send_error(502, f"Cannot connect to {host}:{port} - {e}")
            return

        # 2. 告诉浏览器连接已建立（HTTP 200）
        self.send_response(200, 'Connection Established')
        self.send_header('Proxy-Agent', 'CustomProxy/1.0')
        self.end_headers()

        # 3. 双向转发数据（隧道模式）
        # 获取与客户端通信的底层socket
        client_sock = self.connection
        # 将客户端socket设为非阻塞（配合select使用）
        client_sock.setblocking(False)
        remote_sock.setblocking(False)

        try:
            while True:
                # 监听两个socket的读写状态
                readable, _, exceptional = select.select(
                    [client_sock, remote_sock], 
                    [], 
                    [client_sock, remote_sock], 
                    5  # 超时时间
                )
                if exceptional:
                    break
                for sock in readable:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            break
                        # 将数据转发到另一端
                        if sock is client_sock:
                            remote_sock.sendall(data)
                        else:
                            client_sock.sendall(data)
                    except (ConnectionResetError, BrokenPipeError):
                        break
                else:
                    # 如果没有数据可读，继续循环
                    continue
                break  # 如果发生break，退出外层循环
        except Exception as e:
            print(f"[CONNECT] 隧道传输异常: {e}")
        finally:
            # 清理连接
            client_sock.close()
            remote_sock.close()

    # ---------- 辅助：统一发送响应 ----------
    def _send_response(self, status, headers, body):
        self.send_response(status)
        # 过滤掉一些可能影响代理行为或非标准的头
        for key, value in headers.items():
            if key.lower() not in ['transfer-encoding', 'connection', 'keep-alive']:
                self.send_header(key, value)
        # 关键：告诉浏览器内容长度，确保正确渲染
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---------- 日志简化 ----------
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

# ---------- 启动服务器 ----------
if __name__ == '__main__':
    PORT = 8888
    server = http.server.HTTPServer(('127.0.0.1', PORT), CachingProxyHandler)
    print(f"本地代理已启动，监听端口 {PORT}")
    print("请在浏览器或系统网络设置中配置代理：HTTP代理 127.0.0.1:8888")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n代理已关闭。")