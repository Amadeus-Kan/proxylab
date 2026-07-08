import requests as rq

def http_get(url='http://localhost:12138/'):
    try:
        ## 握手建立连接 --> while true-- recv在这一行里完成了
        response = rq.get(url)
        ## 后面依旧是处理response的部分
        print(f"status code: {response.status_code}")

        for k,v in response.headers.items():
            print(f"{k}:{v}")

        print(response.text)
        '''
            和urllib的 response.read().decode('utf-8')不同
            requests使用的是 response.content(bytes类型) 和 response.text(str类型，帮你转好了) 这两种模式
        '''
    except Exception as e:
        print(f"连接出现问题。{e}")


if __name__ == "__main__":
    http_get()