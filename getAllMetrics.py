from bs4 import BeautifulSoup
from scipy.spatial import cKDTree as KDTree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display

import csv
import cv2
import datetime
import matplotlib
import multiprocessing as mp
import numpy as np
import re
import string
import sys
import unidecode
import traceback
import time


gridCount=1
rois=[]


def timeTaken(startTime, Metric, MetricValue=""):
	print(Metric.ljust(25," "),datetime.datetime.now()-startTime,"\t\t",MetricValue)
def string_to_words(s):
	s=s.replace("\n"," ")
	s=s.replace(string.punctuation,"")
	s=re.sub("[^\w]"," ",  s).split()
	return s
def get_words(d):
	txt=""
	try:
		txt+=d.execute_script("return document.body.innerText;")
	except:
		pass
	try:
		txt+=d.execute_script("return document.innerText;")
	except:
		pass
	words = string_to_words(str(unidecode.unidecode(txt)))
	return words


def get_word_count(d):
	startTime=datetime.datetime.now()
	words=get_words(d)
	wordCount=float(len(words))
	#timeTaken(startTime,"Word Count",wordCount)
	return wordCount
def get_text_body_ratio(soup,wordCount):

	startTime=datetime.datetime.now()
	headers=[]
	for i in range(1,7):
		headers+=soup.findAll("h"+str(i))
	sizeHeaders=[]
	sizeHeaders+=soup.findAll("font",{"size":"3"})
	sizeHeaders+=soup.findAll("font",{"size":"4"})
	sizeHeaders+=soup.findAll("font",{"size":"5"})
	txt=""
	for i in headers:
		txt+=" "+i.text
	for i in sizeHeaders:
		txt+=" "+i.text
	words=[]
	if len(txt)!=0:
		words=string_to_words(str(unidecode.unidecode(txt)))
	#print words
	headTextCount=float(len(words))
	if wordCount:
		textBodyRatio=headTextCount/wordCount
	else:
		textBodyRatio=0.0
	#timeTaken(startTime,"Text Body Ratio",textBodyRatio)
	return textBodyRatio
def get_emph_body_text_percentage(d,bs,wordCount):

	#print "Param3"
	startTime=datetime.datetime.now()
	boldText = bs.findAll("b")
	words=[]
	for i in boldText:
		words+= string_to_words(str(unidecode.unidecode(i.text)))
	boldWordCount=len(words)
	try:
		txt=str(unidecode.unidecode(d.execute_script("return document.body.innerText")))
	except:
		txt=str(unidecode.unidecode(d.execute_script("return document.body.textContent")))
	pattern = re.compile("!+")
	exclWordCount=len(re.findall(pattern,txt))
	words=get_words(d)
	capWordCount=0
	for i in words:
		if i==i.upper():
			capWordCount+=1

	#print boldWordCount, exclWordCount, capWordCount

	emphTextCount=float(boldWordCount + exclWordCount + capWordCount)

	if wordCount:
		emphTextPercent=(emphTextCount/wordCount)*100.0
	else:
		emphTextPercent=0.0
	#timeTaken(startTime,"Emph text Percent",emphTextPercent)
	return emphTextPercent
def get_text_position_changes(s):
	startTime=datetime.datetime.now()
	#print "Param
	elem=s.findAll()
	prev=""
	textPositionChanges=0
	for i in elem:
		try:
			string=str(i["style"])
			if "text-align:"in string:
				align=string.split("text-align:")[1]
				position=align.split(";")[0].strip()
				if position!=prev:
					textPositionChanges+=1
					prev=position
		except:
			pass
	#timeTaken(startTime,"Text Positional Changes",textPositionChanges)
	return textPositionChanges
def get_text_clusters(d,bs):

	#print "Param5"
	startTime=datetime.datetime.now()
	tableText= bs.findAll("td")+bs.findAll("table")
	paraText = bs.findAll("p")
	textClusters=len(tableText)+len(paraText)
	#timeTaken(startTime,"Text Clusters",textClusters)
	return textClusters
