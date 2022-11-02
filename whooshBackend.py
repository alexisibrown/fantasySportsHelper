#from flask import Flask, render_template, url_for, request
import shutil
import whoosh
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser
import os 

class MyWhooshSearcher(object):
	def __init__(self):
		super(MyWhooshSearcher, self).__init__()

	def buildIndex(self,directory):
		#Each tuple will have a url and the content of that url that is in our corpus
		schema = Schema(title = TEXT(stored=True),url=TEXT(stored=True),content=TEXT)
		#check if index is created
		if not os.path.exists("indexdir"):
		    os.mkdir("indexdir")
		else:
			print("Index already created!")
			return
		ix = create_in("indexdir", schema)
		writer = ix.writer()
		for filename in os.listdir(directory):
		    f = os.path.join(directory, filename)
		    # checking if it is a file
		    if os.path.isfile(f):
		    	file = open(f, "r")
		    	Lines = file.readlines()
		    	#clean data to fit schema
		    	if len(Lines) > 1:
		    		if len(Lines[0])<256:
		    			writer.add_document(title = (Lines[1].partition('|')[0]) , url=Lines[0].strip(),content = Lines[1])
		writer.commit()

		#search index based on given query and return user specified number of hits
	def search(self,search_query,index,return_number,disjunctive):
		print("Results for query:",search_query)
		from whoosh.qparser import QueryParser
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

			#print results
			count = 1
			for r in results:
				print(count,"-",r["title"])
				print("URL: ",r["url"])
				count+=1
			print()

		#return size of index in terms of tuples
	def getIndexSize(self,index):
		return index.doc_count()

	def clear_index(self,index):
		shutil.rmtree(index)

if __name__ == '__main__':
	global mySearcher
	mySearcher = MyWhooshSearcher()
	mySearcher.buildIndex("test")