from http.server import HTTPServer, BaseHTTPRequestHandler
# import urllib
from urllib.request import urlopen
## 首先是先要在本地建立服务，接收报文；
## 改代理，计算机会把所有的报文都发道代理地址的






############################################
##              main logic                ##
############################################
'''
    主循环逻辑：
    永远监听本地端口的报文；
    收到报文后，解析，然后作为客户端，connect指定目标，把报文发送给它
    client只是server里的一个小功能
'''
class proxy_handler(BaseHTTPRequestHandler):
    def _send_response(self, status, headers, body):
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        print(self.path) ##这是什么变量啊
        full_url = self.path
        if not full_url.startswith(("http://","https://")):
            self.send_error(404, "resource not found")
            return
        
        try:
            rq = urllib.request.Request(full_url, method='GET')
            for k, v in self.headers.items():
                if k.lower() not in ['connection','proxy-connection']:
                    rq.add_header(k,v)
            
            with urlopen(full_url, timeout=30) as response:
                status = response.getcode()
                headers = dict(response.headers)
                data = response.read()

                self._send_response(status, headers, data)
        except Exception as e:
            self.send_error(502, f"proxy error : {e}")


def run_proxy(host_ip='localhost', host_port=12138):
    host = (host_ip, host_port)
    httpd = HTTPServer(host, proxy_handler)
    print(f"proxy running at {host_ip}:{host_port}")
    try:
        httpd.serve_forever()
    except Exception as e:
        print(f"httpd errors :{e}")
    finally:
        httpd.shutdown()

if __name__ == "__main__":
    run_proxy('localhost', 12138)