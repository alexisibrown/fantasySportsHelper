
import urllib.robotparser
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import socket
import os 
import csv
import json
import signal


class WebCrawler:

	#Set first item in pagesToCrawl array to the seed
	def __init__(self,Seed=[]):
		self.pagesToCrawl = Seed         #List of pages left to crawl
		self.pagesAlreadyCrawled = []    #List of pages already crawled
		self.robotTxts = {}              #Key:domainName,Value:respective robot.txt Object
		self.adjMatrix = {}
		self.count = 0					 #How many pages crawled
		self.fileName = Seed[0]+"#pages" #Name for folder
		self.fileName = self.fileName.replace('/','').replace(':','')

	#Check robots.txt for respective domain and return true if crawlable
	def checkRobots(self,url):
		#Get robots.txt for respective domain
		parsedUrl = urllib.parse.urlsplit(url)
		robotParser = self.robotTxts.get(parsedUrl.hostname)

		#If domain has been crawled before
		if robotParser is not None:
			if robotParser.can_fetch("*",url):
				return True
			return False

		#Add new domain to dict
		else:
			robotParser = urllib.robotparser.RobotFileParser()
			robo = urllib.parse.urljoin(parsedUrl.scheme + '://' + parsedUrl.hostname,"robots.txt")
			robotParser.set_url(robo)
			try:
				robotParser.read()
			except Exception as e:
				print("Failed to read robots.txt of",robo)
				print(e)
				return False
			else:
				self.robotTxts[parsedUrl.hostname] = robotParser
				if self.robotTxts[parsedUrl.hostname].can_fetch("*",url):
					return True
				return False
		
	#Get text from page given
	def getHtml(self,url):
		try:
			#Check content type to make sure its a text/hmtl page and get url
			page = requests.get(url,timeout=5)
			CT = page.headers.get('Content-Type')
			if(CT is not None and "text/html" in CT):
				return page.text
			return "Error"
		except Exception as e:
			print('Error grabbing URL text: Request Timed out')
			print(e)
			return "Error"		

	#Create folder to hold webpages crawled
	def createDir(self,oneFile):
		if oneFile:
			cwd = os.getcwd()
			folderName = "wcFiles"
			self.fileName = folderName
			path = os.path.join(cwd, folderName)
		else:
			cwd = os.getcwd()
			folderName = self.fileName
			path = os.path.join(cwd, "pages")
		try:
			os.mkdir(path)
			print("Created folder to hold crawled pages:",folderName)
		except Exception:
			print("File already Created")

	#DL and create textfile to save info
	def createTextFile(self,url,html):
		try:
			#Get text from html of url and create file based off webpage name
			bs = BeautifulSoup(html, 'lxml')
			content = bs.get_text(" ", strip=True)
			url1 = url.replace('/','').replace(':','')

			if len(url1) > 255:
				url1 = url1[:254]

			with open(f'pages/{url1}.txt', 'w') as f:
				f.write(url)
				f.write('\n')
				f.write(content)
			self.count+=1
		except Exception as e:
			print("Failed to write to file:")
			print(e)

	def handler(self,signum,frame):
		print("\nProgram has been stopped. Crawled Pages:",self.count)
		self.createAdjMatrixFile()
		exit(1)
	
	#Filters out unwanted file types
	def checkUrlType(self,url):
		if ".pdf" in url:
			return 0
		if ".png" in url:
			return 0
		if ".jpg" in url:
			return 0
		if ".doc" in url:
			return 0
		if ".mp3" in url:
			return 0
		if ".mp4" in url:
			return 0
		return 1

	#Return True if URLs were able to get extracted from given page, false if error with reading robots.txt
	def getUrlsFromPage(self,url,html):
		#List of urls that link from current url
		listofUrls = []
		if(html == "Error"):
			return False
		#Parse html and filter out unwanted links. If URLs are not in pagedAlreadyCrawled or pagesToCrawl then we add them
		bs = BeautifulSoup(html,'html.parser')
		for link in bs.find_all('a'):
			UrlPath = link.get("href")
			if(UrlPath != '/'):
				if UrlPath is not None and self.checkUrlType(UrlPath) == 1:
					if UrlPath.startswith('/'):
						UrlPath = urljoin(url,UrlPath)
						listofUrls.append(UrlPath)
						if UrlPath not in self.pagesToCrawl or UrlPath not in self.pagesAlreadyCrawled:
							self.pagesToCrawl.append(UrlPath)
					elif UrlPath.startswith("http"):
						listofUrls.append(UrlPath)
						if UrlPath not in self.pagesToCrawl or UrlPath not in self.pagesAlreadyCrawled:
							self.pagesToCrawl.append(UrlPath)
		self.adjMatrix[url] = listofUrls
		return True

	#Create external file to hold adj matrix. Able to select either json or csv. DEFAULT csv
	def createAdjMatrixFile(self):
		with open(self.fileName + ".json", "w") as outfile:
			json.dump(self.adjMatrix, outfile)

	# Crawl web based off given seed and pages in queue
	def crawl(self,limit):
		signal.signal(signal.SIGINT,self.handler)
		self.createDir(False)
		pagesToCrawl = self.pagesToCrawl
		pagesAlreadyCrawled = self.pagesAlreadyCrawled
		socket.setdefaulttimeout(1)

		#While pages exsist to crawl and limit is not yet reached, Check for if we already crawled them and if not, crawl.
		while pagesToCrawl and self.count <= limit:
			url = pagesToCrawl.pop(0)
			if url not in pagesAlreadyCrawled:
				if self.checkRobots(url):
					print("Crawling",url,"-------- Crawled",self.count," pages")
					html = self.getHtml(url)
					if html != "Error":
						self.getUrlsFromPage(url,html)
						self.createTextFile(url,html)
				pagesAlreadyCrawled.append(url)
		self.createAdjMatrixFile()
		print("Crawled a total of",self.count-1,"pages!")
		

