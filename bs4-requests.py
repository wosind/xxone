
from bs4 import BeautifulSoup
import requests
headers={"User-Agent":
             "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"}

url = "http://www.baidu.com"
res = requests.get(url=url,headers=headers)

content = res.content.decode("utf-8")
print(content)


