from flask import url_for, render_template, request, session
from flask_uploads import UploadSet, configure_uploads, IMAGES
from app import app
from google_cloud_interface import analyze_file
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from secrets import give_secrets
import ssl
from dataAnalysis import goForItBaby








ssl._create_default_https_context = ssl._create_unverified_context
#configuring photo stuff
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

#retrieving instagram client api id and password
secrets = give_secrets()

#managing login
def check_login():
	if 'login' not in session:
		session['login'] = False
	return session['login']

@app.route('/')
@app.route('/index')
def index():
	user = {'username': 'Kiran'}
	logBool = check_login()
	return render_template('index.html', title='Home', user=user, login=logBool)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	user = {'username': 'Kiran'}
	logBool = check_login()
	if request.method == 'POST' and 'photo' in request.files:
		filename = photos.save(request.files['photo'])
		results = analyze_file('static/img/' + filename)
		return render_template('upload.html', title='Upload', user=user, file=filename, data=results, login=logBool)
	return render_template('upload.html', title='Upload', user=user, login=logBool)

@app.route('/login')
def login():
	redirect = "https://api.instagram.com/oauth/authorize/?client_id=" + secrets['client_id'] + "&redirect_uri=http://localhost:5000/auth&response_type=code"
	return render_template('redirect.html', link=redirect, time=0)

@app.route('/auth', methods=['GET'])
def auth():
	#get and store code
	#check if we got code (user logged in) or not
	

	if 'code' in request.args:
		code = request.args['code']
		#make post request to get token
		url = "https://api.instagram.com/oauth/access_token"
		fields = {
			'client_id'     : secrets['client_id'],
			'client_secret' : secrets['client_secret'],
			'grant_type'    : 'authorization_code',
			'redirect_uri'  : 'http://localhost:5000/auth',
			'code'          : code}
		postRequest = Request(url, urlencode(fields).encode())
		json = urlopen(postRequest).read().decode()
		obj = open('access_token.json', 'w')
		obj.write(json)
		obj.close()
		#print("success")


		#REPLACE BY DATABASE PULL AND ANALYSIS
		# results = goForItBaby()
		# best5hastags      = results[0]
		# bestTimesString   = results[1]
		# mostCommonGogleResults = results[2]
		# print(mostCommonGogleResults)

		



		redirect = "/success"
		return render_template('redirect.html', link=redirect, time=5)
		#return render_template('success.html', title='Donald J Trump', best5hastags = best5hastags, bestTimesString = bestTimesString, mostCommonGogleResults = mostCommonGogleResults )
	else:
		user = {'username': 'Kiran'}
		return render_template('index.html', title='Home', user=user)



@app.route('/logout')
def logout():
	session['login'] = False
	obj = open('access_token.json', 'w')
	obj.write('')
	obj.close()
	user = {'username': 'Kiran'}
	return render_template('index.html', title='Home', user=user)

@app.route('/success')
def success():
	results = goForItBaby()
	best5hastags      = results[0]
	bestTimesString   = results[1]
	mostCommonGogleResults = results[2]
	print(mostCommonGogleResults)
	logBool = check_login()
	return render_template('success.html', title='Donald J Trump', best5hastags = best5hastags, bestTimesString = bestTimesString, mostCommonGogleResults = mostCommonGogleResults, login=logBool)



