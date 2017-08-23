#本爬虫以doutula.com为目标进行爬取。创办网站不易，爬取时请注意速度，避免太高的服务器负荷，谢谢！
PAGE_URL_LIST = []
IMG_LIST = []
BASE_PAGE_URL = 'https://www.doutula.com/photo/list/?page='
#20170822,网站共有933页图片
for i in range(1, 934):
	url = BASE_PAGE_URL + str(i)
	PAGE_URL_LIST.append(url)

import requests
from bs4 import BeautifulSoup
import urllib
import os
import threading
import time
from queue import Queue

con = threading.Condition()

class ThreadFoo(threading.Thread):
	def __init__(self, name, q):
		self.name = name
		self.q = q
		super(ThreadFoo, self).__init__()
	def run(self):
		print('this is thread %s' % self.name)

class Producer(threading.Thread):
	def __init__(self, q, name):
		super(Producer, self).__init__()
		self.q = q
		self.name = name
		print('prodocer %s start' % self.name)
	def run(self):
		while PAGE_URL_LIST:
			try:
				con.acquire()
				url = PAGE_URL_LIST.pop()
				con.release()
				response = requests.get(url)
				soup = BeautifulSoup(response.content, 'lxml')
				img_list = soup.find_all('img', class_="img-responsive lazy image_dta")
				IMG_LIST.extend(img_list)
				print('%s: %i img in list, %i img added' % (self.name, len(IMG_LIST), len(img_list)))
			except:
				# con.wait(5)
				print('%s: List is empty, ready to quit!' % (self.name))
			# time.sleep(15)

class Consumer(threading.Thread):
	def __init__(self, q, name):
		super(Consumer, self).__init__()
		self.q = q
		self.name = name
		print('consumer %s start' % self.name)
	def run(self):
		while IMG_LIST:
			try:
				con.acquire()
				img = IMG_LIST.pop()
				con.release()
				filename = str(img['alt'])
				src = str(img['data-original'])
				filesuffix = src.split('/')[-1]
				filesuffix = filesuffix.split('.')[-1]
				filename = filename + '.' + filesuffix
				src = src.replace('//', 'http://')
				path = os.path.join('images', filename)
				urllib.request.urlretrieve(src, path)
				print('%s: %i img in list' % (self.name, len(IMG_LIST)))
			except:
				time.sleep(3)
				print('%s: List is empty, ready to quit!' % (self.name))

queue = Queue()
for i in range(0, 1):
    p = Producer(queue, 'producer%i' % i)
    p.start()
time.sleep(5)
for i in range(0, 30):
    c = Consumer(queue, 'consumer%i' % i)
    c.start()





# for img in img_list:
# 	filename = str(img['alt'])
# 	src = str(img['data-original'])
# 	filesuffix = src.split('/')[-1]
# 	filesuffix = filesuffix.split('.')[-1]
# 	filename = filename + '.' + filesuffix
# 	src = src.replace('//', 'http://')
# 	path = os.path.join('images', filename)
# 	print(path)
# 	print(src)
# 	urllib.request.urlretrieve(src, path)