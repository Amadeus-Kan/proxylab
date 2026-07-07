from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os ##解析文件路径用的
import json ##解析和发送json文件用的

class custom_handler(BaseHTTPRequestHandler):
    def log_msg(self, format, *args):
        print(f"{self.address_string()} - {format % args}") ##没看懂
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path) ##提前parse掉url，获取参数
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        print(f"path is {path}, query is {query}") ## logs: 我想看看path和query是什么，这个应该是urllib的用法

        if path == '/':
            self.send_response(200) ##先返回状态
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers() ##先写头
            html = """
             <html><body>
                <h1>欢迎访问自定义服务器</h1>
                <p>使用 http.server 实现</p>
                <ul>
                    <li><a href="/about">关于</a></li>
                    <li><a href="/api/data?name=test">API 测试</a></li>
                    <li><a href="/static/example.txt">静态文件示例</a></li>
                </ul>
            </body></html>
            """
            self.wfile.write(html.encode('utf-8')) #再写body
        elif path == '/about':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h1>presentation</h1><p>test server for python 3.14</p>')
        ### api用法
        elif path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.end_headers()

            response = {
                "status":"ok",
                "path":'./servers/test.txt',
                "msg":"hello from api!",
                "query":query
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            file_path = '.' + path
            # 安全防护：确保路径在 static 目录内
            '''
                注意！！文件所在的根目录，位于你运行这个server的根目录！
                我是在proxylab下运行的，肯定找不到原来的test.txt；
                但我把它从./servers下挪出来，放到proxylab项目根目录下，就可以访问了！！
            '''
            if os.path.exists(file_path) and os.path.isfile(file_path) and not file_path.startswith('..'):
                self.send_response(200)
                # 根据扩展名设置 Content-Type（略）
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                # 404
                self.send_error(404, "File not found")
            



    def do_POST(self):
        pass
def run_server(port=8080):
    server_addr = ('', port)
    httpd = HTTPServer(server_addr, custom_handler) ## httpserver就两个参数，一个是（ip， port）；另一个是handler，怎么处理请求
    print(f"[start] service running on http://localhost:{port}. print ctrl+c to end service.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        print(f"\n[end]service over.")

if __name__ == "__main__":
    run_server(12138)