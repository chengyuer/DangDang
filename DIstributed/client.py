#coding:utf-8
'''
分布式爬取当当网书籍信息  客户端  接收服务端发来的链接，
使用selenium 抓取评论
'''
import multiprocessing
import multiprocessing.managers
import threading

import time
import urllib.request

import lxml.etree
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains, DesiredCapabilities

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0"
}






def getComment(url):
    mcommentlist = []
    dcap = dict(DesiredCapabilities.PHANTOMJS)  # 处理无界面浏览器
    # dcap["phantomjs.page.settings.userAgent"]=("Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36")
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0"
    )
    driver = selenium.webdriver.PhantomJS(
        executable_path=r"C:\phantomjs.exe",
        desired_capabilities=dcap)
    # driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(2)
    # 将页面滚动条拖到底部
    for i in range(1, 6):
        js = "document.body.scrollTop="  + str(2000 * i)
        # js = "var q=document.documentElement.scrollTop=" + str(2000 * i)
        driver.execute_script(js)
        time.sleep(3)

    elem = driver.find_element_by_id("comment_tab")

    ActionChains(driver).move_to_element(elem).perform()
    time.sleep(0.5)
    elem.click()  # 点击商品评论
    time.sleep(5)
    html = driver.page_source

    try:

        # 发现评论
        mytree = lxml.etree.HTML(html)
        commentlist = mytree.xpath("//div[@class=\"comment_items clearfix\"]")
        for i in range(1, len(commentlist) + 1):
            commenttext = mytree.xpath(
                "//div[@id=\"comment_list\"]//div[@class=\"comment_items clearfix\"][" + str(i) + "]//span/text()")
            print(commenttext[2])
            print("********************")
            mcommentlist.append(commenttext[2])
        driver.close()
        return mcommentlist
    except  Exception as e :
        print(e)
        driver.close()



class QueueManager(multiprocessing.managers.BaseManager):
    pass


def getEveryBookInfo(text,result):
    with sem:
        mdic = {}
        index = text.xpath("./div[1]/text()")[0] if (len(text.xpath("./div[1]/text()")) != 0) else " "
        title = text.xpath("./div[3]/a/text()")[0] if (len(text.xpath("./div[3]/a/text()")) != 0) else " "
        murl = text.xpath("./div[3]/a/@href")[0] if (len(text.xpath("./div[3]/a/@href")) != 0) else " "
        author = text.xpath("./div[5]/a/@title")[0] if (len(text.xpath("./div[5]/a/@title")) != 0) else " "
        recommend = text.xpath("./div[4]//span[2]/text()")[0] if (len(text.xpath("./div[4]//span[2]/text()")) != 0) else " "
        price = text.xpath("./div[@class='price']//p[1]//span[1]/text()")[0] if (len(text.xpath("./div[@class='price']//p[1]//span[1]/text()")) != 0) else " "
        commentlist = getComment(murl)
        mdic["index"] = index
        mdic["title"] = title
        mdic["murl"] = murl
        mdic["author"] = author
        mdic["recommend"] = recommend
        mdic["price"] = price
        mdic["commentlist"] = commentlist
        print("客户端发送数据")
        result.put(mdic)

def getBookInfo(url,result):
    with sem:
        req = urllib.request.Request(url, headers=headers)
        htmltext = urllib.request.urlopen(req).read()
        mytree = lxml.etree.HTML(htmltext)
        lilist = mytree.xpath("//ul[@class='bang_list clearfix bang_list_mode']//li")
        print ("getbookInfo")
        for li in lilist:
            threading.Thread(target=getEveryBookInfo,args = (li,result)).start()



if __name__ == '__main__':
    # 调用服务端注册的函数
    start = time.time()

    QueueManager.register("return_task")
    QueueManager.register("get_result")

    sem = threading.Semaphore(3)
    # 链接服务端
    manager = QueueManager(address=("169.254.48.147",8888),authkey=123456)
    manager.connect()
    task = manager.return_task()
    result = manager.get_result()

    try:
        for i in range(5000):
            url = task.get(timeout =15)
            th = threading.Thread(target=getBookInfo,args = (url,result))
            th.start()
    except Exception as  e:
        print(e)





