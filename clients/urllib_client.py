'''
    注意，不用socket了，连接过程和接受响应省去了（一步），专心处理response data即可
'''
from urllib.request import urlopen
from urllib.error import URLError

def http_get(url): ## 这次是url，不是path；url = 协议 + host(ip+port) + path
    try:
        with urlopen(url) as response: # 打开url建立连接 --> 获取response
            ## 后面都是response parse了
            print(f"status code: {response.status}")
            for k,v in response.headers.items():
                print(f"{k}:{v}")
            body = response.read() #还是bytes类型
            try:
                content = body.decode('utf-8') #转bytes为str
                print(f"content is :\n{content}")
            except UnicodeDecodeError as e:
                print(f"unicode error as {e}")

    except Exception as e:
        print(f"errors as {e}")

'''
    hhh 使用urllib的urlopen，直接省略了connect和后续的while true的recv过程
    直接获取了response，直接解析就好了，无脑爽
'''


if __name__ == "__main__":
    http_get('http://localhost:12138/file/test.txt')