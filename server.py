from flask import Flask, request, Response, render_template
from functools import wraps
import socket
import pymongo

app= Flask(__name__)
client = pymongo.MongoClient()
attDB = client['Attendance']
attCol = attDB['Students']
fullDB = client['FullRoster']
fullCol = fullDB['Students']

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

@app.route("/summary/<date>", methods = ['GET'])
@requires_auth
def summary(date):
	try:
            date = date.replace('-','/')
            print(date)
            fullData = list(fullCol.find())
            print(fullData)
            attData = list(attCol.find({"Date":date}, {"Name": 1,"Status":1,"StudentID":1,"Date":1}))
            if attData == []:
                return "No attendance for that day!"
            print(attData)
            for d in fullData:
                studName = d["Name"]
                presentStud={}
                for s in attData:
                    if s["Name"] == studName:
                        presentStud["Name"]="here"
                        print(presentStud)
                    if presentStud == {}:
                        attData.append({"Name":d["Name"],"StudentIDNumber":d["StudentID"],"Date":date,"Status":"Absent"})
            return render_template('Report.html', data = attData)
	except Exception as e:
		return str(e)
	return "hello user"


def get_self_ip():
	#return str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith()	
	return str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

if __name__ == "__main__":
	ip=get_self_ip()
	app.run(host=ip, port=8080, debug=True)