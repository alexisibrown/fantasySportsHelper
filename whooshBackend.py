import whoosh.index as indexa
from flask import Flask, render_template, url_for, request, session, redirect
from whooshSearchers import MyWhooshPlayerSearcher,MyWhooshSearcher
from datetime import timedelta # persistance

app = Flask(__name__) 
# used to encrypt flask user data
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.permanent_session_lifetime = timedelta(minutes=5)


# checks if there is a session for this clients IP.
# Create a new session if there is not one.
def sessionHandler(clientIP):
	if clientIP not in session:
		print(f"Creating session for IP {clientIP}")
		session.permanent = True
		session[clientIP] = [] # empty list of user searches
	else:
		print(f"Client has session. Client search history: {session.get(clientIP)}")


@app.route('/', methods=['GET', 'POST'])
def index():
	print("Someone is at the home page.")
	clientIP = request.remote_addr
	sessionHandler(clientIP)

	# get latest search string
	latestSearch = None
	searchHistory = session.get(clientIP)

	# IF USER HAS A SEARCH HISTORY:
	if len(searchHistory) != 0:
		latestSearch = searchHistory[-1]

		ix = indexa.open_dir("indexdir")
		titless, urlss,descriptionss = mySearcher.hitsSearch(latestSearch, ix, 5, "disjunctive", 1)

		return render_template('index.html', history=latestSearch, results=zip(titless, urlss, descriptionss))

	# user has no search history, dont search / HITS
	else:
		return render_template('index.html', history=latestSearch)

@app.route('/results/', methods=['GET', 'POST'])
def results():
	ix = indexa.open_dir("indexdir")
	ix2 = indexa.open_dir("player_index_dir")
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args
	query = data.get('query')
	page = data.get('page')
	if page == None:
		page = 1
	
	print("You searched for: " + query,page)

	clientIP = request.remote_addr
	# check if needs to be created. Handles the slim chance that session expires between
	# client entering site and searching (and multiple searches)
	sessionHandler(clientIP)
	session[clientIP].append(query) # add this query to the session user search history info

	player = False
	multiple_players = False
	titless, urlss,descriptionss = mySearcher.search(query,ix,10,"disjunctive",int(page))
	names,teams,urls,positions,PPGs,RPGs,APGs,numbers,images= myPlayerSearcher.search(query,ix2,15,"con")
	if len(names) > 0:  player = True
	if len(names) > 1:  multiple_players = True
	
	#Advanced Search Stuff
	if data.get('ppgmin') != None and data.get('ppgmin') != "":
		for i in range(0,len(names)-1):
			if float(PPGs[i]) < float(data.get('ppgmin')):
				names.pop(i)
				teams.pop(i)
				urls.pop(i)
				positions.pop(i)
				PPGs.pop(i)
				RPGs.pop(i)
				APGs.pop(i)
				numbers.pop(i)
				images.pop(i)
				i -= 1
	if data.get('ppgmax') != None and data.get('ppgmax') != "":
		for i in range(0,len(names)-1):
			if float(PPGs[i]) > float(data.get('ppgmax')):
				names.pop(i)
				teams.pop(i)
				urls.pop(i)
				positions.pop(i)
				PPGs.pop(i)
				RPGs.pop(i)
				APGs.pop(i)
				numbers.pop(i)
				images.pop(i)
				i -= 1
	if data.get('rpgmin') != None and data.get('rpgmin') != "":
		for i in range(0,len(names)-1):
			if float(RPGs[i]) < float(data.get('rpgmin')):
				names.pop(i)
				teams.pop(i)
				urls.pop(i)
				positions.pop(i)
				PPGs.pop(i)
				RPGs.pop(i)
				APGs.pop(i)
				numbers.pop(i)
				images.pop(i)
				i -= 1
	if data.get('rpgmax') != None and data.get('rpgmax') != "":
		for i in range(0,len(names)-1):
			if float(RPGs[i]) > float(data.get('rpgmax')):
				names.pop(i)
				teams.pop(i)
				urls.pop(i)
				positions.pop(i)
				PPGs.pop(i)
				RPGs.pop(i)
				APGs.pop(i)
				numbers.pop(i)
				images.pop(i)
				i -= 1
	if data.get('apgmin') != None and data.get('apgmin') != "":
		for i in range(0,len(names)-1):
			if float(APGs[i]) < float(data.get('apgmin')):
				names.pop(i)
				teams.pop(i)
				urls.pop(i)
				positions.pop(i)
				PPGs.pop(i)
				RPGs.pop(i)
				APGs.pop(i)
				numbers.pop(i)
				images.pop(i)
				i -= 1
	if data.get('apgmax') != None and data.get('apgmax') != "":
		for i in range(0,len(names)-1):
			if float(APGs[i]) > float(data.get('apgmax')):
				names.pop(i)
				teams.pop(i)
				urls.pop(i)
				positions.pop(i)
				PPGs.pop(i)
				RPGs.pop(i)
				APGs.pop(i)
				numbers.pop(i)
				images.pop(i)
				i -= 1
	
	return render_template('results.html', query=query, results=zip(titless, urlss, descriptionss),player_info = zip(names,teams,urls,positions,PPGs,RPGs,APGs,numbers,images),player=player,multiple_players=multiple_players,page=int(page)+1)


if __name__ == '__main__':
	#Create searcher and build index if needed for Whoosh
	global mySearcher, myPlayerSearcher
	mySearcher = MyWhooshSearcher()
	myPlayerSearcher = MyWhooshPlayerSearcher()
	#mySearcher.buildIndex("pages")
	#myPlayerSearcher.buildIndex("players")
	#Run web server
	app.run(debug=True)
