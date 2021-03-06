from flask import url_for, render_template, request, session
from flask_uploads import UploadSet, configure_uploads, IMAGES
from app import app
from google_cloud_interface import analyze_file
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from secrets import give_secrets
import ssl
import dataAnalysis
from api_main import api_main

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
	logBool = check_login()
	return render_template('index.html', title='Home', login=logBool)

@app.route('/login')
def login():
	#redirect = {'url':"https://api.instagram.com/oauth/authorize/?client_id=" + secrets['client_id'] + "&redirect_uri=http://localhost:5000/auth&response_type=code"}
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
		#update login var
		session['login'] = True
		#store token
		session['token'] = json
		#start the api calls here
		#session['username'] = api_main(json)
		#redirect link to results page
		redirect = "/success"
		return render_template('redirect.html', link=redirect, time=5)
	else:
		return render_template('index.html', title='Home')

@app.route('/logout')
def logout():
	session['login'] = False
	obj = open('access_token.json', 'w')
	obj.write('')
	obj.close()
	return render_template('index.html', title='Home')

@app.route('/success')
def success():
	best5hastags      = dataAnalysis.goForItBaby()[0]
	bestTimesString   = dataAnalysis.goForItBaby()[1]
	logBool = check_login()
	return render_template('success.html', title='Donald J Trump', best5hastags = best5hastags, bestTimesString = bestTimesString, login=logBool)



