from flask import Flask, render_template, request, session, redirect, url_for
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from functools import wraps
import pyrebase
import time
from flask import jsonify

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            print("you need to login first")
            return redirect(url_for('login'))

    return wrap

app = Flask(__name__)
app.secret_key = 'messageapp2023'


firebaseConfig = {
	'apiKey': "AIzaSyCrpHaXnjUGqMVyHPEXn8UuXr3Wbg2VGRw",
	'authDomain': "message-2e4ae.firebaseapp.com",
	'databaseURL': "https://message-2e4ae-default-rtdb.firebaseio.com",
	'projectId': "message-2e4ae",
	'storageBucket': "message-2e4ae.appspot.com",
	'messagingSenderId': "291585520596",
	'appId': "1:291585520596:web:cf27994b656816095f5c41",
	'measurementId': "G-Y592LV0XG3"
};

firebaseWeb = pyrebase.initialize_app(firebaseConfig)
db = firebaseWeb.database()
authWeb = firebaseWeb.auth()
# # Initialize Firebase
# cred = credentials.Certificate('./key/message-2e4ae-firebase-adminsdk-8k7x6-2db3860714.json')
# default_app = firebase_admin.initialize_app(cred)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the form data
        email = request.form['username']
        password = request.form['password']
        print(email, password)
        # Create a new Firebase user
        try:
            user = authWeb.create_user_with_email_and_password(email, password)
            db.child("users").child(user['localId']).set(user)
            data = {"active": "0"}
            db.child("users").child(user['localId']).update(data)
            return redirect(url_for('login'))	
        except Exception as e:
            return render_template('signup.html', error=e)

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        password = request.form['password']
        print("user:", username, "and", password)
        # Verify the user's credentials
        try:
            user = authWeb.sign_in_with_email_and_password(username, password)
            session['logged_in'] = True
            session['local_id'] = user['localId']
            db.child("users").child(user['localId']).update({"active": "1"})
            #db.child("joined").push({"join": "1"})
            return redirect(url_for("messages"))
        except:
            return redirect(url_for("login"))

    return render_template('login.html')


from datetime import datetime

def refresh_messages():
    message_list = []
    messages = db.child("messages").get()
    for message in messages.each():
        dt_obj = datetime.fromtimestamp(message.val()['timestamp'])
        time = dt_obj.strftime('%H:%M:%S')
        message_list.append([message.val()['message'], message.val()['username'], time])
    return message_list



def refresh_active_user():
    active_users_c = 0
    active_users_arr = []
    active_users = db.child("users").get()
    for user in active_users.each():
        usr_obj = user.val()['active']
        if usr_obj == "1":
            username = user.val()['email']
            user_displayName = username.split("@")[0]
            active_users_arr.append(user_displayName)
            active_users_c += 1
    return active_users_c, active_users_arr


@app.route('/messages')
@login_required
def messages():
    localId = session.get('local_id')
    user_data = db.child("users").child(localId).get().val()
    print(user_data)
    user_displayName = user_data['email'].split("@")[0]
    message_list = refresh_messages()
    active_users_count, active_users_array = refresh_active_user()
    len_active_users_array = len(active_users_array)
    return render_template('messages.html', user_displayName=user_displayName, message_list=message_list, len = len(message_list), active_users_count = active_users_count, len_active_users_array=len_active_users_array, active_users_array=active_users_array)


@app.route("/add_message", methods=["POST"])
def add_message():
    # Get the current user's display name
    local_id = session.get('local_id')
    user_data = db.child("users").child(local_id).get().val()
    user_displayName = user_data['email'].split("@")[0]
    # Add the message to the database
    db.child("messages").push({
        "username": user_displayName,
        "message": request.form['message'],
        "timestamp": time.time()

    })
    message_list = refresh_messages()
    return redirect(url_for("messages"))




@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    localId = session.get('local_id')
    db.child("users").child(localId).update({"active": "0"})
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.debug = True
    app.run()
