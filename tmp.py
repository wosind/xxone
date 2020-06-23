import re
import requests
from bs4 import BeautifulSoup


def getHTML(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""


def getContent(url):
    html = getHTML(url)

    soup = BeautifulSoup(html, 'html.parser')

    title = soup.select('article-tag')
    paras_tmp = soup.select('p')

    paras = paras_tmp[1:]
    return paras


def get_list(url):
    html = getHTML(url)
    soup = BeautifulSoup(html, 'html.parser')
    html = soup.find_all(class_='list16')
    print(html[0].a["href"])
    # 地址解析不对，改成下面的
    list = []
    for r in html:
        t = r.find_all('a')
        for x in t:
            try:
                href = x["href"]
                # print(href)
                list.append(href)
            except:
                print(r)
    return list


def saveFile(text, i):  # 添加接收文章序号i
    f = open('F{}.txt'.format(i), 'w')  # 文件名不能包含：
    for t in text:
        if len(t) > 0:
            f.writelines(t.get_text() + "\n\n")
    f.close()


if __name__ == '__main__':
    url = 'http://news.sohu.com/'
N = input("请输入爬取的文章数目:")
list = get_list(url)
for i in range(int(N)):
    url = list[i]
    url = "https:%s" % url if url[:2] == "//" else url
    print(url)
    text = getContent(url)
    saveFile(text, i + 1)  # 没有把文章序号传递

print("已爬取{}篇文章".format(i + 1))
text = getContent("https://www.sohu.com/a/403579463_119038")
print(text)