def get_visible_links(d,bs):

	#print "Param6"
	startTime=datetime.datetime.now()
	links=bs.findAll("a")
	visibleLinkCount=0
	for i in links:
		if i.text != "":
			visibleLinkCount+=1
	#timeTaken(startTime,"Visible Links",visibleLinkCount)
	return visibleLinkCount
def get_page_size(d):

	#print "Param7"
	startTime=datetime.datetime.now()
	scriptToExecute = "	var performance = 	window.performance ||\
											window.mozPerformance ||\
											window.msPerformance ||\
									 		window.webkitPerformance || {};\
						var network 	= 	performance.getEntries() || {};\
						return network;"
	networkData = d.execute_script(scriptToExecute)
	pageSize=0
	for i in networkData:
		try:
			pageSize+=float(i[u'transferSize'])
		except:
			pass
	pageSize=float(pageSize)/1024.0
	#timeTaken(startTime,"Page Size",pageSize)
	return pageSize
def get_graphics_percent(d,pageSize):

	#print "Param8"
	startTime=datetime.datetime.now()
	scriptToExecute = "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
	networkData = d.execute_script(scriptToExecute)
	graphicsSize=0.0
	for i in networkData:
		try:
			if i[u'initiatorType']== u'script' or i[u'initiatorType']==u'img' or i['initiatorType']== u'css':
				graphicsSize+=float(i[u'transferSize'])
		except:
			pass
	graphicsSize=float(graphicsSize)/1024.0

	if pageSize==0:
		graphicsPercent=0.0
	else:
		graphicsPercent=graphicsSize*100.0/pageSize
	#timeTaken(startTime,"Graphic Size",graphicsSize)
	return graphicsPercent
def get_graphics_count(d,bs):
	startTime=datetime.datetime.now()
	#print "Param9"
	styleSteets=bs.findAll("style")
	scripts=bs.findAll("script")
	images=d.execute_script("return document.images;")
	graphicsCount=len(styleSteets)+len(images)+len(scripts)
	#timeTaken(startTime,"Graphics Count",graphicsCount)
	return  graphicsCount
def get_color_count(image):

	startTime=datetime.datetime.now()
	use_colors = matplotlib.colors.cnames
	named_colors = {k: tuple(map(int, (v[1:3], v[3:5], v[5:7]), 3*(16,))) for k, v in use_colors.items()}
	ncol = len(named_colors)
	no_match = named_colors['purple']

	color_tuples = list(named_colors.values())
	color_tuples.append(no_match)
	color_tuples = np.array(color_tuples)

	color_names = list(named_colors)
	color_names.append('no match')

	tree = KDTree(color_tuples[:-1])

	tolerance = np.inf
	dist, idx = tree.query(image, distance_upper_bound=tolerance)

	colCounts = np.bincount(idx.ravel(), None, ncol+1).tolist()
	colNames  = color_names

	colors=[]
	for i in range(len(color_names)):
		colors.append([colCounts[i],color_names[i]])

	colors.sort(reverse=True)

	colorCount=0
	for color in colors:
		if color[0]>=7864: #1% of the pixels
			colorCount+=1
		else:
			break

	#timeTaken(startTime,"Color Count",colorCount)
	return colorCount
