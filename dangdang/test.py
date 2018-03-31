#coding:utf-8
'''
做什么
'''

import  urllib
import urllib.request

import lxml
import lxml.etree
import time
from selenium import webdriver
from selenium.webdriver import ActionChains

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0"
}

url = "http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-24hours-0-0-1-1"

# driver = webdriver.Firefox()
#
# driver.get(url)
# time.sleep(2)


#
# # 将页面滚动条拖到底部
# js="var q=document.documentElement.scrollTop=10000"
# driver.execute_script(js)
# time.sleep(3)
# # 将滚动条移动到页面的顶部
# js="var q=document.documentElement.scrollTop=0"
# driver.execute_script(js)
# time.sleep(3)
#
#
# #将页面滚动条移动到页面任意位置，改变等于号后的数值即可
# js="var q=document.documentElement.scrollTop=1500"
# driver.execute_script(js)
# time.sleep(4)
# js="var q=document.documentElement.scrollTop=3000"
# driver.execute_script(js)
# time.sleep(4)
# js="var q=document.documentElement.scrollTop=4550"
# driver.execute_script(js)
# time.sleep(5)
#
# elem = driver.find_element_by_id("comment_tab")
#
# ActionChains(driver).move_to_element(elem).perform()
# time.sleep(0.5)
# elem.click()  # 点击全站热门
# time.sleep(5)
# print(driver.page_source)



def getComment(url):
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(2)
    # 将页面滚动条拖到底部
    for  i in range(1,6):
        print("滑动"+ str(i))
        js="var q=document.documentElement.scrollTop="+str(2000*i)
        driver.execute_script(js)
        time.sleep(3)


    elem = driver.find_element_by_id("comment_tab")

    ActionChains(driver).move_to_element(elem).perform()
    time.sleep(0.5)
    elem.click()  # 点击商品评论
    time.sleep(5)
    html = driver.page_source
    print(html)
    file = open("nool.txt","wb")
    file.write(html.encode('utf-8'))
    file.close()
    # 发现评论
    mytree = lxml.etree.HTML(html)
    commentlist = mytree.xpath("//div[@class=\"comment_items clearfix\"]")
    for i in range(1,len(commentlist)+1):
        commenttext = mytree.xpath("//div[@id=\"comment_list\"]//div[@class=\"comment_items clearfix\"]["+str(i)+"]//span/text()")
        print(commenttext)
        print("********************")





req = urllib.request.Request(url,headers= headers)
htmltext = urllib.request.urlopen(req).read()
mytree = lxml.etree.HTML(htmltext)
lilist = mytree.xpath("//ul[@class='bang_list clearfix bang_list_mode']//li")
print(len(lilist))
print(lilist)
for li in lilist:
    index = li.xpath("./div[1]/text()")[0] if(len( li.xpath("./div[1]/text()")) !=0) else " "
    title = li.xpath("./div[3]/a/text()")[0] if (len(li.xpath("./div[3]/a/text()") )!= 0) else " "
    url = li.xpath("./div[3]/a/@href")[0] if (len(li.xpath("./div[3]/a/@href") )!= 0) else " "
    author = li.xpath("./div[5]/a/@title")[0] if (len(li.xpath("./div[5]/a/@title")) != 0) else " "
    recommend = li.xpath("./div[4]//span[2]/text()")[0] if (len(li.xpath("./div[4]//span[2]/text()")) != 0) else " "
    price = li.xpath("./div[@class='price']//p[1]//span[1]/text()")[0] if (len(li.xpath("./div[@class='price']//p[1]//span[1]/text()")) != 0) else " "
    getComment(url)
    break
    # print(index)
    # print(title)
    # print(url)
    # print(author)
    # print(recommend)
    # print(price)





