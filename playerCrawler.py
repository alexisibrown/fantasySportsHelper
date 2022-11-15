import urllib.robotparser
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import socket
import os 
import csv
import json
import signal
import time

class player_web_crawler(object):

	def __init__(self,Seed = []):
		self.pagesToCrawl = Seed         #List of pages left to crawl
		self.pagesAlreadyCrawled = []    #List of pages already crawled
		self.robotTxts = {}              #Key:domainName,Value:respective robot.txt Object
		self.players = []

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
			except Exception:
				print("Failed to read robots.txt of",robo)
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
				return page
			return "Error"
		except Exception:
			print('Error grabbing URL text: Request Timed out')
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
			path = os.path.join(cwd, "players")
		try:
			os.mkdir(path)
			print("Created folder to hold crawled pages: players")
		except Exception:
			print("File already Created")

	#DL and create textfile to save info
	def createTextFile(self,url,player_info):
		try:
			with open(f'players/{player_info[0]}.txt', 'w') as f:
				f.write(url)
				f.write('\n')
				for info in player_info:
					f.write(info)
					f.write('\n')
		except Exception:
			print("Failed to write to file")

	def find_page_links(self,url):
		count = 0
		html_page = self.getHtml(url)
		soup = BeautifulSoup(html_page.content, "lxml")
		for link in soup.findAll('a'):
			href = link.get('href')
			if "/player/" in href and count <16:
				self.players.append(urljoin(url,href))
				count+=1

	def find_team_page_links(self,url,html):
		soup = BeautifulSoup(html.content,"html.parser")
		team_links = soup.find_all(class_="TeamFigure_tfLinks__gwWFj")
		
		for team in team_links:
			for link in team.findAll('a'):
				href = link.get('href')
				if "/team" in href and "/stats" not in href:
					self.pagesToCrawl.append(urljoin(url,href))



	def get_player_info(self,html):
		try:
			soup = BeautifulSoup(html.content,"html.parser")
			player_bio = soup.find(class_="PlayerSummary_mainInnerBio__JQkoj")
			player_name= player_bio.find_all("p",class_ = "PlayerSummary_playerNameText___MhqC")
			player_image = soup.find("img","PlayerImage_image__wH_YX PlayerSummary_playerImage__sysif")
			player_image_src = player_image['src']
			player_full_name = ""
			for name in player_name:
				player_full_name+=name.text
				player_full_name+=" "
			player_full_name = player_full_name.strip(" ")
			
			team_number_position = player_bio.find("p",class_ ="PlayerSummary_mainInnerInfo__jv3LO")

			team_number_position_split = team_number_position.text.split("|")
			player_team = team_number_position_split[0].strip(" ")
			player_number = team_number_position_split[1].strip(" ")
			player_position = team_number_position_split[2].strip(" ")


			player_stats = soup.find(class_="PlayerSummary_summaryBotInner__1r03I")
			player_stats_per_game = player_stats.find_all("p",class_ = "PlayerSummary_playerStatValue___EDg_")
			player_points_per_game = player_stats_per_game[0].text.strip(" ")
			player_rebounds_per_game = player_stats_per_game[1].text.strip(" ")
			player_assists_per_game = player_stats_per_game[2].text.strip(" ")
			print("Got player info for:",player_full_name)
		except Exception:
			print("ERROR")
			return 0

		return player_full_name,player_team,player_number,player_position,player_points_per_game,player_rebounds_per_game,player_assists_per_game,player_image_src

	def crawl(self):
		 self.createDir(False)
		 url = self.pagesToCrawl.pop(0)
		 html = self.getHtml(url)
		 self.find_team_page_links(url,html)
		 while len(self.pagesToCrawl) != 0:
		 	self.find_page_links(self.pagesToCrawl.pop(0))
		 while len(self.players) !=0:
		 	url = self.players.pop(0)
		 	html = self.getHtml(url)
		 	time.sleep(1)
		 	results = self.get_player_info(html)
		 	if results !=0:
		 		self.createTextFile(url,results)
	


if __name__ == '__main__':
	html = player_web_crawler(Seed = ["https://www.nba.com/teams"]).crawl()
	




