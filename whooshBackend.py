#from flask import Flask, render_template, url_for, request
import whoosh.index as indexa
from flask import Flask, render_template, url_for, request
from whooshSearchers import MyWhooshPlayerSearcher,MyWhooshSearcher

app = Flask(__name__) 

@app.route('/', methods=['GET', 'POST'])
def index():
	print("Someone is at the home page.")
	return render_template('index.html')

@app.route('/results/', methods=['GET', 'POST'])
def results():
	ix = indexa.open_dir("indexdir")
	ix2 = indexa.open_dir("player_index_dir")
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args
	query = data.get('query')
	print("You searched for: " + query)
	player = False
	multiple_players = False
	titless, urlss,descriptionss = mySearcher.search(query,ix,10,"disjunctive")
	names,teams,urls,positions,PPGs,RPGs,APGs,numbers,images= myPlayerSearcher.search(query,ix2,15,"con")
	if len(names) > 0:  player = True
	if len(names) > 1:  multiple_players = True
	return render_template('results.html', query=query, results=zip(titless, urlss, descriptionss),player_info = zip(names,teams,urls,positions,PPGs,RPGs,APGs,numbers,images),player=player,multiple_players=multiple_players)


if __name__ == '__main__':
	#Create searcher and build index if needed for Whoosh
	global mySearcher, myPlayerSearcher
	mySearcher = MyWhooshSearcher()
	myPlayerSearcher = MyWhooshPlayerSearcher()
	#mySearcher.buildIndex("pages")
	#Run web server
	app.run(debug=True)