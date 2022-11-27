import whoosh.index as indexa
from flask import Flask, render_template, url_for, request, session, redirect
from whooshSearchers import MyWhooshPlayerSearcher,MyWhooshSearcher
from datetime import timedelta # persistance
from flask_session import Session

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
	sessionHandler(request.remote_addr)

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

	clientIP = request.remote_addr
	# check if needs to be created. Handles the slim chance that session expires between
	# client entering site and searching (and multiple searches)
	sessionHandler(clientIP)
	session[clientIP].append(query) # add this query to the session user search history info

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
	#myPlayerSearcher.buildIndex("players")
	#Run web server
	app.run(debug=True)