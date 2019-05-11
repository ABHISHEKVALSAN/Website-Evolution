from bs4 import BeautifulSoup
from collections import defaultdict
from itertools import groupby

from contextlib import closing
from selenium.webdriver import Chrome,Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


import csv
import re
import requests
import string
import sys
import unidecode
import urllib
import time
import pandas as pd

def main(filename,year):
	#with closing(Firefox()) as browser:
		webbyUrls=pd.read_csv(filename)
		fields=['id','urls']
		csvFile=open('yearUrlWb/Wb'+str(year)+'.csv','a+')
		csvWriter		= csv.writer(csvFile)
		csvWriter.writerow(fields)
		num=1
		for line in webbyUrls['urls']:
			url="https://web.archive.org/web/"+year+"0101000000/"+line
			print(num,url)
			csvWriter.writerow([num,url])
			num+=1
			"""
			browser.get(url)
			time.sleep(10)
			WebDriverWait(browser, timeout=10).until(lambda x: x.find_elements_by_tag_name('div'))
			page_source = browser.page_source
			soup=BeautifulSoup(page_source,'html.parser')
			links=soup.findAll("div",{"class":"captures"})
			print(links)
			for i in links:
				l=i.find("a")['href']
				nextUrl="https://web.archive.org"+str(l)
				print(nextUrl)
				headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
				page=requests.get(url,headers=headers)
				if page.status_code==200:
					print(nextUrl)
					break
				else:
					print(page.status_code)
			"""
if __name__=="__main__":
	filename=str(sys.argv[-1])
	year=str(sys.argv[-2])
	main(filename,year)