def main():
	seed = 'https://www.basketball-reference.com/'
	pageNumber = 5000

	#Print default settings and ask if they're good
	#If N, go thru the settings one by one

	print("Web Crawler")
	print("==========================")
	print("Default Settings")
	print("==========================")
	print("Seed: https://www.basketball-reference.com/")
	print("# of pages to be crawled: 5000")
	print("==========================")

	isDone = 0
	while not isDone:
		ustr = input("Would you like to use the default settings? (Y/N): ")
		if ustr == "N" or ustr == "n":
			
			isDone2 = 0
			while not isDone2:
				ustr2 = input("Would you like to use the default seed? (Y/N): ")
				if ustr2 == "N" or ustr2 == "n":
					newSeed = input("Please enter a URL: ")
					seed = newSeed
					print(seed+" will be used as the seed.")
					isDone2 = 1
				elif ustr2 == "Y" or ustr2 == "y":
					print("The default seed will be used.")
					isDone2 = 1
				else:
					print("Please enter Y or N.")
					continue
			
			isDone3 = 0
			while not isDone3:
				ustr3 = input("Would you like to use the default number of pages? (Y/N): ")
				if ustr3 == "N" or ustr3 == "n":
					newNum = input("Please enter a number: ")
					pageNumber = int(newNum)
					print(str(pageNumber)+" pages will be crawled.")
					isDone3 = 1
				elif ustr3 == "Y" or ustr3 == "y":
					print("The default number of pages will be used.")
					isDone3 = 1
				else:
					print("Please enter Y or N.")
					continue
			isDone = 1
			
		elif ustr == "Y" or ustr == "y":
			print("Default settings will be used.")
			isDone = 1
		else:
			print("Please enter Y or N.")
			continue
	print("==========================")
	print("Crawler beginning now.")
	print("==========================")
	print()
	WebCrawler(Seed = [seed]).crawl(pageNumber)

	
# Initialize crawler and give it a seed and how many pages to crawl before end
if __name__ == '__main__':
	#WebCrawler(Seed = ["https://www.basketball-reference.com/"]).crawl(5000)
	main()
