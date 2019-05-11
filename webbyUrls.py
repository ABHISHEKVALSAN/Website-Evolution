from bs4 import BeautifulSoup
from contextlib import closing
from selenium.webdriver import Firefox,Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import requests
import string
import sys
import unidecode
import urllib
import pandas as pd

def findLink(url,year):
	try:
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
		page=requests.get(url,headers=headers)
		if page.status_code==200:
			soup=BeautifulSoup(page.text,'html.parser')
			link=soup.find("h1").find("a")['href']
		else:
			print(page.status_code)
			link="error"
		with open("yearUrlWebby/WebbyUrl"+year+".csv","a+") as f:
			f.write(link+"\n")
		return link
	except:
		return url+"#"*10
def setDriverOptions():
	options 				= Options()
	options.binary_location = "webEvPy/bin/chromium-browser"
	chrome_driver_binary	= "webEvPy/bin/chromedriver"
	options.add_argument("--headless")
	return	webdriver.Chrome(options=options)
def main(filename,year):
	browser=setDriverOptions()
	cat=pd.read_csv(filename)
	with open("yearUrlWebby/WebbyUrl"+year+".csv","a+") as f:
		f.write("urls\n")
	for category in cat['category']:
		url="https://www.webbyawards.com/winners/"+str(year)+str(category).strip()
		browser.get(url)
		browser.implicitly_wait(10)
		header = browser.find_elements_by_tag_name('h2')
		WebDriverWait(browser, timeout=10).until(lambda x: x.find_elements_by_tag_name('h2'))
		page_source = browser.page_source
		soup=BeautifulSoup(page_source,'html.parser')
		links=soup.findAll("h2",{"class":"mod-winners-gallery__title"})
		with open("yearUrlWebby/WebbyUrl"+year+".csv","a+") as f:
			for i in links:
				l=i.find("a")
				nextUrl="https://www.webbyawards.com"+str(l['href'])
				print(category,findLink(nextUrl,str(year)))

if __name__=="__main__":
	filename 	= sys.argv[-1]
	year		= sys.argv[-2]
	main(filename,year)
