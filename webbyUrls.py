from bs4 import BeautifulSoup
from collections import defaultdict
from itertools import groupby
from PIL import Image

from contextlib import closing
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webcolors import rgb_to_name



import webcolors
import re
import requests
import string
import sys
import unidecode
import urllib

def findLink(url):
	try:
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
		page=requests.get(url,headers=headers)
		if page.status_code==200:
			soup=BeautifulSoup(page.text,'html.parser')
			link=soup.find("h1").find("a")['href']
		else:
			print(page.status_code)
			link="error"
		return link
	except:
		return url+"#"*10
def setDriverOptions():
	options 				= Options()
	options.binary_location = "/home/abhiavk/git/mysite/mysiteEnv/bin/chromium-browser"
	chrome_driver_binary	= "/home/abhiavk/git/mysite/mysiteEnv/bin/chromedriver"
	#options.add_argument("--headless")
	return	webdriver.Chrome(chrome_options=options)

def main(filename,year):
	browser=setDriverOptions()
	f=open(filename,"r")
	for ext in f:
		url="https://www.webbyawards.com/winners/"+year+str(ext).strip()
		browser.implicitly_wait(10)
		browser.get(url)
		browser.implicitly_wait(10)
		header = browser.find_elements_by_tag_name('h2')
		WebDriverWait(browser, timeout=10).until(lambda x: x.find_elements_by_tag_name('h2'))
		page_source = browser.page_source
		soup=BeautifulSoup(page_source,'html.parser')
		links=soup.findAll("h2",{"class":"mod-winners-gallery__title"})
		for i in links:
			l=i.find("a")
			nextUrl="https://www.webbyawards.com"+str(l['href'])
			print(findLink(nextUrl))

if __name__=="__main__":
	filename 	= sys.argv[-1]
	year		= "2018"
	main(filename,year)
