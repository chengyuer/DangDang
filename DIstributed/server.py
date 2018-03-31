#coding:utf-8
'''
分布式爬取当当网当前热销前500名书籍信息
服务端  将链接传给客户端
接收客户端下载的书籍信息，并存入mongodb数据库
'''

import multiprocessing
import multiprocessing.managers
import threading

import pymongo
import time

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0"
}


task_queue = multiprocessing.Queue()
resulturl_queue = multiprocessing.Queue()

def return_task(): #返回结果队列
    return task_queue
def recvier_result():
    return  resulturl_queue  # 接收结果队列


class QueueManager(multiprocessing.managers.BaseManager):
    pass


# 多线程存入书籍信息
def saveData(mresult,collection):
    with sem:
        collection.insert(
            {"index": mresult['index'], "title": mresult['title'], "murl": mresult['murl'], "author": mresult['author'],
             "recommend": mresult['recommend'], "price": mresult['price'],"commentlist": mresult['commentlist'][0]})

if __name__ == '__main__':

    starttime = time.time()
    # 链接mongo数据库
    conn = pymongo.MongoClient("120.78.177.150",27017)
    client = conn['mydangdang']
    collection = client['recent24']


    # 开启分布式支持
    multiprocessing.freeze_support()

    QueueManager.register("return_task",callable=return_task) # 注册函数给客户端调用
    QueueManager.register("get_result",callable=recvier_result)

    # 创建一个管理器 设置地址与密码
    manager = QueueManager(address= ("169.254.48.147",8888),authkey=123456)
    manager.start() # 开启
    task = manager.return_task()
    result = manager.get_result()  # 接收客户端返回的结果
    for i in range(1,26):  # 构建url链接
        url = "http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-24hours-0-0-1-"+str(i)
        task.put(url)  # 存入服务器任务队列
        print("server distribute task",url)

    print("任务发送完毕")

    sem = threading.Semaphore(10)
    try:
        for i in range(5000):
            mresult = result.get(timeout=1000)
            threading.Thread(target=saveData,args =( mresult,collection)).start()
            print("服务端接收数据")
            print(mresult)

    except Exception as e:
        endtime = time.time()
        print("用时",str(endtime-starttime))
        print(e)