def get_font_count(d,bs):
	return 0
	startTime=datetime.datetime.now()
	divCount=len(bs.findAll("div"))
	diffFont=set([])
	for i in range(divCount):
		fontStr=""
		script='return document.getElementsByTagName("div")['+str(i)+']["style"]'
		fontStr+=d.execute_script(script+'["font"];')+"font"
		fontStr+=d.execute_script(script+'["fontDisplay"];')+"fontDisplay"
		fontStr+=d.execute_script(script+'["fontFamily"];')+"fontFamily"
		fontStr+=d.execute_script(script+'["fontFeatureSettings"];')+"fontFeatureSettings"
		fontStr+=d.execute_script(script+'["fontKerning"];')+"fontKerning"
		fontStr+=d.execute_script(script+'["fontSize"];')+"fontSize"
		fontStr+=d.execute_script(script+'["fontStretch"];')+"fontStretch"
		fontStr+=d.execute_script(script+'["fontStyle"];')+"fontStyle"
		fontStr+=d.execute_script(script+'["fontVariant"];')+"fontVariant"
		fontStr+=d.execute_script(script+'["fontVariantCaps"];')+"fontVariantCaps"
		fontStr+=d.execute_script(script+'["fontVariantEastAsian"];')+"fontVariantEastAsian"
		fontStr+=d.execute_script(script+'["fontVariantLigatures"];')+"fontVariantLigatures"
		fontStr+=d.execute_script(script+'["fontVariantNumeric"];')+"fontVariantNumeric"
		fontStr+=d.execute_script(script+'["fontVariationSettings"];')+"fontVariationSettings"
		fontStr+=d.execute_script(script+'["fontWeight"];')+"fontWeight"

		diffFont.add(fontStr)
	#print(diffFont)
	fontCount=len(diffFont)-1 # -1 for empty font (default font)
	#timeTaken(startTime,"Font Count",fontCount)
	return fontCount
def getColorfullness(image):
	startTime=datetime.datetime.now()
	(B, G, R) = cv2.split(image.astype("float"))
	rg = np.absolute(R - G)
	yb = np.absolute(0.5 * (R + G) - B)
	(rbMean, rbStd) = (np.mean(rg), np.std(rg))
	(ybMean, ybStd) = (np.mean(yb), np.std(yb))
	stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
	meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
	colourFullness = stdRoot + (0.3 * meanRoot)
	#timeTaken(startTime,"Colourfullness",colourFullness)
	return colourFullness
def getVisualComplexity(image,num):
	startTime=datetime.datetime.now()
	year=sys.argv[-2]
	def splitImage(inImg):
		h,w = inImg.shape[0], inImg.shape[1]
		off1X=0
		off1Y=0
		off2X=0
		off2Y=0
		if w >= h:  #split X
			off1X=0
			off2X=int(w/2)
			img1 = inImg[0:h, 0:off2X]
			img2 = inImg[0:h, off2X:w]
		else:       #split Y
			off1Y=0
			off2Y=int(h/2)
			img1 = inImg[0:off2Y, 0:w]
			img2 = inImg[off2Y:h, 0:w]
		return off1X,off1Y,img1, off2X,off2Y,img2
	def qt(inImg, minStd, minSize, offX, offY):
		global gridCount
		global rois
		h,w = inImg.shape[0], inImg.shape[1]
		m,s = cv2.meanStdDev(inImg)
		if s>=minStd and max(h,w)>minSize:
			oX1,oY1,im1, oX2,oY2,im2 = splitImage(inImg)
			gridCount+=1
			qt(im1, minStd, minSize, offX+oX1, offY+oY1)
			qt(im2, minStd, minSize, offX+oX2, offY+oY2)
		else:
			rois.append([offX,offY,w,h,m,s])

	global gridCount
	global rois

	gridCount=1
	rois=[]
	offX, offY=0,0
	minDev        = 10.0
	minSz         = 20

	#cv2.imshow('Start Image',image)
	h,w = image.shape[0], image.shape[1]
	m,s = cv2.meanStdDev(image)
	qt(image,minDev,minSz,offX,offY)
	imgOut=image
	for e in rois:
		col=255
		if e[5]<minDev:
			col=0
		cv2.rectangle(imgOut, (e[0],e[1]), (e[0]+e[2],e[1]+e[3]), col, 1)
	cv2.imwrite('webScreenshot/'+str(year)+'/screenshot'+str(num)+'_Quad.png',imgOut)
	#cv2.imshow('Quad Image',imgOut)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	visualComplexity=gridCount#((gridCount*1.0)/(1024.0*768.0))**-1
	#timeTaken(startTime,"Visual Complexity",visualComplexity)
	return visualComplexity
