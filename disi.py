#!/usr/bin/env python
#-*-coding:utf-8-*-


import requests
from bs4 import BeautifulSoup
import sys
import re
import os
import threading
import Queue
import platform
import time

RosiItems = []
PicItems = []
SaveDiskPath = ""

myQueue = Queue.Queue(0)
threadWorker = 10

def checkPath():
    system = platform.system()
    global SaveDiskPath

    abspath = os.path.abspath(".")
    SaveDiskPath = os.path.join(abspath,"Disi")

    print("System: {0},Save images to {1}".format(system, SaveDiskPath))
    if not os.path.isdir(SaveDiskPath):
        print("{0} Not Exist".format(SaveDiskPath))
        os.mkdir(SaveDiskPath)


def downPic(url,retries=3):
    print url
    html = requests.get(url,timeout=10).content
    soup = BeautifulSoup(html, "html.parser")
    pics = soup.find_all("dt",class_="gallery-icon")
    for pic in pics:
        picUrl = pic.find_all("a")[0]['href']
        print picUrl
        picName = picUrl.split('/')[-1]

        savePath = os.path.join(SaveDiskPath,picName)
        if os.path.isfile(savePath):
            print("{0} Exist".format(picName))
        else:
            try:
                picData = requests.get(picUrl,timeout=10).content
                with open(savePath,"wb")as f:
                    f.write(picData)
                    optimizeImg(savePath)
            except Exception,e:
                print(e.message)
                if retries > 0:
                    time.sleep(1)
                    return downPic(url,retries=retries-1)
                else:
                    print("Pic: {} download failed!".format(picName))


def optimizeImg(File):
    system = platform.system()
    script = os.path.join(os.path.abspath("."),"pingo.exe")
    if (system == "Windows" and os.path.isfile(script)):
        os.system("{} -s5 {}".format(script,File))
    else:
        pass


def getPicList():
    for itmeUrl in RosiItems:
        html = requests.get(itmeUrl,timeout=10).content
        soup = BeautifulSoup(html, "html.parser")
        pics = soup.find_all("dt",class_="gallery-icon")
        for pic in pics:
            pic = pic.find_all("a")[0]['href']
            PicItems.append(pic)

def getRosiItem():
    start = time.time()
    index = 1
    while True:
        url = "http://www.mmxyz.net/category/disi/page/{}/".format(index)
        res = requests.get(url,timeout=10)
        if res.status_code == 404:
            print("+   Time: {:.2f} S         +".format(time.time()-start))
            print("+   Total Pages:     {}   +".format(index-1))
            print("+  Total Numbers:   {}  +".format(len(RosiItems)))
            print("+-------------------------+\r\n\r\n")
            return
        soup = BeautifulSoup(res.content, "html.parser")
        rosiList = soup.find_all("a", class_="inimg")
        for rosi in rosiList:
            RosiItems.append(rosi['href'])
        index += 1

class MyDownloadThread(threading.Thread):
	def __init__(self, input):
		super(MyDownloadThread, self).__init__()
		self._jobq = input
	def run(self):
		while self._jobq.qsize()>0:
			job = self._jobq.get()
			downPic(job)
			if self._jobq.qsize() == 1:
				print("Download complete, you got all pictures!（´∀｀*) ")

def main():
    print("+-------------------------+")
    print("+  Get Total Pages...     +")
    print("+  Be Patient   :)        +")
    getRosiItem()
    #getPicList()
    checkPath()

    print len(RosiItems)
    for i in RosiItems:
        myQueue.put(i)
    print("job myQueue size {0}".format(myQueue.qsize()))
    for x in range(threadWorker):
        MyDownloadThread(myQueue).start()





if __name__ == '__main__':
    main()
