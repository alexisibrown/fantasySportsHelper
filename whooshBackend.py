#from flask import Flask, render_template, url_for, request
import shutil
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser
import os 
import whoosh.index as indexa
from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	print("Someone is at the home page.")
	return render_template('index.html')

@app.route('/results/', methods=['GET', 'POST'])
def results():
	ix = indexa.open_dir("indexdir")
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args
	query = data.get('query')
	titles, urls,descriptions = mySearcher.search(query,ix,10,"con")
	print("You searched for: " + query) 
	return render_template('results.html', query=query, results=zip(titles, urls, descriptions))

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

			#print results
			for r in results:
				titles.append(self.getTitle(r["title"]))
				urls.append(r["url"])
				descriptions.append(self.getDescription(r["content"]))

		return titles,urls,descriptions
	def getTitle(self,title):
		if len(title.partition('|')[0]) < 50:
			return title.partition('|')[0]
		elif(len(title.partition('.')[0])>50):
			return title.partition('.')[0]
		elif(len(title.partition('-')[0])>50):
			return title.partition('-')[0]
		return title[0:50]

		#return description for url
	def getDescription(self,content):
		if len(content.partition('|')[0]) < 150:
			return content.partition('|')[0]
		elif(len(content.partition('.')[0])>150):
			return content.partition('.')[0]
		elif(len(content.partition('-')[0])>150):
			return content.partition('-')[0]
		return content[0:150]+"..."
		return description

		#return size of index in terms of tuples
	def getIndexSize(self,index):
		return index.doc_count()
		#Clear index
	def clear_index(self,index):
		shutil.rmtree(index)

if __name__ == '__main__':
	#Create searcher and build index if needed for Whoosh
	global mySearcher
	mySearcher = MyWhooshSearcher()
	mySearcher.buildIndex("pages")
	#Run web server
	app.run(debug=True)