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
	titles, urls,descriptions = mySearcher.search(query,ix,10,"disjunctive")
	player_results= myPlayerSearcher.search(query,ix2,1,"disjunctive")
	if player_results != -1:
		return render_template('results.html', query=query, results=zip(titles, urls, descriptions),
		player_info = player_results)
	return render_template('results.html', query=query, results=zip(titles, urls, descriptions))


if __name__ == '__main__':
	#Create searcher and build index if needed for Whoosh
	global mySearcher, myPlayerSearcher
	mySearcher = MyWhooshSearcher()
	myPlayerSearcher = MyWhooshPlayerSearcher()
	#mySearcher.buildIndex("pages")
	#Run web server
	app.run(debug=True)