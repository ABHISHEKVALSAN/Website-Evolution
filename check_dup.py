from bs4 import BeautifulSoup
from collections import defaultdict
from itertools import groupby
from PIL import Image

from contextlib import closing
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webcolors import rgb_to_name



import webcolors
import re
import requests
import string
import sys
import unidecode
import urllib
import time


def main(filename):
	
	f=open(filename,"r")
	urls=[]
	for i in f:
		if i not in urls:
			urls.append(str(i))
	urls.sort()
	for i in urls:
		print(i.strip())
	
if __name__=="__main__":
	filename=str(sys.argv[-1]) 
	main(filename)
