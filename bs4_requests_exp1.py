from bs4 import BeautifulSoup
import requests

def genUrl(cnameLis):#生成所有分类第1页URL
    return {x:"https://so.gushiwen.cn/guwen/Default.aspx?p=1&type=%s" % x for x in cnameLis}

def request(url, header=""):#请求URL并返回soup对象
    res = requests.get(url, headers=header)
    content = res.content.decode("gbk")
    soup = BeautifulSoup(content, "lxml")
    return soup

def getClass(soup):#解析soup获取分类信息
    res = soup.find_all("div", class_="sright")
    cnameLis = []
    for sright in res:
        cnames = sright.find_all("a")
        for cname in cnames:
            cnameLis.append(cname.get_text())
    return cnameLis

def getTitle(soup):#解析soup获取标题信息
    res = soup.find_all("div", class_="sonspic")
    return [x.find_all("b")[0].get_text() for x in res]


def getTable(soup):
    res = soup.find_all("tr")
    for x in res[1:]:
        # print(x)
        resB = x.find_all("td",width="48%")[0].find_all("div")[0].get_text()
        resC = x.find_all("td", width="35%")[0].find_all("div")[0].get_text()
        print(resB,resC)


if __name__ == '__main__':
    url = "http://www.chyxx.com/industry/202002/836126.html"
    soup = request(url)             #获取分类

    getTable(soup)

    # cnameLis = getClass(soup)
    # urls = genUrl(cnameLis)
    # for cname in urls:              #获取每个分类第一页所有标题
    #     soup = request(urls[cname])
    #     res = getTitle(soup)
    #     print("%s: %s"%(cname,res))