def setDriverOptions():
	options 				= Options()
	options.binary_location = "webEvPy/bin/chromium-browser"
	chrome_driver_binary	= "webEvPy/bin/chromedriver"
	#options.add_argument("--headless")
	return	webdriver.Chrome(chrome_options=options)
def getMetrics(urlFile):
	num=urlFile['id']
	url=urlFile['urls']
	year=sys.argv[-2]
	startTime 		= datetime.datetime.now()
	textFilename	= "yearMetrics/CorruptUrls"+str(year)+".txt"
	csvFilename		= "yearMetrics/tempMpUrlMetrics"+str(year)+".csv"
	try:
		driver			= setDriverOptions()
		driver.get(url)
		driver.implicitly_wait(10)

		time.sleep(5)
		driver.set_window_size(1024, 768)
		WebDriverWait(driver, timeout=15).until(lambda x: x.find_elements_by_tag_name('body'))

		driver.save_screenshot('webScreenshot/'+str(year)+'/screenshot'+str(num)+'.png')
		image = cv2.imread('webScreenshot/'+str(year)+'/screenshot'+str(num)+'.png')
		imageGrey = cv2.imread('webScreenshot/'+str(year)+'/screenshot'+str(num)+'.png',0)
		page_source=driver.page_source
		soup=BeautifulSoup(page_source,'html.parser')
		#---------------------------------------------------#
		#--------- Web Metric Calculation ------------------#
		#---------------------------------------------------#
		wordCount				= get_word_count(driver)#Parameter 1
		textBodyRatio			= get_text_body_ratio(soup,wordCount)#Parameter 2
		emphTextPercent			= get_emph_body_text_percentage(driver,soup,wordCount)#Parameter 3
		textPositionalChanges	= get_text_position_changes(soup)#Parameter 4
		textClusters			= get_text_clusters(driver,soup)#Parameter 5
		visibleLinks			= get_visible_links(driver,soup)#Parameter 6
		pageSize				= get_page_size(driver)#Parameter 7
		graphicsPercent			= get_graphics_percent(driver,pageSize)#Parameter 8
		graphicsCount 			= get_graphics_count(driver,soup)#Parameter 9
		colorCount				= get_color_count(image)#Parameter 10
		fontCount				= get_font_count(driver,soup)#Parameter 11
		colourFullness			= getColorfullness(image)#Parameter 12
		visualComplexity		= getVisualComplexity(imageGrey,num)


		tempMetrics=[
					num,\
					url,\
					wordCount,\
					textBodyRatio,\
					emphTextPercent,\
					textPositionalChanges,\
					textClusters,\
					visibleLinks,\
					pageSize,\
					graphicsPercent,\
					graphicsCount,\
					colorCount,\
					fontCount,\
					colourFullness,\
					visualComplexity
			]
		line=tempMetrics
		csvFile		= open(csvFilename,"a+")
		csvWriter	= csv.writer(csvFile)
		csvWriter.writerow(line)
		csvFile.close()
		driver.close()
	except:
		print(traceback.format_exc())
		driver		=	setDriverOptions()
		print("Error scraping the Url")
		f2			= open(textFilename,"a+")
		f2.write(num+","+url+"\n")
		f2.close()
	print(datetime.datetime.now()-startTime,"\t",datetime.datetime.now(),"\t",num,url)
def main(filename,year=""):
	fields			= ["slno","url","p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13"]
	csvFilename		= "yearMetrics/tempMpUrlMetrics"+str(year)+".csv"
	csvFile			= open(csvFilename,"a+")
	csvWriter		= csv.writer(csvFile)
	csvWriter.writerow(fields)
	csvFile.close()
	csvFile			= open(filename,"r")
	urlFile			= csv.DictReader(csvFile)
	driver			= setDriverOptions()
	manager 		= mp.Manager()
	urls 			= manager.list()
	results 		= manager.list()
	pool 			= mp.Pool(1)
	results 		= pool.map_async(getMetrics, urlFile)
	while not results.ready():
		pass
	csvFile.close()

if __name__=="__main__":
	filename=sys.argv[-1]
	year=sys.argv[-2]
	main(filename,year)
