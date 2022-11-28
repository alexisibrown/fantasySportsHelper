import shutil
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser
import os 
import whoosh.index as indexa
import json

class MyWhooshPlayerSearcher(object):
	def __init__(self):
		super(MyWhooshPlayerSearcher, self).__init__()

	def buildIndex(self,directory):
		#Each tuple will have a url and the content of that url that is in our corpus
		schema = Schema(name = TEXT(stored=True),url=TEXT(stored=True),team=TEXT(stored=True),position=TEXT(stored=True),PPG=TEXT(stored=True),RPG=TEXT(stored=True),
			APG=TEXT(stored=True),number=TEXT(stored=True),image=TEXT(stored=True))
		#check if index is created
		if not os.path.exists("player_index_dir"):
			os.mkdir("player_index_dir")
		else:
			print("Index already created!")
			return
		ix = create_in("player_index_dir",schema)
		writer = ix.writer()
		for filename in os.listdir(directory):
			f = os.path.join(directory,filename)
			if os.path.isfile(f):
				file = open(f,"r")
				Lines = file.readlines()
				print(Lines)
				writer.add_document(name = Lines[1].rstrip(), url=Lines[0].rstrip(),team = Lines[2].rstrip(),
				position = Lines[4].rstrip(),PPG = Lines[5].rstrip(),RPG = Lines[6].rstrip(),APG = Lines[7].rstrip(),number = Lines[3].rstrip(),
				image = Lines[8])
		writer.commit()

		#search index based on given query and return user specified number of hits
	def search(self,search_query,index,return_number,disjunctive):
		from whoosh.qparser import QueryParser
		names = list()
		teams = list()
		urls = list()
		positions = list()
		PPGs = list()
		RPGs = list()
		APGs = list()
		numbers = list()
		images = list()
		with index.searcher() as searcher:
			#disjunctive
			if(disjunctive=="disjunctive"):
				query = QueryParser('name',schema=index.schema,group=qparser.OrGroup)
			#conjunctive
			else:
				query = QueryParser('name',schema=index.schema)

			#parse query and search
			query = query.parse(search_query)
			results = searcher.search(query,limit = return_number)

			print (len(results))
			if len(results) ==0:
				from whoosh.qparser import MultifieldParser
				query = MultifieldParser(['name','team'],schema=index.schema,group=qparser.AndGroup)
				query = query.parse(search_query)
				results = searcher.search(query,limit = return_number)
			#name,team,url,position,PPG,RPG,APG,number,image = -1,-1,-1,-1,-1,-1,-1,-1,-1
			for r in results:
				names.append(r['name'])
				teams.append(r['team'])
				urls.append(r['url'])
				positions.append(r['position'])
				PPGs.append(r['PPG'])
				RPGs.append(r['RPG'])
				APGs.append(r['APG'])
				numbers.append(r['number'])
				images.append(r['image'])
			return names,teams,urls,positions,PPGs,RPGs,APGs,numbers,images

		#return size of index in terms of tuples
	def getIndexSize(self,index):
		return index.doc_count()
		#Clear index

	def clear_index(self,index):
		shutil.rmtree(index)

class MyWhooshSearcher(object):
	def __init__(self):
		super(MyWhooshSearcher, self).__init__()
		f = open('page_rank_scores.json')
		self.data = json.load(f)

		f1 = open('hits_scores.json')
		hitsData = json.load(f1)
		self.hubDict = hitsData[1]
		self.authDict = hitsData[0]

	def buildIndex(self,directory):
		#Each tuple will have a url and the content of that url that is in our corpus
		schema = Schema(title = TEXT(stored=True),url=TEXT(stored=True),content=TEXT(stored=True))
		#check if index is created
		if not os.path.exists("indexdir"):
			os.mkdir("indexdir")
		else:
			print("Index already created!")
			return
		ix = create_in("indexdir",schema)
		writer = ix.writer()
		for filename in os.listdir(directory):
			f = os.path.join(directory,filename)
			if os.path.isfile(f):
				file = open(f,"r")
				Lines = file.readlines()
				if len(Lines) > 1:
					if (len(Lines[0])<256):
						writer.add_document(title = (Lines[1].partition('|')[0]) , url=Lines[0].strip(),content = Lines[1])
		writer.commit()
		#search index based on given query and return user specified number of hits
	def search(self,search_query,index,return_number,disjunctive ,pagenumber):
		titles = list()
		urls = list()
		descriptions = list()
		with index.searcher() as searcher:
			#disjunctive
			if(disjunctive=="disjunctive"):
				query = QueryParser('content',schema=index.schema,group=qparser.OrGroup)
			#conjunctive
			else:
				query = QueryParser('content',schema=index.schema)

			#parse query and search
			query = query.parse(search_query)
			results = searcher.search_page(query, pagenumber, pagelen=return_number)

			# order it off pagerank scores 
			pr = []
			for result in results:
				pRank = self.data.get(result["url"])
				if pRank == None:
					pRank = 0

				pr.append((pRank, result)) # list of (prScore, result object)

			#print(f"list of pr results {pr}")
			pr.sort(key=lambda x: x[0], reverse=True) # sort list of tuples by pr score (greatest to least)
			

			# greatest pr first, to least pr
			for r in pr:
				#print(r[1]['title'])
				titles.append(self.getTitle(r[1]["title"]))
				urls.append(r[1]["url"])
				descriptions.append(self.getDescription(r[1]["content"]))

		return titles,urls,descriptions


	# if return number is -1, then dont limit returned pages
	def hitsSearch(self, search_query, index, return_number, disjunctive, pagenumber):
		titles = list()
		urls = list()
		descriptions = list()

		with index.searcher() as searcher:
			#disjunctive
			if(disjunctive=="disjunctive"):
				query = QueryParser('content',schema=index.schema,group=qparser.OrGroup)
			#conjunctive
			else:
				query = QueryParser('content',schema=index.schema)

			#parse query and search
			query = query.parse(search_query)
			results = searcher.search_page(query, pagenumber, pagelen=return_number)

			# order it off hits scores 
			hit = []
			for result in results:
				hubVal = self.hubDict.get(result["url"])
				authVal = self.authDict.get(result["url"])

				if hubVal == None:
					hubVal = 0
					print(f"hubval was None")

				if authVal == None:
					authVal = 0
					print(f"authVal was none")

				# hit score combined = authority score + hub score
				hitComb = hubVal + authVal

				hit.append((hitComb, result)) # list of (hitScore, result object)

			#print(f"list of hit results {hit}")
			hit.sort(key=lambda x: x[0], reverse=True) # sort list of tuples by pr score (greatest to least)
			#print(f"\nSORTED hit results: {hit}")
		

			# greatest pr first, to least pr
			for h in hit:
				#print(r[1]['title'])
				titles.append(self.getTitle(h[1]["title"]))
				urls.append(h[1]["url"])
				descriptions.append(self.getDescription(h[1]["content"]))

		return titles, urls, descriptions
		
	def getTitle(self,title):
		new_title = ""
		words = title.split(" ")
		count = 0
		for word in words:
			if count ==12:
				break
			new_title+=word+" "
			count+=1
		return new_title

		#return description for url
	def getDescription(self,content):
		new_description = ""
		words = content.split(" ")
		count = 0
		for word in words:
			if count ==20:
				break
			new_description+=word+" "
			count+=1
		return new_description

		#return size of index in terms of tuples
	def getIndexSize(self,index):
		return index.doc_count()
		#Clear index
	def clear_index(self,index):
		shutil.rmtree(index)









