import shutil
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser
import os 
import whoosh.index as indexa

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
	def search(self,search_query,index,return_number,disjunctive):
		from whoosh.qparser import QueryParser
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
			results = searcher.search(query,limit = return_number)
			print(results)
			#print results
			for r in results:
				print(r['title'])
				titles.append(self.getTitle(r["title"]))
				urls.append(r["url"])
				descriptions.append(self.getDescription(r["content"]))

		return titles,urls,descriptions
		
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

