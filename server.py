from flask import Flask, request, Response, render_template
from functools import wraps
import socket
from pymongo import MongoClient

app= Flask(__name__)
client = MongoClient('localhost:27017')
db = client.Attendance

def check_auth(username,password):
	return username=="abc" and password=='123'

def authenticate():
	return Response(
	'Could ont verify your access level for that URL.\n'
	'you have to login with proper credentials',401,
	{'WWW-Authenticate':'Basic realm="login required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth=request.authorization
		if not  auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated

def authenticate():
	return Response(
	'Could ont verify your access level for that URL.\n'
	'you have to login with proper credentials',401,
	{'WWW-Authenticate':'Basic realm="login required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth=request.authorization
		if not  auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated

@app.route("/")
@requires_auth
def hello():
	return "hello user"

@app.route("/summary", methods = ['GET'])
@requires_auth
def summary():
	try:
		data = db.Students.find()
		return render_template('Report.html', data = data)
	except Exception as e:
		return "error"
	return "hello user"


def get_self_ip():
	#return str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith()	
	return str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

if __name__ == "__main__":
	ip=get_self_ip()
	app.run(host=ip, port=8080, debug=True)
